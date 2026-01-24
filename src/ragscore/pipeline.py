import asyncio
import json
import random

from . import __version__, config
from .data_processing import chunk_text, initialize_nltk
from .llm import agenerate_qa_for_chunk
from .ui import get_async_pbar, get_pbar, patch_asyncio


def _read_from_paths(paths):
    """
    Read documents from a list of file or directory paths.

    Args:
        paths: List of file or directory paths

    Returns:
        List of document dictionaries
    """
    from pathlib import Path

    all_docs = []
    files_to_process = []

    for path_str in paths:
        path = Path(path_str)

        if not path.exists():
            print(f"Warning: Path does not exist: {path}")
            continue

        if path.is_file():
            # Single file
            files_to_process.append(path)
        elif path.is_dir():
            # Directory - read all files from it
            supported_extensions = (".pdf", ".txt", ".md", ".html")
            dir_files = [p for p in path.rglob("*") if p.suffix.lower() in supported_extensions]
            files_to_process.extend(dir_files)
        else:
            print(f"Warning: Not a file or directory: {path}")

    if not files_to_process:
        return []

    # Read all collected files
    print(f"Found {len(files_to_process)} documents to process...")

    import uuid

    import PyPDF2

    for file_path in get_pbar(files_to_process, desc="Reading documents"):
        text = ""
        try:
            if file_path.suffix.lower() == ".pdf":
                with open(file_path, "rb") as fh:
                    reader = PyPDF2.PdfReader(fh)
                    text = "".join(page.extract_text() or "" for page in reader.pages)
            else:
                with open(file_path, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()

            if text.strip():
                all_docs.append({"doc_id": str(uuid.uuid4()), "path": str(file_path), "text": text})
            else:
                print(f"Warning: No text extracted from {file_path}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"Successfully loaded {len(all_docs)} documents.")
    return all_docs


async def _async_generate_qas(
    chunks: list[dict],
    concurrency: int = 5,
    provider=None,
) -> list[dict]:
    """
    Async QA generation with rate limiting via Semaphore.

    Args:
        chunks: List of chunk dictionaries
        concurrency: Max concurrent LLM calls (default: 5)
        provider: LLM provider instance (auto-detected if None)

    Returns:
        List of generated QA pairs
    """
    if provider is None:
        from .providers import get_provider

        provider = get_provider()

    semaphore = asyncio.Semaphore(concurrency)
    all_qas = []
    errors = []

    async def process_chunk(chunk: dict) -> list[dict]:
        """Process a single chunk with rate limiting and retry."""
        difficulty = random.choice(config.DIFFICULTY_MIX)
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            async with semaphore:
                try:
                    items = await agenerate_qa_for_chunk(
                        chunk["text"], difficulty, n=config.NUM_Q_PER_CHUNK, provider=provider
                    )

                    # Add metadata to each item
                    for item in items:
                        item.update(
                            {
                                "doc_id": chunk["doc_id"],
                                "chunk_id": chunk["chunk_id"],
                                "source_path": chunk["path"],
                                "difficulty": difficulty,
                            }
                        )
                        item["metadata"] = {
                            "generator": "RAGScore Generate",
                            "version": __version__,
                            "license": "Apache-2.0",
                            "repo": "https://github.com/HZYAI/RagScore",
                        }
                    return items

                except Exception as e:
                    error_str = str(e).lower()
                    # Check for rate limit errors (429)
                    if "rate" in error_str or "429" in error_str or "limit" in error_str:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (2**attempt)  # Exponential backoff
                            await asyncio.sleep(wait_time)
                            continue
                    # Non-retryable error or max retries reached
                    errors.append(f"Chunk {chunk['chunk_id']}: {e}")
                    return []

        return []

    # Process all chunks with progress bar
    tasks = [process_chunk(chunk) for chunk in chunks]

    try:
        async_pbar = get_async_pbar()
        results = await async_pbar.gather(*tasks, desc="Generating QAs")
        for items in results:
            all_qas.extend(items)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Saving progress...")

    if errors:
        print(f"\n⚠️  {len(errors)} chunks failed to process")

    return all_qas


def run_pipeline(paths=None, docs_dir=None, concurrency: int = 5):
    """
    Executes the QA generation pipeline.

    Reads documents, chunks them, and generates QA pairs using LLM.
    No embeddings or vector indexing required.

    Args:
        paths: List of file or directory paths to process
        docs_dir: [DEPRECATED] Single directory path (use paths instead)
        concurrency: Max concurrent LLM calls (default: 5, use higher for local LLMs)
    """

    # Ensure directories exist
    config.ensure_dirs()

    # Ensure NLTK data is ready
    initialize_nltk()

    # Handle deprecated docs_dir parameter
    if docs_dir is not None:
        paths = [docs_dir]

    # Use provided paths or default
    if paths is None or len(paths) == 0:
        paths = [config.DOCS_DIR]

    # --- 1. Read and Chunk Documents ---
    print("--- Reading and Chunking Documents ---")
    docs = _read_from_paths(paths)
    if not docs:
        print("No documents found.")
        return

    # Build chunks with metadata (no embeddings needed!)
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["text"])
        for chunk_text_content in chunks:
            all_chunks.append(
                {
                    "doc_id": doc["doc_id"],
                    "path": doc["path"],
                    "text": chunk_text_content,
                    "chunk_id": len(all_chunks),
                }
            )

    print(f"Created {len(all_chunks)} chunks from {len(docs)} documents")

    # Filter out short chunks
    valid_chunks = [c for c in all_chunks if len(c["text"].split()) >= 40]
    print(
        f"Processing {len(valid_chunks)} chunks (skipped {len(all_chunks) - len(valid_chunks)} short chunks)"
    )

    # --- 2. Generate QA Pairs ---
    print("\n--- Generating QA Pairs ---")
    print("💡 Tip: Press Ctrl+C to stop and save progress at any time")

    # Patch asyncio for notebook environments
    patch_asyncio()

    # Use async generation for speed
    all_qas = asyncio.run(_async_generate_qas(valid_chunks, concurrency=concurrency))

    # --- 3. Save Results ---
    if not all_qas:
        print("\nNo QA pairs were generated.")
        return

    print(f"\n--- Saving {len(all_qas)} Generated QAs ---")
    with open(config.GENERATED_QAS_PATH, "w", encoding="utf-8") as f:
        for qa in all_qas:
            f.write(json.dumps(qa, ensure_ascii=False) + "\n")

    print(f"✅ Pipeline complete! Results saved to {config.GENERATED_QAS_PATH}")
    print("\n⭐ Enjoying RAGScore? Star us: https://github.com/HZYAI/RagScore")
    print("💬 Questions? Join discussions: https://github.com/HZYAI/RagScore/discussions")

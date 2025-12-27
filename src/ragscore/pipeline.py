import json
import random

from tqdm import tqdm

from . import config
from .data_processing import chunk_text, initialize_nltk
from .llm import generate_qa_for_chunk


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

    for file_path in tqdm(files_to_process, desc="Reading documents"):
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


def run_pipeline(paths=None, docs_dir=None):
    """
    Executes the QA generation pipeline.

    Reads documents, chunks them, and generates QA pairs using LLM.
    No embeddings or vector indexing required.

    Args:
        paths: List of file or directory paths to process
        docs_dir: [DEPRECATED] Single directory path (use paths instead)
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

    # --- 2. Generate QA Pairs ---
    print("\n--- Generating QA Pairs ---")

    all_qas = []
    for chunk in tqdm(all_chunks, desc="Generating QAs"):
        # Skip very short chunks
        if len(chunk["text"].split()) < 40:
            continue

        difficulty = random.choice(config.DIFFICULTY_MIX)
        try:
            items = generate_qa_for_chunk(chunk["text"], difficulty, n=config.NUM_Q_PER_CHUNK)
            for item in items:
                item.update(
                    {
                        "doc_id": chunk["doc_id"],
                        "chunk_id": chunk["chunk_id"],
                        "source_path": chunk["path"],
                        "difficulty": difficulty,
                    }
                )
                all_qas.append(item)
        except Exception as e:
            print(f"Error generating QA for chunk {chunk['chunk_id']}: {e}")

    # --- 3. Save Results ---
    if not all_qas:
        print("\nNo QA pairs were generated.")
        return

    print(f"\n--- Saving {len(all_qas)} Generated QAs ---")
    with open(config.GENERATED_QAS_PATH, "w", encoding="utf-8") as f:
        for qa in all_qas:
            f.write(json.dumps(qa, ensure_ascii=False) + "\n")

    print(f"✅ Pipeline complete! Results saved to {config.GENERATED_QAS_PATH}")

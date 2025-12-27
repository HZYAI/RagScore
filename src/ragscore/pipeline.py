import json
import random

from tqdm import tqdm

from . import config
from .data_processing import chunk_text, initialize_nltk, read_docs
from .llm import generate_qa_for_chunk


def run_pipeline(docs_dir=None):
    """
    Executes the QA generation pipeline.
    
    Reads documents, chunks them, and generates QA pairs using LLM.
    No embeddings or vector indexing required.

    Args:
        docs_dir: Path to documents directory (default: config.DOCS_DIR)
    """
    from pathlib import Path

    # Ensure directories exist
    config.ensure_dirs()

    # Ensure NLTK data is ready
    initialize_nltk()

    # Use provided docs_dir or default
    docs_path = Path(docs_dir) if docs_dir else config.DOCS_DIR

    # --- 1. Read and Chunk Documents ---
    print("--- Reading and Chunking Documents ---")
    docs = read_docs(dir_path=docs_path)
    if not docs:
        print("No documents found.")
        return

    # Build chunks with metadata (no embeddings needed!)
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["text"])
        for i, chunk_text_content in enumerate(chunks):
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

import json
import random
from tqdm import tqdm

from . import config
from .data_processing import read_docs, initialize_nltk
from .vector_store import build_index, save_index, load_index
from .llm import generate_qa_for_chunk

def run_pipeline(force_reindex: bool = False):
    """Executes the full QA generation pipeline."""
    # Ensure directories exist
    config.ensure_dirs()
    
    # Ensure NLTK data is ready
    initialize_nltk()

    # --- 1. Indexing --- 
    if force_reindex or not config.INDEX_PATH.exists():
        print("--- Starting Document Ingestion and Indexing ---")
        docs = read_docs()
        if not docs:
            return
        
        index, meta = build_index(docs)
        if index is not None:
            save_index(index, meta)
    else:
        print("--- Loading Existing Index ---")
        index, meta = load_index()
        if index is None:
            print("Failed to load index. Exiting.")
            return

    # --- 2. QA Generation --- 
    print("\n--- Starting QA Pair Generation ---")
    all_qas = []
    for m in tqdm(meta, desc="Generating QAs"):
        # Skip very short chunks
        if len(m["text"].split()) < 40:
            continue

        difficulty = random.choice(config.DIFFICULTY_MIX)
        try:
            items = generate_qa_for_chunk(m["text"], difficulty, n=config.NUM_Q_PER_CHUNK)
            for item in items:
                item.update({
                    "doc_id": m["doc_id"],
                    "chunk_id": m["chunk_id"],
                    "source_path": m["path"],
                    "difficulty": difficulty,
                })
                all_qas.append(item)
        except Exception as e:
            print(f"Error generating QA for chunk {m['chunk_id']}: {e}")

    # --- 3. Save Results --- 
    if not all_qas:
        print("\nNo QA pairs were generated.")
        return

    print(f"\n--- Saving {len(all_qas)} Generated QAs ---")
    with open(config.GENERATED_QAS_PATH, "w", encoding="utf-8") as f:
        for qa in all_qas:
            f.write(json.dumps(qa, ensure_ascii=False) + "\n")

    print(f"✅ Pipeline complete! Results saved to {config.GENERATED_QAS_PATH}")

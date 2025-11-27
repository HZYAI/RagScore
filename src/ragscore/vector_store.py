import json
import faiss
import numpy as np
from tqdm import tqdm
from typing import List, Dict, Any, Tuple, Optional

from . import config
from .data_processing import chunk_text
from .embedding import embed_texts


def build_index(docs: List[Dict[str, Any]]) -> Tuple[Optional[faiss.Index], List[Dict[str, Any]]]:
    """Builds a FAISS index from a list of documents."""
    chunks_meta = []
    chunk_vecs = []

    for d in tqdm(docs, desc="Building index"):
        chunks = chunk_text(d["text"])
        if not chunks:
            continue

        vecs = embed_texts(chunks)
        if vecs.size == 0:
            continue

        for i, c_text in enumerate(chunks):
            chunk_id = len(chunks_meta)
            chunks_meta.append({
                "doc_id": d["doc_id"],
                "path": d["path"],
                "text": c_text,
                "chunk_id": chunk_id,
            })
            chunk_vecs.append(vecs[i])

    if not chunk_vecs:
        print("No chunks were generated. Index is empty.")
        return None, []

    vecs_np = np.vstack(chunk_vecs).astype("float32")
    index = faiss.IndexFlatIP(vecs_np.shape[1])
    index.add(vecs_np)

    print(f"Index built successfully with {len(chunks_meta)} chunks.")
    return index, chunks_meta

def save_index(index: faiss.Index, meta: List[Dict[str, Any]]):
    """Saves the FAISS index and metadata to disk."""
    print(f"Saving FAISS index to {config.INDEX_PATH}")
    faiss.write_index(index, str(config.INDEX_PATH))
    
    print(f"Saving metadata to {config.META_PATH}")
    with open(config.META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)

def load_index() -> Tuple[Optional[faiss.Index], List[Dict[str, Any]]]:
    """Loads the FAISS index and metadata from disk."""
    if not config.INDEX_PATH.exists() or not config.META_PATH.exists():
        print("Index files not found. Please build the index first.")
        return None, []

    print(f"Loading FAISS index from {config.INDEX_PATH}")
    index = faiss.read_index(str(config.INDEX_PATH))
    
    print(f"Loading metadata from {config.META_PATH}")
    with open(config.META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    return index, meta

def retrieve(query: str, index: faiss.Index, meta: List[Dict[str, Any]], k: int = config.TOP_K) -> List[Dict[str, Any]]:
    """Retrieves the top-k most relevant chunks for a query."""
    if index is None:
        print("Index is not available for retrieval.")
        return []

    query_vector = embed_texts([query])
    if query_vector.size == 0:
        return []

    scores, ids = index.search(query_vector, k)
    
    hits = []
    for score, idx in zip(scores[0], ids[0]):
        if idx != -1:
            hit_meta = meta[idx]
            hits.append({
                **hit_meta,
                "score": float(score),
            })
            
    return hits

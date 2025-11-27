import numpy as np
from typing import List
from langchain_community.embeddings.dashscope import DashScopeEmbeddings

from . import config

# Initialize the embedder once
embedder = DashScopeEmbeddings(
    model=config.MODEL_EMB,
    dashscope_api_key=config.DASHSCOPE_API_KEY
)

def embed_texts(texts: List[str], batch_size: int = 10) -> np.ndarray:
    """Embeds a list of texts using the configured DashScope model.
    
    DashScope API has a limit of 10 items per batch, so we process in batches.
    """
    if not texts:
        return np.array([])
    
    # Process in batches to avoid API limits
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = embedder.embed_documents(batch)
        all_embeddings.extend(batch_embeddings)
    
    return np.array(all_embeddings, dtype="float32")

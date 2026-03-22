"""
retriever.py — Cosine-similarity retrieval over numpy embeddings.

No FAISS required — pure numpy dot product over the small corpus (~60 chunks).
Fast enough: ~0.5 ms per query at 60 chunks × 384 dims.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).parent.parent / "data"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"
CHUNKS_PATH = DATA_DIR / "chunks.json"
MODEL_NAME = "all-MiniLM-L6-v2"

_embeddings: Optional[np.ndarray] = None
_chunks: Optional[List[Dict]] = None
_model: Optional[SentenceTransformer] = None


def _load() -> None:
    global _embeddings, _chunks, _model
    if _embeddings is None:
        _embeddings = np.load(str(EMBEDDINGS_PATH))
    if _chunks is None:
        with open(CHUNKS_PATH) as f:
            _chunks = json.load(f)
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)


def retrieve(query: str, top_k: int = 6) -> List[Dict]:
    """
    Return up to top_k chunks most relevant to query.
    Each result: {text, source_url, source_title, score}
    """
    _load()

    # Encode and normalise query
    q_vec = _model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)[0]  # shape (384,)

    # Cosine scores = dot product (embeddings are already L2-normalised)
    scores = _embeddings.dot(q_vec)  # shape (n_chunks,)
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        chunk = _chunks[int(idx)]
        results.append({
            "text": chunk["text"],
            "source_url": chunk["source_url"],
            "source_title": chunk["source_title"],
            "score": float(scores[idx]),
        })
    return results

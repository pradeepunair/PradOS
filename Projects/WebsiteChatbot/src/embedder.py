"""
embedder.py — Generate embeddings and save them as a numpy array.

Uses sentence-transformers/all-MiniLM-L6-v2 (local, no API key needed).
First run downloads the model (~90 MB); subsequent runs use the HF cache.

Stores two files in data/:
  embeddings.npy  — float32 array (n_chunks, 384)
  chunks.json     — chunk metadata list
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

_model: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"  Loading embedding model: {MODEL_NAME}  (first run downloads ~90 MB)")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_index(chunks: List[Dict]) -> None:
    """Embed all chunks and save embeddings + metadata to data/."""
    DATA_DIR.mkdir(exist_ok=True)
    model = _get_model()

    texts = [c["text"] for c in chunks]
    print(f"  Encoding {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,   # L2-normalise so dot product == cosine
    ).astype(np.float32)

    np.save(str(EMBEDDINGS_PATH), embeddings)
    with open(CHUNKS_PATH, "w") as f:
        json.dump(chunks, f, indent=2)

    print(f"  Saved embeddings → {EMBEDDINGS_PATH}  shape={embeddings.shape}")
    print(f"  Saved chunks     → {CHUNKS_PATH}")


def index_exists() -> bool:
    return EMBEDDINGS_PATH.exists() and CHUNKS_PATH.exists()

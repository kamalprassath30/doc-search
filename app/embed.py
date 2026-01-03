# app/embed.py
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE.parent / "data"
MODEL_NAME = "all-MiniLM-L6-v2"

# lazy model holder
_MODEL = None

def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL

def chunk_text(text, chunk_size=150, overlap=30):
    """Split text into chunks of chunk_size words with overlap."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap  # move forward but keep overlap
    return chunks

def generate_embeddings(chunks):
    model = get_model()
    embs = model.encode(chunks, convert_to_numpy=True)
    return embs.astype("float32")

def save_index(embeddings, chunks, doc_id):
    DATA_DIR.mkdir(exist_ok=True)
    np.save(DATA_DIR / f"{doc_id}_embeddings.npy", embeddings)
    with open(DATA_DIR / f"{doc_id}_chunks.txt", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c + "\n")
    return True

def load_embeddings(doc_id):
    np_path = DATA_DIR / f"{doc_id}_embeddings.npy"
    txt_path = DATA_DIR / f"{doc_id}_chunks.txt"
    if not np_path.exists() or not txt_path.exists():
        return None, None
    emb = np.load(np_path)
    with open(txt_path, "r", encoding="utf-8") as f:
        chunks = [line.strip() for line in f.readlines() if line.strip()]
    return emb, chunks

def build_knn_index(embeddings, n_neighbors=5):
    nn = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
    nn.fit(embeddings)
    return nn

def search(query, doc_id, top_k=5):
    emb, chunks = load_embeddings(doc_id)
    if emb is None:
        return None
    model = get_model()
    q_emb = model.encode([query], convert_to_numpy=True).astype("float32")
    k = min(top_k, len(emb))
    nn = build_knn_index(emb, n_neighbors=k)
    distances, indices = nn.kneighbors(q_emb, n_neighbors=k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            "chunk_index": int(idx),
            "chunk_text": chunks[int(idx)],
            "score": float(1 - dist)
        })
    return results

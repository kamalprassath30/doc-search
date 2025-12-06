# app/chunk.py
from typing import List
from pathlib import Path

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """
    Split text into chunks of approximately chunk_size characters with overlap.
    Returns list of chunk strings.
    """
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def load_text_from_saved_file(doc_id: str, data_dir: Path) -> str:
    from app.extract import extract_text_from_pdf
    matches = list(data_dir.glob(f"{doc_id}_*"))
    if not matches:
        raise FileNotFoundError("Document not found")
    return extract_text_from_pdf(matches[0])

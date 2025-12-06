# app/extract.py
import pdfplumber
from pathlib import Path
from typing import Union

def extract_text_from_pdf(path: Union[str, Path]) -> str:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    full_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            full_text.append(page_text)
    return "\n".join(full_text)

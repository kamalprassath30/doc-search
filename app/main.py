# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.extract import extract_text_from_pdf
from app.embed import (
    chunk_text as embed_chunk_text,
    generate_embeddings,
    save_index,
    search as embed_search,
)

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://doc-search-engine.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATA ----------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ---------------- MODEL ----------------
generator = None

def get_generator():
    global generator
    if generator is None:
        from transformers import pipeline
        generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-small"
        )
    return generator

# ---------------- ROUTES ----------------
@app.get("/")
def root():
    return {"message": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())
    out_path = DATA_DIR / f"{doc_id}_{file.filename}"

    content = await file.read()
    out_path.write_bytes(content)

    return {"doc_id": doc_id, "filename": file.filename}


@app.get("/extract-text/{doc_id}")
def extract_text(doc_id: str):
    matching = list(DATA_DIR.glob(f"{doc_id}_*"))
    if not matching:
        return {"error": "Document not found"}

    text = extract_text_from_pdf(matching[0])

    return {
        "doc_id": doc_id,
        "text_preview": text[:2000],
        "length": len(text)
    }


@app.post("/process/{doc_id}")
def process_and_index(doc_id: str):
    matching = list(DATA_DIR.glob(f"{doc_id}_*"))
    if not matching:
        return {"error": "Document not found"}

    text = extract_text_from_pdf(matching[0])
    chunks = embed_chunk_text(text, chunk_size=800)

    if not chunks:
        return {"status": "no_chunks"}

    embeddings = generate_embeddings(chunks)
    save_index(embeddings, chunks, doc_id)

    return {
        "doc_id": doc_id,
        "chunks_indexed": len(chunks),
        "status": "indexed"
    }


class SearchReq(BaseModel):
    doc_id: str
    query: str
    top_k: int = 3


@app.post("/search")
def search_endpoint(req: SearchReq):
    results = embed_search(req.query, req.doc_id, req.top_k)

    return {
        "query": req.query,
        "results": results
    }


@app.post("/answer")
def answer(req: SearchReq):
    results = embed_search(req.query, req.doc_id, req.top_k)

    if not results:
        return {"answer": "No data found"}

    context = "\n".join([r["chunk_text"] for r in results])[:2000]

    prompt = f"""
Context:
{context}

Question: {req.query}

Answer briefly:
"""

    gen = get_generator()

    output = gen(
        prompt,
        max_new_tokens=100,
        do_sample=False
    )

    return {
        "answer": output[0]["generated_text"]
    }
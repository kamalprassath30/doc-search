# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
# from dotenv import load_dotenv
import uuid
import os
from fastapi.middleware.cors import CORSMiddleware

from app.extract import extract_text_from_pdf
from app.embed import chunk_text as embed_chunk_text, generate_embeddings, save_index, search as embed_search
from pydantic import BaseModel
from transformers import pipeline

# ✅ lightweight model
generator = pipeline(
    "text-generation",
    # model="distilgpt2"
    model="google/flan-t5-small"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://doc-search-engine.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# load_dotenv()


@app.get("/health")
def health():
    return {"status": "ok", "project": "docsearch"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())
    out_path = DATA_DIR / f"{doc_id}_{file.filename}"
    content = await file.read()
    out_path.write_bytes(content)
    return JSONResponse({"doc_id": doc_id, "filename": file.filename})


@app.get("/extract-text/{doc_id}")
def extract_text(doc_id: str):
    matching = list(DATA_DIR.glob(f"{doc_id}_*"))
    if not matching:
        return {"error": "Document not found"}

    try:
        text = extract_text_from_pdf(matching[0])
    except Exception as e:
        return {"error": str(e)}

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

    try:
        full_text = extract_text_from_pdf(matching[0])
    except Exception as e:
        return {"error": f"Failed to extract text: {str(e)}"}

    # ✅ IMPORTANT: better chunking
    chunks = embed_chunk_text(full_text, chunk_size=800)

    if not chunks:
        return {"doc_id": doc_id, "status": "no_chunks_found"}

    try:
        embeddings = generate_embeddings(chunks)
        save_index(embeddings, chunks, doc_id)
    except Exception as e:
        return {"error": f"Embedding/index error: {str(e)}"}

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
    print(">>> SEARCH ENDPOINT HIT <<<")
    if not req.query.strip():
        return {"error": "Query is empty"}

    results = embed_search(req.query, req.doc_id, top_k=req.top_k)

    if results is None:
        return {"error": "Embeddings not found"}

    return {
        "doc_id": req.doc_id,
        "query": req.query,
        "results": results
    }


@app.post("/answer")
def generate_answer(req: SearchReq):
    print(">>> ANSWER ENDPOINT HIT <<<")
    if not req.query.strip():
        return {"error": "Empty query"}

    results = embed_search(req.query, req.doc_id, top_k=req.top_k)

    if not results:
        return {"error": "No indexed chunks found"}

    # ✅ context
    chunks = [r["chunk_text"] for r in results]
    context = "\n\n".join(chunks)

    if len(context) > 2000:
        context = context[:2000]

    # ✅ improved prompt
    prompt = f"""
Context:
{context}

Question: {req.query}

Answer briefly:
"""

    # ✅ better generation settings
    output = generator(
    prompt,
    max_length=150,
    do_sample=False
    )

    answer = output[0]["generated_text"].strip()

    # fallback safety
    if len(answer) < 5:
        answer = "Information not found in document."

    return {
        "answer": answer,
        "sources": [r["chunk_index"] for r in results]
    }
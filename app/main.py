# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import uuid
import os
from fastapi.middleware.cors import CORSMiddleware

from app.extract import extract_text_from_pdf
from app.embed import chunk_text as embed_chunk_text, generate_embeddings, save_index, search as embed_search, load_embeddings

from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    file_path = matching[0]
    try:
        text = extract_text_from_pdf(file_path)
    except Exception as e:
        return {"error": str(e)}
    preview = text[:2000]
    return {"doc_id": doc_id, "text_preview": preview, "length": len(text)}

@app.post("/process/{doc_id}")
def process_and_index(doc_id: str):
    matching = list(DATA_DIR.glob(f"{doc_id}_*"))
    if not matching:
        return {"error": "Document not found"}
    file_path = matching[0]

    try:
        full_text = extract_text_from_pdf(file_path)
    except Exception as e:
        return {"error": f"Failed to extract text: {str(e)}"}

    chunks = embed_chunk_text(full_text, chunk_size=300)

    if not chunks:
        return {"doc_id": doc_id, "status": "no_chunks_found"}

    try:
        embeddings = generate_embeddings(chunks)
    except Exception as e:
        return {"error": f"Failed to generate embeddings: {str(e)}"}

    try:
        save_index(embeddings, chunks, doc_id)
    except Exception as e:
        return {"error": f"Failed to save index files: {str(e)}"}

    return {"doc_id": doc_id, "chunks_indexed": len(chunks), "status": "indexed"}

class SearchReq(BaseModel):
    doc_id: str
    query: str
    top_k: int = 3

@app.post("/search")
def search_endpoint(req: SearchReq):
    if not req.query or not req.query.strip():
        return {"error": "Query is empty"}
    results = embed_search(req.query, req.doc_id, top_k=req.top_k)
    if results is None:
        return {"error": "Embeddings or chunks not found for this doc_id"}
    return {"doc_id": req.doc_id, "query": req.query, "results": results}

# @app.post("/answer")
# def answer_endpoint(req: SearchReq):
#     if not req.query or not req.query.strip():
#         return {"error": "Query is empty"}
#     results = embed_search(req.query, req.doc_id, top_k=req.top_k)
#     if not results:
#         return {"error": "No results or no index for this doc_id"}
#     chosen_chunks = [r["chunk_text"] for r in results]
#     sources = [r["chunk_index"] for r in results]
#     joined = "\n\n".join(chosen_chunks)
#     preview = joined[:3000]
#     return {
#         "doc_id": req.doc_id,
#         "query": req.query,
#         "answer_preview": preview,
#         "sources": sources,
#         "note": "Local concatenation of top-k chunks. Use an LLM for better synthesis."
#     }
@app.post("/answer")
def answer_endpoint(req: SearchReq):
    if not req.query or not req.query.strip():
        return {"error": "Query is empty"}

    # Get top-k relevant chunks
    results = embed_search(req.query, req.doc_id, top_k=req.top_k)
    if not results:
        return {"error": "No results or no index for this doc_id"}

    # Filter chunks by score threshold (only keep relevant ones)
    SCORE_THRESHOLD = 0.6
    filtered = [r for r in results if r["score"] >= SCORE_THRESHOLD]

    if not filtered:
        # fallback: return top chunk if none pass threshold
        filtered = [results[0]]

    # Prepare preview (concatenate, limited length)
    chunks_text = [r["chunk_text"] for r in filtered]
    preview = "\n\n".join(chunks_text)
    if len(preview) > 2000:
        preview = preview[:2000] + "..."

    # Return only relevant info
    return {
        "doc_id": req.doc_id,
        "query": req.query,
        "answer_preview": preview,
        "sources": [r["chunk_index"] for r in filtered],
        "note": "Top-k relevant chunks from document. Filtered by similarity score."
    }


# @app.post("/generate-answer")
# def generate_answer(req: SearchReq):
#     if not req.query.strip():
#         return {"error": "Empty query"}

#     # 1. Retrieve top chunks
#     results = embed_search(req.query, req.doc_id, top_k=req.top_k)
#     if not results:
#         return {"error": "No indexed chunks found for this document"}

#     # 2. Prepare context
#     context = "\n\n".join([r["chunk_text"] for r in results])

#     prompt = f"""
# You are an expert assistant. Use ONLY the context below to answer the question.
# If the answer is not in the context, say "Information not found".

# Context:
# {context}

# Question: {req.query}
# Answer:
# """

#     # 3. Call OpenAI LLM
#     response = client.chat.completions.create(
#         model="gpt-4.1-mini",
#         messages=[
#             {"role": "system", "content": "You answer using only provided context."},
#             {"role": "user", "content": prompt}
#         ]
#     )

#     answer = response.choices[0].message["content"]

#     return {
#         "doc_id": req.doc_id,
#         "query": req.query,
#         "answer": answer,
#         "sources": [r["chunk_index"] for r in results]
#     }

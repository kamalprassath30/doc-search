# 📄 Document Search (Local RAG System)

A local **Document Search & Question Answering system** built using **FastAPI + React**.
This project demonstrates the core ideas of **Retrieval-Augmented Generation (RAG)** without relying on paid LLM APIs.

---

## 🚀 Features

- Upload PDF documents
- Extract and preview document text
- Chunk and embed text using **SentenceTransformers**
- Semantic search using **cosine similarity**
- Retrieve most relevant document chunks for a query
- Fully local pipeline (no external LLM required)

---

## 🧠 How It Works (RAG – Retrieval Only)

1. PDF is uploaded and text is extracted
2. Text is split into chunks
3. Each chunk is converted into embeddings
4. User query is embedded
5. Top matching chunks are retrieved using similarity search

> This project focuses on **retrieval**, which is the core foundation of RAG systems.

---

## 🛠 Tech Stack

### Backend

- FastAPI
- SentenceTransformers
- Scikit-learn (KNN search)
- PDFPlumber

### Frontend

- React + TypeScript
- Axios

---

## 📂 Project Structure

// src/api.ts
import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post("/upload", formData);
};

export const extractText = (docId) => API.get(`/extract-text/${docId}`);
export const processDoc = (docId) => API.post(`/process/${docId}`);
export const searchAnswer = (docId, query, topK = 3) =>
  API.post("/answer", { doc_id: docId, query, top_k: topK });

export const generateAnswer = (docId, query, topK = 3) =>
  API.post("/generate-answer", { doc_id: docId, query, top_k: topK });

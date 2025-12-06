import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const uploadFile = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post("/upload", formData);
};

export const extractText = (docId: string) => API.get(`/extract-text${docId}`);
export const processDoc = (docId: string) => API.post(`/process/${docId}`);
export const searchAnswer = (docId: string, query: string, topK: number = 3) =>
  API.post("/answer", { doc_id: docId, query, top_k: topK });

export const generateAnswer = (
  docId: string,
  question: string,
  topK: number = 3
) => API.post("/generate-answer", { doc_id: docId, question, n_chunks: topK });

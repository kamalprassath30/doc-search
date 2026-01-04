const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  return res.json();
};

export const extractText = async (docId: string) => {
  const res = await fetch(`${BASE_URL}/extract-text/${docId}`);
  return res.json();
};

export const processDoc = async (docId: string) => {
  const res = await fetch(`${BASE_URL}/process/${docId}`, {
    method: "POST",
  });
  return res.json();
};

export const searchAnswer = async (docId: string, query: string, topK = 3) => {
  const res = await fetch(`${BASE_URL}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      doc_id: docId,
      query,
      top_k: topK,
    }),
  });

  return res.json();
};

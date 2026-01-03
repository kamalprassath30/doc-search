// src/components/UploadForm.tsx
import React, { useState } from "react";
import { uploadFile, processDoc, extractText } from "../api/api";

type UploadFormProps = {
  onUploaded: (id: string, filename: string) => void;
};

export default function UploadForm({ onUploaded }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<string>("");

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const res = await uploadFile(file);
      const doc_id = res.data.doc_id;
      const filename = res.data.filename;
      onUploaded(doc_id, filename);

      // Immediately process the document and fetch preview
      // await processDoc(doc_id);
      // const p = await extractText(doc_id);
      // setPreview(p.data.text_preview || "");
    } catch (err) {
      console.error(err);
      alert("Upload or processing failed. Check console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 8, fontWeight: 600 }}>Upload PDF</div>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          style={{
            background: "#2563eb",
            color: "#fff",
            border: "none",
            padding: "8px 12px",
            borderRadius: 6,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Uploading..." : "Upload & Process"}
        </button>
      </div>

      {preview && (
        <>
          <div style={{ marginTop: 10, color: "#6b7280" }}>Preview:</div>
          <div
            style={{
              marginTop: 6,
              background: "#fff",
              padding: 12,
              borderRadius: 6,
              border: "1px solid #e6e9ef",
              maxHeight: 220,
              overflow: "auto",
              whiteSpace: "pre-wrap",
            }}
          >
            {preview.slice(0, 1200)}
            {preview.length > 1200 ? "…" : ""}
          </div>
        </>
      )}
    </div>
  );
}

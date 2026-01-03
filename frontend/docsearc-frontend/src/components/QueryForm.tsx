import React, { useState } from "react";
import { searchAnswer } from "../api/api";

type QueryFormProps = {
  docId: string;
};

export default function QueryForm({ docId }: QueryFormProps) {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<any>(null);

  const ask = async () => {
    if (!docId) {
      alert("Please upload a document!");
      return;
    }
    if (!q.trim()) return;

    setLoading(true);
    try {
      const res = await searchAnswer(docId, q, 3);
      setAnswer(res.data);
    } catch (err) {
      console.error(err);
      alert("Search failed. Check console");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 8, fontWeight: 600 }}>Ask a question</div>

      <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
        <input
          placeholder="Type your question..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{
            flex: 1,
            padding: 10,
            borderRadius: 6,
            border: "1px solid #e6e9ef",
          }}
        />
        <button
          onClick={ask}
          disabled={loading}
          style={{
            background: "#2563eb",
            color: "#fff",
            padding: "9px 12px",
            borderRadius: 6,
            border: "none",
          }}
        >
          {loading ? "Searching..." : "Ask"}
        </button>
      </div>

      {answer && (
        <div>
          <div style={{ color: "#6b7280", marginBottom: 6 }}>
            Answer (preview):
          </div>
          <div style={{ marginTop: 8 }}>
            {answer.answer_preview.slice(0, 1000)}
          </div>
          <div style={{ marginTop: 8, color: "#6b7280" }}>
            Sources: {answer.sources?.join(", ")}
          </div>
        </div>
      )}
    </div>
  );
}

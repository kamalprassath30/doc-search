import React, { useState } from "react";
import { searchAnswer } from "../api/api";

export default function QueryForm({ doc }) {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState(null);

  const ask = async () => {
    if (!doc) {
      alert("Please upload a document!");
      return;
    }
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await searchAnswer(doc.doc_id, q, 3);
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
      <div
        style={{
          display: "flex",
          gap: 8,
          alignItems: "center",
          marginBottom: 10,
        }}
      >
        <input
          className="input"
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
          className="btn"
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
          <div className="result" style={{ marginTop: 8 }}>
            {answer.answer_preview}
          </div>
          <div style={{ marginTop: 8, color: "#6b7280" }}>
            Sources: {answer.sources?.join(", ")}
          </div>
        </div>
      )}
    </div>
  );
}

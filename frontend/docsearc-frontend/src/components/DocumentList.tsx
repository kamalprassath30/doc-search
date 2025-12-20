import React from "react";

interface DocumentListProps {
  documents: { docId: string; filename: string }[];
  onSelect: (docId: string) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, onSelect }) => {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "16px",
        borderRadius: "8px",
        marginBottom: "16px",
        backgroundColor: "#f0f0f0",
      }}
    >
      <h3>Uploaded Document</h3>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {documents.map((doc) => (
          <li key={doc.docId} style={{ marginBottom: "8px" }}>
            <button
              style={{
                padding: "8px 12px",
                cursor: "pointer",
                borderRadius: "4px",
                border: "1px solid #888",
                backgroundColor: "#fff",
              }}
              onClick={() => onSelect(doc.docId)}
            >
              {doc.filename}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DocumentList;

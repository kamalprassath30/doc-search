import React from "react";

interface AnswerCardProps {
  query: string;
  answer: string;
  sources: number[];
}

const AnswerCard: React.FC<AnswerCardProps> = ({ query, answer, sources }) => {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "16px",
        marginBottom: "16px",
        borderRadius: "8px",
        backgroundColor: "#f9f9f9",
      }}
    >
      <h3>Query:</h3>
      <p>{query}</p>

      <h3>Answer:</h3>
      <p>{answer}</p>

      <h4>Sources:</h4>
      <ul>
        {sources.map((s) => (
          <li key={s}>Chunk #{s}</li>
        ))}
      </ul>
    </div>
  );
};

export default AnswerCard;

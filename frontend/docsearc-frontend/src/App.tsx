import React, { use, useState } from "react";
import UploadForm from "./components/UploadForm";
import QueryForm from "./components/QueryForm";
import { extractText, processDoc } from "./api/api";
import DocumentList from "./components/DocumentList";
import AnswerCard from "./components/AnswerCard";

const App: React.FC = () => {
  const [docId, setDocId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string>("");
  const [textPreview, setTextPreview] = useState<string>("");
  const [processed, setProcessed] = useState(false);
  const [documents, setDocuments] = useState<
    { docId: String; filename: string }[]
  >([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [answers, setAnswers] = useState<
    { query: string; answer: string; sources: number[] }[]
  >([]);

  const handleUploaded = async (id: string, file: string) => {
    setDocId(id);
    setFilename(file);

    setDocuments((prev) => [{ docId: id, filename: file }, ...prev]);
    setSelectedDoc(id);

    try {
      const textRes = await extractText(id);
      setTextPreview(textRes.data.text_preview || "");
    } catch (e) {
      console.error("extractText failed", e);
      setTextPreview("");
    }

    try {
      const process = await processDoc(id);
      if (process.data.status == "indexed") setProcessed(true);
    } catch (e) {
      console.error("ProcessDoc failed", e);
      setProcessed(false);
    }
  };

  return (
    <div style={{ maxWidth: "980px", margin: "0 auto", padding: "20px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <h2>Document Search App</h2>
        <div style={{ color: "#6b7280" }}>Local RAG Demo</div>
      </div>

      <div
        style={{ display: "grid", gridTemplateColumns: "1fr 420px", gap: 20 }}
      >
        <div>
          <div className="card">
            <UploadForm onUploaded={handleUploaded} />
          </div>

          <div className="card">
            <h3>Search / Q&A</h3>
            {selectedDoc ? (
              processed ? (
                <QueryForm
                  docId={selectedDoc}
                  onAnswer={(ans) => setAnswers((s) => [ans, ...s])}
                />
              ) : (
                <div className="small">
                  Document indexed: {processed ? "Yes" : "No"}
                </div>
              )
            ) : (
              <div className="small">
                Upload and select a document to start asking questions.
              </div>
            )}

            {answers.map((a, i) => (
              <AnswerCard
                key={i}
                query={a.query}
                answer={a.answer}
                sources={a.sources}
              />
            ))}
          </div>
        </div>

        <div>
          <div className="card">
            <DocumentList
              documents={documents}
              onSelect={(id) => {
                setSelectedDoc(id);
                setDocId(id);
                setProcessed(true);
              }}
            />
          </div>

          <div className="card">
            <h4>Document Preview</h4>
            <div
              style={{ maxHeight: 240, overflow: "auto" }}
              className="result"
            >
              {textPreview || "No preview available."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;

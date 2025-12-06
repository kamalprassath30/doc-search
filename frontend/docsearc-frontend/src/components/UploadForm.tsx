import React, { useState } from "react";
import { uploadFile } from "../api/api";

interface UploadFormProps {
  onUploaded: (docId: string, filename: string) => void;
}

const UploadForm: React.FC<UploadFormProps> = ({ onUploaded }) => {
  const [file, setFile] = useState<file | null>(null);
  const [loading, setLoading] = useState(false);
  const handeUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const res = await uploadFile(file);
      onUploaded(res.data.doc_id, res.data.filename);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div>
      <input
        type="file"
        onChange={(e) => e.target.files && setFile(e.target.files[0])}
      />
      <button onClick={handeUpload} disabled={loading || !file}>
        {loading ? "Uploading..." : "Upload"}
      </button>
    </div>
  );
};

export default UploadForm;

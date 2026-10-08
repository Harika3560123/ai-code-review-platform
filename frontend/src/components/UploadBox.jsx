import React, { useRef, useState } from "react";
import { UploadCloud, FileCode, CheckCircle, AlertCircle } from "lucide-react";

export default function UploadBox({ onFileSelected, disabled = false }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const allowedExtensions = [".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".h"];

  const handleFiles = (files) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    const name = file.name.toLowerCase();
    const hasValidExt = allowedExtensions.some((ext) => name.endsWith(ext));

    if (!hasValidExt) {
      setError(`Unsupported file type. Allowed: ${allowedExtensions.join(", ")}`);
      setSelectedFile(null);
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      setError("File size exceeds maximum 2MB limit.");
      setSelectedFile(null);
      return;
    }

    setError("");
    setSelectedFile(file);
    onFileSelected(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;
    handleFiles(e.dataTransfer.files);
  };

  const handleChange = (e) => {
    handleFiles(e.target.files);
  };

  return (
    <div
      className={`upload-box ${dragOver ? "drag-over" : ""} ${disabled ? "disabled" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        type="file"
        ref={inputRef}
        onChange={handleChange}
        accept=".py,.js,.jsx,.ts,.tsx,.java,.cpp,.c,.h"
        style={{ display: "none" }}
        disabled={disabled}
      />

      <div className="upload-content">
        <UploadCloud size={32} className="upload-icon" />
        <div className="upload-text">
          {selectedFile ? (
            <div className="file-info">
              <FileCode size={18} />
              <span className="file-name">{selectedFile.name}</span>
              <span className="file-size">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
              <CheckCircle size={16} color="#10b981" />
            </div>
          ) : (
            <>
              <p className="upload-title">Drop your code file here, or <span className="browse-text">browse</span></p>
              <p className="upload-hint">Supports Python (.py), JavaScript (.js), Java (.java), C/C++ (max 2MB)</p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="upload-error">
          <AlertCircle size={14} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

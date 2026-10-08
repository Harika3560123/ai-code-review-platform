import React, { useState } from "react";
import CodeEditor from "../components/CodeEditor";
import LanguageSelector from "../components/LanguageSelector";
import UploadBox from "../components/UploadBox";
import AnalyzeButton from "../components/AnalyzeButton";
import ScoreCard from "../components/ScoreCard";
import IssueList from "../components/IssueList";
import IssueDetails from "../components/IssueDetails";
import { reviewService } from "../services/reviewService";
import { Sparkles, FileText, CheckCircle, AlertTriangle, Layers, Code, RefreshCw } from "lucide-react";

// Pre-packaged educational test samples for instant demonstration
const SAMPLES = {
  bad_python: `import os

def calculate_ratio(a, b):
    # Potential division by zero without check
    return a / b

def authenticate_user(username):
    # Hard-coded credential vulnerability
    api_key = "sk_live_998877665544332211"
    
    # SQL injection vulnerability via string concatenation
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    
    try:
        # Bare except bad practice
        print(f"Connecting with {api_key}")
    except:
        pass
        
    return query
`,
  good_python: `from typing import Optional
import logging

logger = logging.getLogger(__name__)

def calculate_ratio(numerator: float, denominator: float) -> Optional[float]:
    """Calculate ratio between two numbers safely with zero validation."""
    if denominator == 0:
        logger.warning("Attempted division by zero; returning None.")
        return None
    return numerator / denominator

def greet_user(name: str) -> str:
    """Format a clean greeting message for the user."""
    safe_name = name.strip()
    return f"Hello, {safe_name}!"
`,
  bad_javascript: `function runQuery(userInput) {
    // Hard-coded secret token
    const token = "ghp_secret_access_token_1234567890";

    // Dangerous eval execution
    eval("var x = " + userInput);

    // Unhandled promise
    fetch("/api/data").then(res => res.json());

    return token;
}
`
};

export default function Review() {
  const [inputMode, setInputMode] = useState("paste"); // "paste" or "upload"
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(SAMPLES.bad_python);
  const [filename, setFilename] = useState("main.py");
  const [uploadedFile, setUploadedFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reviewResult, setReviewResult] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);

  const handleLoadSample = (sampleKey, lang, fname) => {
    setCode(SAMPLES[sampleKey]);
    setLanguage(lang);
    setFilename(fname);
    setInputMode("paste");
    setReviewResult(null);
    setSelectedIssue(null);
    setError("");
  };

  const handleFileSelected = (file) => {
    setUploadedFile(file);
    setFilename(file.name);
    // Read content into editor preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setCode(e.target.result);
    };
    reader.readAsText(file);
  };

  const handleAnalyze = async () => {
    setError("");
    setLoading(true);
    setReviewResult(null);
    setSelectedIssue(null);

    try {
      let result;
      if (inputMode === "upload" && uploadedFile) {
        result = await reviewService.uploadCodeFile(uploadedFile, language);
      } else {
        if (!code || !code.trim()) {
          setError("Source code cannot be empty. Please paste code or upload a file.");
          setLoading(false);
          return;
        }
        result = await reviewService.analyzeCode(code, language, filename);
      }

      setReviewResult(result);
      if (result.issues && result.issues.length > 0) {
        setSelectedIssue(result.issues[0]);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || "Code analysis failed. Check backend connection.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFix = (original, corrected) => {
    if (code.includes(original)) {
      setCode(code.replace(original, corrected));
      alert("Fix applied directly to editor!");
    } else {
      setCode(corrected);
      alert("Updated editor with corrected implementation!");
    }
  };

  return (
    <div className="review-page">
      <div className="review-header-bar">
        <div>
          <h2>AI Code Review Studio</h2>
          <p>Inspect syntax, logical bugs, runtime risks, security flaws, and code health with Explainable AI</p>
        </div>

        {/* Demo Sample Quick Selectors */}
        <div className="sample-buttons">
          <span className="sample-label">Load Test Case:</span>
          <button
            onClick={() => handleLoadSample("bad_python", "python", "bad_python.py")}
            className="btn-sample"
          >
            Defective Python
          </button>
          <button
            onClick={() => handleLoadSample("good_python", "python", "good_python.py")}
            className="btn-sample"
          >
            Clean Python
          </button>
          <button
            onClick={() => handleLoadSample("bad_javascript", "javascript", "bad_script.js")}
            className="btn-sample"
          >
            Defective JS
          </button>
        </div>
      </div>

      {error && <div className="alert-box error">{error}</div>}

      {/* Input Controls Bar */}
      <div className="input-control-strip">
        <div className="input-tabs">
          <button
            className={`tab-btn ${inputMode === "paste" ? "active" : ""}`}
            onClick={() => setInputMode("paste")}
          >
            <Code size={16} />
            <span>Paste / Edit Code</span>
          </button>
          <button
            className={`tab-btn ${inputMode === "upload" ? "active" : ""}`}
            onClick={() => setInputMode("upload")}
          >
            <FileText size={16} />
            <span>Upload File</span>
          </button>
        </div>

        <LanguageSelector language={language} setLanguage={setLanguage} disabled={loading} />
      </div>

      {/* Editor & Upload View */}
      {inputMode === "upload" && (
        <div className="upload-container-wrapper">
          <UploadBox onFileSelected={handleFileSelected} disabled={loading} />
        </div>
      )}

      <div className="editor-wrapper">
        <div className="editor-file-info">
          <span>Editing: <strong>{filename}</strong></span>
          <span className="lang-indicator">{language.toUpperCase()}</span>
        </div>
        <CodeEditor
          code={code}
          onChange={setCode}
          language={language}
          readOnly={loading}
        />
      </div>

      {/* Trigger Analyze Action */}
      <div className="analyze-action-bar">
        <AnalyzeButton onClick={handleAnalyze} loading={loading} />
      </div>

      {/* Analysis Results View */}
      {reviewResult && (
        <div className="review-results-section">
          <div className="results-header">
            <h3>Analysis Report #{reviewResult.review_id}</h3>
            {reviewResult.analyzer_status?.llm && (
              <span className="analyzer-note" title={reviewResult.analyzer_status.llm}>
                AI Engine: {reviewResult.analyzer_status.llm}
              </span>
            )}
          </div>

          {/* Scorecards */}
          <ScoreCard scores={reviewResult.scores} summary={reviewResult.summary} />

          {/* Finding Breakdown: List on Left, Deep Explainable AI on Right */}
          <div className="findings-workspace-grid">
            <div className="findings-sidebar">
              <h4>Findings & Anomalies ({reviewResult.issues?.length || 0})</h4>
              <IssueList
                issues={reviewResult.issues}
                selectedIssue={selectedIssue}
                onSelectIssue={setSelectedIssue}
              />
            </div>

            <div className="findings-main-detail">
              <IssueDetails
                issue={selectedIssue}
                onApplyFix={handleApplyFix}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

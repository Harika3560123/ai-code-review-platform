import React, { useState } from "react";
import { HelpCircle, MapPin, AlertCircle, FileSearch, Sparkles, ExternalLink, Code2 } from "lucide-react";
import CodeDiff from "./CodeDiff";

export default function IssueDetails({ issue, onApplyFix }) {
  const [showDiff, setShowDiff] = useState(false);

  if (!issue) {
    return (
      <div className="empty-details">
        <HelpCircle size={40} className="empty-icon" />
        <p>Select a finding from the list on the left to inspect explainable AI details.</p>
      </div>
    );
  }

  const confidencePct = Math.round((issue.confidence || 0.85) * 100);

  return (
    <div className="issue-details-container">
      {/* Detail Header */}
      <div className="details-header">
        <div>
          <span className="details-type">{issue.issue_type?.toUpperCase()}</span>
          <h3 className="details-title">{issue.title}</h3>
        </div>
        <div className="details-meta">
          <div className="confidence-pill" title="System confidence indicator">
            <span className="conf-label">Confidence</span>
            <span className="conf-value">{confidencePct}%</span>
          </div>
          <span className={`severity-tag badge-${(issue.severity || "low").toLowerCase()}`}>
            {issue.severity}
          </span>
        </div>
      </div>

      <div className="confidence-notice">
        ℹ️ <em>Confidence is an automated system confidence indicator based on static rules and AI corroboration.</em>
      </div>

      {/* 5-Dimension XAI Answers */}
      <div className="xai-sections">
        {/* WHAT & WHERE */}
        <div className="xai-card">
          <div className="xai-title">
            <MapPin size={18} color="#6366f1" />
            <span>WHERE & WHAT Happened?</span>
          </div>
          <div className="xai-content">
            <p><strong>Location:</strong> Line {issue.line || issue.line_number || "Unknown"}</p>
            <p>{issue.message || "An anomalous code construct was identified."}</p>
          </div>
        </div>

        {/* WHY IS IT A PROBLEM (Cause & Impact) */}
        <div className="xai-card">
          <div className="xai-title">
            <AlertCircle size={18} color="#f59e0b" />
            <span>WHY is it a problem? (Impact)</span>
          </div>
          <div className="xai-content">
            <p>{issue.explanation}</p>
          </div>
        </div>

        {/* WHAT IS THE EVIDENCE? */}
        <div className="xai-card">
          <div className="xai-title">
            <FileSearch size={18} color="#3b82f6" />
            <span>WHAT is the evidence?</span>
          </div>
          <div className="xai-content">
            <pre className="code-evidence">
              <code>{issue.evidence || "Direct AST pattern matching"}</code>
            </pre>
          </div>
        </div>

        {/* HOW CAN IT BE FIXED? */}
        <div className="xai-card fix-card">
          <div className="xai-title">
            <Sparkles size={18} color="#10b981" />
            <span>HOW can it be fixed?</span>
          </div>
          <div className="xai-content">
            <p className="rec-text">{issue.suggestion?.recommendation || "Follow secure refactoring guidelines."}</p>

            <div className="fix-actions">
              <button
                className="btn-toggle-fix"
                onClick={() => setShowDiff(!showDiff)}
              >
                <Code2 size={16} />
                <span>{showDiff ? "Hide Code Diff" : "Show Corrected Code & Diff"}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Diff Component */}
      {showDiff && (
        <div className="diff-wrapper">
          <CodeDiff
            originalCode={issue.suggestion?.original_code || issue.evidence || ""}
            correctedCode={issue.suggestion?.corrected_code || ""}
            recommendation={issue.suggestion?.recommendation}
            onApplyFix={onApplyFix}
          />
        </div>
      )}
    </div>
  );
}

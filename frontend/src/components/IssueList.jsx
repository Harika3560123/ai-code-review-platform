import React, { useState } from "react";
import { AlertCircle, ShieldAlert, Cpu, CheckCircle } from "lucide-react";

export default function IssueList({ issues = [], selectedIssue, onSelectIssue }) {
  const [filterSeverity, setFilterSeverity] = useState("ALL");

  const filteredIssues = issues.filter((issue) => {
    if (filterSeverity === "ALL") return true;
    return (issue.severity || "").toUpperCase() === filterSeverity;
  });

  const getSeverityBadgeClass = (sev) => {
    switch ((sev || "").toUpperCase()) {
      case "CRITICAL":
        return "badge-critical";
      case "HIGH":
        return "badge-high";
      case "MEDIUM":
        return "badge-medium";
      case "LOW":
        return "badge-low";
      default:
        return "badge-info";
    }
  };

  if (!issues || issues.length === 0) {
    return (
      <div className="empty-issues">
        <CheckCircle size={36} color="#10b981" />
        <h4>Clean Code!</h4>
        <p>No critical, security, or logical errors were detected in this analysis.</p>
      </div>
    );
  }

  return (
    <div className="issue-list-container">
      <div className="issue-filter-bar">
        <span>Filter:</span>
        {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((sev) => (
          <button
            key={sev}
            className={`filter-btn ${filterSeverity === sev ? "active" : ""}`}
            onClick={() => setFilterSeverity(sev)}
          >
            {sev}
          </button>
        ))}
      </div>

      <div className="issues-scroll">
        {filteredIssues.map((issue, idx) => {
          const isSelected = selectedIssue?.finding_id
            ? selectedIssue.finding_id === issue.finding_id
            : selectedIssue === issue || (idx === 0 && !selectedIssue);

          return (
            <div
              key={issue.finding_id || idx}
              className={`issue-item ${isSelected ? "selected" : ""}`}
              onClick={() => onSelectIssue(issue)}
            >
              <div className="issue-item-header">
                <span className="line-tag">Line {issue.line || issue.line_number || "—"}</span>
                <span className={`severity-tag ${getSeverityBadgeClass(issue.severity)}`}>
                  {issue.severity}
                </span>
                <div className="sources-tags">
                  {(issue.sources || ["static"]).map((src, sIdx) => (
                    <span key={sIdx} className={`source-tag ${src}`}>
                      {src}
                    </span>
                  ))}
                </div>
              </div>

              <h4 className="issue-title">{issue.title}</h4>
              <p className="issue-snippet">{issue.message || issue.explanation}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

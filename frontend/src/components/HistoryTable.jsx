import React from "react";
import { Link } from "react-router-dom";
import { Eye, Clock, FileCode, CheckCircle2 } from "lucide-react";

export default function HistoryTable({ reviews = [] }) {
  if (!reviews || reviews.length === 0) {
    return (
      <div className="empty-history">
        <Clock size={36} className="empty-icon" />
        <p>No past reviews found. Analyze a code snippet or upload a file to start tracking reviews!</p>
      </div>
    );
  }

  const getScoreBadgeClass = (score) => {
    if (score >= 85) return "badge-success";
    if (score >= 60) return "badge-warning";
    return "badge-danger";
  };

  return (
    <div className="history-table-wrapper">
      <table className="history-table">
        <thead>
          <tr>
            <th>Review ID</th>
            <th>File / Module</th>
            <th>Language</th>
            <th>Quality Score</th>
            <th>Critical / High</th>
            <th>Analyzed At</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {reviews.map((r) => {
            const dateStr = new Date(r.created_at).toLocaleString();
            return (
              <tr key={r.review_id}>
                <td className="rev-id">#REV-{r.review_id}</td>
                <td className="rev-file">
                  <FileCode size={16} />
                  <span>{r.filename || "code_snippet"}</span>
                </td>
                <td>
                  <span className={`lang-badge lang-${r.language.toLowerCase()}`}>
                    {r.language}
                  </span>
                </td>
                <td>
                  <span className={`score-badge ${getScoreBadgeClass(r.overall_score)}`}>
                    {Math.round(r.overall_score)} / 100
                  </span>
                </td>
                <td>
                  <span className="issues-indicator">
                    <strong className="text-danger">{r.summary?.critical || 0}</strong> crit,{" "}
                    <strong className="text-warning">{r.summary?.high || 0}</strong> high
                  </span>
                </td>
                <td className="rev-date">{dateStr}</td>
                <td>
                  <Link to={`/review/${r.review_id}`} className="btn-view-review">
                    <Eye size={14} />
                    <span>View</span>
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

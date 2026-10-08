import React from "react";
import { Shield, CheckCircle2, Wrench, Sparkles, Cpu, AlertTriangle, AlertOctagon, Info } from "lucide-react";

export default function ScoreCard({ scores, summary }) {
  if (!scores) return null;

  const overall = Math.round(scores.overall || 0);

  const getScoreColor = (val) => {
    if (val >= 85) return "text-success";
    if (val >= 60) return "text-warning";
    return "text-danger";
  };

  const getScoreBg = (val) => {
    if (val >= 85) return "#10b981";
    if (val >= 60) return "#f59e0b";
    return "#ef4444";
  };

  const dimensions = [
    { label: "Security (25%)", value: scores.security || 100, icon: <Shield size={16} /> },
    { label: "Correctness (30%)", value: scores.correctness || 100, icon: <CheckCircle2 size={16} /> },
    { label: "Maintainability (20%)", value: scores.maintainability || 100, icon: <Wrench size={16} /> },
    { label: "Style (10%)", value: scores.style || 100, icon: <Sparkles size={16} /> },
    { label: "Complexity (15%)", value: scores.complexity || 100, icon: <Cpu size={16} /> },
  ];

  return (
    <div className="scorecard-container">
      {/* Overall Score Circle */}
      <div className="overall-score-panel">
        <div className="score-circle" style={{ borderColor: getScoreBg(overall) }}>
          <span className={`score-number ${getScoreColor(overall)}`}>{overall}</span>
          <span className="score-max">/ 100</span>
        </div>
        <div className="overall-label">
          <h4>Code Quality Score</h4>
          <p className="score-verdict">
            {overall >= 85 ? "Excellent Code Health" : overall >= 60 ? "Needs Remediation" : "Critical Deficiencies Found"}
          </p>
        </div>
      </div>

      {/* 5-Dimension Score Progress Bars */}
      <div className="dimensions-panel">
        <h5>Dimension Breakdown</h5>
        <div className="dimensions-list">
          {dimensions.map((dim, idx) => (
            <div key={idx} className="dimension-row">
              <div className="dim-header">
                <span className="dim-icon-title">
                  {dim.icon}
                  <span>{dim.label}</span>
                </span>
                <span className="dim-value">{Math.round(dim.value)}%</span>
              </div>
              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{
                    width: `${Math.max(5, Math.min(100, dim.value))}%`,
                    backgroundColor: getScoreBg(dim.value)
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Severity Counters */}
      <div className="severity-summary-panel">
        <h5>Issue Distribution</h5>
        <div className="severity-badges">
          <div className="sev-badge critical">
            <AlertOctagon size={16} />
            <div className="sev-text">
              <span className="count">{summary?.critical || 0}</span>
              <span className="label">Critical</span>
            </div>
          </div>

          <div className="sev-badge high">
            <AlertTriangle size={16} />
            <div className="sev-text">
              <span className="count">{summary?.high || 0}</span>
              <span className="label">High</span>
            </div>
          </div>

          <div className="sev-badge medium">
            <AlertTriangle size={16} />
            <div className="sev-text">
              <span className="count">{summary?.medium || 0}</span>
              <span className="label">Medium</span>
            </div>
          </div>

          <div className="sev-badge low">
            <Info size={16} />
            <div className="sev-text">
              <span className="count">{summary?.low || 0}</span>
              <span className="label">Low</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

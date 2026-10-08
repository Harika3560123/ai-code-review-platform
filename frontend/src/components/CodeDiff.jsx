import React, { useState } from "react";
import { Copy, Check, ArrowRight } from "lucide-react";

export default function CodeDiff({ originalCode, correctedCode, recommendation, onApplyFix }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(correctedCode || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="diff-container">
      <div className="diff-header">
        <h4>Remediation Comparison</h4>
        <div className="diff-actions">
          <button onClick={handleCopy} className="btn-copy">
            {copied ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
            <span>{copied ? "Copied!" : "Copy Suggested Fix"}</span>
          </button>
          {onApplyFix && (
            <button
              onClick={() => onApplyFix(originalCode, correctedCode)}
              className="btn-apply"
            >
              Apply to Editor
            </button>
          )}
        </div>
      </div>

      <div className="diff-grid">
        <div className="diff-box original">
          <div className="diff-box-title">Original Problematic Code</div>
          <pre className="diff-code">
            <code>{originalCode || "(No snippet available)"}</code>
          </pre>
        </div>

        <div className="diff-arrow">
          <ArrowRight size={20} />
        </div>

        <div className="diff-box corrected">
          <div className="diff-box-title">Suggested Corrected Code</div>
          <pre className="diff-code">
            <code>{correctedCode || "(No automated replacement generated)"}</code>
          </pre>
        </div>
      </div>

      {recommendation && (
        <div className="diff-recommendation">
          <strong>Recommendation:</strong> {recommendation}
        </div>
      )}
    </div>
  );
}

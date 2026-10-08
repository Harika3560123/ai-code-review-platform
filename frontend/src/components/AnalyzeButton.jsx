import React from "react";
import { Play, Loader2 } from "lucide-react";

export default function AnalyzeButton({ onClick, loading = false, disabled = false }) {
  return (
    <button
      className={`btn-analyze ${loading ? "loading" : ""}`}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? (
        <>
          <Loader2 size={18} className="spin-icon" />
          <span>Analyzing Code & Running AI...</span>
        </>
      ) : (
        <>
          <Play size={18} fill="currentColor" />
          <span>ANALYZE CODE</span>
        </>
      )}
    </button>
  );
}

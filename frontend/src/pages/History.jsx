import React, { useEffect, useState } from "react";
import { reviewService } from "../services/reviewService";
import HistoryTable from "../components/HistoryTable";
import { History as HistoryIcon, Loader2, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

export default function History() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true);
        const data = await reviewService.getReviewHistory();
        setReviews(data);
      } catch (err) {
        setError("Failed to fetch review history from backend.");
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  return (
    <div className="history-page">
      <div className="history-header">
        <div>
          <h2>Code Review History</h2>
          <p>Review past code assessments, audit quality scores, and inspect historical AI recommendations</p>
        </div>
        <Link to="/review" className="btn-primary-action">
          <Sparkles size={16} />
          <span>New Review</span>
        </Link>
      </div>

      {error && <div className="alert-box error">{error}</div>}

      {loading ? (
        <div className="loading-container">
          <Loader2 size={32} className="spin-icon" />
          <p>Loading review history...</p>
        </div>
      ) : (
        <HistoryTable reviews={reviews} />
      )}
    </div>
  );
}

import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { reviewService } from "../services/reviewService";
import ScoreCard from "../components/ScoreCard";
import IssueList from "../components/IssueList";
import IssueDetails from "../components/IssueDetails";
import { ArrowLeft, FileCode, Clock, ShieldCheck, Loader2 } from "lucide-react";

export default function ReviewDetails() {
  const { id } = useParams();
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedIssue, setSelectedIssue] = useState(null);

  useEffect(() => {
    async function loadReview() {
      try {
        setLoading(true);
        const data = await reviewService.getReviewById(id);
        setReview(data);
        if (data.issues && data.issues.length > 0) {
          setSelectedIssue(data.issues[0]);
        }
      } catch (err) {
        setError(`Failed to load review #${id}. Verify the review ID.`);
      } finally {
        setLoading(false);
      }
    }
    loadReview();
  }, [id]);

  if (loading) {
    return (
      <div className="loading-container">
        <Loader2 size={32} className="spin-icon" />
        <p>Retrieving Review Report #{id} from database...</p>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="error-container">
        <p className="error-msg">{error || "Review not found."}</p>
        <Link to="/history" className="btn-secondary">
          Back to Review History
        </Link>
      </div>
    );
  }

  return (
    <div className="review-details-page">
      <div className="details-nav-bar">
        <Link to="/history" className="btn-back">
          <ArrowLeft size={16} />
          <span>Back to History</span>
        </Link>

        <div className="review-meta-pills">
          <span className="meta-pill">
            <FileCode size={14} />
            <span>{review.filename || "code_snippet"}</span>
          </span>
          <span className="meta-pill">
            <ShieldCheck size={14} />
            <span>{review.language?.toUpperCase()}</span>
          </span>
          {review.created_at && (
            <span className="meta-pill">
              <Clock size={14} />
              <span>{new Date(review.created_at).toLocaleString()}</span>
            </span>
          )}
        </div>
      </div>

      <div className="review-title-section">
        <h2>Report for Review #{review.review_id}</h2>
      </div>

      {/* Quality Scorecard */}
      <ScoreCard scores={review.scores} summary={review.summary} />

      {/* Findings Breakdown */}
      <div className="findings-workspace-grid">
        <div className="findings-sidebar">
          <h4>Detected Issues ({review.issues?.length || 0})</h4>
          <IssueList
            issues={review.issues}
            selectedIssue={selectedIssue}
            onSelectIssue={setSelectedIssue}
          />
        </div>

        <div className="findings-main-detail">
          <IssueDetails issue={selectedIssue} />
        </div>
      </div>
    </div>
  );
}

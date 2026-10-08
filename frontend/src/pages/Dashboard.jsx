import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { reviewService } from "../services/reviewService";
import { useAuth } from "../hooks/useAuth";
import {
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  FileCode,
  ArrowRight,
  TrendingUp,
  Cpu,
  Layers,
  Sparkles
} from "lucide-react";

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadStats() {
      try {
        setLoading(true);
        const data = await reviewService.getDashboardStatistics();
        setStats(data);
      } catch (err) {
        setError("Failed to fetch dashboard statistics. Verify backend status.");
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="dashboard-page">
      {/* Welcome Banner */}
      <div className="dash-hero">
        <div className="hero-text">
          <h1>Welcome, {user?.name || "Developer"}</h1>
          <p>
            AI-Powered Code Review and Error Detection Platform Using Explainable AI.
            Inspect logic errors, runtime risks, security flaws, and code health with AI reasoning.
          </p>
        </div>
        <div className="hero-action">
          <Link to="/review" className="btn-primary-action">
            <Sparkles size={18} />
            <span>Launch Code Review Studio</span>
          </Link>
        </div>
      </div>

      {error && <div className="alert-box error">{error}</div>}

      {/* KPI Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon-wrap bg-indigo">
            <Layers size={22} color="#6366f1" />
          </div>
          <div className="stat-info">
            <span className="stat-title">Total Reviews Analyzed</span>
            <span className="stat-value">{stats?.total_reviews || 0}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrap bg-green">
            <CheckCircle2 size={22} color="#10b981" />
          </div>
          <div className="stat-info">
            <span className="stat-title">Average Quality Score</span>
            <span className="stat-value">{stats ? `${Math.round(stats.average_score)}%` : "100%"}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrap bg-red">
            <AlertOctagon size={22} color="#ef4444" />
          </div>
          <div className="stat-info">
            <span className="stat-title">Critical Vulnerabilities</span>
            <span className="stat-value text-danger">{stats?.severity_counts?.critical || 0}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrap bg-amber">
            <AlertTriangle size={22} color="#f59e0b" />
          </div>
          <div className="stat-info">
            <span className="stat-title">High Priority Bugs</span>
            <span className="stat-value text-warning">{stats?.severity_counts?.high || 0}</span>
          </div>
        </div>
      </div>

      {/* Middle Row: Severity & Issue Category Breakdown */}
      <div className="dash-breakdown-grid">
        <div className="dash-panel">
          <div className="panel-header">
            <h3>Severity Distribution</h3>
          </div>
          <div className="panel-body">
            <div className="distribution-list">
              <div className="dist-item">
                <span className="dist-label text-danger">Critical Severity</span>
                <span className="dist-badge bg-danger">{stats?.severity_counts?.critical || 0}</span>
              </div>
              <div className="dist-item">
                <span className="dist-label text-warning">High Severity</span>
                <span className="dist-badge bg-warning">{stats?.severity_counts?.high || 0}</span>
              </div>
              <div className="dist-item">
                <span className="dist-label text-amber">Medium Severity</span>
                <span className="dist-badge bg-amber">{stats?.severity_counts?.medium || 0}</span>
              </div>
              <div className="dist-item">
                <span className="dist-label text-blue">Low Severity</span>
                <span className="dist-badge bg-blue">{stats?.severity_counts?.low || 0}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="dash-panel">
          <div className="panel-header">
            <h3>Language Coverage</h3>
          </div>
          <div className="panel-body">
            {stats?.language_counts && Object.keys(stats.language_counts).length > 0 ? (
              <div className="lang-list">
                {Object.entries(stats.language_counts).map(([lang, count]) => (
                  <div key={lang} className="lang-row">
                    <span className="lang-name">{lang.toUpperCase()}</span>
                    <span className="lang-count">{count} reviews</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-text">No reviews recorded yet. Start your first review above!</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Reviews Table */}
      <div className="dash-panel">
        <div className="panel-header space-between">
          <h3>Recent Code Reviews</h3>
          <Link to="/history" className="link-subtle">
            <span>View All History</span>
            <ArrowRight size={14} />
          </Link>
        </div>
        <div className="panel-body">
          {stats?.recent_reviews && stats.recent_reviews.length > 0 ? (
            <div className="table-responsive">
              <table className="recent-table">
                <thead>
                  <tr>
                    <th>Review ID</th>
                    <th>File</th>
                    <th>Language</th>
                    <th>Score</th>
                    <th>Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent_reviews.map((r) => (
                    <tr key={r.review_id}>
                      <td className="rev-id">#REV-{r.review_id}</td>
                      <td>
                        <div className="file-cell">
                          <FileCode size={16} />
                          <span>{r.filename}</span>
                        </div>
                      </td>
                      <td>
                        <span className="badge-lang">{r.language}</span>
                      </td>
                      <td>
                        <span className={`score-tag ${r.score >= 85 ? "good" : r.score >= 60 ? "med" : "bad"}`}>
                          {Math.round(r.score)}%
                        </span>
                      </td>
                      <td>{r.created_at}</td>
                      <td>
                        <Link to={`/review/${r.review_id}`} className="btn-table-action">
                          Inspect
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <p>No recent reviews. Click below to analyze your first code file.</p>
              <Link to="/review" className="btn-secondary">
                Start Code Review
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

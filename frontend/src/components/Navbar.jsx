import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ShieldCheck, Code, History, BarChart2, User, LogOut, LogIn } from "lucide-react";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="brand">
          <div className="brand-icon">
            <ShieldCheck size={26} color="#6366f1" />
          </div>
          <div className="brand-text">
            <span className="brand-title">AI CODE REVIEW</span>
            <span className="brand-subtitle">Explainable AI Platform</span>
          </div>
        </Link>

        <nav className="nav-links">
          <Link to="/dashboard" className={`nav-item ${isActive("/dashboard") ? "active" : ""}`}>
            <BarChart2 size={18} />
            <span>Dashboard</span>
          </Link>
          <Link to="/review" className={`nav-item ${isActive("/review") ? "active" : ""}`}>
            <Code size={18} />
            <span>Code Review</span>
          </Link>
          <Link to="/history" className={`nav-item ${isActive("/history") ? "active" : ""}`}>
            <History size={18} />
            <span>History</span>
          </Link>
          {isAuthenticated && (
            <Link to="/profile" className={`nav-item ${isActive("/profile") ? "active" : ""}`}>
              <User size={18} />
              <span>Profile</span>
            </Link>
          )}
        </nav>

        <div className="nav-actions">
          {isAuthenticated ? (
            <div className="user-section">
              <span className="user-badge" title={user?.email}>
                {user?.name || "Developer"}
              </span>
              <button onClick={handleLogout} className="btn-logout" title="Log Out">
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div className="auth-btns">
              <Link to="/login" className="btn-login">
                <LogIn size={16} />
                <span>Login</span>
              </Link>
              <Link to="/register" className="btn-register">
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

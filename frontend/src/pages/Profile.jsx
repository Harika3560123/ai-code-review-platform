import React, { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { authService } from "../services/authService";
import { User, Mail, Calendar, Shield, LogOut, CheckCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await authService.fetchProfile();
        setProfile(data);
      } catch (err) {
        // Fall back to local user state
        setProfile(user);
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, [user]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="profile-page">
      <div className="profile-card">
        <div className="profile-avatar-wrap">
          <div className="profile-avatar">
            <User size={40} color="#6366f1" />
          </div>
          <h2>{profile?.name || user?.name || "Developer"}</h2>
          <span className="profile-role">Software Engineer / Student</span>
        </div>

        <div className="profile-info-grid">
          <div className="info-item">
            <Mail size={18} className="info-icon" />
            <div>
              <span className="info-label">Email Address</span>
              <span className="info-val">{profile?.email || user?.email}</span>
            </div>
          </div>

          <div className="info-item">
            <Calendar size={18} className="info-icon" />
            <div>
              <span className="info-label">Member Since</span>
              <span className="info-val">
                {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : "Active Session"}
              </span>
            </div>
          </div>

          <div className="info-item">
            <Shield size={18} className="info-icon" />
            <div>
              <span className="info-label">Authentication</span>
              <span className="info-val text-success">
                <CheckCircle size={14} style={{ display: "inline", marginRight: "4px" }} />
                JWT Bearer Verified
              </span>
            </div>
          </div>
        </div>

        <div className="profile-actions">
          <button onClick={handleLogout} className="btn-logout-full">
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  );
}

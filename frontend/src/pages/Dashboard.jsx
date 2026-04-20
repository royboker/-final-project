import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { api } from "../lib/api";
import Navbar from "../components/Navbar";
import "./Dashboard.css";

import { API_URL } from "../config.js";

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const toast = useToast();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.getMyScans(token);
        setScans(res.scans || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [token]);

  const totalScans = scans.length;
  const realCount = scans.filter(s => s.verdict === "Real").length;
  const fakeCount = scans.filter(s => s.verdict?.startsWith("Fake")).length;
  const classifyOnly = totalScans - realCount - fakeCount;

  const recentScans = scans.slice(0, 8);

  async function downloadReport(scanId) {
    const res = await fetch(`${API_URL}/scans/${scanId}/report`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) { toast({ message: "Failed to download report", type: "error" }); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `docuguard-report-${scanId.slice(0, 8)}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <Navbar />
      <div className="dash-page">
        {/* Header */}
        <div className="dash-header">
          <div>
            <h1>Welcome back, {user?.name?.split(" ")[0] || "User"}</h1>
            <p>Here's an overview of your document analysis activity</p>
          </div>
          <button className="dash-scan-btn" onClick={() => navigate("/scan")}>
            + New Scan
          </button>
        </div>

        {/* Stats */}
        <div className="dash-stats">
          <div className="dash-stat-card">
            <span className="dash-stat-num">{totalScans}</span>
            <span className="dash-stat-label">Total Scans</span>
          </div>
          <div className="dash-stat-card stat-real">
            <span className="dash-stat-num">{realCount}</span>
            <span className="dash-stat-label">Authentic</span>
          </div>
          <div className="dash-stat-card stat-fake">
            <span className="dash-stat-num">{fakeCount}</span>
            <span className="dash-stat-label">Forged</span>
          </div>
          <div className="dash-stat-card stat-classify">
            <span className="dash-stat-num">{classifyOnly}</span>
            <span className="dash-stat-label">Classified</span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="dash-actions">
          <div className="dash-action-card" onClick={() => navigate("/scan")}>
            <div className="dash-action-icon">
              <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
              </svg>
            </div>
            <div className="dash-action-text">
              <span className="dash-action-title">Scan Document</span>
              <span className="dash-action-sub">Upload and analyze a new document</span>
            </div>
          </div>
          <div className="dash-action-card" onClick={() => navigate("/profile")}>
            <div className="dash-action-icon icon-profile">
              <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <div className="dash-action-text">
              <span className="dash-action-title">My Profile</span>
              <span className="dash-action-sub">View account settings and security</span>
            </div>
          </div>
        </div>

        {/* Recent Scans */}
        <div className="dash-recent">
          <div className="dash-recent-header">
            <h2>Recent Scans</h2>
            {scans.length > 0 && (
              <button className="dash-view-all" onClick={() => navigate("/profile")}>
                View all
              </button>
            )}
          </div>

          {loading ? (
            <div className="dash-loading">Loading...</div>
          ) : recentScans.length === 0 ? (
            <div className="dash-empty">
              <div className="dash-empty-icon">
                <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>
                </svg>
              </div>
              <p className="dash-empty-title">No scans yet</p>
              <p className="dash-empty-sub">Upload your first document to get started</p>
              <button className="dash-scan-btn small" onClick={() => navigate("/scan")}>
                Scan your first document
              </button>
            </div>
          ) : (
            <div className="dash-scan-list">
              {recentScans.map((scan) => (
                <div key={scan.id} className="dash-scan-row">
                  <div className="dash-scan-info">
                    <span className="dash-scan-name">{scan.file_name || "Document"}</span>
                    <span className="dash-scan-date">
                      {scan.scanned_at ? new Date(scan.scanned_at).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : ""}
                    </span>
                  </div>
                  <div className="dash-scan-meta">
                    <span className="dash-scan-doctype">{scan.doc_type || "—"}</span>
                    {scan.verdict && scan.verdict !== "Classification only" && (
                      <span className={`dash-scan-verdict ${scan.verdict === "Real" ? "v-real" : "v-fake"}`}>
                        {scan.verdict}
                      </span>
                    )}
                    {scan.confidence != null && (
                      <span className="dash-scan-conf">{(scan.confidence * 100).toFixed(0)}%</span>
                    )}
                  </div>
                  <button className="dash-scan-dl" onClick={() => downloadReport(scan.id)} title="Download report">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

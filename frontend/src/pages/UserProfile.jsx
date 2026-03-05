import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { profileApi, api } from "../lib/api";
import Navbar from "../components/Navbar";
import "./UserProfile.css";

import { API_URL } from "../config.js";

export default function UserProfile() {
  const navigate = useNavigate();
  const { user, token, logout } = useAuth();
  const toast = useToast();
  const [profile, setProfile] = useState(null);
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  const [selectedScan, setSelectedScan] = useState(null);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [pwData, setPwData] = useState({ current: "", next: "", confirm: "" });
  const [pwLoading, setPwLoading] = useState(false);
  const [pwError, setPwError] = useState("");
  const [pwSuccess, setPwSuccess] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null); // { type: 'single', id } | { type: 'all' }

  useEffect(() => {
    async function load() {
      try {
        const [me, myScans] = await Promise.all([
          profileApi.getMe(token),
          api.getMyScans(token),
        ]);
        setProfile(me);
        setScans(myScans.scans.slice(0, 5));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [token]);

  async function handleChangePassword(e) {
    e.preventDefault();
    setPwError(""); setPwSuccess("");
    if (pwData.next !== pwData.confirm) { setPwError("Passwords do not match"); return; }
    if (pwData.next.length < 8) { setPwError("Password must be at least 8 characters"); return; }
    setPwLoading(true);
    try {
      await profileApi.changePassword(token, pwData.current, pwData.next);
      setPwSuccess("Password changed successfully!");
      toast({ message: "Password changed successfully", type: "success" });
      setPwData({ current: "", next: "", confirm: "" });
      setTimeout(() => { setPwSuccess(""); setShowPasswordForm(false); }, 2000);
    } catch (err) {
      setPwError(err.message);
      toast({ message: err.message, type: "error" });
    } finally {
      setPwLoading(false);
    }
  }

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

  async function handleDeleteScan() {
    if (!confirmDelete) return;
    try {
      if (confirmDelete.type === "single") {
        await api.deleteScan(token, confirmDelete.id);
        setScans(prev => prev.filter(s => s.id !== confirmDelete.id));
        toast({ message: "Scan deleted", type: "info" });
      } else {
        await api.deleteAllScans(token);
        setScans([]);
        toast({ message: "All scans deleted", type: "info" });
      }
    } catch (err) {
      toast({ message: "Failed to delete scan", type: "error" });
      console.error(err);
    } finally {
      setConfirmDelete(null);
    }
  }

  async function handleDeleteAccount() {
    try {
      await profileApi.deleteMe(token);
      logout();
      navigate("/");
    } catch (err) {
      console.error(err);
    }
  }

  const isGoogleUser = profile?.auth_method === "google";
  const isAdmin = profile?.role === "admin";
  const joinDate = profile?.created_at
    ? new Date(profile.created_at).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })
    : "—";
  const lastLogin = profile?.last_login
    ? new Date(profile.last_login).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })
    : "Never";
  const totalScans = scans.length;
  const forgedCount = scans.filter(s => s.verdict === "forged").length;

  if (loading) return (
    <>
      <Navbar />
      <div className="profile-loading">
        <div className="profile-spinner" />
        <p>Loading profile...</p>
      </div>
    </>
  );

  return (
    <>
      <Navbar />
      <ScanDetailModal scan={selectedScan} onClose={() => setSelectedScan(null)} />

      {/* ── Delete Confirm Modal ── */}
      {confirmDelete && (
        <div className="scan-modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="scan-modal" style={{ maxWidth: 360 }} onClick={e => e.stopPropagation()}>
            <h2 className="scan-modal-title">Are you sure?</h2>
            <p style={{ fontSize: "0.875rem", color: "#a1a1aa", margin: 0 }}>
              {confirmDelete.type === "all"
                ? "This will permanently delete all your scans."
                : "This will permanently delete this scan."}
            </p>
            <div className="profile-pw-actions" style={{ marginTop: "1rem" }}>
              <button className="profile-btn-danger" onClick={handleDeleteScan}>Yes, delete</button>
              <button className="profile-btn-ghost" onClick={() => setConfirmDelete(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
      <div className="profile-page">
        <div className="profile-glow" />

        <div className="profile-container">

          {/* ── Identity card ── */}
          <div className="profile-identity-card">
            <div className="profile-identity-left">
              <div className="profile-avatar-wrap">
                <div className="profile-avatar-ring" />
                <div className="profile-avatar">{profile?.name?.[0]?.toUpperCase()}</div>
              </div>
              <div className="profile-identity-info">
                <div className="profile-identity-top">
                  <h1>{profile?.name}</h1>
                  <span className={`profile-role-badge ${isAdmin ? "admin" : ""}`}>
                    {isAdmin ? "ADMIN" : "USER"}
                  </span>
                </div>
                <p className="profile-identity-email">{profile?.email}</p>
                <div className="profile-identity-tags">
                  <span className="profile-tag">
                    {isGoogleUser ? "🔵 Google" : "📧 Email"}
                  </span>
                  <span className={`profile-tag ${profile?.is_verified ? "verified" : "unverified"}`}>
                    {profile?.is_verified ? "✓ Verified" : "✕ Unverified"}
                  </span>
                </div>
              </div>
            </div>

            {/* Stats inline */}
            <div className="profile-identity-stats">
              <div className="profile-istat">
                <div className="profile-istat-val">{totalScans}</div>
                <div className="profile-istat-label">Total Scans</div>
              </div>
              <div className="profile-istat-divider" />
              <div className="profile-istat">
                <div className="profile-istat-val red">{forgedCount}</div>
                <div className="profile-istat-label">Forged</div>
              </div>
              <div className="profile-istat-divider" />
              <div className="profile-istat">
                <div className="profile-istat-val green">{totalScans - forgedCount}</div>
                <div className="profile-istat-label">Authentic</div>
              </div>
            </div>
          </div>

          {/* ── Details + Scans row ── */}
          <div className="profile-grid">

            {/* Account details */}
            <div className="profile-card">
              <div className="profile-card-title">
                <InfoIcon /> Account Details
              </div>
              <div className="profile-detail-list">
                <div className="profile-detail-row">
                  <span className="profile-detail-label">Full name</span>
                  <span className="profile-detail-value">{profile?.name}</span>
                </div>
                <div className="profile-detail-row">
                  <span className="profile-detail-label">Email</span>
                  <span className="profile-detail-value">{profile?.email}</span>
                </div>
                <div className="profile-detail-row">
                  <span className="profile-detail-label">Role</span>
                  <span className={`profile-detail-value role ${isAdmin ? "admin" : ""}`}>{profile?.role}</span>
                </div>
                <div className="profile-detail-row">
                  <span className="profile-detail-label">Auth method</span>
                  <span className="profile-detail-value">{isGoogleUser ? "Google OAuth" : "Email & Password"}</span>
                </div>
                <div className="profile-detail-row">
                  <span className="profile-detail-label">Joined</span>
                  <span className="profile-detail-value">{joinDate}</span>
                </div>
                <div className="profile-detail-row">
                  <span className="profile-detail-label">Last login</span>
                  <span className="profile-detail-value">{lastLogin}</span>
                </div>
                <div className="profile-detail-row">
                  <span className="profile-detail-label">Verified</span>
                  <span className={`profile-detail-value ${profile?.is_verified ? "green" : "red"}`}>
                    {profile?.is_verified ? "Yes" : "No"}
                  </span>
                </div>
              </div>
            </div>

            {/* Recent scans */}
            <div className="profile-card">
              <div className="profile-card-title" style={{ justifyContent: "space-between" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <ScanIcon /> Recent Scans
                </span>
                {scans.length > 0 && (
                  <button
                    className="profile-btn-danger"
                    style={{ fontSize: "0.7rem", padding: "0.25rem 0.6rem" }}
                    onClick={() => setConfirmDelete({ type: "all" })}
                  >
                    Clear All
                  </button>
                )}
              </div>
              {scans.length === 0 ? (
                <div className="profile-empty">
                  <div className="profile-empty-icon">📄</div>
                  <p>No scans yet</p>
                </div>
              ) : (
                <div className="profile-scans-list">
                  {scans.map((s, i) => (
                    <div className="profile-scan-row clickable" key={i} onClick={() => setSelectedScan(s)}>
                      <div className="profile-scan-icon">✓</div>
                      <div className="profile-scan-info">
                        <div className="profile-scan-name">{s.file_name}</div>
                        <div className="profile-scan-date">{new Date(s.scanned_at).toLocaleDateString("en-GB")}</div>
                      </div>
                      <span className="profile-verdict">{s.doc_type || "—"}</span>
                      <button
                        className="profile-scan-download-btn"
                        onClick={e => { e.stopPropagation(); downloadReport(s.id); }}
                        title="Download PDF report"
                      >↓</button>
                      <button
                        className="profile-scan-delete-btn"
                        onClick={e => { e.stopPropagation(); setConfirmDelete({ type: "single", id: s.id }); }}
                        title="Delete scan"
                      >🗑</button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* ── Security ── */}
          {!isGoogleUser && (
            <div className="profile-card">
              <div className="profile-card-title">
                <LockIcon /> Security
              </div>
              {!showPasswordForm ? (
                <button className="profile-btn-secondary" onClick={() => setShowPasswordForm(true)}>
                  Change Password
                </button>
              ) : (
                <form className="profile-pw-form" onSubmit={handleChangePassword}>
                  <div className="profile-pw-grid">
                    <div className="profile-input-wrap">
                      <label>Current password</label>
                      <input type="password" value={pwData.current} onChange={e => setPwData(p => ({ ...p, current: e.target.value }))} />
                    </div>
                    <div className="profile-input-wrap">
                      <label>New password</label>
                      <input type="password" value={pwData.next} onChange={e => setPwData(p => ({ ...p, next: e.target.value }))} />
                    </div>
                    <div className="profile-input-wrap">
                      <label>Confirm new password</label>
                      <input type="password" value={pwData.confirm} onChange={e => setPwData(p => ({ ...p, confirm: e.target.value }))} />
                    </div>
                  </div>
                  {pwError && <div className="profile-error">{pwError}</div>}
                  {pwSuccess && <div className="profile-success">{pwSuccess}</div>}
                  <div className="profile-pw-actions">
                    <button type="submit" className="profile-btn-primary" disabled={pwLoading}>
                      {pwLoading ? "Saving..." : "Save Password"}
                    </button>
                    <button type="button" className="profile-btn-ghost" onClick={() => { setShowPasswordForm(false); setPwError(""); }}>
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* ── Danger zone ── */}
          <div className="profile-card danger-zone">
            <div className="profile-card-title danger">
              <DangerIcon /> Danger Zone
            </div>
            {!showDeleteConfirm ? (
              <div className="profile-danger-row">
                <div>
                  <div className="profile-danger-title">Delete Account</div>
                  <div className="profile-danger-desc">Permanently delete your account and all associated data.</div>
                </div>
                <button className="profile-btn-danger" onClick={() => setShowDeleteConfirm(true)}>
                  Delete Account
                </button>
              </div>
            ) : (
              <div className="profile-delete-confirm">
                <p>Are you sure? This action <strong>cannot be undone</strong>.</p>
                <div className="profile-pw-actions">
                  <button className="profile-btn-danger" onClick={handleDeleteAccount}>Yes, delete my account</button>
                  <button className="profile-btn-ghost" onClick={() => setShowDeleteConfirm(false)}>Cancel</button>
                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </>
  );
}

function ScanDetailModal({ scan, onClose }) {
  if (!scan) return null;
  const conf = scan.confidence ? `${(scan.confidence * 100).toFixed(1)}%` : "—";
  return (
    <div className="scan-modal-overlay" onClick={onClose}>
      <div className="scan-modal" onClick={e => e.stopPropagation()}>
        <button className="scan-modal-close" onClick={onClose}>✕</button>
        <h2 className="scan-modal-title">Scan Details</h2>

        {scan.image_data ? (
          <img
            src={`data:image/jpeg;base64,${scan.image_data}`}
            alt={scan.file_name}
            className="scan-modal-img"
          />
        ) : (
          <div className="scan-modal-no-img">No image stored</div>
        )}

        <div className="scan-modal-grid">
          <div className="scan-modal-item">
            <span className="scan-modal-lbl">File</span>
            <span className="scan-modal-val">{scan.file_name}</span>
          </div>
          <div className="scan-modal-item">
            <span className="scan-modal-lbl">Document type</span>
            <span className="scan-modal-val">{scan.doc_type || "—"}</span>
          </div>
          <div className="scan-modal-item">
            <span className="scan-modal-lbl">Model</span>
            <span className="scan-modal-val">{scan.model_used}</span>
          </div>
          <div className="scan-modal-item">
            <span className="scan-modal-lbl">Confidence</span>
            <span className="scan-modal-val">{conf}</span>
          </div>
          <div className="scan-modal-item">
            <span className="scan-modal-lbl">Date</span>
            <span className="scan-modal-val">{new Date(scan.scanned_at).toLocaleDateString("en-GB")}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoIcon() { return <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>; }
function ScanIcon() { return <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>; }
function LockIcon() { return <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>; }
function DangerIcon() { return <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>; }

import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import "./VerifyEmail.css";
import "./Login.css";
import "./Register.css";

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [form, setForm] = useState({ password: "", confirm: "" });
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const strength = getStrength(form.password);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.password || !form.confirm) { setError("Please fill in all fields."); return; }
    if (form.password.length < 8) { setError("Password must be at least 8 characters."); return; }
    if (form.password !== form.confirm) { setError("Passwords do not match."); return; }

    setLoading(true);
    setError("");

    try {
      await api.resetPassword(token, form.password);
      setSuccess(true);
      setTimeout(() => navigate("/login", { replace: true }), 2500);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="verify-layout">
        <div className="verify-card">
          <div className="verify-icon error">✕</div>
          <h2>Invalid link</h2>
          <p>This reset link is invalid or has expired.</p>
          <button className="verify-btn" onClick={() => navigate("/forgot-password")}>
            Request new link →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="verify-layout">
      <div className="verify-glow" />
      <a className="verify-logo" href="/">
        <LogoIcon />
        Docu<span>Guard</span>
      </a>

      {success ? (
        <div className="verify-card">
          <div className="verify-icon success">✓</div>
          <h2>Password updated!</h2>
          <p>Your password has been reset successfully. Redirecting to login...</p>
          <div className="verify-progress">
            <div className="verify-progress-bar" />
          </div>
        </div>
      ) : (
        <div className="verify-card">
          <div className="verify-icon success" style={{ fontSize: "1.6rem" }}>🔒</div>
          <h2>Reset password</h2>
          <p>Enter your new password below.</p>

          {error && <div className="auth-error" style={{ width: "100%", marginTop: "0.5rem" }}>{error}</div>}

          <form onSubmit={handleSubmit} style={{ width: "100%", marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.75rem" }} noValidate>
            <div className="auth-field" style={{ width: "100%" }}>
              <label htmlFor="password">New password</label>
              <div className="auth-input-wrap">
                <input
                  id="password"
                  type={showPass ? "text" : "password"}
                  placeholder="Min. 8 characters"
                  value={form.password}
                  onChange={e => { setForm(f => ({ ...f, password: e.target.value })); setError(""); }}
                  autoComplete="new-password"
                />
                <button type="button" className="auth-eye" onClick={() => setShowPass(s => !s)}>
                  {showPass ? <EyeOff /> : <EyeOn />}
                </button>
              </div>
              {form.password && (
                <div className="reg-strength">
                  <div className="reg-strength-bars">
                    {[1, 2, 3, 4].map(i => (
                      <div key={i} className={`reg-bar ${i <= strength.score ? strength.cls : ""}`} />
                    ))}
                  </div>
                  <span className={`reg-strength-label ${strength.cls}`}>{strength.label}</span>
                </div>
              )}
            </div>

            <div className="auth-field" style={{ width: "100%" }}>
              <label htmlFor="confirm">Confirm new password</label>
              <div className="auth-input-wrap">
                <input
                  id="confirm"
                  type={showConfirm ? "text" : "password"}
                  placeholder="••••••••"
                  value={form.confirm}
                  onChange={e => { setForm(f => ({ ...f, confirm: e.target.value })); setError(""); }}
                  autoComplete="new-password"
                />
                <button type="button" className="auth-eye" onClick={() => setShowConfirm(s => !s)}>
                  {showConfirm ? <EyeOff /> : <EyeOn />}
                </button>
              </div>
              {form.confirm && form.password !== form.confirm && (
                <span className="reg-mismatch">Passwords don't match</span>
              )}
              {form.confirm && form.password === form.confirm && form.confirm.length > 0 && (
                <span className="reg-match">✓ Passwords match</span>
              )}
            </div>

            <button type="submit" className={`auth-submit ${loading ? "loading" : ""}`} disabled={loading}>
              {loading ? <span className="auth-spinner" /> : "Reset password →"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

function getStrength(password) {
  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  const labels = ["", "Weak", "Fair", "Good", "Strong"];
  const classes = ["", "weak", "fair", "good", "strong"];
  return { score, label: labels[score] || "Weak", cls: classes[score] || "weak" };
}

function LogoIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="8" fill="#a3e635" />
      <rect x="8" y="6" width="13" height="17" rx="2" fill="#09090f" />
      <path d="M17 6 L21 10 H17 Z" fill="#a3e635" />
      <rect x="10.5" y="13" width="8" height="1.2" rx="0.6" fill="#a3e635" opacity="0.9" />
      <rect x="10.5" y="16" width="6" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6" />
      <rect x="10.5" y="19" width="7" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6" />
      <circle cx="22" cy="22" r="5" fill="#a3e635" />
      <path d="M19.5 22 L21.2 23.8 L24.5 20.5" stroke="#09090f" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function EyeOn() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeOff() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  );
}

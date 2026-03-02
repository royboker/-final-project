import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";

export default function Login() {
  const navigate = useNavigate();
  const [showPass, setShowPass] = useState(false);
  const [form, setForm] = useState({ email: "", password: "", remember: false });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { setSession } = useAuth();

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === "checkbox" ? checked : value }));
    setError("");
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!form.email || !form.password) {
      setError("Please fill in all fields.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await api.login({
        email: form.email,
        password: form.password,
      });

      // חשוב: זה גם מעדכן Context וגם שומר ל-localStorage
      setSession(res.token, res.user);

      navigate("/");
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-layout">
      {/* ── LEFT PANEL ── */}
      <div className="auth-left">
        <a className="auth-logo" href="/">
          <LogoIcon />
          Docu<span>Guard</span>
        </a>

        <div className="auth-form-wrap">
          <div className="auth-header">
            <h1>Welcome back</h1>
            <p>Sign in to your DocuGuard account</p>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            <div className="auth-field">
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
              />
            </div>

            <div className="auth-field">
              <div className="auth-field-header">
                <label htmlFor="password">Password</label>
                <button type="button" className="auth-forgot" onClick={() => {}}>
                  Forgot password?
                </button>
              </div>

              <div className="auth-input-wrap">
                <input
                  id="password"
                  name="password"
                  type={showPass ? "text" : "password"}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={handleChange}
                  autoComplete="current-password"
                />

                <button
                  type="button"
                  className="auth-eye"
                  onClick={() => setShowPass((s) => !s)}
                >
                  {showPass ? <EyeOff /> : <EyeOn />}
                </button>
              </div>
            </div>

            <label className="auth-check">
              <input
                type="checkbox"
                name="remember"
                checked={form.remember}
                onChange={handleChange}
              />
              <span className="auth-check-box" />
              <span>Remember me for 30 days</span>
            </label>

            <button
              type="submit"
              className={`auth-submit ${loading ? "loading" : ""}`}
              disabled={loading}
            >
              {loading ? <span className="auth-spinner" /> : "Sign in →"}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account?{" "}
            <button onClick={() => navigate("/register")}>Create one</button>
          </p>
        </div>
      </div>

      {/* ── RIGHT PANEL ── */}
      <div className="auth-right">
        <div className="auth-right-glow" />
        <div className="auth-right-grid" />

        <div className="auth-card auth-card-1">
          <div className="auth-card-line" />
          <div className="auth-card-line short" />
          <div className="auth-card-badge green">✓ Authentic</div>
        </div>
        <div className="auth-card auth-card-2">
          <div className="auth-card-line" />
          <div className="auth-card-line short" />
          <div className="auth-card-badge red">⚠ Forged</div>
        </div>
        <div className="auth-card auth-card-3">
          <div className="auth-card-line" />
          <div className="auth-card-line short" />
          <div className="auth-card-badge green">✓ Authentic</div>
        </div>

        <div className="auth-right-content">
          <div className="auth-right-icon">
            <ShieldIcon />
          </div>
          <h2>AI powered document verification</h2>
          <p>Detect forged IDs, passports, and driver licenses in seconds with 97%+ accuracy.</p>

          <div className="auth-stats">
            {[
              { num: "50M+", label: "Docs scanned" },
              { num: "97%", label: "Accuracy" },
              { num: "99.9%", label: "Uptime" },
            ].map((s) => (
              <div className="auth-stat" key={s.label}>
                <span className="auth-stat-num">{s.num}</span>
                <span className="auth-stat-label">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Icons ─────────────────────────────────────────────────────────────────────
function LogoIcon() {
  return (
    <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="8" fill="#a3e635" />
      <rect x="8" y="6" width="13" height="17" rx="2" fill="#09090f" />
      <path d="M17 6 L21 10 H17 Z" fill="#a3e635" />
      <rect x="10.5" y="13" width="8" height="1.2" rx="0.6" fill="#a3e635" opacity="0.9" />
      <rect x="10.5" y="16" width="6" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6" />
      <rect x="10.5" y="19" width="7" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6" />
      <circle cx="22" cy="22" r="5" fill="#a3e635" />
      <path
        d="M19.5 22 L21.2 23.8 L24.5 20.5"
        stroke="#09090f"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
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

function ShieldIcon() {
  return (
    <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  );
}
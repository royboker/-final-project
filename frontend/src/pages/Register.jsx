import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { API_URL } from "../config";
import "./Login.css";
import "./Register.css";

export default function Register() {
  const navigate = useNavigate();
  const [showPass, setShowPass]       = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState("");
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "", terms: false });

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === "checkbox" ? checked : value }));
    setError("");
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!form.name || !form.email || !form.password || !form.confirm) {
      setError("Please fill in all fields.");
      return;
    }
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (form.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (!form.terms) {
      setError("You must accept the terms.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await api.register({
        name: form.name,
        email: form.email,
        password: form.password,
      });

      navigate("/check-email");
    } catch (err) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  const strength = getStrength(form.password);

  return (
    <div className="auth-layout">

      {/* ── LEFT ── */}
      <div className="auth-left">
        <a className="auth-logo" href="/">
          <LogoIcon />
          <span className="logo-text">Docu<span>Guard</span></span>
        </a>

        <div className="auth-form-wrap">

          {/* ── Back button ── */}
          <div className="auth-back-wrap">
            <button className="auth-back" onClick={() => navigate("/")}>
              DocuGuard →
            </button>
          </div>

          <div className="auth-header">
            <h1>Create account</h1>
            <p>Start verifying documents with AI</p>
          </div>

          {/* ── Google ── */}
          <button
            type="button"
            className="auth-google"
            onClick={() => window.location.href = `${API_URL}/auth/google`}
          >
            <GoogleIcon />
            Continue with Google
          </button>

          <div className="auth-divider">
            <span>or</span>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <form className="auth-form" onSubmit={handleSubmit} noValidate>

            <div className="auth-field">
              <label htmlFor="name">Full name</label>
              <input id="name" name="name" type="text"
                placeholder="John Doe"
                value={form.name} onChange={handleChange} autoComplete="name" />
            </div>

            <div className="auth-field">
              <label htmlFor="email">Email address</label>
              <input id="email" name="email" type="email"
                placeholder="you@example.com"
                value={form.email} onChange={handleChange} autoComplete="email" />
            </div>

            <div className="auth-field">
              <label htmlFor="password">Password</label>
              <div className="auth-input-wrap">
                <input id="password" name="password"
                  type={showPass ? "text" : "password"}
                  placeholder="Min. 8 characters"
                  value={form.password} onChange={handleChange}
                  autoComplete="new-password" />
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

            <div className="auth-field">
              <label htmlFor="confirm">Confirm password</label>
              <div className="auth-input-wrap">
                <input id="confirm" name="confirm"
                  type={showConfirm ? "text" : "password"}
                  placeholder="••••••••"
                  value={form.confirm} onChange={handleChange}
                  autoComplete="new-password" />
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

            <label className="auth-check">
              <input type="checkbox" name="terms" checked={form.terms} onChange={handleChange} />
              <span className="auth-check-box" />
              <span>I agree to the <button type="button" className="auth-link">Terms</button> and <button type="button" className="auth-link">Privacy Policy</button></span>
            </label>

            <button type="submit" className={`auth-submit ${loading ? "loading" : ""}`} disabled={loading}>
              {loading ? <span className="auth-spinner" /> : "Create account →"}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account?{" "}
            <button onClick={() => navigate("/login")}>Sign in</button>
          </p>
        </div>
      </div>

      {/* ── RIGHT ── */}
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
          <h2>Join thousands of verifiers</h2>
          <p>DocuGuard uses ViT and ResNet-18 models trained on 9,000+ real documents.</p>

          <div className="reg-features">
            {[
              "ID cards, Passports & Driver Licenses",
              "Dual AI model verification",
              "9 countries supported",
              "Full scan history & audit logs",
            ].map(f => (
              <div className="reg-feature" key={f}>
                <span className="reg-feature-dot" />
                {f}
              </div>
            ))}
          </div>
        </div>
      </div>

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
    <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
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

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05" />
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
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

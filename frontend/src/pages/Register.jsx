import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import "./Login.css";
import "./Register.css";

export default function Register() {
  const navigate = useNavigate();
  const [showPass, setShowPass]     = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState("");
  const [form, setForm] = useState({
    name: "", email: "", password: "", confirm: "", terms: false,
  });

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
    const res = await api.register({
      name: form.name,
      email: form.email,
      password: form.password,
    });

    // הבאקנד שלך מחזיר token
    localStorage.setItem("token", res.token);
    localStorage.setItem("user", JSON.stringify(res.user));

    navigate("/");
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
          Docu<span>Guard</span>
        </a>

        <div className="auth-form-wrap">
          <div className="auth-header">
            <h1>Create account</h1>
            <p>Start verifying documents with AI</p>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <form className="auth-form" onSubmit={handleSubmit} noValidate>

            <div className="auth-field">
              <label htmlFor="name">Full name</label>
              <input id="name" name="name" type="text"
                placeholder="John Doe"
                value={form.name} onChange={handleChange} autoComplete="name"/>
            </div>

            <div className="auth-field">
              <label htmlFor="email">Email address</label>
              <input id="email" name="email" type="email"
                placeholder="you@example.com"
                value={form.email} onChange={handleChange} autoComplete="email"/>
            </div>

            <div className="auth-field">
              <label htmlFor="password">Password</label>
              <div className="auth-input-wrap">
                <input id="password" name="password"
                  type={showPass ? "text" : "password"}
                  placeholder="Min. 8 characters"
                  value={form.password} onChange={handleChange}
                  autoComplete="new-password"/>
                <button type="button" className="auth-eye" onClick={() => setShowPass(s => !s)}>
                  {showPass ? <EyeOff /> : <EyeOn />}
                </button>
              </div>
              {form.password && (
                <div className="reg-strength">
                  <div className="reg-strength-bars">
                    {[1,2,3,4].map(i => (
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
                  autoComplete="new-password"/>
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
              <input type="checkbox" name="terms" checked={form.terms} onChange={handleChange}/>
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

// ── Password strength ─────────────────────────────────────────────────────────
function getStrength(password) {
  let score = 0;
  if (password.length >= 8)  score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  const labels = ["", "Weak", "Fair", "Good", "Strong"];
  const classes = ["", "weak", "fair", "good", "strong"];
  return { score, label: labels[score] || "Weak", cls: classes[score] || "weak" };
}

// ── Icons ─────────────────────────────────────────────────────────────────────
function LogoIcon() {
  return (
    <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="8" fill="#a3e635"/>
      <rect x="8" y="6" width="13" height="17" rx="2" fill="#09090f"/>
      <path d="M17 6 L21 10 H17 Z" fill="#a3e635"/>
      <rect x="10.5" y="13" width="8" height="1.2" rx="0.6" fill="#a3e635" opacity="0.9"/>
      <rect x="10.5" y="16" width="6" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6"/>
      <rect x="10.5" y="19" width="7" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6"/>
      <circle cx="22" cy="22" r="5" fill="#a3e635"/>
      <path d="M19.5 22 L21.2 23.8 L24.5 20.5" stroke="#09090f" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}
function EyeOn() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  );
}
function EyeOff() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/>
      <line x1="1" y1="1" x2="23" y2="23"/>
    </svg>
  );
}
function ShieldIcon() {
  return (
    <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      <path d="M9 12l2 2 4-4"/>
    </svg>
  );
}

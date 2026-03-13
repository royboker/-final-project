import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import "./VerifyEmail.css";
import "./Login.css";

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email) { setError("Please enter your email."); return; }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) { setError("Please enter a valid email address."); return; }
    setLoading(true);
    setError("");

    try {
      await api.forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="verify-layout">
      <div className="verify-glow" />

      <a className="verify-logo" href="/">
        <LogoIcon />
        <span className="logo-text">Docu<span>Guard</span></span>
      </a>

      {sent ? (
        <div className="verify-card">
          <div className="verify-icon success" style={{ fontSize: "1.8rem" }}>📧</div>
          <h2>Check your email</h2>
          <p>If an account exists for <strong style={{ color: "#fff" }}>{email}</strong>, a reset link has been sent.</p>
          <p style={{ fontSize: "0.78rem", color: "#52525b" }}>Didn't receive it? Check your spam folder.</p>
          <button className="verify-btn" onClick={() => navigate("/login")}>
            Back to Login →
          </button>
        </div>
      ) : (
        <div className="verify-card">
          <div className="verify-icon success" style={{ fontSize: "1.8rem" }}>🔑</div>
          <h2>Forgot password?</h2>
          <p>Enter your email and we'll send you a reset link.</p>

          {error && <div className="auth-error" style={{ width: "100%", marginTop: "0.5rem" }}>{error}</div>}

          <form onSubmit={handleSubmit} style={{ width: "100%", marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.75rem" }} noValidate>
            <div className="auth-field" style={{ width: "100%" }}>
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={e => { setEmail(e.target.value); setError(""); }}
                autoComplete="email"
              />
            </div>

            <button
              type="submit"
              className={`auth-submit ${loading ? "loading" : ""}`}
              disabled={loading}
            >
              {loading ? <span className="auth-spinner" /> : "Send reset link →"}
            </button>
          </form>

          <button
            onClick={() => navigate("/login")}
            style={{ background: "none", border: "none", color: "#a1a1aa", fontFamily: "DM Sans, sans-serif", fontSize: "0.85rem", cursor: "pointer", marginTop: "0.25rem" }}
          >
            ← Back to Login
          </button>
        </div>
      )}
    </div>
  );
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

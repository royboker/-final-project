import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import "./VerifyEmail.css";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setSession } = useAuth();

  const [status, setStatus] = useState("loading");
  const ranRef = useRef(false);

  useEffect(() => {
    // React 18 StrictMode (dev) יכול להריץ את ה-effect פעמיים
    if (ranRef.current) return;
    ranRef.current = true;

    const token = searchParams.get("token");
    if (!token) {
      setStatus("error");
      return;
    }

    let timerId = null;

    api
      .verifyEmail(token)
      .then((res) => {
        // אם ה-api שלך מחזיר בצורה אחרת (axios) אולי צריך res.data
        const jwt = res?.token ?? res?.data?.token;
        const user = res?.user ?? res?.data?.user;

        if (!jwt || !user) {
          setStatus("error");
          return;
        }

        setSession(jwt, user);
        setStatus("success");

        timerId = setTimeout(() => {
          navigate("/", { replace: true });
        }, 2500);
      })
      .catch(() => setStatus("error"));

    return () => {
      if (timerId) clearTimeout(timerId);
    };
  }, [searchParams, navigate, setSession]);

  return (
    <div className="verify-layout">
      <div className="verify-glow" />

      <Link className="verify-logo" to="/">
        <LogoIcon />
        Docu<span>Guard</span>
      </Link>

      <div className="verify-card">
        {status === "loading" && (
          <>
            <div className="verify-spinner" />
            <h2>Verifying your email...</h2>
            <p>Please wait a moment.</p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="verify-icon success">✓</div>
            <h2>Email verified!</h2>
            <p>Your account is now active. Redirecting you to the app...</p>
            <div className="verify-progress">
              <div className="verify-progress-bar" />
            </div>
          </>
        )}

        {status === "error" && (
          <>
            <div className="verify-icon error">✕</div>
            <h2>Link invalid or expired</h2>
            <p>This verification link has already been used or has expired.</p>
            <button className="verify-btn" onClick={() => navigate("/register")}>
              Back to Register →
            </button>
          </>
        )}
      </div>
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
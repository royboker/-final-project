import { useNavigate } from "react-router-dom";
import "./VerifyEmail.css"; 

export default function CheckEmail() {
  const navigate = useNavigate();

  return (
    <div className="verify-layout">
      <div className="verify-glow" />

      <a className="verify-logo" href="/">
        <LogoIcon />
        Docu<span>Guard</span>
      </a>

      <div className="verify-card">
        <div className="verify-icon success" style={{ fontSize: "1.8rem" }}>📧</div>
        <h2>Check your email</h2>
        <p>
          We sent a verification link to your inbox.<br />
          Click the link to activate your account.
        </p>
        <p style={{ fontSize: "0.78rem", color: "#52525b", marginTop: "0.25rem" }}>
          Didn't receive it? Check your spam folder.
        </p>
        <button className="verify-btn" onClick={() => navigate("/login")}>
          Go to Login →
        </button>
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
      <path d="M19.5 22 L21.2 23.8 L24.5 20.5" stroke="#09090f" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

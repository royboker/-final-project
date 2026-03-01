import { useNavigate } from "react-router-dom";
import "./Navbar.css";

function DocuGuardLogo() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Background */}
      <rect width="32" height="32" rx="8" fill="#a3e635"/>
      {/* Document shape */}
      <rect x="8" y="6" width="13" height="17" rx="2" fill="#09090f"/>
      {/* Folded corner */}
      <path d="M17 6 L21 10 L17 10 Z" fill="#a3e635"/>
      <rect x="17" y="6" width="4" height="4" rx="0" fill="#a3e635"/>
      <path d="M17 6 L21 10 H17 V6Z" fill="rgba(0,0,0,0.15)"/>
      {/* Lines on document */}
      <rect x="10.5" y="13" width="8" height="1.2" rx="0.6" fill="#a3e635" opacity="0.9"/>
      <rect x="10.5" y="16" width="6" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6"/>
      <rect x="10.5" y="19" width="7" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6"/>
      {/* Shield checkmark */}
      <circle cx="22" cy="22" r="6" fill="#09090f"/>
      <circle cx="22" cy="22" r="5" fill="#a3e635"/>
      <path d="M19.5 22 L21.2 23.8 L24.5 20.5" stroke="#09090f" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className="nav">
      <a className="logo" href="/">
        <DocuGuardLogo />
        Docu<span>Guard</span>
      </a>

      <div className="nav-links">
        <a href="#features"     className="btn-ghost">Features</a>
        <a href="#how-it-works" className="btn-ghost">How it works</a>
        <button className="btn-ghost"   onClick={() => navigate("/login")}>Sign in</button>
        <button className="btn-primary" onClick={() => navigate("/register")}>Get started →</button>
      </div>
    </nav>
  );
}

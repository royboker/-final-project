import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Navbar.css";

function DocuGuardLogo() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="32" height="32" rx="8" fill="#a3e635"/>
      <rect x="8" y="6" width="13" height="17" rx="2" fill="#09090f"/>
      <path d="M17 6 L21 10 L17 10 Z" fill="#a3e635"/>
      <rect x="17" y="6" width="4" height="4" rx="0" fill="#a3e635"/>
      <path d="M17 6 L21 10 H17 V6Z" fill="rgba(0,0,0,0.15)"/>
      <rect x="10.5" y="13" width="8" height="1.2" rx="0.6" fill="#a3e635" opacity="0.9"/>
      <rect x="10.5" y="16" width="6" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6"/>
      <rect x="10.5" y="19" width="7" height="1.2" rx="0.6" fill="#a3e635" opacity="0.6"/>
      <circle cx="22" cy="22" r="6" fill="#09090f"/>
      <circle cx="22" cy="22" r="5" fill="#a3e635"/>
      <path d="M19.5 22 L21.2 23.8 L24.5 20.5" stroke="#09090f" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

export default function Navbar() {
  const navigate = useNavigate();
  const { isAuthed, user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const role = String(user?.role ?? "user").trim().toLowerCase();
  const isAdmin = role === "admin";

  // Close menu on route change or resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 680) setMenuOpen(false);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Prevent body scroll when menu is open
  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  const closeMenu = () => setMenuOpen(false);

  const handleNavigate = (path) => {
    closeMenu();
    navigate(path);
  };

  const handleLogout = () => {
    closeMenu();
    logout();
    navigate("/");
  };

  return (
    <>
      <nav className="nav">
        <a className="logo" href="/">
          <DocuGuardLogo />
          Docu<span>Guard</span>
        </a>

        {/* Desktop links */}
        <div className="nav-links">
          <a href="#how-it-works" className="btn-ghost">How it works</a>

          {!isAuthed ? (
            <>
              <button className="btn-ghost" onClick={() => navigate("/login")}>
                Sign in
              </button>
              <button className="btn-primary" onClick={() => navigate("/register")}>
                Create account
              </button>
            </>
          ) : (
            <>
              <span className="nav-user" title={isAdmin ? "Admin account" : "User account"}>
                <span className={`nav-role ${isAdmin ? "admin" : ""}`}>
                  {isAdmin ? "ADMIN" : "USER"}
                </span>
                Hello <strong>{user?.name}</strong>
              </span>
              <button
                className={`btn-primary ${isAdmin ? "btn-admin" : ""}`}
                onClick={handleLogout}
              >
                Logout
              </button>
            </>
          )}
        </div>

        {/* Hamburger button — mobile only */}
        <button
          className={`hamburger ${menuOpen ? "open" : ""}`}
          onClick={() => setMenuOpen((prev) => !prev)}
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
        >
          <span />
          <span />
          <span />
        </button>
      </nav>

      {/* Mobile drawer */}
      <div className={`mobile-menu ${menuOpen ? "visible" : ""}`}>
        <div className="mobile-menu-inner">
          <a href="#how-it-works" className="mobile-link" onClick={closeMenu}>
            How it works
          </a>

          {!isAuthed ? (
            <>
              <button className="btn-ghost mobile-btn" onClick={() => handleNavigate("/login")}>
                Sign in
              </button>
              <button className="btn-primary mobile-btn" onClick={() => handleNavigate("/register")}>
                Create account
              </button>
            </>
          ) : (
            <>
              <div className="mobile-user">
                <span className={`nav-role ${isAdmin ? "admin" : ""}`}>
                  {isAdmin ? "ADMIN" : "USER"}
                </span>
                Hello <strong>{user?.name}</strong>
              </div>
              <button
                className={`btn-primary mobile-btn ${isAdmin ? "btn-admin" : ""}`}
                onClick={handleLogout}
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>

      {/* Backdrop */}
      {menuOpen && <div className="mobile-backdrop" onClick={closeMenu} />}
    </>
  );
}

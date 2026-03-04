import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useLocation } from "react-router-dom";
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
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const role = String(user?.role ?? "user").trim().toLowerCase();
  const isAdmin = role === "admin";

  useEffect(() => {
    const handleResize = () => { if (window.innerWidth > 680) setMenuOpen(false); };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const closeMenu = () => setMenuOpen(false);
  const handleNavigate = (path) => { closeMenu(); navigate(path); };
  const handleLogout = () => { closeMenu(); setDropdownOpen(false); logout(); navigate("/"); };
  const location = useLocation();
const isProfile = location.pathname === "/profile";

  return (
    <>
      <nav className="nav">
        <a className="logo" href="/">
          <DocuGuardLogo />
          Docu<span>Guard</span>
        </a>

        <div className="nav-links">
          {isProfile ? (
  <button className="btn-ghost nav-back" onClick={() => navigate("/")}>
     Home
  </button>
) : (
  <a href="#how-it-works" className="btn-ghost">How it works</a>
)}

          {!isAuthed ? (
            <>
              <button className="btn-ghost" onClick={() => navigate("/login")}>Sign in</button>
              <button className="btn-primary" onClick={() => navigate("/register")}>Create account</button>
            </>
          ) : (
            <>
              <button className="btn-primary" onClick={() => navigate("/scan")}>Scan document</button>
              {/* Profile dropdown */}
              <div className="nav-profile-wrap" ref={dropdownRef}>
                <button
                  className="nav-profile"
                  onClick={() => setDropdownOpen(o => !o)}
                >

                  <div className="nav-profile-info">
                    <span className={`nav-role ${isAdmin ? "admin" : ""}`}>
                      {isAdmin ? "ADMIN" : "USER"}
                    </span>
                    <span>{user?.name}</span>
                  </div>
                  <svg className={`nav-chevron ${dropdownOpen ? "open" : ""}`} viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polyline points="6 9 12 15 18 9"/>
                  </svg>
                </button>

                {dropdownOpen && (
                  <div className="nav-dropdown">
                    {/* Header */}
<div className="nav-dropdown-header">
  <div>
    <div className="nav-dropdown-name">{user?.name}</div>
    <div className="nav-dropdown-email">{user?.email}</div>
  </div>
</div>
                    <div className="nav-dropdown-divider" />

                    <button className="nav-dropdown-item" onClick={() => { setDropdownOpen(false); navigate("/profile"); }}>
                      <ProfileIcon /> My Profile
                    </button>

{isAdmin && (
  <button
    className="nav-dropdown-item nav-dropdown-admin"
    onClick={() => { setDropdownOpen(false); navigate("/admin"); }}
  >
    <DashboardIcon /> Admin Dashboard
  </button>
)}

                    <div className="nav-dropdown-divider" />

                    <button className="nav-dropdown-item danger" onClick={handleLogout}>
                      <LogoutIcon /> Logout
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        <button
          className={`hamburger ${menuOpen ? "open" : ""}`}
          onClick={() => setMenuOpen(prev => !prev)}
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
        >
          <span /><span /><span />
        </button>
      </nav>

      {/* Mobile drawer */}
      <div className={`mobile-menu ${menuOpen ? "visible" : ""}`}>
        <div className="mobile-menu-inner">
          <a href="#how-it-works" className="mobile-link" onClick={closeMenu}>How it works</a>

          {!isAuthed ? (
            <>
              <button className="btn-ghost mobile-btn" onClick={() => handleNavigate("/login")}>Sign in</button>
              <button className="btn-primary mobile-btn" onClick={() => handleNavigate("/register")}>Create account</button>
            </>
          ) : (
            <>
              <button className="btn-primary mobile-btn" onClick={() => handleNavigate("/scan")}>Scan document</button>
              <button className="nav-profile mobile-btn" onClick={() => handleNavigate("/profile")}>

                <div className="nav-profile-info">
                  <span className={`nav-role ${isAdmin ? "admin" : ""}`}>
                    {isAdmin ? "ADMIN" : "USER"}
                  </span>
                  <span>{user?.name}</span>
                </div>
              </button>
              {isAdmin && (
                <button className="btn-primary mobile-btn btn-admin" onClick={() => handleNavigate("/admin")}>
                  Dashboard
                </button>
              )}
              <button className="btn-ghost mobile-btn" onClick={handleLogout}>Logout</button>
            </>
          )}
        </div>
      </div>

      {menuOpen && <div className="mobile-backdrop" onClick={closeMenu} />}
    </>
  );
}

function ProfileIcon() {
  return <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
}
function DashboardIcon() {
  return <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>;
}
function LogoutIcon() {
  return <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>;
}

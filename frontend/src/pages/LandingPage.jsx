import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import ScanDemo from "../components/ScanDemo";
import "./LandingPage.css";

import { API_URL } from "../config.js";



// ── Animated Counter ──────────────────────────────────────────────────────────
function AnimatedCounter({ value, duration = 1500 }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el || value === 0) return;

    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          const start = performance.now();
          function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            setDisplay(Math.round(eased * value));
            if (progress < 1) requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [value, duration]);

  // Reset if value changes
  useEffect(() => {
    started.current = false;
    setDisplay(0);
  }, [value]);

  return <span ref={ref}>{display.toLocaleString()}</span>;
}

// ── Custom Hook ───────────────────────────────────────────────────────────────
function useReveal() {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) el.classList.add("revealed"); },
      { threshold: 0.12 }
    );

    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return ref;
}

// ── Constants ─────────────────────────────────────────────────────────────────
const FILE_TYPES = ["PDF", "DOCX", "PNG", "JPG", "TIFF"];

const FEATURES = [
  {
    title: "3 Document Types",
    desc: "Supports ID Cards, Passports, and Driver Licenses — the most common identity documents worldwide.",
    icon: <><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M3 9h18M9 21V9" /></>,
  },
  {
    title: "9+ Countries",
    desc: "Works with documents from Greece, Russia, Latvia, Slovakia, Azerbaijan, Albania, and more.",
    icon: <><circle cx="12" cy="12" r="10" /><path d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20" /></>,
  },
  {
    title: "AI-Powered Detection",
    desc: "Advanced deep learning models trained on thousands of real and forged documents to spot forgeries with high accuracy.",
    icon: <><circle cx="12" cy="12" r="3" /><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" /></>,
  },
  {
    title: "Instant Results",
    desc: "Get a clear verdict — Authentic or Forged — with a confidence score in just a few seconds.",
    icon: <><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></>,
  },
  {
    title: "Forgery Type Analysis",
    desc: "When a fake is detected, the system identifies the fraud method — face morphing or face replacement.",
    icon: <><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></>,
  },
  {
    title: "PDF Reports",
    desc: "Download a detailed report for every scan with the full analysis breakdown and confidence scores.",
    icon: <><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /></>,
  },
];

const STEPS = [
  { num: "01", title: "Upload",  desc: "Take a photo or upload an image of your identity document" },
  { num: "02", title: "Analyze", desc: "Our AI instantly checks if the document is authentic or forged" },
  { num: "03", title: "Results", desc: "Get a clear verdict with a detailed report you can download" },
];

const ROLES = [
  {
    badge: "Guest", cls: "badge-guest", title: "Guest",
    perms: ["View landing page", "Read product description", "Register for an account"],
  },
  {
    badge: "User", cls: "badge-user", title: "Registered User",
    perms: ["Upload documents for scanning", "View analysis results", "Access personal scan history", "Manage profile settings"],
  },
  {
    badge: "Admin", cls: "badge-admin", title: "Administrator",
    perms: ["All user permissions", "View & manage all users", "Edit and delete accounts", "Access full analytics", "Modify user permissions"],
  },
];

const STACK = [
  "React", "FastAPI", "PyTorch", "Torchvision",
  "ViT", "ResNet-18",
  "MongoDB Atlas", "Cloudinary",
  "JWT Auth", "RBAC",
  "Python", "REST API",
  "Jupyter Lab", "Git", "IDNET Dataset"
];

// ── Sub-components ────────────────────────────────────────────────────────────
const SvgIcon = ({ children }) => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none"
    stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    {children}
  </svg>
);

const DocCard = ({ className, badge, badgeCls = "" }) => (
  <div className={`doc-card ${className}`}>
    <div className="doc-line" />
    <div className="doc-line short" />
    <div className="doc-line" />
    <div className={`doc-badge ${badgeCls}`}>{badge}</div>
  </div>
);

// ── Page Component ────────────────────────────────────────────────────────────
export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthed } = useAuth();

  // Redirect logged-in users to dashboard
  useEffect(() => {
    if (isAuthed) navigate("/dashboard", { replace: true });
  }, [isAuthed, navigate]);

  // Fetch real stats from API
  const [stats, setStats] = useState({ total_users: 0, total_scans: 0, forged: 0, authentic: 0 });
  useEffect(() => {
    fetch(`${API_URL}/scans/public/stats`)
      .then(r => r.json())
      .then(d => setStats(d))
      .catch(() => {});
  }, []);

  const statsRef    = useReveal();
  const featuresRef = useReveal();
  const flowRef     = useReveal();
  const rolesRef    = useReveal();
  const stackRef    = useReveal();

  return (
    <>
      <Navbar />

      {/* HERO */}
      <section className="hero">
        <div className="hero-glow" />
        <div className="hero-grid" />

        <DocCard className="doc-card-1" badge="✓ Verified" />
        <DocCard className="doc-card-2" badge="⚠ Forged" badgeCls="red" />
        <DocCard className="doc-card-3" badge="✓ Verified" />
        <DocCard className="doc-card-4" badge="AI Scan" />

        <div className="badge">
          <span className="badge-dot" /> Now in beta
        </div>

        <h1 className="hero-title">
          Docu<em>Guard</em><br />Detect forged<br /><em>ID documents</em>
        </h1>

        <p className="hero-sub">
          DocuGuard uses advanced Machine Learning powered by PyTorch to analyze and
          identify fraudulent identity documents in seconds fast, secure, and reliable.
        </p>

<div className="hero-actions">
  {isAuthed ? (
    <>
      <button className="btn-primary-lg" onClick={() => navigate("/scan")}>Start scanning →</button>
      <a href="#how-it-works" className="btn-ghost-lg">How it works</a>
    </>
  ) : (
<>
  <div
    className="signin-cta"
    style={{ transform: "translateX(-35px)" }} // שמאלה
  >
    <span className="pointerFx" aria-hidden="true">
      <span className="pointerTrail" />
      <span className="spark s1">✦</span>
      <span className="spark s2">✧</span>
      <span className="spark s3">✦</span>
      👉
    </span>

    <button className="btn-ghost-lg cta-glow" onClick={() => navigate("/login")}>
      Sign in
    </button>
  </div>
</>
  )}
</div>
      </section>

      {/* STATS */}
      <div className="stats reveal-block" ref={statsRef}>
        <div className="stat">
          <div className="stat-num"><AnimatedCounter value={stats.total_users} /></div>
          <div className="stat-label">Registered Users</div>
        </div>
        <div className="stat">
          <div className="stat-num"><AnimatedCounter value={stats.total_scans} /></div>
          <div className="stat-label">Documents Scanned</div>
        </div>
        <div className="stat">
          <div className="stat-num"><AnimatedCounter value={stats.authentic} /></div>
          <div className="stat-label">Authentic</div>
        </div>
        <div className="stat">
          <div className="stat-num"><AnimatedCounter value={stats.forged} /></div>
          <div className="stat-label">Forged Detected</div>
        </div>
      </div>

{isAuthed && (
  <section className="section" id="upload">
    <div className="scan-cta-card">
      <div className="scan-cta-icon">
        <SvgIcon>
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" />
        </SvgIcon>
      </div>
      <h2 className="scan-cta-title">Ready to scan a document?</h2>
      <p className="scan-cta-sub">Upload an ID, Passport, or Driver License and let our AI classify it in seconds.</p>
      <div className="scan-cta-tags">
        {FILE_TYPES.map(t => <span className="tag" key={t}>{t}</span>)}
      </div>
      <button className="btn-primary-lg" onClick={() => navigate("/scan")}>
        Scan document →
      </button>
    </div>
  </section>
)}

      {/* FEATURES */}
      <section className="section" id="features">
        <h2 className="section-title">What we offer</h2>
        <p className="section-sub">Verify identity documents from multiple countries in seconds</p>

        <div className="features-grid reveal-block" ref={featuresRef}>
          {FEATURES.map(f => (
            <div className="card" key={f.title}>
              <div className="card-icon">
                <SvgIcon>{f.icon}</SvgIcon>
              </div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <div className="flow-section" id="how-it-works">
        <div className="section">
          <h2 className="section-title">How it works</h2>
          <p className="section-sub">Verify any document in seconds — it's that simple</p>

          <div className="flow-steps reveal-block" ref={flowRef}>
            {STEPS.map(s => (
              <div className="step" key={s.num}>
                <div className="step-num">{s.num}</div>
                <h4>{s.title}</h4>
                <p>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

<ScanDemo />

{/* TECH STACK */}
<div className="stack-section">
  <section className="section">
    <h2 className="section-title">Tech stack</h2>
    <p className="section-sub">Technologies and models</p>

    <div className="stack-grid reveal-block" ref={stackRef}>
      {STACK.map(s => (
        <div className="stack-item" key={s}>
          <span className="stack-dot" />{s}
        </div>
      ))}
    </div>
  </section>
</div>

{!isAuthed && (
  <>
      {/* CTA */}
      <div className="cta-section">
        <h2>Ready to get started?</h2>
        <p>Join thousands of users already protecting themselves from document fraud.</p>
        <button className="btn-primary-lg" onClick={() => navigate("/register")}>
          Create free account →
        </button>
      </div>
  </>
)}



      {/* FOOTER */}
      <footer className="footer">
        <a className="logo" href="/"><span className="logo-text">Docu<em>Guard</em></span></a>
        <p>© 2026 DocuGuard — All rights reserved</p>
        <div className="footer-links">
          <a href="#" className="btn-ghost">Privacy</a>
          <a href="#" className="btn-ghost">Terms</a>
        </div>
      </footer>
    </>
  );
}

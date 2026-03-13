import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import ScanDemo from "../components/ScanDemo";
import "./LandingPage.css";



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
const STATS = [
  { num: "10K+",  label: "Registered users" },
  { num: "50M+",  label: "Documents scanned" },
  { num: "99.9%", label: "Uptime SLA" },
  { num: "98%",   label: "Detection accuracy" },
];

const FILE_TYPES = ["PDF", "DOCX", "PNG", "JPG", "TIFF"];

const FEATURES = [
  {
    title: "Document Type Classification",
    desc: "Automatically identifies whether the uploaded document is an ID Card, Passport, or Driver License before running forgery detection.",
    icon: <><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M3 9h18M9 21V9" /></>,
  },
  {
    title: "Dual AI Models (ViT & ResNet-18)",
    desc: "Two deep learning models  Vision Transformer (ViT) and ResNet-18 analyze each document and return Authentic vs. Forged with a confidence score.",
    icon: <><circle cx="12" cy="12" r="3" /><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" /></>,
  },
  {
    title: "Smart Preprocessing",
    desc: "Each image is automatically cropped, aligned, resized, normalized, and denoised to maximize model accuracy before classification.",
    icon: <><path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" /></>,
  },
  {
    title: "Multi-Document & Multi-Country",
    desc: "Supports ID Cards, Passports, and Driver Licenses from 9 countries including GRC, RUS, LVA, SVK, AZ, ALB and more.",
    icon: <><circle cx="12" cy="12" r="10" /><path d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20" /></>,
  },
  {
    title: "Trained on IDNET Dataset",
    desc: "9,000 balanced images — 3,000 per document type   ensuring fair and accurate detection across all document categories.",
    icon: <><ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" /><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" /></>,
  },
  {
    title: "Scan History & Audit Logs",
    desc: "Every scan is stored in MongoDB Atlas with document type, forgery result, confidence score, and timestamp for full traceability.",
    icon: <><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></>,
  },
];

const STEPS = [
  { num: "01", title: "Create Account",  desc: "Register with your email or Google account and verify your identity" },
  { num: "02", title: "Login",           desc: "Sign in to your DocuGuard account to access the platform" },
  { num: "03", title: "Upload Document", desc: "Upload a photo of an ID card, Passport, or Driver License" },
  { num: "04", title: "Choose Model",    desc: "Select an AI model — Vision Transformer (ViT) or ResNet-18" },
  { num: "05", title: "Run Scan",        desc: "Click Scan and let the AI analyze your document in seconds" },
  { num: "06", title: "View Result",     desc: "Get an instant verdict: Authentic or Forged with a confidence score" },
  { num: "07", title: "Download Report", desc: "Export a full PDF report with the scan details and results" },
  { num: "08", title: "Scan History",    desc: "Access all your previous scans anytime from your profile" },
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

  const token = localStorage.getItem("token");
const user = JSON.parse(localStorage.getItem("user") || "null");
const isAuthed = Boolean(token);

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
        {STATS.map(s => (
          <div className="stat" key={s.label}>
            <div className="stat-num">{s.num}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
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
        <h2 className="section-title">Everything you need</h2>
        <p className="section-sub">A complete platform for managing, analyzing, and verifying documents</p>

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
          <p className="section-sub">{STEPS.length} simple steps — from registration to result</p>

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
        <p>© 2025 DocuGuard — All rights reserved</p>
        <div className="footer-links">
          <a href="#" className="btn-ghost">Privacy</a>
          <a href="#" className="btn-ghost">Terms</a>
        </div>
      </footer>
    </>
  );
}

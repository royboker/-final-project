import { useState, useEffect, useRef } from "react";
import "./ScanDemo.css";

// ── Constants ─────────────────────────────────────────────────────────────────
const DOC_TYPES = ["id", "passport", "license"];

const DOC_LABELS     = { id: "ID Card",            passport: "Passport",               license: "Driver License"             };
const DOC_IDENTIFIED = { id: "ID Card Identified", passport: "Passport Identified",    license: "Driver License Identified"  };
const DOC_FORGE_MDL  = { id: "ID Forgery Model",   passport: "Passport Forgery Model", license: "Driving License Forgery Model" };
const DOC_IMGS       = { id: "/img/ID_CARD.jpg",         passport: "/img/passport.jpg",      license: "/img/driver.jpg"            };

const CONFIDENCE = {
  id:       { vit: 97.3, resnet: 91.4 },
  passport: { vit: 86.2, resnet: 93.7 },
  license:  { vit: 88.9, resnet: 95.1 },
};

const DETECT_STEPS = [
  { label: "Reading image metadata",    dur: 500 },
  { label: "Analyzing visual features", dur: 650 },
  { label: "Matching document pattern", dur: 550 },
];

const SCAN_STEPS = [
  { label: "Uploading document",         dur: 700  },
  { label: "Validating input",           dur: 550  },
  { label: "Preprocessing image",        dur: 850  },
  { label: "Classifying document type",  dur: 650  },
  { label: "Running forgery detection",  dur: 1000 },
];

const PIP_LABELS = ["Choose model", "Pick document", "Detecting type…", "Scanning…", "Result"];

// ── Doc icon ──────────────────────────────────────────────────────────────────
function DocIcon({ type }) {
  if (type === "id") return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2"/>
      <path d="M14 9h4M14 12h4M14 15h2"/>
    </svg>
  );
  if (type === "passport") return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="2" width="16" height="20" rx="2"/><circle cx="12" cy="10" r="3"/>
      <path d="M8 18h8M9 15h6"/>
    </svg>
  );
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="11" r="2"/>
      <path d="M14 9h4M14 12h3M6 16h12"/>
    </svg>
  );
}


// ── Ring progress (rounded rect border) ─────────────────────────────────────
function RingProgress({ progress, W = 110, H = 140 }) {
  const stroke = 3, r = 13;
  const perimeter = 2 * (W - 2 * r) + 2 * (H - 2 * r) + 2 * Math.PI * r;
  const offset = perimeter - (progress / 100) * perimeter;
  const pad = stroke + 1;
  return (
    <svg width={W + pad * 2} height={H + pad * 2} viewBox={`0 0 ${W + pad * 2} ${H + pad * 2}`}
      style={{ position: "absolute", top: -pad, left: -pad, pointerEvents: "none", zIndex: 2 }}>
      <rect x={pad} y={pad} width={W} height={H} rx={r} ry={r}
        fill="none" stroke="#e63946" strokeWidth={stroke} strokeLinecap="round"
        strokeDasharray={perimeter} strokeDashoffset={offset}
        style={{ transition: "stroke-dashoffset 0.04s linear" }}
      />
    </svg>
  );
}

// ── Main ──────────────────────────────────────────────────────────────────────
export default function ScanDemo() {
  const [model,        setModel]        = useState(null);
  const [phase,        setPhase]        = useState("idle");
  const [docType,      setDocType]      = useState(null);
  const [loadingDoc,   setLoadingDoc]   = useState(null);
  const [ringProgress, setRingProgress] = useState(0);
  const [detectStep,   setDetectStep]   = useState(0);
  const [scanStep,     setScanStep]     = useState(0);
  const [scanProgress, setScanProgress] = useState(0);
  const [verdict,      setVerdict]      = useState(null);
  const [pip,          setPip]          = useState(0);
  const rafRef = useRef(null);

  // ── Step 1: model ─────────────────────────────────────────────────────────
  function selectModel(m) {
    setModel(m);
    setPip(1);
    setPhase("pick");
  }

  // ── Step 2: doc card click → ring ─────────────────────────────────────────
function pickDoc(docId) {
  if (phase !== "pick") return;
  
  setLoadingDoc(docId);
  setRingProgress(0);
  setPhase("loading");

  const duration = 1200;
  const start = performance.now();
  
  function animate(now) {
    const p = Math.min(((now - start) / duration) * 100, 100);
    setRingProgress(p);
    if (p < 100) {
      rafRef.current = requestAnimationFrame(animate);
    } else {
      const random = DOC_TYPES[Math.floor(Math.random() * 3)];
      setDocType(random);
      setPip(2);
      setDetectStep(0);
      setPhase("detecting");
    }
  }
  
  setTimeout(() => {
    rafRef.current = requestAnimationFrame(animate);
  }, 50);
}

  // ── Step 3: detect steps ──────────────────────────────────────────────────
  useEffect(() => {
    if (phase !== "detecting") return;
    if (detectStep >= DETECT_STEPS.length) {
      const t = setTimeout(() => {
        setTimeout(() => { setPip(3); setScanStep(0); setScanProgress(0); setPhase("scanning"); }, 900);
      }, 200);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setDetectStep(s => s + 1), DETECT_STEPS[detectStep].dur);
    return () => clearTimeout(t);
  }, [phase, detectStep]);

  // ── Step 4: scan steps ────────────────────────────────────────────────────
  useEffect(() => {
    if (phase !== "scanning") return;
    if (scanStep >= SCAN_STEPS.length) {
      setScanProgress(100);
      const t = setTimeout(() => setPhase("tree"), 350);
      return () => clearTimeout(t);
    }
    const stepDur = SCAN_STEPS[scanStep].dur;
    const totalDur = SCAN_STEPS.reduce((s, x) => s + x.dur, 0);
    const baseProgress = SCAN_STEPS.slice(0, scanStep).reduce((s, x) => s + x.dur, 0);
    let t = 0;
    const iv = setInterval(() => {
      t += 25;
      const pct = Math.min(Math.round(((baseProgress + t) / totalDur) * 100), 99);
      setScanProgress(pct);
      if (t >= stepDur) { clearInterval(iv); setScanStep(s => s + 1); }
    }, 25);
    return () => clearInterval(iv);
  }, [phase, scanStep]);

  // ── Step 5: tree → result ─────────────────────────────────────────────────
  useEffect(() => {
    if (phase !== "tree") return;
    const t = setTimeout(() => {
      setVerdict(Math.random() > 0.4 ? "authentic" : "forged");
      setPip(4);
      setPhase("result");
    }, 2000);
    return () => clearTimeout(t);
  }, [phase]);

  useEffect(() => () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); }, []);

  // ── Reset ─────────────────────────────────────────────────────────────────
  function reset() {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    setModel(null); setPhase("idle"); setDocType(null);
    setLoadingDoc(null); setRingProgress(0); setDetectStep(0);
    setScanStep(0); setScanProgress(0); setVerdict(null); setPip(0);
  }

  const mLabel     = model === "vit" ? "ViT" : "ResNet-18";
  const confidence = docType && model ? CONFIDENCE[docType][model] : null;

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <section className="demo-section">
      <h2 className="section-title">See it in action</h2>
      <p className="section-sub">Choose your AI model, pick a document, and watch the pipeline run</p>

      <div className="demo-box">

        {/* LEFT */}
        <div className="demo-left">
          <div>
            <div className="demo-lbl" style={{ marginBottom: "0.5rem" }}>Pipeline</div>
            <div className="demo-pips">
              {PIP_LABELS.map((_, i) => (
                <div key={i} className={`demo-pip ${i < pip ? "done" : i === pip ? "active" : ""}`} />
              ))}
              <span className="demo-pip-lbl">{PIP_LABELS[pip]}</span>
            </div>
          </div>

          <div className="demo-divider" />

          <div>
            <div className="demo-lbl">01 — AI Model</div>
            {["vit", "resnet"].map(m => (
              <button key={m}
                className={`demo-model-btn ${m} ${model === m ? "active" : ""}`}
                disabled={model !== null}
                onClick={() => selectModel(m)}
              >
                <span className="demo-mdot" />
                <span>
                  {m === "vit" ? "ViT" : "ResNet-18"}
                  <span className="demo-msub">{m === "vit" ? "Vision Transformer" : "Residual Network 18"}</span>
                </span>
              </button>
            ))}
          </div>

          <div className="demo-divider" />

          <div className="demo-summary">
            <div className="demo-lbl">Status</div>
            <div className="demo-sum-row">
              <span className="demo-sum-key">Model</span>
              <span className={`demo-sum-val ${model ? model : "empty"}`}>{model ? mLabel : "—"}</span>
            </div>
            <div className="demo-sum-row">
              <span className="demo-sum-key">Doc type</span>
              <span className={`demo-sum-val ${docType ? "" : "empty"}`}>{docType ? DOC_LABELS[docType] : "—"}</span>
            </div>
            <div className="demo-sum-row">
              <span className="demo-sum-key">Verdict</span>
              <span className={`demo-sum-val ${verdict || "empty"}`}>
                {verdict ? (verdict === "authentic" ? "✓ Authentic" : "⚠ Forged") : "—"}
              </span>
            </div>
          </div>

          <div className="demo-divider" />
          {phase === "result" && (
            <button className="demo-reset-btn" onClick={reset}>↩ Start over</button>
          )}
        </div>

        {/* RIGHT */}
        <div className="demo-right">

          {/* IDLE */}
          {phase === "idle" && (
            <div className="demo-idle">
              <div className="demo-idle-ring">
                <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </div>
              <p>Choose a model to begin</p>
            </div>
          )}

          {/* PICK / LOADING */}
          {(phase === "pick" || phase === "loading") && (
            <div className="demo-doc-pick">
              <div className={`demo-model-pill ${model}`}>✓ &nbsp;{mLabel} ready</div>
              <p className="demo-pick-label">Pick a document to scan</p>
              <div className="demo-doc-cards">
                {DOC_TYPES.map(d => (
                  <div key={d}
                    className={`demo-doc-card ${loadingDoc === d ? "loading" : ""}`}
                    onClick={() => pickDoc(d)}
                    style={{ cursor: phase === "loading" ? "not-allowed" : "pointer" }}
                  >
<div className="demo-doc-img-wrap" style={{ position: "relative" }}>
  <div className="demo-doc-icon-box">
    <DocIcon type={d} />
  </div>
  {loadingDoc === d && <RingProgress progress={ringProgress} W={110} H={140} />}
</div>
                    <span className="demo-doc-label">{DOC_LABELS[d]}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* DETECTING */}
          {phase === "detecting" && (
            <div className="demo-detecting">
              <div className="demo-spin-wrap">
                <div className="demo-spin-ring" />
                <div className="demo-spin-inner">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                  </svg>
                </div>
              </div>
              <div className="demo-detect-steps">
                {DETECT_STEPS.map((s, i) => (
                  <div key={i} className={`demo-dstep ${i < detectStep ? "done" : i === detectStep ? "active" : "pending"}`}>
                    <span className="demo-dsdot">{i < detectStep ? "✓" : i === detectStep ? "⟳" : "○"}</span>
                    <span>{s.label}</span>
                  </div>
                ))}
              </div>
              {detectStep >= DETECT_STEPS.length && docType && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.75rem", animation: "demoFadeUp 0.4s ease both" }}>
                  <div className="demo-doc-card-result">
                    <img
                      src={DOC_IMGS[docType]}
                      alt={DOC_LABELS[docType]}
                      className="demo-doc-card-img"
                      onError={e => { e.target.style.display = "none"; e.target.nextSibling.style.display = "flex"; }}
                    />
                    <div className="demo-doc-card-img-fallback">
                      <DocIcon type={docType} />
                    </div>
                    <div className="demo-doc-card-check">✓</div>
                  </div>
                  <div className={`demo-detected-badge ${docType}`}>✓ &nbsp;{DOC_LABELS[docType]} detected</div>
                </div>
              )}
            </div>
          )}

          {/* SCANNING */}
          {phase === "scanning" && docType && (
            <div className="demo-scanning">
              <div className="demo-scan-doc">
<div style={{ position: "relative", width: 64, height: 44, flexShrink: 0 }}>
  <img
    src={DOC_IMGS[docType]}
    alt={DOC_LABELS[docType]}
    style={{ width: 64, height: 44, borderRadius: "8px", objectFit: "cover", border: "1px solid var(--border)", display: "block" }}
    onError={e => { e.target.style.display = "none"; e.target.nextSibling.style.display = "flex"; }}
  />
  <div style={{ display: "none", width: 64, height: 44, borderRadius: "8px", background: "var(--surface2)", alignItems: "center", justifyContent: "center", color: "#e63946" }}>
    <DocIcon type={docType} />
  </div>
</div>

                <div className="demo-scan-info">
                  <span className="demo-scan-name">{DOC_LABELS[docType]}</span>
                  <span className="demo-scan-sub">Running {DOC_FORGE_MDL[docType]}</span>
                </div>
                <span className={`demo-mbadge ${model}`}>{mLabel}</span>
                <div className="demo-beam" />
              </div>
              <div className="demo-steps">
                {SCAN_STEPS.map((s, i) => (
                  <div key={i} className={`demo-step ${i < scanStep ? "done" : i === scanStep ? "active" : "pending"}`}>
                    <span className="demo-sdot">{i < scanStep ? "✓" : i === scanStep ? "⟳" : "○"}</span>
                    <span>{s.label}</span>
                  </div>
                ))}
              </div>
              <div className="demo-prog-wrap">
                <div className="demo-prog-track">
                  <div className="demo-prog-fill" style={{ width: `${scanProgress}%` }} />
                </div>
                <span className="demo-prog-pct">{scanProgress}%</span>
              </div>
            </div>
          )}

          {/* TREE */}
          {(phase === "tree" || phase === "result") && docType && (
            <div className={phase === "result" ? "" : "demo-tree-wrap"}>
              {phase === "tree" && (
                <div className="demo-tree">
                  <div className="demo-tree-lbl">Classification pipeline</div>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <span className="demo-tnode demo-troot">Document Image</span>
                    <div className="demo-tconn" />
                    <span className="demo-tnode demo-tclassifier">Document Type Classifier</span>
                    <div className="demo-tconn" />
                    <div className="demo-trow">
                      {DOC_TYPES.map(d => (
                        <div key={d} className={`demo-tcol ${d !== docType ? "dim" : ""}`}>
                          <div className="demo-tconn" />
                          <span className="demo-tnode demo-tidentified">{DOC_IDENTIFIED[d]}</span>
                          <div className="demo-tconn" />
                          <span className={`demo-tnode demo-tmodel ${d === docType ? model : "dim"}`}>{DOC_FORGE_MDL[d]}</span>
                        </div>
                      ))}
                    </div>
                    <div className="demo-model-sel-row">
                      Running:&nbsp;
                      <span className={`demo-tnode demo-tmodel ${model}`} style={{ padding: "0.1rem 0.55rem", fontSize: "0.68rem" }}>{mLabel}</span>
                      &nbsp;on&nbsp;
                      <span className="demo-tnode demo-tidentified" style={{ padding: "0.1rem 0.55rem", fontSize: "0.68rem" }}>{DOC_LABELS[docType]}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* RESULT */}
              {phase === "result" && verdict && (
                <div className="demo-result">
                  <div className={`demo-verdict ${verdict}`}>
                    <div className="demo-vicon">{verdict === "authentic" ? "✓" : "⚠"}</div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.8rem", flex: 1 }}>
                      <div style={{ position: "relative", flexShrink: 0 }}>
                        <img
                          src={DOC_IMGS[docType]}
                          alt={DOC_LABELS[docType]}
                          style={{ width: 72, height: 48, borderRadius: "8px", objectFit: "cover", border: "2px solid rgba(255,255,255,0.1)" }}
                          onError={e => e.target.style.display = "none"}
                        />
                      </div>
                      <div>
                        <h3>{verdict === "authentic" ? "Authentic Document" : "Forged Document"}</h3>
                        <p>Detected by {mLabel} · {DOC_LABELS[docType]}</p>
                      </div>
                    </div>
                  </div>
                  <div className={`demo-conf ${verdict}`}>
                    <div className="demo-conf-hdr">
                      <span>Confidence Score</span>
                      <span className="demo-conf-val">{confidence}%</span>
                    </div>
                    <div className="demo-conf-track">
                      <div className="demo-conf-fill" style={{ width: `${confidence}%` }} />
                    </div>
                  </div>
                  <div className="demo-meta">
                    {[
                      { lbl: "Document",   val: DOC_LABELS[docType], cls: "" },
                      { lbl: "Model",      val: mLabel,              cls: model },
                      { lbl: "Confidence", val: `${confidence}%`,    cls: "" },
                      { lbl: "Verdict",    val: verdict === "authentic" ? "✓ Authentic" : "⚠ Forged", cls: verdict },
                    ].map(item => (
                      <div className="demo-mcard" key={item.lbl}>
                        <span className="demo-mlbl">{item.lbl}</span>
                        <span className={`demo-mval ${item.cls}`}>{item.val}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </section>
  );
}

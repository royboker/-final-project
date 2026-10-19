import { useState, useRef, useCallback, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import Navbar from "../components/Navbar";
import "./ScanPage.css";

import { API_URL } from "../config.js";

const CONF_COLOR = (c) => {
  if (c >= 0.8) return "high";
  if (c >= 0.55) return "mid";
  return "low";
};

const BRANCH_LABELS = ["ID Card", "Passport", "Driver License"];

export default function ScanPage() {
  const { token } = useAuth();
  const toast = useToast();

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [pipelineStep, setPipelineStep] = useState(0);
  const [pendingResult, setPendingResult] = useState(null);
  const [saveImage, setSaveImage] = useState(true);

  const inputRef = useRef(null);

  // ── File handling ───────────────────────────────────────────────────────────
  const handleFile = useCallback((f) => {
    if (!f || !f.type.startsWith("image/")) {
      setError("Only image files are supported (JPG, PNG, etc.)");
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  }, []);

  const onInputChange = (e) => handleFile(e.target.files[0]);

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  // ── Analyze (full pipeline) ───────────────────────────────────────────────
  const analyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setPendingResult(null);

    try {
      const form = new FormData();
      form.append("file", file);
      form.append("save_image", saveImage);

      // Wait for API + minimum time to show steps 0-2
      const [res] = await Promise.all([
        fetch(`${API_URL}/scans/analyze`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: form,
        }),
        new Promise((r) => setTimeout(r, 2600)),
      ]);

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Analysis failed");

      // Step 3 — highlight winner branch (doc type result)
      setPendingResult(data);
      setPipelineStep(3);
      await new Promise((r) => setTimeout(r, 1300));

      // Step 4 — binary forgery model
      setPipelineStep(4);
      await new Promise((r) => setTimeout(r, 1200));

      // Step 5 — fraud type (if applicable)
      if (data.binary?.predicted === "Fake" && data.fraud_type) {
        setPipelineStep(5);
        await new Promise((r) => setTimeout(r, 1000));
      }

      // Done — show results
      setResult(data);
      toast({ message: "Document analysis complete", type: "success" });
    } catch (err) {
      setError(err.message);
      toast({ message: err.message, type: "error" });
    } finally {
      setLoading(false);
    }
  };

  // ── Download PDF Report ─────────────────────────────────────────────────────
  const downloadReport = async (scanId, imagePrivate) => {
    let res;
    if (imagePrivate && file) {
      const form = new FormData();
      form.append("image_file", file);
      res = await fetch(`${API_URL}/scans/${scanId}/report`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
    } else {
      res = await fetch(`${API_URL}/scans/${scanId}/report`, {
        headers: { Authorization: `Bearer ${token}` },
      });
    }
    if (!res.ok) { toast({ message: "Failed to download report", type: "error" }); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `docuguard-report-${scanId.slice(0, 8)}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ── Pipeline animation — steps 1 & 2 on timers, 3+ set manually ──────────
  useEffect(() => {
    if (!loading) {
      setPipelineStep(0);
      setPendingResult(null);
      return;
    }
    const timers = [
      setTimeout(() => setPipelineStep(1), 800),
      setTimeout(() => setPipelineStep(2), 1800),
    ];
    return () => timers.forEach(clearTimeout);
  }, [loading]);

  // ── Reset ────────────────────────────────────────────────────────────────────
  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const canScan = file && !loading;

  // Derive pipeline status text
  const getPipelineTitle = () => {
    if (pipelineStep >= 5 && pendingResult) return "Fraud type identified";
    if (pipelineStep >= 4 && pendingResult?.binary) {
      return pendingResult.binary.predicted === "Fake"
        ? "Forgery detected — analyzing fraud type..."
        : `Document is authentic`;
    }
    if (pipelineStep >= 3 && pendingResult) return `Identified: ${pendingResult.doc_type?.predicted} — checking forgery...`;
    return "Analyzing document...";
  };

  return (
    <>
      <Navbar />
      <div className="scan-page">
        <div className="scan-header">
          <h1>Document Scanner</h1>
          <p>Upload an identity document for full analysis</p>
        </div>

        <div className="scan-layout">
          {/* ── LEFT PANEL ── */}
          <div className="scan-left">
            {/* Upload */}
            <div className="scan-card">
              <div className="scan-card-label">01 — Upload Document</div>
              <div
                className={`scan-dropzone ${dragging ? "drag-over" : ""} ${file ? "has-file" : ""}`}
                onClick={() => !file && inputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={onInputChange}
                />
                {!file ? (
                  <>
                    <div className="scan-drop-icon">
                      <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" />
                      </svg>
                    </div>
                    <p className="scan-drop-title">Drag & drop or click to upload</p>
                    <p className="scan-drop-sub">JPG, PNG, WEBP</p>
                  </>
                ) : (
                  <div className="scan-file-preview">
                    <img src={preview} alt="preview" className="scan-preview-img" />
                    <div className="scan-file-info">
                      <span className="scan-file-name">{file.name}</span>
                      <span className="scan-file-size">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                    <button
                      className="scan-remove-btn"
                      onClick={(e) => { e.stopPropagation(); reset(); }}
                      title="Remove file"
                    >✕</button>
                  </div>
                )}
              </div>
            </div>

            {/* Privacy toggle */}
            <div className="scan-privacy-card">
              <label className="scan-privacy-toggle">
                <div className="scan-privacy-info">
                  <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
                  </svg>
                  <div>
                    <span className="scan-privacy-label">Save document image</span>
                    <span className="scan-privacy-sub">
                      {saveImage ? "Your document image will be stored in history" : "Only scan results saved — image stays private"}
                    </span>
                  </div>
                </div>
                <div className={`scan-privacy-switch ${saveImage ? "on" : "off"}`} onClick={() => setSaveImage(v => !v)}>
                  <div className="scan-privacy-thumb" />
                </div>
              </label>
            </div>

            {/* Scan button */}
            <button
              className="scan-submit-btn"
              onClick={analyze}
              disabled={!canScan}
            >
              {loading ? (
                <><span className="scan-spinner" /> Analyzing...</>
              ) : (
                <> Scan Document</>
              )}
            </button>

            {error && (
              <div className="scan-error">
                <span>⚠</span> {error}
              </div>
            )}
          </div>

          {/* ── RIGHT PANEL ── */}
          <div className="scan-right">
            {!result && !loading && (
              <div className="scan-empty">
                <div className="scan-empty-icon">
                  <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <path d="M3 9h18M9 21V9" />
                  </svg>
                </div>
                <p className="scan-empty-title">Results will appear here</p>
                <p className="scan-empty-sub">Upload a document to get started with full analysis</p>
              </div>
            )}

            {loading && (
              <div className="scan-pipeline">
                <p className="scan-pipeline-title">{getPipelineTitle()}</p>

                {/* Node 1 — Document Image */}
                <div className={`sp-node sp-node-root ${pipelineStep >= 0 ? "active" : ""}`}>
                  <div className="sp-node-icon">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>
                    </svg>
                  </div>
                  <span>Document Image</span>
                </div>

                {/* Connector */}
                <div className={`sp-line ${pipelineStep >= 1 ? "active" : ""}`} />

                {/* Node 2 — Doc Type Classifier */}
                <div className={`sp-node sp-node-classifier ${pipelineStep >= 1 ? "active" : ""} ${pipelineStep === 1 ? "pulse" : ""}`}>
                  <div className="sp-node-icon">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/>
                    </svg>
                  </div>
                  <span>Document Type Classifier</span>
                  <span className="sp-stage-badge">Stage 1</span>
                </div>

                {/* 3 branches */}
                <div className={`sp-branches ${pipelineStep >= 2 ? "active" : ""} ${pipelineStep >= 4 ? "post-select" : ""} ${pendingResult && pipelineStep >= 3 ? `winner-${BRANCH_LABELS.indexOf(pendingResult.doc_type?.predicted)}` : ""}`}>
                  {/* Top T-junction */}
                  <div className="sp-t-row">
                    <div className="sp-t-stub" /><div className="sp-t-stub" /><div className="sp-t-stub" />
                  </div>

                  {/* 3 branch nodes */}
                  <div className="sp-branch-nodes">
                    {BRANCH_LABELS.map((label, i) => {
                      const isWinner = pipelineStep >= 3 && pendingResult?.doc_type?.predicted === label;
                      const isLoser  = pipelineStep >= 3 && pendingResult && pendingResult.doc_type?.predicted !== label;
                      return (
                        <div
                          key={label}
                          className={`sp-node sp-node-branch
                            ${pipelineStep >= 2 ? "active" : ""}
                            ${pipelineStep === 2 ? "pulse" : ""}
                            ${isWinner ? "winner" : ""}
                            ${isLoser  ? "loser"  : ""}`}
                          style={{ animationDelay: `${i * 0.12}s` }}
                        >
                          <span className="sp-branch-dot" />
                          <span>{label}</span>
                          {isWinner && <span className="sp-winner-check">✓</span>}
                        </div>
                      );
                    })}
                  </div>

                  {/* Bottom T-junction */}
                  <div className="sp-t-row sp-t-row-bottom">
                    <div className="sp-t-stub" /><div className="sp-t-stub" /><div className="sp-t-stub" />
                  </div>
                </div>

                {/* Connector to binary */}
                <div className={`sp-line ${pipelineStep >= 4 ? "active" : ""}`} />

                {/* Node — Binary Forgery Detection */}
                <div className={`sp-node sp-node-binary ${pipelineStep >= 4 ? "active" : ""} ${pipelineStep === 4 && !pendingResult?.binary ? "pulse" : ""} ${pendingResult?.binary?.predicted === "Real" ? "sp-real" : ""} ${pendingResult?.binary?.predicted === "Fake" ? "sp-fake" : ""}`}>
                  <div className="sp-node-icon">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                  </div>
                  <span>Forgery Detection</span>
                  <span className="sp-stage-badge">Stage 2</span>
                  {pipelineStep >= 4 && pendingResult?.binary && (
                    <span className={`sp-verdict-chip ${pendingResult.binary.predicted === "Real" ? "real" : "fake"}`}>
                      {pendingResult.binary.predicted} ({(pendingResult.binary.confidence * 100).toFixed(0)}%)
                    </span>
                  )}
                </div>

                {/* Fraud type section (only if Fake) */}
                {pendingResult?.binary?.predicted === "Fake" && (
                  <>
                    <div className={`sp-line ${pipelineStep >= 5 ? "active" : ""}`} />
                    <div className={`sp-node sp-node-fraud ${pipelineStep >= 5 ? "active" : ""} ${pipelineStep === 5 ? "pulse" : ""}`}>
                      <div className="sp-node-icon">
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                        </svg>
                      </div>
                      <span>Fraud Type Analysis</span>
                      <span className="sp-stage-badge">Stage 3</span>
                      {pipelineStep >= 5 && pendingResult?.fraud_type && (
                        <span className="sp-fraud-chip">
                          {pendingResult.fraud_type.predicted === "face_morphing" ? "Face Morphing" : "Face Replacement"}
                        </span>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}

            {result && (
              <div className="scan-result">
                {/* Demo banner */}
                {result.demo && (
                  <div className="scan-demo-banner">
                    Demo mode — model files not loaded. Results are simulated.
                  </div>
                )}

                {/* Verdict banner */}
                <div className={`scan-verdict ${result.verdict === "Real" ? "verdict-real" : result.verdict?.startsWith("Fake") ? "verdict-fake" : ""}`}>
                  <div className={`scan-verdict-icon ${result.verdict === "Real" ? "icon-real" : result.verdict?.startsWith("Fake") ? "icon-fake" : ""}`}>
                    {result.verdict === "Real" ? (
                      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    ) : result.verdict?.startsWith("Fake") ? (
                      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                  </div>
                  <div>
                    <div className="scan-verdict-label">Verdict</div>
                    <div className="scan-verdict-type">{result.verdict || "Classification only"}</div>
                  </div>
                  <div className="scan-verdict-badge pipeline">Pipeline</div>
                </div>

                {/* Document Type */}
                {result.doc_type && (
                  <div className="scan-stage-card">
                    <div className="scan-stage-header">
                      <span className="scan-stage-num">Stage 1</span>
                      <span className="scan-stage-name">Document Type</span>
                      <span className={`scan-conf-val ${CONF_COLOR(result.doc_type.confidence)}`}>
                        {(result.doc_type.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="scan-stage-result">{result.doc_type.predicted}</div>
                    <div className="scan-probs">
                      {Object.entries(result.doc_type.probabilities)
                        .sort(([, a], [, b]) => b - a)
                        .map(([label, prob]) => (
                          <div key={label} className={`scan-prob-row ${label === result.doc_type.predicted ? "top" : ""}`}>
                            <span className="scan-prob-name">
                              {label === result.doc_type.predicted && <span className="scan-prob-check">✓</span>}
                              {label}
                            </span>
                            <div className="scan-prob-bar-wrap">
                              <div className="scan-prob-bar" style={{ width: `${(prob * 100).toFixed(1)}%` }} />
                            </div>
                            <span className="scan-prob-pct">{(prob * 100).toFixed(1)}%</span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Binary Result */}
                {result.binary && (
                  <div className={`scan-stage-card ${result.binary.predicted === "Real" ? "stage-real" : "stage-fake"}`}>
                    <div className="scan-stage-header">
                      <span className="scan-stage-num">Stage 2</span>
                      <span className="scan-stage-name">Forgery Detection</span>
                      <span className={`scan-conf-val ${CONF_COLOR(result.binary.confidence)}`}>
                        {(result.binary.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className={`scan-stage-result ${result.binary.predicted === "Real" ? "text-real" : "text-fake"}`}>
                      {result.binary.predicted}
                    </div>
                    <div className="scan-probs">
                      {Object.entries(result.binary.probabilities)
                        .sort(([, a], [, b]) => b - a)
                        .map(([label, prob]) => (
                          <div key={label} className={`scan-prob-row ${label === result.binary.predicted ? "top" : ""}`}>
                            <span className="scan-prob-name">
                              {label === result.binary.predicted && <span className="scan-prob-check">✓</span>}
                              {label}
                            </span>
                            <div className="scan-prob-bar-wrap">
                              <div className={`scan-prob-bar ${label === "Fake" && label === result.binary.predicted ? "bar-fake" : ""}`} style={{ width: `${(prob * 100).toFixed(1)}%` }} />
                            </div>
                            <span className="scan-prob-pct">{(prob * 100).toFixed(1)}%</span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Fraud Type Result */}
                {result.fraud_type && (
                  <div className="scan-stage-card stage-fraud">
                    <div className="scan-stage-header">
                      <span className="scan-stage-num">Stage 3</span>
                      <span className="scan-stage-name">Fraud Type</span>
                      <span className={`scan-conf-val ${CONF_COLOR(result.fraud_type.confidence)}`}>
                        {(result.fraud_type.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="scan-stage-result text-fraud">
                      {result.fraud_type.predicted === "face_morphing" ? "Face Morphing" : "Face Replacement"}
                    </div>
                    <div className="scan-probs">
                      {Object.entries(result.fraud_type.probabilities)
                        .sort(([, a], [, b]) => b - a)
                        .map(([label, prob]) => (
                          <div key={label} className={`scan-prob-row ${label === result.fraud_type.predicted ? "top" : ""}`}>
                            <span className="scan-prob-name">
                              {label === result.fraud_type.predicted && <span className="scan-prob-check">✓</span>}
                              {label === "face_morphing" ? "Face Morphing" : "Face Replacement"}
                            </span>
                            <div className="scan-prob-bar-wrap">
                              <div className="scan-prob-bar bar-fraud" style={{ width: `${(prob * 100).toFixed(1)}%` }} />
                            </div>
                            <span className="scan-prob-pct">{(prob * 100).toFixed(1)}%</span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Meta */}
                <div className="scan-meta-grid">
                  {[
                    { label: "Document", value: result.doc_type?.predicted },
                    { label: "Verdict", value: result.verdict, cls: result.verdict === "Real" ? "real" : result.verdict?.startsWith("Fake") ? "fake" : "ok" },
                    { label: "Stages", value: `${result.stages_completed?.length || 0} / 3` },
                    { label: "Status", value: "Complete", cls: "ok" },
                  ].map((item) => (
                    <div className="scan-meta-card" key={item.label}>
                      <span className="scan-meta-lbl">{item.label}</span>
                      <span className={`scan-meta-val ${item.cls || ""}`}>{item.value}</span>
                    </div>
                  ))}
                </div>

                {result.models_used && Object.keys(result.models_used).length > 0 && (
                  <div className="scan-meta-grid" style={{ marginTop: "0.75rem" }}>
                    {[
                      { label: "Stage 1 · Doc Type", arch: result.models_used.doc_type },
                      { label: "Stage 2 · Binary", arch: result.models_used.binary },
                      { label: "Stage 3 · Fraud Type", arch: result.models_used.fraud_type },
                    ].filter(m => m.arch).map(m => (
                      <div className="scan-meta-card" key={m.label}>
                        <span className="scan-meta-lbl">{m.label}</span>
                        <span className="scan-meta-val">{m.arch.toUpperCase()}</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="scan-actions">
                  {result.scan_id && (
                    <button className="scan-download-btn" onClick={() => downloadReport(result.scan_id, result.image_private)}>
                      ↓ Download Report
                    </button>
                  )}
                  <button className="scan-again-btn" onClick={reset}>
                    ↩ Scan another document
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

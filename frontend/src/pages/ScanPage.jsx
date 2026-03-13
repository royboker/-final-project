import { useState, useRef, useCallback, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import Navbar from "../components/Navbar";
import "./ScanPage.css";

import { API_URL } from "../config.js";

const MODELS = [
  {
    id: "vit",
    label: "ViT",
    sub: "Vision Transformer",
    desc: "Transformer-based model. Excellent at capturing global document structure.",
  },
  {
    id: "resnet18",
    label: "ResNet-18",
    sub: "Residual Network",
    desc: "CNN-based model. Fast and accurate for local feature extraction.",
  },
];

const CONF_COLOR = (c) => {
  if (c >= 0.8) return "high";
  if (c >= 0.55) return "mid";
  return "low";
};

const BRANCH_LABELS = ["ID Card", "Passport", "Driver License"];

export default function ScanPage() {
  const { token } = useAuth();
  const toast = useToast();

  const [model, setModel] = useState("vit");

  useEffect(() => {
    fetch(`${API_URL}/scans/settings/model`)
      .then(r => r.json())
      .then(d => setModel(d.model))
      .catch(() => setModel("vit"));
  }, []);

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [pipelineStep, setPipelineStep] = useState(0);
  const [pendingResult, setPendingResult] = useState(null); // holds result during winner reveal
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

  // ── Classify ────────────────────────────────────────────────────────────────
  const classify = async () => {
    if (!file || !model) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setPendingResult(null);

    try {
      const form = new FormData();
      form.append("file", file);
      form.append("model", model);
      form.append("save_image", saveImage);

      // Wait for API + minimum time to show steps 0-2
      const [res] = await Promise.all([
        fetch(`${API_URL}/scans/classify`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: form,
        }),
        new Promise((r) => setTimeout(r, 2600)),
      ]);

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Classification failed");

      // Step 3 — highlight winner branch
      setPendingResult(data);
      setPipelineStep(3);
      await new Promise((r) => setTimeout(r, 1300));

      // Step 4 — forgery model
      setPipelineStep(4);
      await new Promise((r) => setTimeout(r, 1000));

      // Done — show results
      setResult(data);
      toast({ message: "Document classified successfully", type: "success" });
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
      // Image was not saved to DB — send the original file so the PDF includes it
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

  // ── Pipeline animation — steps 1 & 2 on timers, 3 & 4 set manually ─────────
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
  const selectedModel = MODELS.find((m) => m.id === model);

  return (
    <>
      <Navbar />
      <div className="scan-page">
        <div className="scan-header">
          <h1>Document Scanner</h1>
          <p>Upload an identity document to classify it</p>
          {model && (
            <p style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.25rem" }}>
              AI Model: <span style={{ color: "#a3e635", fontWeight: 600 }}>{model === "vit" ? "ViT — Vision Transformer" : "ResNet-18"}</span>
            </p>
          )}
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
                    <p className="scan-drop-sub">JPG, PNG, WEBP · max 10 MB</p>
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
              onClick={classify}
              disabled={!canScan}
            >
              {loading ? (
                <><span className="scan-spinner" /> Analyzing…</>
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
                <p className="scan-empty-sub">Select a model and upload a document to get started</p>
              </div>
            )}

            {loading && (
              <div className="scan-pipeline">
                <p className="scan-pipeline-title">
                  {pipelineStep >= 3 && pendingResult
                    ? `Identified: ${pendingResult.predicted}`
                    : `Analyzing with ${selectedModel?.label}…`}
                </p>

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

                {/* Node 2 — Classifier */}
                <div className={`sp-node sp-node-classifier ${pipelineStep >= 1 ? "active" : ""} ${pipelineStep === 1 ? "pulse" : ""}`}>
                  <div className="sp-node-icon">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/>
                    </svg>
                  </div>
                  <span>Document Type Classifier</span>
                </div>

                {/* 3 branches */}
                <div className={`sp-branches ${pipelineStep >= 2 ? "active" : ""} ${pipelineStep >= 4 ? "post-select" : ""} ${pendingResult && pipelineStep >= 3 ? `winner-${BRANCH_LABELS.indexOf(pendingResult.predicted)}` : ""}`}>
                  {/* Top T-junction: horizontal bar + 3 vertical stubs */}
                  <div className="sp-t-row">
                    <div className="sp-t-stub" /><div className="sp-t-stub" /><div className="sp-t-stub" />
                  </div>

                  {/* 3 branch nodes */}
                  <div className="sp-branch-nodes">
                    {BRANCH_LABELS.map((label, i) => {
                      const isWinner = pipelineStep >= 3 && pendingResult?.predicted === label;
                      const isLoser  = pipelineStep >= 3 && pendingResult && pendingResult.predicted !== label;
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

                {/* Node 4 — Forgery Model */}
                <div className={`sp-node sp-node-forgery ${pipelineStep >= 4 ? "active" : ""} ${pipelineStep === 4 ? "pulse" : ""}`}>
                  <div className="sp-node-icon">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                  </div>
                  <span>Forgery Detection Model</span>
                </div>
              </div>
            )}

            {result && (
              <div className="scan-result">
                {/* Demo banner */}
                {result.demo && (
                  <div className="scan-demo-banner">
                    Demo mode — model file not loaded yet. Results are simulated.
                  </div>
                )}

                {/* Verdict banner */}
                <div className="scan-verdict">
                  <div className="scan-verdict-icon">
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </div>
                  <div>
                    <div className="scan-verdict-label">Document Identified</div>
                    <div className="scan-verdict-type">{result.predicted}</div>
                  </div>
                  <div className={`scan-verdict-badge ${result.model_used}`}>
                    {selectedModel?.label}
                  </div>
                </div>

                {/* Confidence */}
                <div className="scan-conf-card">
                  <div className="scan-conf-header">
                    <span>Confidence Score</span>
                    <span className={`scan-conf-val ${CONF_COLOR(result.confidence)}`}>
                      {(result.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="scan-conf-track">
                    <div
                      className={`scan-conf-fill ${CONF_COLOR(result.confidence)}`}
                      style={{ width: `${(result.confidence * 100).toFixed(1)}%` }}
                    />
                  </div>
                </div>

                {/* Probability breakdown */}
                <div className="scan-probs">
                  <div className="scan-probs-label">Probability Distribution</div>
                  {Object.entries(result.probabilities)
                    .sort(([, a], [, b]) => b - a)
                    .map(([label, prob]) => (
                      <div key={label} className={`scan-prob-row ${label === result.predicted ? "top" : ""}`}>
                        <span className="scan-prob-name">
                          {label === result.predicted && <span className="scan-prob-check">✓</span>}
                          {label}
                        </span>
                        <div className="scan-prob-bar-wrap">
                          <div className="scan-prob-bar" style={{ width: `${(prob * 100).toFixed(1)}%` }} />
                        </div>
                        <span className="scan-prob-pct">{(prob * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                </div>

                {/* Meta */}
                <div className="scan-meta-grid">
                  {[
                    { label: "Document", value: result.predicted },
                    { label: "Model", value: selectedModel?.label, cls: result.model_used },
                    { label: "Confidence", value: `${(result.confidence * 100).toFixed(1)}%` },
                    { label: "Status", value: "Classified", cls: "ok" },
                  ].map((item) => (
                    <div className="scan-meta-card" key={item.label}>
                      <span className="scan-meta-lbl">{item.label}</span>
                      <span className={`scan-meta-val ${item.cls || ""}`}>{item.value}</span>
                    </div>
                  ))}
                </div>

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

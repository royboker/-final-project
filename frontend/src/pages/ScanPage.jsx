import { useState, useRef, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import "./ScanPage.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

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

export default function ScanPage() {
  const { token } = useAuth();

  const [model, setModel] = useState(null);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

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

    try {
      const form = new FormData();
      form.append("file", file);
      form.append("model", model);

      const res = await fetch(`${API_URL}/scans/classify`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Classification failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ── Download PDF Report ─────────────────────────────────────────────────────
  const downloadReport = async (scanId) => {
    const res = await fetch(`${API_URL}/scans/${scanId}/report`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `docuguard-report-${scanId.slice(0, 8)}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ── Reset ────────────────────────────────────────────────────────────────────
  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setModel(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const canScan = file && model && !loading;
  const selectedModel = MODELS.find((m) => m.id === model);

  return (
    <>
      <Navbar />
      <div className="scan-page">
        <div className="scan-header">
          <h1>Document Scanner</h1>
          <p>Upload an identity document and select a model to classify it</p>
        </div>

        <div className="scan-layout">
          {/* ── LEFT PANEL ── */}
          <div className="scan-left">
            {/* Model selector */}
            <div className="scan-card">
              <div className="scan-card-label">01 — Choose AI Model</div>
              <div className="scan-models">
                {MODELS.map((m) => (
                  <button
                    key={m.id}
                    className={`scan-model-btn ${m.id} ${model === m.id ? "active" : ""}`}
                    onClick={() => setModel(m.id)}
                    disabled={loading}
                  >
                    <span className="scan-mdot" />
                    <span className="scan-model-text">
                      <span className="scan-model-name">{m.label}</span>
                      <span className="scan-model-sub">{m.sub}</span>
                    </span>
                    {model === m.id && <span className="scan-check">✓</span>}
                  </button>
                ))}
              </div>
              {selectedModel && (
                <p className="scan-model-desc">{selectedModel.desc}</p>
              )}
            </div>

            {/* Upload */}
            <div className="scan-card">
              <div className="scan-card-label">02 — Upload Document</div>
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
              <div className="scan-analyzing">
                <div className="scan-pulse-ring" />
                <div className="scan-analyzing-steps">
                  {["Uploading document", "Preprocessing image", "Running model inference", "Generating result"].map((s, i) => (
                    <div key={i} className="scan-astep">
                      <span className="scan-astep-dot" />
                      <span>{s}</span>
                    </div>
                  ))}
                </div>
                <p className="scan-analyzing-label">Analyzing with {selectedModel?.label}…</p>
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
                    <button className="scan-download-btn" onClick={() => downloadReport(result.scan_id)}>
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

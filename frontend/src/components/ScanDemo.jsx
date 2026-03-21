import { useState, useEffect, useRef } from "react";
import "./ScanDemo.css";

const DOC_IMGS = {
  passport: "/img/passport.jpg",
  id: "/img/ID_CARD.jpg",
  license: "/img/driver.jpg",
};

// Auto-playing demo that shows the real scan pipeline flow
export default function ScanDemo() {
  const [step, setStep] = useState(0);
  const [visible, setVisible] = useState(false);
  const sectionRef = useRef(null);
  const timerRef = useRef(null);

  // Start animation when section scrolls into view
  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !visible) {
          setVisible(true);
          runDemo();
        }
      },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [visible]);

  function runDemo() {
    setStep(0);
    const delays = [800, 1400, 1200, 1500, 1200, 1500, 2000];
    let total = 0;
    const timers = [];
    delays.forEach((d, i) => {
      total += d;
      timers.push(setTimeout(() => setStep(i + 1), total));
    });
    // Loop after completion
    timers.push(setTimeout(() => {
      setStep(0);
      setTimeout(() => runDemo(), 1200);
    }, total + 3000));
    timerRef.current = timers;
  }

  useEffect(() => {
    return () => {
      if (timerRef.current) timerRef.current.forEach(clearTimeout);
    };
  }, []);

  return (
    <section className="demo-section" ref={sectionRef}>
      <h2 className="section-title">See it in action</h2>
      <p className="section-sub">Watch how DocuGuard analyzes a document in real time</p>

      <div className="demo-flow-box">
        {/* Step indicators */}
        <div className="demo-flow-steps">
          {["Upload", "Classify", "Detect Forgery", "Result"].map((label, i) => (
            <div key={label} className={`demo-flow-step ${step >= (i + 1) ? "done" : step === i ? "active" : ""}`}>
              <div className="demo-flow-dot">
                {step > i ? (
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                ) : (
                  <span>{i + 1}</span>
                )}
              </div>
              <span className="demo-flow-label">{label}</span>
              {i < 3 && <div className={`demo-flow-line ${step > i ? "done" : ""}`} />}
            </div>
          ))}
        </div>

        {/* Visual area */}
        <div className="demo-flow-visual">

          {/* Step 0: Idle / Upload */}
          {step === 0 && (
            <div className="demo-v-center fade-in">
              <div className="demo-v-upload-icon">
                <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                </svg>
              </div>
              <p className="demo-v-text">Uploading document...</p>
            </div>
          )}

          {/* Step 1: Document uploaded, show image */}
          {step === 1 && (
            <div className="demo-v-center fade-in">
              <div className="demo-v-doc-preview">
                <img src={DOC_IMGS.passport} alt="Passport" onError={e => e.target.style.display = "none"} />
              </div>
              <p className="demo-v-text">Document received</p>
            </div>
          )}

          {/* Step 2: Classifying - show pipeline node animation */}
          {step === 2 && (
            <div className="demo-v-pipeline fade-in">
              <div className="demo-v-node active pulse">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/>
                </svg>
                <span>Classifying document type...</span>
              </div>
              <div className="demo-v-branches scanning">
                <span className="demo-v-branch">ID Card</span>
                <span className="demo-v-branch">Passport</span>
                <span className="demo-v-branch">Driver License</span>
              </div>
            </div>
          )}

          {/* Step 3: Doc type identified */}
          {step === 3 && (
            <div className="demo-v-pipeline fade-in">
              <div className="demo-v-node done">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span>Document Type: <strong>Passport</strong></span>
              </div>
              <div className="demo-v-branches resolved">
                <span className="demo-v-branch loser">ID Card</span>
                <span className="demo-v-branch winner">Passport</span>
                <span className="demo-v-branch loser">Driver License</span>
              </div>
            </div>
          )}

          {/* Step 4: Forgery detection running */}
          {step === 4 && (
            <div className="demo-v-pipeline fade-in">
              <div className="demo-v-node done small">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span>Passport</span>
              </div>
              <div className="demo-v-connector" />
              <div className="demo-v-node active pulse">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
                <span>Checking for forgery...</span>
              </div>
            </div>
          )}

          {/* Step 5: Forgery detected, analyzing type */}
          {step === 5 && (
            <div className="demo-v-pipeline fade-in">
              <div className="demo-v-node fake-node">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
                <span>Forgery Detected</span>
                <span className="demo-v-chip fake">Fake — 94%</span>
              </div>
              <div className="demo-v-connector" />
              <div className="demo-v-node active pulse warn">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <span>Identifying fraud type...</span>
              </div>
            </div>
          )}

          {/* Step 6: Fraud type identified */}
          {step === 6 && (
            <div className="demo-v-pipeline fade-in">
              <div className="demo-v-node fake-node small">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
                <span>Fake</span>
              </div>
              <div className="demo-v-connector" />
              <div className="demo-v-node warn-done">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span>Fraud Type: <strong>Face Morphing</strong></span>
                <span className="demo-v-chip warn">87%</span>
              </div>
            </div>
          )}

          {/* Step 7: Final result */}
          {step >= 7 && (
            <div className="demo-v-result fade-in">
              <div className="demo-v-result-card">
                <div className="demo-v-result-icon">
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </div>
                <div className="demo-v-result-info">
                  <span className="demo-v-result-verdict">Forged Document</span>
                  <span className="demo-v-result-detail">Passport — Face Morphing detected</span>
                </div>
              </div>
              <div className="demo-v-result-grid">
                <div className="demo-v-result-stat">
                  <span className="demo-v-stat-label">Document</span>
                  <span className="demo-v-stat-value">Passport</span>
                </div>
                <div className="demo-v-result-stat">
                  <span className="demo-v-stat-label">Verdict</span>
                  <span className="demo-v-stat-value fake">Fake</span>
                </div>
                <div className="demo-v-result-stat">
                  <span className="demo-v-stat-label">Fraud Type</span>
                  <span className="demo-v-stat-value warn">Face Morphing</span>
                </div>
                <div className="demo-v-result-stat">
                  <span className="demo-v-stat-label">Confidence</span>
                  <span className="demo-v-stat-value">94%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

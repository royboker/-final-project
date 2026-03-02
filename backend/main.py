from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.scan import router as scan_router

app = FastAPI(title="DocuGuard API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(scan_router)

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "DocuGuard API is running ✅"}

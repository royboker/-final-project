from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.scan import router as scan_router
from starlette.middleware.sessions import SessionMiddleware
from routes.admin import router as admin_router
from routes.chat import router as chat_router
import os


app = FastAPI(title="DocuGuard API", version="1.0.0")


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET", "secret"))
_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost")
ALLOWED_ORIGINS = [o.strip() for o in _origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(admin_router)
app.include_router(chat_router)

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "DocuGuard API is running ✅"}

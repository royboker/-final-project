from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from jose import jwt, JWTError
from bson import ObjectId
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os

from db.mongo import scans_collection

load_dotenv()

router = APIRouter(prefix="/scans", tags=["Scans"])
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"

# ── Request model ─────────────────────────────────────────────────────────────
class ScanCreate(BaseModel):
    file_url: str
    file_name: str
    doc_type: str
    model_used: str
    verdict: str
    confidence: float = Field(ge=0, le=1)  # 0..1

# ── Auth helper ───────────────────────────────────────────────────────────────
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return {"id": payload["sub"], "email": payload["email"], "role": payload["role"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Save scan ─────────────────────────────────────────────────────────────────
@router.post("/", status_code=201)
def save_scan(data: ScanCreate, user = Depends(get_current_user)):
    scan = {
        "user_id": user["id"],
        "file_url": data.file_url,
        "file_name": data.file_name,
        "doc_type": data.doc_type,
        "model_used": data.model_used,
        "verdict": data.verdict,
        "confidence": data.confidence,
        "scanned_at": datetime.utcnow(),
    }

    result = scans_collection.insert_one(scan)

    return {
        "message": "Scan saved",
        "scan_id": str(result.inserted_id)
    }

# ── Get my scans ──────────────────────────────────────────────────────────────
@router.get("/my")
def get_my_scans(user = Depends(get_current_user)):
    scans = list(scans_collection.find(
        {"user_id": user["id"]},
        sort=[("scanned_at", -1)]
    ))

    for s in scans:
        s["id"] = str(s.pop("_id"))

    return {"scans": scans}

# ── Get ALL scans (admin only) ────────────────────────────────────────────────
@router.get("/all")
def get_all_scans(user = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    scans = list(scans_collection.find({}, sort=[("scanned_at", -1)]))
    for s in scans:
        s["id"] = str(s.pop("_id"))

    return {"scans": scans}

# ── Get single scan ───────────────────────────────────────────────────────────
@router.get("/{scan_id}")
def get_scan(scan_id: str, user = Depends(get_current_user)):
    try:
        oid = ObjectId(scan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    scan = scans_collection.find_one({"_id": oid})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    scan["id"] = str(scan.pop("_id"))
    return scan
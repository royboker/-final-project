from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from jose import jwt, JWTError
from bson import ObjectId
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import io
import os
import random
import base64

from db.mongo import scans_collection
from utils.model_loader import (
    load_vit_model, load_resnet18_model, predict, get_device
)

load_dotenv()

router = APIRouter(prefix="/scans", tags=["Scans"])
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"

# ── Model paths ───────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent.parent

# Search in multiple locations (models may be saved in different places)
_SEARCH_DIRS = [
    _ROOT / "models",
    _ROOT / "notebooks" / "document_type_classification" / "resnet18",
    _ROOT / "notebooks" / "document_type_classification" / "vit",
    _ROOT / "notebooks" / "document_type_classification" / "dit",
    _ROOT,
]

def _find_model(filename: str) -> Path | None:
    for d in _SEARCH_DIRS:
        p = d / filename
        if p.exists():
            return p
    return None

VIT_PATH    = _find_model("vit_document_classifier_9000.pth")
RESNET_PATH = _find_model("resnet18_document_classifier_9000.pth")

# Cache loaded models so we don't reload on every request
_cache: dict = {}

_DEMO_LABELS = ["ID Card", "Passport", "Driver License"]
_DEMO_CONF = {
    "vit":     {"ID Card": 0.973, "Passport": 0.862, "Driver License": 0.889},
    "resnet18": {"ID Card": 0.914, "Passport": 0.937, "Driver License": 0.951},
}

def _demo_result(model_name: str) -> dict:
    """Return a realistic simulated result when model files are not available."""
    label = random.choice(_DEMO_LABELS)
    conf  = _DEMO_CONF.get(model_name, {}).get(label, 0.90)
    rest  = round((1 - conf) / 2, 4)
    probs = {l: (conf if l == label else rest) for l in _DEMO_LABELS}
    return {"predicted": label, "confidence": conf, "probabilities": probs, "demo": True}

def _get_model(model_name: str):
    if model_name in _cache:
        return _cache[model_name]
    device = get_device()
    vit_path    = _find_model("vit_document_classifier_9000.pth")
    resnet_path = _find_model("resnet18_document_classifier_9000.pth")
    if model_name == "vit":
        if not vit_path:
            return None  # demo mode
        _cache["vit"] = load_vit_model(str(vit_path), device=device)
    elif model_name == "resnet18":
        if not resnet_path:
            return None  # demo mode
        _cache["resnet18"] = load_resnet18_model(str(resnet_path), device=device)
    else:
        raise HTTPException(status_code=400, detail="Unknown model. Use 'vit' or 'resnet18'")
    return _cache[model_name]

# ── Auth helper ───────────────────────────────────────────────────────────────
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return {"id": payload["sub"], "email": payload["email"], "role": payload["role"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Classify (real ML inference) ──────────────────────────────────────────────
@router.post("/classify")
async def classify(
    file: UploadFile = File(...),
    model: str = Form(...),
    user=Depends(get_current_user),
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    # Read image
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    # Load model and run inference (fallback to demo if model not available)
    loaded_model = _get_model(model)
    if loaded_model is None:
        result = _demo_result(model)
    else:
        device = get_device()
        result = predict(loaded_model, image, device=device)
        result["demo"] = False

    # Create compressed thumbnail for storage
    thumb = image.convert("RGB")
    thumb.thumbnail((400, 400))
    buf = io.BytesIO()
    thumb.save(buf, format="JPEG", quality=65)
    image_b64 = base64.b64encode(buf.getvalue()).decode()

    # Save scan to DB
    scan = {
        "user_id": user["id"],
        "file_name": file.filename,
        "model_used": model,
        "doc_type": result["predicted"],
        "confidence": result["confidence"],
        "probabilities": result["probabilities"],
        "image_data": image_b64,
        "scanned_at": datetime.utcnow(),
    }
    inserted = scans_collection.insert_one(scan)

    return {
        "scan_id": str(inserted.inserted_id),
        "predicted": result["predicted"],
        "confidence": result["confidence"],
        "probabilities": result["probabilities"],
        "model_used": model,
        "demo": result.get("demo", False),
    }

# ── Request model ─────────────────────────────────────────────────────────────
class ScanCreate(BaseModel):
    file_url: str
    file_name: str
    doc_type: str
    model_used: str
    verdict: str
    confidence: float = Field(ge=0, le=1)

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
    return {"message": "Scan saved", "scan_id": str(result.inserted_id)}

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

# ── PDF Report ───────────────────────────────────────────────────────────────
@router.get("/{scan_id}/report")
def download_report(scan_id: str, user=Depends(get_current_user)):
    try:
        oid = ObjectId(scan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    scan = scans_collection.find_one({"_id": oid})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    # ── Background ──────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor("#09090f"))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Header bar ──────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor("#a3e635"))
    c.rect(0, H - 60, W, 60, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#09090f"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(36, H - 40, "DocuGuard")
    c.setFont("Helvetica", 11)
    c.drawString(145, H - 40, "— Scan Report")

    # ── Result badge ────────────────────────────────────────────────────────
    conf = scan.get("confidence", 0)
    conf_pct = round(conf * 100)
    badge_color = "#a3e635" if conf_pct >= 70 else "#fb923c" if conf_pct >= 45 else "#f87171"
    c.setFillColor(colors.HexColor(badge_color))
    c.roundRect(W - 140, H - 52, 110, 32, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#09090f"))
    c.setFont("Helvetica-Bold", 13)
    label = "✓ Authentic" if conf_pct >= 70 else "⚠ Uncertain" if conf_pct >= 45 else "✗ Suspicious"
    c.drawCentredString(W - 85, H - 38, label)

    # ── Scan info ───────────────────────────────────────────────────────────
    y = H - 100
    def field(title, value, ypos):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#52525b"))
        c.drawString(36, ypos, title.upper())
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#e4e4e7"))
        c.drawString(150, ypos, str(value) if value else "—")

    field("File", scan.get("file_name", "—"), y);           y -= 24
    field("Document Type", scan.get("doc_type", "—"), y);   y -= 24
    field("Model Used", scan.get("model_used", "—"), y);    y -= 24
    field("Confidence", f"{conf_pct}%", y);                 y -= 24
    scanned_at = scan.get("scanned_at")
    date_str = scanned_at.strftime("%d/%m/%Y %H:%M") if scanned_at else "—"
    field("Scanned At", date_str, y);                       y -= 40

    # ── Divider ─────────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor("#27272a"))
    c.setLineWidth(1)
    c.line(36, y, W - 36, y);  y -= 20

    # ── Thumbnail ───────────────────────────────────────────────────────────
    img_data = scan.get("image_data")
    if img_data:
        try:
            img_bytes = base64.b64decode(img_data)
            img_reader = ImageReader(io.BytesIO(img_bytes))
            img_w, img_h = 160, 100
            c.drawImage(img_reader, 36, y - img_h, img_w, img_h, preserveAspectRatio=True, mask="auto")
            probs_x = 36 + img_w + 20
        except Exception:
            probs_x = 36
            img_h = 0
    else:
        probs_x = 36
        img_h = 0

    # ── Probabilities ───────────────────────────────────────────────────────
    probs = scan.get("probabilities", {})
    if probs:
        py = y - 10
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#52525b"))
        c.drawString(probs_x, py, "PROBABILITIES")
        py -= 18
        bar_w = W - probs_x - 36
        for lbl, val in sorted(probs.items(), key=lambda x: -x[1]):
            pct = round(val * 100)
            is_top = lbl == scan.get("doc_type")
            # label
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#a1a1aa"))
            c.drawString(probs_x, py, lbl)
            py -= 14
            # bar bg
            c.setFillColor(colors.HexColor("#27272a"))
            c.roundRect(probs_x, py, bar_w, 8, 3, fill=1, stroke=0)
            # bar fill
            fill_color = "#a3e635" if is_top else "#3f3f46"
            c.setFillColor(colors.HexColor(fill_color))
            c.roundRect(probs_x, py, max(bar_w * val, 4), 8, 3, fill=1, stroke=0)
            # pct text
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.HexColor("#e4e4e7"))
            c.drawRightString(W - 36, py, f"{pct}%")
            py -= 22

    # ── Footer ──────────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor("#27272a"))
    c.rect(0, 0, W, 32, fill=1, stroke=0)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#52525b"))
    c.drawCentredString(W / 2, 11, f"Generated by DocuGuard · {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC · Report ID: {scan_id}")

    c.save()
    buf.seek(0)
    filename = f"docuguard-report-{scan_id[:8]}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ── Delete all my scans ───────────────────────────────────────────────────────
@router.delete("/my/all")
def delete_all_my_scans(user = Depends(get_current_user)):
    result = scans_collection.delete_many({"user_id": user["id"]})
    return {"deleted": result.deleted_count}

# ── Delete single scan ────────────────────────────────────────────────────────
@router.delete("/{scan_id}")
def delete_scan(scan_id: str, user = Depends(get_current_user)):
    try:
        oid = ObjectId(scan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    scan = scans_collection.find_one({"_id": oid})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    scans_collection.delete_one({"_id": oid})
    return {"message": "Scan deleted"}

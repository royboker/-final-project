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

from db.mongo import scans_collection, users_collection, db

settings_col = db["settings"]
from utils.model_loader import (
    load_vit_model, load_resnet18_model, predict, get_device,
    load_binary_model, load_fraud_type_model,
    load_dit_binary_model, load_dit_fraud_type_model,
    predict_image, predict_with_tta,
    DOC_TYPE_LABELS, BINARY_LABELS, FRAUD_TYPE_LABELS,
)

load_dotenv()

router = APIRouter(prefix="/scans", tags=["Scans"])
security = HTTPBearer()

from config import JWT_SECRET, ALGORITHM

# ── Model paths ───────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent.parent
_MODELS_DIR = _ROOT / "models" / "final_models"

def _find_model(filename: str) -> Path | None:
    p = _MODELS_DIR / filename
    return p if p.exists() else None

VIT_PATH    = _find_model("vit_document_classifier_9k.pth")
RESNET_PATH = _find_model("resnet18_document_classifier_9k.pth")

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
    vit_path    = _find_model("vit_document_classifier_9k.pth")
    resnet_path = _find_model("resnet18_document_classifier_9k.pth")
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

# ── Pipeline model paths (all 14 models loaded from models/final_models/) ────
# Roles:
#   doc_type_vit, doc_type_resnet18           (document type classifier)
#   <doctype>_binary_<arch>                   (binary forgery — vit/dit)
#   <doctype>_fraud_type_<arch>               (fraud type — vit/dit)
_PIPELINE_PATHS = {
    # Document type classifiers
    "doc_type_vit":                   str(_MODELS_DIR / "vit_document_classifier_9k.pth"),
    "doc_type_resnet18":              str(_MODELS_DIR / "resnet18_document_classifier_9k.pth"),
    # ViT-Small forgery models
    "passport_binary_vit":            str(_MODELS_DIR / "vit_passport_binary_20k.pth"),
    "passport_fraud_type_vit":        str(_MODELS_DIR / "vit_passport_fraud_type_20k.pth"),
    "id_card_binary_vit":             str(_MODELS_DIR / "vit_id_card_binary_20k.pth"),
    "id_card_fraud_type_vit":         str(_MODELS_DIR / "vit_id_card_fraud_type_20k.pth"),
    "drivers_license_binary_vit":     str(_MODELS_DIR / "vit_drivers_license_binary_15k.pth"),
    "drivers_license_fraud_type_vit": str(_MODELS_DIR / "vit_drivers_license_fraud_type_15k.pth"),
    # DiT-Base forgery models
    "passport_binary_dit":            str(_MODELS_DIR / "dit_passport_binary_20k.pth"),
    "passport_fraud_type_dit":        str(_MODELS_DIR / "dit_passport_fraud_type_20k.pth"),
    "id_card_binary_dit":             str(_MODELS_DIR / "dit_id_card_binary_20k.pth"),
    "id_card_fraud_type_dit":         str(_MODELS_DIR / "dit_id_card_fraud_type_20k.pth"),
    "drivers_license_binary_dit":     str(_MODELS_DIR / "dit_drivers_license_binary_15k.pth"),
    "drivers_license_fraud_type_dit": str(_MODELS_DIR / "dit_drivers_license_fraud_type_15k.pth"),
}

DOC_TYPE_TO_PREFIX = {
    "ID Card": "id_card",
    "Passport": "passport",
    "Driver License": "drivers_license",
}

# ── Active-model settings (admin-configurable, stored in MongoDB) ────────────
_ACTIVE_MODELS_KEY = "active_models"
_ACTIVE_MODELS_DEFAULTS = {
    "doc_type": "vit",                       # vit | resnet18
    "passport_binary": "vit",                # vit | dit
    "passport_fraud_type": "vit",
    "id_card_binary": "vit",
    "id_card_fraud_type": "vit",
    "drivers_license_binary": "vit",
    "drivers_license_fraud_type": "vit",
}
_ACTIVE_MODELS_ALLOWED = {
    "doc_type": {"vit", "resnet18"},
    "passport_binary": {"vit", "dit"},
    "passport_fraud_type": {"vit", "dit"},
    "id_card_binary": {"vit", "dit"},
    "id_card_fraud_type": {"vit", "dit"},
    "drivers_license_binary": {"vit", "dit"},
    "drivers_license_fraud_type": {"vit", "dit"},
}


def _get_active_models() -> dict:
    """Return admin-selected model arch for each pipeline slot,
    merging stored values over defaults."""
    doc = settings_col.find_one({"key": _ACTIVE_MODELS_KEY})
    stored = doc.get("value", {}) if doc else {}
    return {**_ACTIVE_MODELS_DEFAULTS, **{k: v for k, v in stored.items() if k in _ACTIVE_MODELS_DEFAULTS}}


# Role-keyed model cache for the pipeline
_pipeline_cache: dict = {}

def _load_pipeline_model(role: str):
    """Load and cache a pipeline model by role.

    Role naming:
      doc_type_vit, doc_type_resnet18
      <doctype>_binary_<arch>       (arch in {vit, dit})
      <doctype>_fraud_type_<arch>
    """
    if role in _pipeline_cache:
        return _pipeline_cache[role]

    path = _PIPELINE_PATHS.get(role)
    if not path or not Path(path).exists():
        return None

    device = get_device()
    if role == "doc_type_vit":
        model = load_vit_model(path, device=device)
    elif role == "doc_type_resnet18":
        model = load_resnet18_model(path, device=device)
    elif role.endswith("_binary_vit"):
        model = load_binary_model(path, device=device)
    elif role.endswith("_fraud_type_vit"):
        model = load_fraud_type_model(path, device=device)
    elif role.endswith("_binary_dit"):
        model = load_dit_binary_model(path, device=device)
    elif role.endswith("_fraud_type_dit"):
        model = load_dit_fraud_type_model(path, device=device)
    else:
        return None

    _pipeline_cache[role] = model
    return model


def run_pipeline(image: Image.Image, device: str) -> dict:
    """
    Run the 3-stage pipeline using admin-configured model selection:
      Stage 1: Document type classification (vit | resnet18)
      Stage 2: Binary forgery detection        (vit | dit)
      Stage 3: Fraud type classification       (vit | dit, only if Fake)
    """
    active = _get_active_models()
    # models_used tracks which arch ran at each stage that actually executed
    models_used: dict = {}
    result = {"stages_completed": [], "demo": False, "models_used": models_used, "active_models": active}

    # ── Stage 1: Document Type ────────────────────────────────────────────
    doc_arch = active["doc_type"]
    doc_role = f"doc_type_{doc_arch}"
    doc_model = _load_pipeline_model(doc_role)
    if doc_model is None:
        result["demo"] = True
        result["doc_type"] = _demo_result(doc_arch)
        result["stages_completed"].append("doc_type")
        return result

    doc_result = predict_image(doc_model, image, device=device, label_map=DOC_TYPE_LABELS)
    result["doc_type"] = doc_result
    result["stages_completed"].append("doc_type")
    models_used["doc_type"] = doc_arch

    # ── Stage 2: Binary (Real / Fake) ─────────────────────────────────────
    predicted_type = doc_result["predicted"]
    prefix = DOC_TYPE_TO_PREFIX.get(predicted_type)
    if not prefix:
        result["binary"] = None
        result["fraud_type"] = None
        result["verdict"] = "Classification only"
        return result

    binary_arch = active[f"{prefix}_binary"]
    binary_role = f"{prefix}_binary_{binary_arch}"
    binary_model = _load_pipeline_model(binary_role)
    if binary_model is None:
        result["binary"] = None
        result["fraud_type"] = None
        result["verdict"] = "Classification only"
        return result

    binary_result = predict_with_tta(binary_model, image, device=device, label_map=BINARY_LABELS)
    result["binary"] = binary_result
    result["stages_completed"].append("binary")
    models_used["binary"] = binary_arch

    # ── Stage 3: Fraud Type (only if Fake) ────────────────────────────────
    if binary_result["predicted"] == "Real":
        result["fraud_type"] = None
        result["verdict"] = "Real"
        return result

    fraud_arch = active[f"{prefix}_fraud_type"]
    fraud_role = f"{prefix}_fraud_type_{fraud_arch}"
    fraud_model = _load_pipeline_model(fraud_role)
    if fraud_model is None:
        result["fraud_type"] = None
        result["verdict"] = "Fake"
        return result

    fraud_result = predict_with_tta(fraud_model, image, device=device, label_map=FRAUD_TYPE_LABELS)
    result["fraud_type"] = fraud_result
    result["stages_completed"].append("fraud_type")
    models_used["fraud_type"] = fraud_arch
    result["verdict"] = f"Fake - {fraud_result['predicted']}"

    return result


# ── Public stats (no auth required) ───────────────────────────────────────────
@router.get("/public/stats")
def get_public_stats():
    total_users = users_collection.count_documents({})
    total_scans = scans_collection.count_documents({})
    forged = scans_collection.count_documents({"verdict": {"$regex": "^Fake"}})
    authentic = scans_collection.count_documents({"verdict": "Real"})
    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "forged": forged,
        "authentic": authentic,
    }


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
    save_image: bool = Form(True),
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

    # Create thumbnail — real or privacy placeholder
    if save_image:
        thumb = image.convert("RGB")
        thumb.thumbnail((400, 400))
        buf = io.BytesIO()
        thumb.save(buf, format="JPEG", quality=65)
        image_b64 = base64.b64encode(buf.getvalue()).decode()
    else:
        # Generate a grey privacy placeholder with lock icon pattern
        from PIL import ImageDraw
        placeholder = Image.new("RGB", (400, 300), color=(30, 30, 40))
        draw = ImageDraw.Draw(placeholder)
        # Simple lock rectangle
        cx, cy = 200, 150
        draw.rounded_rectangle([cx-30, cy-20, cx+30, cy+30], radius=6, fill=(60, 60, 75))
        draw.arc([cx-18, cy-40, cx+18, cy-10], start=0, end=180, fill=(160, 160, 180), width=6)
        draw.text((cx, cy+55), "Image Hidden", fill=(100, 100, 120), anchor="mm")
        buf = io.BytesIO()
        placeholder.save(buf, format="JPEG", quality=80)
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
        "image_private": not save_image,
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
        "image_private": not save_image,
    }

# ── Analyze (full 3-stage pipeline) ───────────────────────────────────────────
@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    save_image: bool = Form(True),
    user=Depends(get_current_user),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    device = get_device()
    pipeline_result = run_pipeline(image, device)

    # Create thumbnail
    if save_image:
        thumb = image.convert("RGB")
        thumb.thumbnail((400, 400))
        buf = io.BytesIO()
        thumb.save(buf, format="JPEG", quality=65)
        image_b64 = base64.b64encode(buf.getvalue()).decode()
    else:
        from PIL import ImageDraw
        placeholder = Image.new("RGB", (400, 300), color=(30, 30, 40))
        draw = ImageDraw.Draw(placeholder)
        cx, cy = 200, 150
        draw.rounded_rectangle([cx-30, cy-20, cx+30, cy+30], radius=6, fill=(60, 60, 75))
        draw.arc([cx-18, cy-40, cx+18, cy-10], start=0, end=180, fill=(160, 160, 180), width=6)
        draw.text((cx, cy+55), "Image Hidden", fill=(100, 100, 120), anchor="mm")
        buf = io.BytesIO()
        placeholder.save(buf, format="JPEG", quality=80)
        image_b64 = base64.b64encode(buf.getvalue()).decode()

    # Determine overall confidence (deepest completed stage)
    if pipeline_result.get("fraud_type"):
        overall_confidence = pipeline_result["fraud_type"]["confidence"]
    elif pipeline_result.get("binary"):
        overall_confidence = pipeline_result["binary"]["confidence"]
    else:
        overall_confidence = pipeline_result["doc_type"]["confidence"]

    verdict = pipeline_result.get("verdict", "Classification only")

    # Save to DB
    models_used = pipeline_result.get("models_used", {})
    scan = {
        "user_id": user["id"],
        "file_name": file.filename,
        "pipeline": True,
        "model_used": "pipeline",
        "models_used": models_used,
        "doc_type": pipeline_result["doc_type"]["predicted"],
        "doc_type_confidence": pipeline_result["doc_type"]["confidence"],
        "doc_type_probabilities": pipeline_result["doc_type"]["probabilities"],
        "verdict": verdict,
        "binary_result": pipeline_result.get("binary"),
        "fraud_type_result": pipeline_result.get("fraud_type"),
        "stages_completed": pipeline_result["stages_completed"],
        "confidence": overall_confidence,
        "probabilities": pipeline_result["doc_type"]["probabilities"],
        "image_data": image_b64,
        "image_private": not save_image,
        "scanned_at": datetime.utcnow(),
    }
    inserted = scans_collection.insert_one(scan)

    return {
        "scan_id": str(inserted.inserted_id),
        "doc_type": pipeline_result["doc_type"],
        "binary": pipeline_result.get("binary"),
        "fraud_type": pipeline_result.get("fraud_type"),
        "verdict": verdict,
        "models_used": models_used,
        "stages_completed": pipeline_result["stages_completed"],
        "demo": pipeline_result.get("demo", False),
        "image_private": not save_image,
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
# POST version: accepts optional image file (used when image was not saved to DB)
@router.post("/{scan_id}/report")
async def download_report_with_image(
    scan_id: str,
    user=Depends(get_current_user),
    image_file: UploadFile = File(None),
):
    try:
        oid = ObjectId(scan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    scan = scans_collection.find_one({"_id": oid})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan["user_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # If caller provided the original image, use it for the PDF (overrides stored placeholder)
    if image_file:
        contents = await image_file.read()
        try:
            img = Image.open(io.BytesIO(contents)).convert("RGB")
            img.thumbnail((400, 400))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=65)
            scan["image_data"] = base64.b64encode(buf.getvalue()).decode()
        except Exception:
            pass  # fall back to stored image_data

    return _build_pdf_report(scan, scan_id)


def _draw_stage_section(c, y, W, *, title: str, arch: str | None,
                        predicted: str, confidence: float,
                        probabilities: dict, top_key: str | None) -> float:
    """Draw one pipeline stage: title bar + predicted line + probability bars.
    Returns the new y cursor."""
    # Section header (title + arch pill on the right)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#a3e635"))
    c.drawString(36, y, title.upper())
    if arch:
        c.setFillColor(colors.HexColor("#27272a"))
        c.roundRect(W - 80, y - 4, 44, 16, 4, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#a3e635"))
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(W - 58, y, arch.upper())
    y -= 18

    # Predicted line
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#e4e4e7"))
    c.drawString(36, y, str(predicted) if predicted else "—")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#a3e635"))
    c.drawRightString(W - 36, y, f"{round((confidence or 0) * 100)}%")
    y -= 14

    # Probability bars
    if probabilities:
        for lbl, val in sorted(probabilities.items(), key=lambda x: -x[1]):
            pct = round(val * 100)
            is_top = lbl == top_key
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.HexColor("#a1a1aa"))
            c.drawString(36, y, str(lbl))
            y -= 10
            bar_w = W - 36 - 36
            c.setFillColor(colors.HexColor("#27272a"))
            c.roundRect(36, y, bar_w, 6, 3, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#a3e635" if is_top else "#3f3f46"))
            c.roundRect(36, y, max(bar_w * val, 4), 6, 3, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(colors.HexColor("#e4e4e7"))
            c.drawRightString(W - 36, y, f"{pct}%")
            y -= 14

    return y - 8


def _build_pdf_report(scan: dict, scan_id: str) -> StreamingResponse:
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

    # ── Result badge (verdict-based for pipeline scans, confidence-based otherwise) ─
    verdict = scan.get("verdict")
    conf = scan.get("confidence", 0) or 0
    conf_pct = round(conf * 100)
    is_pipeline = bool(scan.get("pipeline")) or verdict is not None

    if is_pipeline and verdict:
        if verdict == "Real":
            badge_color, badge_label = "#a3e635", "✓ Authentic"
        elif verdict.startswith("Fake"):
            badge_color, badge_label = "#f87171", "✗ Forged"
        else:
            badge_color, badge_label = "#fb923c", "⚠ Unknown"
    else:
        if conf_pct >= 70:
            badge_color, badge_label = "#a3e635", "✓ Authentic"
        elif conf_pct >= 45:
            badge_color, badge_label = "#fb923c", "⚠ Uncertain"
        else:
            badge_color, badge_label = "#f87171", "✗ Suspicious"

    c.setFillColor(colors.HexColor(badge_color))
    c.roundRect(W - 140, H - 52, 110, 32, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#09090f"))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W - 85, H - 38, badge_label)

    # ── Top block: thumbnail on left, scan info on right ────────────────────
    y = H - 90
    img_data = scan.get("image_data")
    info_x = 36
    if img_data:
        try:
            img_bytes = base64.b64decode(img_data)
            img_reader = ImageReader(io.BytesIO(img_bytes))
            img_w, img_h = 160, 100
            c.drawImage(img_reader, 36, y - img_h, img_w, img_h,
                        preserveAspectRatio=True, mask="auto")
            info_x = 36 + img_w + 20
        except Exception:
            pass

    def field(title, value, ypos, x):
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#52525b"))
        c.drawString(x, ypos, title.upper())
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#e4e4e7"))
        c.drawString(x, ypos - 13, str(value) if value else "—")

    fy = y - 6
    field("File", scan.get("file_name", "—"), fy, info_x);            fy -= 28
    if is_pipeline:
        field("Verdict", verdict or "—", fy, info_x);                 fy -= 28
        field("Document Type", scan.get("doc_type", "—"), fy, info_x); fy -= 28
    else:
        field("Document Type", scan.get("doc_type", "—"), fy, info_x); fy -= 28
        field("Model Used",    scan.get("model_used", "—"), fy, info_x); fy -= 28
    scanned_at = scan.get("scanned_at")
    date_str = scanned_at.strftime("%d/%m/%Y %H:%M") if scanned_at else "—"
    field("Scanned At", date_str, fy, info_x)

    y -= 120  # below the top block

    # ── Divider ─────────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor("#27272a"))
    c.setLineWidth(1)
    c.line(36, y, W - 36, y);  y -= 22

    # ── Stage sections (pipeline scan) or single prob block (legacy) ────────
    models_used = scan.get("models_used", {}) or {}

    if is_pipeline:
        # Stage 1 — Document Type
        y = _draw_stage_section(
            c, y, W,
            title="Stage 1 · Document Type",
            arch=models_used.get("doc_type"),
            predicted=scan.get("doc_type"),
            confidence=scan.get("doc_type_confidence", 0) or 0,
            probabilities=scan.get("doc_type_probabilities") or scan.get("probabilities") or {},
            top_key=scan.get("doc_type"),
        )

        # Stage 2 — Binary (Real / Fake)
        binary = scan.get("binary_result") or {}
        if binary:
            y = _draw_stage_section(
                c, y, W,
                title="Stage 2 · Real / Fake",
                arch=models_used.get("binary"),
                predicted=binary.get("predicted"),
                confidence=binary.get("confidence", 0) or 0,
                probabilities=binary.get("probabilities") or {},
                top_key=binary.get("predicted"),
            )

        # Stage 3 — Fraud Type (only if executed)
        fraud = scan.get("fraud_type_result") or {}
        if fraud:
            y = _draw_stage_section(
                c, y, W,
                title="Stage 3 · Fraud Type",
                arch=models_used.get("fraud_type"),
                predicted=fraud.get("predicted"),
                confidence=fraud.get("confidence", 0) or 0,
                probabilities=fraud.get("probabilities") or {},
                top_key=fraud.get("predicted"),
            )
    else:
        # Legacy /classify scan — keep single probability block
        probs = scan.get("probabilities", {}) or {}
        y = _draw_stage_section(
            c, y, W,
            title="Classification Probabilities",
            arch=scan.get("model_used"),
            predicted=scan.get("doc_type"),
            confidence=conf,
            probabilities=probs,
            top_key=scan.get("doc_type"),
        )

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
    return _build_pdf_report(scan, scan_id)


# ── Model settings ───────────────────────────────────────────────────────────
@router.get("/settings/model")
def get_default_model():
    doc = settings_col.find_one({"key": "default_model"})
    return {"model": doc["value"] if doc else "vit"}

@router.put("/settings/model")
def set_default_model(data: dict, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    model = data.get("model", "vit")
    if model not in ["vit", "resnet18"]:
        raise HTTPException(status_code=400, detail="Invalid model")
    settings_col.update_one({"key": "default_model"}, {"$set": {"value": model}}, upsert=True)
    return {"model": model}


# ── Pipeline model settings (per-slot active model selection) ─────────────────
@router.get("/settings/pipeline-models")
def get_pipeline_models():
    """Return the currently active model arch for each pipeline slot."""
    return _get_active_models()


@router.put("/settings/pipeline-models")
def set_pipeline_models(data: dict, user=Depends(get_current_user)):
    """Admin updates one or more pipeline-slot model selections.
    Request body: { slot_name: arch, ... } — only included slots are updated."""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if not isinstance(data, dict) or not data:
        raise HTTPException(status_code=400, detail="Body must be a non-empty object of slot -> arch")

    unknown = [k for k in data if k not in _ACTIVE_MODELS_ALLOWED]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown slot(s): {unknown}")

    for slot, value in data.items():
        allowed = _ACTIVE_MODELS_ALLOWED[slot]
        if value not in allowed:
            raise HTTPException(status_code=400, detail=f"Invalid value for {slot}: must be one of {sorted(allowed)}")

    current = _get_active_models()
    merged = {**current, **data}
    settings_col.update_one(
        {"key": _ACTIVE_MODELS_KEY},
        {"$set": {"value": merged}},
        upsert=True,
    )
    return merged

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

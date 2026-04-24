import uuid
import io
from PIL import Image
from db.mongo import users_collection
from bson import ObjectId
from config import JWT_SECRET, ALGORITHM
from datetime import datetime, timedelta
from jose import jwt


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@pytest.com"


def make_token(role="user"):
    fake_id = str(ObjectId())
    email = unique_email()
    users_collection.insert_one({
        "_id": ObjectId(fake_id),
        "name": "Test",
        "email": email,
        "role": role,
        "is_verified": True,
        "created_at": datetime.utcnow(),
    })
    expire = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({"sub": fake_id, "email": email, "role": role, "exp": expire}, JWT_SECRET, algorithm=ALGORITHM)
    return token, fake_id


def make_image_bytes(color=(255, 255, 255)):
    img = Image.new("RGB", (100, 100), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


# ── Classify ──────────────────────────────────────────────────────────────────

def test_classify_vit(client):
    token, user_id = make_token()
    img = make_image_bytes()
    res = client.post(
        "/scans/classify",
        data={"model": "vit", "save_image": "true"},
        files={"file": ("test.jpg", img, "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "predicted" in data
    assert "confidence" in data
    assert data["predicted"] in ["ID Card", "Passport", "Driver License"]
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_classify_resnet18(client):
    token, user_id = make_token()
    img = make_image_bytes()
    res = client.post(
        "/scans/classify",
        data={"model": "resnet18", "save_image": "false"},
        files={"file": ("test.jpg", img, "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert "predicted" in res.json()
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_classify_unknown_model(client):
    token, user_id = make_token()
    img = make_image_bytes()
    res = client.post(
        "/scans/classify",
        data={"model": "unknown_model", "save_image": "false"},
        files={"file": ("test.jpg", img, "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_classify_non_image(client):
    token, user_id = make_token()
    res = client.post(
        "/scans/classify",
        data={"model": "vit", "save_image": "false"},
        files={"file": ("test.txt", b"not an image", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_classify_unauthenticated(client):
    img = make_image_bytes()
    res = client.post(
        "/scans/classify",
        data={"model": "vit", "save_image": "false"},
        files={"file": ("test.jpg", img, "image/jpeg")},
    )
    assert res.status_code in [401, 403, 422]


# ── Analyze (full pipeline) ───────────────────────────────────────────────────

def test_analyze_pipeline(client):
    token, user_id = make_token()
    img = make_image_bytes()
    res = client.post(
        "/scans/analyze",
        data={"save_image": "false"},
        files={"file": ("test.jpg", img, "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "doc_type" in data or "predicted" in data
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_analyze_no_file(client):
    token, user_id = make_token()
    res = client.post(
        "/scans/analyze",
        data={"save_image": "false"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422
    users_collection.delete_one({"_id": ObjectId(user_id)})


# ── Settings ──────────────────────────────────────────────────────────────────

def test_get_model_settings(client):
    token, user_id = make_token()
    res = client.get("/scans/settings/model", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_get_pipeline_models(client):
    token, user_id = make_token()
    res = client.get("/scans/settings/pipeline-models", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    users_collection.delete_one({"_id": ObjectId(user_id)})

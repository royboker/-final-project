import uuid
from db.mongo import users_collection
from bson import ObjectId


def create_verified_user(client):
    email = f"test_{uuid.uuid4().hex[:8]}@pytest.com"
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "TestPass123"})
    users_collection.update_one({"email": email}, {"$set": {"is_verified": True}})
    res = client.post("/auth/login", json={"email": email, "password": "TestPass123"})
    return res.json()["token"]


# ── Public Stats ──────────────────────────────────────────────────────────────

def test_public_stats(client):
    res = client.get("/scans/public/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data or "total_scans" in data


# ── My Scans ──────────────────────────────────────────────────────────────────

def test_get_my_scans_authenticated(client):
    token = create_verified_user(client)
    res = client.get("/scans/my", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list) or "scans" in data


def test_get_my_scans_unauthenticated(client):
    res = client.get("/scans/my")
    assert res.status_code in [401, 422]


# ── Delete Scans ──────────────────────────────────────────────────────────────

def test_delete_all_scans(client):
    token = create_verified_user(client)
    res = client.delete("/scans/my/all", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200


def test_delete_nonexistent_scan(client):
    token = create_verified_user(client)
    fake_id = str(ObjectId())
    res = client.delete(f"/scans/{fake_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code in [404, 200]

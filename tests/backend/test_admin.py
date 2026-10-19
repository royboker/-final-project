import uuid
from db.mongo import users_collection
from bson import ObjectId
from config import JWT_SECRET, ALGORITHM
from datetime import datetime, timedelta
from jose import jwt


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@pytest.com"


def create_admin_token():
    fake_id = str(ObjectId())
    users_collection.insert_one({
        "_id": ObjectId(fake_id),
        "name": "Admin",
        "email": unique_email(),
        "password": "hashed",
        "role": "admin",
        "is_verified": True,
        "created_at": datetime.utcnow(),
    })
    expire = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"sub": fake_id, "email": "admin@pytest.com", "role": "admin", "exp": expire}, JWT_SECRET, algorithm=ALGORITHM), fake_id


def create_user_token():
    fake_id = str(ObjectId())
    email = unique_email()
    users_collection.insert_one({
        "_id": ObjectId(fake_id),
        "name": "User",
        "email": email,
        "password": "hashed",
        "role": "user",
        "is_verified": True,
        "created_at": datetime.utcnow(),
    })
    expire = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"sub": fake_id, "email": email, "role": "user", "exp": expire}, JWT_SECRET, algorithm=ALGORITHM), fake_id


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_admin_stats_success(client):
    token, admin_id = create_admin_token()
    res = client.get("/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "total_scans" in data
    users_collection.delete_one({"_id": ObjectId(admin_id)})


def test_admin_stats_forbidden_for_user(client):
    token, user_id = create_user_token()
    res = client.get("/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_admin_stats_no_token(client):
    res = client.get("/admin/stats")
    assert res.status_code == 422


# ── Users List ────────────────────────────────────────────────────────────────

def test_admin_get_users(client):
    token, admin_id = create_admin_token()
    res = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "users" in res.json()
    users_collection.delete_one({"_id": ObjectId(admin_id)})


def test_admin_get_users_forbidden(client):
    token, user_id = create_user_token()
    res = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    users_collection.delete_one({"_id": ObjectId(user_id)})


# ── Delete User ───────────────────────────────────────────────────────────────

def test_admin_delete_user(client):
    token, admin_id = create_admin_token()
    _, target_id = create_user_token()
    res = client.delete(f"/admin/users/{target_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    users_collection.delete_one({"_id": ObjectId(admin_id)})


def test_admin_cannot_delete_self(client):
    token, admin_id = create_admin_token()
    res = client.delete(f"/admin/users/{admin_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    users_collection.delete_one({"_id": ObjectId(admin_id)})


def test_admin_delete_nonexistent_user(client):
    token, admin_id = create_admin_token()
    fake_id = str(ObjectId())
    res = client.delete(f"/admin/users/{fake_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
    users_collection.delete_one({"_id": ObjectId(admin_id)})


# ── Change Role ───────────────────────────────────────────────────────────────

def test_admin_change_role(client):
    token, admin_id = create_admin_token()
    _, user_id = create_user_token()
    res = client.patch(f"/admin/users/{user_id}/role", json={"role": "admin"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    users_collection.delete_many({"_id": {"$in": [ObjectId(admin_id), ObjectId(user_id)]}})


def test_admin_change_role_invalid(client):
    token, admin_id = create_admin_token()
    _, user_id = create_user_token()
    res = client.patch(f"/admin/users/{user_id}/role", json={"role": "superuser"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    users_collection.delete_many({"_id": {"$in": [ObjectId(admin_id), ObjectId(user_id)]}})

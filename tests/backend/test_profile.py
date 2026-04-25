import uuid
from db.mongo import users_collection
from bson import ObjectId
from config import JWT_SECRET, ALGORITHM
from datetime import datetime, timedelta
from jose import jwt
from argon2 import PasswordHasher

ph = PasswordHasher()


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@pytest.com"


def create_verified_user(client):
    email = unique_email()
    password = "TestPass123"
    client.post("/auth/register", json={"name": "Test", "email": email, "password": password})
    users_collection.update_one({"email": email}, {"$set": {"is_verified": True}})
    res = client.post("/auth/login", json={"email": email, "password": password})
    return res.json()["token"], email


# ── Get Me ────────────────────────────────────────────────────────────────────

def test_get_me(client):
    token, email = create_verified_user(client)
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == email
    assert "name" in data
    assert "role" in data


def test_get_me_no_token(client):
    res = client.get("/auth/me")
    assert res.status_code == 422


def test_get_me_invalid_token(client):
    res = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401


# ── Change Password ───────────────────────────────────────────────────────────

def test_change_password_success(client):
    token, email = create_verified_user(client)
    res = client.patch("/auth/me/password", json={
        "current_password": "TestPass123",
        "new_password": "NewPass456"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200


def test_change_password_wrong_current(client):
    token, _ = create_verified_user(client)
    res = client.patch("/auth/me/password", json={
        "current_password": "WrongPass999",
        "new_password": "NewPass456"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400


def test_change_password_no_token(client):
    res = client.patch("/auth/me/password", json={
        "current_password": "TestPass123",
        "new_password": "NewPass456"
    })
    assert res.status_code == 422


# ── Delete Account ────────────────────────────────────────────────────────────

def test_delete_account(client):
    token, email = create_verified_user(client)
    res = client.delete("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert users_collection.find_one({"email": email}) is None


def test_delete_account_no_token(client):
    res = client.delete("/auth/me")
    assert res.status_code == 422

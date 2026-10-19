import uuid
from db.mongo import users_collection
from bson import ObjectId
import secrets


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@pytest.com"


# ── Verify Email ──────────────────────────────────────────────────────────────

def test_verify_email_success(client):
    email = unique_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "TestPass123"})
    user = users_collection.find_one({"email": email})
    token = user["verify_token"]

    res = client.get(f"/auth/verify-email?token={token}")
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["email"] == email

    updated = users_collection.find_one({"email": email})
    assert updated["is_verified"] is True


def test_verify_email_invalid_token(client):
    res = client.get("/auth/verify-email?token=invalidtoken123")
    assert res.status_code == 400


def test_login_after_verification(client):
    email = unique_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "TestPass123"})
    user = users_collection.find_one({"email": email})
    client.get(f"/auth/verify-email?token={user['verify_token']}")

    res = client.post("/auth/login", json={"email": email, "password": "TestPass123"})
    assert res.status_code == 200
    assert "token" in res.json()


# ── Reset Password ────────────────────────────────────────────────────────────

def test_reset_password_success(client):
    email = unique_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "TestPass123"})
    users_collection.update_one({"email": email}, {"$set": {"is_verified": True}})

    client.post("/auth/forgot-password", json={"email": email})
    user = users_collection.find_one({"email": email})
    reset_token = user.get("reset_token")
    assert reset_token is not None

    res = client.post("/auth/reset-password", json={"token": reset_token, "password": "NewPass999"})
    assert res.status_code == 200

    login_res = client.post("/auth/login", json={"email": email, "password": "NewPass999"})
    assert login_res.status_code == 200


def test_reset_password_invalid_token(client):
    res = client.post("/auth/reset-password", json={"token": "invalidtoken", "password": "NewPass999"})
    assert res.status_code == 400


def test_reset_password_short_password(client):
    email = unique_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "TestPass123"})
    users_collection.update_one({"email": email}, {"$set": {"is_verified": True}})
    client.post("/auth/forgot-password", json={"email": email})
    user = users_collection.find_one({"email": email})
    reset_token = user.get("reset_token")

    res = client.post("/auth/reset-password", json={"token": reset_token, "password": "123"})
    assert res.status_code in [400, 422]

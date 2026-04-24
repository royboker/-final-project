import pytest
import uuid


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@pytest.com"


# ── Register ──────────────────────────────────────────────────────────────────

def test_register_success(client):
    res = client.post("/auth/register", json={
        "name": "Test User",
        "email": unique_email(),
        "password": "TestPass123"
    })
    assert res.status_code == 201
    assert "user_id" in res.json()


def test_register_duplicate_email(client):
    email = unique_email()
    client.post("/auth/register", json={"name": "A", "email": email, "password": "TestPass123"})
    res = client.post("/auth/register", json={"name": "B", "email": email, "password": "TestPass123"})
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"]


def test_register_short_password(client):
    res = client.post("/auth/register", json={
        "name": "Test",
        "email": unique_email(),
        "password": "123"
    })
    assert res.status_code in [400, 422]


def test_register_missing_fields(client):
    res = client.post("/auth/register", json={"name": "Test"})
    assert res.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_unverified_user(client):
    email = unique_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "TestPass123"})
    res = client.post("/auth/login", json={"email": email, "password": "TestPass123"})
    assert res.status_code == 403
    assert "verify" in res.json()["detail"].lower()


def test_login_wrong_password(client):
    email = unique_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "TestPass123"})
    res = client.post("/auth/login", json={"email": email, "password": "WrongPass999"})
    assert res.status_code == 401


def test_login_nonexistent_user(client):
    res = client.post("/auth/login", json={"email": "nobody@pytest.com", "password": "TestPass123"})
    assert res.status_code == 401


# ── Forgot Password ───────────────────────────────────────────────────────────

def test_forgot_password_existing_email(client):
    email = unique_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "TestPass123"})
    res = client.post("/auth/forgot-password", json={"email": email})
    assert res.status_code == 200


def test_forgot_password_nonexistent_email(client):
    res = client.post("/auth/forgot-password", json={"email": "ghost@pytest.com"})
    assert res.status_code == 200


# ── Health ────────────────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/")
    assert res.status_code == 200

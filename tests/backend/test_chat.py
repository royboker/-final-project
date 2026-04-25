import uuid
from db.mongo import users_collection, db
from bson import ObjectId
from config import JWT_SECRET, ALGORITHM
from datetime import datetime, timedelta
from jose import jwt

sessions_col = db["chat_sessions"]


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


# ── Session ───────────────────────────────────────────────────────────────────

def test_get_session_no_active(client):
    token, user_id = make_token()
    res = client.get("/chat/session", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["session"] is None
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_create_session(client):
    token, user_id = make_token()
    res = client.post("/chat/session", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["session"]["status"] == "active"
    sessions_col.delete_many({"user_id": user_id})
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_create_session_twice_returns_same(client):
    token, user_id = make_token()
    res1 = client.post("/chat/session", headers={"Authorization": f"Bearer {token}"})
    res2 = client.post("/chat/session", headers={"Authorization": f"Bearer {token}"})
    assert res1.json()["session"]["id"] == res2.json()["session"]["id"]
    sessions_col.delete_many({"user_id": user_id})
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_get_session_unauthenticated(client):
    res = client.get("/chat/session")
    assert res.status_code == 422


# ── Messages ──────────────────────────────────────────────────────────────────

def test_get_messages_invalid_session(client):
    token, user_id = make_token()
    fake_id = str(ObjectId())
    res = client.get(f"/chat/messages/{fake_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
    users_collection.delete_one({"_id": ObjectId(user_id)})


# ── Unread ────────────────────────────────────────────────────────────────────

def test_get_unread_no_session(client):
    token, user_id = make_token()
    res = client.get("/chat/unread", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["unread"] == 0
    users_collection.delete_one({"_id": ObjectId(user_id)})


# ── Admin Chat ────────────────────────────────────────────────────────────────

def test_admin_get_sessions(client):
    token, admin_id = make_token(role="admin")
    res = client.get("/chat/sessions", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "sessions" in res.json()
    users_collection.delete_one({"_id": ObjectId(admin_id)})


def test_user_cannot_get_all_sessions(client):
    token, user_id = make_token(role="user")
    res = client.get("/chat/sessions", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    users_collection.delete_one({"_id": ObjectId(user_id)})


def test_chat_history(client):
    token, user_id = make_token()
    res = client.get("/chat/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "sessions" in res.json()
    users_collection.delete_one({"_id": ObjectId(user_id)})

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Header
from datetime import datetime
from typing import Optional
from db.mongo import db, users_collection
from bson import ObjectId
from jose import jwt, JWTError
import os

router = APIRouter(tags=["Chat"])

sessions_col = db["chat_sessions"]
messages_col = db["chat_messages"]

from config import JWT_SECRET, ALGORITHM


# ── Connection Manager ─────────────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.user_connections: dict[str, WebSocket] = {}
        self.admin_connections: list[WebSocket] = []

    async def connect_user(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.user_connections[user_id] = ws

    async def connect_admin(self, ws: WebSocket):
        await ws.accept()
        self.admin_connections.append(ws)

    def disconnect_user(self, user_id: str):
        self.user_connections.pop(user_id, None)

    def disconnect_admin(self, ws: WebSocket):
        if ws in self.admin_connections:
            self.admin_connections.remove(ws)

    async def send_to_user(self, user_id: str, data: dict):
        ws = self.user_connections.get(user_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect_user(user_id)

    async def broadcast_to_admins(self, data: dict):
        disconnected = []
        for ws in self.admin_connections:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect_admin(ws)


manager = ConnectionManager()


# ── Helpers ────────────────────────────────────────────────────────────────────
def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def serialize_session(s: dict) -> dict:
    return {
        "id": str(s["_id"]),
        "user_id": s["user_id"],
        "user_name": s.get("user_name", ""),
        "user_email": s.get("user_email", ""),
        "status": s["status"],
        "created_at": s["created_at"].isoformat() if s.get("created_at") else None,
        "closed_at": s["closed_at"].isoformat() if s.get("closed_at") else None,
        "closed_by": s.get("closed_by"),
        "unread_user": s.get("unread_user", 0),
        "unread_admin": s.get("unread_admin", 0),
        "last_message": s.get("last_message", ""),
    }


def serialize_message(m: dict) -> dict:
    return {
        "id": str(m["_id"]),
        "session_id": m["session_id"],
        "sender_id": m["sender_id"],
        "sender_role": m["sender_role"],
        "content": m["content"],
        "timestamp": m["timestamp"].isoformat() if m.get("timestamp") else None,
    }


# ── REST Endpoints ─────────────────────────────────────────────────────────────

@router.get("/chat/session")
def get_my_session(authorization: str = Header(...)):
    user = get_current_user(authorization)
    session = sessions_col.find_one({"user_id": user["sub"], "status": "active"})
    return {"session": serialize_session(session) if session else None}


@router.post("/chat/session")
def create_session(authorization: str = Header(...)):
    user = get_current_user(authorization)
    user_id = user["sub"]

    existing = sessions_col.find_one({"user_id": user_id, "status": "active"})
    if existing:
        return {"session": serialize_session(existing)}

    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    user_name = user_doc.get("name", "") if user_doc else ""

    session = {
        "user_id": user_id,
        "user_name": user_name,
        "user_email": user.get("email", ""),
        "status": "active",
        "created_at": datetime.utcnow(),
        "closed_at": None,
        "closed_by": None,
        "unread_user": 0,
        "unread_admin": 0,
        "last_message": "",
    }
    result = sessions_col.insert_one(session)
    session["_id"] = result.inserted_id
    return {"session": serialize_session(session)}


@router.post("/chat/close/{session_id}")
async def close_session(session_id: str, authorization: str = Header(...)):
    user = get_current_user(authorization)
    user_id = user["sub"]
    role = user.get("role", "user")

    try:
        session = sessions_col.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if role != "admin" and session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    closed_by = "admin" if role == "admin" else "user"
    sessions_col.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": "closed", "closed_at": datetime.utcnow(), "closed_by": closed_by}},
    )

    notif = {"type": "session_closed", "session_id": session_id, "closed_by": closed_by}
    await manager.send_to_user(session["user_id"], notif)
    await manager.broadcast_to_admins({**notif, "user_id": session["user_id"]})

    return {"ok": True}


@router.get("/chat/messages/{session_id}")
def get_messages(session_id: str, authorization: str = Header(...)):
    user = get_current_user(authorization)
    user_id = user["sub"]
    role = user.get("role", "user")

    try:
        session = sessions_col.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if role != "admin" and session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if role == "admin":
        sessions_col.update_one({"_id": ObjectId(session_id)}, {"$set": {"unread_admin": 0}})
    else:
        sessions_col.update_one({"_id": ObjectId(session_id)}, {"$set": {"unread_user": 0}})

    msgs = list(messages_col.find({"session_id": session_id}).sort("timestamp", 1))
    return {"messages": [serialize_message(m) for m in msgs]}


@router.get("/chat/sessions")
def get_all_sessions(authorization: str = Header(...)):
    user = get_current_user(authorization)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    active = list(sessions_col.find({"status": "active"}).sort("created_at", -1))
    return {"sessions": [serialize_session(s) for s in active]}


@router.get("/chat/history")
def get_my_history(authorization: str = Header(...)):
    user = get_current_user(authorization)
    closed = list(
        sessions_col.find({"user_id": user["sub"], "status": "closed"}).sort("closed_at", -1)
    )
    return {"sessions": [serialize_session(s) for s in closed]}


@router.get("/chat/history/all")
def get_all_history(authorization: str = Header(...)):
    user = get_current_user(authorization)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    closed = list(sessions_col.find({"status": "closed"}).sort("closed_at", -1))
    return {"sessions": [serialize_session(s) for s in closed]}


@router.get("/chat/unread")
def get_unread(authorization: str = Header(...)):
    user = get_current_user(authorization)
    session = sessions_col.find_one({"user_id": user["sub"], "status": "active"})
    if not session:
        return {"unread": 0}
    return {"unread": session.get("unread_user", 0)}


# ── User WebSocket ─────────────────────────────────────────────────────────────
@router.websocket("/ws/user/{token}")
async def user_ws(websocket: WebSocket, token: str):
    user = decode_token(token)
    if not user:
        await websocket.close(code=4001)
        return

    user_id = user["sub"]
    await manager.connect_user(user_id, websocket)

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except Exception:
                break

            msg_type = data.get("type")

            if msg_type == "message":
                session_id = data.get("session_id")
                content = data.get("content", "").strip()
                if not content or not session_id:
                    continue

                msg = {
                    "session_id": session_id,
                    "sender_id": user_id,
                    "sender_role": "user",
                    "content": content,
                    "timestamp": datetime.utcnow(),
                }
                result = messages_col.insert_one(msg)
                msg["_id"] = result.inserted_id

                try:
                    sessions_col.update_one(
                        {"_id": ObjectId(session_id)},
                        {"$inc": {"unread_admin": 1}, "$set": {"last_message": content}},
                    )
                except Exception as e:
                    print(f"❌ Failed to update session unread_admin: {e}")

                serialized = serialize_message(msg)
                await websocket.send_json({"type": "message", "message": serialized})

                session = sessions_col.find_one({"_id": ObjectId(session_id)}) if session_id else None
                user_name = session.get("user_name", "") if session else ""

                await manager.broadcast_to_admins({
                    "type": "message",
                    "message": serialized,
                    "user_id": user_id,
                    "user_name": user_name,
                })

            elif msg_type == "typing":
                session_id = data.get("session_id")
                await manager.broadcast_to_admins({
                    "type": "typing",
                    "user_id": user_id,
                    "session_id": session_id,
                })

            elif msg_type == "read":
                session_id = data.get("session_id")
                if session_id:
                    try:
                        sessions_col.update_one(
                            {"_id": ObjectId(session_id)},
                            {"$set": {"unread_user": 0}},
                        )
                    except Exception as e:
                        print(f"❌ Failed to update session unread_user: {e}")

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect_user(user_id)
        await manager.broadcast_to_admins({"type": "user_offline", "user_id": user_id})


# ── Admin WebSocket ────────────────────────────────────────────────────────────
@router.websocket("/ws/admin/{token}")
async def admin_ws(websocket: WebSocket, token: str):
    user = decode_token(token)
    if not user or user.get("role") != "admin":
        await websocket.close(code=4001)
        return

    admin_id = user["sub"]
    await manager.connect_admin(websocket)

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except Exception:
                break

            msg_type = data.get("type")

            if msg_type == "message":
                session_id = data.get("session_id")
                content = data.get("content", "").strip()
                if not content or not session_id:
                    continue

                try:
                    session = sessions_col.find_one({"_id": ObjectId(session_id)})
                except Exception:
                    continue

                if not session:
                    continue

                msg = {
                    "session_id": session_id,
                    "sender_id": admin_id,
                    "sender_role": "admin",
                    "content": content,
                    "timestamp": datetime.utcnow(),
                }
                result = messages_col.insert_one(msg)
                msg["_id"] = result.inserted_id

                sessions_col.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$inc": {"unread_user": 1}, "$set": {"last_message": content}},
                )

                serialized = serialize_message(msg)

                await manager.send_to_user(session["user_id"], {
                    "type": "message",
                    "message": serialized,
                })
                await manager.broadcast_to_admins({
                    "type": "message",
                    "message": serialized,
                    "user_id": session["user_id"],
                })

            elif msg_type == "typing":
                session_id = data.get("session_id")
                if session_id:
                    try:
                        session = sessions_col.find_one({"_id": ObjectId(session_id)})
                        if session:
                            await manager.send_to_user(session["user_id"], {
                                "type": "typing",
                                "session_id": session_id,
                            })
                    except Exception as e:
                        print(f"❌ Failed to forward typing indicator: {e}")

            elif msg_type == "read":
                session_id = data.get("session_id")
                if session_id:
                    try:
                        sessions_col.update_one(
                            {"_id": ObjectId(session_id)},
                            {"$set": {"unread_admin": 0}},
                        )
                    except Exception as e:
                        print(f"❌ Failed to update session unread_admin to 0: {e}")

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect_admin(websocket)

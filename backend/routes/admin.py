from fastapi import APIRouter, HTTPException, Header
from datetime import datetime, timedelta
from jose import jwt, JWTError
from bson import ObjectId
import os

from db.mongo import users_collection
from db.mongo import db  # נצטרך גם scans

router = APIRouter(prefix="/admin", tags=["Admin"])

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"

# ── Middleware helper ─────────────────────────────────────────────────────────
def require_admin(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── Stats ─────────────────────────────────────────────────────────────────────
@router.get("/stats")
def get_stats(authorization: str = Header(...)):
    require_admin(authorization)

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=6)

    total_users = users_collection.count_documents({})
    new_today = users_collection.count_documents({"created_at": {"$gte": today_start}})
    active_today = users_collection.count_documents({"last_login": {"$gte": today_start}})
    active_week = users_collection.count_documents({"last_login": {"$gte": week_start}})

    try:
        scans_collection = db["scans"]
        total_scans = scans_collection.count_documents({})
        forged_scans = scans_collection.count_documents({"result": "forged"})
    except:
        total_scans = 0
        forged_scans = 0

    # גרף 7 ימים אחרונים
    chart = []
    for i in range(6, -1, -1):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = users_collection.count_documents({
            "last_login": {"$gte": day_start, "$lt": day_end}
        })
        chart.append({
            "date": day_start.strftime("%b %d"),
            "logins": count
        })

    return {
        "total_users": total_users,
        "new_today": new_today,
        "active_today": active_today,
        "active_week": active_week,
        "total_scans": total_scans,
        "forged_scans": forged_scans,
        "chart": chart,
    }

# ── Users list ────────────────────────────────────────────────────────────────
@router.get("/users")
def get_users(authorization: str = Header(...)):
    require_admin(authorization)

    users = list(users_collection.find({}, {
        "_id": 1, "name": 1, "email": 1, "role": 1,
        "is_verified": 1, "created_at": 1, "last_login": 1,
        "google_id": 1,
    }).sort("created_at", -1))

    result = []
    for u in users:
        result.append({
            "id": str(u["_id"]),
            "name": u.get("name", ""),
            "email": u.get("email", ""),
            "role": u.get("role", "user"),
            "is_verified": u.get("is_verified", False),
            "created_at": u.get("created_at", "").isoformat() if u.get("created_at") else None,
            "last_login": u.get("last_login", "").isoformat() if u.get("last_login") else None,
            "auth_method": "google" if u.get("google_id") else "email",
        })

    return {"users": result}

# ── Delete user ───────────────────────────────────────────────────────────────
@router.delete("/users/{user_id}")
def delete_user(user_id: str, authorization: str = Header(...)):
    admin =require_admin(authorization)
    if admin.get("sub") == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    try:
        oid = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = users_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}

# ── Change role ───────────────────────────────────────────────────────────────
@router.patch("/users/{user_id}/role")
def change_role(user_id: str, data: dict, authorization: str = Header(...)):
    admin = require_admin(authorization)
    if admin.get("sub") == user_id:
        raise HTTPException(status_code=400, detail="You cannot change your own role")

    new_role = data.get("role")
    if new_role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")

    try:
        oid = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = users_collection.update_one({"_id": oid}, {"$set": {"role": new_role}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"Role updated to {new_role}"}

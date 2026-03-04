from fastapi import APIRouter, HTTPException, status, Header
from datetime import datetime, timedelta
from jose import jwt, JWTError

from dotenv import load_dotenv
import os

import secrets
from utils.email import send_verification_email, send_reset_email

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

from db.mongo import users_collection
from models.user import UserRegister, UserLogin
from bson import ObjectId

# google
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse

load_dotenv()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

router = APIRouter(prefix="/auth", tags=["Auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24 * 7  # 7 days

ph = PasswordHasher()

def normalize_email(email: str) -> str:
    return email.strip().lower()

# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password too short (min 8 chars)")
    if len(password) > 256:
        raise HTTPException(status_code=400, detail="Password too long (max 256 chars)")
    return ph.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except (VerifyMismatchError, InvalidHash):
        return False

def create_token(user_id: str, email: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": user_id, "email": email, "role": role, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def get_current_user_from_token(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── Register ──────────────────────────────────────────────────────────────────
@router.post("/register", status_code=201)
def register(data: UserRegister):
    email = normalize_email(data.email)

    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    verify_token = secrets.token_urlsafe(32)

    user = {
        "name": data.name.strip(),
        "email": email,
        "password": hash_password(data.password),
        "role": "user",
        "is_verified": False,
        "verify_token": verify_token,
        "created_at": datetime.utcnow(),
    }

    result = users_collection.insert_one(user)
    user_id = str(result.inserted_id)

    send_verification_email(email, verify_token, data.name.strip())

    return {
        "message": "Check your email to verify your account",
        "user_id": user_id,
    }

# ── Google OAuth ──────────────────────────────────────────────────────────────
@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")

    email = normalize_email(user_info["email"])
    existing = users_collection.find_one({"email": email})

    if existing:
        user_id = str(existing["_id"])
        role = existing.get("role", "user")
        name = existing.get("name", user_info.get("name", ""))
    else:
        new_user = {
            "name": user_info.get("name", "").strip(),
            "email": email,
            "password": None,
            "role": "user",
            "google_id": user_info.get("sub"),
            "created_at": datetime.utcnow(),
        }
        result = users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        role = "user"
        name = new_user["name"]

    jwt_token = create_token(user_id, email, role)
    return RedirectResponse(
        url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}&name={name}&email={email}&role={role}&id={user_id}"
    )

# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login")
def login(data: UserLogin):
    email = normalize_email(data.email)
    user = users_collection.find_one({"email": email})

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.get("is_verified", False):
        raise HTTPException(status_code=403, detail="Please verify your email first")

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    user_id = str(user["_id"])
    token = create_token(user_id, user["email"], user.get("role", "user"))

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user_id,
            "name": user.get("name", ""),
            "email": user["email"],
            "role": user.get("role", "user"),
        },
    }

# ── Verify Email ──────────────────────────────────────────────────────────────
@router.get("/verify-email")
def verify_email(token: str):
    user = users_collection.find_one({"verify_token": token})

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"is_verified": True}, "$unset": {"verify_token": ""}}
    )

    user_id = str(user["_id"])
    jwt_token = create_token(user_id, user["email"], user.get("role", "user"))

    return {
        "message": "Email verified successfully",
        "token": jwt_token,
        "user": {
            "id": user_id,
            "name": user.get("name", ""),
            "email": user["email"],
            "role": user.get("role", "user"),
        },
    }

# ── Forgot Password ───────────────────────────────────────────────────────────
@router.post("/forgot-password")
def forgot_password(data: dict):
    email = normalize_email(data.get("email", ""))
    user = users_collection.find_one({"email": email})

    if not user:
        return {"message": "If this email exists, a reset link has been sent"}

    reset_token = secrets.token_urlsafe(32)
    reset_expires = datetime.utcnow() + timedelta(hours=1)

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"reset_token": reset_token, "reset_expires": reset_expires}}
    )

    send_reset_email(email, reset_token, user.get("name", ""))
    return {"message": "If this email exists, a reset link has been sent"}

# ── Reset Password ────────────────────────────────────────────────────────────
@router.post("/reset-password")
def reset_password(data: dict):
    token = data.get("token", "")
    new_password = data.get("password", "")

    user = users_collection.find_one({"reset_token": token})

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if user.get("reset_expires") < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset link has expired")

    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password": hash_password(new_password)},
            "$unset": {"reset_token": "", "reset_expires": ""}
        }
    )

    return {"message": "Password reset successfully"}

# ── Get My Profile ────────────────────────────────────────────────────────────
@router.get("/me")
def get_me(authorization: str = Header(...)):
    user_data = get_current_user_from_token(authorization)
    user = users_collection.find_one({"_id": ObjectId(user_data["sub"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role", "user"),
        "created_at": user.get("created_at"),
        "last_login": user.get("last_login"),
        "auth_method": "google" if user.get("google_id") else "email",
        "is_verified": user.get("is_verified", False),
    }

# ── Change Password ───────────────────────────────────────────────────────────
@router.patch("/me/password")
def change_password(data: dict, authorization: str = Header(...)):
    user_data = get_current_user_from_token(authorization)
    user = users_collection.find_one({"_id": ObjectId(user_data["sub"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("google_id"):
        raise HTTPException(status_code=400, detail="Google accounts cannot change password")
    if not verify_password(data.get("current_password", ""), user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"password": hash_password(data.get("new_password", ""))}}
    )
    return {"message": "Password changed successfully"}

# ── Delete Account ────────────────────────────────────────────────────────────
@router.delete("/me")
def delete_me(authorization: str = Header(...)):
    user_data = get_current_user_from_token(authorization)
    users_collection.delete_one({"_id": ObjectId(user_data["sub"])})
    return {"message": "Account deleted"}

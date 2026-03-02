from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

from db.mongo import users_collection
from models.user import UserRegister, UserLogin

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24 * 7  # 7 days

ph = PasswordHasher()  # Argon2 defaults are OK for most projects

def normalize_email(email: str) -> str:
    return email.strip().lower()

# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    # אין מגבלת 72 כמו bcrypt, אבל עדיין טוב להגביל כדי למנוע abuse
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

# ── Register ──────────────────────────────────────────────────────────────────
@router.post("/register", status_code=201)
def register(data: UserRegister):
    email = normalize_email(data.email)

    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "name": data.name.strip(),
        "email": email,
        "password": hash_password(data.password),
        "role": "user",
        "created_at": datetime.utcnow(),
    }

    result = users_collection.insert_one(user)
    user_id = str(result.inserted_id)
    token = create_token(user_id, email, "user")

    return {
        "message": "Account created successfully",
        "token": token,
        "user": {
            "id": user_id,
            "name": user["name"],
            "email": email,
            "role": "user",
        },
    }

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
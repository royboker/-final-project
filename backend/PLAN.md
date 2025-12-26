# Backend Detailed Implementation Plan

## 1. Project Structure & Environment
We will use **FastAPI** for its speed and automatic documentation, **MongoDB** for flexible data storage, and **Cloudinary** for image management.

### Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config.py            # Environment variables settings
│   ├── database.py          # MongoDB connection logic
│   ├── models/              # Pydantic models (Schemas)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── document.py
│   ├── routers/             # API Endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── documents.py
│   │   └── admin.py
│   ├── services/            # Business Logic
│   │   ├── auth_service.py  # JWT & Hashing
│   │   ├── cloud_service.py # Cloudinary upload
│   │   └── ml_service.py    # PyTorch inference
│   └── utils/
├── requirements.txt
└── .env                     # Secrets (DO NOT COMMIT)
```

---

## 2. Infrastructure Setup Guide (Step-by-Step)

### A. MongoDB Atlas (Database)
1.  **Create Account:** Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign up/login.
2.  **Deploy Cluster:** Create a **FREE** shared cluster (M0 Sandbox).
3.  **Create User:** In "Database Access", create a user (e.g., `admin`) and password. **Save these!**
4.  **Network Access:** In "Network Access", add IP Address `0.0.0.0/0` (Allow access from anywhere for development).
5.  **Get Connection String:**
    *   Click "Connect" -> "Drivers" -> "Python".
    *   Copy the string: `mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority`
    *   Replace `<username>` and `<password>` with your credentials.

### B. Cloudinary (Image Storage)
1.  **Create Account:** Go to [Cloudinary](https://cloudinary.com/) and sign up.
2.  **Dashboard:** On the main dashboard, find your **Product Environment Credentials**:
    *   `Cloud Name`
    *   `API Key`
    *   `API Secret`
3.  These will be put in your `.env` file.

---

## 3. Data Schemas (Pydantic & MongoDB)

We use **Pydantic** to validate data entering our API and **Beanie** (or plain Motor/PyMongo) to structure it for MongoDB.

### User Schema (`app/models/user.py`)
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role: str = "user"  # "user", "admin", "developer"

class UserInDB(UserBase):
    hashed_password: str
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # MongoDB relationship: _id is handled automatically by drivers usually,
    # but in Pydantic we might map it to 'id' for JSON responses.
```

### Document/Analysis Schema (`app/models/document.py`)
```python
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class AnalysisResult(BaseModel):
    prediction: str      # e.g., "Forged", "Authentic"
    confidence: float    # e.g., 0.98
    details: Dict        # Extra model outputs

class DocumentSchema(BaseModel):
    user_id: str         # Reference to User ID
    filename: str
    image_url: Optional[str] = None # Cloudinary URL (only if saved)
    consent: bool        # User allowed saving?
    result: AnalysisResult
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    model_version: str   # e.g., "v1.0-resnet"
```

---

## 4. API Endpoints Specification

### Authentication (`/auth`)
| Method | Path | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| POST | `/auth/register` | Create account | `{"email": "...", "password": "...", "role": "user"}` | `{"msg": "User created", "id": "..."}` |
| POST | `/auth/token` | Login | `OAuth2PasswordRequestForm` (username/password) | `{"access_token": "...", "token_type": "bearer"}` |
| GET | `/auth/me` | Current user info | Header: `Authorization: Bearer ...` | User Profile JSON |

### Document Analysis (`/documents`)
| Method | Path | Description | Params/Body | Logic |
| :--- | :--- | :--- | :--- | :--- |
| POST | `/analyze` | Upload & Analyze | Form-Data: `file` (image), `consent` (true/false) | 1. **Inference**: Run PyTorch model.<br>2. **Cloudinary**: If `consent=True`, upload image.<br>3. **DB**: Save metadata + result.<br>4. **Return**: JSON with prediction. |
| GET | `/history` | User History | Query: `limit`, `skip` | List of user's past analyses. |

### Admin/Developer (`/admin`)
| Method | Path | Description | Permissions |
| :--- | :--- | :--- | :--- |
| GET | `/stats` | System usage stats | Role: `admin` |
| POST | `/models` | Upload new model | Role: `developer` |

---

## 5. Development Roadmap (Zero to Hero)

### Phase 1: Foundation (Day 1)
1.  **Initialize Project:**
    *   Create `backend` folder.
    *   `python -m venv venv` and `source venv/bin/activate`.
    *   Install: `fastapi`, `uvicorn`, `pymongo`, `python-dotenv`.
2.  **Basic Server:**
    *   Create `main.py` with a "Hello World" endpoint.
    *   Run `uvicorn app.main:app --reload`.
3.  **Database Connect:**
    *   Create `app/database.py`.
    *   Use `pymongo.MongoClient` with your Atlas URI.
    *   Verify connection on startup.

### Phase 2: Authentication (Day 2)
1.  **User Model:** Define the Pydantic schema.
2.  **Security Utils:**
    *   Install `passlib[bcrypt]` and `python-jose`.
    *   Create `hash_password` and `verify_password` functions.
    *   Create `create_access_token` function.
3.  **Auth Routes:** Implement Register and Login endpoints.

### Phase 3: The Core - Analysis & Storage (Day 3-4)
1.  **Cloudinary:**
    *   Install `cloudinary`.
    *   Create `app/services/cloud_service.py` with an `upload_image(file)` function.
2.  **ML Placeholder:**
    *   Create `app/services/ml_service.py`.
    *   Initially, make it return a random dummy prediction (e.g., `{"prediction": "Real", "confidence": 0.95}`).
    *   *Later, you will load the real .pth file here.*
3.  **Analyze Endpoint:**
    *   Combine them in `POST /documents/analyze`.
    *   Receive file -> Call ML service -> (If consent) Call Cloudinary -> Save to MongoDB.

### Phase 4: Integration (Day 5)
1.  **Real Model:** Replace the dummy ML service with actual PyTorch code loading your trained model.
2.  **Frontend Connection:** Ensure CORS is enabled in FastAPI so React can talk to it.

---

## 6. Code Snippet: Main Application Entry (`app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, documents, admin
from app.database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="DocAnalysis API")

# Allow frontend to communicate
origins = ["http://localhost:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Analysis API"}
```

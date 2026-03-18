# Backend — Identity Document Fraud Detection

FastAPI server providing REST + WebSocket API for document classification, user management, and real-time chat support.

## Tech Stack

| Tool | Purpose |
|------|---------|
| FastAPI | Async REST API + WebSocket |
| Uvicorn | ASGI server |
| MongoDB (PyMongo) | Database |
| PyTorch + timm | ML model inference |
| Albumentations | Image preprocessing |
| python-jose | JWT authentication |
| Passlib + Argon2 | Password hashing |
| Authlib | Google OAuth 2.0 |
| Brevo API | Transactional email |
| ReportLab | PDF report generation |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app init (alternative entry)
│   ├── config.py         # Settings (JWT, MongoDB, Cloudinary)
│   └── database.py       # MongoDB connection manager
├── db/
│   └── mongo.py          # MongoDB client + collection references
├── models/
│   ├── user.py           # Pydantic schemas: UserRegister, UserLogin, UserResponse
│   └── scan.py           # Pydantic schema: ScanResponse
├── routes/
│   ├── auth.py           # Authentication endpoints
│   ├── scan.py           # Document scanning + ML inference endpoints
│   ├── admin.py          # Admin-only endpoints
│   └── chat.py           # Chat REST + WebSocket endpoints
├── utils/
│   ├── model_loader.py   # ViT + ResNet-18 inference utilities
│   └── email.py          # Email sending via Brevo
├── main.py               # Application entry point
├── config.py             # Top-level config
├── requirements.txt
├── .env.example
└── Dockerfile
```

## API Endpoints

### Auth — `/auth`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create account (sends verification email) |
| POST | `/auth/login` | Email + password login → JWT |
| GET | `/auth/google` | Initiate Google OAuth |
| GET | `/auth/google/callback` | OAuth callback |
| GET | `/auth/verify-email` | Verify email via token |
| POST | `/auth/resend-verification` | Resend verification email |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Set new password via token |
| GET | `/auth/me` | Get current user profile |
| PATCH | `/auth/me/password` | Change password |
| DELETE | `/auth/me` | Delete account |

### Scans — `/scans`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/scans/classify` | Upload image → ML inference (ViT or ResNet-18) |
| POST | `/scans/` | Save a scan result to the database |
| GET | `/scans/my` | Get logged-in user's scan history |
| GET | `/scans/all` | Get all scans (admin only) |
| GET | `/scans/{scan_id}` | Get a single scan |
| POST | `/scans/{scan_id}/report` | Generate PDF report |
| DELETE | `/scans/{scan_id}` | Delete a scan |
| DELETE | `/scans/my/all` | Delete all user's scans |
| GET/PUT | `/scans/settings/model` | Get / set default model (admin) |

### Admin — `/admin`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/stats` | Dashboard stats (user count, scan count, activity chart) |
| GET | `/admin/users` | List all users |
| DELETE | `/admin/users/{user_id}` | Delete a user |
| PATCH | `/admin/users/{user_id}/role` | Change user role |

### Chat — `/chat` + WebSocket

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/chat/session` | Get or create chat session |
| POST | `/chat/close/{session_id}` | Close a session |
| GET | `/chat/messages/{session_id}` | Get messages for a session |
| GET | `/chat/sessions` | All active sessions (admin) |
| GET | `/chat/history` | User's closed sessions |
| GET | `/chat/history/all` | All closed sessions (admin) |
| POST | `/chat/admin/send` | Admin sends a message |
| GET | `/chat/unread` | Unread message count |
| WS | `/ws/user/{token}` | User WebSocket connection |
| WS | `/ws/admin/{token}` | Admin WebSocket connection |

## ML Models

Two document classifiers are served:

| Model | File | Input |
|-------|------|-------|
| ViT-Tiny | `models/vit_document_classifier.pth` | 224×224 RGB |
| ResNet-18 | `models/resnet18_document_classifier.pth` | 224×224 RGB |

**Output classes:** `0 = ID Card`, `1 = Passport`, `2 = Driver License`

Image preprocessing uses albumentations with ImageNet normalization (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).

## Database

MongoDB with four collections:

| Collection | Contents |
|-----------|---------|
| `users` | Accounts, hashed passwords, roles, OAuth IDs, verification status |
| `scans` | Scan records with model used, predicted class, confidence scores, image |
| `chat_sessions` | Session metadata, unread counts |
| `chat_messages` | Individual chat messages with sender role and timestamp |
| `settings` | App-wide settings (e.g., default model) |

## Getting Started

### Prerequisites

- Python 3.10+
- MongoDB running locally or a MongoDB Atlas connection string
- Trained model `.pth` files in `../models/`

### Install and Run

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then fill in all values
uvicorn main:app --reload         # starts on http://localhost:8000
```

### Environment Variables

Copy `.env.example` to `.env`:

```env
MONGODB_URI=mongodb://localhost:27017
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Brevo (email)
BREVO_API_KEY=
FROM_EMAIL=no-reply@yourdomain.com

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:5173

# Cloudinary (optional, for image storage)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

### Interactive API Docs

Once the server is running, open:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Docker

```bash
docker build -t fraud-detection-backend .
docker run -p 8000:8000 --env-file .env fraud-detection-backend
```

## Authentication Flow

1. User registers → verification email sent via Brevo
2. User clicks link → email verified → can now log in
3. Login returns a JWT (7-day expiry) stored in frontend `localStorage`
4. All protected endpoints require `Authorization: Bearer <token>` header
5. Admin-only routes check `user.role == "admin"` extracted from the JWT

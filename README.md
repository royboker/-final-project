# DocuGuard — Identity Document Fraud Detection

An end-to-end AI platform for detecting forged identity documents. Combines a 3-stage deep learning pipeline with a full-stack web application.

---

## Pipeline Overview

Document verification runs in three sequential stages:

```
Image Input
    │
    ▼
Stage 1 — Document Type Classification
    ViT-Tiny or ResNet18
    → ID Card / Passport / Driver License
    │
    ▼
Stage 2 — Forgery Detection
    ViT-Small or DiT-Base  (model specific to detected doc type)
    → Real → done
    → Fake → continue
    │
    ▼
Stage 3 — Fraud Type Classification
    ViT-Small or DiT-Base  (only runs if Stage 2 = Fake)
    → Morphing / Replacement
    │
    ▼
Verdict: "Real" / "Fake - Morphing" / "Fake - Replacement"
```

**Morphing** — two faces blended into one image (both people can pass with the same document).  
**Replacement** — photo or data field swapped on a genuine document.

---

## Models

14 trained `.pth` checkpoints stored in `models/final_models/`:

| Role | Architecture | File |
|------|-------------|------|
| Document type classifier | ViT-Tiny | `vit_document_classifier_9k.pth` |
| Document type classifier | ResNet18 | `resnet18_document_classifier_9k.pth` |
| Passport forgery (binary) | ViT-Small | `vit_passport_binary_20k.pth` |
| Passport fraud type | ViT-Small | `vit_passport_fraud_type_20k.pth` |
| ID Card forgery (binary) | ViT-Small | `vit_id_card_binary_20k.pth` |
| ID Card fraud type | ViT-Small | `vit_id_card_fraud_type_20k.pth` |
| Driver License forgery (binary) | ViT-Small | `vit_drivers_license_binary_15k.pth` |
| Driver License fraud type | ViT-Small | `vit_drivers_license_fraud_type_15k.pth` |
| Passport forgery (binary) | DiT-Base | `dit_passport_binary_20k.pth` |
| Passport fraud type | DiT-Base | `dit_passport_fraud_type_20k.pth` |
| ID Card forgery (binary) | DiT-Base | `dit_id_card_binary_20k.pth` |
| ID Card fraud type | DiT-Base | `dit_id_card_fraud_type_20k.pth` |
| Driver License forgery (binary) | DiT-Base | `dit_drivers_license_binary_15k.pth` |
| Driver License fraud type | DiT-Base | `dit_drivers_license_fraud_type_15k.pth` |

The number suffix (9k / 20k / 15k) reflects training set size. Stage 2 and 3 use **Test-Time Augmentation** (4 views averaged) for more stable predictions.

Admins can switch the active architecture per pipeline slot (ViT ↔ DiT) from the dashboard without redeployment.

---

## Dataset

**IDNet** — ~130GB, 290,000+ images  
Source: [Kaggle - IDNet Identity Document Analysis](https://www.kaggle.com/datasets/chitreshkr/idnet-identity-document-analysis)

- 9 countries: Albania, Greece, Russia, Latvia, Slovakia, Nevada, Washington DC, Arizona, West Virginia
- Document types: Passports, ID Cards, Driver Licenses
- Labels: Real / Fake, fraud type per image
- Not tracked in git — see `SETUP.md` for download instructions

---

## Tech Stack

**ML**
- PyTorch + timm (ViT models), torchvision (ResNet)
- Albumentations (transforms + TTA)
- Training in Jupyter notebooks (`notebooks/document_type_classification/`)

**Backend** — `backend/`
- FastAPI + uvicorn
- MongoDB (Atlas) via pymongo
- JWT authentication (argon2 password hashing)
- Cloudinary for image storage
- PDF report generation with ReportLab
- Google OAuth

**Frontend** — `frontend/`
- React 18 + Vite
- React Router, Recharts
- Real-time chat (user ↔ admin)
- Dark/light theme

**Tests** — `tests/`
- `tests/backend/` — pytest + FastAPI TestClient (57 tests)
- `tests/e2e/` — Playwright (27 tests, Chromium)

---

## Project Structure

```
final-project/
├── notebooks/                  # Training experiments
│   └── document_type_classification/
│       ├── resnet18/           # Stage 1 ResNet18 training
│       ├── vit/                # Stage 1 ViT-Tiny training
│       └── dit/                # Stage 2+3 DiT-Base training
├── models/
│   └── final_models/           # 14 trained .pth checkpoints
├── demo/
│   └── model_loader.py         # Model classes + inference functions
├── src/
│   └── data/                   # Dataset preparation scripts
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── routes/                 # auth, scan, admin, chat
│   ├── utils/                  # model_loader, email
│   ├── db/                     # MongoDB collections
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/              # Login, Register, Dashboard, Scan, Admin
│   │   ├── components/         # Navbar, ChatWidget, ScanDemo
│   │   └── context/            # Auth, Chat, Theme
│   └── package.json
├── tests/
│   ├── backend/                # pytest test suite
│   └── e2e/                    # Playwright E2E tests
├── datasets/                   # gitignored — download separately
├── SETUP.md
├── DEPLOYMENT.md
└── TECH_STACK.md
```

---

## Running Locally

**Backend**
```bash
cd backend
# Windows
..\venv\Scripts\Activate.ps1
# macOS/Linux
source ../venv/bin/activate

uvicorn main:app --port 8000 --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

**Backend tests**
```bash
cd tests/backend
pytest -v
```

**E2E tests** (requires backend running on 8000)
```bash
cd tests/e2e
npx playwright test --project=chromium
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login |
| GET | `/auth/me` | Current user profile |
| POST | `/scans/classify` | Classify doc type (single model) |
| POST | `/scans/analyze` | Full 3-stage pipeline |
| GET | `/scans/my` | User scan history |
| GET | `/scans/{id}/report` | Download PDF report |
| GET | `/admin/stats` | Platform statistics (admin) |
| GET | `/admin/users` | User management (admin) |
| GET/PUT | `/scans/settings/pipeline-models` | Active model config (admin) |

---

## Environment Variables

Create `backend/.env` (see `backend/env.example`):

```
MONGODB_URI=
JWT_SECRET=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173
```

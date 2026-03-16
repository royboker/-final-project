# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Identity Document Fraud Detection platform using PyTorch deep learning models. Classifies identity documents (passports, ID cards, driver's licenses) and detects forgeries across multiple countries using the IDNet dataset (~130GB+, 290k+ images).

**Current state:** Phase 1 (Document Type Classification) is complete with trained models. Backend (FastAPI) and frontend (React) are scaffolded but mostly unimplemented. See `backend/PLAN.md` and `frontend/PLAN.md` for implementation roadmaps.

## Common Commands

```bash
# Python environment
source venv/bin/activate
pip install -r requirements.txt

# Jupyter notebooks (primary experimentation workflow)
jupyter lab

# Streamlit demo (document classification with trained models)
streamlit run demo/app.py

# Dataset preparation
python src/data/create_document_type_dataset.py
python src/data/create_unified_grc_dataset.py
python src/data/create_unified_rus_dataset.py
python src/data/create_unified_wv_dataset.py

# Backend (FastAPI)
cd backend && uvicorn app.main:app --reload

# Frontend (React + Vite)
cd frontend && npm install && npm run dev
npm run build    # production build
npm run lint     # ESLint
```

## Architecture

### ML Pipeline (`src/`, `notebooks/`, `models/`, `demo/`)
- **`src/models/cnn_models.py`** — Model architectures: `BaselineCNN`, `ResNetDocumentClassifier`, `EfficientNetDocumentClassifier`. All use 224x224 input, 3-class output (passport, id_card, driver_license).
- **`demo/model_loader.py`** — Inference-time model definitions (`ViTTinyClassifier`, `ResNet18Classifier`) with loading utilities and prediction functions. Uses `timm` for ViT and `albumentations` for transforms.
- **`notebooks/document_type_classification/`** — Training experiments organized by model (`resnet18/`, `vit/`, `dit/`). Naming: `{model}_{task}_{samples}.ipynb`. Training happens in notebooks, not scripts.
- **`models/`** — Saved `.pth` checkpoints (ResNet18, ViT, multi-task ViT). Gitignored but present locally.
- **`src/data/`** — Dataset creation and processing scripts. Each `create_unified_*.py` handles a country. `create_document_type_dataset.py` builds the combined classification dataset.

### Backend (`backend/`)
- FastAPI app in `backend/app/main.py` with CORS for localhost:5173 and localhost:3000
- MongoDB via `backend/app/database.py`, Cloudinary for image storage
- Config from `.env` (see `backend/env.example` for required vars: MongoDB URI, JWT secret, Cloudinary credentials)
- Planned: JWT auth, document analysis endpoints, ML inference service (see `backend/PLAN.md`)

### Frontend (`frontend/`)
- React 18 + Vite + React Router + Material-UI + Axios + Recharts
- Currently just routing skeleton (Home, Login, Dashboard placeholders)
- Planned: file upload with react-dropzone, analysis results display (see `frontend/PLAN.md`)

### Data Flow
Raw images in `datasets/idnet/{country}/` → processing scripts in `src/data/` → CSV metadata + organized splits in `datasets/idnet/document_type_classification_country_split/` → notebook training → `.pth` models in `models/` → inference via `demo/model_loader.py`

## Key Conventions

- **ML framework:** PyTorch with transfer learning (ImageNet pretrained). `timm` library for ViT models.
- **Image preprocessing:** Albumentations for augmentation/transforms. ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]).
- **3 document classes:** `{0: "ID Card", 1: "Passport", 2: "Driver License"}`
- **Dataset files are large** (~130GB+) and gitignored. CSV metadata files are kept in git.
- **Git workflow:** `develop` branch for work, `main` for PRs.
- **Backend dependencies** are in `backend/requirements.txt` (separate from root `requirements.txt`).
- **Frontend dependencies** managed via npm in `frontend/package.json`.

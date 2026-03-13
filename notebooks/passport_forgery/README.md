# Passport Forgery Detection

This folder contains the training notebooks, models, and evaluation scripts for a **2-phase forgery detection pipeline** on passport documents from 3 countries (ALB, GRC, LVA).

## Pipeline

```
Image → Phase 1: Real or Fake?
              ├── Real → Done
              └── Fake → Phase 2: What type of fraud?
                           ├── Face Morphing
                           └── Face Replacement
```

Both phases use **ViT-Small** (384-dim) with:
- Focal Loss (gamma=2.0) for hard example mining
- 3-stage gradual unfreezing (head → last 4 blocks → full backbone)
- Test-Time Augmentation (4 views averaged at inference)
- Light augmentation during training to preserve forgery artifacts

## Folder Structure

### `production/` — Final Models (20,000 images)

The production pipeline trained on **20,000 images** — 10,000 real and 10,000 fake passports from 3 countries (ALB, GRC, LVA), with ~3,333 subjects per country.

| File | Description |
|------|-------------|
| `vit_binary_improved_20k.ipynb` | Phase 1 training — Real vs Fake classification |
| `vit_binary_improved_20k.pth` | Phase 1 saved model weights (83 MB) |
| `vit_fraud_type_20k.ipynb` | Phase 2 training — Face Morphing vs Face Replacement |
| `vit_fraud_type_20k.pth` | Phase 2 saved model weights (83 MB) |
| `evaluate_outsource.py` | Standalone out-of-dataset evaluation for Phase 1 |
| `evaluate_fraud_type.py` | Standalone out-of-dataset evaluation for Phase 2 |
| `prepare_splits.py` | Creates train/val/test splits with GroupShuffleSplit |
| `data/` | Train (16K), val (2K), test (2K) CSV split files |

### `experiments/` — Out-of-Dataset Evaluation Samples

| File | Description |
|------|-------------|
| `test_samples.json` | 2,997 out-of-dataset samples (999 subjects × 3 images each) used for evaluation |

## Dataset

Images come from the IDNet dataset with 3 countries:
- **ALB** (Albania), **GRC** (Greece), **LVA** (Latvia)
- Each subject has a real photo + morphed version + replaced version
- The 20K dataset is stored at `datasets/passport_20k/` and was created by `src/data/create_passport_20k_dataset.py`

### Data Splits & Integrity

The data is split into train (80%), validation (10%), and test (10%) using `GroupShuffleSplit` on the `original_id` field. This ensures that all images of the same subject stay in the same split — no subject appears in more than one split.

| Split | Images | Real | Fake | Balance |
|-------|--------|------|------|---------|
| Train | 16,000 | 8,000 | 8,000 | 50/50 |
| Val | 2,000 | 1,000 | 1,000 | 50/50 |
| Test | 2,000 | 1,000 | 1,000 | 50/50 |

**Verified properties:**
- **No data leakage** — zero subject overlap between train, val, and test splits
- **No duplicates** — each image appears exactly once across all splits
- **Perfectly balanced** — 50/50 real/fake in every split, equal country distribution (ALB/GRC/LVA)
- **Subject pairing** — every subject has exactly 1 real image and 1 fake image
- **Out-of-dataset separation** — the 2,997 evaluation samples (`test_samples.json`) are fully excluded from the 20K training dataset

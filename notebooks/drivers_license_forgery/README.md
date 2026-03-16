# Driver's License Forgery Detection

This folder contains the training notebooks, models, and evaluation scripts for a **2-phase forgery detection pipeline** on driver's license documents from 3 US states (WV, DC, AZ).

## Pipeline

```
Image → Phase 1: Real or Fake? (93.5% accuracy)
              ├── Real → Done
              └── Fake → Phase 2: What type of fraud? (95.6% accuracy)
                           ├── Face Morphing
                           └── Face Replacement
```

Both phases use **ViT-Small** (384-dim) with:
- Focal Loss (gamma=2.0) for hard example mining
- 3-stage gradual unfreezing (head → last 4 blocks → full backbone)
- Test-Time Augmentation (4 views averaged at inference)
- Light augmentation during training to preserve forgery artifacts

## Folder Structure

### `production/` — Final Models (15,000 images)

The production pipeline trained on **15,000 images** — 7,500 real and 7,500 fake driver's licenses from 3 US states (WV, DC, AZ), with 2,500 subjects per state.

| File | Description |
|------|-------------|
| `vit_binary_improved_15k.ipynb` | Phase 1 training — Real vs Fake classification |
| `vit_binary_improved_15k.pth` | Phase 1 saved model weights (83 MB) |
| `vit_fraud_type_15k.ipynb` | Phase 2 training — Face Morphing vs Face Replacement |
| `vit_fraud_type_15k.pth` | Phase 2 saved model weights (83 MB) |
| `evaluate_outsource.py` | Standalone out-of-dataset evaluation for Phase 1 |
| `evaluate_fraud_type.py` | Standalone out-of-dataset evaluation for Phase 2 |
| `prepare_splits.py` | Creates train/val/test splits with GroupShuffleSplit |
| `data/` | Train (12K), val (1.5K), test (1.5K) CSV split files |

**Results:**

| Model | In-Dataset (TTA) | Out-of-Dataset (999 samples) |
|-------|-------------------|------------------------------|
| Phase 1 — Real/Fake | 93.47% | 92.79% |
| Phase 2 — Fraud Type | 95.60% | 97.15% |

### `experiments/` — Initial Experiments (9,996 images)

Early training runs on a smaller dataset used to iterate on model architecture, loss functions, and augmentation strategies. These notebooks document the progression from 74.8% (multi-task baseline) to 92.1% (improved binary model), which informed the final production setup.

This folder also contains `test_samples.json` — 999 out-of-dataset samples used for evaluation across all experiments.

## Dataset

Images come from the IDNet dataset with 3 US states:
- **WV** (West Virginia), **DC** (Washington DC), **AZ** (Arizona)
- Each subject has a real photo + morphed version + replaced version
- The 15K dataset is stored at `datasets/drivers_license_15k/` and was created by `src/data/create_15k_dataset.py`

### Data Splits & Integrity

The data is split into train (80%), validation (10%), and test (10%) using `GroupShuffleSplit` on the `original_id` field. This ensures that all images of the same subject stay in the same split — no subject appears in more than one split.

| Split | Images | Real | Fake | Balance |
|-------|--------|------|------|---------|
| Train | 12,000 | 6,000 | 6,000 | 50/50 |
| Val | 1,500 | 750 | 750 | 50/50 |
| Test | 1,500 | 750 | 750 | 50/50 |

**Verified properties:**
- **No data leakage** — zero subject overlap between train, val, and test splits
- **No duplicates** — each image appears exactly once across all splits
- **Perfectly balanced** — 50/50 real/fake in every split, equal country distribution (WV/DC/AZ)
- **Subject pairing** — every subject has exactly 1 real image and 1 fake image
- **Out-of-dataset separation** — the 999 evaluation samples (`test_samples.json`) are fully excluded from the 15K training dataset, ensuring the out-of-dataset evaluation is on truly unseen data


# ResNet18 Baseline Experiments

## Overview
This directory contains baseline experiments for document type classification using ResNet18. The experiments test the model's performance with different dataset sizes to understand the relationship between data volume and model accuracy.

## Task
**Document Type Classification**: Classify images into 3 categories:
- `id_card` (label: 0)
- `passport` (label: 1)
- `driver_license` (label: 2)

## Model Architecture
- **Base Model**: ResNet18 (pre-trained on ImageNet)
- **Final Layer**: Dropout (0.3) + Linear layer (512 → 3 classes)
- **Total Parameters**: ~11.2M

## Experiments


### 2. `resnet18_baseline_1000.ipynb`
- **Dataset Size**: 1000 images (333 per class)
- **Split**: Train: 721 | Val: 128 | Test: 150
- **Configuration**:
  - Batch size: 32
  - Learning rate: 1e-6
  - Epochs: 25
  - Optimizer: Adam (weight decay: 1e-4)

### 3. `resnet18_baseline_2000.ipynb`
- **Dataset Size**: 2000 images (666 per class)
- **Split**: Train: 1443 | Val: 255 | Test: 300
- **Configuration**:
  - Batch size: 64
  - Learning rate: 5e-7
  - Epochs: 30
  - Optimizer: Adam (weight decay: 1e-4)

### 4. `resnet18_baseline_3600.ipynb`
- **Dataset Size**: 3600 images (1200 per class)
- **Split**: Train: 2601 | Val: 459 | Test: 540
- **Configuration**:
  - Batch size: 128
  - Learning rate: 1e-7
  - Epochs: 35
  - Optimizer: Adam (weight decay: 1e-4)

### 5. `resnet18_baseline_5400.ipynb` (Full Dataset)
- **Dataset Size**: 5400 images (1800 per class) - **Complete dataset**
- **Split**: Train: 3901 | Val: 689 | Test: 810
- **Configuration**:
  - Batch size: 128
  - Learning rate: 1e-7
  - Epochs: 40
  - Optimizer: Adam (weight decay: 1e-4)

## Data Augmentation
All experiments use the same augmentation strategy:
- **Training**: Random crop, horizontal flip (p=0.3), rotation (±15°), color jitter, random affine, random erasing (p=0.3)
- **Validation/Test**: Resize to 256, center crop to 224, normalization only

## Data Split Strategy
- Stratified sampling to maintain class balance
- Split ratio: 85% train → 15% test, then 85% train → 15% val
- Random state: 42 (for reproducibility)

## Observations
- As dataset size increases, learning rate decreases (from 1e-5 to 1e-7)
- Batch size increases with dataset size (32 → 64 → 128)
- Number of epochs increases for larger datasets (25 → 30 → 35 → 40)
- All experiments use the same dropout rate (0.3) and weight decay (1e-4)


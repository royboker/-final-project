# ResNet18 Baseline Experiments

## Overview
This directory contains baseline experiments for document type classification using ResNet18. The experiments test the model's performance with different dataset sizes to understand the relationship between data volume and model accuracy.

## Task
**Document Type Classification**: Classify images into 3 categories:
- `id_card` (label: 0)
- `passport` (label: 1)
- `driver_license` (label: 2)

## Model Architecture
- **Base Model**: ResNet18 (trained from scratch - no pre-training)
- **Final Layer**: Dropout (0.3) + Linear layer (512 → 3 classes)
- **Total Parameters**: ~11.2M

## Experiments

### 1. `resnet18_baseline_1000.ipynb`
- **Dataset Size**: 1000 images (333 per class)
- **Split**: Train: 699 | Val: 150 | Test: 150
- **Configuration**:
  - Batch size: 32
  - Learning rate: 1e-4 (0.0001)
  - Epochs: 20
  - Optimizer: Adam (weight decay: 1e-4)
  - Dropout: 0.3
  - Pre-trained: No (from scratch)
  - Early Stopping: Yes (patience: 5, min_delta: 0.001)

### 2. `resnet18_baseline_2000.ipynb`
- **Dataset Size**: 2000 images (666 per class)
- **Split**: Train: 1399 | Val: 299 | Test: 300
- **Configuration**:
  - Batch size: 64
  - Learning rate: 5e-5 (0.00005)
  - Epochs: 25
  - Optimizer: Adam (weight decay: 1e-4)
  - Dropout: 0.3
  - Pre-trained: No (from scratch)
  - Early Stopping: Yes (patience: 5, min_delta: 0.001)

### 3. `resnet18_baseline_3600.ipynb`
- **Dataset Size**: 3600 images (1200 per class)
- **Split**: Train: 2521 | Val: 539 | Test: 540
- **Configuration**:
  - Batch size: 64
  - Learning rate: 2e-5 (0.00002)
  - Epochs: 30
  - Optimizer: Adam (weight decay: 1e-4)
  - Dropout: 0.3
  - Pre-trained: No (from scratch)
  - Early Stopping: Yes (patience: 5, min_delta: 0.001)

### 4. `resnet18_baseline_5400.ipynb`
- **Dataset Size**: 5400 images (1800 per class)
- **Split**: Train: 3782 | Val: 808 | Test: 810
- **Configuration**:
  - Batch size: 128
  - Learning rate: 0.00001
  - Epochs: 30
  - Optimizer: Adam (weight decay: 1e-4)
  - Dropout: 0.3
  - Pre-trained: No (from scratch)
  - Early Stopping: Yes (patience: 5, min_delta: 0.001)

### 5. `resnet18_baseline_9000.ipynb`
- **Dataset Size**: 9000 images (3000 per class)
- **Split**: Train: 6303 | Val: 1347 | Test: 1350
- **Configuration**:
  - Batch size: 128
  - Learning rate: 1.2e-6 (0.0000012)
  - Epochs: 35 (maximum, with early stopping)
  - Optimizer: Adam (weight decay: 1e-4)
  - Dropout: 0.3
  - Pre-trained: No (from scratch)
  - Early Stopping: Yes (patience: 5, min_delta: 0.001)
  - Learning Rate Scheduler: ReduceLROnPlateau (factor=0.5, patience=3, min_lr=1e-8)
  - Gradient Clipping: Yes (max_norm=1.0)

## Data Augmentation
All experiments use the same augmentation strategy:
- **Training**: 
  - Resize to 256
  - Random crop to 224
  - Random rotation (±15°)
  - Gaussian blur (kernel_size=(5,9), sigma=(0.1,5))
  - Color jitter (brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1)
  - Random grayscale (p=0.5)
  - Random affine (translate=(0.1,0.1), scale=(0.9,1.1))
  - Random erasing (p=0.3)
  - Normalization (ImageNet stats)
- **Validation/Test**: 
  - Resize to 256
  - Center crop to 224
  - Normalization (ImageNet stats)

## Data Split Strategy
- GroupShuffleSplit to prevent data leakage (based on source_file or image_path)
- Split ratio: 85% train → 15% test, then ~85% train → ~15% val
- Random state: 42 (for reproducibility)

## Training Features
- **Early Stopping**: Implemented in all experiments (patience: 5 epochs)
- **Learning Rate Scheduler**: ReduceLROnPlateau (only in 9000 experiment)
- **Gradient Clipping**: max_norm=1.0 (only in 9000 experiment)
- **Best Model Saving**: Automatically saves best model based on validation accuracy

## Observations
- Learning rate decreases as dataset size increases (1e-4 → 5e-5 → 2e-5 → 7e-6 → 1.2e-6)
- Batch size increases with dataset size (32 → 64 → 128)
- Number of epochs increases for larger datasets (20 → 25 → 30 → 35)
- All experiments use the same dropout rate (0.3) and weight decay (1e-4)
- All models are trained from scratch (no ImageNet pre-training)
- All experiments use Early Stopping (patience: 5 epochs, min_delta: 0.001)
- Larger datasets (9000) benefit from additional training features:
  - Learning Rate Scheduler: ReduceLROnPlateau (reduces LR when validation loss plateaus)
  - Gradient Clipping: Prevents exploding gradients (max_norm=1.0)

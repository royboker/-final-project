# ViT-Tiny Baseline Experiment

## Overview
This directory contains baseline experiment for document type classification using Vision Transformer (ViT-Tiny). The experiment tests the model's performance on a dataset of 9000 images with aggressive augmentations and robust training techniques.

## Task
**Document Type Classification**: Classify images into 3 categories:
- `id_card` (label: 0)
- `passport` (label: 1)
- `driver_license` (label: 2)

## Model Architecture
- **Base Model**: ViT-Tiny (Vision Transformer, trained from scratch - no pre-training)
- **Embedding Dimension**: 192
- **Patch Size**: 16x16
- **Final Layer**: Dropout (0.2) + Linear layer (192 → 3 classes)
- **Total Parameters**: ~5.5M

## Experiment: `vit_baseline_9000.ipynb`

### Dataset
- **Dataset Size**: 9000 images (3000 per class, balanced)
- **Split**: 
  - Train: 6303 images
  - Validation: 1347 images
  - Test: 1350 images
- **Split Strategy**: Stratified sampling to maintain class balance

### Training Configuration
- **Batch Size**: 128
- **Learning Rate**: 8e-5 (0.00008)
- **Weight Decay**: 0.05
- **Dropout**: 0.2
- **Epochs**: 15 (maximum, with early stopping)
- **Optimizer**: AdamW
- **Pre-trained**: Yes
- **Early Stopping**: Yes (patience: 5 epochs)
- **Learning Rate Scheduler**: ReduceLROnPlateau (factor=0.5, patience=4, min_lr=1e-6)
- **Gradient Clipping**: Yes (max_norm=1.0)
- **Label Smoothing**: 0.05
- **Mixup**: Disabled (too hard with frozen backbone)

### Training Strategy
- Head Only Training (Backbone Frozen)
  - Only the classifier head is trained
  - ViT backbone remains frozen throughout training
  - This limits maximum achievable accuracy but provides realistic performance

### Data Augmentation (Aggressive - Albumentations)
**Training Augmentations:**
- **Resize**: 224x224
- **ShiftScaleRotate**: shift_limit=0.1, scale_limit=0.2, rotate_limit=30° (50% probability)
- **Perspective**: scale=(0.05, 0.1) (50% probability) - simulates non-straight camera angles
- **GaussianBlur**: blur_limit=(3, 7) (30% probability) - simulates poor focus
- **GaussNoise**: var_limit=(10.0, 50.0) (30% probability) - simulates poor lighting
- **ColorJitter**: brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1 (30% probability)
- **CoarseDropout**: max_holes=8, max_height=32, max_width=32, min_holes=2 (50% probability)
  - **CRITICAL**: Forces model to not rely on single regions, simulates occlusion
- **Normalization**: ImageNet stats (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

**Validation/Test Augmentations:**
- **Resize**: 224x224
- **Normalization**: ImageNet stats

**Why Aggressive Augmentations?**
- Prevents model from learning superficial features (like "blue rectangle = ID card")
- Forces model to learn deeper, more robust features
- Simulates real-world conditions (poor lighting, blur, occlusion, perspective distortion)

### Data Split Strategy
- Stratified sampling to maintain class balance across splits
- Random state: 42 (for reproducibility)
- **Data Leakage Check**: Subject-based split verification implemented to prevent model from "cheating" by recognizing individuals

### Training Features
- **Early Stopping**: Implemented (patience: 5 epochs)
- **Learning Rate Scheduler**: ReduceLROnPlateau (reduces LR when validation loss plateaus)
- **Gradient Clipping**: max_norm=1.0 (prevents exploding gradients)
- **Best Model Saving**: Automatically saves best model based on validation accuracy
- **Label Smoothing**: 0.05 (reduces overfitting)
- **Mixup**: Disabled (too difficult with frozen backbone)

### Robust Training Techniques
- ✅ **Aggressive Albumentations**: Perspective, Blur, Noise, CoarseDropout
  - Simulates real-world conditions (poor lighting, blur, occlusion)
  - Forces model to learn deep features, not superficial patterns
- ✅ **Data Leakage Check**: Subject-based split verification
  - Prevents model from "cheating" by recognizing individuals
- ✅ **Grad-CAM Visualization**: Explainability
  - Visualizes where model focuses (document features vs. background)
  - Proves model learned meaningful features

### Key Observations
- Model trained
- **Frozen backbone** throughout training (only classifier head trained)
- **Aggressive augmentations** used to prevent overfitting and achieve realistic accuracy
- **Lower dropout** (0.2) and **label smoothing** (0.05) to help frozen backbone learn
- **Higher learning rate** (8e-5) compared to ResNet18 experiments for better convergence
- **Single-stage training** (Stage A only) - no fine-tuning of backbone

### Model Files
- **Model Weights**: `vit_document_classifier_9000.pth`
- **Label Map**: `vit_label_map.pkl`



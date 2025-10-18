# 🎯 Document Type Classification

## 📋 Overview

This directory contains all data and resources for the **Document Type Classification** task - a computer vision model that classifies identity documents into three categories:

- 🛂 **Passport** (דרכון)
- 🪪 **ID Card** (תעודת זהות)
- 🚗 **Driver's License** (רישיון נהיגה)

## 🎯 Goal

Train a model that can **generalize across countries** - identifying document types based on their visual structure and layout, not country-specific features.

### Key Challenge
The model should work on documents from **any country**, even those not seen during training!

## 📁 Directory Structure

```
document_type_classification/
├── data/
│   ├── full_dataset.csv      # Complete dataset (2,100 images)
│   ├── train_dataset.csv     # Training set (1,470 images - 70%)
│   ├── val_dataset.csv       # Validation set (315 images - 15%)
│   └── test_dataset.csv      # Test set (315 images - 15%)
├── models/                    # (to be created) Trained models
├── results/                   # (to be created) Training results
└── README.md                  # This file
```

## 📊 Dataset Statistics

### Full Dataset
- **Total Images**: 2,100
- **Classes**: 3 (balanced)
- **Source Countries**: 
  - 🇬🇷 Greece (Passports)
  - 🇷🇺 Russia (ID Cards)
  - 🇺🇸 USA - West Virginia (Driver's Licenses)

### Data Split (Stratified)

| Split | Total | Passports | ID Cards | Driver Licenses | Percentage |
|-------|-------|-----------|----------|-----------------|------------|
| **Train** | 1,470 | 490 | 490 | 490 | 70% |
| **Validation** | 315 | 105 | 105 | 105 | 15% |
| **Test** | 315 | 105 | 105 | 105 | 15% |

### Key Properties
- ✅ **Balanced Classes**: Each class has exactly 33.3% representation
- ✅ **Stratified Split**: Class distribution maintained across all splits
- ✅ **No Data Leakage**: Zero overlap between train/val/test sets
- ✅ **Reproducible**: Fixed random seed (42) for consistent splits

## 🎯 Model Requirements

### Input
- **Format**: RGB images of identity documents
- **Size**: Variable (will be resized during preprocessing)
- **Source**: Real document images from IDNet dataset

### Output
- **Classes**: 3 categories
  - `passport` (0)
  - `id_card` (1)
  - `driver_license` (2)
- **Format**: Probability distribution over classes

### Success Criteria
- **Primary**: High accuracy on test set
- **Secondary**: Good generalization to unseen countries
- **Tertiary**: Balanced performance across all classes

## 🔧 Data Loading

### Python Example
```python
import pandas as pd

# Load datasets
train_df = pd.read_csv('data/train_dataset.csv')
val_df = pd.read_csv('data/val_dataset.csv')
test_df = pd.read_csv('data/test_dataset.csv')

# Check structure
print(f"Train: {len(train_df)} images")
print(f"Validation: {len(val_df)} images")
print(f"Test: {len(test_df)} images")

# View class distribution
print(train_df['document_type'].value_counts())
```

## 🧠 Model Architecture Recommendations

### Option 1: Transfer Learning (Recommended)
```python
Base Model: ResNet50 / EfficientNet-B0
Pre-trained: ImageNet
Fine-tuning: Last layers + custom classifier
Expected Accuracy: 90-95%
```

### Option 2: Custom CNN
```python
Architecture: Custom convolutional layers
Training: From scratch
Expected Accuracy: 80-90%
```

### Option 3: Vision Transformer
```python
Base Model: ViT-Base
Pre-trained: ImageNet-21k
Expected Accuracy: 92-97%
```

## 📈 Training Strategy

### 1. Data Augmentation
```python
- Rotation: ±15 degrees
- Horizontal Flip: 50%
- Brightness: ±20%
- Contrast: ±20%
- Zoom: 90-110%
- Crop: Random crops
```

### 2. Training Parameters
```python
- Optimizer: Adam
- Learning Rate: 0.001 (with decay)
- Batch Size: 32
- Epochs: 50-100
- Early Stopping: Patience 10
```

### 3. Evaluation Metrics
- **Accuracy**: Overall correctness
- **Precision/Recall/F1**: Per-class performance
- **Confusion Matrix**: Detailed error analysis
- **Cross-Country Performance**: Test on new countries

## 🎯 Expected Challenges

1. **Visual Similarity**: ID cards and driver's licenses can look similar
2. **Size Variation**: Documents have different aspect ratios
3. **Text Language**: Different scripts (Latin, Cyrillic, Greek)
4. **Color Schemes**: Varying color palettes across countries
5. **Security Features**: Different hologram and watermark patterns

## 🔍 What the Model Should Learn

### Passports
- International standard format (125mm × 88mm)
- Multiple languages (at least English)
- Large photo
- Country emblem at top
- Longer validity period

### ID Cards
- Credit card size
- Compact layout
- Dense information
- Often bilingual
- Barcode/QR code common

### Driver's Licenses
- Credit card size
- Vehicle-related information
- License categories (A, B, C, etc.)
- Smaller photo
- Shorter validity period

## 📝 Next Steps

1. **Create Training Notebook**: `notebooks/04_document_type_classification.ipynb`
2. **Build Model**: Implement architecture
3. **Train**: Run training with augmentation
4. **Evaluate**: Test on validation set
5. **Fine-tune**: Adjust hyperparameters
6. **Final Test**: Evaluate on test set
7. **Cross-Country Test**: Test on new countries (if available)

## 🚀 Usage

### Training
```bash
# Run training script (to be created)
python src/training/train_document_classifier.py
```

### Inference
```python
# Load trained model
model = load_model('models/document_classifier_v1.h5')

# Predict document type
image = load_image('path/to/document.jpg')
prediction = model.predict(image)
document_type = ['passport', 'id_card', 'driver_license'][prediction.argmax()]
```

## 📚 References

- **Dataset Source**: IDNet - Identity Document Analysis
- **Countries**: Greece (GRC), Russia (RUS), USA (WV)
- **Task Type**: Multi-class image classification
- **Domain**: Computer Vision, Document Analysis

---

**Created**: October 14, 2024  
**Status**: Data prepared, ready for model training  
**Next**: Build and train classification model


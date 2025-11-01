# 📓 Document Type Classification - Notebooks

This directory contains all Jupyter notebooks for the **Document Type Classification** project.

## 📋 Notebooks Overview

### Completed Notebooks ✅

1. **01_data_exploration_and_visualization.ipynb** ✅
   - Load and explore the dataset
   - Visualize sample images from each class
   - Analyze class distribution
   - Check image dimensions and properties
   - Verify data quality

2. **02_data_preprocessing_and_augmentation.ipynb** ✅
   - Load train/validation/test datasets
   - Define preprocessing pipeline with normalization (ImageNet stats)
   - Implement data augmentations (Rotation, ColorJitter, Affine, Sharpness)
   - Create custom Dataset class with error handling
   - Configure DataLoaders (notebook-optimized)
   - Visualize augmented samples
   - Compute dataset statistics
   - Save configuration files for training
   - **Features:**
     - ImageNet normalization for pretrained model compatibility
     - Multiple augmentation techniques (no horizontal flip - not suitable for documents)
     - Robust error handling (3 retries for corrupted images)
     - Comprehensive statistics for research documentation
     - Configuration saved to JSON files

### Planned Notebooks 📝

3. **03_model_training.ipynb** (To be created)
   - Load preprocessing configuration
   - Build models (Baseline CNN, ResNet18/50, EfficientNet-B0)
   - Train models on training set
   - Monitor training with validation metrics
   - Save model checkpoints
   - Compare model performance

4. **04_model_evaluation.ipynb** (To be created)
   - Load best model
   - Evaluate on test set
   - Generate confusion matrix
   - Analyze errors
   - Visualize predictions
   - Performance metrics across classes

## 🎯 Goals

- **Primary**: Achieve >90% accuracy on test set
- **Secondary**: Balanced performance across all 3 classes
- **Tertiary**: Model generalizes to unseen countries

## 📊 Dataset Location

All notebooks load data from:
```python
DATA_DIR = '../../datasets/idnet/document_type_classification/data/'
TRAIN_CSV = DATA_DIR + 'train_dataset.csv'
VAL_CSV = DATA_DIR + 'val_dataset.csv'
TEST_CSV = DATA_DIR + 'test_dataset.csv'
```

**Dataset Statistics:**
- **Train**: 1,470 samples (490 per class - balanced)
- **Validation**: 315 samples (105 per class - balanced)
- **Test**: 315 samples (105 per class - balanced)
- **Total**: 2,100 images
- **Classes**: 3 (driver_license, id_card, passport)

## 🚀 Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Start Jupyter
jupyter notebook

# Navigate to this directory and open a notebook
```

## 📝 Notebook Template Structure

Each notebook should follow this structure:

1. **Setup**
   - Imports
   - Configuration
   - Set random seeds

2. **Data Loading**
   - Load CSV files
   - Verify data integrity
   - Display samples

3. **Preprocessing**
   - Image loading
   - Resizing
   - Normalization
   - Augmentation (if applicable)

4. **Model Building**
   - Define architecture
   - Compile model
   - Display summary

5. **Training**
   - Train model
   - Monitor metrics
   - Save checkpoints

6. **Evaluation**
   - Evaluate on validation/test set
   - Generate metrics
   - Visualize results

7. **Analysis**
   - Error analysis
   - Confusion matrix
   - Sample predictions

## 🔧 Common Imports (PyTorch)

```python
# Data handling
import pandas as pd
import numpy as np
from pathlib import Path
import json
import time

# Image processing
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Deep Learning - PyTorch
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import models

# Models (from src)
import sys
sys.path.append('../../src')
from models.cnn_models import create_model, get_model_info

# Metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
```

## 📈 Expected Results

| Model | Parameters | Accuracy (Expected) | Training Time |
|-------|------------|---------------------|---------------|
| Baseline CNN | ~51.6M | 80-85% | 1-2 hours |
| ResNet18 | ~11.3M | 90-93% | 2-3 hours |
| EfficientNet-B0 | ~4.3M | 92-95% | 2-4 hours |
| ResNet50 | ~24M | 93-96% | 3-5 hours |

## 🎯 Classes

- **0**: driver_license (רישיון נהיגה)
- **1**: id_card (תעודת זהות)
- **2**: passport (דרכון)

**Class Mapping** (saved in `models/class_mapping.json`):
```json
{
  "driver_license": 0,
  "id_card": 1,
  "passport": 2
}
```

## ⚙️ Preprocessing Configuration

The preprocessing pipeline is configured in `02_data_preprocessing_and_augmentation.ipynb` and saved to:
- **Configuration**: `models/preprocessing_config.json`
- **Class Mapping**: `models/class_mapping.json`

**Key Settings:**
- **Image Size**: 224×224 pixels
- **Normalization**: ImageNet standard (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- **Augmentations**: 
  - RandomRotation (10°)
  - ColorJitter (brightness, contrast, saturation, hue)
  - RandomAffine (translation)
  - RandomAdjustSharpness
  - ⚠️ **No HorizontalFlip** (not suitable for documents with text)
- **Batch Size**: 32
- **Error Handling**: 3 retries for corrupted images

## 📚 Resources

- **Dataset README**: `../../datasets/idnet/document_type_classification/README.md`
- **Main Project README**: `../../README.md`
- **Model Documentation**: `../../src/models/cnn_models.py`
- **Preprocessing Config**: `../../models/preprocessing_config.json`
- **Class Mapping**: `../../models/class_mapping.json`

## 📦 Available Models

All models are defined in `src/models/cnn_models.py`:

```python
from models.cnn_models import create_model

# Create any model
model = create_model('baseline', num_classes=3, pretrained=False)
model = create_model('resnet18', num_classes=3, pretrained=True)
model = create_model('resnet50', num_classes=3, pretrained=True)
model = create_model('efficientnet', num_classes=3, pretrained=True)
```

All models are compatible with the preprocessing pipeline (224×224, ImageNet normalization).

## 🚨 Important Notes

1. **Notebook vs Script**: DataLoaders use `num_workers=0` for notebooks (multiprocessing limitations). In training scripts, you can use `num_workers=2-4`.

2. **MPS/CUDA**: `pin_memory` is automatically disabled for MPS devices (Mac) and only enabled for CUDA.

3. **Augmentation**: Horizontal flip is intentionally excluded as it reverses text, which is not suitable for document classification.

4. **Dataset Balance**: The dataset is perfectly balanced (33.3% per class in all splits).

---

**Status**: ✅ Data exploration and preprocessing completed  
**Next Step**: Create `03_model_training.ipynb` for model training


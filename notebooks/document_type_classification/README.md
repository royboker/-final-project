# 📓 Document Type Classification - Notebooks

This directory contains all Jupyter notebooks for the **Document Type Classification** project.

## 📋 Notebooks Overview

### Planned Notebooks

1. **01_data_exploration.ipynb** (To be created)
   - Load and explore the dataset
   - Visualize sample images from each class
   - Analyze class distribution
   - Check image dimensions and properties
   - Verify data quality

2. **02_baseline_model.ipynb** (To be created)
   - Build a simple CNN baseline
   - Train on training set
   - Evaluate on validation set
   - Establish baseline performance

3. **03_transfer_learning.ipynb** (To be created)
   - Use pre-trained models (ResNet50/EfficientNet)
   - Fine-tune on our dataset
   - Compare with baseline
   - Optimize hyperparameters

4. **04_data_augmentation.ipynb** (To be created)
   - Implement augmentation strategies
   - Test different augmentation techniques
   - Measure impact on performance

5. **05_final_evaluation.ipynb** (To be created)
   - Load best model
   - Evaluate on test set
   - Generate confusion matrix
   - Analyze errors
   - Visualize predictions

## 🎯 Goals

- **Primary**: Achieve >90% accuracy on test set
- **Secondary**: Balanced performance across all 3 classes
- **Tertiary**: Model generalizes to unseen countries

## 📊 Dataset Location

All notebooks should load data from:
```python
DATA_DIR = '../../datasets/idnet/document_type_classification/data/'
TRAIN_CSV = DATA_DIR + 'train_dataset.csv'
VAL_CSV = DATA_DIR + 'val_dataset.csv'
TEST_CSV = DATA_DIR + 'test_dataset.csv'
```

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

## 🔧 Common Imports

```python
# Data handling
import pandas as pd
import numpy as np
from pathlib import Path

# Image processing
from PIL import Image
import cv2

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Deep Learning
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# or PyTorch
import torch
import torchvision

# Metrics
from sklearn.metrics import classification_report, confusion_matrix
```

## 📈 Expected Results

| Model | Accuracy | F1-Score | Training Time |
|-------|----------|----------|---------------|
| Baseline CNN | 80-85% | 0.80-0.85 | 1-2 hours |
| ResNet50 | 90-95% | 0.90-0.95 | 2-4 hours |
| EfficientNet | 92-97% | 0.92-0.97 | 3-5 hours |

## 🎯 Classes

- **0**: passport (דרכון)
- **1**: id_card (תעודת זהות)
- **2**: driver_license (רישיון נהיגה)

## 📚 Resources

- **Dataset README**: `../../datasets/idnet/document_type_classification/README.md`
- **Main Project README**: `../../README.md`
- **Model Documentation**: `../../models/README.md`

---

**Status**: Ready for notebook creation  
**Next Step**: Create `01_data_exploration.ipynb`


# 💻 Source Code Directory

This directory contains all source code for the Identity Document Fraud Detection project.

## 📁 Directory Structure

```
src/
├── data/                 # Data processing and loading
│   ├── create_unified_*.py              # Country-specific dataset creation
│   ├── create_document_type_dataset.py  # Document type dataset
│   ├── prepare_idnet_full_dataset.py    # Full IDNet preparation
│   ├── fix_dataset_splits.py            # Fix train/val/test splits
│   ├── split_dataset.py                 # Dataset splitting utilities
│   ├── load_idnet_dataset.py            # Dataset loading utilities
│   └── explore_idnet.py                 # Data exploration tools
│
├── models/               # Model architectures
│   └── cnn_models.py     # CNN models (ResNet, EfficientNet, etc.)
│
├── training/             # Training scripts and utilities
│   └── __init__.py
│
├── utils/                # Utility functions
│   └── __init__.py
│
└── README.md            # This file
```

## 📂 Module Descriptions

### 1. `data/` - Data Processing

Contains scripts for dataset creation, processing, and loading.

#### Dataset Creation Scripts
- **`create_unified_grc_dataset.py`**: Create unified Greek passport dataset
- **`create_unified_rus_dataset.py`**: Create unified Russian ID card dataset
- **`create_unified_wv_dataset.py`**: Create unified West Virginia driver's license dataset
- **`create_unified_idnet_dataset.py`**: Create unified dataset from all countries
- **`create_document_type_dataset.py`**: Create document type classification dataset

**Usage**:
```bash
python src/data/create_unified_grc_dataset.py
python src/data/create_document_type_dataset.py
```

#### Data Preparation Scripts
- **`prepare_idnet_full_dataset.py`**: Prepare full IDNet dataset with multiple countries
  - Loads data from all available countries
  - Creates mixed dataset for document type classification
  - Splits into train/val/test without data leakage

**Usage**:
```bash
python src/data/prepare_idnet_full_dataset.py --idnet_path datasets/idnet --output_dir datasets/idnet/document_type_classification/data
```

#### Utility Scripts
- **`fix_dataset_splits.py`**: Fix train/val/test splits to prevent data leakage
- **`split_dataset.py`**: Dataset splitting utilities with stratification
- **`load_idnet_dataset.py`**: Dataset loading utilities and data loaders
- **`explore_idnet.py`**: Data exploration and statistics tools
- **`create_dataset_csv.py`**: General CSV dataset creation utilities
- **`create_fcdp_csv.py`**: Specialized dataset creation utilities

---

### 2. `models/` - Model Architectures

Contains neural network architectures for document classification.

#### `cnn_models.py`
Implements various CNN architectures:

**Classes**:
- **`BaselineCNN`**: Simple CNN built from scratch
  - 3 convolutional blocks
  - 2 fully connected layers
  - Dropout for regularization

- **`ResNetDocumentClassifier`**: ResNet with transfer learning
  - Supports ResNet18, ResNet34, ResNet50
  - Pre-trained on ImageNet
  - Customizable final layer

- **`EfficientNetDocumentClassifier`**: EfficientNet with transfer learning
  - Supports EfficientNet-B0 through B7
  - State-of-the-art efficiency
  - Optimized for accuracy vs computational cost

**Usage**:
```python
from src.models.cnn_models import ResNetDocumentClassifier

# Create ResNet18 model for 3 document types
model = ResNetDocumentClassifier(
    num_classes=3,
    pretrained=True,
    model_name='resnet18'
)
```

**Available Models**:
- `BaselineCNN`: Custom lightweight CNN
- `ResNetDocumentClassifier`: ResNet18, ResNet34, ResNet50
- `EfficientNetDocumentClassifier`: EfficientNet-B0 to B7

---

### 3. `training/` - Training Scripts

Contains training loops, optimization, and experiment management.

**Current Status**: Directory structure is set up, training scripts to be added.

**Planned Components**:
- Training loops with validation
- Learning rate scheduling
- Early stopping
- Checkpoint management
- Experiment tracking

---

### 4. `utils/` - Utility Functions

Contains helper functions used across the project.

**Current Status**: Directory structure is set up, utilities to be added.

**Planned Components**:
- Visualization utilities
- Metrics calculation
- Configuration management
- File I/O helpers

---

## 🚀 Getting Started

### 1. Prepare Datasets
```bash
# Create unified datasets for each country
python src/data/create_unified_grc_dataset.py
python src/data/create_unified_rus_dataset.py
python src/data/create_unified_wv_dataset.py

# Create document type classification dataset
python src/data/create_document_type_dataset.py --samples_per_class 1000
```

### 2. Explore Data
```python
from src.data.explore_idnet import explore_dataset

# Explore dataset statistics
explore_dataset('datasets/idnet/GRC_Unified_Dataset.csv')
```

### 3. Load Model
```python
from src.models.cnn_models import ResNetDocumentClassifier

# Create model
model = ResNetDocumentClassifier(num_classes=3, pretrained=True)

# Train on your data
# (See notebooks for training examples)
```

---

## 📋 Code Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular

### Documentation
- Add module-level docstrings explaining purpose
- Document function parameters and return values
- Include usage examples for complex functions

### Error Handling
- Use meaningful error messages
- Validate inputs
- Handle edge cases gracefully

---

## 🔧 Development Workflow

### Adding New Dataset Scripts
1. Create new script in `src/data/`
2. Follow naming convention: `create_*.py` or `process_*.py`
3. Add docstrings and usage examples
4. Test with sample data
5. Update this README

### Adding New Models
1. Add model class to `src/models/cnn_models.py` or create new file
2. Inherit from `nn.Module` (PyTorch) or `Model` (Keras/TensorFlow)
3. Add docstring with architecture description
4. Include example usage in docstring
5. Test model forward pass
6. Update this README

### Adding Training Scripts
1. Create training script in `src/training/`
2. Include:
   - Data loading
   - Model initialization
   - Training loop
   - Validation
   - Checkpoint saving
   - Logging
3. Make it configurable (argparse or config file)
4. Test with small dataset first
5. Update this README

---

## 🛠️ Dependencies

Key libraries used:
- **PyTorch**: Deep learning framework
- **torchvision**: Pre-trained models and transforms
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **Pillow**: Image processing
- **scikit-learn**: Data splitting and metrics

See `requirements.txt` for complete list.

---

## 📚 Additional Resources

### PyTorch
- [PyTorch Documentation](https://pytorch.org/docs/)
- [torchvision Models](https://pytorch.org/vision/stable/models.html)

### Data Processing
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [PIL/Pillow Documentation](https://pillow.readthedocs.io/)

### Model Architectures
- [ResNet Paper](https://arxiv.org/abs/1512.03385)
- [EfficientNet Paper](https://arxiv.org/abs/1905.11946)
- [Vision Transformer Paper](https://arxiv.org/abs/2010.11929)

---

## 🤝 Contributing

When adding new code:
1. Follow existing code structure
2. Add comprehensive docstrings
3. Test your code
4. Update relevant README files
5. Consider adding example usage in notebooks

---

**Happy Coding! 🚀**


# 📓 Document Type Classification Notebooks

This directory contains Jupyter notebooks for document type classification experiments and analysis.

## 🎯 Task Overview

**Goal**: Classify identity documents into 3 types:
- 🛂 **Passports** (e.g., Greece, Latvia)
- 🪪 **ID Cards** (e.g., Russia, Slovakia)
- 🚗 **Driver's Licenses** (e.g., West Virginia, Arizona)

## 📁 Directory Structure

```
document_type_classification/
├── README.md                    # This file
├── dataset_overview.ipynb       # Dataset analysis and visualization
├── template.ipynb               # Template for new experiments
│
├── resnet18/                    # ResNet18 experiments
│   ├── resnet18_baseline_500.ipynb    # 500 samples per class
│   ├── resnet18_baseline_1000.ipynb   # 1000 samples per class
│   ├── resnet18_baseline_2000.ipynb   # 2000 samples per class
│   ├── resnet18_baseline_3600.ipynb   # 3600 samples per class
│   ├── train.csv              # Training set
│   ├── val.csv                # Validation set
│   ├── test.csv               # Test set
│   └── images/                # Plots and visualizations
│
└── vit/                         # Vision Transformer experiments
    ├── vit_baseline_500.ipynb   # 500 samples per class
    ├── train.csv              # Training set
    ├── val.csv                # Validation set
    ├── test.csv               # Test set
    └── images/                # Plots and visualizations
```

## 📊 Notebooks Description

### 1. dataset_overview.ipynb
**Purpose**: Comprehensive dataset analysis and visualization
- Dataset statistics (class distribution, image counts)
- Sample image visualization from each document type
- Image dimension analysis
- Data quality checks
- Dataset imbalance analysis

**Use this to**: Understand the dataset before training models

---

### 2. template.ipynb
**Purpose**: Template for creating new experiments
- Standard structure for new experiments
- Best practices and code organization
- Data loading utilities
- Training loop structure
- Evaluation metrics

**Use this to**: Start a new experiment with consistent structure

---

### 3. ResNet18 Experiments (`resnet18/`)

#### resnet18_baseline_500.ipynb
- **Dataset Size**: 500 samples per class (1,500 total)
- **Architecture**: ResNet18 with transfer learning
- **Purpose**: Quick baseline with small dataset

#### resnet18_baseline_1000.ipynb
- **Dataset Size**: 1,000 samples per class (3,000 total)
- **Architecture**: ResNet18 with transfer learning
- **Purpose**: Baseline with medium dataset

#### resnet18_baseline_2000.ipynb
- **Dataset Size**: 2,000 samples per class (6,000 total)
- **Architecture**: ResNet18 with transfer learning
- **Purpose**: Baseline with larger dataset

#### resnet18_baseline_3600.ipynb
- **Dataset Size**: 3,600 samples per class (10,800 total)
- **Architecture**: ResNet18 with transfer learning
- **Purpose**: Full dataset baseline (maximum available samples)

**Key Features**:
- Transfer learning from ImageNet
- Data augmentation (rotation, flip, color jitter)
- Learning rate scheduling
- Early stopping
- Model checkpointing

---

### 4. Vision Transformer Experiments (`vit/`)

#### vit_baseline_500.ipynb
- **Dataset Size**: 500 samples per class (1,500 total)
- **Architecture**: Vision Transformer (ViT)
- **Purpose**: Baseline with transformer architecture

**Key Features**:
- Transformer-based architecture
- Patch-based image processing
- Self-attention mechanisms
- Comparison with CNN approaches

---

## 🚀 Getting Started

### 1. Start with Dataset Overview
```bash
jupyter lab dataset_overview.ipynb
```
- Understand the dataset
- View sample images
- Check class distribution

### 2. Run a Baseline Experiment
```bash
# Start with small dataset for quick iteration
jupyter lab resnet18/resnet18_baseline_500.ipynb
```

### 3. Scale Up
- Try larger datasets as needed
- Compare different architectures
- Tune hyperparameters

### 4. Create New Experiments
```bash
# Use template for new experiments
jupyter lab template.ipynb
```

## 📈 Typical Training Results

### ResNet18 Baselines
- **500 samples/class**: ~85-90% validation accuracy
- **1000 samples/class**: ~90-93% validation accuracy
- **2000 samples/class**: ~92-95% validation accuracy
- **3600 samples/class**: ~93-96% validation accuracy

### Training Time (Apple M1/M2)
- **500 samples**: ~5-10 minutes
- **1000 samples**: ~10-15 minutes
- **2000 samples**: ~15-25 minutes
- **3600 samples**: ~25-40 minutes

## 🔧 Common Hyperparameters

### ResNet18
- **Learning Rate**: 0.001 - 0.0001
- **Batch Size**: 32 - 64
- **Epochs**: 20 - 50
- **Optimizer**: Adam or SGD with momentum
- **Scheduler**: ReduceLROnPlateau or CosineAnnealing

### Data Augmentation
- **Rotation**: ±15 degrees
- **Horizontal Flip**: 50% probability
- **Color Jitter**: brightness, contrast, saturation
- **Normalization**: ImageNet mean/std

## 📊 Evaluation Metrics

All notebooks track:
- **Accuracy**: Overall classification accuracy
- **Precision**: Per-class precision
- **Recall**: Per-class recall
- **F1-Score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Detailed error analysis
- **Training/Validation Loss**: Loss curves over epochs

## 🎨 Visualization

Each notebook includes:
- Sample images from each class
- Training/validation loss curves
- Training/validation accuracy curves
- Confusion matrix
- Per-class performance metrics
- Misclassified samples analysis

## 💡 Best Practices

1. **Start Small**: Begin with small dataset (500 samples) for quick iteration
2. **Use Template**: Use `template.ipynb` for consistent experiment structure
3. **Track Everything**: Log all hyperparameters and results
4. **Save Checkpoints**: Save best model and regular checkpoints
5. **Visualize Results**: Always plot loss/accuracy curves and confusion matrix
6. **Document Experiments**: Add markdown cells explaining your approach
7. **Compare Models**: Use consistent train/val/test splits for fair comparison

## 🔬 Experiment Ideas

- [ ] Compare ResNet18 vs ResNet50 vs EfficientNet
- [ ] Test different data augmentation strategies
- [ ] Experiment with learning rate schedules
- [ ] Try ensemble methods
- [ ] Add attention mechanisms
- [ ] Test on cross-country generalization
- [ ] Fine-tune on specific document types
- [ ] Implement mixup or cutmix augmentation

## 📚 Resources

### Model Architectures
- [ResNet Paper](https://arxiv.org/abs/1512.03385)
- [Vision Transformer Paper](https://arxiv.org/abs/2010.11929)
- [EfficientNet Paper](https://arxiv.org/abs/1905.11946)

### PyTorch Resources
- [PyTorch Documentation](https://pytorch.org/docs/)
- [torchvision Models](https://pytorch.org/vision/stable/models.html)
- [Transfer Learning Tutorial](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)

## 🤝 Contributing

When adding new notebooks:
1. Use the `template.ipynb` as starting point
2. Follow naming convention: `{model}_{variant}_{samples}.ipynb`
3. Document hyperparameters clearly
4. Include visualizations
5. Save results in `images/` subdirectory
6. Update this README with your experiment

## 📝 Notes

- **Dataset**: Using `datasets/idnet/document_type_classification_country_split/`
- **Models**: Saved to `models/checkpoints/`
- **Results**: Plots saved in respective `images/` folders
- **Train/Val/Test CSVs**: Each experiment directory contains its data splits
- **GPU Recommended**: Training is faster with GPU (CUDA or MPS)

---

**Happy Experimenting! 🚀**


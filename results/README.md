# 📊 Results Directory

This directory stores all experimental results, visualizations, and training logs.

## 📁 Directory Structure

```
results/
├── figures/               # Plots and visualizations
│   ├── dataset_statistics.png
│   ├── image_dimensions_distribution.png
│   ├── real_vs_fake_comparison.png
│   └── sample_images_all_categories.png
│
├── logs/                  # Training logs and metrics
│   └── (training log files)
│
└── README.md             # This file
```

## 📈 Figures Directory

The `figures/` directory contains visualizations from:
- **Dataset Analysis**: Statistics, distributions, sample images
- **Training Progress**: Loss curves, accuracy plots
- **Model Evaluation**: Confusion matrices, ROC curves
- **Results Comparison**: Model comparison charts

### Current Figures
- `dataset_statistics.png` - Dataset size and class distribution statistics
- `image_dimensions_distribution.png` - Distribution of image dimensions
- `real_vs_fake_comparison.png` - Comparison between real and fake documents
- `sample_images_all_categories.png` - Sample images from all document categories

## 📝 Logs Directory

The `logs/` directory stores:
- **Training Logs**: Training progress, loss, metrics per epoch
- **Validation Logs**: Validation performance during training
- **Experiment Logs**: Detailed experiment configurations and results
- **Error Logs**: Any errors or warnings during training

## 💡 Usage

### Saving Figures
```python
import matplotlib.pyplot as plt

# Save figure
plt.savefig('results/figures/my_plot.png', dpi=300, bbox_inches='tight')
```

### Saving Logs
```python
import logging

# Setup logging
logging.basicConfig(
    filename='results/logs/training.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log training progress
logging.info(f'Epoch {epoch}: Loss={loss:.4f}, Acc={acc:.4f}')
```

## 📦 File Formats

- **Images**: PNG, JPG (prefer PNG for plots)
- **Logs**: TXT, LOG, CSV
- **Metrics**: CSV, JSON
- **Plots**: PNG (300 DPI recommended)

## 🗂️ Organization Best Practices

1. **Use Descriptive Names**: `resnet18_confusion_matrix_epoch50.png`
2. **Date Stamps**: `training_log_2024-11-21.log`
3. **Experiment IDs**: Group results by experiment ID or model name
4. **Subdirectories**: Create subdirectories for large experiments

Example structure:
```
results/
├── figures/
│   ├── experiment_001/
│   │   ├── loss_curve.png
│   │   ├── confusion_matrix.png
│   │   └── accuracy_plot.png
│   └── experiment_002/
│       └── ...
└── logs/
    ├── experiment_001_training.log
    └── experiment_002_training.log
```

## 🔍 What to Save

### During Training
- Loss curves (training and validation)
- Accuracy curves (training and validation)
- Learning rate schedules
- Sample predictions

### After Training
- Confusion matrix
- Per-class metrics
- ROC curves (for binary classification)
- Sample predictions with confidence scores
- Misclassified examples analysis

### Dataset Analysis
- Class distribution
- Image dimension statistics
- Sample images
- Data quality visualizations

## ⚠️ Important Notes

- Large log files (>100MB) should be compressed or archived
- Keep results organized by experiment for easy comparison
- Consider using experiment tracking tools (MLflow, Weights & Biases)
- Backup important results before major changes

---

**Note**: This directory is typically excluded from git (via .gitignore) to save space. Only commit key visualizations and summary results.


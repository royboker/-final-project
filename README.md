# 🛂 Identity Document Fraud Detection - Final Project

## 🎯 Project Overview

This project focuses on **Identity Document Fraud Detection** using machine learning and deep learning techniques. The goal is to develop models that can accurately identify forged identity documents across different types (passports, ID cards, driver's licenses) and fraud techniques.

## 📊 Datasets

### IDNet Dataset
- **Source**: [Kaggle - IDNet Identity Document Analysis](https://www.kaggle.com/datasets/chitreshkr/idnet-identity-document-analysis)
- **Size**: ~49GB (125,556 images total)
- **Countries**: 3 (Greece, Russia, USA)
- **Document Types**: Passports, ID Cards, Driver's Licenses
- **Fraud Types**: 6 different fraud techniques
- **Location**: `datasets/idnet/`

### Key Features
- **Real vs Fake**: Balanced dataset with authentic and forged documents
- **Multi-Country**: Documents from different countries and languages
- **Rich Metadata**: Personal information and detailed fraud annotations
- **Unified Format**: Processed into CSV files for easy model training

## 🏗️ Project Structure

```
final-project/
│
├── datasets/              # All datasets and processed data
│   ├── idnet/            # IDNet dataset (raw + processed)
│   │   ├── GRC/          # Greek passports
│   │   ├── RUS/          # Russian ID cards  
│   │   ├── WV/           # American driver's licenses
│   │   └── README.md     # IDNet dataset documentation
│   ├── examples/         # Sample data for demonstration
│   │   └── README.md     # Examples documentation
│   └── README.md         # General dataset documentation
│
├── notebooks/            # Jupyter notebooks for exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_exploration_WV.ipynb
│   └── 03_data_exploration_RUS.ipynb
│
├── src/                  # Source code
│   ├── data/            # Data processing and loading scripts
│   │   ├── create_unified_*.py  # Dataset creation scripts
│   │   ├── explore_idnet.py     # Data exploration
│   │   └── fix_fraud5_data.py   # Data quality fixes
│   ├── models/          # Model architectures
│   ├── training/        # Training scripts
│   └── utils/           # Utility functions
│
├── models/              # Trained models
│   └── README.md        # Model documentation
│
├── results/             # Experiment results
│   ├── figures/         # Visualizations
│   └── logs/            # Training logs
│
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Setup Instructions

### 1. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Setup Jupyter Kernel

```bash
python -m ipykernel install --user --name=final-project --display-name "Python (Final Project)"
```

## 🚀 Getting Started

### Quick Start
1. **Explore the Data**: Start with `notebooks/01_data_exploration.ipynb`
2. **Check Examples**: Look at `datasets/examples/` for sample data
3. **Load Processed Data**: Use the unified CSV files in `datasets/idnet/`
4. **Build Models**: Create fraud detection models using the processed data

### Data Loading Example
```python
import pandas as pd

# Load unified datasets
grc_df = pd.read_csv('datasets/idnet/GRC_Unified_Dataset.csv')
rus_df = pd.read_csv('datasets/idnet/RUS_Unified_Dataset.csv')
wv_df = pd.read_csv('datasets/idnet/WV_Unified_Dataset.csv')

# Check data structure
print(f"GRC: {grc_df.shape[0]} images, {grc_df['is_real'].sum()} real")
print(f"RUS: {rus_df.shape[0]} images, {rus_df['is_real'].sum()} real")
print(f"WV: {wv_df.shape[0]} images, {wv_df['is_real'].sum()} real")
```

## 🛠️ Key Libraries

- **Data Science**: NumPy, Pandas, SciPy
- **Machine Learning**: Scikit-learn, XGBoost
- **Deep Learning**: TensorFlow, PyTorch
- **Computer Vision**: OpenCV, Pillow, Albumentations
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Image Processing**: PIL, OpenCV
- **Data Validation**: Great Expectations

## 📈 Project Goals

1. **Binary Classification**: Real vs Fake documents
2. **Multi-Class Classification**: Identify specific fraud types
3. **Cross-Country Generalization**: Model performance across different countries
4. **Document Type Analysis**: Performance on different document types
5. **Fraud Type Detection**: Identify specific fraud techniques

## 🔬 Research Questions

- Which fraud types are most detectable?
- How does model performance vary across countries?
- Can models generalize across document types?
- What features are most important for fraud detection?

## 📝 Best Practices

- **Data Quality**: All datasets have been cleaned and validated
- **Version Control**: Use git for code, consider DVC for large files
- **Documentation**: Document experiments and model performance
- **Reproducibility**: Use fixed random seeds and save model states
- **Evaluation**: Use appropriate metrics for imbalanced datasets

## ⚠️ Important Notes

- **Large Files**: Raw datasets (~49GB) are excluded from git
- **Processing**: Use the provided scripts to recreate processed data
- **Examples**: Check `datasets/examples/` for sample data structure
- **Metadata**: Rich personal information available for each document


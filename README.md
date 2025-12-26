# 🛂 Identity Document Fraud Detection - Final Project

## 🎯 Project Overview

This project focuses on **Identity Document Fraud Detection** using machine learning and deep learning techniques. The goal is to develop models that can accurately identify forged identity documents across different types (passports, ID cards, driver's licenses) and fraud techniques.

## 📊 Datasets

### IDNet Dataset
- **Source**: [Kaggle - IDNet Identity Document Analysis](https://www.kaggle.com/datasets/chitreshkr/idnet-identity-document-analysis)
- **Size**: ~130GB+ (290,000+ images and expanding)
- **Countries**: 9+ (Albania, Greece, Russia, Latvia, Slovakia, Nevada, Washington DC, Arizona, West Virginia)
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
│   │   ├── ALB/          # Albanian passports
│   │   ├── GRC/          # Greek passports
│   │   ├── RUS/          # Russian ID cards  
│   │   ├── WV/           # West Virginia driver's licenses
│   │   ├── DC/           # Washington DC driver's licenses
│   │   ├── NV/           # Nevada ID cards
│   │   ├── LVA/          # Latvian passports
│   │   ├── SVK/          # Slovakian ID cards
│   │   ├── AZ/           # Arizona driver's licenses
│   │   ├── document_type_classification_country_split/  # Document type dataset
│   │   └── README.md     # IDNet dataset documentation
│   ├── examples/         # Sample data for demonstration
│   │   └── README.md     # Examples documentation
│   └── README.md         # General dataset documentation
│
├── notebooks/            # Jupyter notebooks for experiments
│   └── document_type_classification/  # Document type classification experiments
│       ├── dataset_overview.ipynb     # Dataset analysis and visualization
│       ├── template.ipynb             # Template for new experiments
│       ├── resnet18/                  # ResNet18 experiments
│       │   ├── resnet18_baseline_500.ipynb
│       │   ├── resnet18_baseline_1000.ipynb
│       │   ├── resnet18_baseline_2000.ipynb
│       │   └── resnet18_baseline_3600.ipynb
│       └── vit/                       # Vision Transformer experiments
│           └── vit_baseline_500.ipynb
│
├── src/                  # Source code
│   ├── data/            # Data processing and loading scripts
│   │   ├── create_unified_*.py           # Country-specific dataset creation
│   │   ├── create_document_type_dataset.py  # Document type dataset
│   │   ├── prepare_idnet_full_dataset.py    # Full IDNet dataset preparation
│   │   ├── fix_dataset_splits.py         # Fix train/val/test splits
│   │   ├── split_dataset.py              # Dataset splitting utilities
│   │   ├── load_idnet_dataset.py         # Dataset loading utilities
│   │   └── explore_idnet.py              # Data exploration tools
│   ├── models/          # Model architectures
│   │   └── cnn_models.py                 # CNN models (ResNet, EfficientNet, etc.)
│   ├── training/        # Training scripts
│   └── utils/           # Utility functions
│
├── models/              # Trained models
│   ├── checkpoints/     # Model checkpoints during training
│   └── README.md        # Model documentation
│
├── backend/               # FastAPI Backend
│   ├── app/
│   │   ├── models/       # Database schemas & Pydantic models
│   │   ├── routers/      # API Endpoints
│   │   ├── services/     # Business logic (ML, Cloudinary)
│   │   ├── main.py       # Application entry point
│   │   └── database.py   # DB Connection
│   ├── PLAN.md           # Backend technical plan
│   └── requirements.txt  # Python dependencies
│
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── components/   # Reusable UI parts
│   │   ├── pages/        # Main views (Dashboard, Analyze)
│   │   ├── context/      # State management
│   │   └── App.jsx       # Main component & Routing
│   ├── PLAN.md           # Frontend technical plan
│   └── package.json      # JS dependencies
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
1. **Explore the Data**: Start with `notebooks/document_type_classification/dataset_overview.ipynb`
2. **Check Examples**: Look at `datasets/examples/` for sample data
3. **Load Processed Data**: Use the unified CSV files in `datasets/idnet/`
4. **Train Models**: Use the notebooks in `notebooks/document_type_classification/` for model training
5. **Build Custom Models**: Create fraud detection models using the processed data



## 🛠️ Key Libraries

- **Data Science**: NumPy, Pandas, SciPy
- **Machine Learning**: Scikit-learn, XGBoost
- **Deep Learning**: TensorFlow, PyTorch
- **Computer Vision**: OpenCV, Pillow, Albumentations
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Image Processing**: PIL, OpenCV
- **Data Validation**: Great Expectations

## 📈 Project Goals

### Phase 1: Document Type Classification (Current Focus)
1. **Multi-Class Classification**: Classify documents into types (Passport, ID Card, Driver's License)
2. **Cross-Country Analysis**: Train on multiple countries, test generalization
3. **Model Comparison**: Compare different architectures (ResNet, ViT, EfficientNet)

### Phase 2: Fraud Detection (Future)
1. **Binary Classification**: Real vs Fake documents
2. **Multi-Class Classification**: Identify specific fraud types
3. **Cross-Country Generalization**: Model performance across different countries
4. **Fraud Type Detection**: Identify specific fraud techniques

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


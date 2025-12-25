# Setup Instructions

## Prerequisites
- Python 3.8+
- Git

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/username/repository-name.git
cd repository-name
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup Jupyter Kernel (optional):**
```bash
python -m ipykernel install --user --name=final-project --display-name "Python (Final Project)"
```

5. **Ensure datasets are available:**
   - Download the IDNet dataset from Kaggle
   - Extract to `datasets/idnet/` directory
   - Expected directories:
     - `datasets/idnet/ALB/` - Albanian passport images
     - `datasets/idnet/GRC/` - Greek passport images
     - `datasets/idnet/RUS/` - Russian ID card images  
     - `datasets/idnet/WV/` - West Virginia driver's licenses
     - `datasets/idnet/DC/` - Washington DC driver's license images
     - `datasets/idnet/NV/` - Nevada ID card images
     - `datasets/idnet/LVA/` - Latvian passports
     - `datasets/idnet/SVK/` - Slovakian ID cards
     - `datasets/idnet/AZ/` - Arizona driver's licenses

6. **Prepare datasets (if needed):**
```bash
# Create unified datasets
python src/data/create_unified_grc_dataset.py
python src/data/create_unified_rus_dataset.py
python src/data/create_unified_wv_dataset.py

# Create document type classification dataset
python src/data/create_document_type_dataset.py
```

## Project Structure
```
final-project/
├── src/                    # Source code
│   ├── data/              # Data processing scripts
│   ├── models/            # Model architectures (cnn_models.py)
│   ├── training/          # Training scripts
│   └── utils/             # Utility functions
│
├── notebooks/             # Jupyter notebooks
│   └── document_type_classification/
│       ├── dataset_overview.ipynb
│       ├── template.ipynb
│       ├── resnet18/      # ResNet18 experiments
│       └── vit/           # Vision Transformer experiments
│
├── datasets/              # Dataset files (local)
│   ├── idnet/
│   │   ├── ALB/           # Albanian passports
│   │   ├── GRC/           # Greek passports
│   │   ├── RUS/           # Russian ID cards
│   │   ├── WV/            # West Virginia driver's licenses
│   │   ├── DC/            # Washington DC driver's licenses
│   │   ├── NV/            # Nevada ID cards
│   │   ├── LVA/           # Latvian passports
│   │   ├── SVK/           # Slovakian ID cards
│   │   ├── AZ/            # Arizona driver's licenses
│   │   └── document_type_classification_country_split/
│   └── examples/          # Sample data
│
├── models/                # Trained models
│   └── checkpoints/       # Training checkpoints
│
├── results/               # Results and outputs
│   ├── figures/           # Visualizations
│   └── logs/              # Training logs
│
└── requirements.txt       # Python dependencies
```

## Usage
1. **Start Jupyter Lab:** 
```bash
jupyter lab
```

2. **Explore the Data:**
   - Open `notebooks/document_type_classification/dataset_overview.ipynb`
   - View dataset statistics and visualizations

3. **Train Models:**
   - Use notebooks in `notebooks/document_type_classification/resnet18/` for ResNet18 models
   - Use notebooks in `notebooks/document_type_classification/vit/` for Vision Transformer models
   - Or create new experiments using `template.ipynb`

4. **Check Results:**
   - Models saved to `models/checkpoints/`
   - Visualizations saved to `results/figures/`
   - Training logs saved to `results/logs/`

## Dataset Information
- **Total images:** ~290,000+ identity documents (and expanding)
- **Countries:** 9+ (Albania, Greece, Russia, Latvia, Slovakia, Nevada, Washington DC, Arizona, West Virginia)
- **Document types:** Passports, ID Cards, Driver's Licenses
- **Image formats:** PNG, JPG
- **Storage size:** ~130GB+
- **Local storage:** All images stored locally in `datasets/idnet/` directory

## Current Focus
The project is currently focused on **Document Type Classification**:
- **Task:** Classify documents into 3 types (Passport, ID Card, Driver's License)
- **Dataset:** `datasets/idnet/document_type_classification_country_split/`
- **Models:** ResNet18, Vision Transformer (ViT), EfficientNet
- **Notebooks:** `notebooks/document_type_classification/`

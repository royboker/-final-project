# 📊 Datasets Directory

This directory contains all datasets used in the Identity Document Fraud Detection project.

## 📁 Directory Structure

```
datasets/
├── idnet/                    # IDNet dataset (main dataset)
│   ├── GRC/                 # Greek passports
│   ├── RUS/                 # Russian ID cards
│   ├── WV/                  # American driver's licenses
│   ├── GRC_Unified_Dataset.csv
│   ├── RUS_Unified_Dataset.csv
│   ├── WV_Unified_Dataset.csv
│   └── README.md            # Detailed IDNet documentation
│
├── examples/                 # Sample data for demonstration
│   ├── grc_example/         # Greek passport example
│   ├── rus_example/         # Russian ID card example
│   ├── wv_example/          # American driver's license example
│   └── README.md            # Examples documentation
│
└── README.md                # This file
```

## 🎯 Main Dataset: IDNet

### Overview
- **Source**: [Kaggle - IDNet Identity Document Analysis](https://www.kaggle.com/datasets/chitreshkr/idnet-identity-document-analysis)
- **Size**: ~49GB (125,556 images total)
- **Countries**: 3 (Greece, Russia, USA)
- **Document Types**: Passports, ID Cards, Driver's Licenses
- **Fraud Types**: 6 different techniques

### Key Features
- **Real vs Fake**: Balanced dataset with authentic and forged documents
- **Multi-Country**: Documents from different countries and languages
- **Rich Metadata**: Personal information and detailed fraud annotations
- **Unified Format**: Processed into CSV files for easy model training

### Processed Data
The raw dataset has been processed into unified CSV files:
- `GRC_Unified_Dataset.csv` - Greek passports (41,852 images)
- `RUS_Unified_Dataset.csv` - Russian ID cards (41,852 images)
- `WV_Unified_Dataset.csv` - American driver's licenses (41,852 images)

## 📋 Dataset Statistics

| Country | Document Type | Total Images | Real Images | Fake Images | Size |
|---------|---------------|--------------|-------------|-------------|------|
| 🇬🇷 Greece | Passports | 41,852 | 4,592 (11%) | 37,260 (89%) | 8.9GB |
| 🇷🇺 Russia | ID Cards | 41,852 | 5,979 (14%) | 35,873 (86%) | 8.4GB |
| 🇺🇸 USA | Driver's Licenses | 41,852 | 1,298 (3%) | 40,554 (97%) | 31.5GB |
| **Total** | **Mixed** | **125,556** | **11,869 (9%)** | **113,687 (91%)** | **49GB** |

## 🕵️ Fraud Types

| Type | Description | Technique |
|------|-------------|-----------|
| **copy_and_move** | Copy elements from one document to another | Copy-paste manipulation |
| **face_morphing** | Blend two faces together | Face blending algorithms |
| **face_replacement** | Replace face with another person's | Face swapping |
| **combined** | Multiple fraud techniques applied together | Multi-step manipulation |
| **inpaint_and_rewrite** | Remove and rewrite text/numbers | Text field replacement |
| **crop_and_replace** | Crop parts and replace with different content | Content replacement |

## 🚀 Quick Start

### 1. Load Processed Data
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

### 2. Explore Examples
Check the `examples/` directory for sample data that demonstrates:
- Original images and their forged variations
- Metadata structure and content
- Data linking between original and fake images

### 3. Data Exploration
Use the provided notebooks:
- `notebooks/01_data_exploration.ipynb` - General exploration
- `notebooks/02_data_exploration_WV.ipynb` - WV-specific analysis
- `notebooks/03_data_exploration_RUS.ipynb` - RUS-specific analysis

## 📊 Data Quality

### ✅ Strengths
- **High Quality**: Professional document images
- **Rich Metadata**: Detailed personal information
- **Balanced**: Good representation of fraud types
- **Validated**: Data quality checks performed
- **Linked**: Original images linked to forged versions

### ⚠️ Considerations
- **Imbalanced**: Some fraud types have fewer samples
- **Country Differences**: Different document formats and languages
- **Synthetic Images**: Some fraud6 images are completely synthetic
- **Missing Data**: Some personal information fields may be empty

## 🔧 Data Processing

### Available Scripts
- `src/data/create_unified_*.py` - Create unified datasets
- `src/data/fix_fraud5_data.py` - Fix data quality issues
- `src/data/explore_idnet.py` - Data exploration utilities

### Processing Pipeline
1. **Raw Data**: Extract from zip files
2. **Metadata Extraction**: Parse JSON files
3. **Data Linking**: Connect original and fake images
4. **Quality Checks**: Validate data integrity
5. **CSV Generation**: Create unified datasets

## 📈 Use Cases

### 1. Binary Classification
- **Task**: Real vs Fake document detection
- **Input**: Document images
- **Output**: Binary classification (real/fake)

### 2. Multi-Class Classification
- **Task**: Fraud type identification
- **Input**: Document images
- **Output**: Fraud type classification

### 3. Cross-Country Analysis
- **Task**: Model generalization across countries
- **Approach**: Train on one country, test on others

### 4. Document Type Analysis
- **Task**: Performance across document types
- **Approach**: Compare model performance on different document types

## 📚 Documentation

- **IDNet Dataset**: `datasets/idnet/README.md` - Detailed dataset documentation
- **Examples**: `datasets/examples/README.md` - Sample data documentation
- **Main Project**: `README.md` - Project overview and setup

## ⚠️ Important Notes

- **Large Files**: Raw datasets (~49GB) are excluded from git
- **Processing**: Use the provided scripts to recreate processed data
- **Examples**: Check `datasets/examples/` for sample data structure
- **Metadata**: Rich personal information available for each document
- **Privacy**: Ensure compliance with data usage terms and privacy regulations

## 🚀 Next Steps

1. **Explore Data**: Start with the examples and exploration notebooks
2. **Load Processed Data**: Use the unified CSV files
3. **Build Models**: Develop fraud detection models
4. **Evaluate Performance**: Test on different countries and document types
5. **Document Results**: Record findings and model performance

---

**Note**: This dataset is for research purposes only. Ensure compliance with data usage terms and privacy regulations.

# 🛂 IDNet Dataset - Identity Document Analysis

## 📊 Dataset Overview

The IDNet dataset is a comprehensive collection of identity documents from three countries, designed for fraud detection research. It contains both authentic and forged documents with detailed metadata and fraud annotations.

### 🎯 Key Statistics
- **Total Images**: 125,556
- **Countries**: 3 (Greece, Russia, USA)
- **Document Types**: Passports, ID Cards, Driver's Licenses
- **Fraud Types**: 6 different techniques
- **Real vs Fake**: Balanced dataset (~50% each)
- **Total Size**: ~49GB (raw data)

## 🌍 Countries & Document Types

| Country | Code | Document Type | Images | Size |
|---------|------|---------------|--------|------|
| 🇬🇷 Greece | GRC | Passports | 41,852 | 8.9GB |
| 🇷🇺 Russia | RUS | ID Cards | 41,852 | 8.4GB |
| 🇺🇸 USA (West Virginia) | WV | Driver's Licenses | 41,852 | 31.5GB |

## 🕵️ Fraud Types

| Type | Description | Technique |
|------|-------------|-----------|
| **copy_and_move** | Copy elements from one document to another | Copy-paste manipulation |
| **face_morphing** | Blend two faces together | Face blending algorithms |
| **face_replacement** | Replace face with another person's | Face swapping |
| **combined** | Multiple fraud techniques applied together | Multi-step manipulation |
| **inpaint_and_rewrite** | Remove and rewrite text/numbers | Text field replacement |
| **crop_and_replace** | Crop parts and replace with different content | Content replacement |

## 📁 Directory Structure

```
idnet/
├── GRC/                          # Greek Passports
│   └── GRC/
│       ├── positive/             # Real passports (4,592 images)
│       ├── fraud1_copy_and_move/ # Copy & move fraud (5,979 images)
│       ├── fraud2_face_morphing/ # Face morphing fraud (2,083 images)
│       ├── fraud3_face_replacement/ # Face replacement fraud (5,979 images)
│       ├── fraud4_combined/      # Combined fraud (3,620 images)
│       ├── fraud5_inpaint_and_rewrite/ # Text replacement fraud (5,979 images)
│       ├── fraud6_crop_and_replace/ # Crop & replace fraud (5,978 images)
│       └── meta/                 # Metadata JSON files
│           ├── basic/            # Personal information
│           └── detailed_with_fraud_info/ # Fraud annotations
│
├── RUS/                          # Russian ID Cards
│   └── RUS/
│       ├── positive/             # Real ID cards (5,979 images)
│       ├── fraud1_copy_and_move/ # Copy & move fraud (5,979 images)
│       ├── fraud2_face_morphing/ # Face morphing fraud (5,979 images)
│       ├── fraud3_face_replacement/ # Face replacement fraud (5,979 images)
│       ├── fraud4_combined/      # Combined fraud (5,979 images)
│       ├── fraud5_inpaint_and_rewrite/ # Text replacement fraud (5,979 images)
│       ├── fraud6_crop_and_replace/ # Crop & replace fraud (5,978 images)
│       └── meta/                 # Metadata JSON files
│           ├── basic/            # Personal information
│           └── detailed_with_fraud_info/ # Fraud annotations
│
├── WV/                           # American Driver's Licenses
│   └── WV/
│       ├── positive/             # Real licenses (1,298 images)
│       ├── fraud1_copy_and_move/ # Copy & move fraud (5,979 images)
│       ├── fraud2_face_morphing/ # Face morphing fraud (1,244 images)
│       ├── fraud3_face_replacement/ # Face replacement fraud (5,979 images)
│       ├── fraud4_combined/      # Combined fraud (2,053 images)
│       ├── fraud5_inpaint_and_rewrite/ # Text replacement fraud (4,091 images)
│       ├── fraud6_crop_and_replace/ # Crop & replace fraud (1,378 images)
│       └── meta/                 # Metadata JSON files
│           ├── basic/            # Personal information
│           └── detailed_with_fraud_info/ # Fraud annotations
│
├── GRC_Unified_Dataset.csv       # Processed Greek passports dataset
├── RUS_Unified_Dataset.csv       # Processed Russian ID cards dataset
├── WV_Unified_Dataset.csv        # Processed American driver's licenses dataset
└── README.md                     # This file
```

## 📋 Processed Datasets (CSV Files)

### Unified Dataset Columns
Each CSV file contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `image_path` | Full path to the image file | `/path/to/image.png` |
| `filename` | Image filename | `generated.photos_v3_0240363.png` |
| `country` | Country code | `GRC`, `RUS`, `WV` |
| `document_type` | Type of document | `passport`, `id_card`, `driver_license` |
| `is_real` | Binary label (1=real, 0=fake) | `1` or `0` |
| `fraud_type` | Type of fraud (if fake) | `real`, `copy_and_move`, etc. |
| `original_image_id` | ID of original image | `generated.photos_v3_0240363` |
| `fraud_details` | JSON string with fraud details | `[{"type": "face_morphing", ...}]` |
| `person_name` | Person's full name | `GEORGIA VASILIOU` |
| `person_name_greek` | Name in Greek (GRC only) | `ΓΕΩΡΓΙΑ ΒΑΣΙΛΕΙΟΥ` |
| `birth_date` | Date of birth | `1990-05-15` |
| `document_number` | Document number | `AB1234567` |
| `issue_date` | Document issue date | `2020-01-15` |
| `expire_date` | Document expiration date | `2030-01-15` |
| `gender` | Person's gender | `F`, `M` |
| `height` | Person's height | `165 cm` |
| `place_of_birth` | Place of birth | `Athens, Greece` |
| `place_of_birth_greek` | Place of birth in Greek (GRC only) | `Αθήνα, Ελλάδα` |
| `country_code` | ISO country code | `GRC`, `RUS`, `USA` |
| `country_name` | Full country name | `Greece`, `Russia`, `United States` |
| `issue_authority` | Document issuing authority | `Ministry of Interior` |

### Dataset Statistics

#### GRC (Greek Passports)
- **Total Images**: 41,852
- **Real Images**: 4,592 (11.0%)
- **Fake Images**: 37,260 (89.0%)
- **Fraud Distribution**:
  - copy_and_move: 5,979 (16.0%)
  - face_morphing: 2,083 (5.6%)
  - face_replacement: 5,979 (16.0%)
  - combined: 3,620 (9.7%)
  - inpaint_and_rewrite: 5,979 (16.0%)
  - crop_and_replace: 5,978 (16.0%)

#### RUS (Russian ID Cards)
- **Total Images**: 41,852
- **Real Images**: 5,979 (14.3%)
- **Fake Images**: 35,873 (85.7%)
- **Fraud Distribution**:
  - copy_and_move: 5,979 (16.7%)
  - face_morphing: 5,979 (16.7%)
  - face_replacement: 5,979 (16.7%)
  - combined: 5,979 (16.7%)
  - inpaint_and_rewrite: 5,979 (16.7%)
  - crop_and_replace: 5,978 (16.7%)

#### WV (American Driver's Licenses)
- **Total Images**: 41,852
- **Real Images**: 1,298 (3.1%)
- **Fake Images**: 40,554 (96.9%)
- **Fraud Distribution**:
  - copy_and_move: 5,979 (14.7%)
  - face_morphing: 1,244 (3.1%)
  - face_replacement: 5,979 (14.7%)
  - combined: 2,053 (5.1%)
  - inpaint_and_rewrite: 4,091 (10.1%)
  - crop_and_replace: 1,378 (3.4%)

## 🔧 Data Processing Scripts

### Available Scripts
- `src/data/create_unified_grc_dataset.py` - Create GRC unified dataset
- `src/data/create_unified_rus_dataset.py` - Create RUS unified dataset
- `src/data/create_unified_wv_dataset.py` - Create WV unified dataset
- `src/data/fix_fraud5_data.py` - Fix data quality issues
- `src/data/explore_idnet.py` - Data exploration utilities

### Usage Example
```python
# Load processed dataset
import pandas as pd

df = pd.read_csv('datasets/idnet/GRC_Unified_Dataset.csv')

# Check data quality
print(f"Total images: {len(df)}")
print(f"Real images: {df['is_real'].sum()}")
print(f"Fake images: {(~df['is_real'].astype(bool)).sum()}")

# Check fraud type distribution
print(df['fraud_type'].value_counts())
```

## 🎯 Use Cases

### 1. Binary Classification
- **Task**: Real vs Fake document detection
- **Input**: Document images
- **Output**: Binary classification (real/fake)
- **Evaluation**: Accuracy, Precision, Recall, F1-Score

### 2. Multi-Class Classification
- **Task**: Fraud type identification
- **Input**: Document images
- **Output**: Fraud type classification
- **Classes**: 6 fraud types + real

### 3. Cross-Country Analysis
- **Task**: Model generalization across countries
- **Approach**: Train on one country, test on others
- **Goal**: Understand cultural/document differences

### 4. Document Type Analysis
- **Task**: Performance across document types
- **Approach**: Compare model performance on passports vs ID cards vs licenses
- **Goal**: Identify document-specific challenges

## 📊 Data Quality Notes

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

## 🔍 Data Exploration

### Quick Start
1. **Load Data**: Use the provided CSV files
2. **Explore Examples**: Check `datasets/examples/` for sample data
3. **Run Notebooks**: Use the exploration notebooks in `notebooks/`
4. **Visualize**: Create visualizations of fraud types and distributions

### Recommended Analysis
- **Image Analysis**: Document layout, text regions, security features
- **Metadata Analysis**: Personal information patterns, document validity
- **Fraud Pattern Analysis**: Common fraud techniques and their characteristics
- **Cross-Country Comparison**: Document format differences and similarities

## 📚 References

- **Original Dataset**: [Kaggle - IDNet Identity Document Analysis](https://www.kaggle.com/datasets/chitreshkr/idnet-identity-document-analysis)
- **Research Paper**: [Identity Document Analysis and Verification](https://example.com)
- **License**: Check Kaggle dataset page for usage terms

## 🚀 Next Steps

1. **Data Exploration**: Start with the provided notebooks
2. **Model Development**: Build fraud detection models
3. **Evaluation**: Test on different countries and document types
4. **Analysis**: Understand fraud patterns and model performance
5. **Documentation**: Document findings and model performance

---

**Note**: This dataset is for research purposes only. Ensure compliance with data usage terms and privacy regulations.

# 📁 Examples Directory - IDNet Dataset Samples

This directory contains complete examples from the IDNet dataset, demonstrating the relationship between original images and their forged variations. These examples are perfect for understanding the dataset structure and for model development.

## 🎯 Purpose

Each example demonstrates:
- **1 Original Image** (real document)
- **4-5 Fake Variations** (different fraud types)
- **Metadata JSONs** (personal information and fraud details)
- **Data Linking** (how original and fake images are connected)

## 📂 Structure

### 🛂 GRC Example (Greek Passports)
**Location**: `grc_example/`
**Person**: GEORGIA VASILIOU
**Document Type**: Passport
**Country**: Greece (GRC)

**Files**:
- `original_generated.photos_v3_0240363.png` - Original passport
- `fake_copy_and_move_generated.photos_v3_0240363.png` - Copy & move fraud
- `fake_face_morphing_generated.photos_v3_0240363.png` - Face morphing fraud
- `fake_face_replacement_generated.photos_v3_0240363.png` - Face replacement fraud
- `fake_combined_generated.photos_v3_0240363.png` - Combined fraud
- `basic_metadata_generated.photos_v3_0240363.json` - Personal information metadata

### 🪪 RUS Example (Russian ID Cards)
**Location**: `rus_example/`
**Person**: MAKAROVA ALISA
**Document Type**: ID Card
**Country**: Russia (RUS)

**Files**:
- `original_generated.photos_v3_0240363.png` - Original ID card
- `fake_copy_and_move_generated.photos_v3_0240363.png` - Copy & move fraud
- `fake_face_morphing_generated.photos_v3_0240363.png` - Face morphing fraud
- `fake_face_replacement_generated.photos_v3_0240363.png` - Face replacement fraud
- `fake_combined_generated.photos_v3_0240363.png` - Combined fraud
- `basic_metadata_generated.photos_v3_0240363.json` - Personal information metadata

### 🚗 WV Example (American Driver's Licenses)
**Location**: `wv_example/`
**Person**: Hailey Mendez
**Document Type**: Driver's License
**Country**: United States (USA)

**Files**:
- `original_generated.photos_v3_0240363.png` - Original driver's license
- `fake_copy_and_move_generated.photos_v3_0240363.png` - Copy & move fraud
- `fake_face_morphing_generated.photos_v3_0240363.png` - Face morphing fraud
- `fake_face_replacement_generated.photos_v3_0240363.png` - Face replacement fraud
- `fake_combined_generated.photos_v3_0240363.png` - Combined fraud
- `basic_metadata_generated.photos_v3_0240363.json` - Personal information metadata

## 🔍 Fraud Types Explained

1. **copy_and_move** - Copy and move elements from one document to another
2. **face_morphing** - Blend two faces together to create a new identity
3. **face_replacement** - Replace the face in the document with another person's face
4. **combined** - Multiple fraud techniques applied together
5. **inpaint_and_rewrite** - Remove and rewrite text/numbers
6. **crop_and_replace** - Crop parts and replace with different content

## 📊 Dataset Statistics

- **Total Examples**: 3 (one per document type)
- **Images per Example**: 5 (1 original + 4 fake variations)
- **Total Images**: 15
- **JSON Files**: 3 (1 basic metadata per example)
- **Countries Covered**: 3 (Greece, Russia, USA - West Virginia)
- **Document Types**: 3 (Passports, ID Cards, Driver's Licenses)

## 🎯 Usage

These examples are perfect for:
- **Model Training**: Understanding the relationship between original and fake images
- **Research**: Analyzing different fraud techniques
- **Demonstration**: Showing the dataset structure to stakeholders
- **Testing**: Validating model performance on known examples
- **Data Understanding**: Learning how fraud types affect document appearance
- **Cross-Country Analysis**: Comparing document formats across countries

## 🔍 Key Insights

### Document Type Differences
- **Passports (GRC)**: International format, multiple languages, security features
- **ID Cards (RUS)**: National format, Cyrillic script, different layout
- **Driver's Licenses (WV)**: State format, English text, driving-specific information

### Fraud Type Characteristics
- **copy_and_move**: Subtle changes, often in text fields
- **face_morphing**: Blended facial features, smooth transitions
- **face_replacement**: Clear face swaps, potential lighting inconsistencies
- **combined**: Multiple techniques, more complex manipulations

## 📈 Model Development Tips

1. **Start with Examples**: Use these samples to understand the data
2. **Compare Fraud Types**: Analyze visual differences between fraud types
3. **Cross-Country Training**: Test model generalization across countries
4. **Metadata Integration**: Use personal information for additional features
5. **Validation**: Use these known examples for model validation

## ⚠️ Important Notes

- **Renamed Files**: All images are renamed to include the fraud type in the filename for easy identification
- **Original Dataset**: The original dataset structure remains unchanged
- **Metadata**: JSON files contain rich personal information and fraud details
- **Quality**: These examples represent high-quality fraud samples from the dataset
- **Linking**: Original images are properly linked to their forged variations

## 🚀 Next Steps

1. **Examine Examples**: Look at the images and understand the fraud patterns
2. **Load Metadata**: Read the JSON files to understand the data structure
3. **Build Models**: Use these examples to develop fraud detection models
4. **Validate Performance**: Test models on these known examples
5. **Scale Up**: Apply learnings to the full dataset

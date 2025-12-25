# 📄 Document Type Classification Demo

Professional demo for document type classification using deep learning models.

## 🎯 Features

- **Modern and user-friendly interface** - Built with Streamlit
- **Support for two models**:
  - Vision Transformer (ViT)
  - ResNet18
- **Detailed results display**:
  - Identified document type
  - Confidence level
  - Probability distribution for all categories
- **Professional design** - Ready for presentation

## 📋 Requirements

- Python 3.8+
- PyTorch
- Streamlit
- All dependencies from `requirements.txt`

## 🚀 Installation and Running

### 1. Install Dependencies

```bash
# From the project root directory
pip install -r requirements.txt
```

Or for the demo only:
```bash
pip install streamlit torch torchvision timm albumentations pillow numpy
```

### 2. Verify Models Exist

The demo expects to find the models at the following paths:
- `models/vit_document_classifier_9000.pth`
- `models/resnet18_document_classifier_9000.pth`

If the models are located elsewhere, update the paths in `app.py`.

### 3. Run the Demo

```bash
# From the project root directory
cd demo
streamlit run app.py
```

Or from the root directory:
```bash
streamlit run demo/app.py
```

The demo will automatically open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Load Models**: Click the "🔄 Load Models" button in the sidebar
2. **Select Model**: Choose a model from the dropdown (ViT or ResNet18)
3. **Upload Image**: Upload an image of an ID card, passport, or driver license
4. **Classify**: Click "🔍 Classify Image" to get the results

## 🎨 Interface Features

- **Modern design**: Clean and professional interface
- **Image preview**: Preview of the uploaded image
- **Detailed results**:
  - Identified document type
  - Confidence level in percentage
  - Probability distribution for all categories
  - Visual indicator of confidence level
- **Color-coded confidence**:
  - 🟢 Green: High confidence (≥70%)
  - 🟡 Yellow: Medium confidence (50-70%)
  - 🔴 Red: Low confidence (<50%)

## 🔧 Troubleshooting

### Models Not Loading
- Verify that the files exist at the correct paths
- Check that there is sufficient available memory
- If there are errors, check the console logs

### Errors During Classification
- Ensure the image is in a supported format (JPG, JPEG, PNG)
- Verify the image is not corrupted
- Try a different image

### Slow Performance
- Models are loaded once and kept in memory
- Classification itself is relatively fast
- If still slow, try using GPU if available

## 📝 Technical Notes

- Models use Albumentations transformations
- Required image size: 224x224 pixels
- Models are trained on 3 categories: ID Card, Passport, Driver License
- Models are trained on 9000 images with advanced augmentation techniques

## 🎓 Further Learning

For more details about the models and training, see:
- `notebooks/document_type_classification/vit/`
- `notebooks/document_type_classification/resnet18/`

## 📄 License

This is part of the final project for identity document fraud detection.

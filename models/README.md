# 🤖 Trained Models - Identity Document Fraud Detection

This directory stores all trained models for the Identity Document Fraud Detection project.

## 📁 Directory Structure

```
models/
├── checkpoints/          # Model checkpoints saved during training
│                        # (e.g., best model, epoch checkpoints)
└── README.md            # This file
```

## 📂 Checkpoints Directory

The `checkpoints/` directory contains:
- **Training Checkpoints**: Model states saved during training
- **Best Models**: Best performing models based on validation metrics
- **Epoch Saves**: Regular saves at specific epochs for recovery
- **Experiment Tracking**: Models from different experiments and configurations

### Checkpoint Naming Convention
- `{model_name}_epoch_{epoch}_val_acc_{acc}.pth` - PyTorch models
- `{model_name}_best.pth` - Best model based on validation performance
- `{model_name}_latest.pth` - Latest checkpoint for recovery

## 🎯 Model Types

### Document Type Classification Models (Current Focus)
- **Document Type Detection**: Models that classify document types
- **Use Case**: Identify if document is Passport, ID Card, or Driver's License
- **Target**: `document_type` column (3 classes)
- **Architectures**: ResNet18, Vision Transformer (ViT), EfficientNet

### Binary Classification Models (Future)
- **Real vs Fake Detection**: Models that classify documents as authentic or forged
- **Use Case**: General fraud detection across all document types
- **Target**: `is_real` column (1=real, 0=fake)

### Multi-Class Classification Models (Future)
- **Fraud Type Detection**: Models that identify specific fraud techniques
- **Use Case**: Detailed fraud analysis and forensic investigation
- **Target**: `fraud_type` column (6 fraud types + real)

### Cross-Country Models
- **Country-Specific Models**: Trained on specific countries (GRC, RUS, WV, LVA, SVK, AZ)
- **Generalization Models**: Trained on multiple countries for cross-country performance
- **Use Case**: Understanding cultural and document format differences

## 📝 Naming Convention

Use descriptive names with versions and dates:
- `{model_type}_{dataset}_{task}_{version}_{date}.{ext}`
- Examples:
  - `resnet18_document_type_v1_20241120.pth`
  - `vit_document_type_baseline_20241120.pth`
  - `efficientnet_crosscountry_binary_v1_20241120.pth`
  
For checkpoints:
- `resnet18_document_type_epoch_10_val_acc_0.92.pth`
- `vit_baseline_best.pth`
- `resnet18_latest.pth`

## File Formats

- `.pkl` - Scikit-learn models (pickle)
- `.h5` - Keras/TensorFlow models
- `.pth` / `.pt` - PyTorch models
- `.onnx` - ONNX format (cross-platform)
- `.pb` - TensorFlow SavedModel format

## 📊 Model Documentation Template

For each model, document:

### Model Name: [Name]
- **Date Trained**: YYYY-MM-DD
- **Model Type**: CNN, ResNet, EfficientNet, etc.
- **Framework**: TensorFlow, PyTorch, Scikit-learn
- **Dataset**: IDNet (GRC/RUS/WV/All)
- **Task**: Binary/Multi-class classification
- **Countries**: Which countries used for training/testing
- **Performance Metrics**:
  - Accuracy: X%
  - Precision: X%
  - Recall: X%
  - F1-Score: X
  - AUC-ROC: X
  - Loss: X
- **Hyperparameters**: List key hyperparameters
- **Training Time**: How long it took to train
- **Data Augmentation**: What augmentation techniques used
- **Cross-Validation**: CV strategy and results
- **Notes**: Any special considerations or observations

## 🎯 Recommended Model Architectures

### Computer Vision Models
- **CNN**: Custom convolutional neural networks
- **ResNet**: Residual networks for deep learning
- **EfficientNet**: Efficient and accurate models
- **Vision Transformer**: Transformer-based models
- **MobileNet**: Lightweight models for deployment

### Traditional ML Models
- **Random Forest**: For metadata-based classification
- **XGBoost**: Gradient boosting for tabular data
- **SVM**: Support vector machines
- **Logistic Regression**: Baseline models

## 📈 Evaluation Metrics

### Binary Classification
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under the ROC curve

### Multi-Class Classification
- **Macro F1**: Average F1-score across all classes
- **Weighted F1**: F1-score weighted by class frequency
- **Confusion Matrix**: Detailed class-wise performance
- **Per-Class Metrics**: Individual class performance

## 🔄 Cross-Validation Strategy

### Recommended Approaches
1. **Country-Based Split**: Train on 2 countries, test on 1
2. **Document Type Split**: Train on 2 document types, test on 1
3. **Fraud Type Split**: Ensure all fraud types in train/test
4. **Temporal Split**: If temporal information available
5. **Stratified Split**: Maintain class distribution

## 📋 Model Comparison Template

| Model | Architecture | Dataset | Countries | Accuracy | F1-Score | Training Time | Notes |
|-------|-------------|---------|-----------|----------|----------|---------------|-------|
| Baseline | CNN | GRC | GRC | 85% | 0.84 | 2h | Simple architecture |
| ResNet50 | ResNet | All | All | 92% | 0.91 | 8h | Best overall performance |
| EfficientNet | EfficientNet | GRC+RUS | WV | 78% | 0.76 | 6h | Cross-country test |

## 🚀 Deployment Considerations

### Model Size
- **Edge Deployment**: Lightweight models (MobileNet, EfficientNet-B0)
- **Cloud Deployment**: Larger models (ResNet, EfficientNet-B7)
- **Batch Processing**: Any architecture suitable

### Inference Speed
- **Real-time**: < 100ms per image
- **Batch**: < 1s per image
- **Offline**: Any speed acceptable

### Accuracy vs Speed Trade-off
- **High Accuracy**: ResNet, EfficientNet-B7
- **Balanced**: EfficientNet-B3, ResNet50
- **High Speed**: MobileNet, EfficientNet-B0

---

## 📝 Your Models

Document your trained models below:

### Example Entry

### Model Name: cnn_idnet_binary_v1_20241004.h5
- **Date Trained**: 2024-10-04
- **Model Type**: Custom CNN
- **Framework**: TensorFlow/Keras
- **Dataset**: IDNet (All countries)
- **Task**: Binary classification (Real vs Fake)
- **Countries**: Train: GRC+RUS, Test: WV
- **Performance Metrics**:
  - Accuracy: 89%
  - Precision: 0.88
  - Recall: 0.90
  - F1-Score: 0.89
  - AUC-ROC: 0.94
- **Hyperparameters**: 
  - Learning Rate: 0.001
  - Batch Size: 32
  - Epochs: 50
  - Optimizer: Adam
- **Training Time**: 4 hours
- **Data Augmentation**: Rotation, Flip, Brightness
- **Cross-Validation**: 5-fold stratified
- **Notes**: Good baseline model, struggles with face_morphing fraud type



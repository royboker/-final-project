"""
CNN Models for Document Type Classification

This module contains various CNN architectures for classifying document types:
- Passports (Greece)
- ID Cards (Russia) 
- Driver's Licenses (USA - West Virginia)

Models included:
1. BaselineCNN - Simple CNN from scratch
2. ResNetDocumentClassifier - ResNet with transfer learning
3. EfficientNetDocumentClassifier - EfficientNet with transfer learning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torchvision.models import efficientnet_b0, resnet18, resnet50


class BaselineCNN(nn.Module):
    """
    Simple CNN architecture built from scratch for document classification.
    
    Architecture:
    - 3 Convolutional blocks (Conv2D + BatchNorm + ReLU + MaxPool)
    - 2 Fully connected layers
    - Dropout for regularization
    """
    
    def __init__(self, num_classes=3, input_channels=3):
        super(BaselineCNN, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        # Calculate the size after convolutions
        # For 224x224 input: 224 -> 112 -> 56 -> 28
        self.fc_input_size = 128 * 28 * 28
        
        # Fully connected layers
        self.fc1 = nn.Linear(self.fc_input_size, 512)
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(256, num_classes)
        
    def forward(self, x):
        # Convolutional layers
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        
        # Flatten
        x = x.view(-1, self.fc_input_size)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.fc3(x)
        
        return x


class ResNetDocumentClassifier(nn.Module):
    """
    ResNet-based document classifier with transfer learning.
    
    Uses pre-trained ResNet backbone and replaces the final layer
    for document type classification.
    """
    
    def __init__(self, num_classes=3, pretrained=True, model_size='resnet18'):
        super(ResNetDocumentClassifier, self).__init__()
        
        # Load pre-trained ResNet backbone
        if model_size == 'resnet18':
            self.backbone = resnet18(weights='IMAGENET1K_V1' if pretrained else None)
            feature_dim = self.backbone.fc.in_features
        elif model_size == 'resnet50':
            self.backbone = resnet50(weights='IMAGENET1K_V1' if pretrained else None)
            feature_dim = self.backbone.fc.in_features
        else:
            raise ValueError(f"Unsupported model size: {model_size}")
        
        # Replace the final layer
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        return self.backbone(x)


class EfficientNetDocumentClassifier(nn.Module):
    """
    EfficientNet-based document classifier with transfer learning.
    
    Uses pre-trained EfficientNet-B0 backbone and replaces the final layer
    for document type classification.
    """
    
    def __init__(self, num_classes=3, pretrained=True):
        super(EfficientNetDocumentClassifier, self).__init__()
        
        # Load pre-trained EfficientNet-B0
        self.backbone = efficientnet_b0(weights='IMAGENET1K_V1' if pretrained else None)
        feature_dim = self.backbone.classifier[1].in_features
        
        # Replace the classifier
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        return self.backbone(x)


def create_model(model_name='baseline', num_classes=3, pretrained=True, **kwargs):
    """
    Factory function to create different model architectures.
    
    Args:
        model_name (str): Name of the model to create
            - 'baseline': Simple CNN from scratch
            - 'resnet18': ResNet-18 with transfer learning
            - 'resnet50': ResNet-50 with transfer learning
            - 'efficientnet': EfficientNet-B0 with transfer learning
        num_classes (int): Number of output classes
        pretrained (bool): Whether to use pre-trained weights
        **kwargs: Additional arguments for specific models
    
    Returns:
        torch.nn.Module: The created model
    """
    
    if model_name == 'baseline':
        return BaselineCNN(num_classes=num_classes)
    
    elif model_name == 'resnet18':
        return ResNetDocumentClassifier(
            num_classes=num_classes, 
            pretrained=pretrained, 
            model_size='resnet18'
        )
    
    elif model_name == 'resnet50':
        return ResNetDocumentClassifier(
            num_classes=num_classes, 
            pretrained=pretrained, 
            model_size='resnet50'
        )
    
    elif model_name == 'efficientnet':
        return EfficientNetDocumentClassifier(
            num_classes=num_classes, 
            pretrained=pretrained
        )
    
    else:
        raise ValueError(f"Unknown model name: {model_name}")


def get_model_info(model):
    """
    Get information about a model including number of parameters.
    
    Args:
        model (torch.nn.Module): The model to analyze
    
    Returns:
        dict: Model information including parameter count
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'model_name': model.__class__.__name__
    }


if __name__ == "__main__":
    # Test the models
    print("🧪 Testing CNN Models for Document Classification")
    print("=" * 60)
    
    # Test input
    batch_size = 4
    input_tensor = torch.randn(batch_size, 3, 224, 224)
    
    # Test each model
    models_to_test = ['baseline', 'resnet18', 'resnet50', 'efficientnet']
    
    for model_name in models_to_test:
        print(f"\n📊 Testing {model_name.upper()}:")
        print("-" * 30)
        
        # Create model
        model = create_model(model_name, num_classes=3, pretrained=False)
        
        # Get model info
        info = get_model_info(model)
        print(f"   Model: {info['model_name']}")
        print(f"   Total parameters: {info['total_parameters']:,}")
        print(f"   Trainable parameters: {info['trainable_parameters']:,}")
        
        # Test forward pass
        model.eval()
        with torch.no_grad():
            output = model(input_tensor)
            print(f"   Input shape: {input_tensor.shape}")
            print(f"   Output shape: {output.shape}")
            print(f"   ✅ Forward pass successful!")
    
    print(f"\n🎯 All models tested successfully!")
    print(f"Ready for training on document classification task.")

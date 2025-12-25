"""
Model loader utility for document classification demo.
Supports both ViT and ResNet18 models.
"""

import torch
import torch.nn as nn
import timm
from torchvision.models import resnet18
from PIL import Image
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2


class ViTTinyClassifier(nn.Module):
    """ViT-Tiny model for document classification."""
    
    def __init__(self, num_classes=3, pretrained=True, dropout=0.2):
        super(ViTTinyClassifier, self).__init__()
        
        # Load ViT-Tiny from timm
        self.vit = timm.create_model('vit_tiny_patch16_224', pretrained=pretrained, num_classes=0)
        
        # Get the feature dimension
        num_features = self.vit.embed_dim
        
        # Add classifier head with dropout
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(num_features, num_classes)
        )
        
    def forward(self, x):
        # Get features from ViT backbone
        features = self.vit(x)
        # Pass through classifier head
        return self.head(features)


class ResNet18Classifier(nn.Module):
    """ResNet18 model for document classification."""
    
    def __init__(self, num_classes=3, pretrained=False, dropout=0.3):
        super(ResNet18Classifier, self).__init__()
        
        # Load ResNet18
        self.backbone = resnet18(weights=None if not pretrained else 'IMAGENET1K_V1')
        feature_dim = self.backbone.fc.in_features
        
        # Replace the final layer
        self.backbone.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        return self.backbone(x)


def load_vit_model(model_path, device='cpu'):
    """Load ViT model from checkpoint."""
    model = ViTTinyClassifier(num_classes=3, pretrained=True, dropout=0.2)
    
    try:
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        
        # Handle different checkpoint formats
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'], strict=False)
            elif 'state_dict' in checkpoint:
                model.load_state_dict(checkpoint['state_dict'], strict=False)
            else:
                # Try to load as state_dict directly
                try:
                    model.load_state_dict(checkpoint, strict=False)
                except Exception as e:
                    # If that fails, try loading each key individually
                    model_dict = model.state_dict()
                    pretrained_dict = {k: v for k, v in checkpoint.items() if k in model_dict}
                    model_dict.update(pretrained_dict)
                    model.load_state_dict(model_dict, strict=False)
        else:
            # Checkpoint is directly a state_dict
            model.load_state_dict(checkpoint, strict=False)
    except Exception as e:
        raise Exception(f"Failed to load ViT model: {str(e)}")
    
    model.to(device)
    model.eval()
    return model


def load_resnet18_model(model_path, device='cpu'):
    """Load ResNet18 model from checkpoint."""
    model = ResNet18Classifier(num_classes=3, pretrained=False, dropout=0.3)
    
    try:
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        
        # Handle different checkpoint formats
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'], strict=False)
            elif 'state_dict' in checkpoint:
                model.load_state_dict(checkpoint['state_dict'], strict=False)
            else:
                # Try to load as state_dict directly
                try:
                    model.load_state_dict(checkpoint, strict=False)
                except Exception as e:
                    # If that fails, try loading each key individually
                    model_dict = model.state_dict()
                    pretrained_dict = {k: v for k, v in checkpoint.items() if k in model_dict}
                    model_dict.update(pretrained_dict)
                    model.load_state_dict(model_dict, strict=False)
        else:
            # Checkpoint is directly a state_dict
            model.load_state_dict(checkpoint, strict=False)
    except Exception as e:
        raise Exception(f"Failed to load ResNet18 model: {str(e)}")
    
    model.to(device)
    model.eval()
    return model


def get_transforms():
    """Get image transforms for inference (same as validation/test)."""
    return A.Compose([
        A.Resize(224, 224),
        A.Normalize(
            mean=(0.485, 0.456, 0.406), 
            std=(0.229, 0.224, 0.225)
        ),
        ToTensorV2(),
    ])


def predict_image(model, image, device='cpu', label_map=None):
    """
    Predict document type from an image.
    
    Args:
        model: Loaded PyTorch model
        image: PIL Image or numpy array
        device: Device to run inference on
        label_map: Dictionary mapping class indices to labels
    
    Returns:
        dict with 'predicted', 'confidence', and 'probabilities'
    """
    if label_map is None:
        label_map = {
            0: "ID Card",
            1: "Passport",
            2: "Driver License"
        }
    
    # Get transforms
    transform = get_transforms()
    
    # Convert PIL to numpy if needed
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert("RGB"))
    else:
        img_np = np.array(image)
    
    # Apply transform
    transformed = transform(image=img_np)
    img_tensor = transformed['image'].unsqueeze(0).to(device)
    
    # Make prediction
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        predicted_class = torch.argmax(outputs, dim=1).item()
        confidence = probabilities[0][predicted_class].item()
    
    # Build result
    result = {
        'predicted': label_map[predicted_class],
        'confidence': confidence,
        'probabilities': {
            label_map[0]: probabilities[0][0].item(),
            label_map[1]: probabilities[0][1].item(),
            label_map[2]: probabilities[0][2].item()
        }
    }
    
    return result


def get_device():
    """Get the best available device."""
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


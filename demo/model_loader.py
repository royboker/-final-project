"""
Model loader utility for document analysis demo.
Supports document type classification, binary forgery detection, and fraud type classification.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
from torchvision.models import resnet18
from PIL import Image
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2


# ============================================
# Document Type Classification Models
# ============================================

class ViTTinyClassifier(nn.Module):
    """ViT-Tiny model for document type classification (3 classes)."""

    def __init__(self, num_classes=3, pretrained=True, dropout=0.2):
        super(ViTTinyClassifier, self).__init__()
        self.vit = timm.create_model('vit_tiny_patch16_224', pretrained=pretrained, num_classes=0)
        num_features = self.vit.embed_dim
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(num_features, num_classes)
        )

    def forward(self, x):
        features = self.vit(x)
        return self.head(features)


class ResNet18Classifier(nn.Module):
    """ResNet18 model for document type classification (3 classes)."""

    def __init__(self, num_classes=3, pretrained=False, dropout=0.3):
        super(ResNet18Classifier, self).__init__()
        self.backbone = resnet18(weights=None if not pretrained else 'IMAGENET1K_V1')
        feature_dim = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


# ============================================
# Forgery Detection Models (ViT-Small)
# ============================================

class ViTBinaryClassifier(nn.Module):
    """ViT-Small model for binary forgery detection (Real vs Fake)."""

    def __init__(self, model_name='vit_small_patch16_224', num_classes=2, pretrained=False, dropout=0.1):
        super(ViTBinaryClassifier, self).__init__()
        self.vit = timm.create_model(model_name, pretrained=pretrained, num_classes=0)
        num_features = self.vit.embed_dim
        self.classifier = nn.Sequential(
            nn.LayerNorm(num_features),
            nn.Linear(num_features, num_features // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(num_features // 2, num_classes)
        )

    def forward(self, x):
        features = self.vit(x)
        return self.classifier(features)


class ViTFraudTypeClassifier(nn.Module):
    """ViT-Small model for fraud type classification (Morphing vs Replacement)."""

    def __init__(self, model_name='vit_small_patch16_224', num_classes=2, pretrained=False, dropout=0.1):
        super(ViTFraudTypeClassifier, self).__init__()
        self.vit = timm.create_model(model_name, pretrained=pretrained, num_classes=0)
        num_features = self.vit.embed_dim
        self.classifier = nn.Sequential(
            nn.LayerNorm(num_features),
            nn.Linear(num_features, num_features // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(num_features // 2, num_classes)
        )

    def forward(self, x):
        features = self.vit(x)
        return self.classifier(features)


# ============================================
# Model Loading Functions
# ============================================

def _load_state_dict(model, model_path, device):
    """Load state dict with flexible format handling."""
    checkpoint = torch.load(model_path, map_location=device, weights_only=True)

    if isinstance(checkpoint, dict):
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'], strict=False)
        elif 'state_dict' in checkpoint:
            model.load_state_dict(checkpoint['state_dict'], strict=False)
        else:
            model.load_state_dict(checkpoint, strict=False)
    else:
        model.load_state_dict(checkpoint, strict=False)

    model.to(device)
    model.eval()
    return model


def load_vit_model(model_path, device='cpu'):
    """Load ViT document type classifier."""
    model = ViTTinyClassifier(num_classes=3, pretrained=False, dropout=0.2)
    return _load_state_dict(model, model_path, device)


def load_resnet18_model(model_path, device='cpu'):
    """Load ResNet18 document type classifier."""
    model = ResNet18Classifier(num_classes=3, pretrained=False, dropout=0.3)
    return _load_state_dict(model, model_path, device)


def load_binary_model(model_path, device='cpu'):
    """Load ViT-Small binary forgery detector."""
    model = ViTBinaryClassifier(pretrained=False)
    return _load_state_dict(model, model_path, device)


def load_fraud_type_model(model_path, device='cpu'):
    """Load ViT-Small fraud type classifier."""
    model = ViTFraudTypeClassifier(pretrained=False)
    return _load_state_dict(model, model_path, device)


# ============================================
# Transforms
# ============================================

def get_transforms():
    """Standard inference transforms (resize + normalize)."""
    return A.Compose([
        A.Resize(224, 224),
        A.Normalize(
            mean=(0.485, 0.456, 0.406),
            std=(0.229, 0.224, 0.225)
        ),
        ToTensorV2(),
    ])


def get_tta_transforms():
    """Test-Time Augmentation transforms (4 views)."""
    base = A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    scale_down = A.Compose([
        A.Resize(224, 224),
        A.Affine(scale=(0.95, 0.95), p=1.0),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    scale_up = A.Compose([
        A.Resize(224, 224),
        A.Affine(scale=(1.05, 1.05), p=1.0),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    brightness = A.Compose([
        A.Resize(224, 224),
        A.ColorJitter(brightness=0.1, contrast=0, saturation=0, hue=0, p=1.0),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    return [base, scale_down, scale_up, brightness]


# ============================================
# Prediction Functions
# ============================================

def predict_image(model, image, device='cpu', label_map=None):
    """
    Predict document type (standard, no TTA).
    Returns dict with 'predicted', 'confidence', and 'probabilities'.
    """
    if label_map is None:
        label_map = {0: "ID Card", 1: "Passport", 2: "Driver License"}

    transform = get_transforms()

    if isinstance(image, Image.Image):
        img_np = np.array(image.convert("RGB"))
    else:
        img_np = np.array(image)

    transformed = transform(image=img_np)
    img_tensor = transformed['image'].unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = F.softmax(outputs, dim=1)
        predicted_class = torch.argmax(outputs, dim=1).item()
        confidence = probabilities[0][predicted_class].item()

    result = {
        'predicted': label_map[predicted_class],
        'confidence': confidence,
        'probabilities': {
            label_map[i]: probabilities[0][i].item()
            for i in range(len(label_map))
        }
    }
    return result


def predict_with_tta(model, image, device='cpu', label_map=None):
    """
    Predict with Test-Time Augmentation (4 views averaged).
    Returns dict with 'predicted', 'confidence', 'probabilities', and 'predicted_idx'.
    """
    if label_map is None:
        label_map = {0: "Real", 1: "Fake"}

    if isinstance(image, Image.Image):
        img_np = np.array(image.convert("RGB"))
    else:
        img_np = np.array(image)

    tta_transforms = get_tta_transforms()
    model.eval()
    all_probs = []

    with torch.no_grad():
        for t in tta_transforms:
            transformed = t(image=img_np)
            img_tensor = transformed['image'].unsqueeze(0).to(device)
            outputs = model(img_tensor)
            probs = F.softmax(outputs, dim=1)
            all_probs.append(probs.cpu())

    avg_probs = torch.stack(all_probs).mean(dim=0)
    predicted_idx = avg_probs.argmax(dim=1).item()
    confidence = avg_probs[0][predicted_idx].item()

    result = {
        'predicted': label_map[predicted_idx],
        'predicted_idx': predicted_idx,
        'confidence': confidence,
        'probabilities': {
            label_map[i]: avg_probs[0][i].item()
            for i in range(len(label_map))
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

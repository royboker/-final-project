"""
Model loader for document analysis inference.
Supports document type classification (ViT-Tiny, ResNet18),
binary forgery detection (ViT-Small), and fraud type classification (ViT-Small).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image
import timm
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torchvision.models import resnet18


# ── Label Maps ────────────────────────────────────────────────────────────────

DOC_TYPE_LABELS = {0: "ID Card", 1: "Passport", 2: "Driver License"}
BINARY_LABELS = {0: "Real", 1: "Fake"}
FRAUD_TYPE_LABELS = {0: "face_morphing", 1: "face_replacement"}

# Keep old name for backward compat
LABEL_MAP = DOC_TYPE_LABELS


# ── Model Architectures ──────────────────────────────────────────────────────

class ViTTinyClassifier(nn.Module):
    """ViT-Tiny for document type classification (3 classes)."""
    def __init__(self, num_classes=3, dropout=0.2):
        super().__init__()
        self.vit = timm.create_model("vit_tiny_patch16_224", pretrained=False, num_classes=0)
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(self.vit.embed_dim, num_classes),
        )

    def forward(self, x):
        return self.head(self.vit(x))


class ResNet18Classifier(nn.Module):
    """ResNet18 for document type classification (3 classes)."""
    def __init__(self, num_classes=3, dropout=0.3):
        super().__init__()
        self.backbone = resnet18(weights=None)
        feat_dim = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(feat_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)


class ViTBinaryClassifier(nn.Module):
    """ViT-Small for binary forgery detection (Real vs Fake)."""
    def __init__(self, model_name="vit_small_patch16_224", num_classes=2, dropout=0.1):
        super().__init__()
        self.vit = timm.create_model(model_name, pretrained=False, num_classes=0)
        num_features = self.vit.embed_dim
        self.classifier = nn.Sequential(
            nn.LayerNorm(num_features),
            nn.Linear(num_features, num_features // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(num_features // 2, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.vit(x))


class ViTFraudTypeClassifier(nn.Module):
    """ViT-Small for fraud type classification (Morphing vs Replacement)."""
    def __init__(self, model_name="vit_small_patch16_224", num_classes=2, dropout=0.1):
        super().__init__()
        self.vit = timm.create_model(model_name, pretrained=False, num_classes=0)
        num_features = self.vit.embed_dim
        self.classifier = nn.Sequential(
            nn.LayerNorm(num_features),
            nn.Linear(num_features, num_features // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(num_features // 2, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.vit(x))


# ── State Dict Loading ───────────────────────────────────────────────────────

def _load_state(model, checkpoint):
    if isinstance(checkpoint, dict):
        key = next((k for k in ("model_state_dict", "state_dict") if k in checkpoint), None)
        state = checkpoint[key] if key else checkpoint
    else:
        state = checkpoint
    model.load_state_dict(state, strict=False)
    return model


# ── Model Loaders ────────────────────────────────────────────────────────────

def load_vit_model(path: str, device="cpu"):
    model = ViTTinyClassifier(num_classes=3)
    ckpt = torch.load(path, map_location=device, weights_only=False)
    _load_state(model, ckpt)
    return model.to(device).eval()


def load_resnet18_model(path: str, device="cpu"):
    model = ResNet18Classifier(num_classes=3)
    ckpt = torch.load(path, map_location=device, weights_only=False)
    _load_state(model, ckpt)
    return model.to(device).eval()


def load_binary_model(path: str, device="cpu"):
    model = ViTBinaryClassifier()
    ckpt = torch.load(path, map_location=device, weights_only=False)
    _load_state(model, ckpt)
    return model.to(device).eval()


def load_fraud_type_model(path: str, device="cpu"):
    model = ViTFraudTypeClassifier()
    ckpt = torch.load(path, map_location=device, weights_only=False)
    _load_state(model, ckpt)
    return model.to(device).eval()


# ── Transforms ───────────────────────────────────────────────────────────────

def get_transforms():
    return A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])


def get_tta_transforms():
    """Test-Time Augmentation: 4 views (base, scale down, scale up, brightness)."""
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


# ── Prediction Functions ─────────────────────────────────────────────────────

def predict_image(model, image: Image.Image, device="cpu", label_map=None) -> dict:
    """Standard single-view prediction."""
    if label_map is None:
        label_map = DOC_TYPE_LABELS

    img_np = np.array(image.convert("RGB"))
    transform = get_transforms()
    tensor = transform(image=img_np)["image"].unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        probs = F.softmax(outputs, dim=1)
        idx = probs.argmax(dim=1).item()
        confidence = probs[0][idx].item()

    return {
        "predicted": label_map[idx],
        "confidence": round(confidence, 4),
        "probabilities": {
            label_map[i]: round(probs[0][i].item(), 4)
            for i in range(len(label_map))
        },
    }


def predict_with_tta(model, image: Image.Image, device="cpu", label_map=None) -> dict:
    """Predict with Test-Time Augmentation (4 views averaged)."""
    if label_map is None:
        label_map = BINARY_LABELS

    img_np = np.array(image.convert("RGB"))
    tta_transforms = get_tta_transforms()
    all_probs = []

    with torch.no_grad():
        for t in tta_transforms:
            tensor = t(image=img_np)["image"].unsqueeze(0).to(device)
            outputs = model(tensor)
            probs = F.softmax(outputs, dim=1)
            all_probs.append(probs.cpu())

    avg_probs = torch.stack(all_probs).mean(dim=0)
    idx = avg_probs.argmax(dim=1).item()
    confidence = avg_probs[0][idx].item()

    return {
        "predicted": label_map[idx],
        "confidence": round(confidence, 4),
        "probabilities": {
            label_map[i]: round(avg_probs[0][i].item(), 4)
            for i in range(len(label_map))
        },
    }


# Keep old predict() for backward compat
def predict(model, image: Image.Image, device="cpu") -> dict:
    return predict_image(model, image, device=device, label_map=DOC_TYPE_LABELS)


def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

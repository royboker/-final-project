"""
Model loader for document classification inference.
Supports ViT-Tiny and ResNet18 models.
"""

import torch
import torch.nn as nn
import numpy as np
from PIL import Image

try:
    import timm
    HAS_TIMM = True
except ImportError:
    HAS_TIMM = False

try:
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    HAS_ALBUMENTATIONS = True
except ImportError:
    HAS_ALBUMENTATIONS = False

from torchvision.models import resnet18

LABEL_MAP = {0: "ID Card", 1: "Passport", 2: "Driver License"}


class ViTTinyClassifier(nn.Module):
    def __init__(self, num_classes=3, dropout=0.2):
        super().__init__()
        if not HAS_TIMM:
            raise ImportError("timm is required. Run: pip install timm")
        self.vit = timm.create_model("vit_tiny_patch16_224", pretrained=False, num_classes=0)
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(self.vit.embed_dim, num_classes),
        )

    def forward(self, x):
        return self.head(self.vit(x))


class ResNet18Classifier(nn.Module):
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


def _load_state(model, checkpoint):
    if isinstance(checkpoint, dict):
        key = next((k for k in ("model_state_dict", "state_dict") if k in checkpoint), None)
        state = checkpoint[key] if key else checkpoint
    else:
        state = checkpoint
    model.load_state_dict(state, strict=False)
    return model


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


def _get_transforms():
    if HAS_ALBUMENTATIONS:
        return A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2(),
        ])
    from torchvision import transforms
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ])


def predict(model, image: Image.Image, device="cpu") -> dict:
    img = image.convert("RGB")
    if HAS_ALBUMENTATIONS:
        t = _get_transforms()
        tensor = t(image=np.array(img))["image"].unsqueeze(0).to(device)
    else:
        t = _get_transforms()
        tensor = t(img).unsqueeze(0).to(device)

    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0]
        idx = probs.argmax().item()

    return {
        "predicted": LABEL_MAP[idx],
        "confidence": round(probs[idx].item(), 4),
        "probabilities": {LABEL_MAP[i]: round(probs[i].item(), 4) for i in range(3)},
    }


def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

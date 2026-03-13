"""
Evaluate the ViT-Small fraud type classifier on out-of-dataset fake samples.
Filters test_samples.json to fakes only (666 samples: 333 morphing + 333 replacement).

Usage: python notebooks/drivers_license_forgery/production/evaluate_fraud_type.py
"""
import json
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from tqdm import tqdm
from sklearn.metrics import classification_report
import timm
import albumentations as A
from albumentations.pytorch import ToTensorV2

PROJECT_ROOT = "/Users/roy-siftt/final-project"
MODEL_PATH = os.path.join(PROJECT_ROOT, "notebooks/drivers_license_forgery/production/vit_fraud_type_15k.pth")
SAMPLES_PATH = os.path.join(PROJECT_ROOT, "notebooks/drivers_license_forgery/experiments/test_samples.json")

FRAUD_TYPE_MAP = {'face_morphing': 0, 'face_replacement': 1}
FRAUD_TYPE_NAMES = {0: 'Face Morphing', 1: 'Face Replacement'}


class ViTFraudTypeClassifier(nn.Module):
    def __init__(self, model_name='vit_small_patch16_224', num_classes=2, pretrained=False, dropout=0.1):
        super().__init__()
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


tta_transforms = [
    A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ]),
    A.Compose([
        A.Resize(224, 224),
        A.Affine(scale=(0.95, 0.95), p=1.0),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ]),
    A.Compose([
        A.Resize(224, 224),
        A.Affine(scale=(1.05, 1.05), p=1.0),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ]),
    A.Compose([
        A.Resize(224, 224),
        A.ColorJitter(brightness=0.1, contrast=0, saturation=0, hue=0, p=1.0),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ]),
]


def predict(image_path, model, device):
    img = Image.open(image_path).convert("RGB")
    img_np = np.array(img)

    model.eval()
    all_probs = []
    with torch.no_grad():
        for t in tta_transforms:
            tensor = t(image=img_np)['image'].unsqueeze(0).to(device)
            probs = F.softmax(model(tensor), dim=1)
            all_probs.append(probs.cpu())

    avg = torch.stack(all_probs).mean(dim=0)
    pred = avg.argmax(dim=1).item()
    return pred, avg[0][pred].item()


def main():
    if torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    print(f"Device: {device}")

    # Load model
    model = ViTFraudTypeClassifier(pretrained=False).to(device)
    state = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    print(f"Model loaded: {MODEL_PATH}")

    # Load samples — fakes only
    with open(SAMPLES_PATH) as f:
        all_samples = json.load(f)
    samples = [s for s in all_samples if s['is_fake'] == 1]
    print(f"Fake samples: {len(samples)} (from {len(all_samples)} total)")
    print(f"  face_morphing: {sum(1 for s in samples if s['fraud_type'] == 'face_morphing')}")
    print(f"  face_replacement: {sum(1 for s in samples if s['fraud_type'] == 'face_replacement')}")

    # Run predictions
    true_labels, pred_labels, details = [], [], []
    skipped = 0

    for s in tqdm(samples, desc="Evaluating"):
        img_path = os.path.join(PROJECT_ROOT, s['path'])
        if not os.path.exists(img_path):
            skipped += 1
            continue

        true_idx = FRAUD_TYPE_MAP[s['fraud_type']]
        pred_idx, confidence = predict(img_path, model, device)

        true_labels.append(true_idx)
        pred_labels.append(pred_idx)
        details.append({
            'path': s['path'],
            'country': s['country'],
            'fraud_type': s['fraud_type'],
            'true': FRAUD_TYPE_NAMES[true_idx],
            'pred': FRAUD_TYPE_NAMES[pred_idx],
            'confidence': confidence,
            'correct': pred_idx == true_idx
        })

    if skipped:
        print(f"Skipped {skipped} (file not found)")

    # Results
    correct = sum(d['correct'] for d in details)
    total = len(details)
    accuracy = correct / total

    print("\n" + "=" * 60)
    print("OUT-OF-DATASET FRAUD TYPE RESULTS - 15K MODEL")
    print("=" * 60)
    print(f"\nOverall Accuracy: {accuracy:.4f} ({correct}/{total})")

    # Per fraud type
    print(f"\nPer Fraud Type:")
    for ftype in ['face_morphing', 'face_replacement']:
        subset = [d for d in details if d['fraud_type'] == ftype]
        acc = sum(d['correct'] for d in subset) / len(subset)
        avg_conf = sum(d['confidence'] for d in subset) / len(subset)
        print(f"  {ftype:20s}: {acc:.4f} ({sum(d['correct'] for d in subset)}/{len(subset)}) avg conf: {avg_conf:.4f}")

    # Per country
    print(f"\nPer Country:")
    for country in sorted(set(d['country'] for d in details)):
        subset = [d for d in details if d['country'] == country]
        acc = sum(d['correct'] for d in subset) / len(subset)
        print(f"  {country}: {acc:.4f} ({sum(d['correct'] for d in subset)}/{len(subset)})")

    # Classification report
    print(f"\n{'=' * 60}")
    print(classification_report(true_labels, pred_labels, target_names=['Face Morphing', 'Face Replacement']))

    # Comparison
    print(f"{'=' * 60}")
    print("COMPARISON WITH OLD MULTI-TASK MODEL")
    print(f"{'=' * 60}")
    print(f"  Old multi-task out-of-dataset: 65.3%")
    print(f"  This model out-of-dataset:     {accuracy*100:.1f}%")
    print(f"  Change:                        {(accuracy - 0.653)*100:+.1f}%")

    # Worst mistakes
    wrong = sorted([d for d in details if not d['correct']], key=lambda x: -x['confidence'])
    if wrong:
        print(f"\nTop 10 most confident WRONG predictions:")
        print("-" * 80)
        for d in wrong[:10]:
            fname = d['path'].split('/')[-1]
            print(f"  {d['country']} | true={d['true']:20s} pred={d['pred']:20s} | conf={d['confidence']*100:.1f}% | {fname}")


if __name__ == "__main__":
    main()

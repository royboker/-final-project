"""
Evaluate the improved ViT-Small binary model (trained on 15K dataset) on 999 out-of-dataset samples.
Usage: python notebooks/drivers_license_forgery/vit_15k/evaluate_outsource.py
"""
import json
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from tqdm import tqdm
from sklearn.metrics import confusion_matrix, classification_report
import timm
import albumentations as A
from albumentations.pytorch import ToTensorV2

PROJECT_ROOT = "/Users/roy-siftt/final-project"
MODEL_PATH = os.path.join(PROJECT_ROOT, "notebooks/drivers_license_forgery/vit_15k/vit_binary_improved_15k.pth")
SAMPLES_PATH = os.path.join(PROJECT_ROOT, "notebooks/drivers_license_forgery/vit/test_samples.json")

# ============================================
# Model definition (must match training)
# ============================================
class ViTBinaryClassifierImproved(nn.Module):
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

# ============================================
# TTA transforms
# ============================================
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
    """Predict with TTA"""
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

# ============================================
# Main
# ============================================
def main():
    # Device
    if torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    print(f"Device: {device}")

    # Load model
    model = ViTBinaryClassifierImproved(pretrained=False).to(device)
    state = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    print(f"Model loaded: {MODEL_PATH}")

    # Load samples
    with open(SAMPLES_PATH) as f:
        samples = json.load(f)
    print(f"Samples: {len(samples)}")

    # Run predictions
    true_labels, pred_labels, details = [], [], []
    skipped = 0

    for s in tqdm(samples, desc="Evaluating"):
        img_path = os.path.join(PROJECT_ROOT, s['path'])
        if not os.path.exists(img_path):
            skipped += 1
            continue

        pred_idx, confidence = predict(img_path, model, device)
        true_idx = s['is_fake']
        pred_label = "Fake" if pred_idx == 1 else "Real"
        true_label = s['expected_binary']

        true_labels.append(true_idx)
        pred_labels.append(pred_idx)
        details.append({
            'path': s['path'],
            'country': s['country'],
            'fraud_type': s['fraud_type'],
            'true': true_label,
            'pred': pred_label,
            'confidence': confidence,
            'correct': pred_label == true_label
        })

    if skipped:
        print(f"Skipped {skipped} (file not found)")

    # ============================================
    # Results
    # ============================================
    correct = sum(d['correct'] for d in details)
    total = len(details)
    accuracy = correct / total

    print("\n" + "=" * 60)
    print("OUT-OF-DATASET RESULTS (999 unseen samples) - 15K MODEL")
    print("=" * 60)
    print(f"\nOverall Accuracy: {accuracy:.4f} ({correct}/{total})")

    # Per class
    print(f"\nPer Class:")
    for label in ['Real', 'Fake']:
        subset = [d for d in details if d['true'] == label]
        acc = sum(d['correct'] for d in subset) / len(subset)
        avg_conf = sum(d['confidence'] for d in subset) / len(subset)
        print(f"  {label:5s}: {acc:.4f} ({sum(d['correct'] for d in subset)}/{len(subset)}) avg conf: {avg_conf:.4f}")

    # Per fraud type
    print(f"\nPer Fraud Type:")
    for ftype in ['real', 'face_morphing', 'face_replacement']:
        subset = [d for d in details if d['fraud_type'] == ftype]
        acc = sum(d['correct'] for d in subset) / len(subset)
        print(f"  {ftype:20s}: {acc:.4f} ({sum(d['correct'] for d in subset)}/{len(subset)})")

    # Per country
    print(f"\nPer Country:")
    for country in ['DC', 'AZ', 'WV']:
        subset = [d for d in details if d['country'] == country]
        acc = sum(d['correct'] for d in subset) / len(subset)
        print(f"  {country}: {acc:.4f} ({sum(d['correct'] for d in subset)}/{len(subset)})")

    # Classification report
    print(f"\n{'=' * 60}")
    print(classification_report(true_labels, pred_labels, target_names=['Real', 'Fake']))

    # Comparison with 9,996 model
    print(f"{'=' * 60}")
    print("COMPARISON WITH 9,996 MODEL")
    print(f"{'=' * 60}")
    print(f"  9,996 model out-of-dataset: 90.2%")
    print(f"  15K model out-of-dataset:   {accuracy*100:.1f}%")
    print(f"  Change:                     {(accuracy - 0.902)*100:+.1f}%")

    # Worst mistakes
    wrong = sorted([d for d in details if not d['correct']], key=lambda x: -x['confidence'])
    if wrong:
        print(f"\nTop 10 most confident WRONG predictions:")
        print("-" * 80)
        for d in wrong[:10]:
            fname = d['path'].split('/')[-1]
            print(f"  {d['country']} | {d['fraud_type']:20s} | true={d['true']:4s} pred={d['pred']:4s} | conf={d['confidence']*100:.1f}% | {fname}")

if __name__ == "__main__":
    main()

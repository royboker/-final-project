"""
Evaluate the DiT-Base fraud type classifier on out-of-dataset fake ID card samples.
Filters test_samples.json to fakes only (1998 samples: 999 morphing + 999 replacement).

Usage: python notebooks/id_card_forgery/production/evaluate_fraud_type_dit.py
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
from huggingface_hub import hf_hub_download
import albumentations as A
from albumentations.pytorch import ToTensorV2

PROJECT_ROOT = "/Users/roy-siftt/final-project"
MODEL_PATH = os.path.join(PROJECT_ROOT, "notebooks/id_card_forgery/production/dit_fraud_type_20k.pth")
SAMPLES_PATH = os.path.join(PROJECT_ROOT, "notebooks/id_card_forgery/experiments/test_samples.json")

FRAUD_TYPE_MAP = {'face_morphing': 0, 'face_replacement': 1}
FRAUD_TYPE_NAMES = {0: 'Face Morphing', 1: 'Face Replacement'}


class DiTFraudTypeClassifier(nn.Module):
    def __init__(self, num_classes=2, dropout=0.1):
        super().__init__()
        self.backbone = timm.create_model('vit_base_patch16_224', pretrained=False, num_classes=0, init_values=1e-5)
        num_features = 768
        self.classifier = nn.Sequential(
            nn.LayerNorm(num_features),
            nn.Linear(num_features, num_features // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(num_features // 2, num_classes)
        )

    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features)

    @staticmethod
    def _convert_dit_to_timm(dit_state_dict):
        """Convert HuggingFace DiT/BEiT state dict to timm ViT format."""
        import torch
        new_state = {}
        for key, value in dit_state_dict.items():
            k = key.replace('beit.', '') if key.startswith('beit.') else key
            if k in ('embeddings.mask_token',): continue
            if k.startswith('layernorm.'):
                new_state[k.replace('layernorm.', 'norm.')] = value; continue
            if k.startswith('classifier.') or k.startswith('lm_head.'): continue
            if k == 'embeddings.cls_token':
                new_state['cls_token'] = value; continue
            if k == 'embeddings.position_embeddings':
                new_state['pos_embed'] = value; continue
            if k.startswith('embeddings.patch_embeddings.projection.'):
                new_state[k.replace('embeddings.patch_embeddings.projection.', 'patch_embed.proj.')] = value; continue
            if k.startswith('encoder.layer.'):
                rest = k[len('encoder.layer.'):]
                layer_idx = rest.split('.')[0]
                layer_rest = rest[len(layer_idx) + 1:]
                prefix = f'blocks.{layer_idx}'
                if layer_rest == 'attention.attention.query.weight':
                    new_state[f'{prefix}.attn.q.weight'] = value; continue
                if layer_rest == 'attention.attention.key.weight':
                    new_state[f'{prefix}.attn.k.weight'] = value; continue
                if layer_rest == 'attention.attention.value.weight':
                    new_state[f'{prefix}.attn.v.weight'] = value; continue
                if layer_rest == 'attention.attention.query.bias':
                    new_state[f'{prefix}.attn.q.bias'] = value; continue
                if layer_rest == 'attention.attention.value.bias':
                    new_state[f'{prefix}.attn.v.bias'] = value; continue
                if layer_rest.startswith('attention.output.dense.'):
                    suffix = layer_rest.split('.')[-1]
                    new_state[f'{prefix}.attn.proj.{suffix}'] = value; continue
                if layer_rest.startswith('intermediate.dense.'):
                    suffix = layer_rest.split('.')[-1]
                    new_state[f'{prefix}.mlp.fc1.{suffix}'] = value; continue
                if layer_rest.startswith('output.dense.'):
                    suffix = layer_rest.split('.')[-1]
                    new_state[f'{prefix}.mlp.fc2.{suffix}'] = value; continue
                if layer_rest.startswith('layernorm_before.'):
                    suffix = layer_rest.split('.')[-1]
                    new_state[f'{prefix}.norm1.{suffix}'] = value; continue
                if layer_rest.startswith('layernorm_after.'):
                    suffix = layer_rest.split('.')[-1]
                    new_state[f'{prefix}.norm2.{suffix}'] = value; continue
                if layer_rest == 'lambda_1':
                    new_state[f'{prefix}.ls1.gamma'] = value; continue
                if layer_rest == 'lambda_2':
                    new_state[f'{prefix}.ls2.gamma'] = value; continue
        fused_state = {}
        q_weight_keys = sorted([k for k in new_state if '.attn.q.weight' in k])
        for q_key in q_weight_keys:
            bp = q_key.replace('.attn.q.weight', '')
            q_w = new_state[f'{bp}.attn.q.weight']
            k_w = new_state[f'{bp}.attn.k.weight']
            v_w = new_state[f'{bp}.attn.v.weight']
            fused_state[f'{bp}.attn.qkv.weight'] = torch.cat([q_w, k_w, v_w], dim=0)
            q_b = new_state[f'{bp}.attn.q.bias']
            v_b = new_state[f'{bp}.attn.v.bias']
            k_b = torch.zeros_like(q_b)
            fused_state[f'{bp}.attn.qkv.bias'] = torch.cat([q_b, k_b, v_b], dim=0)
        skip = ('.attn.q.weight', '.attn.k.weight', '.attn.v.weight', '.attn.q.bias', '.attn.v.bias')
        for k, v in new_state.items():
            if not any(k.endswith(s) for s in skip):
                fused_state[k] = v
        return fused_state

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

    model = DiTFraudTypeClassifier().to(device)
    state = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    print(f"Model loaded: {MODEL_PATH}")

    with open(SAMPLES_PATH) as f:
        all_samples = json.load(f)
    samples = [s for s in all_samples if s['is_fake'] == 1]
    print(f"Fake samples: {len(samples)} (from {len(all_samples)} total)")
    print(f"  face_morphing: {sum(1 for s in samples if s['fraud_type'] == 'face_morphing')}")
    print(f"  face_replacement: {sum(1 for s in samples if s['fraud_type'] == 'face_replacement')}")

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

    correct = sum(d['correct'] for d in details)
    total = len(details)
    accuracy = correct / total

    print("\n" + "=" * 60)
    print("OUT-OF-DATASET FRAUD TYPE RESULTS - DiT-Base 20K ID CARD MODEL")
    print("=" * 60)
    print(f"\nOverall Accuracy: {accuracy:.4f} ({correct}/{total})")

    print(f"\nPer Fraud Type:")
    for ftype in ['face_morphing', 'face_replacement']:
        subset = [d for d in details if d['fraud_type'] == ftype]
        acc = sum(d['correct'] for d in subset) / len(subset)
        avg_conf = sum(d['confidence'] for d in subset) / len(subset)
        print(f"  {ftype:20s}: {acc:.4f} ({sum(d['correct'] for d in subset)}/{len(subset)}) avg conf: {avg_conf:.4f}")

    print(f"\nPer Country:")
    for country in ['RUS', 'SVK', 'NV']:
        subset = [d for d in details if d['country'] == country]
        acc = sum(d['correct'] for d in subset) / len(subset)
        print(f"  {country}: {acc:.4f} ({sum(d['correct'] for d in subset)}/{len(subset)})")

    print(f"\n{'=' * 60}")
    print(classification_report(true_labels, pred_labels, target_names=['Face Morphing', 'Face Replacement']))

    wrong = sorted([d for d in details if not d['correct']], key=lambda x: -x['confidence'])
    if wrong:
        print(f"\nTop 10 most confident WRONG predictions:")
        print("-" * 80)
        for d in wrong[:10]:
            fname = d['path'].split('/')[-1]
            print(f"  {d['country']} | true={d['true']:20s} pred={d['pred']:20s} | conf={d['confidence']*100:.1f}% | {fname}")


if __name__ == "__main__":
    main()

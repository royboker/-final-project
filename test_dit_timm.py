"""Test: Load actual DiT-Base weights into timm BEiT model."""
import torch
import timm
from huggingface_hub import hf_hub_download

# Step 1: Download DiT weights (no transformers needed)
print("Downloading DiT-Base weights...")
weights_path = hf_hub_download(repo_id="microsoft/dit-base", filename="pytorch_model.bin")
print(f"Downloaded to: {weights_path}")

# Step 2: Load the weights
dit_state = torch.load(weights_path, map_location="cpu", weights_only=True)
print(f"\nDiT keys sample: {list(dit_state.keys())[:5]}")

# Step 3: Create timm BEiT model
model = timm.create_model('beit_base_patch16_224', pretrained=False, num_classes=0)
timm_state = model.state_dict()
print(f"timm keys sample: {list(timm_state.keys())[:5]}")

# Step 4: Build key mapping from HF DiT -> timm BEiT
def convert_dit_to_timm(dit_state_dict):
    """Convert HuggingFace DiT/BEiT state dict to timm BEiT format."""
    new_state = {}

    for key, value in dit_state_dict.items():
        # Strip 'beit.' prefix
        k = key.replace('beit.', '') if key.startswith('beit.') else key

        # Skip keys we don't need
        if k in ('embeddings.mask_token',):
            continue

        # Final layer norm
        if k.startswith('layernorm.'):
            new_state[k.replace('layernorm.', 'fc_norm.')] = value
            continue

        # Skip classifier head (we add our own)
        if k.startswith('classifier.') or k.startswith('lm_head.'):
            continue

        # Embeddings
        if k == 'embeddings.cls_token':
            new_state['cls_token'] = value
            continue
        if k == 'embeddings.position_embeddings':
            # DiT uses absolute pos embeds; timm BEiT doesn't have this key
            # We'll skip it - timm BEiT uses relative position bias instead
            continue
        if k.startswith('embeddings.patch_embeddings.projection.'):
            new_state[k.replace('embeddings.patch_embeddings.projection.', 'patch_embed.proj.')] = value
            continue

        # Encoder layers
        if k.startswith('encoder.layer.'):
            rest = k[len('encoder.layer.'):]
            layer_idx = rest.split('.')[0]
            layer_rest = rest[len(layer_idx) + 1:]
            prefix = f'blocks.{layer_idx}'

            # Q weight -> store temporarily for fusion
            if layer_rest == 'attention.attention.query.weight':
                new_state[f'{prefix}.attn.q.weight'] = value
                continue
            if layer_rest == 'attention.attention.key.weight':
                new_state[f'{prefix}.attn.k.weight'] = value
                continue
            if layer_rest == 'attention.attention.value.weight':
                new_state[f'{prefix}.attn.v.weight'] = value
                continue

            # Q and V biases -> timm stores these separately as q_bias, v_bias
            if layer_rest == 'attention.attention.query.bias':
                new_state[f'{prefix}.attn.q_bias'] = value
                continue
            if layer_rest == 'attention.attention.value.bias':
                new_state[f'{prefix}.attn.v_bias'] = value
                continue

            # Attention output projection
            if layer_rest.startswith('attention.output.dense.'):
                suffix = layer_rest.split('.')[-1]
                new_state[f'{prefix}.attn.proj.{suffix}'] = value
                continue

            # MLP
            if layer_rest.startswith('intermediate.dense.'):
                suffix = layer_rest.split('.')[-1]
                new_state[f'{prefix}.mlp.fc1.{suffix}'] = value
                continue
            if layer_rest.startswith('output.dense.'):
                suffix = layer_rest.split('.')[-1]
                new_state[f'{prefix}.mlp.fc2.{suffix}'] = value
                continue

            # Layer norms
            if layer_rest.startswith('layernorm_before.'):
                suffix = layer_rest.split('.')[-1]
                new_state[f'{prefix}.norm1.{suffix}'] = value
                continue
            if layer_rest.startswith('layernorm_after.'):
                suffix = layer_rest.split('.')[-1]
                new_state[f'{prefix}.norm2.{suffix}'] = value
                continue

            # Layer scale
            if layer_rest == 'lambda_1':
                new_state[f'{prefix}.gamma_1'] = value
                continue
            if layer_rest == 'lambda_2':
                new_state[f'{prefix}.gamma_2'] = value
                continue

    # Fuse Q, K, V weights into qkv.weight
    fused_state = {}
    q_weight_keys = sorted([k for k in new_state if '.attn.q.weight' in k])
    for q_w_key in q_weight_keys:
        block_prefix = q_w_key.replace('.attn.q.weight', '')
        q_w = new_state[f'{block_prefix}.attn.q.weight']
        k_w = new_state[f'{block_prefix}.attn.k.weight']
        v_w = new_state[f'{block_prefix}.attn.v.weight']
        fused_state[f'{block_prefix}.attn.qkv.weight'] = torch.cat([q_w, k_w, v_w], dim=0)

    # Add all non-temporary keys
    for k, v in new_state.items():
        if '.attn.q.weight' not in k and '.attn.k.weight' not in k and '.attn.v.weight' not in k:
            fused_state[k] = v

    return fused_state

# Convert
timm_dit_state = convert_dit_to_timm(dit_state)

# Check alignment
timm_keys = set(timm_state.keys())
converted_keys = set(timm_dit_state.keys())

matched = timm_keys & converted_keys
missing_in_dit = timm_keys - converted_keys
extra_in_dit = converted_keys - timm_keys

print(f"\n--- Results ---")
print(f"timm model keys: {len(timm_keys)}")
print(f"Converted DiT keys: {len(converted_keys)}")
print(f"Matched: {len(matched)}")
print(f"Missing from DiT: {len(missing_in_dit)}")
if missing_in_dit:
    print(f"  {sorted(missing_in_dit)}")
print(f"Extra in DiT: {len(extra_in_dit)}")
if extra_in_dit:
    print(f"  {sorted(extra_in_dit)}")

# Load
result = model.load_state_dict(timm_dit_state, strict=False)
print(f"\nMissing keys: {len(result.missing_keys)}")
if result.missing_keys:
    # Only show unique suffixes
    suffixes = set(k.split('.')[-1] for k in result.missing_keys)
    print(f"  Types: {suffixes}")
print(f"Unexpected keys: {result.unexpected_keys}")

# Quick shape test
dummy = torch.randn(1, 3, 224, 224)
with torch.no_grad():
    out = model(dummy)
print(f"\nOutput shape: {out.shape}")
print("SUCCESS! DiT weights loaded into timm BEiT model.")

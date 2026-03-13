import os
import random
import json
import pandas as pd

# Set random seed for reproducibility
random.seed(42)

# Target number of test samples
TARGET_SAMPLES = 1000

# Load training dataset to exclude overlapping files
train_df_path = 'notebooks/drivers_license_forgery/vit/data/dataset.csv'
if os.path.exists(train_df_path):
    train_df = pd.read_csv(train_df_path)
    # Get set of original filenames used in training
    training_filenames = set(train_df['original_filename'].dropna().unique())
    print(f"✓ Loaded training dataset: {len(training_filenames)} unique filenames to exclude")
else:
    print("⚠️  Warning: Training dataset not found. Will not exclude any files.")
    training_filenames = set()

# Countries and their paths
countries = {
    'WV': 'datasets/idnet/WV/WV',
    'DC': 'datasets/idnet/DC',
    'AZ': 'datasets/idnet/AZ'
}

# Collect samples (excluding those in training set)
samples = []

# Calculate target per category (aim for balanced distribution)
# Target: ~333 Real, ~333 Face Morphing, ~334 Face Replacement
# Per country: ~111 Real, ~111 Morphing, ~111 Replacement
target_per_category_per_country = TARGET_SAMPLES // (3 * len(countries))  # ~111 per category per country

for country_code, base_path in countries.items():
    # Real images
    pos_path = os.path.join(base_path, 'positive')
    if os.path.exists(pos_path):
        pos_files = [f for f in os.listdir(pos_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Filter out files that are in training set
        pos_files_filtered = [f for f in pos_files if f not in training_filenames]
        pos_files = [os.path.join(pos_path, f) for f in pos_files_filtered]
        if len(pos_files) > 0:
            # Take as many as available, up to target
            num_to_select = min(target_per_category_per_country, len(pos_files))
            selected = random.sample(pos_files, num_to_select)
            for f in selected:
                samples.append({
                    'path': f,
                    'country': country_code,
                    'is_fake': 0,
                    'fraud_type': 'real',
                    'expected_binary': 'Real',
                    'expected_fraud_type': 'N/A'
                })
    
    # Face Morphing
    morph_path = os.path.join(base_path, 'fraud2_face_morphing')
    if os.path.exists(morph_path):
        morph_files = [f for f in os.listdir(morph_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Filter out files that are in training set
        morph_files_filtered = [f for f in morph_files if f not in training_filenames]
        morph_files = [os.path.join(morph_path, f) for f in morph_files_filtered]
        if len(morph_files) > 0:
            # Take as many as available, up to target
            num_to_select = min(target_per_category_per_country, len(morph_files))
            selected = random.sample(morph_files, num_to_select)
            for f in selected:
                samples.append({
                    'path': f,
                    'country': country_code,
                    'is_fake': 1,
                    'fraud_type': 'face_morphing',
                    'expected_binary': 'Fake',
                    'expected_fraud_type': 'Face Morphing'
                })
    
    # Face Replacement
    rep_path = os.path.join(base_path, 'fraud3_face_replacement')
    if os.path.exists(rep_path):
        rep_files = [f for f in os.listdir(rep_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Filter out files that are in training set
        rep_files_filtered = [f for f in rep_files if f not in training_filenames]
        rep_files = [os.path.join(rep_path, f) for f in rep_files_filtered]
        if len(rep_files) > 0:
            # Take as many as available, up to target
            num_to_select = min(target_per_category_per_country, len(rep_files))
            selected = random.sample(rep_files, num_to_select)
            for f in selected:
                samples.append({
                    'path': f,
                    'country': country_code,
                    'is_fake': 1,
                    'fraud_type': 'face_replacement',
                    'expected_binary': 'Fake',
                    'expected_fraud_type': 'Face Replacement'
                })

# Shuffle and take up to TARGET_SAMPLES
random.shuffle(samples)
samples = samples[:TARGET_SAMPLES]

# Save to JSON
output_path = 'notebooks/drivers_license_forgery/vit/test_samples.json'
with open(output_path, 'w') as f:
    json.dump(samples, f, indent=2)

print(f'\n✓ Collected {len(samples)} samples (excluding training set)')
print(f'  Real: {sum(1 for s in samples if s["is_fake"] == 0)}')
print(f'  Fake: {sum(1 for s in samples if s["is_fake"] == 1)}')
print(f'  Face Morphing: {sum(1 for s in samples if s["fraud_type"] == "face_morphing")}')
print(f'  Face Replacement: {sum(1 for s in samples if s["fraud_type"] == "face_replacement")}')
print(f'  WV: {sum(1 for s in samples if s["country"] == "WV")}')
print(f'  DC: {sum(1 for s in samples if s["country"] == "DC")}')
print(f'  AZ: {sum(1 for s in samples if s["country"] == "AZ")}')

# Verify no overlap
if training_filenames:
    test_filenames = {os.path.basename(s['path']) for s in samples}
    overlap = test_filenames & training_filenames
    if overlap:
        print(f'\n⚠️  WARNING: {len(overlap)} files still overlap with training set!')
    else:
        print(f'\n✅ Verified: No overlap with training set ({len(test_filenames)} test files, {len(training_filenames)} training files)')

print(f'\n✓ Saved to: {output_path}')


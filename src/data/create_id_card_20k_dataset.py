"""
Create a 20,000-image ID card dataset for binary forgery detection.
Countries: RUS (Russia), SVK (Slovakia), NV (Nevada)
3,333 subjects per country → 10,000 subjects → 20,000 images (10K real + 10K fake).

Also creates test_samples.json (~999 out-of-dataset eval samples) BEFORE building
the training set, so those subjects are fully excluded.

Output: datasets/id_card_20k/
  - images/ (20,000 PNG files)
  - dataset.csv (with is_fake, fraud_type, original_id, source_country columns)
"""
import os
import shutil
import json
import pandas as pd
import random
from tqdm import tqdm
import re

# Settings
TARGET_COUNTRIES = ['RUS', 'SVK', 'NV']
ROOT_DIR = 'datasets/idnet'
OUTPUT_DIR = 'datasets/id_card_20k'
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')

# 20,000 images = 10,000 subjects = 3,333 per country (last gets 3,334)
TARGET_SUBJECTS_PER_COUNTRY = 3333
# Out-of-dataset eval: 333 subjects per country × 3 images = 999
TEST_SUBJECTS_PER_COUNTRY = 333

TEST_SAMPLES_PATH = 'notebooks/id_card_forgery/experiments/test_samples.json'

RANDOM_SEED = 42


def get_folders(country_path, country_code):
    """Handle both flat (NV/positive/) and nested (RUS/RUS/positive/) folder layouts."""
    if os.path.exists(os.path.join(country_path, 'positive')):
        return country_path
    nested = os.path.join(country_path, country_code)
    if os.path.exists(os.path.join(nested, 'positive')):
        return nested
    return None


def extract_pure_id(filename):
    """Extract numeric ID from IDNet filename."""
    match = re.search(r'generated\.photos(?:_v3)?_([0-9]+)', filename)
    return match.group(1) if match else filename


def build_subject_pool(country, base_path):
    """Build list of subjects that have real + morphing + replacement images."""
    pos_dir = os.path.join(base_path, 'positive')
    morph_dir = os.path.join(base_path, 'fraud2_face_morphing')
    rep_dir = os.path.join(base_path, 'fraud3_face_replacement')

    def list_files(d):
        return {f for f in os.listdir(d) if f.lower().endswith(('.png', '.jpg'))}

    pos_files = list_files(pos_dir)
    morph_files = list_files(morph_dir)
    rep_files = list_files(rep_dir)

    candidates = {}
    for fname in pos_files:
        if fname in morph_files and fname in rep_files:
            pid = extract_pure_id(fname)
            candidates[pid] = fname

    return candidates


def create_test_samples():
    """Create out-of-dataset evaluation samples (~999) before building training set."""
    print("=" * 60)
    print("STEP 1: Creating out-of-dataset evaluation samples")
    print("=" * 60)

    test_samples = []

    for country in TARGET_COUNTRIES:
        country_path = os.path.join(ROOT_DIR, country)
        base_path = get_folders(country_path, country)
        if not base_path:
            print(f"Skipping {country}: folders not found")
            continue

        candidates = build_subject_pool(country, base_path)
        print(f"  {country}: {len(candidates)} valid subjects")

        # Select test subjects
        candidate_ids = sorted(candidates.keys())
        random.seed(RANDOM_SEED + hash(country))
        random.shuffle(candidate_ids)
        test_ids = candidate_ids[:TEST_SUBJECTS_PER_COUNTRY]

        pos_dir = os.path.join(base_path, 'positive')
        morph_dir = os.path.join(base_path, 'fraud2_face_morphing')
        rep_dir = os.path.join(base_path, 'fraud3_face_replacement')

        for pid in test_ids:
            fname = candidates[pid]
            # Real
            test_samples.append({
                'path': os.path.join(pos_dir, fname),
                'country': country,
                'is_fake': 0,
                'fraud_type': 'real',
                'expected_binary': 'Real',
                'expected_fraud_type': 'N/A'
            })
            # Face morphing
            test_samples.append({
                'path': os.path.join(morph_dir, fname),
                'country': country,
                'is_fake': 1,
                'fraud_type': 'face_morphing',
                'expected_binary': 'Fake',
                'expected_fraud_type': 'Face Morphing'
            })
            # Face replacement
            test_samples.append({
                'path': os.path.join(rep_dir, fname),
                'country': country,
                'is_fake': 1,
                'fraud_type': 'face_replacement',
                'expected_binary': 'Fake',
                'expected_fraud_type': 'Face Replacement'
            })

    # Save
    os.makedirs(os.path.dirname(TEST_SAMPLES_PATH), exist_ok=True)
    with open(TEST_SAMPLES_PATH, 'w') as f:
        json.dump(test_samples, f, indent=2)

    print(f"\n  Total test samples: {len(test_samples)}")
    print(f"  Saved to: {TEST_SAMPLES_PATH}")

    # Return excluded IDs
    excluded_ids = set()
    for s in test_samples:
        fname = os.path.basename(s['path'])
        pid = extract_pure_id(fname)
        excluded_ids.add(f"{s['country']}_{pid}")

    return excluded_ids


def create_dataset():
    # Step 1: Create test samples and get excluded IDs
    excluded_ids = create_test_samples()
    print(f"\n  Excluding {len(excluded_ids)} subject IDs from training data")

    # Step 2: Build the 20K training dataset
    print("\n" + "=" * 60)
    print("STEP 2: Creating 20K training dataset")
    print("=" * 60)

    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning existing directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(IMAGES_DIR)

    csv_rows = []

    total_target = TARGET_SUBJECTS_PER_COUNTRY * len(TARGET_COUNTRIES)
    print(f"\nTarget: {TARGET_SUBJECTS_PER_COUNTRY} subjects per country = {total_target * 2} total images")

    for idx, country in enumerate(TARGET_COUNTRIES):
        print(f"\n--- Processing {country} ---")
        country_path = os.path.join(ROOT_DIR, country)
        base_path = get_folders(country_path, country)

        if not base_path:
            print(f"Skipping {country}: folders not found")
            continue

        candidates = build_subject_pool(country, base_path)

        # Remove excluded subjects
        filtered = {}
        for pid, fname in candidates.items():
            unique_id = f"{country}_{pid}"
            if unique_id not in excluded_ids:
                filtered[pid] = fname

        print(f"  Available candidates (excluding eval set): {len(filtered)}")

        # Select subjects — last country gets +1 if needed to reach 10,000 total
        target = TARGET_SUBJECTS_PER_COUNTRY
        if idx == len(TARGET_COUNTRIES) - 1:
            target = TARGET_SUBJECTS_PER_COUNTRY + 1  # 3,334 for last country

        candidate_ids = sorted(filtered.keys())
        random.seed(RANDOM_SEED)
        random.shuffle(candidate_ids)

        if len(candidate_ids) > target:
            selected_ids = candidate_ids[:target]
        else:
            selected_ids = candidate_ids
            print(f"  Warning: only {len(selected_ids)} available (target was {target})")

        # 50/50 split for fake types (morphing/replacement)
        mid_point = len(selected_ids) // 2

        pos_dir = os.path.join(base_path, 'positive')
        morph_dir = os.path.join(base_path, 'fraud2_face_morphing')
        rep_dir = os.path.join(base_path, 'fraud3_face_replacement')

        print(f"  Processing {len(selected_ids)} subjects...")
        for i, pid in enumerate(tqdm(selected_ids)):
            fname = filtered[pid]
            unique_subject_id = f"{country}_{pid}"

            # Real image
            new_real_name = f"real_{country}_{pid}.png"
            shutil.copy2(os.path.join(pos_dir, fname), os.path.join(IMAGES_DIR, new_real_name))

            csv_rows.append({
                'image_path': os.path.join('images', new_real_name),
                'label': 0,
                'label_name': 'real',
                'is_fake': 0,
                'fraud_type': '',
                'original_id': unique_subject_id,
                'source_country': country,
                'original_filename': fname
            })

            # Fake image (50/50 morphing/replacement)
            if i < mid_point:
                src_fake = os.path.join(morph_dir, fname)
                lbl, lbl_name, fraud_type = 1, 'face_morphing', 'face_morphing'
            else:
                src_fake = os.path.join(rep_dir, fname)
                lbl, lbl_name, fraud_type = 2, 'face_replacement', 'face_replacement'

            new_fake_name = f"{lbl_name}_{country}_{pid}.png"
            shutil.copy2(src_fake, os.path.join(IMAGES_DIR, new_fake_name))

            csv_rows.append({
                'image_path': os.path.join('images', new_fake_name),
                'label': lbl,
                'label_name': lbl_name,
                'is_fake': 1,
                'fraud_type': fraud_type,
                'original_id': unique_subject_id,
                'source_country': country,
                'original_filename': fname
            })

    # Save CSV
    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(OUTPUT_DIR, 'dataset.csv')
    df.to_csv(csv_path, index=False)

    # Statistics
    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"Total images: {len(df)}")
    print(f"Unique subjects: {df['original_id'].nunique()}")

    print(f"\nBinary Distribution (is_fake):")
    for val, count in df['is_fake'].value_counts().sort_index().items():
        print(f"  {val} ({'Real' if val == 0 else 'Fake'}): {count} ({count/len(df)*100:.1f}%)")

    print(f"\nFraud Type Distribution (fakes only):")
    fakes = df[df['is_fake'] == 1]
    for val, count in fakes['fraud_type'].value_counts().items():
        print(f"  {val}: {count} ({count/len(fakes)*100:.1f}%)")

    print(f"\nCountry Distribution:")
    for val, count in df['source_country'].value_counts().sort_index().items():
        print(f"  {val}: {count} ({count/len(df)*100:.1f}%)")

    # Verify pairing
    issues = 0
    for uid, group in df.groupby('original_id'):
        reals = (group['is_fake'] == 0).sum()
        fakes_count = (group['is_fake'] == 1).sum()
        if reals != 1 or fakes_count != 1:
            issues += 1
    print(f"\nSubject pairing check: {issues} issues {'PASS' if issues == 0 else 'FAIL'}")
    print(f"\nDataset saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    create_dataset()

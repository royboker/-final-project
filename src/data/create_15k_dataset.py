"""
Create a 15,000-image driver's license dataset for binary forgery detection.
Same structure as the 9,996 dataset but with 2,500 subjects per country.

Output: datasets/drivers_license_15k/
  - images/ (15,000 PNG files)
  - dataset.csv (with is_fake, fraud_type, original_id, source_country columns)
"""
import os
import shutil
import pandas as pd
import random
from tqdm import tqdm
import re

# Settings
TARGET_COUNTRIES = ['WV', 'DC', 'AZ']
ROOT_DIR = 'datasets/idnet'
OUTPUT_DIR = 'datasets/drivers_license_15k'
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')

# 15,000 images = 7,500 subjects = 2,500 per country
TARGET_REAL_PER_COUNTRY = 2500


def get_folders(country_path, country_code):
    if os.path.exists(os.path.join(country_path, 'positive')):
        return country_path
    nested = os.path.join(country_path, country_code)
    if os.path.exists(os.path.join(nested, 'positive')):
        return nested
    return None


def extract_pure_id(filename):
    match = re.search(r'generated\.photos(?:_v3)?_([0-9]+)', filename)
    return match.group(1) if match else filename


def create_dataset():
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning existing directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(IMAGES_DIR)

    csv_rows = []

    # Load existing 9,996 dataset IDs to ensure we INCLUDE them (superset)
    existing_csv = 'notebooks/drivers_license_forgery/vit/data/dataset.csv'
    existing_ids = set()
    if os.path.exists(existing_csv):
        existing_df = pd.read_csv(existing_csv)
        existing_ids = set(existing_df['original_id'].unique())
        print(f"Existing 9,996 dataset has {len(existing_ids)} subject IDs")

    # Load test_samples.json IDs to EXCLUDE them (keep them for out-of-dataset eval)
    test_samples_path = 'notebooks/drivers_license_forgery/vit/test_samples.json'
    excluded_ids = set()
    if os.path.exists(test_samples_path):
        import json
        with open(test_samples_path) as f:
            test_samples = json.load(f)
        for s in test_samples:
            fname = s['path'].split('/')[-1]
            pid = extract_pure_id(fname)
            country = s['country']
            excluded_ids.add(f"{country}_{pid}")
        print(f"Excluding {len(excluded_ids)} subject IDs (reserved for out-of-dataset eval)")

    print(f"\nTarget: {TARGET_REAL_PER_COUNTRY} subjects per country = {TARGET_REAL_PER_COUNTRY * 3 * 2} total images")

    for country in TARGET_COUNTRIES:
        print(f"\n--- Processing {country} ---")
        country_path = os.path.join(ROOT_DIR, country)
        base_path = get_folders(country_path, country)

        if not base_path:
            print(f"Skipping {country}: folders not found")
            continue

        pos_dir = os.path.join(base_path, 'positive')
        morph_dir = os.path.join(base_path, 'fraud2_face_morphing')
        rep_dir = os.path.join(base_path, 'fraud3_face_replacement')

        def list_files(d):
            return {f: os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(('.png', '.jpg'))}

        pos_files_map = list_files(pos_dir)
        morph_files_map = list_files(morph_dir)
        rep_files_map = list_files(rep_dir)

        # Build candidates (must have real + morph + replacement)
        candidates = {}
        for fname_real in pos_files_map:
            pid = extract_pure_id(fname_real)
            if fname_real in morph_files_map and fname_real in rep_files_map:
                unique_id = f"{country}_{pid}"
                # Exclude test_samples subjects
                if unique_id not in excluded_ids:
                    candidates[pid] = {'real_file': fname_real}

        print(f"  Available candidates (excluding eval set): {len(candidates)}")

        # Select subjects
        candidate_ids = list(candidates.keys())
        random.seed(42)
        random.shuffle(candidate_ids)

        if len(candidate_ids) > TARGET_REAL_PER_COUNTRY:
            selected_ids = candidate_ids[:TARGET_REAL_PER_COUNTRY]
        else:
            selected_ids = candidate_ids
            print(f"  Warning: only {len(selected_ids)} available (target was {TARGET_REAL_PER_COUNTRY})")

        # Split 50/50 for fake types
        mid_point = len(selected_ids) // 2

        print(f"  Processing {len(selected_ids)} subjects...")
        for i, pid in enumerate(tqdm(selected_ids)):
            fname = candidates[pid]['real_file']
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

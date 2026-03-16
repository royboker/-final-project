import os
import shutil
import pandas as pd
import random
from tqdm import tqdm

# Settings
TARGET_COUNTRIES = ['WV', 'DC', 'AZ']
ROOT_DIR = 'datasets/idnet'
OUTPUT_DIR = 'datasets/drivers_license_balanced'
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')

# Classes
CLASSES = {
    'positive': {'label': 0, 'name': 'real'},
    'fraud2_face_morphing': {'label': 1, 'name': 'face_morphing'},
    'fraud3_face_replacement': {'label': 2, 'name': 'face_replacement'}
}

# Target total (approx 10k -> 3333 per class -> 3333 IDs)
TARGET_IDS = 3333

def get_folders(country_path, country_code):
    """Handles the potential nested folder structure (WV/WV vs ALB)"""
    # Check directly under country path
    if os.path.exists(os.path.join(country_path, 'positive')):
        return country_path
    # Check nested
    nested = os.path.join(country_path, country_code)
    if os.path.exists(os.path.join(nested, 'positive')):
        return nested
    return None

def create_balanced_dataset():
    # 1. Clean/Create Output Directory
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning existing directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(IMAGES_DIR)

    # 2. Collect Valid Candidates (IDs that exist in all 3 classes)
    print("Scanning for valid candidates...")
    candidates = [] # List of (country, relative_base_path, filename, id)

    for country in TARGET_COUNTRIES:
        country_path = os.path.join(ROOT_DIR, country)
        base_path = get_folders(country_path, country)
        
        if not base_path:
            print(f"Skipping {country}: folders not found")
            continue
            
        # Get list of files in positive
        pos_dir = os.path.join(base_path, 'positive')
        morph_dir = os.path.join(base_path, 'fraud2_face_morphing')
        rep_dir = os.path.join(base_path, 'fraud3_face_replacement')
        
        # We need files that exist in ALL 3
        pos_files = set(os.listdir(pos_dir))
        morph_files = set(os.listdir(morph_dir))
        rep_files = set(os.listdir(rep_dir))
        
        # Intersection
        valid_files = pos_files.intersection(morph_files).intersection(rep_files)
        valid_files = [f for f in valid_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        print(f"  {country}: Found {len(valid_files)} complete triplets.")
        
        for f in valid_files:
            # Extract ID usually found in generated.photos_v3_XXXXXX.png
            # Just use filename as ID for simplicity since it's unique per person usually
            candidates.append({
                'country': country,
                'base_path': base_path,
                'filename': f
            })

    print(f"Total candidates found: {len(candidates)}")
    
    # 3. Random Sample
    if len(candidates) > TARGET_IDS:
        print(f"Sampling {TARGET_IDS} candidates from {len(candidates)}...")
        random.seed(42)
        selected_candidates = random.sample(candidates, TARGET_IDS)
    else:
        print(f"Using all {len(candidates)} candidates (less than target {TARGET_IDS}).")
        selected_candidates = candidates

    # 4. Process and Copy
    csv_rows = []
    
    print("Copying images and generating metadata...")
    for item in tqdm(selected_candidates):
        country = item['country']
        base = item['base_path']
        fname = item['filename']
        
        # Original ID (extract from filename for metadata)
        # Assuming format like generated.photos_v3_0000170.png
        import re
        match = re.search(r'([0-9]+)', fname)
        original_id = match.group(1) if match else fname

        # Process each class for this candidate
        for folder_key, class_info in CLASSES.items():
            src_path = os.path.join(base, folder_key, fname)
            
            # New filename: class_country_filename
            # E.g. real_WV_generated.photos...png
            new_fname = f"{class_info['name']}_{country}_{fname}"
            dst_path = os.path.join(IMAGES_DIR, new_fname)
            
            shutil.copy2(src_path, dst_path)
            
            csv_rows.append({
                'image_path': os.path.join('images', new_fname),
                'label': class_info['label'],
                'label_name': class_info['name'],
                'original_id': original_id,
                'source_country': country,
                'original_filename': fname
            })

    # 5. Save CSV
    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(OUTPUT_DIR, 'dataset.csv')
    df.to_csv(csv_path, index=False)
    
    # 6. Final Checks
    print("\n--- Final Checks ---")
    print(f"Total images: {len(df)}")
    print(f"Class distribution:\n{df['label_name'].value_counts()}")
    
    # Check for duplicates in 'image_path'
    duplicates = df['image_path'].duplicated().sum()
    print(f"Duplicate files in CSV: {duplicates}")
    
    # Check physical file count
    physical_files = len(os.listdir(IMAGES_DIR))
    print(f"Physical files in images/: {physical_files}")
    
    if physical_files != len(df):
        print("WARNING: Mismatch between CSV and physical files!")
    else:
        print("Consistency check: PASSED")

if __name__ == "__main__":
    create_balanced_dataset()


import os
import shutil
import pandas as pd
import random
from tqdm import tqdm
import re

# Settings
TARGET_COUNTRIES = ['WV', 'DC', 'AZ']
ROOT_DIR = 'datasets/idnet'
OUTPUT_DIR = 'datasets/drivers_license_balanced_50_50_country_split'
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')

# Target per country (Total 5000 Real / 3 countries ~= 1666)
TARGET_REAL_PER_COUNTRY = 1666 

def get_folders(country_path, country_code):
    """Handles the potential nested folder structure (WV/WV vs ALB)"""
    if os.path.exists(os.path.join(country_path, 'positive')):
        return country_path
    nested = os.path.join(country_path, country_code)
    if os.path.exists(os.path.join(nested, 'positive')):
        return nested
    return None

def create_balanced_dataset():
    # 1. Setup Directories
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning existing directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(IMAGES_DIR)

    csv_rows = []
    
    print("Processing countries...")
    for country in TARGET_COUNTRIES:
        print(f"\n--- Processing {country} ---")
        country_path = os.path.join(ROOT_DIR, country)
        base_path = get_folders(country_path, country)
        
        if not base_path:
            print(f"Skipping {country}: folders not found")
            continue
            
        # Find candidates (IDs present in all 3 folders)
        pos_dir = os.path.join(base_path, 'positive')
        morph_dir = os.path.join(base_path, 'fraud2_face_morphing')
        rep_dir = os.path.join(base_path, 'fraud3_face_replacement')
        
        pos_files = set(os.listdir(pos_dir))
        morph_files = set(os.listdir(morph_dir))
        rep_files = set(os.listdir(rep_dir))
        
        # Intersection
        valid_files = pos_files.intersection(morph_files).intersection(rep_files)
        valid_files = [f for f in valid_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        print(f"Found {len(valid_files)} valid triplets.")
        
        # Sample candidates
        candidates = list(valid_files)
        if len(candidates) > TARGET_REAL_PER_COUNTRY:
            random.seed(42) # Fixed seed for reproducibility
            selected_candidates = random.sample(candidates, TARGET_REAL_PER_COUNTRY)
        else:
            print(f"Warning: Using all {len(candidates)} candidates (less than target {TARGET_REAL_PER_COUNTRY})")
            selected_candidates = candidates
            
        # Split for Fake types
        mid_point = len(selected_candidates) // 2
        
        print(f"Processing {len(selected_candidates)} candidates for {country}...")
        for i, fname in enumerate(tqdm(selected_candidates)):
            # Extract Original ID
            match = re.search(r'generated\.photos(?:_v3)?_([0-9]+)', fname)
            original_id = match.group(1) if match else fname
            
            # --- 1. Real Image (Everyone gets one) ---
            src_real = os.path.join(pos_dir, fname)
            dst_real_name = f"real_{country}_{fname}"
            shutil.copy2(src_real, os.path.join(IMAGES_DIR, dst_real_name))
            
            csv_rows.append({
                'image_path': os.path.join('images', dst_real_name),
                'label': 0,
                'label_name': 'real',
                'original_id': original_id,
                'source_country': country,
                'original_filename': fname
            })
            
            # --- 2. Fake Image (Split 50/50 between types) ---
            if i < mid_point:
                # Morphing
                src_fake = os.path.join(morph_dir, fname)
                lbl = 1
                lbl_name = 'face_morphing'
            else:
                # Replacement
                src_fake = os.path.join(rep_dir, fname)
                lbl = 2
                lbl_name = 'face_replacement'
                
            dst_fake_name = f"{lbl_name}_{country}_{fname}"
            shutil.copy2(src_fake, os.path.join(IMAGES_DIR, dst_fake_name))
            
            csv_rows.append({
                'image_path': os.path.join('images', dst_fake_name),
                'label': lbl,
                'label_name': lbl_name,
                'original_id': original_id,
                'source_country': country,
                'original_filename': fname
            })

    # Save CSV
    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(OUTPUT_DIR, 'dataset.csv')
    df.to_csv(csv_path, index=False)
    
    print("\n--- Final Statistics ---")
    print(f"Total Images: {len(df)}")
    print("\nLabel Distribution:")
    print(df['label_name'].value_counts())
    print("\nCountry Distribution:")
    print(df['source_country'].value_counts())
    
    # Check consistency
    print("\nChecking Balance:")
    real_count = len(df[df['label_name'] == 'real'])
    fake_count = len(df[df['label_name'] != 'real'])
    print(f"Real: {real_count}")
    print(f"Fake: {fake_count}")
    
    if real_count == fake_count:
        print("✅ Global Real/Fake Balance: PERFECT (50/50)")
    else:
        print(f"⚠️ Global Balance Mismatch! ({real_count} vs {fake_count})")

if __name__ == "__main__":
    create_balanced_dataset()


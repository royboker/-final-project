import os
import shutil
import pandas as pd
import random
from tqdm import tqdm
import re

# Settings
TARGET_COUNTRIES = ['WV', 'DC', 'AZ']
ROOT_DIR = 'datasets/idnet'
OUTPUT_DIR = 'datasets/drivers_license_final'  # Final cleaned name
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')

# Target per country (Total 5000 Real -> ~1666 per country)
TARGET_REAL_PER_COUNTRY = 1666

def get_folders(country_path, country_code):
    if os.path.exists(os.path.join(country_path, 'positive')):
        return country_path
    nested = os.path.join(country_path, country_code)
    if os.path.exists(os.path.join(nested, 'positive')):
        return nested
    return None

def extract_pure_id(filename):
    """
    Extracts the numerical ID from the filename.
    Pattern: generated.photos_v3_XXXXXX.png OR generated.photos_v3_XXXXXX_YYYYYY.png
    We take the FIRST sequence of digits as the primary ID.
    """
    match = re.search(r'generated\.photos(?:_v3)?_([0-9]+)', filename)
    return match.group(1) if match else filename

def create_perfect_dataset():
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
            
        pos_dir = os.path.join(base_path, 'positive')
        morph_dir = os.path.join(base_path, 'fraud2_face_morphing')
        rep_dir = os.path.join(base_path, 'fraud3_face_replacement')
        
        # Helper to list full paths
        def list_files(d):
            return {f: os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(('.png', '.jpg'))}

        pos_files_map = list_files(pos_dir)
        morph_files_map = list_files(morph_dir)
        rep_files_map = list_files(rep_dir)

        # Build Candidate Map by ID
        # candidate_id -> { 'real': file, 'morph': file, 'rep': file }
        candidates = {}
        
        # Iterate over REAL files to find matching Fakes
        for fname_real in pos_files_map:
            pid = extract_pure_id(fname_real)
            
            # Check if this ID exists in both fake folders
            # Note: The filenames might differ slightly (e.g. suffixes), 
            # so we look for files containing this ID.
            
            # Simple check: assuming exact filename match first (most common in IDNet)
            has_morph = fname_real in morph_files_map
            has_rep = fname_real in rep_files_map
            
            if has_morph and has_rep:
                candidates[pid] = {
                    'real_file': fname_real,
                    'morph_file': fname_real,
                    'rep_file': fname_real
                }
        
        print(f"Found {len(candidates)} valid candidate subjects (ID triplets).")
        
        # Sampling
        candidate_ids = list(candidates.keys())
        if len(candidate_ids) > TARGET_REAL_PER_COUNTRY:
            random.seed(42)
            selected_ids = random.sample(candidate_ids, TARGET_REAL_PER_COUNTRY)
        else:
            selected_ids = candidate_ids
            
        # Split for Fake Types
        mid_point = len(selected_ids) // 2
        
        print(f"Processing {len(selected_ids)} subjects...")
        for i, pid in enumerate(tqdm(selected_ids)):
            triplet = candidates[pid]
            fname = triplet['real_file'] # using the filename from the real folder
            
            # IMPORTANT: Unique ID must include Country to avoid cross-country collisions
            unique_subject_id = f"{country}_{pid}"
            
            # --- 1. Real Image ---
            # Rename: real_WV_000170.png
            # Using simple, clean naming
            new_real_name = f"real_{country}_{pid}.png"
            shutil.copy2(os.path.join(pos_dir, fname), os.path.join(IMAGES_DIR, new_real_name))
            
            csv_rows.append({
                'image_path': os.path.join('images', new_real_name),
                'label': 0,
                'label_name': 'real',
                'original_id': unique_subject_id, # Validated Unique ID
                'source_country': country,
                'original_filename': fname
            })
            
            # --- 2. Fake Image (One per subject) ---
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
            
            new_fake_name = f"{lbl_name}_{country}_{pid}.png"
            shutil.copy2(src_fake, os.path.join(IMAGES_DIR, new_fake_name))
            
            csv_rows.append({
                'image_path': os.path.join('images', new_fake_name),
                'label': lbl,
                'label_name': lbl_name,
                'original_id': unique_subject_id,
                'source_country': country,
                'original_filename': fname
            })

    # Save CSV
    df = pd.DataFrame(csv_rows)
    csv_path = os.path.join(OUTPUT_DIR, 'dataset.csv')
    df.to_csv(csv_path, index=False)
    
    print("\n✅ Dataset creation complete.")

if __name__ == "__main__":
    create_perfect_dataset()


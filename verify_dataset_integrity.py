import pandas as pd
import os
import hashlib
from tqdm import tqdm

DATASET_DIR = 'datasets/drivers_license_balanced_50_50_country_split'
CSV_PATH = os.path.join(DATASET_DIR, 'dataset.csv')
IMAGES_DIR = os.path.join(DATASET_DIR, 'images')

def calculate_file_hash(filepath):
    """Calculates MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def verify_dataset():
    print(f"🔍 Verifying dataset at: {DATASET_DIR}")
    
    # 1. Load CSV
    if not os.path.exists(CSV_PATH):
        print("❌ Error: dataset.csv not found!")
        return
    
    df = pd.read_csv(CSV_PATH)
    print(f"✅ CSV loaded. Total rows: {len(df)}")
    
    # 2. Check File Existence & Calculate Hashes
    print("\n📦 Checking file existence and calculating hashes (Duplicate Check)...")
    file_hashes = {} # hash -> list of filenames
    missing_files = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        rel_path = row['image_path']
        # Fix path if needed (remove 'images/' prefix if it exists in CSV but we are joining with IMAGES_DIR which might be wrong logic depending on CSV content)
        # In previous script: image_path was 'images/filename'. 
        # So full path is DATASET_DIR + image_path
        
        full_path = os.path.join(DATASET_DIR, rel_path)
        
        if not os.path.exists(full_path):
            missing_files.append(rel_path)
            continue
            
        # Calc Hash
        f_hash = calculate_file_hash(full_path)
        if f_hash in file_hashes:
            file_hashes[f_hash].append(rel_path)
        else:
            file_hashes[f_hash] = [rel_path]

    if missing_files:
        print(f"❌ Error: {len(missing_files)} files listed in CSV are missing on disk!")
    else:
        print("✅ All files exist on disk.")

    # 3. Check for Duplicate Hashes
    duplicates = {k: v for k, v in file_hashes.items() if len(v) > 1}
    if duplicates:
        print(f"⚠️ Warning: Found {len(duplicates)} duplicate images (identical content)!")
        # Let's inspect a few
        print("Sample duplicates:")
        for k, v in list(duplicates.items())[:5]:
            print(f"  Hash {k}: {v}")
    else:
        print("✅ No duplicate images found (Content-based check passed).")

    # 4. Verify Original <-> Fake Linkage
    print("\n🔗 Verifying Original <-> Fake connections...")
    
    # Group by original_id and country
    groups = df.groupby(['source_country', 'original_id'])
    
    valid_groups = 0
    invalid_groups = 0
    
    for (country, oid), group in groups:
        # Each group must have exactly:
        # 1 Real image
        # 1 Fake image (either Morphing OR Replacement)
        
        real_rows = group[group['label_name'] == 'real']
        fake_rows = group[group['label_name'] != 'real']
        
        is_valid = True
        
        if len(real_rows) != 1:
            print(f"❌ Error for ID {oid} ({country}): Found {len(real_rows)} Real images (Expected 1)")
            is_valid = False
            
        if len(fake_rows) != 1:
            print(f"❌ Error for ID {oid} ({country}): Found {len(fake_rows)} Fake images (Expected 1)")
            is_valid = False
            
        if is_valid:
            valid_groups += 1
        else:
            invalid_groups += 1
            
    if invalid_groups == 0:
        print(f"✅ All {valid_groups} subjects have exactly 1 Real and 1 Fake image.")
    else:
        print(f"❌ Found {invalid_groups} subjects with broken linkage!")

    # 5. Final Balance Check (Recap)
    print("\n⚖️ Final Balance Recap:")
    print(df['label_name'].value_counts())
    print(df['source_country'].value_counts())

if __name__ == "__main__":
    verify_dataset()


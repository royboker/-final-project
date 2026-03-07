import pandas as pd
import os
import hashlib
from tqdm import tqdm

DATASET_DIR = 'datasets/drivers_license_final'
CSV_PATH = os.path.join(DATASET_DIR, 'dataset.csv')
IMAGES_DIR = os.path.join(DATASET_DIR, 'images')

def calculate_file_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def verify_dataset():
    print(f"🔍 Verifying FINAL dataset at: {DATASET_DIR}")
    
    if not os.path.exists(CSV_PATH):
        print("❌ Error: dataset.csv not found!")
        return
    
    df = pd.read_csv(CSV_PATH)
    print(f"✅ CSV loaded. Total rows: {len(df)}")
    
    # 1. Check ID Uniqueness & Grouping
    print("\n🔗 Checking Subject Linkage (One Real, One Fake)...")
    groups = df.groupby('original_id')
    
    invalid_groups = 0
    valid_groups = 0
    
    for oid, group in groups:
        real_count = len(group[group['label_name'] == 'real'])
        fake_count = len(group[group['label_name'] != 'real'])
        
        if real_count != 1 or fake_count != 1:
            print(f"❌ ID {oid}: Real={real_count}, Fake={fake_count}")
            invalid_groups += 1
        else:
            valid_groups += 1
            
    if invalid_groups == 0:
        print(f"✅ PERFECT LINKAGE: All {valid_groups} subjects have exactly 1 Real + 1 Fake.")
    else:
        print(f"❌ BROKEN LINKAGE: {invalid_groups} subjects are invalid.")

    # 2. Check Duplicates (Hash)
    print("\n📦 Checking for physical duplicates (MD5)...")
    file_hashes = {}
    duplicates = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        path = os.path.join(DATASET_DIR, row['image_path'])
        if os.path.exists(path):
            h = calculate_file_hash(path)
            if h in file_hashes:
                duplicates.append((row['image_path'], file_hashes[h]))
            else:
                file_hashes[h] = row['image_path']
                
    if not duplicates:
        print("✅ No duplicate images found.")
    else:
        print(f"⚠️ Found {len(duplicates)} duplicate pairs! (This shouldn't happen now)")

    # 3. Final Balance
    print("\n⚖️ Final Balance Recap:")
    print(df['label_name'].value_counts())
    print(df['source_country'].value_counts())

if __name__ == "__main__":
    verify_dataset()


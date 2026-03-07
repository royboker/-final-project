import pandas as pd
import os
import hashlib
from PIL import Image
from tqdm import tqdm

DATASET_DIR = 'datasets/drivers_license_multi_task'
CSV_PATH = os.path.join(DATASET_DIR, 'dataset.csv')
IMAGES_DIR = os.path.join(DATASET_DIR, 'images')

def calculate_file_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def verify_multi_task_dataset():
    print(f"🔍 Verifying Multi-Task Dataset at: {DATASET_DIR}")
    
    if not os.path.exists(CSV_PATH):
        print("❌ Error: dataset.csv not found!")
        return
    
    df = pd.read_csv(CSV_PATH)
    print(f"✅ CSV loaded. Total rows: {len(df)}")
    
    # 1. Check Column Structure
    print("\n📋 Checking column structure...")
    required_cols = ['image_path', 'label', 'label_name', 'is_fake', 'fraud_type', 'original_id', 'source_country']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
    else:
        print("✅ All required columns present")
    
    # 2. Check Data Consistency
    print("\n🔗 Checking data consistency...")
    
    # Check is_fake values
    invalid_is_fake = df[~df['is_fake'].isin([0, 1])]
    if len(invalid_is_fake) > 0:
        print(f"❌ Found {len(invalid_is_fake)} rows with invalid is_fake values")
    else:
        print("✅ All is_fake values are valid (0 or 1)")
    
    # Check fraud_type consistency
    real_with_fraud_type = df[(df['is_fake'] == 0) & (df['fraud_type'] != '')]
    fake_without_fraud_type = df[(df['is_fake'] == 1) & (df['fraud_type'] == '')]
    
    if len(real_with_fraud_type) > 0:
        print(f"⚠️ Warning: {len(real_with_fraud_type)} Real images have non-empty fraud_type")
    if len(fake_without_fraud_type) > 0:
        print(f"❌ Error: {len(fake_without_fraud_type)} Fake images have empty fraud_type")
    if len(real_with_fraud_type) == 0 and len(fake_without_fraud_type) == 0:
        print("✅ fraud_type is consistent with is_fake")
    
    # 3. Check Subject Linkage
    print("\n🔗 Checking subject linkage...")
    groups = df.groupby('original_id')
    
    invalid_groups = 0
    valid_groups = 0
    
    for oid, group in groups:
        real_count = len(group[group['is_fake'] == 0])
        fake_count = len(group[group['is_fake'] == 1])
        
        if real_count != 1 or fake_count != 1:
            print(f"❌ ID {oid}: Real={real_count}, Fake={fake_count}")
            invalid_groups += 1
        else:
            valid_groups += 1
            
    if invalid_groups == 0:
        print(f"✅ PERFECT LINKAGE: All {valid_groups} subjects have exactly 1 Real + 1 Fake.")
    else:
        print(f"❌ BROKEN LINKAGE: {invalid_groups} subjects are invalid.")
    
    # 4. Check for Duplicates (Hash)
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
        print(f"⚠️ Found {len(duplicates)} duplicate pairs!")
    
    # 5. Check Image Integrity
    print("\n🖼️ Checking image integrity...")
    corrupted = []
    missing = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        path = os.path.join(DATASET_DIR, row['image_path'])
        if not os.path.exists(path):
            missing.append(row['image_path'])
            continue
            
        try:
            with Image.open(path) as img:
                img.verify()
        except (IOError, SyntaxError) as e:
            corrupted.append({'path': row['image_path'], 'error': str(e)})
    
    if not missing and not corrupted:
        print("✅ All images are valid and readable!")
    else:
        if missing:
            print(f"❌ {len(missing)} files missing")
        if corrupted:
            print(f"❌ {len(corrupted)} files corrupted")
    
    # 6. Final Balance Recap
    print("\n⚖️ Final Balance Recap:")
    print(f"Binary (is_fake):\n{df['is_fake'].value_counts()}")
    print(f"\nFraud Type (on fakes only):\n{df[df['is_fake'] == 1]['fraud_type'].value_counts()}")
    print(f"\nCountry Distribution:\n{df['source_country'].value_counts()}")

if __name__ == "__main__":
    verify_multi_task_dataset()


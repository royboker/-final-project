import pandas as pd
import os
from PIL import Image
from tqdm import tqdm

DATASET_DIR = 'datasets/drivers_license_final'
CSV_PATH = os.path.join(DATASET_DIR, 'dataset.csv')

def deep_integrity_check():
    print(f"🕵️ Starting Deep Integrity Check on: {DATASET_DIR}")
    
    if not os.path.exists(CSV_PATH):
        print("❌ CRITICAL: dataset.csv missing!")
        return
        
    df = pd.read_csv(CSV_PATH)
    total_files = len(df)
    print(f"📋 CSV contains {total_files} entries.")
    
    corrupted_files = []
    missing_files = []
    
    print("🖼️ Verifying image files (opening each file)...")
    
    for idx, row in tqdm(df.iterrows(), total=total_files):
        rel_path = row['image_path']
        full_path = os.path.join(DATASET_DIR, rel_path)
        
        if not os.path.exists(full_path):
            missing_files.append(rel_path)
            continue
            
        try:
            with Image.open(full_path) as img:
                img.verify()
        except (IOError, SyntaxError) as e:
            corrupted_files.append({'path': rel_path, 'error': str(e)})

    print("\n--- 📊 Final Report ---")
    
    if not missing_files and not corrupted_files:
        print("✅ SUCCESS: All images are valid and readable!")
    else:
        if missing_files:
            print(f"❌ FAILED: {len(missing_files)} files are missing.")
        if corrupted_files:
            print(f"❌ FAILED: {len(corrupted_files)} files are corrupted.")

if __name__ == "__main__":
    deep_integrity_check()


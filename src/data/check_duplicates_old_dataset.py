"""Check for duplicate images in the old dataset based on hash"""
import pandas as pd
import hashlib
from pathlib import Path

base = Path('/Users/roy-siftt/final-project/datasets/idnet/document_type_classification_new')
df = pd.read_csv(base / 'data/dataset.csv')

print(f"Total images in CSV: {len(df)}")

hashes = {}
duplicates = []

print("\nCalculating hashes...")
for idx, row in df.iterrows():
    if idx % 1000 == 0:
        print(f"  Processed {idx}/{len(df)} images...")
    
    img_path = base / row['image_path']
    if img_path.exists():
        try:
            with open(img_path, 'rb') as f:
                h = hashlib.md5(f.read()).hexdigest()
            
            if h in hashes:
                duplicates.append({
                    'hash': h,
                    'image1': row['image_path'],
                    'image2': hashes[h],
                    'label1': row['label'],
                    'label2': df[df['image_path'] == hashes[h]]['label'].iloc[0] if len(df[df['image_path'] == hashes[h]]) > 0 else 'unknown'
                })
            else:
                hashes[h] = row['image_path']
        except Exception as e:
            print(f"  Error processing {img_path}: {e}")

print(f"\n✅ Unique hashes: {len(hashes)}")
print(f"⚠️  Duplicates found: {len(duplicates)}")

if duplicates:
    print("\nFirst 10 duplicates:")
    for i, d in enumerate(duplicates[:10]):
        print(f"\n{i+1}. Hash: {d['hash'][:16]}...")
        print(f"   Image 1: {d['image1']} ({d['label1']})")
        print(f"   Image 2: {d['image2']} ({d['label2']})")
else:
    print("\n✅ No duplicates found!")


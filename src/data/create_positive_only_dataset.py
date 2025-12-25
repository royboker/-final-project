"""
Create a new document type classification dataset - POSITIVE ONLY
For each of 9 countries:
- From positive folder: 1000 images
Total: 1000 images per country × 9 countries = 9000 images

This script also removes duplicate images based on file hash (MD5).
"""
import os
import shutil
import random
import pandas as pd
import hashlib
from pathlib import Path
from collections import defaultdict

# Set random seed for reproducibility
random.seed(42)

# Base path
base_path = Path("/Users/roy-siftt/final-project/datasets/idnet")

# Output directory
output_dir = Path("/Users/roy-siftt/final-project/datasets/idnet/document_type_classification_positive_only")
output_dir.mkdir(exist_ok=True)
images_dir = output_dir / "images"
images_dir.mkdir(exist_ok=True)
data_dir = output_dir / "data"
data_dir.mkdir(exist_ok=True)

# Country configuration
# Some countries have nested structure (GRC/GRC, RUS/RUS, WV/WV)
countries_config = {
    'ALB': {
        'path': base_path / 'ALB',
        'label': 'passport',
        'nested': False
    },
    'GRC': {
        'path': base_path / 'GRC' / 'GRC',
        'label': 'passport',
        'nested': True
    },
    'LVA': {
        'path': base_path / 'LVA',
        'label': 'passport',
        'nested': False
    },
    'RUS': {
        'path': base_path / 'RUS' / 'RUS',
        'label': 'id_card',
        'nested': True
    },
    'NV': {
        'path': base_path / 'NV',
        'label': 'id_card',
        'nested': False
    },
    'SVK': {
        'path': base_path / 'SVK',
        'label': 'id_card',
        'nested': False
    },
    'WV': {
        'path': base_path / 'WV' / 'WV',
        'label': 'driver_license',
        'nested': True
    },
    'DC': {
        'path': base_path / 'DC',
        'label': 'driver_license',
        'nested': False
    },
    'AZ': {
        'path': base_path / 'AZ',
        'label': 'driver_license',
        'nested': False
    }
}

# Number of images to take from positive folder per country
images_per_country = 1000

def calculate_file_hash(file_path):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"   ⚠️  Error calculating hash for {file_path}: {e}")
        return None

# Collect all images with hash tracking
all_images_with_hash = []
seen_hashes = set()
image_counter = 0
country_stats = defaultdict(int)
duplicate_count = 0

print("="*60)
print("Creating New Document Type Classification Dataset - POSITIVE ONLY")
print("="*60)
print(f"\nTarget: 9000 images (1000 per country × 9 countries)")
print(f"Output directory: {output_dir}")
print(f"Removing duplicates based on file hash (MD5)")
print(f"\n{'='*60}\n")

for country_code, config in countries_config.items():
    country_path = config['path']
    label = config['label']
    
    if not country_path.exists():
        print(f"⚠️  Warning: {country_code} path not found: {country_path}")
        continue
    
    print(f"📂 Processing {country_code} ({label})...")
    
    # Only process positive folder
    positive_folder = country_path / 'positive'
    
    if not positive_folder.exists():
        print(f"   ⚠️  Positive folder not found: {positive_folder}")
        continue
    
    # Find all image files in positive folder
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']
    all_images_in_folder = []
    
    for ext in image_extensions:
        all_images_in_folder.extend(list(positive_folder.glob(ext)))
    
    if len(all_images_in_folder) < images_per_country:
        print(f"   ⚠️  Only {len(all_images_in_folder)} images available, requested {images_per_country}")
        candidate_images = all_images_in_folder
    else:
        # Randomly sample images
        candidate_images = random.sample(all_images_in_folder, images_per_country)
    
    # Process images and check for duplicates
    country_images_added = 0
    country_duplicates = 0
    attempts = 0
    max_attempts = len(all_images_in_folder)  # Don't try more than available
    
    # Try to get enough unique images
    for img_path in candidate_images:
        if country_images_added >= images_per_country:
            break
        
        attempts += 1
        if attempts > max_attempts:
            break
        
        # Calculate hash
        file_hash = calculate_file_hash(img_path)
        
        if file_hash is None:
            continue
        
        # Check if we've seen this hash before
        if file_hash in seen_hashes:
            country_duplicates += 1
            duplicate_count += 1
            # Try to get another image if we haven't reached the target
            if country_images_added < images_per_country and len(all_images_in_folder) > attempts:
                # Get a random image we haven't tried yet
                remaining_images = [img for img in all_images_in_folder if img not in candidate_images[:attempts]]
                if remaining_images:
                    # Add a random image from remaining to try
                    candidate_images.append(random.choice(remaining_images))
            continue
        
        # New unique image
        seen_hashes.add(file_hash)
        
        # Generate new filename
        image_counter += 1
        new_filename = f"{image_counter:05d}{img_path.suffix}"
        new_image_path = images_dir / new_filename
        
        # Copy image
        shutil.copy2(img_path, new_image_path)
        
        # Create relative path for CSV
        relative_path = f"images/{new_filename}"
        
        # Add to dataset
        all_images_with_hash.append({
            'image_path': relative_path,
            'label': label,
            'hash': file_hash,
            'source_country': country_code,
            'source_path': str(img_path)
        })
        
        country_images_added += 1
    
    # If we still don't have enough, try to get more from remaining images
    if country_images_added < images_per_country:
        remaining_images = [img for img in all_images_in_folder if img not in candidate_images[:attempts]]
        random.shuffle(remaining_images)
        
        for img_path in remaining_images:
            if country_images_added >= images_per_country:
                break
            
            file_hash = calculate_file_hash(img_path)
            if file_hash is None:
                continue
            
            if file_hash in seen_hashes:
                country_duplicates += 1
                duplicate_count += 1
                continue
            
            seen_hashes.add(file_hash)
            image_counter += 1
            new_filename = f"{image_counter:05d}{img_path.suffix}"
            new_image_path = images_dir / new_filename
            shutil.copy2(img_path, new_image_path)
            relative_path = f"images/{new_filename}"
            
            all_images_with_hash.append({
                'image_path': relative_path,
                'label': label,
                'hash': file_hash,
                'source_country': country_code,
                'source_path': str(img_path)
            })
            
            country_images_added += 1
    
    print(f"   ✓ positive: Added {country_images_added} unique images")
    if country_duplicates > 0:
        print(f"   ⚠️  Skipped {country_duplicates} duplicate images")
    if country_images_added < images_per_country:
        print(f"   ⚠️  Could only get {country_images_added} unique images (target: {images_per_country})")
    country_stats[country_code] = country_images_added
    
    print(f"   📊 Total for {country_code}: {country_images_added} images")
    print()

# If we have duplicates, we might need to get more images to reach target
# For now, we'll just use what we have

# Create DataFrame
df = pd.DataFrame(all_images_with_hash)

# Remove hash column from final dataset (keep only image_path and label)
df_final = df[['image_path', 'label']].copy()

# Shuffle the dataset
df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to CSV
output_csv = data_dir / "dataset.csv"
df_final.to_csv(output_csv, index=False)

# Save detailed info with hashes (for debugging)
detailed_csv = data_dir / "dataset_detailed.csv"
df.to_csv(detailed_csv, index=False)

# Print statistics
print("="*60)
print("Dataset Creation Summary")
print("="*60)
print(f"\n✅ Total unique images collected: {len(df_final)}")
print(f"✅ Expected: 9000 images")
print(f"✅ Difference: {9000 - len(df_final)} images")
print(f"⚠️  Duplicates removed: {duplicate_count}")

print(f"\n📊 Distribution by label:")
print(df_final['label'].value_counts().sort_index())

print(f"\n📊 Distribution by country:")
for country_code in countries_config.keys():
    count = country_stats[country_code]
    if count > 0:
        print(f"   {country_code}: {count} images")

print(f"\n💾 Dataset saved to: {output_csv}")
print(f"💾 Detailed dataset (with hash info) saved to: {detailed_csv}")
print(f"📁 Images directory: {images_dir}")
print(f"   Total images copied: {len(list(images_dir.glob('*.*')))}")
print(f"\n{'='*60}")
print("✅ Dataset creation completed!")

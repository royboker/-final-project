"""
Create a new document type classification dataset
For each of 9 countries:
- From positive folder: 520 images
- From fraud1_copy_and_move: 130 images
- From fraud2_face_morphing: 130 images
- From fraud3_face_replacement: 130 images
- From fraud4_combined: 130 images
Total: 1040 images per country × 9 countries = 9360 images
"""
import os
import shutil
import random
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Set random seed for reproducibility
random.seed(42)

# Base path
base_path = Path("/Users/roy-siftt/final-project/datasets/idnet")

# Output directory
output_dir = Path("/Users/roy-siftt/final-project/datasets/idnet/document_type_classification_new")
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

# Folder configuration
folders_config = {
    'positive': 520,
    'fraud1_copy_and_move': 130,
    'fraud2_face_morphing': 130,
    'fraud3_face_replacement': 130,
    'fraud4_combined': 130
}

# Collect all images
all_data = []
image_counter = 0
country_stats = defaultdict(lambda: defaultdict(int))

print("="*60)
print("Creating New Document Type Classification Dataset")
print("="*60)
print(f"\nTarget: 9360 images (1040 per country × 9 countries)")
print(f"Output directory: {output_dir}")
print(f"\n{'='*60}\n")

for country_code, config in countries_config.items():
    country_path = config['path']
    label = config['label']
    
    if not country_path.exists():
        print(f"⚠️  Warning: {country_code} path not found: {country_path}")
        continue
    
    print(f"📂 Processing {country_code} ({label})...")
    country_images = []
    
    for folder_name, num_images in folders_config.items():
        folder_path = country_path / folder_name
        
        if not folder_path.exists():
            print(f"   ⚠️  Folder not found: {folder_name}")
            continue
        
        # Find all image files
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']
        all_images_in_folder = []
        
        for ext in image_extensions:
            all_images_in_folder.extend(list(folder_path.glob(ext)))
        
        if len(all_images_in_folder) < num_images:
            print(f"   ⚠️  {folder_name}: Only {len(all_images_in_folder)} images available, requested {num_images}")
            selected_images = all_images_in_folder
        else:
            # Randomly sample images
            selected_images = random.sample(all_images_in_folder, num_images)
        
        print(f"   ✓ {folder_name}: Selected {len(selected_images)} images")
        country_stats[country_code][folder_name] = len(selected_images)
        
        # Copy images and create entries
        for img_path in selected_images:
            # Generate new filename
            image_counter += 1
            new_filename = f"{image_counter:05d}{img_path.suffix}"
            new_image_path = images_dir / new_filename
            
            # Copy image
            shutil.copy2(img_path, new_image_path)
            
            # Create relative path for CSV
            relative_path = f"images/{new_filename}"
            
            # Add to dataset
            all_data.append({
                'image_path': relative_path,
                'label': label
            })
            
            country_images.append(relative_path)
    
    print(f"   📊 Total for {country_code}: {len(country_images)} images")
    print()

# Create DataFrame
df = pd.DataFrame(all_data)

# Shuffle the dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to CSV
output_csv = data_dir / "dataset.csv"
df.to_csv(output_csv, index=False)

# Print statistics
print("="*60)
print("Dataset Creation Summary")
print("="*60)
print(f"\n✅ Total images collected: {len(df)}")
print(f"✅ Expected: 9360 images")
print(f"✅ Difference: {9360 - len(df)} images")

print(f"\n📊 Distribution by label:")
print(df['label'].value_counts().sort_index())

print(f"\n📊 Distribution by country (approximate):")
for country_code in countries_config.keys():
    total = sum(country_stats[country_code].values())
    if total > 0:
        print(f"   {country_code}: {total} images")
        for folder, count in country_stats[country_code].items():
            print(f"      - {folder}: {count}")

print(f"\n💾 Dataset saved to: {output_csv}")
print(f"📁 Images directory: {images_dir}")
print(f"   Total images copied: {len(list(images_dir.glob('*.*')))}")
print(f"\n{'='*60}")
print("✅ Dataset creation completed!")


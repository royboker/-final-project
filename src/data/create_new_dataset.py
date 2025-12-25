#!/usr/bin/env python3
"""
Script to create a new dataset with 300 images from positive and 300 from fraud4_combined
from each of the 9 countries, ensuring all images are unique by hash.
"""
import os
import hashlib
import pandas as pd
from collections import defaultdict
import random

# Define countries and their paths with document types
# Document types: passport, id_card, driver_license
countries = {
    'ALB': {
        'positive': 'datasets/idnet/ALB/positive',
        'fraud4_combined': 'datasets/idnet/ALB/fraud4_combined',
        'document_type': 'passport'
    },
    'AZ': {
        'positive': 'datasets/idnet/AZ/positive',
        'fraud4_combined': 'datasets/idnet/AZ/fraud4_combined',
        'document_type': 'driver_license'
    },
    'DC': {
        'positive': 'datasets/idnet/DC/positive',
        'fraud4_combined': 'datasets/idnet/DC/fraud4_combined',
        'document_type': 'driver_license'
    },
    'GRC': {
        'positive': 'datasets/idnet/GRC/GRC/positive',
        'fraud4_combined': 'datasets/idnet/GRC/GRC/fraud4_combined',
        'document_type': 'passport'
    },
    'LVA': {
        'positive': 'datasets/idnet/LVA/positive',
        'fraud4_combined': 'datasets/idnet/LVA/fraud4_combined',
        'document_type': 'passport'
    },
    'NV': {
        'positive': 'datasets/idnet/NV/positive',
        'fraud4_combined': 'datasets/idnet/NV/fraud4_combined',
        'document_type': 'id_card'
    },
    'RUS': {
        'positive': 'datasets/idnet/RUS/RUS/positive',
        'fraud4_combined': 'datasets/idnet/RUS/RUS/fraud4_combined',
        'document_type': 'id_card'
    },
    'SVK': {
        'positive': 'datasets/idnet/SVK/positive',
        'fraud4_combined': 'datasets/idnet/SVK/fraud4_combined',
        'document_type': 'id_card'
    },
    'WV': {
        'positive': 'datasets/idnet/WV/WV/positive',
        'fraud4_combined': 'datasets/idnet/WV/WV/fraud4_combined',
        'document_type': 'driver_license'
    }
}

def get_image_files(directory):
    """Get all image files from a directory."""
    if not os.path.exists(directory):
        return []
    files = [f for f in os.listdir(directory) 
             if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return files

def calculate_hash(file_path):
    """Calculate MD5 hash of a file."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f'Error reading {file_path}: {e}')
        return None

def select_unique_images(directory, num_images, used_hashes):
    """Select unique images from directory that are not in used_hashes."""
    image_files = get_image_files(directory)
    if len(image_files) < num_images:
        print(f'Warning: Only {len(image_files)} images available in {directory}, requested {num_images}')
    
    random.shuffle(image_files)
    selected = []
    selected_hashes = set()
    
    for filename in image_files:
        if len(selected) >= num_images:
            break
        
        file_path = os.path.join(directory, filename)
        file_hash = calculate_hash(file_path)
        
        if file_hash is None:
            continue
        
        # Check if hash is already used (either in this selection or globally)
        if file_hash not in used_hashes and file_hash not in selected_hashes:
            selected.append((filename, file_path, file_hash))
            selected_hashes.add(file_hash)
    
    return selected, selected_hashes

print('=== Creating New Dataset ===')
print(f'Countries: {len(countries)}')
print(f'Images per country: 300 (positive) + 300 (fraud4_combined) = 600')
print(f'Total images: {len(countries) * 600}')
print()

# Create output directory
output_dir = 'datasets/idnet/document_type_classification_country_split_new'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'data'), exist_ok=True)

# Store all selected images
all_images = []
used_hashes_global = set()
image_counter = 1

# Process each country
for country_code, paths in countries.items():
    print(f'Processing {country_code}...')
    
    # Select 300 unique images from positive
    print(f'  Selecting 300 images from positive...')
    positive_images, positive_hashes = select_unique_images(
        paths['positive'], 300, used_hashes_global
    )
    used_hashes_global.update(positive_hashes)
    print(f'  Selected {len(positive_images)} unique images from positive')
    
    # Select 300 unique images from fraud4_combined
    print(f'  Selecting 300 images from fraud4_combined...')
    fraud_images, fraud_hashes = select_unique_images(
        paths['fraud4_combined'], 300, used_hashes_global
    )
    used_hashes_global.update(fraud_hashes)
    print(f'  Selected {len(fraud_images)} unique images from fraud4_combined')
    
    # Get document type for this country
    document_type = paths['document_type']
    
    # Copy positive images and add to dataset
    for filename, source_path, file_hash in positive_images:
        new_filename = f'{image_counter:05d}.png'
        dest_path = os.path.join(output_dir, 'images', new_filename)
        
        # Copy file
        import shutil
        shutil.copy2(source_path, dest_path)
        
        all_images.append({
            'image_path': f'images/{new_filename}',
            'document_type': document_type
        })
        image_counter += 1
    
    # Copy fraud images and add to dataset
    for filename, source_path, file_hash in fraud_images:
        new_filename = f'{image_counter:05d}.png'
        dest_path = os.path.join(output_dir, 'images', new_filename)
        
        # Copy file
        import shutil
        shutil.copy2(source_path, dest_path)
        
        all_images.append({
            'image_path': f'images/{new_filename}',
            'document_type': document_type
        })
        image_counter += 1
    
    print(f'  Total for {country_code}: {len(positive_images)} positive + {len(fraud_images)} fraud = {len(positive_images) + len(fraud_images)} images')
    print()

# Create DataFrame and save
df = pd.DataFrame(all_images)
print(f'=== Dataset Summary ===')
print(f'Total images: {len(df)}')
print(f'Document types: {df["document_type"].nunique()}')
print()
print('Distribution by document_type:')
print(df.groupby('document_type').size())
print()

# Save dataset
dataset_path = os.path.join(output_dir, 'data', 'dataset.csv')
df.to_csv(dataset_path, index=False)
print(f'Dataset saved to: {dataset_path}')

# Verify uniqueness by hash
print()
print('=== Verifying uniqueness ===')
hash_to_paths = defaultdict(list)
for idx, row in df.iterrows():
    image_path = os.path.join(output_dir, row['image_path'])
    if os.path.exists(image_path):
        file_hash = calculate_hash(image_path)
        if file_hash:
            hash_to_paths[file_hash].append(row['image_path'])

duplicate_hashes = {h: paths for h, paths in hash_to_paths.items() if len(paths) > 1}
if duplicate_hashes:
    print(f'Warning: Found {len(duplicate_hashes)} duplicate hashes!')
    for h, paths in list(duplicate_hashes.items())[:5]:
        print(f'  Hash {h[:16]}...: {paths}')
else:
    print(f'✓ All {len(hash_to_paths)} images are unique by hash')

print()
print('=== Done ===')


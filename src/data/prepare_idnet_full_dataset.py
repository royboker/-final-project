#!/usr/bin/env python3
"""
Script to prepare IDNet full dataset for document type classification.
This script will:
1. Load the full IDNet dataset
2. Create a mixed dataset where each document type comes from multiple countries
3. Split into train/val/test without data leakage
4. Save the new datasets

Usage:
    python prepare_idnet_full_dataset.py --idnet_path /path/to/idnet --output_dir datasets/idnet/document_type_classification/data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from sklearn.model_selection import train_test_split
import json
import os

def extract_country_from_path(path):
    """Extract country code from image path"""
    path_str = str(path)
    if '/Albania/' in path_str or '/ALB/' in path_str:
        return 'Albania'
    elif '/Azerbaijan/' in path_str or '/AZE/' in path_str:
        return 'Azerbaijan'
    elif '/Estonia/' in path_str or '/EST/' in path_str:
        return 'Estonia'
    elif '/Finland/' in path_str or '/FIN/' in path_str:
        return 'Finland'
    elif '/Greece/' in path_str or '/GRC/' in path_str:
        return 'Greece'
    elif '/Latvia/' in path_str or '/LVA/' in path_str:
        return 'Latvia'
    elif '/Russia/' in path_str or '/RUS/' in path_str:
        return 'Russia'
    elif '/Serbia/' in path_str or '/SRB/' in path_str:
        return 'Serbia'
    elif '/Slovakia/' in path_str or '/SVK/' in path_str:
        return 'Slovakia'
    elif '/Spain/' in path_str or '/ESP/' in path_str:
        return 'Spain'
    elif '/Nevada/' in path_str or '/NV/' in path_str:
        return 'Nevada'
    elif '/Arizona/' in path_str or '/AZ/' in path_str:
        return 'Arizona'
    elif '/California/' in path_str or '/CA/' in path_str:
        return 'California'
    elif '/North Carolina/' in path_str or '/NC/' in path_str:
        return 'North Carolina'
    elif '/Pennsylvania/' in path_str or '/PA/' in path_str:
        return 'Pennsylvania'
    elif '/South Dakota/' in path_str or '/SD/' in path_str:
        return 'South Dakota'
    elif '/Utah/' in path_str or '/UT/' in path_str:
        return 'Utah'
    elif '/Washington D.C./' in path_str or '/DC/' in path_str:
        return 'Washington D.C.'
    elif '/West Virginia/' in path_str or '/WV/' in path_str:
        return 'West Virginia'
    elif '/Wisconsin/' in path_str or '/WI/' in path_str:
        return 'Wisconsin'
    return 'unknown'

def load_idnet_data(idnet_path):
    """
    Load IDNet data from various possible structures.
    This function tries different common structures.
    """
    idnet_path = Path(idnet_path)
    
    print(f"🔍 Checking IDNet structure in: {idnet_path}")
    
    # Possible structures:
    # 1. CSV files per country
    # 2. Single unified CSV
    # 3. Folders per country with metadata
    
    # Check for unified CSV files
    csv_files = list(idnet_path.glob("**/*_Unified_Dataset.csv"))
    if csv_files:
        print(f"✅ Found {len(csv_files)} unified dataset CSV files")
        all_dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                df['source_file'] = csv_file.name
                all_dfs.append(df)
                print(f"   Loaded {csv_file.name}: {len(df)} rows")
            except Exception as e:
                print(f"   ⚠️  Error loading {csv_file.name}: {e}")
        
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            return combined_df
    
    # Check for single CSV file
    csv_files = list(idnet_path.glob("**/*.csv"))
    if len(csv_files) == 1:
        print(f"✅ Found single CSV file: {csv_files[0]}")
        return pd.read_csv(csv_files[0], low_memory=False)
    
    print("❌ Could not find expected CSV structure")
    print(f"   Please check the IDNet dataset structure")
    return None

def prepare_mixed_dataset(df, output_dir):
    """
    Create a mixed dataset where each document type comes from multiple countries.
    Split into train/val/test without data leakage.
    """
    print("\n" + "=" * 70)
    print("Preparing Mixed Dataset")
    print("=" * 70)
    
    # Extract country and ensure we have document_type
    if 'country' not in df.columns:
        df['country'] = df['image_path'].apply(extract_country_from_path)
    
    if 'document_type' not in df.columns:
        print("❌ Error: 'document_type' column not found in dataset")
        print(f"   Available columns: {list(df.columns)}")
        return None
    
    # Filter to only real documents (if is_real column exists)
    if 'is_real' in df.columns:
        df = df[df['is_real'] == True].copy()
        print(f"✅ Filtered to real documents: {len(df)} rows")
    
    # Show distribution
    print("\n📊 Document Type Distribution by Country:")
    print("-" * 70)
    pivot = pd.crosstab(df['country'], df['document_type'])
    print(pivot)
    
    # Check if we have multiple countries per document type
    print("\n🔍 Checking diversity:")
    for doc_type in df['document_type'].unique():
        countries = df[df['document_type'] == doc_type]['country'].unique()
        print(f"   {doc_type}: {len(countries)} countries - {list(countries)}")
        
        if len(countries) == 1:
            print(f"      ⚠️  Warning: {doc_type} only from one country!")
    
    # Extract base image ID to avoid leakage from augmented images
    def extract_base_id(path):
        """Extract base image ID from path"""
        filename = Path(path).name.replace('.png', '').replace('.jpg', '')
        # Common patterns: generated.photos_v3_XXXXXXXX
        parts = filename.split('_')
        if len(parts) >= 3 and parts[0] == 'generated' and parts[1] == 'photos':
            # Base ID is the first 3 parts
            return '_'.join(parts[:3])
        # Fallback: use filename without extension
        return filename.split('_')[0] if '_' in filename else filename
    
    df['base_id'] = df['image_path'].apply(extract_base_id)
    
    # Split by base_id to avoid leakage
    print("\n📦 Creating train/val/test splits by base image ID...")
    
    train_base_ids = []
    val_base_ids = []
    test_base_ids = []
    
    # Split each document type separately to maintain balance
    for doc_type in df['document_type'].unique():
        doc_data = df[df['document_type'] == doc_type]
        unique_base_ids = doc_data['base_id'].unique()
        
        # First split: 70% train, 30% temp
        train_ids, temp_ids = train_test_split(
            unique_base_ids, 
            test_size=0.3, 
            random_state=42
        )
        
        # Second split: 50% val, 50% test (of the 30%)
        val_ids, test_ids = train_test_split(
            temp_ids,
            test_size=0.5,
            random_state=42
        )
        
        train_base_ids.extend(train_ids)
        val_base_ids.extend(val_ids)
        test_base_ids.extend(test_ids)
        
        print(f"   {doc_type}:")
        print(f"      Train: {len(train_ids)} base images")
        print(f"      Val:   {len(val_ids)} base images")
        print(f"      Test:  {len(test_ids)} base images")
    
    # Create final datasets
    train_df = df[df['base_id'].isin(train_base_ids)].copy()
    val_df = df[df['base_id'].isin(val_base_ids)].copy()
    test_df = df[df['base_id'].isin(test_base_ids)].copy()
    
    # Select only needed columns
    output_cols = ['image_path', 'document_type']
    if 'country' in train_df.columns:
        output_cols.insert(1, 'country')
    
    train_df = train_df[output_cols]
    val_df = val_df[output_cols]
    test_df = test_df[output_cols]
    
    # Save
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup existing files
    backup_dir = output_dir / 'backup_mixed'
    backup_dir.mkdir(exist_ok=True)
    
    for file_name in ['train_dataset.csv', 'val_dataset.csv', 'test_dataset.csv']:
        existing_file = output_dir / file_name
        if existing_file.exists():
            import shutil
            shutil.copy(existing_file, backup_dir / file_name)
            print(f"   📦 Backed up {file_name}")
    
    # Save new datasets
    train_df.to_csv(output_dir / 'train_dataset.csv', index=False)
    val_df.to_csv(output_dir / 'val_dataset.csv', index=False)
    test_df.to_csv(output_dir / 'test_dataset.csv', index=False)
    
    print("\n✅ Saved new datasets:")
    print(f"   Train:  {len(train_df)} images ({len(train_base_ids)} unique base images)")
    print(f"   Val:    {len(val_df)} images ({len(val_base_ids)} unique base images)")
    print(f"   Test:   {len(test_df)} images ({len(test_base_ids)} unique base images)")
    
    # Save statistics
    stats = {
        'train': {
            'total_images': len(train_df),
            'unique_base_images': len(train_base_ids),
            'document_types': train_df['document_type'].value_counts().to_dict(),
            'countries': train_df['country'].value_counts().to_dict() if 'country' in train_df.columns else {}
        },
        'val': {
            'total_images': len(val_df),
            'unique_base_images': len(val_base_ids),
            'document_types': val_df['document_type'].value_counts().to_dict(),
            'countries': val_df['country'].value_counts().to_dict() if 'country' in val_df.columns else {}
        },
        'test': {
            'total_images': len(test_df),
            'unique_base_images': len(test_base_ids),
            'document_types': test_df['document_type'].value_counts().to_dict(),
            'countries': test_df['country'].value_counts().to_dict() if 'country' in test_df.columns else {}
        }
    }
    
    with open(output_dir / 'dataset_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n📊 Statistics saved to: {output_dir / 'dataset_stats.json'}")
    
    return train_df, val_df, test_df

def main():
    parser = argparse.ArgumentParser(description='Prepare IDNet full dataset for document type classification')
    parser.add_argument('--idnet_path', type=str, required=True,
                        help='Path to IDNet full dataset directory')
    parser.add_argument('--output_dir', type=str,
                        default='datasets/idnet/document_type_classification/data',
                        help='Output directory for processed datasets')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("IDNet Full Dataset Preparation")
    print("=" * 70)
    
    # Load data
    df = load_idnet_data(args.idnet_path)
    if df is None:
        print("\n❌ Failed to load IDNet data")
        return
    
    print(f"\n✅ Loaded {len(df)} total rows")
    print(f"   Columns: {list(df.columns)}")
    
    # Prepare mixed dataset
    train_df, val_df, test_df = prepare_mixed_dataset(df, args.output_dir)
    
    if train_df is not None:
        print("\n" + "=" * 70)
        print("✅ Dataset preparation complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Verify the datasets look correct")
        print("2. Re-run your preprocessing notebook")
        print("3. Train the model with the new mixed dataset")
        print("4. The model should now learn general document types!")

if __name__ == '__main__':
    main()


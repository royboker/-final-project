#!/usr/bin/env python3
"""
Script to create a mapping between local file paths and Google Drive file IDs.
This script will help you manually map each image to its Google Drive URL.
"""

import pandas as pd
import os
from pathlib import Path
import json

def create_file_mapping(csv_file_path, output_mapping_file):
    """
    Create a mapping file that lists all images that need Google Drive URLs.
    
    Args:
        csv_file_path: Path to the CSV file
        output_mapping_file: Path to save the mapping file
    """
    print(f"Processing: {csv_file_path}")
    
    # Read CSV
    df = pd.read_csv(csv_file_path)
    
    if 'image_path' not in df.columns:
        print(f"  ⚠️  No 'image_path' column found in {csv_file_path}")
        return
    
    # Create mapping
    mapping = []
    
    for idx, row in df.iterrows():
        old_path = row['image_path']
        
        # Skip if already a Google Drive URL
        if 'drive.google.com' in old_path:
            continue
            
        # Extract relative path
        if 'datasets/idnet/' in old_path:
            relative_path = old_path.split('datasets/idnet/')[1]
            
            mapping.append({
                'local_path': old_path,
                'relative_path': relative_path,
                'document_type': row.get('document_type', 'unknown'),
                'google_drive_url': '',  # To be filled manually
                'file_id': ''  # To be filled manually
            })
    
    # Save mapping to JSON
    with open(output_mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"  ✅ Created mapping with {len(mapping)} files")
    print(f"  📁 Saved to: {output_mapping_file}")

def main():
    """Main function to create mappings for all CSV files"""
    
    # Find all CSV files
    project_root = Path(__file__).parent.parent.parent
    csv_files = [
        "datasets/idnet/document_type_classification/data/full_dataset.csv",
        "datasets/idnet/document_type_classification/data/train_dataset.csv", 
        "datasets/idnet/document_type_classification/data/val_dataset.csv",
        "datasets/idnet/document_type_classification/data/test_dataset.csv"
    ]
    
    print("Creating file mappings for Google Drive URLs...")
    print("="*50)
    
    for csv_file in csv_files:
        full_path = project_root / csv_file
        if full_path.exists():
            # Create mapping file name
            mapping_file = f"mapping_{Path(csv_file).stem}.json"
            mapping_path = project_root / "src" / "utils" / mapping_file
            
            create_file_mapping(full_path, mapping_path)
    
    print("\n" + "="*50)
    print("Next steps:")
    print("1. Open each mapping file (mapping_*.json)")
    print("2. For each file, get the Google Drive sharing URL")
    print("3. Fill in the 'google_drive_url' and 'file_id' fields")
    print("4. Run update_csv_with_mapping.py to update the CSV files")
    print("="*50)

if __name__ == "__main__":
    main()

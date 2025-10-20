#!/usr/bin/env python3
"""
Script to update CSV files to use local Google Drive Desktop paths.
This script will replace the current paths with local Google Drive Desktop paths.
"""

import pandas as pd
import os
from pathlib import Path

def update_csv_to_local_drive_paths(csv_file_path, google_drive_path):
    """
    Update CSV file to use local Google Drive Desktop paths.
    
    Args:
        csv_file_path: Path to the CSV file
        google_drive_path: Local Google Drive Desktop path
    """
    print(f"Processing: {csv_file_path}")
    
    # Read CSV
    df = pd.read_csv(csv_file_path)
    
    if 'image_path' not in df.columns:
        print(f"  ⚠️  No 'image_path' column found in {csv_file_path}")
        return
    
    # Count original paths
    original_count = len(df)
    updated_count = 0
    
    # Update paths
    for idx, row in df.iterrows():
        old_path = row['image_path']
        
        # Skip if already a local Google Drive path
        if 'Google Drive' in old_path:
            continue
            
        # Extract relative path from current path
        if 'datasets/idnet/' in old_path:
            # Extract the part after 'datasets/idnet/'
            relative_path = old_path.split('datasets/idnet/')[1]
            
            # Remove duplicate directory names (e.g., GRC/GRC -> GRC)
            path_parts = relative_path.split('/')
            if len(path_parts) >= 2 and path_parts[0] == path_parts[1]:
                # Remove the duplicate part
                relative_path = '/'.join(path_parts[1:])
            
            # Create new local Google Drive path
            new_path = f"{google_drive_path}/IDNET/{relative_path}"
            
            # Update the dataframe
            df.at[idx, 'image_path'] = new_path
            updated_count += 1
    
    # Save updated CSV
    df.to_csv(csv_file_path, index=False)
    
    print(f"  ✅ Updated {updated_count}/{original_count} paths")
    print(f"  📁 Saved to: {csv_file_path}")

def main():
    """Main function to update all CSV files"""
    
    # Default Google Drive Desktop path (adjust for your system)
    GOOGLE_DRIVE_PATH = "/Users/roy-siftt/Google Drive/final-project-datasets"
    
    print("Updating CSV files to use local Google Drive Desktop paths...")
    print("="*60)
    print(f"Google Drive path: {GOOGLE_DRIVE_PATH}")
    print("="*60)
    
    # Check if Google Drive path exists
    if not os.path.exists(GOOGLE_DRIVE_PATH):
        print(f"❌ Google Drive path not found: {GOOGLE_DRIVE_PATH}")
        print("Please:")
        print("1. Install Google Drive Desktop")
        print("2. Sync the 'final-project-datasets' folder")
        print("3. Update the GOOGLE_DRIVE_PATH in this script")
        return
    
    # Find all CSV files
    project_root = Path(__file__).parent.parent.parent
    csv_files = [
        "datasets/idnet/document_type_classification/data/full_dataset.csv",
        "datasets/idnet/document_type_classification/data/train_dataset.csv", 
        "datasets/idnet/document_type_classification/data/val_dataset.csv",
        "datasets/idnet/document_type_classification/data/test_dataset.csv",
        "datasets/idnet/GRC_Unified_Dataset.csv",
        "datasets/idnet/RUS_Unified_Dataset.csv",
        "datasets/idnet/WV_Unified_Dataset.csv"
    ]
    
    print(f"Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        full_path = project_root / csv_file
        if full_path.exists():
            print(f"  - {csv_file}")
        else:
            print(f"  - {csv_file} (not found)")
    
    print("\n" + "="*60)
    
    # Update each CSV file
    for csv_file in csv_files:
        full_path = project_root / csv_file
        if full_path.exists():
            update_csv_to_local_drive_paths(full_path, GOOGLE_DRIVE_PATH)
    
    print("\n" + "="*60)
    print("✅ All CSV files have been updated!")
    print("\nNext steps:")
    print("1. Test loading an image with the new path")
    print("2. Update your notebooks to use the new paths")
    print("3. Run your data exploration and training")

if __name__ == "__main__":
    main()

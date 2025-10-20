#!/usr/bin/env python3
"""
Script to update CSV files for Google Colab usage.
This script will replace local paths with Google Colab Drive paths.
"""

import pandas as pd
import os
from pathlib import Path

def update_csv_for_colab(csv_file_path):
    """
    Update CSV file to use Google Colab Drive paths.
    
    Args:
        csv_file_path: Path to the CSV file
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
        
        # Skip if already a Colab path
        if '/content/drive/MyDrive/' in old_path:
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
            
            # Create new Colab Drive path
            new_path = f"/content/drive/MyDrive/final-project-datasets/IDNET/{relative_path}"
            
            # Update the dataframe
            df.at[idx, 'image_path'] = new_path
            updated_count += 1
    
    # Save updated CSV
    df.to_csv(csv_file_path, index=False)
    
    print(f"  ✅ Updated {updated_count}/{original_count} paths")
    print(f"  📁 Saved to: {csv_file_path}")

def main():
    """Main function to update all CSV files for Colab"""
    
    print("Updating CSV files for Google Colab...")
    print("="*50)
    
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
    
    print("\n" + "="*50)
    
    # Update each CSV file
    for csv_file in csv_files:
        full_path = project_root / csv_file
        if full_path.exists():
            update_csv_for_colab(full_path)
    
    print("\n" + "="*50)
    print("✅ All CSV files have been updated for Google Colab!")
    print("\nNext steps:")
    print("1. Upload your project to Google Colab")
    print("2. Mount Google Drive: drive.mount('/content/drive')")
    print("3. Run this script in Colab to update paths")
    print("4. Start working with your data!")

if __name__ == "__main__":
    main()

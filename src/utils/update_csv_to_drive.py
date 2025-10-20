#!/usr/bin/env python3
"""
Script to update CSV files with Google Drive URLs instead of local paths.
This script will replace local file paths with Google Drive sharing URLs.
"""

import pandas as pd
import os
from pathlib import Path
import re

def extract_file_id_from_drive_url(url):
    """Extract file ID from Google Drive sharing URL"""
    # Pattern to match Google Drive URLs
    patterns = [
        r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def convert_to_direct_download_url(share_url):
    """Convert Google Drive sharing URL to direct download URL"""
    file_id = extract_file_id_from_drive_url(share_url)
    if file_id:
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return share_url

def update_csv_paths(csv_file_path, drive_base_url):
    """
    Update CSV file to use Google Drive URLs instead of local paths.
    
    Args:
        csv_file_path: Path to the CSV file
        drive_base_url: Base URL of the Google Drive folder
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
        
        # Skip if already a Google Drive URL
        if 'drive.google.com' in old_path:
            continue
            
        # Extract relative path from local path
        # Example: /Users/roy-siftt/final-project/datasets/idnet/GRC/GRC/positive/...
        # Should become: GRC/GRC/positive/...
        
        if 'datasets/idnet/' in old_path:
            # Extract the part after 'datasets/idnet/'
            relative_path = old_path.split('datasets/idnet/')[1]
            
            # For now, we'll create a placeholder URL that needs to be updated manually
            # with actual Google Drive file IDs
            new_path = f"PLACEHOLDER_DRIVE_URL_FOR_{relative_path.replace('/', '_')}"
            
            # Update the dataframe
            df.at[idx, 'image_path'] = new_path
            updated_count += 1
    
    # Save updated CSV
    df.to_csv(csv_file_path, index=False)
    
    print(f"  ✅ Updated {updated_count}/{original_count} paths")
    print(f"  📁 Saved to: {csv_file_path}")

def main():
    """Main function to update all CSV files"""
    
    # Base URL of your Google Drive folder
    DRIVE_BASE_URL = "https://drive.google.com/drive/folders/1flQv8CqWEgxHyZUh0k17gAo0wrrMooYz"
    
    # Alternative: if you have individual file URLs, you can use this format:
    # DRIVE_BASE_URL = "https://drive.google.com/file/d"
    
    # Find only relevant CSV files (exclude venv and other system files)
    project_root = Path(__file__).parent.parent.parent
    csv_files = []
    
    # Add specific CSV files we want to update
    target_files = [
        "datasets/idnet/document_type_classification/data/full_dataset.csv",
        "datasets/idnet/document_type_classification/data/train_dataset.csv", 
        "datasets/idnet/document_type_classification/data/val_dataset.csv",
        "datasets/idnet/document_type_classification/data/test_dataset.csv",
        "datasets/idnet/GRC_Unified_Dataset.csv",
        "datasets/idnet/RUS_Unified_Dataset.csv",
        "datasets/idnet/WV_Unified_Dataset.csv"
    ]
    
    for file_path in target_files:
        full_path = project_root / file_path
        if full_path.exists():
            csv_files.append(full_path)
    
    print(f"Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        print(f"  - {csv_file.relative_to(project_root)}")
    
    print("\n" + "="*50)
    print("IMPORTANT: Before running this script:")
    print("1. Replace 'YOUR_FOLDER_ID' with your actual Google Drive folder ID")
    print("2. Make sure all images are uploaded to Google Drive")
    print("3. Test with one CSV file first")
    print("="*50)
    
    # Run the updates
    for csv_file in csv_files:
        update_csv_paths(csv_file, DRIVE_BASE_URL)
    
    print("\n✅ All CSV files have been updated with Google Drive URLs!")

if __name__ == "__main__":
    main()

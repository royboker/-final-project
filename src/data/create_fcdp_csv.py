"""
Create a unified CSV file for the FCD-P (Forged Characters Detection on Passports) dataset.
Scans all country folders and creates a structured DataFrame.
"""

import os
import json
import pandas as pd
from pathlib import Path

def create_fcdp_dataset_csv(base_path):
    """
    Create CSV files for the FCD-P dataset
    
    Args:
        base_path: Path to the fcd-passports folder
    """
    
    countries = ['australia', 'canada', 'ireland', 'pakistan', 'usa']
    
    all_data = []
    
    for country in countries:
        print(f"\n🌍 Processing {country.upper()}...")
        
        country_path = os.path.join(base_path, country)
        json_folder = os.path.join(country_path, 'json files')
        
        # Get all image files
        image_files = sorted([f for f in os.listdir(country_path) 
                             if f.endswith('.jpg')])
        
        print(f"   Found {len(image_files)} images")
        
        for img_file in image_files:
            # Construct paths
            img_path = os.path.join(country_path, img_file)
            
            # Get corresponding JSON file
            json_file = img_file.replace('.jpg', '.json')
            json_path = os.path.join(json_folder, json_file)
            
            # Read bounding boxes if JSON exists
            bounding_boxes = []
            num_forged_chars = 0
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        bounding_boxes = json.load(f)
                        num_forged_chars = len(bounding_boxes)
                except:
                    pass
            
            # Determine if image is real or forged based on JSON existence
            # Images without JSON annotations are the original (real) passports
            is_real = 1 if num_forged_chars == 0 else 0
            fraud_type = 'real' if is_real else 'character_forgery'
            
            # Add to dataset
            record = {
                'image_path': img_path,
                'filename': img_file,
                'country': country,
                'is_real': is_real,
                'fraud_type': fraud_type,
                'num_forged_chars': num_forged_chars,
                'bounding_boxes': str(bounding_boxes)  # Store as string
            }
            
            all_data.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    print(f"\n\n📊 Total dataset statistics:")
    print(f"   Total images: {len(df)}")
    print(f"   Countries: {df['country'].nunique()}")
    
    print(f"\n   Real vs Fake:")
    print(f"   Real images: {df['is_real'].sum()} ({df['is_real'].sum()/len(df)*100:.1f}%)")
    print(f"   Fake images: {(~df['is_real'].astype(bool)).sum()} ({(~df['is_real'].astype(bool)).sum()/len(df)*100:.1f}%)")
    
    print(f"\n   Distribution by country:")
    print(df['country'].value_counts().to_string())
    
    print(f"\n   Forged characters statistics (fake images only):")
    fake_df = df[df['is_real'] == 0]
    print(f"   Total forged characters: {fake_df['num_forged_chars'].sum()}")
    print(f"   Average per fake image: {fake_df['num_forged_chars'].mean():.2f}")
    print(f"   Max per image: {fake_df['num_forged_chars'].max()}")
    print(f"   Min per image: {fake_df['num_forged_chars'].min()}")
    
    # Save unified CSV
    output_file = os.path.join(base_path, 'dataset_fcdp_all.csv')
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved unified dataset to: {output_file}")
    
    # Save individual country CSVs
    for country in countries:
        country_df = df[df['country'] == country]
        country_file = os.path.join(base_path, f'dataset_fcdp_{country}.csv')
        country_df.to_csv(country_file, index=False)
        print(f"✅ Saved {country} dataset to: {country_file} ({len(country_df)} images)")
    
    return df


if __name__ == "__main__":
    # Path to the FCD-P dataset
    base_path = "/Users/roy-siftt/final-project/datasets/fcd-passports"
    
    print("🚀 Creating FCD-P Dataset CSV Files...")
    print("=" * 60)
    
    df = create_fcdp_dataset_csv(base_path)
    
    print("\n" + "=" * 60)
    print("✨ Dataset CSV creation completed!")
    print("\nYou can now load the data using:")
    print("  df = pd.read_csv('datasets/fcd-passports/dataset_fcdp_all.csv')")


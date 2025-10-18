"""
Create a unified CSV dataset from the IDNet folder structure
"""
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import json


def create_unified_dataset(country='GRC', output_path='datasets/idnet/dataset.csv'):
    """
    Create a unified CSV dataset from the IDNet folder structure.
    
    Args:
        country: Country code (GRC, WV, or RUS)
        output_path: Path to save the CSV file
    """
    
    # Define paths
    base_path = Path('datasets/idnet') / country / country
    
    # Define categories
    categories = {
        'positive': 'real',
        'fraud1_copy_and_move': 'fraud_copy_move',
        'fraud2_face_morphing': 'fraud_face_morphing',
        'fraud3_face_replacement': 'fraud_face_replacement',
        'fraud4_combined': 'fraud_combined',
        'fraud5_inpaint_and_rewrite': 'fraud_inpaint_rewrite',
        'fraud6_crop_and_replace': 'fraud_crop_replace'
    }
    
    print(f"🔍 Scanning {country} dataset...")
    print(f"📂 Base path: {base_path.resolve()}\n")
    
    # Collect all images
    data = []
    
    for folder, label in tqdm(categories.items(), desc="Processing categories"):
        folder_path = base_path / folder
        
        if not folder_path.exists():
            print(f"⚠️  Warning: {folder_path} doesn't exist, skipping...")
            continue
        
        # Find all images (jpg and png)
        image_files = list(folder_path.glob('*.jpg')) + list(folder_path.glob('*.png'))
        
        for img_path in image_files:
            # Create relative path for portability
            rel_path = img_path.relative_to(Path('datasets/idnet'))
            
            # Determine if it's real or fake
            is_real = 1 if folder == 'positive' else 0
            
            # Extract fraud type (if fake)
            fraud_type = 'none' if is_real else label.replace('fraud_', '')
            
            data.append({
                'image_path': str(rel_path),
                'absolute_path': str(img_path.resolve()),
                'filename': img_path.name,
                'country': country,
                'category': folder,
                'label': label,
                'is_real': is_real,
                'fraud_type': fraud_type,
                'extension': img_path.suffix
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total images: {len(df)}")
    print(f"   Real images: {(df['is_real'] == 1).sum()}")
    print(f"   Fake images: {(df['is_real'] == 0).sum()}")
    print(f"\n📋 Images per category:")
    print(df['label'].value_counts().sort_index())
    
    # Save to CSV
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Dataset saved to: {output_file.resolve()}")
    print(f"   Columns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    return df


def create_all_countries_dataset(output_path='datasets/idnet/dataset_all.csv'):
    """
    Create a unified dataset with all countries combined.
    """
    all_dfs = []
    
    for country in ['GRC', 'WV', 'RUS']:
        country_path = Path('datasets/idnet') / country / country
        
        if not country_path.exists():
            print(f"⚠️  {country} not extracted yet, skipping...")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing {country}...")
        print(f"{'='*60}")
        
        df = create_unified_dataset(
            country=country, 
            output_path=f'datasets/idnet/dataset_{country}.csv'
        )
        all_dfs.append(df)
    
    if all_dfs:
        # Combine all countries
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        print(f"\n{'='*60}")
        print(f"📊 Combined Dataset Statistics:")
        print(f"{'='*60}")
        print(f"Total images: {len(combined_df)}")
        print(f"\nImages per country:")
        print(combined_df['country'].value_counts())
        print(f"\nReal vs Fake:")
        print(combined_df['is_real'].value_counts())
        
        # Save combined dataset
        output_file = Path(output_path)
        combined_df.to_csv(output_file, index=False)
        print(f"\n✅ Combined dataset saved to: {output_file.resolve()}")
        
        return combined_df
    
    return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create unified dataset CSV')
    parser.add_argument('--country', type=str, default='GRC', 
                       help='Country code: GRC, WV, or RUS')
    parser.add_argument('--all', action='store_true',
                       help='Process all countries')
    parser.add_argument('--output', type=str, default=None,
                       help='Output CSV path')
    
    args = parser.parse_args()
    
    if args.all:
        create_all_countries_dataset(
            output_path=args.output or 'datasets/idnet/dataset_all.csv'
        )
    else:
        create_unified_dataset(
            country=args.country,
            output_path=args.output or f'datasets/idnet/dataset_{args.country}.csv'
        )


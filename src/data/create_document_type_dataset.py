import pandas as pd
import os
from pathlib import Path

def create_document_type_classification_dataset(samples_per_class=700, output_dir="../../datasets/idnet"):
    """
    Create a dataset for document type classification (passport/id_card/driver_license).
    
    Args:
        samples_per_class (int): Number of real images to sample from each dataset
        output_dir (str): Output directory for the dataset
    """
    print('🚀 Creating Document Type Classification Dataset')
    print('=' * 60)
    
    script_dir = Path(__file__).parent
    base_path = (script_dir / output_dir).resolve()
    
    # Load all three datasets
    print('\n📂 Loading datasets...')
    grc_df = pd.read_csv(base_path / 'GRC_Unified_Dataset.csv')
    rus_df = pd.read_csv(base_path / 'RUS_Unified_Dataset.csv')
    wv_df = pd.read_csv(base_path / 'WV_Unified_Dataset.csv', low_memory=False)
    
    print(f'   ✓ GRC loaded: {len(grc_df):,} images')
    print(f'   ✓ RUS loaded: {len(rus_df):,} images')
    print(f'   ✓ WV loaded: {len(wv_df):,} images')
    
    # Filter only real images (is_real=1)
    print(f'\n🔍 Filtering real images only (is_real=1)...')
    grc_real = grc_df[grc_df['is_real'] == 1].copy()
    rus_real = rus_df[rus_df['is_real'] == 1].copy()
    wv_real = wv_df[wv_df['is_real'] == 1].copy()
    
    print(f'   GRC real images: {len(grc_real):,}')
    print(f'   RUS real images: {len(rus_real):,}')
    print(f'   WV real images: {len(wv_real):,}')
    
    # Sample first N images from each dataset
    print(f'\n✂️  Sampling first {samples_per_class} images from each dataset...')
    grc_sample = grc_real.head(samples_per_class).copy()
    rus_sample = rus_real.head(samples_per_class).copy()
    wv_sample = wv_real.head(samples_per_class).copy()
    
    print(f'   ✓ GRC sampled: {len(grc_sample)} images')
    print(f'   ✓ RUS sampled: {len(rus_sample)} images')
    print(f'   ✓ WV sampled: {len(wv_sample)} images')
    
    # Keep only essential columns: image_path and document_type
    print(f'\n📋 Selecting columns: image_path, document_type...')
    
    grc_final = grc_sample[['image_path', 'document_type']].copy()
    rus_final = rus_sample[['image_path', 'document_type']].copy()
    wv_final = wv_sample[['image_path', 'document_type']].copy()
    
    # Verify document types
    print(f'\n🔍 Verifying document types:')
    print(f'   GRC: {grc_final["document_type"].unique()}')
    print(f'   RUS: {rus_final["document_type"].unique()}')
    print(f'   WV: {wv_final["document_type"].unique()}')
    
    # Combine all datasets
    print(f'\n🔗 Combining all datasets...')
    combined_df = pd.concat([grc_final, rus_final, wv_final], ignore_index=True)
    
    print(f'   Total images: {len(combined_df):,}')
    print(f'\n📊 Document type distribution:')
    print(combined_df['document_type'].value_counts().to_string())
    
    # Save to CSV
    output_file = base_path / 'Document_Type_Classification_Dataset.csv'
    combined_df.to_csv(output_file, index=False)
    print(f'\n✅ Dataset saved to: {output_file}')
    
    # Print summary statistics
    print(f'\n' + '=' * 60)
    print(f'📈 SUMMARY')
    print(f'=' * 60)
    print(f'Total images: {len(combined_df):,}')
    print(f'Classes: {combined_df["document_type"].nunique()}')
    print(f'Images per class: {samples_per_class}')
    print(f'\nClass distribution:')
    for doc_type, count in combined_df['document_type'].value_counts().items():
        percentage = (count / len(combined_df)) * 100
        print(f'  • {doc_type}: {count} ({percentage:.1f}%)')
    
    print(f'\n✨ Dataset creation completed!')
    print(f'\nYou can now use this dataset for training a document type classifier.')
    print(f'Load it with: df = pd.read_csv("{output_file}")')
    
    return combined_df

if __name__ == "__main__":
    # Create dataset with 700 images per class
    df = create_document_type_classification_dataset(samples_per_class=700)
    
    print(f'\n📋 First few rows:')
    print(df.head(10).to_string())
    
    print(f'\n📋 Sample from each class:')
    for doc_type in df['document_type'].unique():
        print(f'\n{doc_type.upper()}:')
        print(df[df['document_type'] == doc_type].head(3).to_string())


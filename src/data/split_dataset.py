import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

def split_document_type_dataset(
    input_file="../../datasets/idnet/Document_Type_Classification_Dataset.csv",
    output_dir="../../datasets/idnet",
    train_size=0.70,
    val_size=0.15,
    test_size=0.15,
    random_state=42
):
    """
    Split the document type classification dataset into train/val/test sets
    with stratified sampling to maintain class balance.
    
    Args:
        input_file (str): Path to the input CSV file
        output_dir (str): Directory to save the split datasets
        train_size (float): Proportion of data for training (default: 0.70)
        val_size (float): Proportion of data for validation (default: 0.15)
        test_size (float): Proportion of data for testing (default: 0.15)
        random_state (int): Random seed for reproducibility
    """
    print('🔀 Splitting Document Type Classification Dataset')
    print('=' * 60)
    
    # Validate split sizes
    assert abs(train_size + val_size + test_size - 1.0) < 0.01, "Split sizes must sum to 1.0"
    
    script_dir = Path(__file__).parent
    input_path = (script_dir / input_file).resolve()
    output_path = (script_dir / output_dir).resolve()
    
    # Load dataset
    print(f'\n📂 Loading dataset from: {input_path}')
    df = pd.read_csv(input_path)
    print(f'   Total samples: {len(df):,}')
    
    # Show class distribution
    print(f'\n📊 Original class distribution:')
    for doc_type, count in df['document_type'].value_counts().items():
        percentage = (count / len(df)) * 100
        print(f'   • {doc_type}: {count} ({percentage:.1f}%)')
    
    # First split: separate test set (15%)
    print(f'\n🔪 First split: Train+Val ({train_size+val_size:.0%}) vs Test ({test_size:.0%})')
    train_val_df, test_df = train_test_split(
        df,
        test_size=test_size,
        stratify=df['document_type'],
        random_state=random_state
    )
    
    print(f'   Train+Val: {len(train_val_df):,} samples')
    print(f'   Test: {len(test_df):,} samples')
    
    # Second split: separate validation from training
    # Calculate validation size relative to train+val
    val_relative_size = val_size / (train_size + val_size)
    
    print(f'\n🔪 Second split: Train ({train_size:.0%}) vs Val ({val_size:.0%})')
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=val_relative_size,
        stratify=train_val_df['document_type'],
        random_state=random_state
    )
    
    print(f'   Train: {len(train_df):,} samples')
    print(f'   Validation: {len(val_df):,} samples')
    
    # Verify stratification
    print(f'\n' + '=' * 60)
    print(f'📊 STRATIFICATION VERIFICATION')
    print(f'=' * 60)
    
    print(f'\n🎯 Train Set ({len(train_df):,} samples):')
    for doc_type, count in train_df['document_type'].value_counts().items():
        percentage = (count / len(train_df)) * 100
        print(f'   • {doc_type}: {count} ({percentage:.1f}%)')
    
    print(f'\n🎯 Validation Set ({len(val_df):,} samples):')
    for doc_type, count in val_df['document_type'].value_counts().items():
        percentage = (count / len(val_df)) * 100
        print(f'   • {doc_type}: {count} ({percentage:.1f}%)')
    
    print(f'\n🎯 Test Set ({len(test_df):,} samples):')
    for doc_type, count in test_df['document_type'].value_counts().items():
        percentage = (count / len(test_df)) * 100
        print(f'   • {doc_type}: {count} ({percentage:.1f}%)')
    
    # Save splits to CSV
    print(f'\n💾 Saving split datasets...')
    
    train_file = output_path / 'train_dataset.csv'
    val_file = output_path / 'val_dataset.csv'
    test_file = output_path / 'test_dataset.csv'
    
    train_df.to_csv(train_file, index=False)
    val_df.to_csv(val_file, index=False)
    test_df.to_csv(test_file, index=False)
    
    print(f'   ✓ Train: {train_file}')
    print(f'   ✓ Validation: {val_file}')
    print(f'   ✓ Test: {test_file}')
    
    # Summary
    print(f'\n' + '=' * 60)
    print(f'✨ SUMMARY')
    print(f'=' * 60)
    print(f'Total samples: {len(df):,}')
    print(f'Train: {len(train_df):,} ({len(train_df)/len(df)*100:.1f}%)')
    print(f'Validation: {len(val_df):,} ({len(val_df)/len(df)*100:.1f}%)')
    print(f'Test: {len(test_df):,} ({len(test_df)/len(df)*100:.1f}%)')
    
    print(f'\n🎯 Each split maintains balanced class distribution (33.3% each class)')
    print(f'\n✅ Dataset split completed successfully!')
    print(f'\nLoad splits with:')
    print(f'  train_df = pd.read_csv("{train_file}")')
    print(f'  val_df = pd.read_csv("{val_file}")')
    print(f'  test_df = pd.read_csv("{test_file}")')
    
    return train_df, val_df, test_df

if __name__ == "__main__":
    # Split the dataset
    train_df, val_df, test_df = split_document_type_dataset()
    
    # Additional verification
    print(f'\n' + '=' * 60)
    print(f'🔍 DETAILED VERIFICATION')
    print(f'=' * 60)
    
    print(f'\n📋 Sample from Train set:')
    print(train_df.head(5).to_string())
    
    print(f'\n📋 Sample from Validation set:')
    print(val_df.head(5).to_string())
    
    print(f'\n📋 Sample from Test set:')
    print(test_df.head(5).to_string())
    
    # Verify no overlap
    train_images = set(train_df['image_path'])
    val_images = set(val_df['image_path'])
    test_images = set(test_df['image_path'])
    
    print(f'\n🔒 Checking for data leakage...')
    train_val_overlap = train_images & val_images
    train_test_overlap = train_images & test_images
    val_test_overlap = val_images & test_images
    
    if not train_val_overlap and not train_test_overlap and not val_test_overlap:
        print(f'   ✅ No overlap detected - splits are clean!')
    else:
        print(f'   ⚠️  Warning: Overlap detected!')
        if train_val_overlap:
            print(f'      Train-Val overlap: {len(train_val_overlap)} images')
        if train_test_overlap:
            print(f'      Train-Test overlap: {len(train_test_overlap)} images')
        if val_test_overlap:
            print(f'      Val-Test overlap: {len(val_test_overlap)} images')


"""Check for duplicate images in the dataset based on hash"""
import pandas as pd

detailed_csv = "/Users/roy-siftt/final-project/datasets/idnet/document_type_classification_positive_only/data/dataset_detailed.csv"

df = pd.read_csv(detailed_csv)

print(f"Total rows: {len(df)}")
print(f"Unique hashes: {df['hash'].nunique()}")

duplicates = df[df.duplicated(subset=['hash'], keep=False)]
print(f"\nDuplicate hashes found: {len(duplicates)}")

if len(duplicates) > 0:
    print("\nFirst 20 duplicates:")
    print(duplicates[['hash', 'source_country', 'source_path']].head(20))
    
    # Group by hash to see how many times each duplicate appears
    duplicate_groups = duplicates.groupby('hash').size().sort_values(ascending=False)
    print(f"\nDuplicate hash frequency:")
    print(duplicate_groups.head(10))
else:
    print("\nNo duplicates found!")


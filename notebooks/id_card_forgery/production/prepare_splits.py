"""
Create train/val/test splits for the 20K ID card dataset.
Uses GroupShuffleSplit on original_id to prevent data leakage.

Split strategy: 80/10/10.

Usage: python notebooks/id_card_forgery/production/prepare_splits.py
"""
import os
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

PROJECT_ROOT = "/Users/roy-siftt/final-project"
DATASET_CSV = os.path.join(PROJECT_ROOT, "datasets/id_card_20k/dataset.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "notebooks/id_card_forgery/production/data")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(DATASET_CSV)
    print(f"Total images: {len(df)}")
    print(f"Unique subjects (original_id): {df['original_id'].nunique()}")
    print(f"\nBalance:")
    print(f"  Real: {(df['is_fake'] == 0).sum()} | Fake: {(df['is_fake'] == 1).sum()}")
    print(f"  Countries: {df['source_country'].value_counts().to_dict()}")

    # Split 1: Train (80%) and Temp (20%)
    splitter1 = GroupShuffleSplit(test_size=0.2, n_splits=1, random_state=42)
    train_idx, temp_idx = next(splitter1.split(df, groups=df['original_id']))

    train_df = df.iloc[train_idx].reset_index(drop=True)
    temp_df = df.iloc[temp_idx].reset_index(drop=True)

    # Split 2: Val (50% of temp = 10%) and Test (50% of temp = 10%)
    splitter2 = GroupShuffleSplit(test_size=0.5, n_splits=1, random_state=42)
    val_idx, test_idx = next(splitter2.split(temp_df, groups=temp_df['original_id']))

    val_df = temp_df.iloc[val_idx].reset_index(drop=True)
    test_df = temp_df.iloc[test_idx].reset_index(drop=True)

    # Save
    train_df.to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
    val_df.to_csv(os.path.join(OUTPUT_DIR, "val.csv"), index=False)
    test_df.to_csv(os.path.join(OUTPUT_DIR, "test.csv"), index=False)
    df.to_csv(os.path.join(OUTPUT_DIR, "dataset.csv"), index=False)

    # Verify
    print(f"\nSplits created:")
    print(f"  Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Val:   {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"  Test:  {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")

    # Balance check per split
    for name, split_df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        real = (split_df['is_fake'] == 0).sum()
        fake = (split_df['is_fake'] == 1).sum()
        print(f"\n  {name} balance: Real={real} ({real/len(split_df)*100:.1f}%), Fake={fake} ({fake/len(split_df)*100:.1f}%)")

    # Leakage check
    train_ids = set(train_df['original_id'])
    val_ids = set(val_df['original_id'])
    test_ids = set(test_df['original_id'])

    leak_tv = train_ids & val_ids
    leak_tt = train_ids & test_ids
    leak_vt = val_ids & test_ids

    print(f"\nLeakage check:")
    print(f"  Train-Val overlap:  {len(leak_tv)} {'PASS' if len(leak_tv) == 0 else 'FAIL'}")
    print(f"  Train-Test overlap: {len(leak_tt)} {'PASS' if len(leak_tt) == 0 else 'FAIL'}")
    print(f"  Val-Test overlap:   {len(leak_vt)} {'PASS' if len(leak_vt) == 0 else 'FAIL'}")

    print(f"\nFiles saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

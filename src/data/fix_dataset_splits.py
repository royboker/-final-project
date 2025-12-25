#!/usr/bin/env python3
"""
סקריפט לתיקון פיצול ה-datasets לפי תמונות בסיס (base images)
מונע חפיפות בין train/val/test ברמת תמונות הבסיס
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path
import os

def extract_base_image_id(image_path):
    """
    מחלץ את ה-base image ID מתמונת הבסיס
    לדוגמה: generated.photos_v3_0246269_0101561_0614321.png -> generated.photos_v3_0246269
    """
    filename = os.path.basename(image_path)
    # הסרת .png
    filename = filename.replace('.png', '')
    
    # חילוץ base ID - לוקח את 3 החלקים הראשונים
    parts = filename.split('_')
    if len(parts) >= 3:
        # generated.photos.v3 + המספר הראשון
        base_id = '_'.join(parts[:3])
        return base_id
    return filename

def group_by_base_id(df):
    """
    מקובץ את כל התמונות לפי base image ID
    מחזיר dict: {base_id: [dataframe rows]}
    """
    base_id_groups = defaultdict(list)
    
    for idx, row in df.iterrows():
        base_id = extract_base_image_id(row['image_path'])
        base_id_groups[base_id].append({
            'image_path': row['image_path'],
            'document_type': row['document_type'],
            'base_id': base_id
        })
    
    return base_id_groups

def split_base_ids_by_class(base_id_groups, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
    """
    מחלק את base IDs ל-train/val/test לפי מחלקות
    מוודא שכל base ID מופיע רק בסט אחד
    """
    # קיבוץ לפי מחלקה
    class_groups = defaultdict(list)
    for base_id, images in base_id_groups.items():
        # כל התמונות באותו base_id צריכות להיות מאותה מחלקה
        document_type = images[0]['document_type']
        class_groups[document_type].append(base_id)
    
    train_base_ids = []
    val_base_ids = []
    test_base_ids = []
    
    # חלוקה לכל מחלקה בנפרד
    for doc_type, base_ids in class_groups.items():
        np.random.seed(42)  # לשם reproducible split
        np.random.shuffle(base_ids)
        
        n_total = len(base_ids)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        
        train_base_ids.extend(base_ids[:n_train])
        val_base_ids.extend(base_ids[n_train:n_train+n_val])
        test_base_ids.extend(base_ids[n_train+n_val:])
        
        print(f"  {doc_type:15s}: Train={n_train}, Val={n_val}, Test={n_total-n_train-n_val}")
    
    return set(train_base_ids), set(val_base_ids), set(test_base_ids)

def create_datasets(base_id_groups, train_base_ids, val_base_ids, test_base_ids):
    """
    יוצר את ה-datasets הסופיים
    עבור כל base ID, לוקח את כל ה-variants שלו (augmentations)
    """
    train_data = []
    val_data = []
    test_data = []
    
    for base_id, images in base_id_groups.items():
        if base_id in train_base_ids:
            for img in images:
                train_data.append({
                    'image_path': img['image_path'],
                    'document_type': img['document_type']
                })
        elif base_id in val_base_ids:
            for img in images:
                val_data.append({
                    'image_path': img['image_path'],
                    'document_type': img['document_type']
                })
        elif base_id in test_base_ids:
            for img in images:
                test_data.append({
                    'image_path': img['image_path'],
                    'document_type': img['document_type']
                })
    
    train_df = pd.DataFrame(train_data)
    val_df = pd.DataFrame(val_data)
    test_df = pd.DataFrame(test_data)
    
    return train_df, val_df, test_df

def verify_no_overlap(train_df, val_df, test_df):
    """מוודא שאין חפיפות ברמת base IDs"""
    
    def get_base_ids(df):
        return set([extract_base_image_id(path) for path in df['image_path'].unique()])
    
    train_base_ids = get_base_ids(train_df)
    val_base_ids = get_base_ids(val_df)
    test_base_ids = get_base_ids(test_df)
    
    train_val_overlap = train_base_ids & val_base_ids
    train_test_overlap = train_base_ids & test_base_ids
    val_test_overlap = val_base_ids & test_base_ids
    
    if train_val_overlap or train_test_overlap or val_test_overlap:
        print("\n❌ עדיין יש חפיפות!")
        if train_val_overlap:
            print(f"  Train ∩ Val: {len(train_val_overlap)}")
        if train_test_overlap:
            print(f"  Train ∩ Test: {len(train_test_overlap)}")
        if val_test_overlap:
            print(f"  Val ∩ Test: {len(val_test_overlap)}")
        return False
    else:
        print("\n✅ אין חפיפות! הכל תקין")
        return True

def main():
    print("=" * 70)
    print("תיקון פיצול Datasets לפי Base Images")
    print("=" * 70)
    
    # קריאת full dataset
    data_dir = Path('datasets/idnet/document_type_classification/data')
    full_dataset_path = data_dir / 'full_dataset.csv'
    
    print(f"\n📖 קורא full_dataset...")
    full_df = pd.read_csv(full_dataset_path)
    print(f"  סה\"כ תמונות: {len(full_df)}")
    
    # קיבוץ לפי base ID
    print(f"\n🔍 מקובץ לפי Base Image ID...")
    base_id_groups = group_by_base_id(full_df)
    print(f"  סה\"כ base images: {len(base_id_groups)}")
    
    # ספירת variants לכל base ID
    variant_counts = [len(images) for images in base_id_groups.values()]
    print(f"  ממוצע variants לכל base image: {np.mean(variant_counts):.1f}")
    print(f"  מקסימום variants: {max(variant_counts)}")
    print(f"  מינימום variants: {min(variant_counts)}")
    
    # חלוקה ל-train/val/test
    print(f"\n📊 מחלק ל-train/val/test לפי base IDs...")
    train_base_ids, val_base_ids, test_base_ids = split_base_ids_by_class(
        base_id_groups,
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15
    )
    
    print(f"\n  סה\"כ base IDs:")
    print(f"    Train: {len(train_base_ids)}")
    print(f"    Val:   {len(val_base_ids)}")
    print(f"    Test:  {len(test_base_ids)}")
    
    # יצירת datasets
    print(f"\n🔨 יוצר datasets...")
    train_df, val_df, test_df = create_datasets(
        base_id_groups,
        train_base_ids,
        val_base_ids,
        test_base_ids
    )
    
    print(f"  Train:  {len(train_df)} תמונות")
    print(f"  Val:    {len(val_df)} תמונות")
    print(f"  Test:   {len(test_df)} תמונות")
    
    # בדיקת התפלגות מחלקות
    print(f"\n📊 התפלגות מחלקות:")
    for name, df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        print(f"  {name}:")
        dist = df['document_type'].value_counts()
        for doc_type, count in dist.items():
            pct = (count / len(df)) * 100
            print(f"    {doc_type:15s}: {count:4d} ({pct:5.1f}%)")
    
    # בדיקת חפיפות
    print(f"\n🔍 בודק חפיפות...")
    if verify_no_overlap(train_df, val_df, test_df):
        # שמירת הקבצים
        print(f"\n💾 שומר קבצים...")
        
        # גיבוי קבצים ישנים
        backup_dir = data_dir / 'backup'
        backup_dir.mkdir(exist_ok=True)
        
        for filename in ['train_dataset.csv', 'val_dataset.csv', 'test_dataset.csv']:
            old_path = data_dir / filename
            if old_path.exists():
                backup_path = backup_dir / filename
                import shutil
                shutil.copy(old_path, backup_path)
                print(f"  גיבוי: {filename} -> backup/{filename}")
        
        # שמירת קבצים חדשים
        train_df.to_csv(data_dir / 'train_dataset.csv', index=False)
        val_df.to_csv(data_dir / 'val_dataset.csv', index=False)
        test_df.to_csv(data_dir / 'test_dataset.csv', index=False)
        
        print(f"\n✅ הקבצים נשמרו בהצלחה!")
        print(f"  {data_dir / 'train_dataset.csv'}")
        print(f"  {data_dir / 'val_dataset.csv'}")
        print(f"  {data_dir / 'test_dataset.csv'}")
        print(f"\n📁 גיבויים נשמרו ב: {backup_dir}")
    else:
        print(f"\n❌ יש בעיה - הקבצים לא נשמרו!")
        return
    
    print("\n" + "=" * 70)
    print("✅ תהליך הושלם בהצלחה!")
    print("=" * 70)

if __name__ == '__main__':
    main()


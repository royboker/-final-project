import pandas as pd
import os

csv_path = 'datasets/drivers_license_balanced/dataset.csv'

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f"Total rows: {len(df)}")
    print("\nCounts per label:")
    print(df['label_name'].value_counts())
    
    # Calculate percentages
    counts = df['label_name'].value_counts()
    total = len(df)
    print("\nPercentages:")
    for label, count in counts.items():
        print(f"{label}: {count/total*100:.2f}%")
else:
    print("Dataset CSV not found!")


import os

roots = ['datasets/idnet/WV', 'datasets/idnet/DC', 'datasets/idnet/AZ']
folders = ['positive', 'fraud2_face_morphing', 'fraud3_face_replacement']

total_counts = {f: 0 for f in folders}

for root in roots:
    print(f"Checking {root}...")
    for folder in folders:
        # Check direct path
        path = os.path.join(root, folder)
        if not os.path.exists(path):
            # Check nested country path (e.g. WV/WV/positive)
            country_code = os.path.basename(root)
            path = os.path.join(root, country_code, folder)
        
        if os.path.exists(path):
            count = len([name for name in os.listdir(path) if name.lower().endswith(('.png', '.jpg', '.jpeg'))])
            print(f"  {folder}: {count}")
            total_counts[folder] += count
        else:
            print(f"  {folder}: Not found")

print("\nTotal Counts:")
for f, c in total_counts.items():
    print(f"{f}: {c}")


"""
Simple script to explore the IDNet dataset
"""
from pathlib import Path
from collections import Counter
from PIL import Image
import numpy as np


def explore_dataset(dataset_path="datasets/idnet"):
    """Explore the IDNet dataset structure"""
    
    path = Path(dataset_path)
    
    print(f"📁 Exploring: {path.resolve()}\n")
    
    # Find all ZIP files
    zip_files = list(path.glob("*.zip"))
    if zip_files:
        print("📦 ZIP Files:")
        for zip_file in zip_files:
            size_gb = zip_file.stat().st_size / (1024**3)
            print(f"  - {zip_file.name}: {size_gb:.2f} GB")
        print()
    
    # Find directories (extracted countries)
    dirs = [d for d in path.iterdir() if d.is_dir()]
    if dirs:
        print(f"📂 Extracted Directories:")
        for dir in dirs:
            all_files = list(dir.rglob("*"))
            files = [f for f in all_files if f.is_file()]
            
            # Count file types
            extensions = Counter([f.suffix.lower() for f in files if f.suffix])
            
            print(f"\n  {dir.name}/")
            print(f"    Total files: {len(files)}")
            print(f"    File types: {dict(extensions)}")
            
            # Sample image if exists
            image_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
            images = [f for f in files if f.suffix.lower() in image_exts]
            
            if images:
                print(f"    Images: {len(images)}")
                
                # Analyze sample images
                sample_size = min(20, len(images))
                sample = np.random.choice(images, sample_size, replace=False)
                
                widths, heights = [], []
                for img_path in sample:
                    try:
                        img = Image.open(img_path)
                        w, h = img.size
                        widths.append(w)
                        heights.append(h)
                    except:
                        continue
                
                if widths:
                    print(f"    Avg dimensions: {int(np.mean(widths))}x{int(np.mean(heights))}")
    else:
        print("⚠️  No extracted directories found yet.")
        print("   Waiting for unzip to complete...")


if __name__ == "__main__":
    explore_dataset()


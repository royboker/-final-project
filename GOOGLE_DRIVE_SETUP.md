# Google Drive Setup Instructions

## 📁 Google Drive Structure

Your Google Drive folder: [final-project-datasets](https://drive.google.com/drive/folders/1flQv8CqWEgxHyZUh0k17gAo0wrrMooYz?usp=sharing)

```
final-project-datasets/
└── IDNET/
    ├── GRC/
    │   ├── positive/                    # תמונות אמיתיות
    │   ├── fraud1_copy_and_move/       # תמונות מזויפות
    │   ├── fraud2_face_morphing/       # תמונות מזויפות
    │   ├── fraud3_face_replacement/    # תמונות מזויפות
    │   ├── fraud4_combined/            # תמונות מזויפות
    │   ├── fraud5_inpaint_and_rewrite/ # תמונות מזויפות
    │   ├── fraud6_crop_and_replace/    # תמונות מזויפות
    │   └── meta/                       # קבצי metadata
    ├── RUS/
    │   ├── positive/
    │   ├── fraud1_.../
    │   └── meta/
    └── WV/
        ├── positive/
        ├── fraud1_.../
        └── meta/
```

## 🚀 Setup Steps

### 1. Clone the Repository
```bash
git clone https://github.com/username/repository-name.git
cd repository-name
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Access Google Drive Data
- **Request access** to the Google Drive folder
- **Copy the folder** to your Google Drive (optional, for faster access)
- **Update CSV files** with Google Drive URLs (see below)

## 🔄 Updating CSV Files

### Option A: Automatic Update (Recommended)
```bash
cd src/utils
python update_csv_to_drive.py
```

### Option B: Manual Update
1. Open each CSV file
2. Replace local paths with Google Drive URLs
3. Save the files

## 📝 Using the Drive Loader

### In Jupyter Notebooks:
```python
from src.utils.drive_loader import load_image_from_drive

# Load image from Google Drive
img = load_image_from_drive("https://drive.google.com/file/d/...")
```

### In Python Scripts:
```python
import sys
sys.path.append('src')
from utils.drive_loader import load_image_from_drive

# Load image
img = load_image_from_drive(drive_url)
```

## 🔧 Troubleshooting

### Common Issues:

1. **"File not found" errors**
   - Check if the Google Drive URL is correct
   - Verify the file exists in the Drive folder
   - Make sure you have access to the folder

2. **Slow loading**
   - Google Drive can be slow for large files
   - Consider downloading frequently used files locally
   - Use the fallback mechanism in `drive_loader.py`

3. **Permission errors**
   - Make sure the Google Drive folder is shared with you
   - Check if the sharing settings allow access

### Testing Connection:
```python
from src.utils.drive_loader import test_drive_connection

# Test if a URL is accessible
url = "https://drive.google.com/file/d/..."
is_accessible = test_drive_connection(url)
print(f"URL accessible: {is_accessible}")
```

## 📊 Data Access

### Current CSV Files:
- `datasets/idnet/document_type_classification/data/full_dataset.csv`
- `datasets/idnet/document_type_classification/data/train_dataset.csv`
- `datasets/idnet/document_type_classification/data/val_dataset.csv`
- `datasets/idnet/document_type_classification/data/test_dataset.csv`

### After Update:
All `image_path` columns will contain Google Drive URLs instead of local paths.

## 🎯 Next Steps

1. **Update CSV files** with Google Drive URLs
2. **Test the drive loader** with a few sample images
3. **Run the notebooks** to verify everything works
4. **Share the repository** with collaborators

## 📞 Support

If you encounter issues:
1. Check the Google Drive folder access
2. Verify the CSV file URLs are correct
3. Test the drive loader with sample URLs
4. Check the error messages in the console

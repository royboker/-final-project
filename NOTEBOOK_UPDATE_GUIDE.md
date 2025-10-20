# Notebook Update Guide for Google Drive Integration

## 🔄 Required Changes in Notebooks

### 1. Import the Drive Loader

**Add this import at the beginning of each notebook:**

```python
# Add to the imports section
import sys
sys.path.append('src')
from utils.drive_loader import load_image_from_drive
```

### 2. Replace Image Loading Functions

**Find this pattern in notebooks:**
```python
# OLD - Local file loading
img = Image.open(image_path)
```

**Replace with:**
```python
# NEW - Google Drive loading
img = load_image_from_drive(image_path)
```

### 3. Update Data Generators

**In notebooks that use Keras data generators:**

**OLD:**
```python
train_generator = train_datagen.flow_from_dataframe(
    dataframe=train_df,
    x_col='image_path',
    y_col='document_type',
    target_size=TARGET_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)
```

**NEW:**
```python
# Custom data generator for Google Drive
def custom_data_generator(dataframe, datagen, target_size, batch_size, class_mode):
    while True:
        batch_indices = np.random.choice(len(dataframe), batch_size)
        batch_data = dataframe.iloc[batch_indices]
        
        images = []
        labels = []
        
        for _, row in batch_data.iterrows():
            # Load image from Google Drive
            img = load_image_from_drive(row['image_path'])
            img = img.resize(target_size)
            img_array = np.array(img) / 255.0  # Normalize
            
            images.append(img_array)
            
            # Convert label to categorical
            if class_mode == 'categorical':
                label = to_categorical(row['document_type'], num_classes=3)
                labels.append(label)
            else:
                labels.append(row['document_type'])
        
        yield np.array(images), np.array(labels)

# Use custom generator
train_generator = custom_data_generator(
    dataframe=train_df,
    datagen=train_datagen,
    target_size=TARGET_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)
```

### 4. Update Image Display Functions

**For displaying sample images:**

**OLD:**
```python
def display_sample_images(df, num_samples=3):
    fig, axes = plt.subplots(1, num_samples, figsize=(15, 5))
    
    for i, (_, row) in enumerate(df.head(num_samples).iterrows()):
        img = Image.open(row['image_path'])
        axes[i].imshow(img)
        axes[i].set_title(row['document_type'])
        axes[i].axis('off')
```

**NEW:**
```python
def display_sample_images(df, num_samples=3):
    fig, axes = plt.subplots(1, num_samples, figsize=(15, 5))
    
    for i, (_, row) in enumerate(df.head(num_samples).iterrows()):
        try:
            img = load_image_from_drive(row['image_path'])
            axes[i].imshow(img)
            axes[i].set_title(row['document_type'])
            axes[i].axis('off')
        except Exception as e:
            print(f"Error loading image {i}: {e}")
            axes[i].text(0.5, 0.5, f"Error loading\n{row['document_type']}", 
                        ha='center', va='center', transform=axes[i].transAxes)
            axes[i].axis('off')
```

### 5. Add Error Handling

**Add try-catch blocks for robust loading:**

```python
def safe_load_image(drive_url, max_retries=3):
    """Safely load image from Google Drive with retries"""
    for attempt in range(max_retries):
        try:
            return load_image_from_drive(drive_url)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(2 ** attempt)
            else:
                print(f"Failed to load image after {max_retries} attempts: {e}")
                return None
```

## 📝 Specific Notebook Updates

### 01_data_exploration_and_visualization.ipynb

**Changes needed:**
1. Add drive loader import
2. Replace `Image.open()` calls with `load_image_from_drive()`
3. Add error handling for image loading
4. Update image display functions

### 02_data_preprocessing_and_augmentation.ipynb

**Changes needed:**
1. Add drive loader import
2. Replace `Image.open()` calls with `load_image_from_drive()`
3. Update data generators to use custom Google Drive loader
4. Add error handling for batch loading

## 🧪 Testing the Updates

### Test 1: Load Single Image
```python
# Test loading one image
test_url = "https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing"
img = load_image_from_drive(test_url)
print(f"Image loaded successfully: {img.size}")
```

### Test 2: Load Batch of Images
```python
# Test loading multiple images
sample_df = train_df.head(5)
for _, row in sample_df.iterrows():
    try:
        img = load_image_from_drive(row['image_path'])
        print(f"✅ Loaded: {row['document_type']}")
    except Exception as e:
        print(f"❌ Failed: {row['document_type']} - {e}")
```

### Test 3: Check Drive Connection
```python
from utils.drive_loader import test_drive_connection

# Test connection
test_url = "https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing"
is_accessible = test_drive_connection(test_url)
print(f"Drive accessible: {is_accessible}")
```

## ⚠️ Important Notes

1. **Google Drive URLs** - Make sure all URLs in CSV files are correct
2. **Access Permissions** - Ensure you have access to the Google Drive folder
3. **Rate Limiting** - Google Drive may have rate limits, add delays if needed
4. **Error Handling** - Always wrap image loading in try-catch blocks
5. **Caching** - Consider caching frequently used images locally

## 🚀 Next Steps

1. **Update notebooks** with the changes above
2. **Test image loading** with sample URLs
3. **Run data exploration** to verify everything works
4. **Update data generators** for model training
5. **Test end-to-end** workflow

## 📞 Troubleshooting

### Common Issues:

1. **"File not found"** - Check Google Drive URL format
2. **"Permission denied"** - Verify Drive folder access
3. **"Slow loading"** - Add retry logic and delays
4. **"Memory issues"** - Use smaller batch sizes

### Debug Commands:

```python
# Check URL format
print(f"URL: {drive_url}")
file_id = extract_file_id_from_drive_url(drive_url)
print(f"File ID: {file_id}")

# Test direct download
direct_url = convert_to_direct_download_url(drive_url)
print(f"Direct URL: {direct_url}")
```

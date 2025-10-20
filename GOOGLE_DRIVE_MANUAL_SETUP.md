# Google Drive Manual Setup Guide

## 🚨 **הבעיה הנוכחית**

ה-URLs שיצרנו לא עובדים כי הם לא נכונים. צריך ליצור URLs נכונים לכל תמונה.

## 🔧 **הפתרון - Setup ידני**

### **שלב 1: יצירת מיפוי קבצים**

```bash
cd src/utils
python3 create_drive_mapping.py
```

זה ייצור קבצי JSON עם רשימת כל התמונות שצריכות Google Drive URLs.

### **שלב 2: קבלת Google Drive URLs**

**עבור כל תמונה ב-Google Drive:**

1. **פתח את התמונה** ב-Google Drive
2. **לחץ ימין** על התמונה
3. **"Get link"** או **"קבל קישור"**
4. **"Copy link"** או **"העתק קישור"**
5. **שמור את הקישור**

**דוגמה לקישור נכון:**
```
https://drive.google.com/file/d/1ABC123DEF456GHI789JKL/view?usp=sharing
```

### **שלב 3: עדכון קבצי המיפוי**

**פתח כל קובץ `mapping_*.json` ועדכן:**

```json
{
  "local_path": "/Users/roy-siftt/final-project/datasets/idnet/GRC/GRC/positive/generated.photos_v3_0240363.png",
  "relative_path": "GRC/GRC/positive/generated.photos_v3_0240363.png",
  "document_type": "passport",
  "google_drive_url": "https://drive.google.com/file/d/1ABC123DEF456GHI789JKL/view?usp=sharing",
  "file_id": "1ABC123DEF456GHI789JKL"
}
```

### **שלב 4: עדכון ה-CSV files**

```bash
python3 update_csv_with_mapping.py
```

## 🎯 **גישה חלופית - עבודה עם תיקיות**

### **אם יש לך הרבה תמונות, אפשר לעבוד עם תיקיות:**

1. **שתף כל תיקייה** (positive, fraud1, וכו')
2. **קבל קישור לתיקייה**
3. **עדכן את הסקריפט** לעבוד עם תיקיות

### **דוגמה לעבודה עם תיקיות:**

```python
# במקום קישור לתמונה בודדת
image_url = "https://drive.google.com/file/d/1ABC123.../view?usp=sharing"

# עבוד עם קישור לתיקייה
folder_url = "https://drive.google.com/drive/folders/1XYZ789..."
image_path = "GRC/GRC/positive/generated.photos_v3_0240363.png"
```

## 🚀 **גישה מהירה - עבודה עם דוגמאות**

### **אם יש לך הרבה תמונות, אפשר לעבוד רק עם דוגמאות:**

1. **בחר 10-20 תמונות** מכל קטגוריה
2. **צור URLs רק עבורן**
3. **עבוד עם דוגמאות** במקום כל הנתונים

### **דוגמה:**

```python
# עבוד רק עם דוגמאות
sample_df = full_df.sample(100)  # 100 תמונות אקראיות

# במקום כל ה-2,100 תמונות
```

## 📝 **הוראות מפורטות**

### **1. עבודה עם Google Drive API (מתקדם)**

אם יש לך הרבה תמונות, אפשר להשתמש ב-Google Drive API:

```python
from googleapiclient.discovery import build

# הגדרת API
service = build('drive', 'v3', credentials=credentials)

# רשימת קבצים בתיקייה
results = service.files().list(
    q="'FOLDER_ID' in parents",
    fields="files(id, name, webViewLink)"
).execute()
```

### **2. עבודה עם Google Drive Desktop**

1. **התקן Google Drive Desktop**
2. **סנכרן את התיקייה** עם המחשב
3. **עבוד עם נתיבים מקומיים** (הם יסונכרנו אוטומטית)

### **3. עבודה עם Google Colab**

```python
# ב-Google Colab
from google.colab import drive
drive.mount('/content/drive')

# עבוד עם נתיבים מקומיים
image_path = '/content/drive/MyDrive/final-project-datasets/IDNET/GRC/GRC/positive/generated.photos_v3_0240363.png'
```

## ⚠️ **הערות חשובות**

1. **Google Drive URLs** חייבים להיות קישורי שיתוף נכונים
2. **File IDs** חייבים להיות נכונים
3. **הרשאות** - ודא שיש לך גישה לכל הקבצים
4. **Rate Limits** - Google Drive עלול להגביל בקשות

## 🎯 **המלצה**

**עבור התחלה מהירה:**
1. **עבוד עם דוגמאות** (100-200 תמונות)
2. **צור URLs ידנית** עבור הדוגמאות
3. **בדוק שהכל עובד**
4. **הרחב בהדרגה** לכל הנתונים

**האם תרצה שאעזור לך עם אחת מהגישות האלה?**

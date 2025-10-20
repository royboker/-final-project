# Google Drive Desktop Setup - הפתרון הפשוט

## 🎯 **למה Google Drive Desktop?**

הקישורים שיצרנו לא עובדים כי Google Drive לא יודע איך לפרש נתיבי קבצים אחרי URL של תיקייה. Google Drive Desktop פותר את זה!

## 📥 **התקנה:**

### 1. הורד Google Drive Desktop
- לך ל: https://www.google.com/drive/download/
- הורד עבור Mac
- התקן את האפליקציה

### 2. התחבר לחשבון Google
- פתח את Google Drive Desktop
- התחבר עם אותו חשבון Google שיש לך את התיקייה

### 3. סנכרן את התיקייה
- לחץ על "Add folder"
- בחר "Choose folder"
- בחר את התיקייה: `final-project-datasets`
- לחץ "Done"

## 🔄 **איך זה יעבוד:**

### **לפני (לא עובד):**
```python
# URL שלא עובד
url = "https://drive.google.com/drive/u/1/folders/1flQv8CqWEgxHyZUh0k17gAo0wrrMooYz/IDNET/GRC/positive/generated.photos_v3_0609594.png"
img = load_image_from_drive(url)  # ❌ לא עובד
```

### **אחרי (עובד):**
```python
# נתיב מקומי שנסונכרן אוטומטית
local_path = "/Users/roy-siftt/Google Drive/final-project-datasets/IDNET/GRC/positive/generated.photos_v3_0609594.png"
img = Image.open(local_path)  # ✅ עובד!
```

## 🔧 **עדכון ה-CSV files:**

### **שלב 1: מצא את הנתיב המקומי**
אחרי הסנכרון, Google Drive Desktop ייצור נתיב מקומי כמו:
```
/Users/roy-siftt/Google Drive/final-project-datasets/IDNET/GRC/positive/
```

### **שלב 2: עדכן את ה-CSV files**
```python
# סקריפט לעדכון נתיבים
import pandas as pd

def update_to_local_paths(csv_file):
    df = pd.read_csv(csv_file)
    
    # החלף נתיבים
    df['image_path'] = df['image_path'].str.replace(
        '/Users/roy-siftt/final-project/datasets/idnet/',
        '/Users/roy-siftt/Google Drive/final-project-datasets/IDNET/'
    )
    
    # שמור
    df.to_csv(csv_file, index=False)
    print(f"Updated {csv_file}")

# עדכן את כל הקבצים
csv_files = [
    'datasets/idnet/document_type_classification/data/full_dataset.csv',
    'datasets/idnet/document_type_classification/data/train_dataset.csv',
    'datasets/idnet/document_type_classification/data/val_dataset.csv',
    'datasets/idnet/document_type_classification/data/test_dataset.csv'
]

for csv_file in csv_files:
    update_to_local_paths(csv_file)
```

## 🚀 **יתרונות:**

✅ **עובד מיד** - לא צריך API או קישורים מורכבים  
✅ **סנכרון אוטומטי** - כל שינוי ב-Drive מתעדכן במחשב  
✅ **עבודה מקומית** - מהיר כמו קבצים מקומיים  
✅ **גישה משותפת** - כולם יכולים לגשת לאותם קבצים  
✅ **גרסאות** - Google Drive שומר היסטוריה  

## 📝 **הוראות מפורטות:**

### 1. **התקן Google Drive Desktop**
```bash
# הורד מהאתר הרשמי
open https://www.google.com/drive/download/
```

### 2. **סנכרן את התיקייה**
- פתח Google Drive Desktop
- לחץ על "+" (Add folder)
- בחר "Choose folder"
- בחר את התיקייה `final-project-datasets`
- לחץ "Done"

### 3. **בדוק את הנתיב המקומי**
```bash
# בדוק איפה נמצאת התיקייה
ls -la "/Users/roy-siftt/Google Drive/"
```

### 4. **עדכן את ה-CSV files**
```python
# הרץ את הסקריפט לעדכון נתיבים
python3 update_to_local_paths.py
```

### 5. **בדוק שהכל עובד**
```python
# בדוק טעינת תמונה
from PIL import Image
img = Image.open("/Users/roy-siftt/Google Drive/final-project-datasets/IDNET/GRC/positive/generated.photos_v3_0609594.png")
print(f"Image loaded: {img.size}")
```

## ⚠️ **הערות חשובות:**

1. **נתיב התיקייה** - יכול להיות שונה במחשב שלך
2. **סנכרון** - יכול לקחת זמן בהתחלה
3. **מקום דיסק** - Google Drive Desktop יוריד את כל הקבצים
4. **עדכונים** - כל שינוי ב-Drive יתעדכן אוטומטית

## 🎯 **האם תרצה לנסות את זה?**

זה הפתרון הפשוט והאמין ביותר. Google Drive Desktop יטפל בכל הבעיות הטכניות ואתה תוכל לעבוד עם הנתונים כמו קבצים מקומיים רגילים.

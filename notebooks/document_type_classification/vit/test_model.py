"""
סקריפט לבדיקת מודל ViT לזיהוי סוג מסמך
"""
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import sys
import os

class ViTClassifier(nn.Module):
    def __init__(self, num_classes=3, pretrained=True, dropout=0.3):
        super(ViTClassifier, self).__init__()
        if pretrained:
            self.vit = models.vit_b_32(weights=models.ViT_B_32_Weights.IMAGENET1K_V1)
        else:
            self.vit = models.vit_b_32(weights=None)
        
        num_features = self.vit.heads.head.in_features
        self.vit.heads.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(num_features, num_classes)
        )
        
    def forward(self, x):
        return self.vit(x)

# מיפוי תוויות
label_map = {
    0: "תעודת זהות (ID Card)",
    1: "דרכון (Passport)",
    2: "רישיון נהיגה (Driver License)"
}

def load_model(model_path, device):
    """טוען את המודל המאומן"""
    model = ViTClassifier(num_classes=3, pretrained=True, dropout=0.3)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model

def preprocess_image(image_path):
    """מעבד את התמונה לפני הזנתה למודל"""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                            std=[0.229, 0.224, 0.225])
    ])
    
    img = Image.open(image_path).convert("RGB")
    img_tensor = transform(img).unsqueeze(0)  # מוסיף batch dimension
    return img_tensor, img

def predict_image(model, image_path, device):
    """חוזה את סוג המסמך בתמונה"""
    # טעינת ועיבוד התמונה
    img_tensor, original_img = preprocess_image(image_path)
    img_tensor = img_tensor.to(device)
    
    # חיזוי
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        predicted_class = torch.argmax(outputs, dim=1).item()
        confidence = probabilities[0][predicted_class].item()
    
    return predicted_class, confidence, probabilities[0], original_img

def main():
    # קביעת device
    device = torch.device("mps" if torch.backends.mps.is_available() else 
                         "cuda" if torch.cuda.is_available() else "cpu")
    
    # נתיב למודל
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "vit_document_classifier.pth")
    
    # בדיקה אם המודל קיים
    if not os.path.exists(model_path):
        print(f"❌ שגיאה: לא נמצא המודל ב-{model_path}")
        return
    
    # טעינת המודל
    print(f"📦 טוען מודל מ-{model_path}...")
    model = load_model(model_path, device)
    print(f"✅ המודל נטען בהצלחה!")
    print(f"🖥️  Device: {device}\n")
    
    # קבלת נתיב התמונה מהמשתמש
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("📸 הזן נתיב לתמונה (או לחץ Enter לשימוש בתמונה לדוגמה): ").strip()
        if not image_path:
            # שימוש בתמונה לדוגמה מהדאטה סט
            dataset_dir = "/Users/roy-siftt/final-project/datasets/idnet/document_type_classification_country_split_new"
            example_image = os.path.join(dataset_dir, "images/00002.png")
            if os.path.exists(example_image):
                image_path = example_image
                print(f"📸 משתמש בתמונה לדוגמה: {image_path}")
            else:
                print("❌ לא נמצאה תמונה לדוגמה. אנא הזן נתיב לתמונה.")
                return
    
    # בדיקה אם התמונה קיימת
    if not os.path.exists(image_path):
        print(f"❌ שגיאה: התמונה לא נמצאה ב-{image_path}")
        return
    
    # חיזוי
    print(f"\n🔍 מנתח תמונה: {image_path}")
    try:
        predicted_class, confidence, all_probs, original_img = predict_image(model, image_path, device)
        
        print(f"\n{'='*60}")
        print(f"📊 תוצאות החיזוי:")
        print(f"{'='*60}")
        print(f"🎯 סוג מסמך מזוהה: {label_map[predicted_class]}")
        print(f"📈 רמת ביטחון: {confidence*100:.2f}%")
        print(f"\n📋 כל ההסתברויות:")
        for i, (class_idx, class_name) in enumerate(label_map.items()):
            prob = all_probs[i].item()
            marker = "✓" if i == predicted_class else " "
            print(f"  {marker} {class_name}: {prob*100:.2f}%")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ שגיאה בעת עיבוד התמונה: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


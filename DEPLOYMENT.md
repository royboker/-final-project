# 🚀 מדריך העלאה לאוויר (Deployment Guide)

## דרישות מקדימות

1. ✅ הפרויקט עובד locally עם Docker
2. ✅ הקוד מועלה ל-GitHub
3. ✅ יש לך את כל משתני הסביבה (Environment Variables)

---

## אופציה 1: Render.com (מומלץ למתחילים)

### צעדים:

1. **העלה את הפרויקט ל-GitHub** (אם עדיין לא)
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **היכנס ל-Render**
   - לך ל-https://render.com
   - התחבר עם GitHub

3. **צור Blueprint**
   - לחץ "New +" → "Blueprint"
   - בחר את הרפוזיטורי שלך
   - Render יזהה את `render.yaml` אוטומטית

4. **הגדר משתני סביבה**
   עבור ל-Backend service והוסף:
   ```
   MONGO_URI=mongodb+srv://...
   JWT_SECRET=your-secret-key
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   MAIL_USER=...
   MAIL_PASSWORD=...
   ```

5. **עדכן URLs**
   - אחרי ש-Backend עולה, קבל את ה-URL שלו
   - עדכן את `VITE_API_URL` ב-Frontend
   - עדכן את `FRONTEND_URL` ב-Backend
   - Redeploy את שני השירותים

6. **עדכן Google OAuth**
   - לך ל-Google Cloud Console
   - הוסף את ה-Frontend URL ל-Authorized redirect URIs:
     - `https://your-app.onrender.com/auth/callback`

### ⚠️ הערות חשובות:

- **Free tier** של Render ישן את השירות אחרי 15 דקות של חוסר שימוש
- טעינה ראשונה יכולה לקחת 30-60 שניות
- יש מגבלה של 750 שעות חינמיות בחודש

---

## אופציה 2: Railway.app

### צעדים:

1. **התחבר ל-Railway**
   - https://railway.app
   - Sign up עם GitHub

2. **צור פרויקט חדש**
   - "New Project" → "Deploy from GitHub repo"
   - בחר את הרפוזיטורי

3. **הוסף שירותים**
   Railway יזהה את `docker-compose.yml`:
   - Backend Service (Port 8000)
   - Frontend Service (Port 80)

4. **הגדר Environment Variables**
   לכל שירות בנפרד:

   **Backend:**
   ```
   MONGO_URI=...
   JWT_SECRET=...
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   FRONTEND_URL=https://your-frontend.railway.app
   MAIL_USER=...
   MAIL_PASSWORD=...
   ```

   **Frontend:**
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```

5. **Deploy**
   - Railway יעשה deploy אוטומטי
   - תקבל URLs לכל שירות

### 💰 עלות:
- $5 קרדיט חינמי בחודש
- אחר כך ~$10-20/חודש תלוי בשימוש

---

## אופציה 3: AWS EC2 (למתקדמים)

### צעדים:

1. **צור EC2 Instance**
   - Ubuntu 22.04 LTS
   - t2.medium (לפחות 4GB RAM בגלל PyTorch)
   - פתח פורטים: 22, 80, 443, 8000

2. **התחבר לשרת**
   ```bash
   ssh -i your-key.pem ubuntu@your-server-ip
   ```

3. **התקן Docker**
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose git
   sudo usermod -aG docker ubuntu
   exit
   # התחבר שוב
   ```

4. **העלה פרויקט**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

5. **הגדר Environment Variables**
   ```bash
   cd backend
   nano .env  # הדבק את המשתנים שלך
   ```

6. **עדכן docker-compose.yml**
   ```yaml
   services:
     backend:
       # ... שאר ההגדרות
       environment:
         - FRONTEND_URL=http://your-server-ip

     frontend:
       build:
         args:
           - VITE_API_URL=http://your-server-ip:8000
   ```

7. **הרץ**
   ```bash
   docker-compose up -d --build
   ```

8. **בדוק לוגים**
   ```bash
   docker-compose logs -f
   ```

### 🔒 הוסף HTTPS (אופציונלי אבל מומלץ):

```bash
# התקן Nginx
sudo apt install nginx certbot python3-certbot-nginx

# הגדר Nginx כ-reverse proxy
sudo nano /etc/nginx/sites-available/docuguard

# הוסף:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}

# אפשר ואתחל
sudo ln -s /etc/nginx/sites-available/docuguard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# קבל SSL
sudo certbot --nginx -d your-domain.com
```

---

## אופציה 4: DigitalOcean App Platform

### צעדים:

1. **צור App**
   - https://cloud.digitalocean.com/apps
   - "Create App" → "GitHub"

2. **בחר Repo**
   - אשר גישה ל-DigitalOcean
   - בחר את הרפוזיטורי

3. **הגדר Components**

   **Backend:**
   - Type: Web Service
   - Dockerfile: `backend/Dockerfile`
   - HTTP Port: 8000
   - Environment Variables: הוסף את כולם

   **Frontend:**
   - Type: Web Service
   - Dockerfile: `frontend/Dockerfile`
   - HTTP Port: 80
   - Build Args: `VITE_API_URL`

4. **Deploy**
   - לחץ "Create Resources"
   - המתן לסיום

### 💰 עלות:
- $5-10/חודש לכל component

---

## ✅ Checklist לפני Production

- [ ] כל המשתנים הסודיים הוגדרו כ-Environment Variables
- [ ] הוספת `.dockerignore` ו-`.gitignore` מתאימים
- [ ] `JWT_SECRET` הוא חזק ואקראי (לא המוגדר כברירת מחדל!)
- [ ] URLs מעודכנים בכל המקומות (Frontend, Backend, Google OAuth)
- [ ] MongoDB Atlas מאפשר גישה מה-IP של השרת
- [ ] Google OAuth Redirect URIs מעודכנים
- [ ] CORS מוגדר נכון ב-Backend
- [ ] הפרויקט עובד locally ב-Docker לפני upload

---

## 🐛 פתרון בעיות נפוצות

### Backend לא עולה:

```bash
# בדוק לוגים
docker-compose logs backend

# בעיות נפוצות:
# 1. חסר email-validator
# 2. MongoDB URI לא תקין
# 3. חסר משתנה סביבה
```

### Frontend לא מתחבר ל-Backend:

1. בדוק CORS ב-Backend (`main.py`)
2. ודא ש-`VITE_API_URL` נכון
3. פתח Developer Tools → Network ובדוק את ה-requests

### PyTorch/Model לא עובד:

- ודא שהשרת לפחות 4GB RAM
- שקול להשתמש ב-model קטן יותר
- או העלה את המודל ל-cloud storage (S3, Cloudinary)

---

## 📞 צריך עזרה?

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- AWS EC2: https://docs.aws.amazon.com/ec2

---

**הצלחה! 🎉**

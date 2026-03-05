# 🚀 מדריך העלאה לאוויר - DocuGuard

## 📋 לפני שמתחילים - Checklist

- [x] הפרויקט עובד locally עם Docker (`docker-compose up`)
- [ ] הקוד מועלה ל-GitHub
- [ ] יש לך חשבון ב-Render.com (או Railway/AWS)
- [ ] MongoDB Atlas מוגדר ומאפשר גישה מכל IP
- [ ] יש לך את כל משתני הסביבה

---

## 🎯 אופציה מומלצת: Render.com (חינמי!)

### שלב 1: הכנת הפרויקט

#### 1.1 ודא ש-.env לא יעלה ל-GitHub
```bash
# בדוק שקובץ .gitignore מכיל:
cat .gitignore | grep ".env"
```

צריך לראות:
```
.env
backend/.env
frontend/.env
```

✅ כבר הוספתי את זה בשבילך!

#### 1.2 העלה את הפרויקט ל-GitHub

```bash
# אתחל Git (אם עדיין לא)
git init

# הוסף הכל
git add .

# צור commit
git commit -m "Prepare for deployment to Render"

# צור repository חדש ב-GitHub, ואז:
git remote add origin https://github.com/YOUR_USERNAME/docuguard.git
git branch -M main
git push -u origin main
```

---

### שלב 2: פתיחת חשבון ב-Render

1. **לך ל-Render:**
   👉 https://render.com

2. **Sign Up עם GitHub**
   - לחץ "Get Started"
   - בחר "Sign in with GitHub"
   - אשר את הגישה

---

### שלב 3: Deploy עם Blueprint

#### 3.1 צור Blueprint

1. בדף הבית של Render, לחץ **"New +"**
2. בחר **"Blueprint"**
3. חבר את הרפוזיטורי שלך (GitHub)
4. Render יזהה את קובץ `render.yaml` אוטומטית
5. לחץ **"Apply"**

#### 3.2 הגדר משתני סביבה לBackend

Render יצור 2 שירותים:
- `docuguard-backend`
- `docuguard-frontend`

**לחץ על `docuguard-backend`** ולך ל-**Environment** בצד שמאל:

הוסף את המשתנים הבאים (לחץ "Add Environment Variable"):

```
MONGO_URI=mongodb+srv://noamkadosh4444_db_user:y2qGwhPAO6EkZeVz@docuguardproject.6tfj7z3.mongodb.net/docuguard?appName=DocuGuardProject&tlsInsecure=true

GOOGLE_CLIENT_ID=733426219413-jttfdeom3oreludutaiko043fe0bqbul.apps.googleusercontent.com

GOOGLE_CLIENT_SECRET=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

MAIL_USER=Noamkadosh4444@gmail.com

MAIL_PASSWORD=ylct hfwr tihl xkwq

FRONTEND_URL=https://docuguard-frontend.onrender.com

ALLOWED_ORIGINS=https://docuguard-frontend.onrender.com
```

⚠️ **חשוב:** `JWT_SECRET` כבר נוצר אוטומטית על ידי Render!

---

### שלב 4: עדכון Google OAuth

אחרי שה-Backend עולה, תקבל URL כמו:
```
https://docuguard-backend.onrender.com
```

**עכשיו עדכן את Google Cloud Console:**

1. **לך ל-Google Cloud Console:**
   👉 https://console.cloud.google.com/apis/credentials

2. **לחץ על OAuth 2.0 Client ID שלך**

3. **ב-"Authorized redirect URIs" הוסף:**
   ```
   https://docuguard-backend.onrender.com/auth/google/callback
   https://docuguard-frontend.onrender.com/auth/callback
   ```

4. **שמור**

---

### שלב 5: עדכון URLs

#### 5.1 עדכן את FRONTEND_URL ב-Backend

1. לך ל-Backend service ב-Render
2. Environment → ערוך את `FRONTEND_URL`
3. שנה ל-URL של הfrontend שלך (למשל: `https://docuguard-frontend.onrender.com`)
4. שמור → Render יעשה redeploy אוטומטי

#### 5.2 עדכן את VITE_API_URL ב-Frontend

1. לך ל-Frontend service ב-Render
2. Environment → ערוך את `VITE_API_URL`
3. שנה ל-URL של הbackend שלך (למשל: `https://docuguard-backend.onrender.com`)
4. שמור → Render יעשה redeploy אוטומטי

---

### שלב 6: עדכון MongoDB Atlas

ודא ש-MongoDB מאפשר גישה מכל IP:

1. **לך ל-MongoDB Atlas:**
   👉 https://cloud.mongodb.com

2. **Network Access** (בצד שמאל)

3. **לחץ "Add IP Address"**

4. **בחר "Allow Access from Anywhere"** (0.0.0.0/0)

5. **Confirm**

⚠️ **שים לב:** זה בטוח כי יש לך username/password ב-connection string!

---

### שלב 7: בדיקה 🧪

1. **פתח את הFrontend URL:**
   ```
   https://docuguard-frontend.onrender.com
   ```

2. **נסה להירשם עם email**

3. **נסה להתחבר עם Google**

4. **בדוק את הלוגים ב-Render:**
   - לך לכל service
   - לחץ "Logs" בצד שמאל
   - תראה את כל הפעילות

---

## 🐛 פתרון בעיות נפוצות

### הBackend לא עולה

**בדוק לוגים:**
```
Render → Backend Service → Logs
```

**בעיות נפוצות:**
- חסר `email-validator` → ✅ כבר תיקנתי!
- MongoDB URI לא תקין → בדוק connection string
- משתנה סביבה חסר → ודא שכל המשתנים מוגדרים

### הFrontend לא מתחבר לBackend

1. **בדוק CORS:**
   - ודא ש-`ALLOWED_ORIGINS` כולל את ה-Frontend URL
   - פתח F12 → Console ובדוק שגיאות

2. **בדוק את VITE_API_URL:**
   - צריך להיות: `https://docuguard-backend.onrender.com`
   - ללא "/" בסוף!

### Google OAuth לא עובד

1. **בדוק Redirect URIs ב-Google Console**
2. **ודא שה-URLs תואמים בדיוק** (עם/בלי https, בדיוק אותו domain)

### האתר איטי / לא עובד

- **Free tier של Render ישן אחרי 15 דקות**
- טעינה ראשונה לוקחת 30-60 שניות
- פתרון: שדרג ל-Paid plan ($7/חודש) או השתמש ב-Railway

---

## 💰 עלויות

### Render Free Tier:
- ✅ 750 שעות חינמיות בחודש
- ✅ SSL אוטומטי (HTTPS)
- ⚠️ השירות ישן אחרי 15 דקות
- ⚠️ טעינה ראשונה איטית

### Render Paid ($7/חודש לכל service):
- ✅ תמיד זמין (לא ישן)
- ✅ מהיר יותר
- ✅ יותר זיכרון/CPU

### Railway ($5 חינם בחודש):
- לאחר מכן ~$10-20/חודש
- לא ישן
- Deploy מהיר יותר

---

## 🎉 סיימת!

האתר שלך עכשיו חי באינטרנט! 🚀

**URLs שלך:**
- Frontend: `https://docuguard-frontend.onrender.com`
- Backend API: `https://docuguard-backend.onrender.com`
- API Docs: `https://docuguard-backend.onrender.com/docs`

---

## 📞 צריך עזרה?

- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

---

## 🔐 אבטחה - חשוב!

לפני Production אמיתי:

1. **שנה את JWT_SECRET** למשהו אקראי וחזק
2. **שנה את סיסמאות MongoDB** אם זה פרויקט ציבורי
3. **אל תשתף את קובץ .env** עם אף אחד!
4. **הגדר rate limiting** ב-Backend (למנוע spam)
5. **הוסף monitoring** (כמו Sentry)

---

**בהצלחה! 🎊**

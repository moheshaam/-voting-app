# 🚀 إعداد التطبيق على Streamlit Cloud

## الخطوات بالتفصيل:

### 1️⃣ إنشاء Google Sheets

1. افتح [Google Sheets](https://sheets.google.com)
2. اعمل شيت جديد واسمه **Voting_App_Data**
3. في الصف الأول، اكتب:
   - A1: `Option`
   - B1: `Votes`
   - D1: `Voters`

### 2️⃣ إنشاء Google Cloud Project

1. روح على [Google Cloud Console](https://console.cloud.google.com)
2. اعمل مشروع جديد (New Project)
3. اختار المشروع

### 3️⃣ تفعيل Google Sheets API

1. في القائمة الجانبية، اختار **APIs & Services** > **Library**
2. ابحث عن "Google Sheets API" وفعّلها (Enable)
3. ابحث عن "Google Drive API" وفعّلها برضو

### 4️⃣ إنشاء Service Account

1. روح على **APIs & Services** > **Credentials**
2. اضغط **Create Credentials** > **Service Account**
3. اكتب اسم للـ Service Account (مثلاً: `voting-app`)
4. اضغط **Create and Continue**
5. اختار Role: **Editor**
6. اضغط **Done**

### 5️⃣ الحصول على JSON Key

1. في صفحة Credentials، اضغط على الـ Service Account اللي عملته
2. روح لـ **Keys** tab
3. اضغط **Add Key** > **Create new key**
4. اختار **JSON**
5. الملف هيتحمل تلقائياً - **احتفظ بيه في مكان آمن!**

### 6️⃣ مشاركة Google Sheet مع Service Account

1. افتح ملف الـ JSON اللي حملته
2. انسخ الـ `client_email` (بيبدأ بـ `your-app@your-project.iam.gserviceaccount.com`)
3. افتح الـ Google Sheet (**Voting_App_Data**)
4. اضغط **Share** (مشاركة)
5. الصق الـ email واديله صلاحية **Editor**
6. اضغط **Send**

### 7️⃣ إعداد Streamlit Secrets (محلي)

1. افتح ملف `.streamlit/secrets.toml`
2. انسخ محتوى ملف الـ JSON في الملف بالشكل ده:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\nYour Key Here\n-----END PRIVATE KEY-----\n"
client_email = "your-app@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**ملحوظة مهمة:** الـ `private_key` لازم يكون على سطر واحد مع `\n` للـ line breaks

### 8️⃣ رفع الكود على GitHub

```bash
git init
git add .
git commit -m "Initial commit: Voting app with Google Sheets"
git branch -M main
git remote add origin https://github.com/your-username/voting-app.git
git push -u origin main
```

**⚠️ مهم:** الملف `.gitignore` موجود عشان ميرفعش الـ `secrets.toml` على GitHub

### 9️⃣ نشر على Streamlit Cloud

1. روح على [Streamlit Cloud](https://share.streamlit.io)
2. سجل دخول بحساب GitHub
3. اضغط **New app**
4. اختار الـ repository بتاعك
5. Main file: `app.py`
6. اضغط **Advanced settings**
7. في **Secrets**، الصق محتوى ملف `secrets.toml` بالكامل
8. اضغط **Deploy**

---

## 🎉 خلاص!

التطبيق دلوقتي شغال على الكلاود، والـ votes بتتخزن في Google Sheets ومتزامنة لكل المستخدمين!

---

## 🧪 تجربة محلية

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## ❓ مشاكل شائعة

### خطأ: "Error connecting to Google Sheets"
- تأكد إن الـ Service Account عنده صلاحية على الـ Sheet
- تأكد إن اسم الـ Sheet هو `Voting_App_Data` بالظبط

### خطأ: "Invalid credentials"
- تأكد إن ملف `secrets.toml` منسوخ صح
- تأكد إن الـ `private_key` فيه `\n` للـ line breaks

### الـ votes مش بتتحدث
- اعمل refresh للصفحة
- تأكد إن Google Sheets API مفعّل

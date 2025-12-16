# Quick Setup Guide

## خطوات سهلة لتشغيل ال app

### الخطوات السريعة

#### 1. Fork الـ Repository
اضغط Fork فوق على GitHub

#### 2. إعداد Google Cloud (5 دقائق)

**Google Cloud Console:**
https://console.cloud.google.com

الخطوات:
- اعمل مشروع جديد (New Project)
   
**فعّل APIs:**
- روح على: APIs & Services > Library
- ابحث عن: Google Sheets API واضغط Enable
- ابحث عن: Google Drive API واضغط Enable
   
**اعمل Service Account:**
- روح على: APIs & Services > Credentials
- اضغط: Create Credentials > Service Account
- اكتب اسم للـ Service Account مثل: voting-app
- اختار Role: Editor
- اضغط Done

**حمّل JSON Key:**
- في صفحة Credentials، اضغط على الـ Service Account اللي عملته
- روح لـ Keys tab
- اضغط: Add Key > Create new key
- اختار: JSON
- الملف هيتحمل تلقائياً - احتفظ بيه في مكان آمن

**اعمل Google Sheet:**
- افتح: https://sheets.google.com
- اعمل شيت جديد اسمه: Voting_App_Data
- في الصف الأول اكتب: Option | Votes | | Voters
- اضغط Share (مشاركة)
- الصق الـ client_email من ملف الـ JSON
- اديله صلاحية Editor
- اضغط Send

#### 3. نشر على Streamlit Cloud

**رابط Streamlit Cloud:**
https://share.streamlit.io

الخطوات:
- سجل دخول بحساب GitHub
- اضغط New app
- اختار الـ repository بتاعك
- Main file: app.py
- اضغط Advanced settings
- في Secrets، الصق محتوى الـ JSON بصيغة TOML:

```toml
[gcp_service_account]
type = "service_account"
project_id = "من الـ JSON"
private_key_id = "من الـ JSON"
private_key = "من الـ JSON - على سطر واحد مع \\n"
client_email = "من الـ JSON"
client_id = "من الـ JSON"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "من الـ JSON"
universe_domain = "googleapis.com"
```

- اضغط Deploy

---

## تخصيص الخيارات

في app.py، سطر 66-71، غيّر:

```python
votes_data["options"] = {
    "خيارك الأول": 0,
    "خيارك الثاني": 0,
    "خيارك الثالث": 0,
}
```

---

## مشاكل شائعة

**Error 403:**
فعّل Google Drive API من:
https://console.cloud.google.com/apis/library/drive.googleapis.com

**No votes showing:**
شارك الشيت مع الـ service account email من ملف الـ JSON

**Secrets error:**
تأكد من صيغة الـ TOML صح والـ private_key على سطر واحد مع \\n

---

جاهز!

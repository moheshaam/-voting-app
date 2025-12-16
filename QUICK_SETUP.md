# 🚀 Quick Setup Guide

## للي عايز ياخد البروجكت ويشغله:

### الخطوات السريعة:

#### 1️⃣ Fork الـ Repository
اضغط **Fork** فوق على GitHub

#### 2️⃣ إعداد Google Cloud (5 دقائق)

1. **Google Cloud Console**: https://console.cloud.google.com
   - اعمل مشروع جديد
   
2. **فعّل APIs**:
   - Google Sheets API
   - Google Drive API
   
3. **اعمل Service Account**:
   - APIs & Services → Credentials
   - Create Credentials → Service Account
   - Role: Editor
   - Create Key → JSON
   - حمّل الملف

4. **اعمل Google Sheet**:
   - اسمه: `Voting_App_Data`
   - الصف الأول: `Option | Votes | | Voters`
   - شارك الشيت مع الـ `client_email` من الـ JSON

#### 3️⃣ نشر على Streamlit Cloud

1. https://share.streamlit.io
2. New app → اختار الـ repo
3. Advanced settings → Secrets:
   - انسخ محتوى الـ JSON بصيغة TOML:

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

4. Deploy!

---

## تخصيص الخيارات

في `app.py`، سطر 66-71، غيّر:

```python
votes_data["options"] = {
    "خيارك الأول": 0,
    "خيارك الثاني": 0,
    "خيارك الثالث": 0,
}
```

---

## مشاكل شائعة

**Error 403**: فعّل Google Drive API
**No votes showing**: شارك الشيت مع الـ service account email
**Secrets error**: تأكد من صيغة الـ TOML صح

---

🎉 **جاهز!**

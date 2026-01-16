# 🔧 Configuration Guide - Assistant MaTanne

## 🚀 Quick Start

### Local Development
```bash
cd /workspaces/assistant_matanne
pip install -r requirements.txt
streamlit run src/app.py --server.enableCORS false --server.enableXsrfProtection false
```

### Streamlit Cloud
See [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)

---

## 🔑 Configuration Mistral API

### 3 ways to configure the API key:

#### 1️⃣ **Local Development (`.env.local`)**
Best for local testing

```dotenv
MISTRAL_API_KEY=sk-YOUR_ACTUAL_KEY
```

- File loaded automatically at startup
- Not committed to git (in `.gitignore`)
- Python automatically loads it via `load_dotenv()`

#### 2️⃣ **Environment Variable**
For CI/CD or shell configuration

```bash
export MISTRAL_API_KEY='sk-YOUR_ACTUAL_KEY'
streamlit run src/app.py
```

#### 3️⃣ **Streamlit Cloud Secrets** ⭐ RECOMMENDED
For production on Streamlit Cloud

1. Go to your app: https://share.streamlit.io/
2. Click **Settings** (⚙️)
3. Go to **Secrets** tab
4. Add:
```toml
[mistral]
api_key = "sk-YOUR_ACTUAL_KEY"
model = "mistral-small-latest"
```

---

## 📦 Database Configuration

### Local Development
Uses local PostgreSQL or Supabase dev instance

### Streamlit Cloud
Add to Secrets:
```toml
[database]
url = "postgresql://user:password@host:port/postgres"
```

---

## 🐛 Troubleshooting

### "Clé API Mistral manquante"
- ✅ Check that `MISTRAL_API_KEY` is set
- ✅ Restart Streamlit after changing `.env.local`
- ✅ For Cloud, check that secrets are saved

### "Invalid API Key" or "401 Unauthorized"
- ✅ Your key might be invalid or expired
- ✅ Get a new key from https://console.mistral.ai/

### "Request URL is missing protocol"
- ✅ You might have a test key (`sk-test-...`)
- ✅ Replace with a real API key from Mistral

---

## 📚 Related Files

- [`.env.local`](.env.local) - Local development config (not committed)
- [`.streamlit/secrets.toml`](.streamlit/secrets.toml) - Streamlit secrets template
- [MISTRAL_SETUP.md](MISTRAL_SETUP.md) - Detailed Mistral setup
- [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md) - Cloud deployment guide

---

## ✅ Verification Checklist

- [ ] API key is set (test locally: `echo $MISTRAL_API_KEY`)
- [ ] Streamlit can load environment (check startup logs)
- [ ] No error messages on app startup
- [ ] Can navigate to different pages
- [ ] Can generate a recipe with AI
- [ ] Database operations work (if applicable)

---

## 🎯 Priority Order for API Key Loading

The app checks for API key in this order:
1. **Streamlit Secrets** (`st.secrets['mistral']['api_key']`)
2. **Environment variable** (`MISTRAL_API_KEY`)
3. Raises error if not found

This ensures Streamlit Cloud works automatically without extra setup!

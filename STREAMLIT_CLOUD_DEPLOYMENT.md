# 🚀 Streamlit Cloud Deployment - Guide Complet

> Déployez votre application Jeux gratuitement sur Streamlit Cloud en 10 minutes!

---

## 📋 Prérequis

Avant de commencer, vous devez avoir:

- [ ] Compte GitHub (gratuit)
- [ ] Compte Streamlit Cloud (gratuit)
- [ ] Code pushé sur GitHub
- [ ] Fichier `requirements.txt` à jour
- [ ] Clé API Football-Data.org

---

## 🎯 Étapes du déploiement

### Étape 1: Préparer le repository GitHub (5 min)

#### 1.1 Créer un repo GitHub

```bash
# À la racine du projet
git init
git add .
git commit -m "Initial commit - Jeux module with APIs"
git branch -M main
git remote add origin https://github.com/VOTRE_USERNAME/assistant_matanne.git
git push -u origin main
```

#### 1.2 Créer un fichier `.gitignore` (si pas encore fait)

```bash
# À la racine du projet, créer .gitignore
```

**.gitignore** (doit inclure):

```
# Secrets
.env.local
.env
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/

# Data
*.db
*.sqlite
data/uploads/
```

#### 1.3 Vérifier que `requirements.txt` est à jour

```bash
# Générer depuis pyproject.toml
python manage.py generate_requirements

# Ou manuellement
pip freeze > requirements.txt
```

**Fichier doit contenir**:

```
streamlit>=1.28.0
requests>=2.32.0
beautifulsoup4>=4.12.0
sqlalchemy>=2.0.0
pandas>=2.0.0
plotly>=5.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
psycopg2-binary>=2.9.0
# ... autres packages
```

#### 1.4 Vérifier `secrets.toml` pour Streamlit

À la racine du projet, créer `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml (pour dev local)
FOOTBALL_DATA_API_KEY = "votre_token_ici"
DATABASE_URL = "postgresql://user:pass@host/db"
```

⚠️ **Ne pas committer ce fichier!** Il doit être dans `.gitignore`.

#### 1.5 Vérifier la structure du projet

```
project-root/
├── .github/
├── .streamlit/          ← Pour config
├── src/
│   └── app.py           ← Point d'entrée
├── requirements.txt     ← OBLIGATOIRE
├── pyproject.toml
├── .gitignore           ← IMPORTANT!
└── README.md
```

### Étape 2: Créer/connecter un compte Streamlit Cloud (2 min)

#### 2.1 Créer compte Streamlit Cloud

1. Aller sur: https://share.streamlit.io
2. Cliquer "Sign up with GitHub"
3. Autoriser Streamlit à accéder à vos repos
4. Créer compte

#### 2.2 Dashboard Streamlit Cloud

```
https://share.streamlit.io/
└─ New app
   ├─ GitHub repo selection
   ├─ Branch
   ├─ Main file path: src/app.py
   └─ Deploy!
```

### Étape 3: Déployer l'application (3 min)

#### 3.1 Créer une nouvelle app

1. Aller sur https://share.streamlit.io
2. Cliquer **"New app"** (bouton en haut à gauche)
3. Remplir le formulaire:

```
Repository:  VOTRE_USERNAME/assistant_matanne
Branch:      main
Main file path:  src/app.py
```

4. Cliquer **"Deploy!"**

#### 3.2 Attendre le déploiement

```
Streamlit will:
1. Clone your repo
2. Install requirements.txt
3. Build the image
4. Deploy on their servers

Estimated time: 2-3 minutes
You'll see: "App is running at: https://..."
```

### Étape 4: Configurer les secrets (2 min)

#### 4.1 Ajouter secrets dans Streamlit Cloud

Dans le dashboard:

1. Cliquer sur votre app
2. Cliquer l'icône ⚙️ (Settings)
3. Aller dans **"Secrets"**
4. Coller votre `.streamlit/secrets.toml` (contenu):

```toml
FOOTBALL_DATA_API_KEY = "votre_token_api"
DATABASE_URL = "postgresql://..."
```

5. Cliquer **"Save"**

#### 4.2 L'app redémarre automatiquement

Streamlit redeploie automatiquement et recharge avec les secrets.

---

## 🌐 Votre app est maintenant en ligne!

```
URL: https://share.streamlit.io/USERNAME/assistant_matanne/main/src/app.py

Ou plus court:
URL: https://share.streamlit.io/USERNAME/assistant_matanne
```

---

## 🔄 Mise à jour de l'app

### Automatique (recommandé)

```
Streamlit Cloud redéploie automatiquement quand vous:
1. Pushez du code sur la branch 'main'
2. Modifiez requirements.txt
3. Mettez à jour secrets

Processus:
  git push → GitHub → Streamlit detects → Auto redeploy (2-3 min)
```

### Manuel (si besoin)

```
1. Dashboard Streamlit Cloud
2. Cliquer l'app
3. Menu "Manage app"
4. Cliquer "Reboot"
```

---

## 🐛 Troubleshooting Streamlit Cloud

### ❌ Erreur: "requirements.txt not found"

```bash
# Solution:
1. Vérifier que requirements.txt existe à la racine
2. git add requirements.txt
3. git commit -m "Add requirements"
4. git push

# Puis redeploy dans Streamlit Cloud
```

### ❌ Erreur: "Module not found"

```bash
# Possible causes:
1. src/app.py doesn't exist
2. Wrong path in Streamlit Cloud (should be src/app.py)
3. Package missing from requirements.txt

# Solutions:
1. Check file exists: ls -la src/app.py
2. Update requirements.txt: pip freeze > requirements.txt
3. Git push et redeploy
```

### ❌ Erreur: "API key not found"

```
Likely cause: Secrets not configured in Streamlit Cloud

Solution:
1. Go to Settings → Secrets
2. Add FOOTBALL_DATA_API_KEY
3. Save
4. App auto-redeploys
```

### ❌ Erreur: "Database connection failed"

```
Possible causes:
1. DATABASE_URL not in secrets
2. Supabase IP restriction
3. Connection string malformed

Solutions:
1. Add DATABASE_URL to Streamlit Cloud secrets
2. Whitelist Streamlit Cloud IPs in Supabase:
   - Supabase Dashboard
   - Project Settings → Database
   - Add all IPs: 0.0.0.0/0 (or be specific)
3. Verify format: postgresql://user:pass@host/db
```

### ⚠️ Performance lente

```
Cause: First load builds environment

Solutions:
1. Add packages to requirements.txt only if needed
2. Use caching: @st.cache_data, @st.cache_resource
3. Optimize database queries
4. Use CDN for static files

Already done in your code!
```

### ⚠️ Tier limits

```
Free tier Streamlit Cloud allows:
✅ 3 apps
✅ Unlimited public views
✅ 1GB app storage
✅ 25MB upload per file
❌ No persistent backend (restarts hourly)

Your app doesn't need backend, so OK!
```

---

## 📊 Monitoring & Debugging

### Voir les logs

```
1. Dashboard Streamlit Cloud
2. Cliquer votre app
3. Tab "Logs" (en haut)
4. Voir les erreurs en temps réel
```

### Déboguer localement avant de déployer

```bash
# Test local
streamlit run src/app.py --logger.level=debug

# Si ça marche en local, ça marchera sur cloud (99%)
```

### Profiler performance

```python
# Dans votre code (pour debug)
import time
import streamlit as st

start = time.time()
# ... votre code ...
st.write(f"Execution time: {time.time() - start:.2f}s")
```

---

## 🔐 Sécurité sur Streamlit Cloud

### ✅ Bonnes pratiques

```
1. ✅ Secrets jamais en git
2. ✅ Use .streamlit/secrets.toml pour secrets
3. ✅ Streamlit gère les secrets en tant que env vars
4. ✅ Logs ne montrent pas les secrets
5. ✅ HTTPS obligatoire
```

### ❌ À éviter

```
1. ❌ Hardcoder les clés API dans le code
2. ❌ Committer .env ou secrets.toml
3. ❌ Partager les secrets dans les logs
4. ❌ Utiliser les mêmes secrets partout
```

### Configuration de Supabase pour Streamlit Cloud

```
Supabase → Project Settings → Database → Networking

Add Streamlit Cloud IPs:
1. Option A: Whitelist all (0.0.0.0/0) - simple mais moins sécurisé
2. Option B: Whitelist specific IPs - plus sécurisé

Your app uses only database, no public API exposure!
```

---

## 🎯 URL & Partage

### URL de votre app

```
Format court:
https://share.streamlit.io/USERNAME/assistant_matanne

Format long:
https://share.streamlit.io/USERNAME/assistant_matanne/main/src/app.py

Les deux marchent!
```

### Partager votre app

```
1. Copier l'URL
2. Envoyer aux amis/collègues
3. Ils peuvent utiliser directement (pas de login requis pour app publique)
4. Ils voient: 🎲 Jeux → ⚽ Paris / 🎰 Loto
```

### App privée (optionnel - Pro tier)

```
By default: PUBLIC (anyone with URL can view)

Pour rendre PRIVÉ (Pro tier):
1. Upgrade à Streamlit Pro
2. Settings → Share button disabled
```

---

## 🚀 Workflow de déploiement continu

```
Développement local:
  1. Faire des changements
  2. Test local: streamlit run src/app.py
  3. Tests: python tests/test_jeux_apis.py
  4. OK? Continuer

Ready à déployer:
  1. git add .
  2. git commit -m "Description du changement"
  3. git push origin main
  4. Streamlit Cloud detect change
  5. Auto redeploy (2-3 min)
  6. App updated!

Monitoring:
  1. Logs dans Streamlit Cloud dashboard
  2. App metrics en bas du dashboard
```

---

## 📈 Limites & Considérations

### Streamlit Cloud Free Tier

| Limite           | Valeur      |
| ---------------- | ----------- |
| Nombre d'apps    | 3           |
| App storage      | 1 GB        |
| Upload max       | 25 MB       |
| Timeout requête  | 30 secondes |
| Memory par app   | 1 GB        |
| CPU cores        | 2           |
| Public           | Oui         |
| Custom domain    | Non         |
| Priority support | Non         |

### Votre app

```
Requirements:
- ✅ Database: Supabase (externe)
- ✅ APIs: Football-Data (externe)
- ✅ Storage: Cache Streamlit (<100MB)
- ✅ Compute: Léger (< 1GB RAM)

Verdict: COMPATIBLE avec free tier! 🎉
```

### Si vous outpassez les limites

```
Upgrade options:
1. Streamlit Pro ($5/mo)
   - 30 apps
   - Custom domain
   - Priority support

2. Self-host (Docker)
   - Full control
   - Cost varies (Heroku, AWS, etc)
```

---

## 🎁 Bonus: GitHub Actions (CI/CD)

### Auto-test avant deploy (optionnel)

Créer `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: python tests/test_jeux_apis.py
```

Effet:

```
Chaque push → Tests run → Deploy only if tests pass
```

---

## ✅ Checklist Déploiement

### Avant de déployer

- [ ] Code complet et testé en local
- [ ] `python tests/test_jeux_apis.py` passe
- [ ] `streamlit run src/app.py` marche sans erreurs
- [ ] `.gitignore` contient `.env.local`, `secrets.toml`
- [ ] `requirements.txt` à jour
- [ ] Pas de hardcoded secrets
- [ ] README.md explique comment utiliser

### GitHub

- [ ] Repo créé et public
- [ ] Code pushé sur main branch
- [ ] `.gitignore` commité
- [ ] `requirements.txt` présent à la racine

### Streamlit Cloud

- [ ] Compte créé (gratuit)
- [ ] App déployée
- [ ] Main file: `src/app.py`
- [ ] Secrets configurés dans settings
- [ ] App fonctionne (tester l'URL)

### Finalisation

- [ ] Vérifier que 🎲 Jeux module charge
- [ ] Essayer ⚽ Paris (doit charger matchs)
- [ ] Essayer 🎰 Loto (doit charger tirages)
- [ ] Tester fallback (simuler API down)
- [ ] Partager l'URL avec des gens!

---

## 📞 Support & Ressources

### Docs officielles

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud)
- [Deploy an app](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)
- [App management](https://docs.streamlit.io/streamlit-cloud/get-started/manage-your-app)

### Troubleshooting

- [Common issues](https://docs.streamlit.io/streamlit-cloud/get-started/troubleshooting)
- [Configuration](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/app-dependencies)

### Community

- [Streamlit forum](https://discuss.streamlit.io/)
- [GitHub issues](https://github.com/streamlit/streamlit/issues)

---

## 🎉 Voilà!

Votre app est maintenant:

✅ **Online** - Accessible 24/7  
✅ **Live** - Matchs et Loto en temps réel  
✅ **Shareable** - URL facile à partager  
✅ **Gratuit** - Tier free suffisant  
✅ **Automatic** - Redeploy sur chaque push

**Profitez-en! 🚀**

---

## 💡 Conseils finaux

### Pour une meilleure expérience

```python
# 1. Ajouter un titre dans le header
st.set_page_config(page_title="🎲 Jeux", page_icon="🎲")

# 2. Ajouter un footer avec lien
st.markdown("---")
st.markdown("[Made with ❤️ on Streamlit Cloud](https://streamlit.io)")

# 3. Ajouter un sidebar avec infos
with st.sidebar:
    st.markdown("### About")
    st.markdown("Paris & Loto predictions")
    st.markdown("[GitHub](https://github.com/...)")
```

### Auto-refresh des données

```python
# Les APIs auto-refresh (cache 30min)
# Pour forcer refresh manuel:
if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
```

---

**Ready to deploy? Let's go! 🚀🎲**

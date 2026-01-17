# Déploiement sur Streamlit Cloud avec Génération d'Images

## 🚀 Configuration pour Streamlit Cloud

### Étape 1: Préparer les Secrets Streamlit

1. **Aller sur votre dashboard** Streamlit Cloud:
   - https://share.streamlit.io/

2. **Sélectionner votre application**

3. **Cliquer sur "Settings"** → **"Secrets"**

4. **Ajouter les variables d'environnement**:
   ```
   # Pour votre app Streamlit
   UNSPLASH_API_KEY = "your_unsplash_key_here"
   PEXELS_API_KEY = "your_pexels_key_here"
   PIXABAY_API_KEY = "your_pixabay_key_here"
   REPLICATE_API_TOKEN = "r8_your_replicate_token_here"
   ```

### Étape 2: Vérifier le `.gitignore`

S'assurer que le `.env` n'est PAS en ligne (sensibilité):
```
.env
.env.local
.env.*.local
```

### Étape 3: Tester

1. **Redéployer** votre application:
   ```bash
   git push
   ```

2. **Les images doivent fonctionner** automatiquement

---

## 📝 Fichier `secrets.toml` (Alternative)

Si vous utilisez Streamlit localement:
```
# ~/.streamlit/secrets.toml
UNSPLASH_API_KEY = "your_key"
PEXELS_API_KEY = "your_key"
PIXABAY_API_KEY = "your_key"
```

Accès dans le code:
```python
import streamlit as st
key = st.secrets.get("UNSPLASH_API_KEY")
```

---

## 🐳 Docker (Déploiement Custom)

Si vous utilisez Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Définir les variables d'environnement
ENV UNSPLASH_API_KEY=${UNSPLASH_API_KEY}
ENV PEXELS_API_KEY=${PEXELS_API_KEY}
ENV PIXABAY_API_KEY=${PIXABAY_API_KEY}

CMD ["streamlit", "run", "app.py"]
```

Lancer avec:
```bash
docker build -t assistant_matanne .
docker run \
  -e UNSPLASH_API_KEY=your_key \
  -e PEXELS_API_KEY=your_key \
  -p 8501:8501 \
  assistant_matanne
```

---

## 🐛 Dépannage

### Les images ne s'affichent pas
1. ✅ Vérifier dans Streamlit Cloud → Settings → Secrets
2. ✅ Redéployer après changement
3. ✅ Attendre 5-10 minutes

### "API key not found"
→ Les secrets ne sont pas encore synchronisés
→ Patience: max 10 minutes

### Erreur 403/401
→ Clé API incorrecte ou révoquée
→ Régénérer une nouvelle clé

---

## 📊 Monitoring

Pour vérifier les appels API en production:

```python
# Dans le code
import logging
logger = logging.getLogger(__name__)

# Les logs montreront:
# ✅ Image générée via Unsplash
# ✅ Image trouvée via Pexels
# ❌ Erreur API (si problème)
```

Vérifier les logs Streamlit Cloud:
1. Dashboard → Select App
2. "Logs" → Voir les détails

---

## 💡 Pro Tips

1. **Unsplash gratuitement**: Aucune limite pour les clés publiques
2. **Cache les images**: Streamlit met en cache automatiquement
3. **Monitoring**: Loggez tout pour le debugging en prod
4. **Fallback**: Pollinations.ai fonctionne sans clé de secours

---

## ✅ Checklist Avant Production

- [ ] Clé Unsplash obtenue et testée
- [ ] Variables définies dans Streamlit Cloud (ou .env)
- [ ] `.env` dans `.gitignore`
- [ ] `test_image_generation.py` passé avec succès
- [ ] Images affichées dans l'app locale
- [ ] Redéploiement effectué après ajout des secrets

---

## 🔗 Références

- [Streamlit Secrets Management](https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app/secrets-management)
- [Docker Docs](https://docs.docker.com/)
- [Unsplash API](https://unsplash.com/oauth/applications)
- [Pexels API](https://www.pexels.com/api/)

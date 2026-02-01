# 🌍 Déploiement - Toutes les options

> Comparez les différentes façons de déployer votre app Jeux

---

## 📊 Comparaison des plateformes

| Plateforme          | Prix        | Setup     | Performance  | Customization | Données persistantes |
| ------------------- | ----------- | --------- | ------------ | ------------- | -------------------- |
| **Streamlit Cloud** | 🟢 Gratuit  | 🟢 5 min  | 🟡 Moyen     | 🟡 Moyen      | ✅ BD externe        |
| **Heroku**          | 🟡 7$/mois  | 🟡 15 min | 🟢 Bon       | 🟢 Bon        | ✅ BD externe        |
| **Railway**         | 🟡 5$/mois  | 🟡 10 min | 🟢 Bon       | 🟢 Bon        | ✅ BD externe        |
| **Render**          | 🟡 10$/mois | 🟡 15 min | 🟢 Bon       | 🟢 Bon        | ✅ BD externe        |
| **AWS**             | 🔴 Variable | 🔴 45 min | 🟢 Excellent | 🟢 Excellent  | ✅ Oui               |
| **Docker local**    | 🟡 VPS      | 🟡 30 min | 🟢 Excellent | 🟢 Excellent  | ✅ Oui               |
| **DigitalOcean**    | 🟡 5$/mois  | 🟡 20 min | 🟢 Bon       | 🟢 Bon        | ✅ Oui               |

---

## 🚀 1. STREAMLIT CLOUD (Recommandé - Gratuit)

### ✅ Avantages

- ✅ **Gratuit** (free tier)
- ✅ **5 minutes** de setup
- ✅ **Auto-deploy** on git push
- ✅ **HTTPS** inclus
- ✅ **Aucune configuration** serveur
- ✅ **Scaling automatique**

### ❌ Inconvénients

- ❌ Limited à 3 apps (free)
- ❌ Limites CPU/RAM
- ❌ Redémarrage occasionnel
- ❌ Pas de custom domain (free)

### 📖 Guide complet

→ Voir: [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)

### 🚀 Quick start

```bash
# 1. Push code sur GitHub
git push origin main

# 2. Go to https://share.streamlit.io
# 3. New app → select repo → Deploy!
# 4. Configurez secrets
# 5. Done!
```

### Idéal pour

- 🎯 MVP / Prototypage
- 🎯 Demande faible-modérée
- 🎯 Gratuit!
- 🎯 Vous venez de terminer l'app

---

## 🟡 2. HEROKU (Classique)

### ✅ Avantages

- ✅ **Populaire** (beaucoup de docs)
- ✅ **Git deploy** automatique
- ✅ **Add-ons** (Postgres, Redis)
- ✅ **Scaling facile**
- ✅ **Free tier** (limité mais gratuit)

### ❌ Inconvénients

- ❌ **$7/mo** minimum (après free tier)
- ❌ **Démarrage lent** (dynos idle)
- ❌ Setup un peu complexe
- ❌ Moins de performance

### 🚀 Setup rapide

```bash
# 1. Install Heroku CLI
brew install heroku  # macOS
# ou choco install heroku  # Windows

# 2. Login
heroku login

# 3. Create app
heroku create your-app-name

# 4. Add Procfile à la racine
echo "web: streamlit run src/app.py" > Procfile

# 5. Config secrets
heroku config:set FOOTBALL_DATA_API_KEY=votre_token
heroku config:set DATABASE_URL=postgresql://...

# 6. Deploy
git push heroku main
```

### 📖 Ressources

- [Heroku Streamlit deploy](https://discuss.streamlit.io/t/how-to-deploy-streamlit-on-heroku-cloud/20619)
- [Procfile docs](https://devcenter.heroku.com/articles/procfile)

### Idéal pour

- 🎯 Production stable
- 🎯 Vous avez budget
- 🎯 Besoin add-ons Heroku
- 🎯 Historique/communauté

---

## 🟢 3. RAILWAY (Nouveau & Simpliste)

### ✅ Avantages

- ✅ **$5/mo** ou pay-as-you-go
- ✅ **Super simple** (UI géniale)
- ✅ **GitHub integration** native
- ✅ **Templates** pré-faits
- ✅ **Modernes** & active dev

### ❌ Inconvénients

- ❌ Plus jeune (moins de docs)
- ❌ Pas encore de free tier
- ❌ Communauté plus petite

### 🚀 Setup rapide

```
1. Railway.app → Sign up (GitHub)
2. New project → Deploy from GitHub repo
3. Ajouter variables d'env
4. Auto-deploy on git push
```

### 📖 Ressources

- [Railway docs](https://docs.railway.app/)
- [Streamlit template](https://railway.app/template/streamlit)

### Idéal pour

- 🎯 Vous aimez l'UX simple
- 🎯 Budget limité mais pas gratuit
- 🎯 Nouveau projet

---

## 🔵 4. RENDER (Alternative Heroku)

### ✅ Avantages

- ✅ **$10/mo** ou free tier
- ✅ **GitHub integration** simple
- ✅ **Performant**
- ✅ **Moderne** et bien maintenu
- ✅ **Dashboard** clair

### ❌ Inconvénients

- ❌ Pas de free tier premium
- ❌ Moins populaire

### 🚀 Setup rapide

```
1. Render.com → Sign up (GitHub)
2. New Web Service → Select repo
3. Environment: Python 3.11
4. Build command: pip install -r requirements.txt
5. Start command: streamlit run src/app.py --server.port=10000
6. Add env vars
7. Deploy!
```

### 📖 Ressources

- [Render docs](https://render.com/docs)
- [Streamlit on Render](https://render.com/docs/deploy-streamlit)

### Idéal pour

- 🎯 Vous voulez Heroku mais plus moderne
- 🎯 Performance acceptable
- 🎯 Setup simple

---

## 🟠 5. DOCKER + VPS (Complet)

### ✅ Avantages

- ✅ **Full control** du serveur
- ✅ **Pas de limites** d'apps
- ✅ **Custom domain** facile
- ✅ **Performance excellente**
- ✅ **Scaling** granulaire

### ❌ Inconvénients

- ❌ **Complex** setup
- ❌ **Maintenance** requise
- ❌ Besoin Linux/Docker knowledge
- ❌ Plus cher ($5-50/mois)

### 📦 Dockerfile exemple

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "src/app.py", "--server.port=8501"]
```

### 🚀 Deploy sur DigitalOcean (exemple)

```bash
# 1. Create Droplet (Ubuntu 22.04)
# 2. SSH into droplet

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Clone repo & build
git clone https://github.com/USERNAME/assistant_matanne.git
cd assistant_matanne
docker build -t jeux-app .

# 5. Run
docker run -d -p 80:8501 \
  -e FOOTBALL_DATA_API_KEY=token \
  -e DATABASE_URL=postgresql://... \
  jeux-app

# 6. Setup nginx (reverse proxy)
# 7. Setup SSL (Let's Encrypt)
```

### 📖 Ressources

- [Docker + Streamlit](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
- [DigitalOcean Droplet](https://www.digitalocean.com/products/droplets/)
- [Nginx + Streamlit](https://discuss.streamlit.io/t/how-to-run-streamlit-on-a-subdirectory-using-nginx-reverse-proxy/21306)

### Idéal pour

- 🎯 Production critique
- 🎯 Scaling important
- 🎯 Vous maîtrisez Docker
- 🎯 Budget flexible

---

## 🟢 6. AWS (Enterprise)

### ✅ Avantages

- ✅ **Scalabilité infinie**
- ✅ **Reliability 99.9%+**
- ✅ **Services intégrés** (RDS, etc)
- ✅ **Global distribution**
- ✅ **Professional support**

### ❌ Inconvénients

- ❌ **Complexe** setup
- ❌ **Coûteux** (~$50+/mois)
- ❌ **Steep learning curve**
- ❌ Overkill pour cette app

### 🚀 Optionen (pick one)

#### Option A: AWS Elastic Beanstalk

```bash
# Similar à Heroku mais sur AWS
eb init -p python-3.11 jeux-app
eb create jeux-app-env
eb deploy
```

#### Option B: ECS + Fargate

- Docker + managed containers
- Auto-scaling
- $$$

### 📖 Ressources

- [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/)
- [Streamlit on AWS](https://aws.amazon.com/blogs/machine-learning/deploy-streamlit-apps-with-aws-amplify-console/)

### Idéal pour

- 🎯 Enterprise / Production
- 🎯 Millions d'utilisateurs
- 🎯 Budget illimité

---

## 🎯 Recommandation par cas d'usage

### 🎯 "Je viens de terminer, je veux tester rapidement"

**→ Streamlit Cloud** ⭐⭐⭐⭐⭐

- Gratuit
- 5 minutes
- Pas de config
- Parfait pour MVP

### 🎯 "Je veux produire, budget limité"

**→ Railway ou Render** ⭐⭐⭐⭐

- $5-10/mo
- Simple deploy
- Bon perf
- Parfait pour prod stable

### 🎯 "Je connais Heroku, j'aime l'écosystème"

**→ Heroku** ⭐⭐⭐⭐

- $7+/mo
- Add-ons intégrés
- Communauté grande
- Classique & fiable

### 🎯 "Je veux contrôle complet, je maîtrise Docker"

**→ Docker + VPS** ⭐⭐⭐⭐⭐

- $5-20/mo
- Full control
- Performance excelente
- Pour experts

### 🎯 "Je dois scale à l'infini, budget illimité"

**→ AWS ou Google Cloud** ⭐⭐⭐⭐⭐

- $$$
- Infinité de options
- Enterprise-grade
- Pour vraie prod

---

## 📝 Checklist de déploiement (générique)

Peu importe quelle plateforme, vous devez:

- [ ] Code pushé sur GitHub
- [ ] `.gitignore` inclut secrets
- [ ] `requirements.txt` à jour
- [ ] `src/app.py` existe
- [ ] Tests passent localement
- [ ] API keys en variables d'env (pas en dur)
- [ ] DB connection string en env
- [ ] App teste sur URL déployée
- [ ] Performance acceptable
- [ ] Secrets configurés

---

## 🚀 Étapes générales pour n'importe quelle plateforme

```
1. PRÉPARER
   - Code clean
   - Tests OK
   - Requirements.txt OK
   - Secrets en env vars

2. CONFIGURER
   - Créer compte plateforme
   - Connecter repo GitHub
   - Ajouter env variables

3. DÉPLOYER
   - Deploy button
   - Attendre build (2-5 min)
   - Tester l'URL

4. MONITORER
   - Vérifier logs
   - Tester fonctionnalités
   - Gérer secrets

5. MAINTENIR
   - Git push = auto-redeploy
   - Monitorer performance
   - Mettre à jour dépendances
```

---

## 💡 Pro Tips

### Tip 1: Tester localement avant de déployer

```bash
# Toujours tester d'abord
streamlit run src/app.py
# Si marche en local → 99% marche en cloud
```

### Tip 2: Utiliser environment variables

```python
import os

api_key = os.getenv("FOOTBALL_DATA_API_KEY")
db_url = os.getenv("DATABASE_URL")

# Jamais hardcoder!
```

### Tip 3: Monitorer les logs

```
Toujours vérifier:
- Build logs (import errors)
- Runtime logs (execution errors)
- Performance metrics
```

### Tip 4: Versionner requirements.txt

```bash
# Avant de déployer
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update deps"
git push
# Platform redeploy automatique!
```

---

## ❓ FAQ Déploiement

**Q: Mon app redémarre tout le temps?**  
A: Check les logs. Probable: import error ou missing env var.

**Q: Performance lente au démarrage?**  
A: Normal - premier démarrage cache modules. Deuxième chargement = rapide.

**Q: Comment update mon app?**  
A: Git push → Platform détecte → Auto redeploy (1-5 min).

**Q: Mes données disparaissent?**  
A: Normal si vous avez pas de BD externe! Utilisez Supabase.

**Q: Peux-je utiliser free tier?**  
A: Oui! Streamlit Cloud free tier est vraiment gratuit.

**Q: Combien coûte réellement?**  
A: Streamlit Cloud = gratuit. Si besoin plus = $5-10/mo environ.

---

## 🎉 You're Ready to Deploy!

Choisissez votre plateforme et lancez! 🚀

**Streamlit Cloud** est recommandé pour commencer.
→ [Guide complet ici](STREAMLIT_CLOUD_DEPLOYMENT.md)

---

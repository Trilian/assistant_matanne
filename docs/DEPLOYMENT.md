# 🚀 Guide de Déploiement — MaTanne

> **Dernière mise à jour** : Mars 2026

## Table des matières

1. [Prérequis](#prérequis)
2. [Variables d'environnement](#variables-denvironnement)
3. [Déploiement Local (Développement)](#déploiement-local)
4. [Déploiement Docker (Backend)](#déploiement-docker)
5. [Déploiement Frontend — Vercel](#déploiement-frontend--vercel)
6. [Base de données — Supabase](#base-de-données--supabase)
7. [Déploiement Backend — Railway](#déploiement-backend--railway)
8. [Vérification post-déploiement](#vérification-post-déploiement)

---

## Prérequis

| Composant        | Version minimale | Rôle                         |
|-----------------|-----------------|------------------------------|
| Python          | 3.13+           | Runtime backend               |
| Node.js         | 20+             | Runtime frontend              |
| Docker          | 24+             | Conteneurisation backend      |
| Compte Supabase | —               | PostgreSQL + Auth             |
| Compte Vercel   | —               | Hébergement frontend Next.js  |
| Compte Railway  | —               | Hébergement backend FastAPI   |

---

## Variables d'environnement

### Backend (`.env.local` à la racine)

```env
# ─── BASE DE DONNÉES ───
DATABASE_URL=postgresql://user:password@host:5432/database

# ─── SUPABASE ───
SUPABASE_URL=https://xxxxxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJxxxxxxxxxxxxxxxxxxxxx
SUPABASE_SERVICE_ROLE_KEY=eyJxxxxxxxxxxxxxxxxxxxxx

# ─── AUTHENTIFICATION JWT ───
JWT_SECRET_KEY=votre_secret_jwt_tres_long_et_aleatoire
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# ─── IA MISTRAL ───
MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MISTRAL_MODEL=mistral-small-latest
AI_RATE_LIMIT_DAILY=100
AI_RATE_LIMIT_HOURLY=20

# ─── APPLICATION ───
ENVIRONMENT=production       # development | production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://votre-domaine.vercel.app

# ─── NOTIFICATIONS PUSH ───
VAPID_PUBLIC_KEY=xxxxxxxxxxxx
VAPID_PRIVATE_KEY=xxxxxxxxxxxx
VAPID_SUBJECT=mailto:contact@exemple.com

# ─── REDIS (optionnel — cache L2) ───
REDIS_URL=redis://localhost:6379/0
```

### Frontend (`.env.local` dans `frontend/`)

```env
# URL de l'API backend
NEXT_PUBLIC_API_URL=https://votre-backend.railway.app

# Supabase (côté client — clé anon publique uniquement)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ Ne jamais committer les fichiers `.env.local`. Ils sont dans `.gitignore`.

---

## Déploiement Local

### Backend

```bash
# 1. Cloner le dépôt
git clone https://github.com/vous/assistant_matanne.git
cd assistant_matanne

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/macOS

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env.local
# Éditer .env.local avec vos valeurs

# 5. Initialiser la base de données (voir section Supabase)

# 6. Lancer le serveur de développement
python manage.py run
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger UI)
```

### Frontend

```bash
cd frontend

# 1. Installer les dépendances
npm install

# 2. Configurer les variables d'environnement
cp .env.example .env.local
# Éditer frontend/.env.local

# 3. Lancer le serveur de développement
npm run dev
# → http://localhost:3000
```

---

## Déploiement Docker

Le backend est conteneurisé avec le `Dockerfile` à la racine.

### Build et run local

```bash
# Build
docker build -t assistant-matanne-api .

# Run avec le fichier .env.local
docker run -p 8000:8000 --env-file .env.local assistant-matanne-api

# Run en détaché
docker run -d -p 8000:8000 --env-file .env.local --name matanne-api assistant-matanne-api
```

### Docker Compose (développement local complet)

```yaml
# docker-compose.yml (à créer si nécessaire)
version: '3.9'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env.local
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Variables d'environnement Docker

Toutes les variables dans `.env.local` sont passées avec `--env-file`. En production, utiliser les secrets de la plateforme (Railway secrets, Vercel env vars).

---

## Déploiement Frontend — Vercel

### Méthode GitHub (recommandée)

1. **Connecter le dépôt** : Vercel → "Import Project" → GitHub → `assistant_matanne`

2. **Configuration build** :
   - **Root Directory** : `frontend`
   - **Build Command** : `npm run build`
   - **Output Directory** : `.next`
   - **Framework Preset** : Next.js

3. **Variables d'environnement** (dans Settings → Environment Variables) :
   ```
   NEXT_PUBLIC_API_URL = https://votre-backend.railway.app
   NEXT_PUBLIC_SUPABASE_URL = https://xxxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJxxx...
   ```

4. **Déploiement** : automatique sur chaque push `main`

### Méthode CLI

```bash
cd frontend
npx vercel --prod
```

### Vérifier le build avant déploiement

```bash
cd frontend
npm run build   # Vérifie les erreurs TypeScript et de build
npm run lint    # Vérifie le linting ESLint
```

---

## Base de données — Supabase

### Initialisation du schéma (première fois)

1. **Créer un projet Supabase** : https://supabase.com/dashboard

2. **Récupérer les credentials** dans Settings → API :
   - Project URL → `SUPABASE_URL`
   - `anon` key → `SUPABASE_ANON_KEY`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY`
   - Database URL → `DATABASE_URL` (Settings → Database)

3. **Exécuter le schéma initial** dans Supabase SQL Editor :
   ```sql
   -- Copier et coller le contenu de sql/INIT_COMPLET.sql
   -- Ce fichier crée toutes les tables, RLS, triggers et vues
   ```

4. **Vérifier la connexion** :
   ```bash
   python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect(); print('OK')"
   ```

### Appliquer des migrations

```bash
# Créer une nouvelle migration
python manage.py create-migration

# Lister les migrations en attente
python manage.py migrate --dry-run

# Appliquer les migrations
python manage.py migrate
```

Les fichiers de migration sont dans `sql/migrations/`. La table `schema_migrations` en DB trace les migrations appliquées.

### Row Level Security (RLS)

Toutes les tables ont RLS activé. Les politiques sont définies dans `sql/INIT_COMPLET.sql`. Toujours utiliser le `service_role_key` dans le backend pour contourner RLS (accès admin), et le token JWT utilisateur pour l'accès filtré.

### Sauvegarde

```bash
# Export via pg_dump (remplacer les credentials)
pg_dump "postgresql://user:pass@host:5432/db" > backup_$(date +%Y%m%d).sql
```

---

## Déploiement Backend — Railway

### Méthode GitHub (recommandée)

1. **Créer un projet Railway** : https://railway.app/new

2. **Connecter le dépôt GitHub**

3. **Configuration du service** :
   - **Root Directory** : `/` (racine du projet)
   - **Start Command** : `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Build Command** : `pip install -r requirements.txt`
   - Ou utiliser le **Dockerfile** (Railway le détecte automatiquement)

4. **Variables d'environnement** dans Railway → Variables :
   ```
   DATABASE_URL = postgresql://...
   SUPABASE_URL = https://...
   SUPABASE_ANON_KEY = eyJ...
   SUPABASE_SERVICE_ROLE_KEY = eyJ...
   JWT_SECRET_KEY = ...
   MISTRAL_API_KEY = ...
   ENVIRONMENT = production
   CORS_ORIGINS = https://votre-frontend.vercel.app
   ```

5. **Domaine** : Railway fournit un domaine automatique `*.railway.app`. L'utiliser comme `NEXT_PUBLIC_API_URL` dans Vercel.

### Scaling

Le `Dockerfile` utilise 1 worker (`--workers 1`) pour économiser la RAM sur le plan gratuit Railway (512 MB). Augmenter selon les ressources disponibles.

---

## Vérification post-déploiement

### Backend

```bash
# Health check
curl https://votre-backend.railway.app/health
# → {"status": "healthy", "version": "1.0", ...}

# Documentation Swagger
open https://votre-backend.railway.app/docs

# Vérifier l'authentification
curl -X POST https://votre-backend.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "password"}'
```

### Frontend

```bash
# Vérifier la page de connexion
open https://votre-frontend.vercel.app/connexion

# Vérifier les variables d'environnement chargées
open https://votre-frontend.vercel.app/api/health
```

### Checklist complète

- [ ] Backend répond sur `/health`
- [ ] Swagger accessible sur `/docs`
- [ ] Frontend charge le login
- [ ] Login fonctionne (token JWT reçu)
- [ ] Dashboard charge après login
- [ ] Requêtes API réussies (network tab = 200)
- [ ] Pas d'erreur CORS dans la console browser
- [ ] RLS Supabase filtre correctement les données utilisateur

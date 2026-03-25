# Workflows CI/CD — Assistant Matanne

Configuration GitHub Actions pour l'intégration continue et le déploiement continu.

## 📋 Workflows disponibles

### 1. Backend Tests (`backend-tests.yml`)

**Déclenchement** : Push sur `main`/`develop` ou PR touchant les fichiers backend

**Actions** :
- ✅ Linter (ruff)
- ✅ Formatter check (black)
- ✅ Type checker (mypy) — permissif
- ✅ Tests unitaires + couverture (pytest)
- ✅ Upload coverage vers Codecov
- ✅ Fail si couverture < 70%

**Services** :
- PostgreSQL 15 (base de test)

**Secrets requis** :
- `CODECOV_TOKEN` — Token Codecov (optionnel)
- `MISTRAL_API_KEY` — Clé API Mistral pour tests IA

---

### 2. Frontend Tests (`frontend-tests.yml`)

**Déclenchement** : Push sur `main`/`develop` ou PR touchant les fichiers frontend

**Actions** :
- ✅ Linter (ESLint)
- ✅ Type check (TypeScript)
- ✅ Tests unitaires (Vitest)
- ✅ Build production (Next.js)
- ✅ Tests E2E (Playwright) — permissif

**Artifacts** :
- Coverage reports (7 jours)
- Playwright reports (7 jours)

---

### 3. Deploy Production (`deploy-production.yml`)

**Déclenchement** : 
- Push sur `main`
- Déclenchement manuel (workflow_dispatch)

**Jobs** :
1. **deploy-backend** : Déploie backend sur Railway
   - Déploiement via Railway API
   - Exécution migrations DB automatiques
2. **deploy-frontend** : Déploie frontend sur Vercel
   - Build production optimisé
   - Déploiement avec arguments `--prod`
3. **notify** : Notification Slack (optionnel)

**Secrets requis** :
- `RAILWAY_TOKEN` — Token d'API Railway
- `PRODUCTION_DATABASE_URL` — URL base de données production
- `VERCEL_TOKEN` — Token d'API Vercel
- `VERCEL_ORG_ID` — ID organisation Vercel
- `VERCEL_PROJECT_ID` — ID projet Vercel
- `SLACK_WEBHOOK_URL` — Webhook Slack (optionnel)

---

### 4. Deploy Preview (`deploy-preview.yml`)

**Déclenchement** : Ouverture/mise à jour d'une Pull Request

**Actions** :
- 🚀 Déploiement preview frontend sur Vercel
- 💬 Commentaire PR avec URLs preview
- 🧪 Smoke tests (health checks)

**Secrets requis** :
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `BACKEND_PREVIEW_URL` — URL backend preview (ex: staging Railway)

---

## ⚙️ Configuration requise

### GitHub Secrets

Allez dans **Settings → Secrets and variables → Actions** et ajoutez :

```
# Backend
CODECOV_TOKEN=xxx
MISTRAL_API_KEY=xxx

# Vercel
VERCEL_TOKEN=xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx

# Railway
RAILWAY_TOKEN=xxx

# Database
PRODUCTION_DATABASE_URL=postgresql://...

# Preview
BACKEND_PREVIEW_URL=https://staging-api.assistant-matanne.fr

# Optionnel
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Variables d'environnement Vercel

Dans le dashboard Vercel, configurez :
- `NEXT_PUBLIC_API_URL` : URL de l'API backend

### Variables d'environnement Railway

Dans Railway, configurez :
- `DATABASE_URL` : URL PostgreSQL
- `JWT_SECRET` : Secret JWT
- `MISTRAL_API_KEY` : Clé API Mistral
- `SUPABASE_URL` : URL Supabase
- `SUPABASE_SERVICE_KEY` : Clé service Supabase

---

## 🚦 Statuts des workflows

Les badges de statut apparaissent dans le README principal :

```markdown
![Backend Tests](https://github.com/votreorg/assistant-matanne/workflows/Backend%20Tests/badge.svg)
![Frontend Tests](https://github.com/votreorg/assistant-matanne/workflows/Frontend%20Tests/badge.svg)
```

---

## 📊 Codecov

La couverture de code est suivie sur [Codecov.io](https://codecov.io).

**Objectif** : Maintenir une couverture > 70%

**Badge** :
```markdown
[![codecov](https://codecov.io/gh/votreorg/assistant-matanne/branch/main/graph/badge.svg)](https://codecov.io/gh/votreorg/assistant-matanne)
```

---

## 🔄 Workflow de développement

### Feature branches

1. Créer une branche depuis `develop` : `feature/nom-feature`
2. Pusher → Tests automatiques s'exécutent
3. Ouvrir une PR → Preview deployment créé
4. Review + merge dans `develop`

### Release vers production

1. Merger `develop` dans `main`
2. Push → Déploiement automatique en production
3. Vérifier logs Railway + Vercel
4. Tester production : https://assistant-matanne.vercel.app

---

## 🐛 Debugging

### Tests échouent

1. Vérifier les logs GitHub Actions (onglet "Actions")
2. Reproduire localement :
   ```bash
   # Backend
   pytest --cov=src -v
   
   # Frontend
   cd frontend && npm test
   ```

### Déploiement échoue

1. Vérifier les secrets GitHub (Settings → Secrets)
2. Vérifier les logs Railway / Vercel
3. Vérifier les variables d'environnement

### Coverage trop basse

- Ajouter des tests pour les modules non couverts
- Voir rapport détaillé sur Codecov.io

---

## 📝 Maintenance

**Mise à jour des workflows** :
1. Modifier les fichiers `.github/workflows/*.yml`
2. Commit + push
3. Les workflows s'exécutent avec la nouvelle config

**Ajout de nouveaux workflows** :
1. Créer un nouveau fichier `.yml` dans `.github/workflows/`
2. Définir `on:` (triggers) et `jobs:` (actions)
3. Documenter dans ce README

---

**Dernière mise à jour** : Mars 2026

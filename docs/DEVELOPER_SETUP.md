# Developer Setup

> Installation locale complète pour développer sur Assistant Matanne.

---

## Prérequis

- Python 3.13+
- Node.js 20+
- npm
- accès à une base PostgreSQL ou Supabase
- Git

Optionnel:

- Docker Desktop pour la stack staging locale
- Playwright pour les tests E2E

---

## 1. Cloner et préparer l'environnement

```bash
git clone <repo>
cd assistant_matanne
python -m venv .venv
```

Activer l'environnement puis installer les dépendances backend:

```bash
pip install -r requirements.txt
```

Installer le frontend:

```bash
cd frontend
npm install
cd ..
```

---

## 2. Configurer les variables d'environnement

Le projet utilise un fichier unique `.env.local` à la racine.

Variables minimales:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
JWT_SECRET_KEY=...
MISTRAL_API_KEY=...
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_VAPID_PUBLIC_KEY=
```

---

## 3. Initialiser la base

Pour une première installation:

1. créer la base cible
2. exécuter `sql/INIT_COMPLET.sql`
3. vérifier la connexion

Commande de contrôle:

```bash
python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect(); print('OK')"
```

---

## 4. Lancer l'application

Backend:

```bash
python manage.py run
```

Frontend:

```bash
cd frontend
npm run dev
```

URLs utiles:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

---

## 5. Tests et qualité

Backend:

```bash
pytest -v
python manage.py test_coverage
python manage.py lint
python manage.py format_code
```

Frontend:

```bash
cd frontend
npm run lint
npm test
npx next build
```

E2E:

```bash
cd frontend
npx playwright test
```

---

## 6. Staging local avec Docker

Le dépôt fournit `docker-compose.staging.yml` pour monter une stack locale avec PostgreSQL, backend et frontend.

Exemples:

```bash
python manage.py staging start
python manage.py staging logs
python manage.py staging stop
```

---

## 7. Outils utiles en développement

- `/admin` pour diagnostiquer jobs, cache et services
- `/docs` pour tester les routes FastAPI
- `.pre-commit-config.yaml` pour la qualité avant commit

---

## 8. Points d'attention

- ne pas committer `.env.local`
- utiliser les factories et patterns de session DB du projet
- privilégier les noms et docstrings en français côté backend
- garder les docs à jour quand une feature modifie des flux admin, jobs ou notifications
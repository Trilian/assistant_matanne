# Guide Contribution — Assistant Matanne

> **Type de projet** : Personnel / Familial — Pas de contributions externes  
> **Mainteneur** : Famille Matanne  
> **Branches** : `main` (production), `staging` (pre-prod optionnel)

---

## Workflow de développement

### 1. Setup initial

```bash
# Backend
python -m venv .venv-1
.\.venv-1\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Variables d'environnement
cp .env.example .env.local  # ou créer depuis zéro (voir DEVELOPER_SETUP.md)
```

### 2. Lancer le projet

```bash
# Terminal 1 — Backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
# ou :
python manage.py run

# Terminal 2 — Frontend
cd frontend && npm run dev
```

### 3. Workflow Git

```bash
# Toujours partir de main à jour
git pull origin main

# Créer une branche feature (optionnel pour projet perso)
git checkout -b feat/nom-feature

# Committer avec message descriptif
git add .
git commit -m "feat(cuisine): ajouter filtrage par saison dans les recettes"

# Revenir sur main et merger
git checkout main
git merge feat/nom-feature
git push origin main
```

---

## Conventions de commit (Conventional Commits)

```
<type>(<scope>): <description courte>

Types :
  feat     — Nouvelle fonctionnalité
  fix      — Correction de bug
  docs     — Documentation uniquement
  style    — Formatage, espaces (pas de logique)
  refactor — Refactorisation (ni feat ni fix)
  test     — Ajout / modification de tests
  chore    — Mise à jour dépendances, config

Scopes recommandés :
  cuisine, famille, maison, jeux, planning, habitat
  api, core, services, frontend, db, auth, tests, docs

Exemples :
  feat(jeux): ajouter backtest stratégie paris
  fix(courses): corriger déduplication articles identiques
  docs(h): créer guide IA avancée sprint H
  chore: mettre à jour mistralai 1.3.0
```

---

## Conventions de code

### Backend Python

- **Langue** : Français partout (variables, fonctions, commentaires, docstrings)
- **Formatter** : `black` (`python manage.py format_code`)
- **Linter** : `ruff` (`python manage.py lint`)
- **Type hints** : Obligatoires (PEP 561, `py.typed` présent)
- **Docstrings** : Format Google style en français

```python
# ✅ Correct
def obtenir_recettes_par_saison(saison: str, limite: int = 20) -> list[Recette]:
    """Retourne les recettes disponibles pour la saison donnée.
    
    Args:
        saison: Saison parmi 'printemps', 'ete', 'automne', 'hiver'
        limite: Nombre maximum de recettes retournées
        
    Returns:
        Liste de Recette triée par note décroissante
        
    Raises:
        ValueError: Si la saison n'est pas reconnue
    """
    ...

# ❌ Éviter
def getRecipes(season, limit=20):
    # get recipes
    ...
```

### Frontend TypeScript

- **Langue** : Français pour les noms de variables et hooks, anglais pour composants shadcn/ui
- **Formatter** : ESLint (`npm run lint`)
- **Composants** : kebab-case pour les fichiers (`mon-composant.tsx`)
- **Hooks** : préfixe `utiliser-` (`utiliser-auth.ts`)
- **Stores** : préfixe `store-` (`store-auth.ts`)
- **Pattern** : `'use client'` en haut si composant client

```tsx
// ✅ Correct
export function CarteRecette({ recette }: { recette: Recette }) {
  const { utilisateur } = utiliserAuth();
  ...
}

// ❌ Éviter
export function RecipeCard({ recipe }: { recipe: any }) {
  const { user } = useAuth();
  ...
}
```

---

## Ajouter une fonctionnalité

### Pattern complet backend + frontend

**1. Base de données** (si nécessaire)
```bash
# Éditer le fichier thématique
notepad sql/schema/04_cuisine.sql  # ex: nouvelle table

# Régénérer INIT_COMPLET.sql
python scripts/db/regenerate_init.py

# Appliquer sur Supabase (SQL Editor)
# Mettre à jour ORM : src/core/models/cuisine.py
```

**2. API Backend**
```bash
# Schéma Pydantic : src/api/schemas/recettes.py
# Route : src/api/routes/recettes.py
# Service : src/services/cuisine/
```

**3. Client API Frontend**
```typescript
// src/bibliotheque/api/recettes.ts
export async function listerRecettesParSaison(saison: string) {
  const { data } = await apiClient.get(`/api/v1/recettes?saison=${saison}`);
  return data;
}
```

**4. Page / Composant**
```bash
# Page : frontend/src/app/(app)/cuisine/recettes/page.tsx
```

**5. Tests**
```bash
# Backend : tests/api/test_routes_recettes.py
# Frontend : vitest ou playwright
```

---

## Qualité du code

### Avant chaque commit

```bash
# Backend
python manage.py format_code    # black
python manage.py lint           # ruff
pytest tests/ -x --tb=short    # tests unitaires (stop au 1er echec)

# Frontend
cd frontend
npm run lint                    # ESLint
npx tsc --noEmit                # TypeScript check
npm test                        # Vitest
```

### Couverture de tests cible

| Couche | Cible |
| -------- | ------- |
| API routes | 80% |
| Core modules | 85% |
| Services métier | 75% |
| Frontend hooks | 70% |

---

## Structure des branches

```
main          ← Code de production — déployé automatiquement sur Railway
└── staging   ← Pre-production (optionnel, docker-compose.staging.yml)
```

**Règle** : Toujours tester en local avant de pusher sur `main`.

---

## Documentation

### Quand mettre à jour les docs ?

| Changement | Doc à mettre à jour |
| ----------- | --------------------- |
| Nouvelle route API | `docs/API_REFERENCE.md` |
| Nouveau module | `docs/MODULES.md` + guide module dans `docs/guides/` |
| Changement de schéma SQL | `docs/ERD_SCHEMA.md` + `docs/MIGRATION_GUIDE.md` |
| Nouvelle dépendance | `docs/MIGRATION_GUIDE.md` (section Stack actuelle) |
| Nouveau composant UI | `docs/DESIGN_SYSTEM.md` |
| Nouvelle variable d'env | `docs/DEPLOYMENT.md` + `.env.example` |

---

## Voir aussi

- [DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md) — Setup complet développeur
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — Architecture du projet
- [PATTERNS.md](docs/PATTERNS.md) — Patterns de code utilisés

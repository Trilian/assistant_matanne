# Guide Contribution â€” Assistant Matanne

> **Type de projet** : Personnel / Familial â€” Pas de contributions externes  
> **Mainteneur** : Famille Matanne  
> **Branches** : `main` (production), `staging` (pre-prod optionnel)

---

## Workflow de dÃ©veloppement

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
cp .env.example .env.local  # ou crÃ©er depuis zÃ©ro (voir DEVELOPER_SETUP.md)
```

### 2. Lancer le projet

```bash
# Terminal 1 â€” Backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
# ou :
python manage.py run

# Terminal 2 â€” Frontend
cd frontend && npm run dev
```

### 3. Workflow Git

```bash
# Toujours partir de main Ã  jour
git pull origin main

# CrÃ©er une branche feature (optionnel pour projet perso)
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
  feat     â€” Nouvelle fonctionnalitÃ©
  fix      â€” Correction de bug
  docs     â€” Documentation uniquement
  style    â€” Formatage, espaces (pas de logique)
  refactor â€” Refactorisation (ni feat ni fix)
  test     â€” Ajout / modification de tests
  chore    â€” Mise Ã  jour dÃ©pendances, config

Scopes recommandÃ©s :
  cuisine, famille, maison, jeux, planning, habitat
  api, core, services, frontend, db, auth, tests, docs

Exemples :
  feat(jeux): ajouter backtest stratÃ©gie paris
  fix(courses): corriger dÃ©duplication articles identiques
  docs(h): crÃ©er guide IA avancÃ©e sprint H
  chore: mettre Ã  jour mistralai 1.3.0
```

---

## Conventions de code

### Backend Python

- **Langue** : FranÃ§ais partout (variables, fonctions, commentaires, docstrings)
- **Formatter** : `black` (`python manage.py format_code`)
- **Linter** : `ruff` (`python manage.py lint`)
- **Type hints** : Obligatoires (PEP 561, `py.typed` prÃ©sent)
- **Docstrings** : Format Google style en franÃ§ais

```python
# âœ… Correct
def obtenir_recettes_par_saison(saison: str, limite: int = 20) -> list[Recette]:
    """Retourne les recettes disponibles pour la saison donnÃ©e.
    
    Args:
        saison: Saison parmi 'printemps', 'ete', 'automne', 'hiver'
        limite: Nombre maximum de recettes retournÃ©es
        
    Returns:
        Liste de Recette triÃ©e par note dÃ©croissante
        
    Raises:
        ValueError: Si la saison n'est pas reconnue
    """
    ...

# âŒ Ã‰viter
def getRecipes(season, limit=20):
    # get recipes
    ...
```

### Frontend TypeScript

- **Langue** : FranÃ§ais pour les noms de variables et hooks, anglais pour composants shadcn/ui
- **Formatter** : ESLint (`npm run lint`)
- **Composants** : kebab-case pour les fichiers (`mon-composant.tsx`)
- **Hooks** : prÃ©fixe `utiliser-` (`utiliser-auth.ts`)
- **Stores** : prÃ©fixe `store-` (`store-auth.ts`)
- **Pattern** : `'use client'` en haut si composant client

```tsx
// âœ… Correct
export function CarteRecette({ recette }: { recette: Recette }) {
  const { utilisateur } = utiliserAuth();
  ...
}

// âŒ Ã‰viter
export function RecipeCard({ recipe }: { recipe: any }) {
  const { user } = useAuth();
  ...
}
```

---

## Ajouter une fonctionnalitÃ©

### Pattern complet backend + frontend

**1. Base de donnÃ©es** (si nÃ©cessaire)
```bash
# Ã‰diter le fichier thÃ©matique
notepad sql/schema/04_cuisine.sql  # ex: nouvelle table

# RÃ©gÃ©nÃ©rer INIT_COMPLET.sql
python scripts/db/regenerate_init.py

# Appliquer sur Supabase (SQL Editor)
# Mettre Ã  jour ORM : src/core/models/cuisine.py
```

**2. API Backend**
```bash
# SchÃ©ma Pydantic : src/api/schemas/recettes.py
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

## QualitÃ© du code

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
| Services mÃ©tier | 75% |
| Frontend hooks | 70% |

---

## Structure des branches

```
main          â† Code de production â€” dÃ©ployÃ© automatiquement sur Railway
â””â”€â”€ staging   â† Pre-production (optionnel, docker-compose.staging.yml)
```

**RÃ¨gle** : Toujours tester en local avant de pusher sur `main`.

---

## Documentation

### Quand mettre Ã  jour les docs ?

| Changement | Doc Ã  mettre Ã  jour |
| ----------- | --------------------- |
| Nouvelle route API | `docs/API_REFERENCE.md` |
| Nouveau module | `docs/MODULES.md` + guide module dans `docs/guides/` |
| Changement de schÃ©ma SQL | `docs/ERD_SCHEMA.md` + `docs/MIGRATION_GUIDE.md` |
| Nouvelle dÃ©pendance | `docs/MIGRATION_GUIDE.md` (section Stack actuelle) |
| Nouveau composant UI | `docs/DESIGN_SYSTEM.md` |
| Nouvelle variable d'env | `docs/DEPLOYMENT.md` + `.env.example` |

---

## Voir aussi

- [DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md) â€” Setup complet dÃ©veloppeur
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) â€” Architecture du projet
- [PATTERNS.md](docs/PATTERNS.md) â€” Patterns de code utilisÃ©s

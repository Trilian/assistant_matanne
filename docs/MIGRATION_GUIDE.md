# Guide de Migration — Assistant Matanne

> Ce document recense les migrations de versions majeures déjà effectuées et les points d'attention pour les mises à jour futures.

---

## Workflow schéma DB

**Source de vérité : `sql/schema/*.sql` régénère `sql/INIT_COMPLET.sql`**

Le workflow actif est SQL-first et modulaire :

```text
✅ sql/schema/*.sql   ← source éditable du schéma
✅ sql/INIT_COMPLET.sql ← artefact régénéré pour initialisation complète
✅ sql/migrations/    ← journal incrémental des changements déjà appliqués
❌ alembic/           ← abandonné
```

### Initialisation d'une nouvelle DB

```sql
-- Dans Supabase SQL Editor ou psql :
-- Exécuter sql/INIT_COMPLET.sql dans son intégralité
```

### Ajouter une colonne ou une table

1. Modifier le fichier thématique concerné dans `sql/schema/`
2. Régénérer `sql/INIT_COMPLET.sql` avec `scripts/db/regenerate_init.py`
3. Sur la DB existante (Supabase), exécuter manuellement l'`ALTER TABLE` ou le `CREATE TABLE` correspondant
4. Mettre à jour le modèle ORM SQLAlchemy dans `src/core/models/`
5. Mettre à jour le schéma Pydantic dans `src/api/schemas/`
6. Consigner le delta dans `sql/migrations/` si la modification a déjà été appliquée sur un environnement persistant

> `INIT_COMPLET.sql` sert aux installations neuves. Les évolutions incrémentales restent appliquées explicitement sur les environnements existants.

---

## Workflow SQL-first — Structure modulaire

**Structure actuelle :**

```
sql/
├── INIT_COMPLET.sql          ← Régénéré automatiquement (NE PAS ÉDITER À LA MAIN)
├── schema/
│   ├── 01_extensions.sql     ← Extensions PostgreSQL (uuid-ossp, pgcrypto…)
│   ├── 02_functions.sql      ← Fonctions PL/pgSQL et triggers
│   ├── 03_cuisine.sql        ← Tables cuisine (recettes, ingrédients, planning, courses)
│   ├── 04_famille.sql        ← Tables famille (profils, activités, budget, santé)
│   ├── 05_maison.sql         ← Tables maison (projets, entretien, jardin, stocks)
│   ├── 06_habitat.sql        ← Tables habitat (scénarios, plans, veille)
│   ├── 07_jeux.sql           ← Tables jeux (paris, loto, euromillions)
│   ├── 08_systeme.sql        ← Tables système (logs, config, notifications)
│   ├── 09_rls_policies.sql   ← Politiques Row-Level Security
│   └── ...
└── migrations/               ← Changements incrémentiels (garde tel quel)
```

### Règle fondamentale — Ne jamais éditer INIT_COMPLET.sql directement

`INIT_COMPLET.sql` est **régénéré automatiquement** par le script `scripts/db/regenerate_init.py`.
Il ne faut **jamais l'éditer manuellement** — toute modification serait écrasée lors du prochain `make regenerate`.

### Workflow complet pour modifier le schéma

**Étape 1 — Modifier le fichier thématique dans `sql/schema/`**

```bash
# Exemple : ajouter une colonne à la table recettes
# Éditer sql/schema/03_cuisine.sql
#   ALTER TABLE recettes ADD COLUMN ... dans le CREATE TABLE correspondant
```

**Étape 2 — Régénérer `INIT_COMPLET.sql`**

```bash
python scripts/db/regenerate_init.py
# Concatène sql/schema/*.sql → sql/INIT_COMPLET.sql (avec header + séparateurs)
# Idempotent — peut être lancé plusieurs fois sans effet de bord
```

**Étape 3 — Appliquer sur la DB existante** (Supabase SQL Editor ou psql)

```sql
-- NE PAS réexécuter INIT_COMPLET.sql (DROP CASCADE sur toutes les tables !)
-- Exécuter UNIQUEMENT l'ALTER TABLE / CREATE TABLE de la modification :
ALTER TABLE recettes ADD COLUMN calories INTEGER DEFAULT NULL;
```

**Étape 4 — Logger dans `sql/migrations/`** (optionnel mais recommandé)

```bash
# Nommer le fichier avec la date et une description courte
touch sql/migrations/V008_20260401_add_recettes_calories.sql
# Contenu : la requête ALTER TABLE exacte appliquée
```

**Étape 5 — Mettre à jour le modèle ORM**

```python
# Fichier src/core/models/cuisine.py
class Recette(Base):
  ...
  calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

**Étape 6 — Mettre à jour le schéma Pydantic** (si exposé en API)

```python
# Fichier src/api/schemas/recettes.py
class RecetteResponse(BaseModel):
  ...
  calories: int | None = None
```

### Réinitialisation complète d'une DB vide

```bash
# 1. Régénérer INIT_COMPLET.sql depuis sql/schema/ (obligatoire si modifs récentes)
python scripts/db/regenerate_init.py

# 2. Exécuter dans Supabase SQL Editor (ou psql)
#    Copier-coller le contenu de sql/INIT_COMPLET.sql
#    ⚠️ DESTRUCTIF — DROP CASCADE sur tout !
```

### Vérifier la cohérence schéma ↔ ORM ↔ API

```bash
# Vérifier que tous les modèles ORM ont un CREATE TABLE dans INIT_COMPLET.sql
python -c "
import re
from pathlib import Path
from src.core.models import Base, charger_tous_modeles
charger_tous_modeles()
sql = Path('sql/INIT_COMPLET.sql').read_text()
sql_tables = set(re.findall(r'CREATE TABLE (?:IF NOT EXISTS )?(\w+)', sql))
missing = [m.class_.__tablename__ for m in Base.registry.mappers if m.class_.__tablename__ not in sql_tables]
if missing:
  print('MANQUANT:', missing)
else:
  print('OK — tous les modèles ORM ont un CREATE TABLE')
"
```

### Conventions de nommage SQL

| Objet | Convention | Exemple |
|-------|-----------|---------|
| Tables | `snake_case` pluriel | `recettes`, `paris_sportifs` |
| Colonnes | `snake_case` | `date_creation`, `user_id` |
| Index | `idx_{table}_{colonne(s)}` | `idx_recettes_user_id` |
| Contraintes FK | `fk_{table}_{ref}` | `fk_recettes_user` |
| Triggers | `trg_{table}_{action}` | `trg_recettes_updated_at` |
| Politiques RLS | `{table}_{role}_{action}` | `recettes_user_select` |


### Vérification cohérence ORM ↔ SQL

```bash
# Test automatique de cohérence :
python -c "
import re
from pathlib import Path
from src.core.models import Base, charger_tous_modeles
charger_tous_modeles()
sql = Path('sql/INIT_COMPLET.sql').read_text()
sql_tables = set(re.findall(r'CREATE TABLE (?:IF NOT EXISTS )?(\\w+)', sql))
for m in Base.registry.mappers:
    t = m.class_.__tablename__
    assert t in sql_tables, f'ORM table {t!r} absente de INIT_COMPLET.sql'
print('OK — tous les modèles ORM ont un CREATE TABLE')
"
```

---

## Stack actuelle (Mars 2026)

| Composant | Version | Requirement |
|-----------|---------|------------|
| **Python** | 3.13+ | `^3.13` |
| **FastAPI** | 0.109+ | `^0.109.0` |
| **Pydantic** | 2.5+ | `^2.5.0` |
| **SQLAlchemy** | 2.0+ | `^2.0.0` |
| **httpx** | 0.27–0.28 | `>=0.27,<0.29` |
| **mistralai** | 1.0+ | `^1.0.0` |
| **Node.js** | 20+ | `@types/node ^20` |
| **Next.js** | 16.2.1 | `next@16.2.1` |
| **React** | 19.2.4 | `react@19.2.4` |
| **TypeScript** | 5.x | `^5` |
| **Tailwind CSS** | 4.x | `^4` |
| **TanStack Query** | 5.94+ | `^5.94.5` |
| **Zustand** | 5.0+ | `^5.0.12` |
| **Zod** | 4.3+ | `^4.3.6` |

---

## Backend Python

### Python 3.12 → 3.13

**Breaking changes** :
- `distutils` supprimé définitivement (était déprécié depuis 3.10). Remplacer par `setuptools` si besoin.
- `typing.TypeAlias` est `type` depuis Python 3.12 (syntaxe `type X = ...`).
- `asyncio.get_event_loop()` sur un thread sans event loop lève une `DeprecationWarning`. Utiliser `asyncio.get_running_loop()` ou `asyncio.new_event_loop()`.
- Les f-strings supportent maintenant des expressions imbriquées (Python 3.12+).

**Ce qui a été fait dans ce projet** :
- SQLAlchemy 2.0 avec `Mapped[]` et `mapped_column` — compatible 3.13 natif.
- `asyncio_mode = strict` dans `pytest.ini` pour forcer les bonnes pratiques async.

---

### FastAPI 0.100 → 0.109+

**Migrations effectuées** :

**`on_event` → `lifespan`** (déprécié depuis 0.93) :
```python
# ❌ Ancien (déprécié)
@app.on_event("startup")
async def startup():
    ...

# ✅ Nouveau
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown

app = FastAPI(lifespan=lifespan)
```

**`response_model_exclude_unset`** : Utiliser dans les routeurs pour éviter de sérialiser les champs `None` par défaut :
```python
@router.get("/", response_model=MonSchema, response_model_exclude_unset=True)
```

**Compatibilité Pydantic v2** : FastAPI 0.109+ supporte nativement Pydantic v2. Les schémas `BaseModel` utilisent `model_dump()` au lieu de `dict()`, `model_validate()` au lieu de `parse_obj()`.

---

### Pydantic v1 → v2

**Ce projet utilise Pydantic v2 partout.** Points clés :

| v1 | v2 |
|----|-----|
| `validator` decorator | `field_validator` + `@classmethod` |
| `root_validator` | `model_validator(mode='before'/'after')` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `parse_obj()` | `model_validate()` |
| `schema()` | `model_json_schema()` |
| `__fields__` | `model_fields` |
| `Config` inner class | `model_config = ConfigDict(...)` |

**Exemple de migration schéma** :
```python
# ✅ Style Pydantic v2 utilisé dans ce projet
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

class RecetteCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nom: str = Field(..., min_length=1, max_length=200)
    temps_preparation: int = Field(..., ge=0)

    @field_validator("nom")
    @classmethod
    def nom_non_vide(cls, v: str) -> str:
        return v.strip()
```

---

### SQLAlchemy 1.4 → 2.0

**Ce projet utilise SQLAlchemy 2.0 exclusivement.** Points clés :

| 1.4 | 2.0 |
|-----|-----|
| `Column(Integer)` | `mapped_column(Integer)` |
| `relationship(...)` | `relationship(...)` + `Mapped[...]` |
| `session.query(Model)` | `select(Model)` + `session.execute()` |
| `session.query(Model).first()` | `session.scalar(select(Model))` |

**Pattern sessions** dans ce projet :
```python
# Dans les routes FastAPI
from src.api.utils import executer_avec_session, executer_async

def _query():
    with executer_avec_session() as session:
        result = session.execute(select(Recette)).scalars().all()
        return [r.__dict__ for r in result]

return await executer_async(_query)

# Dans les services
from src.core.decorators import avec_session_db

@avec_session_db
def creer_item(data: dict, db: Session) -> MonModel:
    item = MonModel(**data)
    db.add(item)
    db.commit()
    return item
```

**Chargement des modèles pour tests** : Toujours appeler `charger_tous_modeles()` avant `Base.metadata.create_all()` dans les fixtures de test, sinon les FK ne sont pas résolues :
```python
from src.core.models import charger_tous_modeles
charger_tous_modeles()
Base.metadata.create_all(bind=engine)
```

---

### httpx — Contrainte de version

**Contrainte actuelle** : `>=0.27,<0.29`

**Raison** : `mistralai ^1.0.0` requiert `httpx >= 0.28.1`. La version 0.29+ introduit des breaking changes dans `ASGITransport`.

**Impact sur les tests** : `starlette.testclient.TestClient` (synchrone) est **incompatible** avec httpx 0.28+. Utiliser obligatoirement `httpx.AsyncClient` :

```python
# ❌ Ne plus utiliser
from fastapi.testclient import TestClient
client = TestClient(app)

# ✅ Pattern obligatoire dans ce projet
import httpx
import pytest_asyncio

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_endpoint(client):
    response = await client.get("/api/v1/recettes")
    assert response.status_code == 200
```

**Si httpx 0.29 sort** : Vérifier les notes de release pour les changements `ASGITransport` avant de lever la contrainte.

---

## Frontend Node.js / Next.js

### Next.js 14 → 16 (App Router)

**Migrations effectuées** :

**Pages Router → App Router** :
```
pages/          → app/
pages/_app.tsx  → app/layout.tsx (+ providers)
pages/_document → intégré dans layout.tsx
getServerSideProps → React Server Components ou fetch()
getStaticProps  → generateStaticParams()
```

**Middleware** : En Next.js 16, le "middleware" est renommé "proxy" dans la terminologie interne mais `middleware.ts` à la racine de `src/` fonctionne toujours.

**Layout imbriqués** : Chaque dossier peut avoir son propre `layout.tsx`. Ce projet utilise :
```
app/layout.tsx          — root (providers : query, auth, theme)
app/(auth)/layout.tsx   — pages login/register
app/(app)/layout.tsx    — app protégée (sidebar + header)
```

**`loading.tsx` et `error.tsx`** : Ajoutés au niveau des modules hub. Les sous-routes n'ont pas de boundaries individuelles — comportement normal (elles héritent du module parent).

---

### React 18 → 19

**React 19 — Points clés** :

- **`use()` hook** : Permet de lire des Promises et Context directement dans le rendu.
- **`useActionState()`** : Nouveau hook pour les Server Actions (remplace `useFormState`).
- **`useOptimistic()`** : État optimiste automatique sur les mutations.
- **Ref comme prop** : Plus besoin de `forwardRef` — `ref` peut être passé directement.
- **`ReactDOM.preload/preinit`** : API de preloading de ressources.

**Ce projet** utilise React 19 côté client (SPA Next.js). Les Server Components sont disponibles mais non utilisés activement — toutes les pages ont `'use client'`.

---

### Tailwind CSS v3 → v4

**Breaking changes majeurs** :

| v3 | v4 |
|----|-----|
| `tailwind.config.ts` | Configuration via CSS `@theme` |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Plugins JS | Plugins CSS natifs |
| `theme.extend.colors` | `@theme { --color-X: ... }` |
| `darkMode: 'class'` | `@variant dark (&:is(.dark *))` |

**Ce projet** utilise `postcss.config.mjs` avec `@tailwindcss/postcss`. Les tokens de couleur par domaine sont définis dans `globals.css` via `@theme`.

**dark mode** : Déclaré via `next-themes` (ajoute la classe `dark` sur `<html>`). Les classes `dark:` Tailwind v4 fonctionnent automatiquement.

---

### TanStack Query v4 → v5

**Breaking changes** :

| v4 | v5 |
|----|-----|
| `useQuery({ onSuccess, onError })` | Callbacks supprimés — utiliser `useEffect` ou `useMutation` |
| `cacheTime` | `gcTime` |
| `useQuery(key, fn, options)` | `useQuery({ queryKey, queryFn, ...options })` |
| `isFetching` global | `useIsFetching()` hook |

**Ce projet** — les callbacks `onError` sont gérés globalement dans `utiliserMutation` via `sonner` toast. Les handlers individuels `onError` peuvent surcharger le défaut.

```typescript
// Pattern utilisé dans crochets/utiliser-api.ts
export function utiliserMutation<TData, TVariables>(
  mutationFn: (vars: TVariables) => Promise<TData>,
  options?: UseMutationOptions<TData, Error, TVariables>
) {
  return useMutation({
    mutationFn,
    onError: (error) => toast.error(error.message),  // défaut global
    ...options,  // options individuelles surchargent
  })
}
```

---

### Zustand v4 → v5

**Breaking changes** :

- L'API `createStore` est maintenant le pattern recommandé pour les stores partagés.
- `subscribeWithSelector` middleware intégré nativement.
- `immer` middleware maintenu mais patterns simplifiés.
- TypeScript : meilleure inférence sans `as` casting.

**Ce projet** — stores dans `magasins/` (nomenclature française). Pattern actuel compatible v5 :
```typescript
// magasins/store-auth.ts
import { create } from 'zustand'

interface AuthState {
  user: User | null
  setUser: (user: User | null) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}))
```

---

### Zod v3 → v4

**Breaking changes** :

| v3 | v4 |
|----|-----|
| `z.record(valueSchema)` | `z.record(z.string(), valueSchema)` — **2 args obligatoires** |
| `z.string().email()` | Inchangé |
| Performances | 2× plus rapide en v4 |
| `z.discriminatedUnion` | API légèrement modifiée |

**Ce projet** — `bibliotheque/validateurs.ts` utilise Zod v4. Toujours passer 2 arguments à `z.record()` :
```typescript
// ✅
z.record(z.string(), z.unknown())
z.record(z.string(), z.number())
// ❌
z.record(z.unknown())
```

---

## Considérations futures

### Upgrade httpx → 0.29+
- Attendre que `mistralai` supporte httpx 0.29 (suivre [mistralai releases](https://github.com/mistralai/client-python/releases))
- Vérifier l'API `ASGITransport` dans la release httpx 0.29
- Mettre à jour la contrainte dans `pyproject.toml` : `>=0.27,<0.30`

### Python 3.14 (prévu fin 2025)
- `typing.TypeForm` nouveau type
- GIL optionnel (expérimental depuis 3.13t) — potentiellement important pour les workers async
- Vérifier compatibilité SQLAlchemy, Pydantic, mistralai

### Next.js 17 (hypothétique)
- Surveiller la dépréciation de comportements App Router actuels
- `middleware.ts` / "proxy" : vérifier renommage officiel
- Partial Prerendering (PPR) : candidat pour les hubs statiques

### Supabase SDK v3 (si disponible)
- `supabase ^2.3.0` — surveiller les breaking changes d'auth et storage
- RLS : aucun impact (géré côté SQL, indépendant du SDK)

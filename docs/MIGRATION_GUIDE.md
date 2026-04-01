# Guide de Migration â€” Assistant Matanne

> Ce document recense les migrations de versions majeures dÃ©jÃ  effectuÃ©es et les points d'attention pour les mises Ã  jour futures.

---

## Workflow schÃ©ma DB (Phase 10)

**Source de vÃ©ritÃ© : `sql/schema/*.sql` rÃ©gÃ©nÃ¨re `sql/INIT_COMPLET.sql`**

Le workflow actif est SQL-first et modulaire :

```text
âœ… sql/schema/*.sql   â† source Ã©ditable du schÃ©ma
âœ… sql/INIT_COMPLET.sql â† artefact rÃ©gÃ©nÃ©rÃ© pour initialisation complÃ¨te
âœ… sql/migrations/    â† journal incrÃ©mental des changements dÃ©jÃ  appliquÃ©s
âŒ alembic/           â† abandonnÃ©
```

### Initialisation d'une nouvelle DB

```sql
-- Dans Supabase SQL Editor ou psql :
-- ExÃ©cuter sql/INIT_COMPLET.sql dans son intÃ©gralitÃ©
```

### Ajouter une colonne ou une table

1. Modifier le fichier thÃ©matique concernÃ© dans `sql/schema/`
2. RÃ©gÃ©nÃ©rer `sql/INIT_COMPLET.sql` avec `scripts/db/regenerate_init.py`
3. Sur la DB existante (Supabase), exÃ©cuter manuellement l'`ALTER TABLE` ou le `CREATE TABLE` correspondant
4. Mettre Ã  jour le modÃ¨le ORM SQLAlchemy dans `src/core/models/`
5. Mettre Ã  jour le schÃ©ma Pydantic dans `src/api/schemas/`
6. Consigner le delta dans `sql/migrations/` si la modification a dÃ©jÃ  Ã©tÃ© appliquÃ©e sur un environnement persistant

> `INIT_COMPLET.sql` sert aux installations neuves. Les Ã©volutions incrÃ©mentales restent appliquÃ©es explicitement sur les environnements existants.

---

## Workflow SQL-first â€” Structure modulaire (Sprint H)

**Structure depuis le Sprint H :**

```
sql/
â”œâ”€â”€ INIT_COMPLET.sql          â† RÃ©gÃ©nÃ©rÃ© automatiquement (NE PAS Ã‰DITER Ã€ LA MAIN)
â”œâ”€â”€ schema/
â”‚   â”œâ”€â”€ 01_extensions.sql     â† Extensions PostgreSQL (uuid-ossp, pgcryptoâ€¦)
â”‚   â”œâ”€â”€ 02_functions.sql      â† Fonctions PL/pgSQL et triggers
â”‚   â”œâ”€â”€ 03_cuisine.sql        â† Tables cuisine (recettes, ingrÃ©dients, planning, courses)
â”‚   â”œâ”€â”€ 04_famille.sql        â† Tables famille (profils, activitÃ©s, budget, santÃ©)
â”‚   â”œâ”€â”€ 05_maison.sql         â† Tables maison (projets, entretien, jardin, stocks)
â”‚   â”œâ”€â”€ 06_habitat.sql        â† Tables habitat (scÃ©narios, plans, veille)
â”‚   â”œâ”€â”€ 07_jeux.sql           â† Tables jeux (paris, loto, euromillions)
â”‚   â”œâ”€â”€ 08_systeme.sql        â† Tables systÃ¨me (logs, config, notifications)
â”‚   â”œâ”€â”€ 09_rls_policies.sql   â† Politiques Row-Level Security
â”‚   â””â”€â”€ ...
â””â”€â”€ migrations/               â† Changements incrÃ©mentiels (garde tel quel)
```

### RÃ¨gle fondamentale â€” Ne jamais Ã©diter INIT_COMPLET.sql directement

`INIT_COMPLET.sql` est **rÃ©gÃ©nÃ©rÃ© automatiquement** par le script `scripts/db/regenerate_init.py`.
Il ne faut **jamais l'Ã©diter manuellement** â€” toute modification serait Ã©crasÃ©e lors du prochain `make regenerate`.

### Workflow complet pour modifier le schÃ©ma

**Ã‰tape 1 â€” Modifier le fichier thÃ©matique dans `sql/schema/`**

```bash
# Exemple : ajouter une colonne Ã  la table recettes
# Ã‰diter sql/schema/03_cuisine.sql
#   ALTER TABLE recettes ADD COLUMN ... dans le CREATE TABLE correspondant
```

**Ã‰tape 2 â€” RÃ©gÃ©nÃ©rer `INIT_COMPLET.sql`**

```bash
python scripts/db/regenerate_init.py
# ConcatÃ¨ne sql/schema/*.sql â†’ sql/INIT_COMPLET.sql (avec header + sÃ©parateurs)
# Idempotent â€” peut Ãªtre lancÃ© plusieurs fois sans effet de bord
```

**Ã‰tape 3 â€” Appliquer sur la DB existante** (Supabase SQL Editor ou psql)

```sql
-- NE PAS rÃ©exÃ©cuter INIT_COMPLET.sql (DROP CASCADE sur toutes les tables !)
-- ExÃ©cuter UNIQUEMENT l'ALTER TABLE / CREATE TABLE de la modification :
ALTER TABLE recettes ADD COLUMN calories INTEGER DEFAULT NULL;
```

**Ã‰tape 4 â€” Logger dans `sql/migrations/`** (optionnel mais recommandÃ©)

```bash
# Nommer le fichier avec la date et une description courte
touch sql/migrations/V008_20260401_add_recettes_calories.sql
# Contenu : la requÃªte ALTER TABLE exacte appliquÃ©e
```

**Ã‰tape 5 â€” Mettre Ã  jour le modÃ¨le ORM**

```python
# Fichier src/core/models/cuisine.py
class Recette(Base):
  ...
  calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

**Ã‰tape 6 â€” Mettre Ã  jour le schÃ©ma Pydantic** (si exposÃ© en API)

```python
# Fichier src/api/schemas/recettes.py
class RecetteResponse(BaseModel):
  ...
  calories: int | None = None
```

### RÃ©initialisation complÃ¨te d'une DB vide

```bash
# 1. RÃ©gÃ©nÃ©rer INIT_COMPLET.sql depuis sql/schema/ (obligatoire si modifs rÃ©centes)
python scripts/db/regenerate_init.py

# 2. ExÃ©cuter dans Supabase SQL Editor (ou psql)
#    Copier-coller le contenu de sql/INIT_COMPLET.sql
#    âš ï¸ DESTRUCTIF â€” DROP CASCADE sur tout !
```

### VÃ©rifier la cohÃ©rence schÃ©ma â†” ORM â†” API

```bash
# VÃ©rifier que tous les modÃ¨les ORM ont un CREATE TABLE dans INIT_COMPLET.sql
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
  print('OK â€” tous les modÃ¨les ORM ont un CREATE TABLE')
"
```

### Conventions de nommage SQL

| Objet | Convention | Exemple |
| ------- | ----------- | --------- |
| Tables | `snake_case` pluriel | `recettes`, `paris_sportifs` |
| Colonnes | `snake_case` | `date_creation`, `user_id` |
| Index | `idx_{table}_{colonne(s)}` | `idx_recettes_user_id` |
| Contraintes FK | `fk_{table}_{ref}` | `fk_recettes_user` |
| Triggers | `trg_{table}_{action}` | `trg_recettes_updated_at` |
| Politiques RLS | `{table}_{role}_{action}` | `recettes_user_select` |


### VÃ©rification cohÃ©rence ORM â†” SQL

```bash
# Sprint 3 prÃ©voir test automatique :
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
print('OK â€” tous les modÃ¨les ORM ont un CREATE TABLE')
"
```

---

## Stack actuelle (Mars 2026)

| Composant | Version | Requirement |
| ----------- | --------- | ------------ |
| **Python** | 3.13+ | `^3.13` |
| **FastAPI** | 0.109+ | `^0.109.0` |
| **Pydantic** | 2.5+ | `^2.5.0` |
| **SQLAlchemy** | 2.0+ | `^2.0.0` |
| **httpx** | 0.27â€“0.28 | `>=0.27,<0.29` |
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

### Python 3.12 â†’ 3.13

**Breaking changes** :
- `distutils` supprimÃ© dÃ©finitivement (Ã©tait dÃ©prÃ©ciÃ© depuis 3.10). Remplacer par `setuptools` si besoin.
- `typing.TypeAlias` est `type` depuis Python 3.12 (syntaxe `type X = ...`).
- `asyncio.get_event_loop()` sur un thread sans event loop lÃ¨ve une `DeprecationWarning`. Utiliser `asyncio.get_running_loop()` ou `asyncio.new_event_loop()`.
- Les f-strings supportent maintenant des expressions imbriquÃ©es (Python 3.12+).

**Ce qui a Ã©tÃ© fait dans ce projet** :
- SQLAlchemy 2.0 avec `Mapped[]` et `mapped_column` â€” compatible 3.13 natif.
- `asyncio_mode = strict` dans `pytest.ini` pour forcer les bonnes pratiques async.

---

### FastAPI 0.100 â†’ 0.109+

**Migrations effectuÃ©es** :

**`on_event` â†’ `lifespan`** (dÃ©prÃ©ciÃ© depuis 0.93) :
```python
# âŒ Ancien (dÃ©prÃ©ciÃ©)
@app.on_event("startup")
async def startup():
    ...

# âœ… Nouveau
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown

app = FastAPI(lifespan=lifespan)
```

**`response_model_exclude_unset`** : Utiliser dans les routeurs pour Ã©viter de sÃ©rialiser les champs `None` par dÃ©faut :
```python
@router.get("/", response_model=MonSchema, response_model_exclude_unset=True)
```

**CompatibilitÃ© Pydantic v2** : FastAPI 0.109+ supporte nativement Pydantic v2. Les schÃ©mas `BaseModel` utilisent `model_dump()` au lieu de `dict()`, `model_validate()` au lieu de `parse_obj()`.

---

### Pydantic v1 â†’ v2

**Ce projet utilise Pydantic v2 partout.** Points clÃ©s :

| v1 | v2 |
| ---- | ----- |
| `validator` decorator | `field_validator` + `@classmethod` |
| `root_validator` | `model_validator(mode='before'/'after')` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `parse_obj()` | `model_validate()` |
| `schema()` | `model_json_schema()` |
| `__fields__` | `model_fields` |
| `Config` inner class | `model_config = ConfigDict(...)` |

**Exemple de migration schÃ©ma** :
```python
# âœ… Style Pydantic v2 utilisÃ© dans ce projet
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

### SQLAlchemy 1.4 â†’ 2.0

**Ce projet utilise SQLAlchemy 2.0 exclusivement.** Points clÃ©s :

| 1.4 | 2.0 |
| ----- | ----- |
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

**Chargement des modÃ¨les pour tests** : Toujours appeler `charger_tous_modeles()` avant `Base.metadata.create_all()` dans les fixtures de test, sinon les FK ne sont pas rÃ©solues :
```python
from src.core.models import charger_tous_modeles
charger_tous_modeles()
Base.metadata.create_all(bind=engine)
```

---

### httpx â€” Contrainte de version

**Contrainte actuelle** : `>=0.27,<0.29`

**Raison** : `mistralai ^1.0.0` requiert `httpx >= 0.28.1`. La version 0.29+ introduit des breaking changes dans `ASGITransport`.

**Impact sur les tests** : `starlette.testclient.TestClient` (synchrone) est **incompatible** avec httpx 0.28+. Utiliser obligatoirement `httpx.AsyncClient` :

```python
# âŒ Ne plus utiliser
from fastapi.testclient import TestClient
client = TestClient(app)

# âœ… Pattern obligatoire dans ce projet
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

**Si httpx 0.29 sort** : VÃ©rifier les notes de release pour les changements `ASGITransport` avant de lever la contrainte.

---

## Frontend Node.js / Next.js

### Next.js 14 â†’ 16 (App Router)

**Migrations effectuÃ©es** :

**Pages Router â†’ App Router** :
```
pages/          â†’ app/
pages/_app.tsx  â†’ app/layout.tsx (+ providers)
pages/_document â†’ intÃ©grÃ© dans layout.tsx
getServerSideProps â†’ React Server Components ou fetch()
getStaticProps  â†’ generateStaticParams()
```

**Middleware** : En Next.js 16, le "middleware" est renommÃ© "proxy" dans la terminologie interne mais `middleware.ts` Ã  la racine de `src/` fonctionne toujours.

**Layout imbriquÃ©s** : Chaque dossier peut avoir son propre `layout.tsx`. Ce projet utilise :
```
app/layout.tsx          â€” root (providers : query, auth, theme)
app/(auth)/layout.tsx   â€” pages login/register
app/(app)/layout.tsx    â€” app protÃ©gÃ©e (sidebar + header)
```

**`loading.tsx` et `error.tsx`** : AjoutÃ©s au niveau des modules hub. Les sous-routes n'ont pas de boundaries individuelles â€” comportement normal (elles hÃ©ritent du module parent).

---

### React 18 â†’ 19

**React 19 â€” Points clÃ©s** :

- **`use()` hook** : Permet de lire des Promises et Context directement dans le rendu.
- **`useActionState()`** : Nouveau hook pour les Server Actions (remplace `useFormState`).
- **`useOptimistic()`** : Ã‰tat optimiste automatique sur les mutations.
- **Ref comme prop** : Plus besoin de `forwardRef` â€” `ref` peut Ãªtre passÃ© directement.
- **`ReactDOM.preload/preinit`** : API de preloading de ressources.

**Ce projet** utilise React 19 cÃ´tÃ© client (SPA Next.js). Les Server Components sont disponibles mais non utilisÃ©s activement â€” toutes les pages ont `'use client'`.

---

### Tailwind CSS v3 â†’ v4

**Breaking changes majeurs** :

| v3 | v4 |
| ---- | ----- |
| `tailwind.config.ts` | Configuration via CSS `@theme` |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Plugins JS | Plugins CSS natifs |
| `theme.extend.colors` | `@theme { --color-X: ... }` |
| `darkMode: 'class'` | `@variant dark (&:is(.dark *))` |

**Ce projet** utilise `postcss.config.mjs` avec `@tailwindcss/postcss`. Les tokens de couleur par domaine sont dÃ©finis dans `globals.css` via `@theme`.

**dark mode** : DÃ©clarÃ© via `next-themes` (ajoute la classe `dark` sur `<html>`). Les classes `dark:` Tailwind v4 fonctionnent automatiquement.

---

### TanStack Query v4 â†’ v5

**Breaking changes** :

| v4 | v5 |
| ---- | ----- |
| `useQuery({ onSuccess, onError })` | Callbacks supprimÃ©s â€” utiliser `useEffect` ou `useMutation` |
| `cacheTime` | `gcTime` |
| `useQuery(key, fn, options)` | `useQuery({ queryKey, queryFn, ...options })` |
| `isFetching` global | `useIsFetching()` hook |

**Ce projet** â€” les callbacks `onError` sont gÃ©rÃ©s globalement dans `utiliserMutation` via `sonner` toast. Les handlers individuels `onError` peuvent surcharger le dÃ©faut.

```typescript
// Pattern utilisÃ© dans crochets/utiliser-api.ts
export function utiliserMutation<TData, TVariables>(
  mutationFn: (vars: TVariables) => Promise<TData>,
  options?: UseMutationOptions<TData, Error, TVariables>
) {
  return useMutation({
    mutationFn,
    onError: (error) => toast.error(error.message),  // dÃ©faut global
    ...options,  // options individuelles surchargent
  })
}
```

---

### Zustand v4 â†’ v5

**Breaking changes** :

- L'API `createStore` est maintenant le pattern recommandÃ© pour les stores partagÃ©s.
- `subscribeWithSelector` middleware intÃ©grÃ© nativement.
- `immer` middleware maintenu mais patterns simplifiÃ©s.
- TypeScript : meilleure infÃ©rence sans `as` casting.

**Ce projet** â€” stores dans `magasins/` (nomenclature franÃ§aise). Pattern actuel compatible v5 :
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

### Zod v3 â†’ v4

**Breaking changes** :

| v3 | v4 |
| ---- | ----- |
| `z.record(valueSchema)` | `z.record(z.string(), valueSchema)` â€” **2 args obligatoires** |
| `z.string().email()` | InchangÃ© |
| Performances | 2Ã— plus rapide en v4 |
| `z.discriminatedUnion` | API lÃ©gÃ¨rement modifiÃ©e |

**Ce projet** â€” `bibliotheque/validateurs.ts` utilise Zod v4. Toujours passer 2 arguments Ã  `z.record()` :
```typescript
// âœ…
z.record(z.string(), z.unknown())
z.record(z.string(), z.number())
// âŒ
z.record(z.unknown())
```

---

## ConsidÃ©rations futures

### Upgrade httpx â†’ 0.29+
- Attendre que `mistralai` supporte httpx 0.29 (suivre [mistralai releases](https://github.com/mistralai/client-python/releases))
- VÃ©rifier l'API `ASGITransport` dans la release httpx 0.29
- Mettre Ã  jour la contrainte dans `pyproject.toml` : `>=0.27,<0.30`

### Python 3.14 (prÃ©vu fin 2025)
- `typing.TypeForm` nouveau type
- GIL optionnel (expÃ©rimental depuis 3.13t) â€” potentiellement important pour les workers async
- VÃ©rifier compatibilitÃ© SQLAlchemy, Pydantic, mistralai

### Next.js 17 (hypothÃ©tique)
- Surveiller la dÃ©prÃ©ciation de comportements App Router actuels
- `middleware.ts` / "proxy" : vÃ©rifier renommage officiel
- Partial Prerendering (PPR) : candidat pour les hubs statiques

### Supabase SDK v3 (si disponible)
- `supabase ^2.3.0` â€” surveiller les breaking changes d'auth et storage
- RLS : aucun impact (gÃ©rÃ© cÃ´tÃ© SQL, indÃ©pendant du SDK)

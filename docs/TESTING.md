# Guide de Test Unifié

> Référence complète pour pytest (backend), Vitest (frontend), Playwright (E2E) — fixtures, patterns et bonnes pratiques.
>
> **Dernière mise à jour** : 1er avril 2026

---

## Vue d'ensemble

| Couche | Outil | Config | Commande |
| -------- | ------- | -------- | ---------- |
| **Backend** | pytest 7+ | `pytest.ini` + `pyproject.toml` | `pytest` |
| **Frontend unit** | Vitest | `frontend/vitest.config.ts` | `cd frontend && npm test` |
| **Frontend E2E** | Playwright | `frontend/playwright.config.ts` | `cd frontend && npx playwright test` |
| **Couverture backend** | pytest-cov | `pyproject.toml [tool.coverage]` | `python manage.py test_coverage` |
| **Contrats API** | Schemathesis | `pyproject.toml` | `pytest tests/contracts/` |
| **Performance** | benchmarks internes | `tests/benchmarks/` | `pytest tests/benchmarks/ -m benchmark` |
| **Load** | k6 | `tests/load/k6_baseline.js` | `k6 run tests/load/k6_baseline.js` |
| **Recette manuelle** | Telegram Sprint 5 | `docs/TELEGRAM_RECETTE_SPRINT5.md` | `pytest tests/api/test_webhooks_telegram_endpoints.py tests/api/test_webhooks_telegram_callbacks.py -q` |

---

## Backend — pytest

### Configuration (pytest.ini)

```ini
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
pythonpath = src
asyncio_mode = strict
asyncio_default_fixture_loop_scope = function
```

### Markers disponibles (17)

| Marker | Usage |
| -------- | ------- |
| `@pytest.mark.unit` | Tests rapides, sans dépendances externes |
| `@pytest.mark.integration` | Peut utiliser des dépendances externes |
| `@pytest.mark.slow` | Tests nécessitant optimisation |
| `@pytest.mark.requires_db` | Nécessite base de données |
| `@pytest.mark.requires_redis` | Nécessite Redis |
| `@pytest.mark.requires_internet` | Nécessite accès réseau |
| `@pytest.mark.endpoint` | Tests d'endpoints API |
| `@pytest.mark.auth` | Tests d'authentification |
| `@pytest.mark.rate_limit` | Tests de limitation de débit |
| `@pytest.mark.cache` | Tests de cache |
| `@pytest.mark.asyncio` | Tests asynchrones |
| `@pytest.mark.benchmark` | Mesures de performance |
| `@pytest.mark.contract` | Tests de contrat OpenAPI |
| `@pytest.mark.e2e` | Tests end-to-end |
| `@pytest.mark.visual` | Régression visuelle |
| `@pytest.mark.a11y` | Accessibilité |

### Structure des tests

```text
tests/
├── conftest.py              ← Fixtures racine (DB, services, factories)
├── api/                     ← Tests routes API (~54 fichiers)
│   ├── conftest.py          ← Fixtures API (app, client, auth override)
│   └── test_*_routes.py     ← Un fichier par domaine de routes
├── services/                ← Tests logique métier
│   ├── base/                ← Tests services de base
│   ├── cuisine/             ← Tests services cuisine
│   ├── famille/             ← Tests services famille
│   ├── maison/              ← Tests services maison
│   ├── jeux/                ← Tests services jeux
│   └── core/                ← Tests services core
├── core/                    ← Tests infrastructure
│   ├── conftest.py          ← Fixtures core (mocks session, redis, query)
│   ├── ai/                  ← Tests client IA
│   ├── models/              ← Tests modèles ORM
│   └── test_*.py            ← Cache, resilience, validation, event bus...
├── benchmarks/              ← Tests performance
├── contracts/               ← Tests contrat OpenAPI (Schemathesis)
├── load/                    ← Tests charge (k6)
└── sql/                     ← Tests cohérence schéma SQL
```

### Fixtures racine (tests/conftest.py)

#### Base de données

| Fixture | Scope | Usage |
| --------- | ------- | ------- |
| `engine` | session | SQLite in-memory + compatibilité JSONB |
| `db` | function | Session DB isolée avec auto-rollback |
| `test_db` | function | Alias de `db` (rétrocompatibilité) |
| `mock_session` | function | Alias de `db` (rétrocompatibilité) |

Particularités :

- **SQLite in-memory** avec traduction dialect PostgreSQL (JSONB → JSON)
- **Foreign keys activées** automatiquement
- **143+ modèles ORM** chargés avant les tests
- **Auto-rollback** par test pour isolation
- Singleton production remplacé globalement

#### Services

| Fixture | Service |
| --------- | --------- |
| `recette_service` | `ServiceRecettes()` |
| `inventaire_service` | `ServiceInventaire()` |
| `planning_service` | `ServicePlanning()` |
| `courses_service` | `ServiceCourses()` |

#### Factories de données

| Factory | Données par défaut |
| --------- | ------------------- |
| `RecetteFactory` | Recette avec compteur auto-incrémenté |
| `IngredientFactory` | Ingrédient avec compteur |
| `PlanningFactory` | Planning avec compteur |

#### Données échantillon

| Fixture | Contenu |
| --------- | --------- |
| `sample_recipe` | "Poulet Rôti" (6 portions, 75 min) |
| `sample_ingredients` | Dict de 3 ingrédients test |
| `sample_planning` | Semaine du 13 jan 2026 |
| `sample_articles` | 2 articles de courses mock |
| `sample_suggestions` | 3 suggestions IA mock |

#### Environnement

- Rate limiting désactivé (`RATE_LIMITING_DISABLED=true`)
- Environnement test (`ENVIRONMENT=test`)
- Auto-auth prêt pour mode développement

### Fixtures API (tests/api/conftest.py)

| Fixture | Usage |
| --------- | ------- |
| `disable_rate_limiting()` | Force `RATE_LIMITING_DISABLED=true` |
| `app(monkeypatch, db)` | TestClient FastAPI avec patches DB |

L'app fixture :

- Patche le compilateur JSONB avant import
- Mock `obtenir_contexte_db()` globalement
- Override `get_current_user` → `{"id": "test-user", "role": "admin"}`

### Fixtures core (tests/core/conftest.py)

| Fixture | Usage |
| --------- | ------- |
| `mock_session()` | Mock SQLAlchemy Session |
| `mock_query()` | Mock Query chaînable (`.filter()`, `.all()`, etc.) |
| `mock_model()` | Mock modèle ORM |
| `mock_redis()` | Mock client Redis |
| `mock_logger()` | MagicMock logger |

### Patterns de test

#### Test unitaire service

```python
@pytest.mark.unit
def test_create_recipe(recette_factory):
    recipe = recette_factory.create(nom="Tarte")
    assert recipe.nom == "Tarte"
```

#### Test intégration DB

```python
@pytest.mark.integration
def test_planning_service(db, planning_service):
    planning = Planning(nom="Test", ...)
    db.add(planning)
    db.commit()
    result = planning_service.get_planning(planning.id)
    assert result.nom == "Test"
```

#### Test endpoint API

```python
@pytest.mark.endpoint
def test_list_recipes(client):
    response = client.get("/api/v1/recettes")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
```

#### Test paramétré

```python
@pytest.mark.parametrize("difficulty", ["facile", "moyen", "difficile"])
def test_recipe_difficulty(recette_factory, difficulty):
    recipe = recette_factory.create(difficulte=difficulty)
    assert recipe.difficulte == difficulty
```

#### Test asynchrone

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### Commandes utiles

```bash
# Tous les tests
pytest

# Avec couverture
python manage.py test_coverage
# → pytest --cov=src --cov-report=html --cov-report=term

# Fichier spécifique
pytest tests/test_recettes.py -v

# Test unique
pytest tests/test_recettes.py::TestRecette::test_create -v

# Par marker
pytest -m unit
pytest -m "not slow"
pytest -m endpoint

# Rapport couverture HTML
open htmlcov/index.html
```

---

## Frontend — Vitest

### Configuration (frontend/vitest.config.ts)

- **Environnement** : jsdom (browser-like)
- **Globals** : true (pas d'imports pour `describe`, `it`, `expect`)
- **Setup** : `vitest.setup.ts` → `@testing-library/jest-dom/vitest`
- **Patterns** : `src/**/*.test.{ts,tsx}`, `__tests__/**/*.test.{ts,tsx}`

### Seuils de couverture

| Métrique | Seuil |
| ---------- | ------- |
| Lines | 50% |
| Functions | 50% |
| Branches | 40% |
| Statements | 50% |

Exclusions : layout files, middleware, providers.

### Pattern de test frontend

```typescript
import { describe, it, expect } from 'vitest'

describe('listerRecettes', () => {
  it('retourne une liste paginée', async () => {
    const result = await listerRecettes(1)
    expect(result.data).toBeDefined()
    expect(Array.isArray(result.data)).toBe(true)
  })
})
```

### Commandes

```bash
cd frontend

npm test              # Mode watch
npm run test:run      # Exécution unique
```

---

## Frontend — Playwright (E2E)

### Configuration (frontend/playwright.config.ts)

- **Dossier** : `frontend/e2e/`
- **Parallèle** : oui
- **Retries** : 2 en CI, 0 en local
- **Reporter** : HTML
- **Base URL** : `http://localhost:3000`
- **Locale** : `fr-FR`
- **Screenshots** : uniquement sur échec

### Navigateurs couverts

| Projet | Device |
| -------- | -------- |
| Desktop Chrome | Chromium |
| Mobile Chrome | Pixel 5 |
| Mobile Safari | iPhone 13 |

### Suite E2E (17 scénarios)

| Fichier | Couverture |
| --------- | ------------ |
| `accessibility.spec.ts` | Conformité a11y (axe-core) |
| `auth-flow.spec.ts` | Login/logout/2FA |
| `courses-collaboration.spec.ts` | Collaboration temps réel courses |
| `cuisine-complet.spec.ts` | Module cuisine complet |
| `famille-complet.spec.ts` | Module famille E2E |
| `inter-modules-flow.spec.ts` | Interactions inter-modules |
| `interactions.spec.ts` | UI interactions & formulaires |
| `jules-activites.spec.ts` | Profil enfant & activités |
| `maison-complet.spec.ts` | Module maison/entretien |
| `modules.spec.ts` | Navigation tous modules |
| `navigation.spec.ts` | Routage & navigation |
| `pages-interaction.spec.ts` | Interactions pages spécifiques |
| `parcours-utilisateur.spec.ts` | Parcours utilisateur complet |
| `planning-ia.spec.ts` | Planning repas avec IA |
| `projets-maison.spec.ts` | Projets maison workflow |
| `recettes-flow.spec.ts` | Création/gestion recettes |
| `visual-regression.spec.ts` | Comparison screenshots |

### Pattern E2E

```typescript
import { test, expect } from '@playwright/test'

test('user can login and view dashboard', async ({ page }) => {
  await page.goto('/')
  await page.fill('input[type="email"]', 'test@test.com')
  await page.fill('input[type="password"]', 'password')
  await page.click("button:has-text('Connexion')")
  await expect(page).toHaveURL('/dashboard')
})
```

### Commandes E2E

```bash
cd frontend

npx playwright test                    # Tous les E2E
npx playwright test e2e/auth-flow.spec.ts  # Fichier spécifique
npx playwright test --project=chromium     # Navigateur spécifique

# Régression visuelle
npm run test:visual
npm run test:visual:update             # Mettre à jour les snapshots
```

---

## Tests spécialisés

### Tests de contrat OpenAPI (Schemathesis)

```bash
pytest tests/contracts/test_openapi_contract.py -m contract
```

Valide que les endpoints respectent le schéma OpenAPI généré.

### Benchmarks performance

```bash
pytest tests/benchmarks/test_perf_core_operations.py -m benchmark
```

### Tests charge (k6)

```bash
k6 run tests/load/k6_baseline.js
```

### Tests cohérence schéma SQL

```bash
pytest tests/sql/test_schema_coherence.py
```

Vérifie l'alignement ORM ↔ SQL.

### Recette manuelle Telegram Sprint 5

Référence de validation manuelle: `docs/TELEGRAM_RECETTE_SPRINT5.md`

Cette recette couvre:

- les commandes slash (`/planning`, `/courses`, `/ajout`, `/repas`, `/jules`, `/maison`, `/budget`, `/meteo`, `/menu`, `/aide`)
- les callbacks inline (validation planning/courses, toggle des articles)
- les réponses rapides (`OK`, `oui`, `go`, `valide`)
- les fallbacks conversationnels historiques
- le briefing matinal enrichi

Pour la vérification automatisée associée:

```bash
pytest tests/api/test_webhooks_telegram_endpoints.py tests/api/test_webhooks_telegram_callbacks.py -q
```

---

## Bonnes pratiques

1. **Isolement** : chaque test est indépendant grâce aux fixtures auto-rollback
2. **Markers** : toujours annoter les tests avec le marker approprié
3. **Factories** : utiliser les factories plutôt que créer des données manuellement
4. **Nettoyage** : supprimer `__pycache__/` après refactoring pour éviter les `.pyc` obsolètes
5. **Mode test** : `ENVIRONMENT=test` et `RATE_LIMITING_DISABLED=true` sont automatiques
6. **Frontend** : les matchers `@testing-library/jest-dom` sont chargés globalement
7. **E2E** : les screenshots ne sont capturés que sur échec → pas de bruit en CI

---

## Couverture actuelle estimée

| Couche | Couverture | Objectif |
| -------- | ------------ | ---------- |
| Backend services | ~55% | 70% |
| Backend routes | ~50% | 65% |
| Frontend composants | ~40% | 50% |
| E2E scénarios critiques | ~80% | 90% |


---

# Testing Advanced

Guide d'execution pour le socle de tests avances:

- mutation testing (mutmut)
- contract testing OpenAPI (Schemathesis)
- visual regression (Playwright snapshots)

---

## 1) Prerequis

- Python 3.13+
- Node.js 20+
- dependances backend et frontend installees
- backend local disponible sur http://localhost:8000 pour certains usages

Installation backend des outils (si necessaire):

```bash
pip install mutmut schemathesis
```

---

## 2) Contract testing (Schemathesis)

Test de base present: `tests/contracts/test_openapi_contract.py`

Execution locale:

```bash
pytest tests/contracts -m contract -v
```

Notes:

- le test utilise `pytest.importorskip("schemathesis")` si le package manque
- l'ASGI app est chargee directement depuis `src.api.main:app`

---

## 3) Visual regression (Playwright)

Spec en place: `frontend/e2e/visual-regression.spec.ts`

Executer les snapshots:

```bash
cd frontend
npm run test:visual
```

Mettre a jour les baselines (apres validation UI):

```bash
cd frontend
npm run test:visual:update
```

Notes:

- les snapshots sont cibles sur la page connexion desktop/mobile
- en CI, les artefacts visuels sont uploades pour inspection

---

## 4) Mutation testing (mutmut)
## 5) Conventions de nommage des tests

### Structure cible

```
tests/
├── conftest.py                     → Fixtures globales (DB, client HTTP, auth)
├── api/
│   ├── conftest.py                 → Fixtures API (TestClient, headers auth)
│   ├── test_auth.py                → Tests auth (login, refresh, me)
│   ├── test_routes_{domain}.py     → Tests routes par domaine — convention principale
│   ├── test_hardening_{topic}.py   → Tests sécurité/rate-limiting/hardening
│   └── test_e2e.py                 → Tests end-to-end API
├── core/
│   ├── test_{module}.py            → Tests modules core (test_cache.py, test_config.py...)
│   ├── ai/test_{ai_module}.py      → Tests sous-module AI
│   └── models/test_{domain}.py     → Tests modèles ORM par domaine
├── services/
│   └── {domain}/test_{service}.py  → Tests services par domaine
├── contracts/                      → Tests contrat OpenAPI (Schemathesis)
├── benchmarks/                     → Tests performance
├── load/                           → Tests charge
└── sql/                            → Tests cohérence schéma SQL ↔ ORM
```

### Règles de nommage

| Contexte | Pattern | Exemples |
|---------|---------|---------|
| Tests de routes API | `test_routes_{domain}.py` | `test_routes_recettes.py`, `test_routes_jeux.py` |
| Tests de services | `test_{service_name}.py` dans `services/{domain}/` | `test_service.py`, `test_bankroll.py` |
| Tests unitaires core | `test_{module}.py` dans `core/` | `test_cache.py`, `test_config.py` |
| Tests de modèles ORM | `test_{domain}.py` dans `core/models/` | `test_recettes.py`, `test_jeux.py` |
| Tests sécurité | `test_hardening_{topic}.py` | `test_hardening_auth_rate.py` |
| Tests E2E | `test_e2e.py` | |
| Tests de contrat | `test_openapi_contract.py` | |

### Conventions pour les classes et méthodes

```python
# Fichier: tests/api/test_routes_recettes.py

class TestRecettesList:
	"""Tests GET /api/v1/recettes"""
    
	def test_liste_sans_auth_retourne_401(self, client):
		...
    
	def test_liste_avec_auth_retourne_200(self, client, auth_headers):
		...
    
	def test_liste_paginee_retourne_20_items_max(self, client, auth_headers):
		...

class TestRecettesCreate:
	"""Tests POST /api/v1/recettes"""
    
	def test_creation_valide_retourne_201(self, client, auth_headers, payload_recette):
		...
    
	def test_creation_sans_nom_retourne_422(self, client, auth_headers):
		...
```

Règles :
- Noms de méthodes descriptifs en français : `test_{action}_{condition}_retourne_{résultat}`
- Grouper par endpoint (classe `TestXxxList`, `TestXxxCreate`, `TestXxxUpdate`, `TestXxxDelete`)
- Un `conftest.py` par sous-dossier pour les fixtures spécifiques au domaine

### Fichiers ne respectant pas encore les conventions (TODO)

| Fichier actuel | Rename recommandé | Priorité |
|----------------|-------------------|---------|
| `api/test_api_automations_garmin_voyages.py` | `api/test_routes_automations_garmin.py` | 🟢 |
| `api/test_admin.py` + `api/test_admin_routes.py` | Fusionner en `api/test_routes_admin.py` | 🟡 |
| `services/test_automations_engine.py` | `services/automations/test_engine.py` | 🟢 |
| `services/test_cron_jobs.py` | `services/cron/test_cron_jobs.py` | 🟢 |
| `services/test_cron_legacy.py` | Fusionner dans `services/cron/test_cron_jobs.py` | 🟡 |
| `services/test_gamification_legacy.py` | `services/gamification/test_gamification.py` | 🟢 |
| `services/test_jeux_legacy.py` | `services/jeux/test_phases_tuw.py` ou fusionner | 🟢 |
| `services/test_notif_dispatcher_legacy.py` | `services/core/test_notif_dispatcher.py` | 🟡 |
| `services/test_recettes_enrichers.py` | `services/recettes/test_enrichers.py` | 🟢 |

> ⚠️ Avant tout renommage : s'assurer que pytest discover toujours les tests (`pytest --collect-only`).
> Mettre à jour les imports dans les CI/CD scripts si les chemins changent.

---

## 4) Mutation testing (mutmut)

Exemple d'execution sur un module cible:

```bash
mutmut run --paths-to-mutate src/services/dashboard
mutmut results
```

Conseils:

- lancer sur sous-modules cibles pour limiter le temps
- utiliser les resultats pour renforcer les tests unitaires existants

---

## 5) CI branchee

Backend (`.github/workflows/backend-tests.yml`):

- tests backend avec couverture
- tests contract `pytest tests/contracts -m contract -v`

Frontend (`.github/workflows/frontend-tests.yml`):

- lint + typecheck + unit + build
- visual regression `npm run test:visual`
- upload artefacts snapshots/resultats

---

## 6) Pipeline recommande en local

```bash
# Backend
pytest -v
pytest tests/contracts -m contract -v

# Frontend
cd frontend
npm run lint
npm run test:run
npm run test:visual
```

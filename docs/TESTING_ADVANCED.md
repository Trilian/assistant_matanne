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

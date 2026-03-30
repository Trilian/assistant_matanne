# Testing Advanced

Guide d'execution pour le socle Phase 10.11:

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

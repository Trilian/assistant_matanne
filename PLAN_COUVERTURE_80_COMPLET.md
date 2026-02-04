# 🎯 PLAN COMPLET POUR ATTEINDRE 80% DE COUVERTURE

## État Actuel (Mesuré le 2026-02-04)

| Métrique                  | Valeur                | Gap 80%          |
| ------------------------- | --------------------- | ---------------- |
| **Couverture Statements** | 11.33% (3,563/31,434) | +21,584 lignes   |
| **Couverture Branches**   | 0.37% (34/9,216)      | +7,339 branches  |
| **Couverture Totale**     | 8.85% (3,597/40,650)  | +28,923 éléments |
| **Tests existants**       | 3,908 tests           | -                |
| **Fichiers source**       | 175 fichiers          | -                |

---

## 📊 Analyse par Module (de htmlcov/index.html)

### Modules avec Couverture CORRECTE (>70%) ✅

Ces modules ont déjà une bonne couverture, peu d'effort requis:

| Module                               | Couverture | Lignes | Action |
| ------------------------------------ | ---------- | ------ | ------ |
| `src/core/constants.py`              | 97.20%     | 214    | ✅ OK  |
| `src/core/models/base.py`            | 96.43%     | 28     | ✅ OK  |
| `src/core/models/famille.py`         | 100%       | 82     | ✅ OK  |
| `src/core/models/maison.py`          | 100%       | 72     | ✅ OK  |
| `src/core/models/maison_extended.py` | 100%       | 163    | ✅ OK  |
| `src/core/models/courses.py`         | 98.36%     | 61     | ✅ OK  |
| `src/core/models/inventaire.py`      | 93.88%     | 49     | ✅ OK  |
| `src/core/models/jeux.py`            | 92.66%     | 177    | ✅ OK  |
| `src/core/models/batch_cooking.py`   | 90.07%     | 141    | ✅ OK  |

### Modules MOYENS (30-70%) ⚠️

Besoin d'amélioration:

| Module                      | Couverture | Gap 80%     | Effort |
| --------------------------- | ---------- | ----------- | ------ |
| `src/core/logging.py`       | 62.11%     | +17 lignes  | Faible |
| `src/core/errors_base.py`   | 57.50%     | +9 lignes   | Faible |
| `src/core/ai/cache.py`      | 37.31%     | +29 lignes  | Moyen  |
| `src/core/config.py`        | 37.31%     | +82 lignes  | Moyen  |
| `src/api/main.py`           | 34.52%     | +191 lignes | Élevé  |
| `src/core/cache.py`         | 33.65%     | +97 lignes  | Moyen  |
| `src/core/ai/rate_limit.py` | 34.48%     | +26 lignes  | Faible |
| `src/api/rate_limiting.py`  | 30.21%     | +96 lignes  | Moyen  |
| `src/core/cache_multi.py`   | 32.64%     | +160 lignes | Élevé  |

### Modules CRITIQUES (<30%) 🚨

Besoin de travail important:

| Module                    | Couverture | Lignes | Gap 80%     |
| ------------------------- | ---------- | ------ | ----------- |
| `src/core/database.py`    | 25.00%     | 200    | +110 lignes |
| `src/core/decorators.py`  | 27.45%     | 102    | +54 lignes  |
| `src/core/errors.py`      | 19.85%     | 131    | +79 lignes  |
| `src/core/ai/client.py`   | 12.50%     | 152    | +103 lignes |
| `src/core/ai/parser.py`   | 10.92%     | 174    | +120 lignes |
| `src/core/lazy_loader.py` | 0.00%      | 116    | +93 lignes  |
| `src/core/ai_agent.py`    | 0.00%      | 37     | +30 lignes  |

### Modules À 0% 🔴

Nécessitent des tests complets:

- `src/app.py` - 45 lignes (point d'entrée Streamlit)
- `src/domains/*` - ~15,000+ lignes (logique métier + UI)
- `src/services/*` - ~15,000+ lignes (services)
- `src/ui/*` - ~3,000+ lignes (composants UI)
- `src/utils/*` - ~2,000+ lignes (utilitaires)

---

## 🚀 PLAN EN 6 PHASES

### PHASE 1: CORE FOUNDATION (Semaine 1)

**Objectif**: Amener `src/core/` à 80%+

#### Jour 1-2: AI Module

```
tests/core/test_ai_client.py       → src/core/ai/client.py (12% → 80%)
tests/core/test_ai_parser.py       → src/core/ai/parser.py (10% → 80%)
tests/core/test_ai_cache.py        → src/core/ai/cache.py (37% → 80%)
tests/core/test_ai_rate_limit.py   → src/core/ai/rate_limit.py (34% → 80%)
```

**Gap à combler**: ~280 lignes

#### Jour 3-4: Infrastructure Core

```
tests/core/test_database.py        → src/core/database.py (25% → 80%)
tests/core/test_decorators.py      → src/core/decorators.py (27% → 80%)
tests/core/test_errors.py          → src/core/errors.py (19% → 80%)
tests/core/test_lazy_loader.py     → src/core/lazy_loader.py (0% → 80%)
tests/core/test_ai_agent.py        → src/core/ai_agent.py (0% → 80%)
```

**Gap à combler**: ~390 lignes

#### Jour 5: Cache & Performance

```
tests/core/test_cache.py           → src/core/cache.py (33% → 80%)
tests/core/test_cache_multi.py     → src/core/cache_multi.py (32% → 80%)
tests/core/test_config.py          → src/core/config.py (37% → 80%)
```

**Gap à combler**: ~340 lignes

**Livrable Phase 1**: `src/core/` à 80%+ (actuellement ~45%)

---

### PHASE 2: API MODULE (Semaine 2, Jours 1-3)

**Objectif**: Amener `src/api/` à 80%+

```
tests/api/test_main.py             → src/api/main.py (34% → 80%)
tests/api/test_rate_limiting.py    → src/api/rate_limiting.py (30% → 80%)
```

**Actions**:

1. Créer/compléter fixtures FastAPI dans `tests/fixtures/`
2. Tester tous les endpoints CRUD
3. Tester rate limiting et middlewares
4. Tester error handlers

**Gap à combler**: ~290 lignes

**Livrable Phase 2**: `src/api/` à 80%+

---

### PHASE 3: SERVICES (Semaine 2-3)

**Objectif**: Amener `src/services/` à 80%+

#### Services prioritaires (plus utilisés):

```
tests/services/test_recettes.py         → src/services/recettes.py
tests/services/test_inventaire.py       → src/services/inventaire.py
tests/services/test_courses.py          → src/services/courses.py
tests/services/test_planning.py         → src/services/planning.py
tests/services/test_auth.py             → src/services/auth.py
tests/services/test_backup.py           → src/services/backup.py
```

#### Services secondaires:

```
tests/services/test_barcode.py          → src/services/barcode.py
tests/services/test_base_ai_service.py  → src/services/base_ai_service.py
tests/services/test_batch_cooking.py    → src/services/batch_cooking.py
tests/services/test_budget.py           → src/services/budget.py
tests/services/test_calendar_sync.py    → src/services/calendar_sync.py
tests/services/test_weather.py          → src/services/weather.py
... (tous les services)
```

**Gap estimé**: ~12,000 lignes

**Livrable Phase 3**: `src/services/` à 80%+

---

### PHASE 4: DOMAINS (Semaine 3-4)

**Objectif**: Amener `src/domains/` à 80%+

#### Structure respectée:

```
tests/domains/cuisine/
├── services/     → src/domains/cuisine/logic/
└── ui/           → src/domains/cuisine/ui/

tests/domains/famille/
├── services/     → src/domains/famille/logic/
└── ui/           → src/domains/famille/ui/

tests/domains/jeux/
└── ui/           → src/domains/jeux/ (logic + ui)

tests/domains/maison/
├── services/     → src/domains/maison/logic/
└── ui/           → src/domains/maison/ui/

tests/domains/planning/
├── logic/        → src/domains/planning/logic/
└── ui/           → src/domains/planning/ui/

tests/domains/utils/
└── ui/           → src/domains/utils/ (logic + ui)
```

**Gap estimé**: ~12,000 lignes

**Livrable Phase 4**: `src/domains/` à 80%+

---

### PHASE 5: UI & UTILS (Semaine 5)

**Objectif**: Amener `src/ui/` et `src/utils/` à 80%+

#### UI Components:

```
tests/ui/test_components.py      → src/ui/components/
tests/ui/test_core.py           → src/ui/core/
tests/ui/test_feedback.py       → src/ui/feedback/
tests/ui/test_layout.py         → src/ui/layout/
```

#### Utils:

```
tests/utils/test_formatters.py   → src/utils/formatters/
tests/utils/test_helpers.py      → src/utils/helpers/
tests/utils/test_validators.py   → src/utils/validators/
```

**Gap estimé**: ~4,000 lignes

**Livrable Phase 5**: `src/ui/` et `src/utils/` à 80%+

---

### PHASE 6: TRANSVERSAL & FINALISATION (Semaine 5-6)

**Objectif**: Atteindre 80% global stable

#### Tests transverses existants à valider:

```
tests/integration/     → Tests d'intégration entre modules
tests/e2e/            → Tests end-to-end complets
tests/edge_cases/     → Cas limites
tests/benchmarks/     → Tests de performance
tests/property_tests/ → Tests basés sur propriétés
```

**Actions**:

1. Valider que tous tests passent
2. Combler les derniers gaps
3. Vérifier couverture branches (actuellement 0.37%)
4. Générer rapport final

---

## 📋 CHECKLIST PAR PHASE

### Phase 1: Core ☐

- [ ] `src/core/ai/client.py` → 80%
- [ ] `src/core/ai/parser.py` → 80%
- [ ] `src/core/ai/cache.py` → 80%
- [ ] `src/core/ai/rate_limit.py` → 80%
- [ ] `src/core/database.py` → 80%
- [ ] `src/core/decorators.py` → 80%
- [ ] `src/core/errors.py` → 80%
- [ ] `src/core/lazy_loader.py` → 80%
- [ ] `src/core/ai_agent.py` → 80%
- [ ] `src/core/cache.py` → 80%
- [ ] `src/core/cache_multi.py` → 80%
- [ ] `src/core/config.py` → 80%

### Phase 2: API ☐

- [ ] `src/api/main.py` → 80%
- [ ] `src/api/rate_limiting.py` → 80%

### Phase 3: Services ☐

- [ ] Tous les 35+ services → 80%

### Phase 4: Domains ☐

- [ ] `src/domains/cuisine/` → 80%
- [ ] `src/domains/famille/` → 80%
- [ ] `src/domains/jeux/` → 80%
- [ ] `src/domains/maison/` → 80%
- [ ] `src/domains/planning/` → 80%
- [ ] `src/domains/utils/` → 80%

### Phase 5: UI & Utils ☐

- [ ] `src/ui/` → 80%
- [ ] `src/utils/` → 80%

### Phase 6: Validation ☐

- [ ] Tests transverses OK
- [ ] Couverture globale ≥ 80%
- [ ] CI/CD mis à jour

---

## ⏱️ ESTIMATION TEMPORELLE

| Phase               | Durée   | Effort         | Priorité    |
| ------------------- | ------- | -------------- | ----------- |
| Phase 1: Core       | 5 jours | ~1,000 lignes  | 🔴 CRITIQUE |
| Phase 2: API        | 3 jours | ~290 lignes    | 🔴 HAUTE    |
| Phase 3: Services   | 7 jours | ~12,000 lignes | 🟠 HAUTE    |
| Phase 4: Domains    | 7 jours | ~12,000 lignes | 🟠 MOYENNE  |
| Phase 5: UI/Utils   | 3 jours | ~4,000 lignes  | 🟡 MOYENNE  |
| Phase 6: Validation | 2 jours | Validation     | 🟢 FINALE   |

**Total estimé: 27 jours de travail (~6 semaines)**

---

## 🔧 COMMANDES CLÉS

```bash
# Mesurer couverture globale
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Mesurer couverture par module
pytest tests/core/ --cov=src/core --cov-report=term-missing
pytest tests/api/ --cov=src/api --cov-report=term-missing
pytest tests/services/ --cov=src/services --cov-report=term-missing
pytest tests/domains/ --cov=src/domains --cov-report=term-missing

# Vérifier un fichier spécifique
pytest tests/core/test_database.py --cov=src/core/database.py --cov-report=term-missing

# Tests rapides (sans couverture)
pytest tests/ -q --tb=short

# Tests avec verbose
pytest tests/ -v --tb=long
```

---

## ✅ CRITÈRES DE SUCCÈS

1. **Couverture globale ≥ 80%** (actuellement 11.33%)
2. **Tous les modules principaux ≥ 75%**
3. **Aucun module < 60%**
4. **Tous les tests passent (0 failures)**
5. **Couverture branches ≥ 50%** (actuellement 0.37%)

---

**Généré**: 2026-02-04
**Basé sur**: htmlcov/index.html (3,908 tests collectés)

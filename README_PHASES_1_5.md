# 📚 GUIDE COMPLET: Amélioration couverture tests 29% → >80%

## 🎯 Objectif

Passer la couverture de tests de **29.37% à >80%** en 5 phases structurées sur 8 semaines (~340 heures).

## 📚 Documentation créée

### 🔴 PRIORITÉ HAUTE - Lire d'abord

1. **[MASTER_DASHBOARD.md](MASTER_DASHBOARD.md)** ⭐
   - Vue d'ensemble complète des 5 phases
   - Timeline et effort estimés
   - Status de chaque fichier
   - Checkpoints de validation

2. **[PLAN_ACTION_FINAL.md](PLAN_ACTION_FINAL.md)** ⭐
   - Commandes à exécuter pour chaque phase
   - Étapes détaillées
   - Scripts à lancer
   - **À lire en premier!**

### 🟡 PRIORITÉ MOYENNE - Détails PHASE 1

3. **[ACTION_PHASE_1_IMMEDIATEMENT.md](ACTION_PHASE_1_IMMEDIATEMENT.md)**
   - Tâches immédiates
   - Validation PHASE 1
   - Conseils pratiques

4. **[PHASE_1_IMPLEMENTATION_GUIDE.md](PHASE_1_IMPLEMENTATION_GUIDE.md)**
   - Guide complet PHASE 1
   - Patterns de test
   - Métriques de succès

### 🟢 PRIORITÉ BASSE - Reference

5. **[COVERAGE_EXECUTIVE_SUMMARY.md](COVERAGE_EXECUTIVE_SUMMARY.md)**
   - Données baseline de couverture
   - Top 10 fichiers à couvrir

6. **[TEST_COVERAGE_CHECKLIST.md](TEST_COVERAGE_CHECKLIST.md)**
   - Checklist hebdomadaire
   - Tracking de progression

---

## 🎬 DÉMARRAGE RAPIDE (5 minutes)

### 1️⃣ Comprendre la portée

```bash
# Voir le plan global
cat MASTER_DASHBOARD.md | head -50
```

### 2️⃣ Lancer PHASE 1

```bash
# Les fichiers de test ont déjà été GÉNÉRÉS par le script
# Vérifier:
ls -la tests/domains/maison/ui/test_depenses.py
ls -la tests/domains/planning/ui/components/test_components_init.py
ls -la tests/domains/famille/ui/test_jules_planning.py
ls -la tests/domains/cuisine/ui/test_planificateur_repas.py
ls -la tests/domains/jeux/test_setup.py
ls -la tests/domains/jeux/test_integration.py

# Exécuter les tests
pytest tests/utils/test_image_generator.py -v
pytest tests/utils/test_helpers_general.py -v
pytest tests/domains/maison/ui/test_depenses.py -v
```

### 3️⃣ Voir la couverture

```bash
# Générer rapport HTML
pytest --cov=src --cov-report=html

# Ouvrir dans navigateur
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html # Linux
```

---

## 📊 État actuel (État MAINTENANT)

```
📌 PHASE 1: 2/8 COMPLÉTÉES ✅
   ✅ test_image_generator.py (312 stmts)
   ✅ test_helpers_general.py (102 stmts)
   🔄 test_depenses.py (271 stmts) - Template généré
   🔄 test_components_init.py (?) - Template généré
   🔄 test_jules_planning.py (?) - Template généré
   🔄 test_planificateur_repas.py (?) - Template généré
   🔄 test_setup.py (?) - Template généré
   🔄 test_integration.py (?) - Template généré

📊 COUVERTURE ACTUELLE: 29.37%
   - Fichiers testés: 66/209
   - Statements couverts: 2,091

🎯 COUVERTURE CIBLE: >80%
   - Phases restantes: PHASE 2, 3, 4, 5
   - Effort total: ~330h restantes
   - Timeline: 8 semaines
```

---

## 🔄 Structure des 5 phases

### PHASE 1 (Sem. 1-2): Tests fichiers 0%

```
8 fichiers with 0% coverage
→ Expected gain: +3-5% (29% → 32-35%)
→ Effort: 35 hours
→ Status: 🔄 IN PROGRESS (2/8 done)
```

### PHASE 2 (Sem. 3-4): Améliorer tests <5%

```
12 fichiers with <5% coverage
→ Expected gain: +5-8% (32% → 40-45%)
→ Effort: 100 hours
→ Status: ⏳ NOT STARTED
→ CRITICAL: 4 fichiers ÉNORMES (825, 825, 659, 622 stmts)
```

### PHASE 3 (Sem. 5-6): Services

```
33 fichiers services (30% → 60%)
→ Expected gain: +10-15%
→ Effort: 80 hours
→ Status: ⏳ NOT STARTED
→ PARALLEL avec PHASE 4
```

### PHASE 4 (Sem. 5-6): UI (PARALLÈLE)

```
26 fichiers UI (37% → 70%)
→ Expected gain: +10-15%
→ Effort: 75 hours
→ Status: ⏳ NOT STARTED
→ PARALLEL avec PHASE 3
```

### PHASE 5 (Sem. 7-8): E2E

```
5 flux utilisateur complets
→ Expected gain: +2-3% (>80% FINAL) ✅
→ Effort: 50 hours
→ Status: ⏳ NOT STARTED
```

---

## 🛠️ Scripts d'automation

### Script 1: Générer PHASE 1 tests

```bash
python generate_phase1_tests.py
# ✅ ALREADY RUN - 6 fichiers générés
```

### Script 2: Exécuter all phases

```bash
python phase_executor.py
# Affiche le plan détaillé des 5 phases
```

### Script 3: Analyser couverture

```bash
python analyze_coverage.py
# Génère coverage_analysis.json
```

---

## 📋 Checklist action immédiate

### ☐ Jour 1: Valider PHASE 1

```bash
# Vérifier syntaxe Python
python -m py_compile tests/domains/maison/ui/test_depenses.py

# Exécuter les 8 tests
pytest tests/utils/test_image_generator.py -v
pytest tests/utils/test_helpers_general.py -v
pytest tests/domains/maison/ui/test_depenses.py -v
pytest tests/domains/planning/ui/components/test_components_init.py -v
pytest tests/domains/famille/ui/test_jules_planning.py -v
pytest tests/domains/cuisine/ui/test_planificateur_repas.py -v
pytest tests/domains/jeux/test_setup.py -v
pytest tests/domains/jeux/test_integration.py -v

# Générer rapport
pytest --cov=src --cov-report=html
```

### ☐ Jours 2-7: Améliorer templates PHASE 1

```
- Ajouter de vraies logiques aux templates générés
- Tester les cas d'erreur et edge cases
- Augmenter la couverture ligne + branche
- Viser >32% couverture
```

### ☐ Semaine 2: Compléter PHASE 1

```bash
# Valider que tous les 8 fichiers ont des tests réels
pytest tests/utils/ tests/domains/ -v --cov=src

# Vérifier gain: 29.37% → 32-35%
python analyze_coverage.py
```

### ☐ Semaine 3-4: PHASE 2

```bash
# Générer templates PHASE 2
python generate_phase2_tests.py  # À créer

# Remplir les 12 templates
# Priorité: 4 fichiers énormes (825, 825, 659, 622 stmts)
```

---

## 🎓 Concepts clés

### Mocking Streamlit

```python
from unittest.mock import patch

@patch('streamlit.write')
def test_something(mock_write):
    mock_write.return_value = None
    # Test code
    assert mock_write.called
```

### Fixtures DB

```python
@pytest.fixture
def db_session():
    from src.core.database import get_db_context
    with get_db_context() as session:
        yield session
        session.rollback()
```

### Patterns de test

```python
# Arrange
mock_data = {"key": "value"}

# Act
result = function_under_test(mock_data)

# Assert
assert result is not None
```

---

## 📊 Métriques de succès

### PHASE 1 (Maintenant)

- [ ] 8/8 fichiers avec tests
- [ ] Coverage: 32-35% (gain +3-5%)
- [ ] Tous les tests passent: ✅

### PHASE 2

- [ ] 12 fichiers avec tests améliorés
- [ ] Coverage: 40-45% (gain +5-8%)
- [ ] Focus: 4 UI énormes

### PHASE 3+4

- [ ] Services: 33 fichiers, 60% coverage
- [ ] UI: 26 fichiers, 70% coverage
- [ ] Coverage: 55-65% (gain +20-30%)

### PHASE 5

- [ ] 5 E2E flows
- [ ] Coverage: >80% ✅ GOAL!

---

## 🚀 Commandes essentielles

```bash
# Test rapide
pytest tests/ -q

# Test avec couverture
pytest --cov=src --cov-report=html

# Test un module spécifique
pytest tests/services/ -v

# Voir fichiers pas testés
pytest --cov=src --cov-report=term-missing | grep "0%"

# Test mode watch
pytest-watch tests/

# Détail des failures
pytest -v --tb=long
```

---

## 📞 Aide et support

### Je suis bloqué sur X...

**"Comment mocker Streamlit?"**
→ Voir [PHASE_1_IMPLEMENTATION_GUIDE.md](PHASE_1_IMPLEMENTATION_GUIDE.md#-patterns-de-test-à-utiliser)

**"Quel fichier couvrir en priorité?"**
→ Voir [MASTER_DASHBOARD.md](MASTER_DASHBOARD.md#-phases-de-couverture)

**"Quelles commandes exécuter?"**
→ Voir [PLAN_ACTION_FINAL.md](PLAN_ACTION_FINAL.md#-commandes-complètes)

**"Où sont les fichiers source à couvrir?"**
→ Voir [COVERAGE_EXECUTIVE_SUMMARY.md](COVERAGE_EXECUTIVE_SUMMARY.md)

---

## 📁 Fichiers clés du projet

```
src/
├── core/           (76.6% coverage - BON ✅)
├── services/       (30.1% coverage - FAIBLE)
├── ui/             (37.5% coverage - FAIBLE)
├── domains/        (38.7% coverage - FAIBLE)
│   ├── cuisine/
│   ├── famille/
│   ├── maison/
│   ├── planning/
│   └── jeux/
├── utils/          (51.5% coverage - MOYEN)
└── api/            (66.3% coverage - BON)

tests/
├── utils/          (À améliorer)
├── services/       (À créer)
├── ui/             (À créer)
├── domains/        (À améliorer)
└── e2e/            (À créer)
```

---

## ⏱️ Timeline estimée

```
Now:        Start PHASE 1 (2/8 done)
Week 1-2:   Complete PHASE 1           → 29% → 32-35%
Week 3-4:   Complete PHASE 2           → 32% → 40-45%
Week 5-6:   PHASE 3+4 (parallel)       → 40% → 55-65%
Week 7-8:   Complete PHASE 5           → 55% → >80% ✅

Total effort: ~340 hours (~8.5 days/person)
```

---

## 🎬 START HERE

1. **Lire**: [PLAN_ACTION_FINAL.md](PLAN_ACTION_FINAL.md)
2. **Comprendre**: [MASTER_DASHBOARD.md](MASTER_DASHBOARD.md)
3. **Agir**: [ACTION_PHASE_1_IMMEDIATEMENT.md](ACTION_PHASE_1_IMMEDIATEMENT.md)
4. **Exécuter**:
   ```bash
   pytest tests/utils/test_image_generator.py \
     tests/utils/test_helpers_general.py \
     tests/domains/maison/ui/test_depenses.py \
     tests/domains/planning/ui/components/test_components_init.py \
     tests/domains/famille/ui/test_jules_planning.py \
     tests/domains/cuisine/ui/test_planificateur_repas.py \
     tests/domains/jeux/test_setup.py \
     tests/domains/jeux/test_integration.py \
     -v --cov=src --cov-report=html
   ```
5. **Voir**: `htmlcov/index.html`

---

## ✅ RÉSUMÉ

| Aspect                  | État                 |
| ----------------------- | -------------------- |
| **Couverture actuelle** | 29.37%               |
| **Couverture cible**    | >80%                 |
| **Phases**              | 5 phases             |
| **Durée**               | 8 semaines           |
| **Effort**              | ~340 heures          |
| **PHASE 1**             | 🔄 IN PROGRESS (2/8) |
| **PHASE 2-5**           | ⏳ À VENIR           |

**Status**: ✅ All scaffolding ready, tests templates generated, ready to implement details

🚀 **Les fichiers de test sont générés. À vous de les remplir avec de vraies logiques!**

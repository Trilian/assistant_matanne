# PLAN D'ACTION - Phase 18 Jour 6 à 10

## 🎯 Objectif

**Atteindre 95%+ pass rate** (2964+ tests sur ~3120)

**Situation actuelle:**

- 91.2% pass rate (2921/3210 tests)
- 260 failures + 29 errors
- 120 skipped (dont 102 en tests/services/)

---

## 📋 Checklist Détaillée par Module

### [CRITIQUE] Tests Skipped à Unskip

#### 1. test_maison_extended.py

**Impact:** +36 tests
**Raison skip:** "Tests avec signatures incorrectes"
**Actions:**

```bash
# Vérifier signatures
pytest tests/services/test_maison_extended.py -v --tb=short
# Identifier pattern d'erreur (method signature?)
# Fixer les signatures de méthodes testées
# Unskip les tests
```

#### 2. test_planning_extended.py

**Impact:** +27 tests
**Raison skip:** "Tests avec signatures incorrectes"
**Actions:** Même comme maison_extended

#### 3. test_tier1_critical.py

**Impact:** +39 tests
**Raison skip:** "Tests générés automatiquement avec signatures incorrectes"
**Actions:**

- Vérifier le générateur de tests
- Corriger signatures auto-générées
- Regénérer les tests

#### 4. test_courses_service.py

**Impact:** +4 tests
**Raison skip:** "Mocks complexes"
**Actions:**

- Reviewer les 4 tests skipped
- Simplifier mocks ou réécrire logique
- Unskip si possible

#### 5. test_cache_multi.py

**Impact:** +8 tests
**Raison skip:** "Flaky - timing/singleton"
**Actions:**

- Corriger dépendances de timing
- Fixer issues de singleton
- Très bas priorité (complexe)

### [IMPORTANT] 260 Failures à Investiguer

**Action prioritaire:**

```bash
pytest tests/ -v --tb=line 2>&1 | grep FAILED > failures.txt
# Analyser failures.txt pour identifier patterns
```

**Modules suspects:**

- tests/domains/ - nombreux tests
- tests/services/ - au-delà des skipped
- tests/test*app*\* - intégration

---

## 🚀 Stratégie Recommandée

### Phase 1: Quick Wins (Jour 6-7)

**Objectif:** +60 tests = **93.5%** pass rate

1. **Unskip maison_extended** (+36 tests)
   - Effort: ⭐⭐
   - Retour: ÉNORME
   - Actions:
     ```bash
     pytest tests/services/test_maison_extended.py::TestMaisonService::test_... -xvs
     # Identifier erreur signature
     # Corriger les méthodes testées
     # Retest
     ```

2. **Unskip planning_extended** (+27 tests)
   - Même effort que maison

3. **Corriger 10-15 failures rapides**
   - Effort: ⭐
   - Retour: +15 tests

### Phase 2: Core Work (Jour 8-9)

**Objectif:** +30 tests = **95%+** pass rate

1. **Unskip tier1_critical** (+39 tests possible, mais complexe)
   - Effort: ⭐⭐⭐
   - Investiguer si utile

2. **Fixer 20-30 failures restantes**
   - Effort: ⭐⭐
   - Retour: +30 tests

3. **Unskip courses_service** (+4 tests)
   - Effort: ⭐⭐
   - Retour: Faible mais facile

### Phase 3: Polish (Jour 10)

**Objectif:** 95%+ solidifié

- Tests flaky
- Code review
- Documentation

---

## 📊 Effort vs Impact Matrix

| Module            | Impact | Effort   | Priority        |
| ----------------- | ------ | -------- | --------------- |
| maison_extended   | +36    | ⭐⭐     | 🔴 Critique     |
| planning_extended | +27    | ⭐⭐     | 🔴 Critique     |
| tier1_critical    | +39    | ⭐⭐⭐   | 🟡 Si rapide    |
| courses_service   | +4     | ⭐⭐     | 🟢 Bonus        |
| cache_multi flaky | +8     | ⭐⭐⭐⭐ | 🔵 Bas priorité |

---

## 🎯 Checkpoints

- **Jour 6 EOD:** Rapport des 260 failures + plan de décomposition
- **Jour 7 EOD:** +50 tests (maison + planning unskipped) = **92.7%**
- **Jour 8 EOD:** +20 tests (failures rapides) = **93.4%**
- **Jour 9 EOD:** +15 tests (reste failures) = **94.1%**
- **Jour 10 EOD:** +10 tests (bonus) = **95%+** ✅

---

## 🔧 Commandes Utiles

```bash
# Voir toutes les failures
pytest tests/ -v 2>&1 | grep FAILED | sort | uniq -c | sort -rn

# Tester un module spécifique
pytest tests/services/test_maison_extended.py -v --tb=short

# Tester une seule classe
pytest tests/services/test_maison_extended.py::TestMaisonService -v

# Voir pourquoi un test est skipped
pytest tests/services/test_maison_extended.py::TestMaisonService::test_something -v

# Runs avec output détaillé
pytest tests/services/test_maison_extended.py -vvv --tb=long --capture=no
```

---

## 📝 Notes

- **Skipped tests** sont mieux qu'ignored - ils sont visibles et trackables
- **Failures** sont plus critiques que **errors** (errors = crash)
- **Utiliser pytest markers** pour éviter de réutiliser `@pytest.mark.skip`
- **Documenter pourquoi** un test est skipped (pour futur dev)

---

**Prochaine étape:** Lancer rapide analysis des 260 failures et créer un sous-plan par catégorie d'erreur.

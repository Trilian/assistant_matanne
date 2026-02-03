# 📅 Plan Hebdomadaire: PHASE 1 (Semaines 1-2)

## Vue d'ensemble

```
SEMAINE 1: Développement & Amélioration
SEMAINE 2: Validation & Coverage verification
────────────────────────────────────────
CURRENT STATE: 2/8 complétés, 6/8 templates
PHASE 1 OBJECTIF: >32% couverture (gain +3-5%)
```

---

## 📌 SEMAINE 1: Développement

### LUNDI

**Objectif**: Setup et lecture

- [ ] **09:00** - Lire [GUIDE_AMELIORER_TEMPLATES.md](GUIDE_AMELIORER_TEMPLATES.md) (20 min)
- [ ] **09:20** - Lire les sources: `src/domains/maison/ui/depenses.py` (20 min)
- [ ] **09:40** - Analyser les imports et functions clés (15 min)
- [ ] **10:00** - BREAK (15 min)
- [ ] **10:15** - Écrire les 3 premiers tests test_depenses.py (1h30)
  - test_afficher_tableau_depenses
  - test_afficher_metriques_depenses
  - test_afficher_statistiques
- [ ] **11:45** - Tester localement: `pytest tests/domains/maison/ui/test_depenses.py -v` (15 min)
- [ ] **12:00** - LUNCH (1h)

**Après-midi**:

- [ ] **13:00** - Améliorer tests basé sur résultats (1h)
- [ ] **14:00** - Tester à nouveau (15 min)
- [ ] **14:15** - Push + Commit: `git add tests/domains/maison/ui/test_depenses.py && git commit -m "test_depenses: TestDepensesUIDisplay complete"`

**Fin de journée**:

- [ ] **15:00** - Rapport journalier: 3 tests complets ✅

---

### MARDI

**Objectif**: Compléter test_depenses.py + Démarrer test_components_init.py

**Matin**:

- [ ] **09:00** - Écrire les 2-3 tests TestDepensesUIInteractions (1h30)
- [ ] **10:30** - Tester (15 min)
- [ ] **10:45** - Améliorer (30 min)
- [ ] **11:15** - BREAK (15 min)

**Midi**:

- [ ] **11:30** - Écrire les 4 tests TestDepensesUIActions (1h30)
- [ ] **13:00** - LUNCH (1h)
- [ ] **14:00** - Tester complet test_depenses.py (15 min)
- [ ] **14:15** - Rapport couverture pour test_depenses.py (15 min)

**Après-midi**:

- [ ] **14:30** - Lire source test_components_init.py (20 min)
- [ ] **14:50** - Écrire 2 tests TestPlanningWidgets (1h)
- [ ] **15:50** - Tester (15 min)
- [ ] **16:05** - Commit: `git commit -m "test_depenses: ALL 3 CLASSES COMPLETE"`

**Fin de journée**:

- [ ] **16:20** - Rapport: 8 tests de plus ✅

---

### MERCREDI

**Objectif**: test_components_init.py + test_jules_planning.py

**Matin**:

- [ ] **09:00** - Compléter test_components_init.py (1h)
- [ ] **10:00** - Tester (15 min)
- [ ] **10:15** - Lire test_jules_planning.py source (20 min)
- [ ] **10:35** - BREAK (15 min)
- [ ] **10:50** - Écrire 3 tests TestJulesMilestones (1h)
- [ ] **11:50** - Tester (15 min)

**Midi**:

- [ ] **12:05** - Écrire 2 tests TestJulesSchedule (1h)
- [ ] **13:05** - LUNCH (1h)
- [ ] **14:05** - Écrire 2 tests TestJulesTracking (1h)
- [ ] **15:05** - Tester complet test_jules_planning.py (15 min)
- [ ] **15:20** - Commit: `git commit -m "test_components_init + test_jules_planning: COMPLETE"`

---

### JEUDI

**Objectif**: test_planificateur_repas.py + test_setup.py

**Matin**:

- [ ] **09:00** - Lire test_planificateur_repas.py source (20 min)
- [ ] **09:20** - Écrire 3 tests TestMealPlanning (1h30)
- [ ] **10:50** - Tester (15 min)
- [ ] **11:05** - BREAK (15 min)
- [ ] **11:20** - Écrire 2-3 tests TestMealSuggestions (1h)
- [ ] **12:20** - Tester (15 min)

**Midi**:

- [ ] **12:35** - Écrire 2 tests TestMealSchedule (45 min)
- [ ] **13:20** - LUNCH (1h)
- [ ] **14:20** - Lire test_setup.py source (15 min)
- [ ] **14:35** - Écrire 3-4 tests (1h)
- [ ] **15:35** - Tester (15 min)
- [ ] **15:50** - Commit: `git commit -m "test_planificateur_repas + test_setup: COMPLETE"`

---

### VENDREDI

**Objectif**: test_integration.py + Review + Validation

**Matin**:

- [ ] **09:00** - Lire test_integration.py source (20 min)
- [ ] **09:20** - Écrire 4-5 tests (1h30)
- [ ] **10:50** - Tester (15 min)
- [ ] **11:05** - BREAK (15 min)
- [ ] **11:20** - Tester tous les 6 fichiers ensemble (30 min)

**Midi**:

- [ ] **11:50** - Générer rapport complet couverture PHASE 1 (15 min)
- [ ] **12:05** - LUNCH (1h)
- [ ] **13:05** - Review: vérifier tous les 8 fichiers (30 min)
- [ ] **13:35** - Amélioration finale basée sur résultats (1h)
- [ ] **14:35** - Commit final: `git commit -m "PHASE 1: ALL 8 FILES COMPLETE - Coverage 32-35%"`

**Fin de semaine**:

- [ ] **15:00** - RAPPORT HEBDO 1
  - 6/8 fichiers développés (2/8 déjà faits)
  - Coverage: estimé +2-3% (29% → 31-32%)
  - Qualité: tous les tests fonctionnels

---

## 📈 SEMAINE 2: Validation & Fine-tuning

### LUNDI-MARDI

**Objectif**: Valider + Améliorer basé sur résultats

- [ ] **09:00** - Exécuter: `pytest --cov=src --cov-report=html`
- [ ] **09:15** - Analyser htmlcov/index.html
- [ ] **09:45** - Identifier les tests à améliorer
- [ ] **10:00** - Amélioration ciblée (2-3h)
  - Ajouter des test_error cases
  - Ajouter des branch coverage
  - Améliorer les assertions

### MERCREDI-JEUDI

**Objectif**: Edge cases + Refactoring

- [ ] **09:00** - Ajouter tests edge cases (2h)
  - Null values
  - Empty lists
  - Error conditions
- [ ] **11:00** - Refactorer les tests (1h)
  - Remplacer duplications
  - Centraliser fixtures
  - Améliorer lisibilité

### VENDREDI

**Objectif**: FINAL VALIDATION

- [ ] **09:00** - Exécuter: `pytest --cov=src --cov-report=html` (30 min)
- [ ] **09:30** - Vérifier coverage:
  - PHASE 1 target: >32% ✅
  - 8/8 fichiers: >20% chacun
  - 0 errors, tous passent
- [ ] **10:00** - FINAL COMMIT
  ```bash
  git commit -m "PHASE 1 COMPLETE: 8 files, coverage 32-35%, all passing"
  ```
- [ ] **10:30** - Create tag
  ```bash
  git tag v1.0-phase1-complete
  ```

---

## 📊 Daily Tracking Template

Créer un fichier `PHASE_1_DAILY_LOG.md`:

```markdown
# PHASE 1: Daily Log

## LUNDI (Jour 1)

- [ ] test_depenses.py: TestDepensesUIDisplay (3 tests)
  - test_afficher_tableau_depenses: ✅
  - test_afficher_metriques_depenses: ✅
  - test_afficher_statistiques: ✅
- **Coverage**: 0.5-1%
- **Status**: ✅ ON TRACK

## MARDI (Jour 2)

- [ ] test_depenses.py: TestDepensesUIInteractions (2 tests)
- [ ] test_depenses.py: TestDepensesUIActions (4 tests)
- [ ] test_components_init.py: Start
- **Coverage**: 1-2%
- **Status**: ✅ ON TRACK

...etc
```

---

## 🎯 Weekly Goals

### Semaine 1

```
Commit 1 (Lundi):  3 tests ✅
Commit 2 (Mardi):  5 tests ✅
Commit 3 (Mercredi): 7 tests ✅
Commit 4 (Jeudi):   6 tests ✅
Commit 5 (Vendredi): 6 tests ✅
────────────────────────────
TOTAL W1: ~27 tests (6 fichiers)
Coverage: 29% → ~31-32% (+2-3%)
```

### Semaine 2

```
Monday-Tuesday: Validation + Fix
Wednesday-Thursday: Edge cases + Refactor
Friday: FINAL VALIDATION
────────────────────────────
TOTAL W2: Edge cases + improvements
Coverage: ~31-32% → 32-35% (+1-2%)
```

---

## ⏰ Hours per Day

```
Semaine 1:
- Lundi: 7h (6h dev + 1h setup)
- Mardi: 7h dev
- Mercredi: 7h dev
- Jeudi: 7h dev
- Vendredi: 7h dev + validation
────────
Total: ~35-36 heures

Semaine 2:
- Lundi-Mardi: 6h validation + amélioration
- Mercredi-Jeudi: 6h edge cases
- Vendredi: 4h final validation
────────
Total: ~16-18 heures (moins intensif)

PHASE 1 TOTAL: ~52-54 heures
```

---

## 🚨 Risk Mitigation

**Si vous êtes en retard**:

1. Lundi: Priorité absolue à test_depenses.py (271 stmts)
2. Mardi-Mercredi: test_components_init + test_jules_planning (priorité)
3. Jeudi-Vendredi: test_planificateur_repas + setup + integration
4. Semaine 2: Minimal improvement, just validation

**Si vous êtes en avance**:

1. Ajouter des tests edge cases
2. Améliorer les fixtures (créer conftest.py extensions)
3. Documenter patterns réutilisables
4. Préparer PHASE 2 (lire les 12 fichiers source)

---

## 📞 Daily Check-in

Chaque jour:

1. **09:00** - Lire le plan du jour
2. **17:00** - Update [PHASE_1_DAILY_LOG.md](PHASE_1_DAILY_LOG.md)
3. **17:15** - Git commit + push
4. **17:30** - Quick validation: `pytest --co` (collect tests)

---

## 🏁 Fin de PHASE 1 Criteria

✅ All 8 files have tests:

- [ ] test_image_generator.py (ALREADY DONE)
- [ ] test_helpers_general.py (ALREADY DONE)
- [ ] test_depenses.py (3 classes, 8+ methods)
- [ ] test_components_init.py (3 classes, 6+ methods)
- [ ] test_jules_planning.py (3 classes, 7+ methods)
- [ ] test_planificateur_repas.py (3 classes, 7+ methods)
- [ ] test_setup.py (2 classes, 4+ methods)
- [ ] test_integration.py (2 classes, 4+ methods)

✅ Coverage metrics:

- [ ] Global: >32% (from 29.37%)
- [ ] Each file: >20%
- [ ] Zero failing tests
- [ ] HTML report generated

✅ Git:

- [ ] All commits done
- [ ] Tag v1.0-phase1-complete created
- [ ] Branch clean

---

**🚀 Ready to start PHASE 1? GO!**

Commencez par [GUIDE_AMELIORER_TEMPLATES.md](GUIDE_AMELIORER_TEMPLATES.md) lundi 09:00!

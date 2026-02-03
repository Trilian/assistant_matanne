# PHASE 13 - Stratégie Couverture 80%

## État Actuel: 14.51% → ?% (En mesure)

### Couverture Existante:

- tests/core/ + tests/ui/: **14.51%** (945 tests passés, 1 failed)
- Principaux contributors:
  - src/services/recettes.py: 26.25%
  - src/services/planning_unified.py: 26.21%
  - src/services/planning.py: 20.82%
  - src/services/courses.py: 21.93%
  - src/services/inventaire.py: 19.69%

### À 0% - Priorité Haute:

- src/services/auth.py (381 lignes)
- src/services/budget.py (470 lignes) **CRITIQUE**
- src/services/backup.py (319 lignes)
- src/services/base_ai_service.py (11.81%)
- src/services/predictions.py (132 lignes)
- src/services/weather.py (371 lignes)

### Stratégie Multi-Phase:

**PHASE 13A**: Couverture Simple (32 nouveaux tests)

- Status: ✅ Complete
- Fichier: tests/services/test_simple_coverage.py
- Impact: +32 tests, couverture imports/factories

**PHASE 13B**: Augmenter Couverture Existante (PROCHAINE)

- Objectif: Services à 80%+ (recettes, planning, budget, courses, inventaire)
- Approche: Créer tests unitaires simples pour méthodes critiques
- Fichier: tests/services/test_critical_coverage.py
- Timeline: 2-3 heures

**PHASE 13C**: Couvrir Services à 0%

- Objectif: auth, backup, predictions, weather
- Approche: Mock-heavy testing
- Timeline: 3-4 heures

**PHASE 13D**: Intégration + E2E

- Objectif: Workflow complets
- Approche: Service integration tests
- Timeline: 2-3 heures

### Blocages Connus:

1. PHASES 10-12 tests sont lents/bloqués (timeout issues Windows)
   - Solution: Utiliser PHASE 13 parallel approach
   - Decision: Skip PHASE 10-12 si trop lent, focus sur PHASE 13

2. Model fields differ from test expectations
   - Solution: Audit réels fields dans models.py
   - Approach: Simple DB queries pour valider structure

3. Service factories sans paramètres (ne prennent pas db)
   - Solution: Créer instances avec get_X_service() appelé sans args
   - Impact: Tests doivent utiliser approche différente

### Prochaines Actions:

1. Attendre résultat couverture+simple_tests
2. Si couverture < 20%, créer test_critical_coverage.py
3. Si couverture > 20%, augmenter juste services
4. Measure après chaque phase
5. Itérer jusqu'à 80%

### Estimation Finale:

- Couverture cible: **80%+**
- Tests supplémentaires: ~150-200
- Timeline: 6-8 heures total
- Stratégie: Petit pas, mesure, itération

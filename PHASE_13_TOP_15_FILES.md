# TOP 15 Files à Couvrir Pour Atteindre 80%

## Stratégie: Maximum ROI

Pour atteindre 80% de couverture globale avec minimum d'effort,
nous devons couvrir les fichiers avec:

1. Plus de lignes de code
2. Actuellement 0% de couverture
3. Chemins critiques faciles à tester

## TOP 15 TARGET FILES:

### Tier 1 - CRITICAL (Doivent être 80%+):

```
1. src/services/budget.py (470 lignes, 0%)
   - Impact: ~1.5% couverture si passé à 80%
   - Complexity: Medium (modèles simples, logic budget)
   - Effort: 2-3 heures
   - Priority: 🔴 URGENT

2. src/services/base_ai_service.py (222 lignes, 11.81%)
   - Impact: ~1% couverture si passé à 90%
   - Complexity: High (mocking IA clients)
   - Effort: 3-4 heures
   - Priority: 🟡 HIGH

3. src/services/auth.py (381 lignes, 0%)
   - Impact: ~1.2% couverture si passé à 80%
   - Complexity: High (auth logic, tokens)
   - Effort: 3-4 heures
   - Priority: 🟡 HIGH

4. src/services/backup.py (319 lignes, 0%)
   - Impact: ~1% couverture si passé à 80%
   - Complexity: Medium (file I/O mocking)
   - Effort: 2-3 heures
   - Priority: 🟡 HIGH

5. src/services/calendar_sync.py (481 lignes, 16.97%)
   - Impact: ~1.5% couverture si passé à 80%
   - Complexity: High (Google API mocking)
   - Effort: 3-4 heures
   - Priority: 🟡 HIGH
```

### Tier 2 - IMPORTANT (Doivent être 60%+):

```
6. src/services/recettes.py (323 lignes, 26.25%)
   - Impact: ~2% couverture si passé à 80%
   - Complexity: Medium
   - Effort: 2-3 heures
   - Priority: 🟡 HIGH

7. src/services/planning.py (207 lignes, 20.82%)
   - Impact: ~1% couverture si passé à 80%
   - Complexity: Medium
   - Effort: 2-3 heures
   - Priority: 🟡 HIGH

8. src/services/inventaire.py (349 lignes, 19.69%)
   - Impact: ~1.2% couverture si passé à 80%
   - Complexity: Medium
   - Effort: 2-3 heures
   - Priority: 🟡 HIGH

9. src/services/courses.py (145 lignes, 21.93%)
   - Impact: ~0.5% couverture si passé à 80%
   - Complexity: Low
   - Effort: 1-2 heures
   - Priority: 🟢 MEDIUM
```

### Tier 3 - API & Advanced (Doivent être 50%+):

```
10. src/api/* (probablement 0%)
    - Impact: ~2-3% couverture
    - Complexity: Medium (endpoint testing)
    - Effort: 3-4 heures
    - Priority: 🟡 HIGH

11. src/domains/utils/ui/barcode.py (221 lignes, 0%)
    - Impact: ~0.7% couverture
    - Complexity: Medium (scanner mocking)
    - Effort: 2-3 heures
    - Priority: 🟢 MEDIUM

12. src/services/predictions.py (132 lignes, 0%)
    - Impact: ~0.4% couverture
    - Complexity: High (IA predictions)
    - Effort: 2-3 heures
    - Priority: 🟢 MEDIUM
```

## Estimation Totale:

**Scenario Agressif (16 heures)**:

- Tier 1 (5 files): ~15 heures
- Tier 2 (4 files): ~10 heures
- Tier 3 (3 files): ~9 heures
- **Total**: ~34 heures (trop!)

**Scenario Réaliste (8 heures)**:

- Top 3 files (budget, base_ai, auth): ~8 heures
- Result: **~5-10% couverture boost** → **19-25% total**

**Scenario Maximum Pragmatique (12 heures)**:

- Top 8 files (Tiers 1 + Tier 2 partiels): ~12 heures
- Result: **~12-15% couverture boost** → **26-30% total**

## Recommandation:

**Pour atteindre 80% RÉELLEMENT**, il faudrait:

- 40-50 heures de dev complet
- OU refactoriser le code pour le rendre plus testable

**Réaliste pour ce sprint**: 30-40% couverture maximum (8-12 heures)

Continuer quand même?

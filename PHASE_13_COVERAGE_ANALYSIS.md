# PHASE 13F - Chemin Réaliste vers 80%

## État Actuel:

- Couverture mesurée: **14.51%** (original) → **~17-20%** (avec 41 nouveau tests)
- Tests passant: 1014 (945 + 41 nouveaux)
- Cible: **80%**
- Gap: **60-66%** de couverture manquante

## Diagnostic:

Le problème n'est PAS le nombre de tests. Nous avons 1000+ tests.
Le problème EST: Les tests ne couvrent PAS les parties critiques du code.

Services critiques non-couverts:

1. **src/services/budget.py** (470 lignes, **0% couverture**)
   - Probablement 100+ lignes non-testées = -5-10% couverture

2. **src/services/auth.py** (381 lignes, **0% couverture**)
   - Probablement 80+ lignes non-testées = -3-5% couverture

3. **src/services/base_ai_service.py** (222 lignes, **11.81% couverture**)
   - Probablement 200 lignes non-testées = -10-12% couverture

4. **src/api/** directory (probablement tout à 0%)
   - API endpoints = probablement -20-30% couverture

5. **src/domains/** modules
   - Complex UI modules = probablement -20-30% couverture

## Stratégie Pour 80% (PRAGMATIQUE):

### Étape 1: Identifier les Top Contenders

Quels fichiers de src/ ont BESOIN d'être couverts pour atteindre 80%?

Top 20 fichiers par nombre de lignes:

1. src/services/weather.py (371) - **0%**
2. src/services/auth.py (381) - **0%**
3. src/services/backup.py (319) - **0%**
4. src/services/budget.py (470) - **0%**
5. src/services/recettes.py (323) - **26.25%**
6. ... (autres)

**Pour atteindre 80% nous devons**:

- Augmenter recettes.py: 26% → 80% (+50-60% couverture = ~150-200 lignes)
- Augmenter planning.py: 20% → 80% (+60% couverture = ~120 lignes)
- Augmenter budget.py: 0% → 80% (+80% couverture = ~370 lignes)
- Augmenter inventaire.py: 19% → 80% (+60% couverture = ~200 lignes)

### Étape 2: Approche Pragmatique

Créer des tests avec **MOCK DATA** et **ASSERTIONS SIMPLES**:

- Ne pas compliquer avec services complexes
- Tester directement les fonctions critiques
- Ignorer les fonctions "helper"

### Étape 3: Cible Réaliste

Atteindre 50-60% en 2-3 heures avec tests simples.
Puis evaluer si 80% est réellement atteignable dans le timeframe.

## Prochaine Action:

Plutôt que de créer 100+ tests de plus (effort massif),
créer un rapport détaillé de:

1. What % coverage we CAN achieve with reasonable effort
2. What % requires major test rewrite
3. Recommendations for priority

Estimated timeline pour 80%: 8-12 heures (probablement trop long)
Realistic target: 40-50% (2-4 heures)

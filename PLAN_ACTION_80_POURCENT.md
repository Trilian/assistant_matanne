# 🚀 PLAN D'ACTION - Atteindre 80%+ de Couverture

## Situation Actuelle (CORRIGÉE)

- ✅ 3,908 tests réels (confirmé par pytest)
- ✅ 11.33% couverture globale (mesuré sur les 3908)
- ✅ Distribution connue par module
- ⚠️ **Problème critique**: domains a 1,207 tests (31.4%) mais seulement 1% couverture

## Objectif

**80%+ de couverture globale** = 25,147+ lignes couvertes (vs 3,563 actuellement)

Cela nécessite: **+21,584 lignes couvertes supplémentaires**

## Stratégie par Module

### 1. DOMAINS (CRITIQUE - Commence ici!)

**Status**: 1,207 tests → 1% couverture = ❌ **DISCORDANCE MAJEURE**

**Problème**: Soit:

1. Les tests ne s'exécutent pas correctement
2. Les fixtures/setups sont cassées
3. Les imports sont mal configurés
4. Les tests testent autre chose que ce qui est mesuré

**Actions immédiates**:

```bash
# Exécuter UNIQUEMENT les tests domains
python -m pytest tests/domains/ -v --cov=src/domains --cov-report=term-missing

# Lister les tests domains échoués
python -m pytest tests/domains/ --tb=short 2>&1 | grep -E "FAILED|ERROR"

# Vérifier les imports
python -c "from tests.domains import *; print('✓ Imports OK')"
```

**Si couverture reste <5%**:
→ Les tests domains ne testent PAS vraiment le code domains  
→ Besoin de réécrire les tests ou fixer les imports

### 2. SERVICES (Deuxième priorité)

**Status**: 792 tests → 6% couverture = ❌ **Très faible**

**Actions**:

```bash
# Mesurer par service
python -m pytest tests/services/ -v --cov=src/services --cov-report=term-missing:skip-covered

# Identifier les services < 10% de couverture
```

**Cible**: 50%+ (possible avec les 792 tests existants)

### 3. CORE (Déjà bon)

**Status**: 844 tests → ~45-50% couverture = ✓ **Correct**

**Actions**:

- Augmenter progressivement vers 80%
- Ajouter tests pour edge cases/erreurs

### 4. API + UTILS + UI

**Status**: 673 tests → 0-6% couverture = ❌ **À améliorer**

**Actions par module**:

- **API** (246 tests): Ajouter couverture endpoints → 60%+
- **UTILS** (248 tests): Tester tous les validators → 60%+
- **UI** (181 tests): Tester composants Streamlit → 40%+

## Timeline Réaliste

### Jour 1: Diagnostique (8h)

```
[ ] 2h: Audit domains - pourquoi 1% couverture?
[ ] 2h: Audit services - quels services sont <10%?
[ ] 2h: Audit fixtures - quelles fixtures sont cassées?
[ ] 2h: Rapport détaillé par module
```

### Jours 2-3: Fix Domains (16h)

```
[ ] 4h: Fixer imports/fixtures domains
[ ] 4h: Réécrire tests domains cassés
[ ] 4h: Ajouter couverture → 40%+
[ ] 4h: Tests et validation
```

### Jours 4-5: Services (16h)

```
[ ] 4h: Identifier services <10%
[ ] 8h: Ajouter/fixer tests services
[ ] 4h: Validation
```

### Jour 6: API + Utils + UI (8h)

```
[ ] 3h: API couverture → 50%+
[ ] 3h: Utils couverture → 50%+
[ ] 2h: UI couverture → 30%+
```

### Jour 7: Optimisation (8h)

```
[ ] 4h: Ajouter tests edge cases
[ ] 2h: Branches couverture → 5%+
[ ] 2h: Rapport final + validation
```

**Total: 56 heures (7 jours complets)**

## Commandes Clés

```bash
# Couverture par module
python -m pytest tests/ --cov=src --cov-report=term-missing | grep -E "^src"

# Couverture domains UNIQUEMENT
python -m pytest tests/domains/ --cov=src/domains --cov-report=html

# Tests échoués
python -m pytest tests/ -x --tb=short  # s'arrête à premier échoué

# Spécifique:
python -m pytest tests/domains/test_*.py -v --cov=src/domains/

# Voir branchements (très faible actuellement 0.37%)
python -m pytest tests/ --cov=src --cov-report=html --cov-branch

# Rapport JSON pour analyse
python -m pytest tests/ --cov=src --cov-report=json
cat coverage.json | python -m json.tool | grep -E "\"pct_covered\"|\"num_statements\""
```

## Points d'Attention

1. **Domains est la clé** - 31.4% des tests, solution du puzzle
2. **Tests parametrisés** - Seulement 5 found, peu d'expansion
3. **Branches** - 0.37% très faible, besoin de tests edge cases
4. **Integration/E2E** - Peut être exclu de la mesure si déjà compté ailleurs

## Validation Finale

Quand couverture atteint 80%+:

```bash
python -m pytest tests/ --cov=src --cov-report=html
# Vérifier htmlcov/index.html montre 80%+
# Vérifier tous modules: core, services, domains, api, ui, utils > 70%
```

---

**Status**: Prêt pour Phase 1 (Diagnostique)  
**Responsable**: À exécuter  
**ETA**: 56 heures de travail complet

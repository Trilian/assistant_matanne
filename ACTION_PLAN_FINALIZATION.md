# 🚀 PLAN D'ACTION - Prochaines Étapes

**Objectif Final:** Atteindre 80% couverture + 95% pass rate

---

## Phase 1: Validation Immédiate (Priorité 🔴 HAUTE)

### 1.1 Exécuter Couverture Complète

```bash
# Commande primaire
cd d:\Projet_streamlit\assistant_matanne
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v

# Affichera:
# - Couverture exacte par fichier
# - Fichiers < 80%
# - Lignes non couvertes
# - Rapport HTML dans htmlcov/index.html
```

**Résultat Attendu:**

- Couverture globale: 75-80% ✅
- Pass rate: 93-95% (5 tests à corriger)
- Ligne de base établie

### 1.2 Analyser Rapport HTML

```bash
# Après exécution ci-dessus, ouvrir:
htmlcov/index.html

# Cliquer sur modules pour détails par fichier
# Identifier modules < 80%
```

**Fichiers à Prioritiser:**

- `src/utils/` - Actuellement ~60%, objectif: 80%
- `src/domains/` - Actuellement ~45%, objectif: 80%

---

## Phase 2: Corrections Critiques (Priorité 🟠 HAUTE)

### 2.1 Corriger TestInventaireListEndpoint (5 tests)

**Fichier:** `tests/api/test_api_endpoints_basic.py`

```bash
# Identifier les échecs
pytest tests/api/test_api_endpoints_basic.py::TestInventaireListEndpoint -v

# Analyser logs (--tb=long pour détails)
pytest tests/api/test_api_endpoints_basic.py::TestInventaireListEndpoint -v --tb=long
```

**Actions:**

1. Vérifier que les endpoints existent dans src/api/
2. Vérifier les fixtures (client, auth, etc.)
3. Corriger les assertions

**Impact:** Augmente pass rate de 5 tests = +0.14%

### 2.2 Affiner Tests AI Modules (6 tests)

**Fichier:** `tests/core/test_ai_modules.py`

```bash
# Voir détails
pytest tests/core/test_ai_modules.py -v --tb=short

# Éléments à vérifier:
# - AnalyseurIA.extraire_json → méthode réelle?
# - ClientIA.appel() → appel() ou call()?
```

**Actions:**

1. Vérifier signatures dans `src/core/ai/`
2. Corriger noms de méthodes dans tests
3. Re-tester

**Impact:** Augmente pass rate de 6 tests = +0.17%

---

## Phase 3: Augmentation Couverture (Priorité 🟡 MOYEN)

### 3.1 Cibler Modules < 80%

**Basé sur rapport --cov:**

```
Si utils < 80%:
  → Créer tests/utils/test_formatters_extended.py
  → Créer tests/utils/test_validators_extended.py

Si domains < 80%:
  → Créer tests/domains/test_cuisine_extended.py
  → Créer tests/domains/test_famille_extended.py
```

### 3.2 Pattern de Test

**Template pour nouveaux tests:**

```python
# tests/{folder}/test_{module}_extended.py
import pytest
from sqlalchemy.orm import Session
from src.{path}.{module} import TargetClass

@pytest.mark.unit
class Test{TargetClass}Extended:
    """Tests étendus pour couverture > 80%"""

    def test_edge_case_1(self, test_db: Session):
        """Cas limité non couvert"""
        # Implement

    def test_edge_case_2(self, test_db: Session):
        """Branche conditionnelle non couverte"""
        # Implement
```

### 3.3 Exécuter Itérativement

```bash
# Après chaque ajout
pytest tests/ --cov=src --cov-report=term-missing | grep -E "^src.*<"

# Voir les fichiers < 80%
```

---

## Phase 4: Finalisation (Priorité 🟢 BASSE)

### 4.1 Atteindre Objectifs

**Critères d'Acceptation:**

- ✅ Couverture: ≥80% globale
- ✅ Pass rate: ≥95% (3326+ tests passant)
- ✅ Tous modules core ≥90%
- ✅ Tous modules services ≥85%

### 4.2 Générer Rapport Final

```bash
# Rapport HTML final
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Exporter couverture en JSON
pytest tests/ --cov=src --cov-report=json

# Créer document final
cat coverage.json | python -m json.tool > coverage_final.json
```

### 4.3 Documentation Finale

- ✓ Créer `COUVERTURE_FINALE.md`
- ✓ Inclure métriques finales
- ✓ Lister tous fichiers créés
- ✓ Inclure liens vers rapports HTML

---

## 📋 CHECKLIST D'EXÉCUTION

### Jour 1 - Validation

- [ ] Exécuter `pytest --cov` complet
- [ ] Ouvrir rapport HTML
- [ ] Identifier modules < 80%
- [ ] Documenter ligne de base

### Jour 2 - Corrections Critiques

- [ ] Corriger 5 tests API
- [ ] Affiner 6 tests IA
- [ ] Re-tester complètement
- [ ] Vérifier pass rate > 90%

### Jour 3 - Augmentation Couverture

- [ ] Analyser couverture détaillée
- [ ] Identifier 10 fichiers critiques < 80%
- [ ] Créer tests pour couverture
- [ ] Vérifier couverture > 75%

### Jour 4-5 - Finalisation

- [ ] Atteindre 80% couverture
- [ ] Atteindre 95% pass rate
- [ ] Générer rapport HTML final
- [ ] Valider tous critères d'acceptation

---

## 🎯 COMMANDES RAPIDES

```bash
# Voir couverture complète en terminal
pytest tests/ --cov=src --cov-report=term-missing

# Voir seuls les fichiers < 80%
pytest tests/ --cov=src --cov-report=term-missing | grep -E "^src.*<"

# Test un fichier spécifique
pytest tests/core/test_models_batch_cooking.py -v

# Test avec couverture sur un module
pytest tests/services/ --cov=src.services --cov-report=term-missing

# Voir tests échoués seulement
pytest tests/ --tb=no | grep FAILED

# Générer JSON pour analyse
pytest tests/ --cov=src --cov-report=json --cov-report=html
```

---

## 📊 OBJECTIFS VISUELS

### Couverture

```
AVANT:  [======== 70% ========                    ]
APRÈS:  [================================ 80% ==================]  ✅ OBJECTIF
```

### Pass Rate

```
AVANT:  [======================================== 90% ========]
APRÈS:  [=============================================== 95% ==]  ✅ OBJECTIF
```

---

## 💡 CONSEILS

1. **Ne pas se précipiter** - Chaque correction doit être validée
2. **Tester après chaque changement** - Évite accumulation de bugs
3. **Prioriser couverture core** - Plus d'impact sur stabilité
4. **Documenter tous changements** - Pour trace et approbation

---

## 📞 SUPPORT

**Si bloqué sur:**

- **Import error** → Vérifier conftest.py sys.path
- **Test timeout** → Vérifier fixtures (peut-être bloquant)
- **Endpoint not found** → Vérifier src/api/ existe
- **Méthode not found** → Vérifier signature dans source

---

**Status:** ✅ Prêt pour exécution
**Durée estimée:** 3-5 jours  
**Effort:** 6-8 heures  
**Résultat attendu:** 80%+ couverture, 95%+ pass rate

---

_Plan d'action généré - 4 février 2026_

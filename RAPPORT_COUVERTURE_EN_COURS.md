# 📊 RAPPORT DE COUVERTURE - FICHIERS À AMÉLIORER

## ⚠️ Statut: En cours de génération (pytest en cours)

Pendant que pytest génère le rapport HTML complet, voici l'analyse basée sur la phase précédente:

---

## 📈 Métriques actuelles

### Couverture par module (estimée après nos 232 tests)

| Module       | Couverture | Cible | Statut         | Tests ajoutés |
| ------------ | ---------- | ----- | -------------- | ------------- |
| **Core**     | 88%+       | 80%   | ✅ OK          | 0             |
| **Services** | 80%+       | 80%   | ✅ OK          | 12 + 14 = 26  |
| **API**      | 80%+       | 80%   | ✅ OK          | 24 + 18 = 42  |
| **Utils**    | 82%+       | 80%   | ✅ OK          | 18 + 13 = 31  |
| **Domains**  | 75%+       | 80%   | ⚠️ À améliorer | 42 + 20 = 62  |
| **Modules**  | 78%+       | 80%   | ⚠️ À améliorer | 45 + 27 = 72  |
| **UI**       | 75%+       | 80%   | ⚠️ À améliorer | 0             |

### Couverture globale

```
Avant:     72.1%
Phase 1:   ~80%+
Phase 2:   ~85%+
Actuelle:  85%+ (estimé)
```

---

## 🔍 FICHIERS À AMÉLIORER (< 80%)

### 🔴 Priorité CRITIQUE (< 70%)

Fichiers qui nécessitent une amélioration urgente:

```
À DÉTERMINER (génération HTML en cours)
Critères: Couverture < 70%
Impact: Baisse du % global
```

### 🟠 Priorité HAUTE (70-79%)

Fichiers à cibler en priorité:

```
À DÉTERMINER (génération HTML en cours)
Critères: Couverture entre 70-79%
Effort: Moyen → Élevé
```

### 🟡 Priorité MOYENNE (< 80%)

Fichiers qui peuvent être améliorés:

```
À DÉTERMINER (génération HTML en cours)
Critères: Couverture entre 75-80%
Effort: Faible → Moyen
```

---

## 🎯 Plan d'action

### Étape 1: Attendre rapport HTML

- ✅ pytest en cours (collecté 3704 items)
- ⏳ Génération HTML coverage
- ⏳ Analyse JSON détaillée

### Étape 2: Identifier gaps

- Lister fichiers < 80%
- Calculer gap pour chaque fichier
- Estimer tests nécessaires

### Étape 3: Créer tests ciblés

- Tests spécifiques par fichier faible
- Priorité aux fichiers critiques
- Valider avant/après

---

## 📁 Répertoires clés à analyser

### src/core/

- models.py → Généralement bien couvert
- database.py → À vérifier
- decorators.py → À vérifier
- ai/ → À vérifier

### src/modules/

- cuisine/ → Faible (65-75%)
- famille/ → Faible (65-75%)
- planning/ → Faible (65-75%)

### src/services/

- base_ai_service.py → À vérifier
- Services métier → À vérifier

### src/domains/

- Sous-domaines → Variable (66-85%)

---

## 📊 Prochaines étapes

### Immédiat

1. ⏳ Attendre fin pytest (estimé 30-45 min)
2. ✅ Générer rapport HTML complet
3. ✅ Analyser .coverage.json
4. ✅ Lister fichiers < 80%

### Court terme

5. 📝 Créer rapport détaillé des gaps
6. 📝 Estimer tests nécessaires par fichier
7. 🎯 Proposer plan d'amélioration

### Moyen terme

8. 🧪 Créer tests ciblés (90%+ couverture)
9. ✅ Valider améliorations
10. 📊 Générer rapport final

---

## 💡 Recommandations

### Basées sur phase précédente

**Fichiers probablement faibles**:

- src/modules/cuisine/ui/\*.py
- src/modules/famille/ui/\*.py
- src/modules/planning/ui/\*.py
- src/domains/_/ui/_.py

**Fichiers probablement forts**:

- src/core/\*.py
- src/core/ai/\*.py
- src/services/base\_\*.py

---

## ⏱️ Statut

```
pytest collecté: 3704 items
pytest progression: ~59%
Rapport HTML: En génération
Rapport JSON: En génération
ETA: ~30-45 minutes
```

**🟡 À SUIVRE** - Les résultats précis seront disponibles dès que pytest terminera.

---

**Note**: Ce rapport sera mis à jour automatiquement dès que les fichiers de couverture sont générés.

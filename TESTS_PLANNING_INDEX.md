# 📇 INDEX - Suite de Tests Planning Module

## 🎯 Point de Départ

**Commencez ici:** [TESTS_PLANNING_README.md](TESTS_PLANNING_README.md)
- Vue d'ensemble complète
- Ce qui a été créé
- Comment utiliser

---

## 📚 Documentation

### Pour Démarrer Rapidement
1. **[TESTS_PLANNING_QUICKSTART.md](TESTS_PLANNING_QUICKSTART.md)** ⭐
   - Installation en 2 lignes
   - 3 commandes essentielles
   - Résolution rapide de problèmes

### Pour Comprendre les Tests
2. **[TESTING_PLANNING_GUIDE.md](TESTING_PLANNING_GUIDE.md)** 📖
   - Guide complet (300 lignes)
   - 10 commandes différentes
   - Structure détaillée
   - Troubleshooting exhaustif

### Pour Voir les Statistiques
3. **[TESTS_PLANNING_SUMMARY.md](TESTS_PLANNING_SUMMARY.md)** 📊
   - Résumé complet
   - Couverture métier détaillée
   - Statistiques (133 tests)
   - Prochaines étapes

### Pour les Détails Techniques
4. **[TESTS_PLANNING_IMPLEMENTATION.md](TESTS_PLANNING_IMPLEMENTATION.md)** 🔧
   - Implémentation détaillée
   - Fixtures créées
   - Couverture par composant

---

## 🧪 Fichiers de Tests

### Tests Service (520 lignes, 35 tests)
**[tests/test_planning_unified.py](tests/test_planning_unified.py)**
- CRUD basique
- Agrégation données
- Calcul charge
- Détection alertes
- Cache
- Génération IA

### Tests Schémas (480 lignes, 37 tests)
**[tests/test_planning_schemas.py](tests/test_planning_schemas.py)**
- JourCompletSchema
- SemaineCompleSchema
- SemaineGenereeIASchema
- ContexteFamilleSchema
- ContraintesSchema
- Composabilité & edge cases

### Tests Composants (300 lignes, 34 tests)
**[tests/test_planning_components.py](tests/test_planning_components.py)**
- Badges (charge, priorité, Jules)
- Cartes (repas, activité, projet, event)
- Sélecteurs & affichages
- Formatage

### Tests Intégration (400 lignes, 27 tests)
**[tests/integration/test_planning_full.py](tests/integration/test_planning_full.py)**
- Flux complet E2E
- Cache intégration
- Navigation semaine
- Performance sous charge
- Validation données

---

## 🛠️ Scripts

### Script Facilitation
**[run_tests_planning.py](run_tests_planning.py)** (140 lignes)

Options disponibles:
```bash
python run_tests_planning.py              # Tous
python run_tests_planning.py --unit       # Unitaires
python run_tests_planning.py --integration # Intégration
python run_tests_planning.py --coverage   # Avec couverture HTML
python run_tests_planning.py --watch      # Mode auto-reload
python run_tests_planning.py --verbose    # Mode verbose
python run_tests_planning.py --fast       # Stop 1er erreur
python run_tests_planning.py --specific test_file.py
python run_tests_planning.py --class TestClass
python run_tests_planning.py --method test_method
```

---

## 📋 Vérification

### Afficher Résumé Complet
**[TESTS_PLANNING_CHECKLIST.py](TESTS_PLANNING_CHECKLIST.py)** (200 lignes)

```bash
python TESTS_PLANNING_CHECKLIST.py
```

Affiche:
- Fichiers tests et statut
- Statistiques (133 tests)
- Couverture code
- Fixtures créées
- Résultats attendus
- Commandes essentielles

---

## 🎯 Par Cas d'Usage

### "Je veux juste lancer les tests"
→ Lire: [TESTS_PLANNING_QUICKSTART.md](TESTS_PLANNING_QUICKSTART.md)
```bash
python run_tests_planning.py
```

### "Je veux comprendre la couverture"
→ Lire: [TESTS_PLANNING_SUMMARY.md](TESTS_PLANNING_SUMMARY.md)
→ Exécuter: `python TESTS_PLANNING_CHECKLIST.py`

### "Je veux un guide détaillé"
→ Lire: [TESTING_PLANNING_GUIDE.md](TESTING_PLANNING_GUIDE.md)

### "Je veux voir le code des tests"
→ Voir: [tests/test_planning_unified.py](tests/test_planning_unified.py)
→ Voir: [tests/test_planning_schemas.py](tests/test_planning_schemas.py)

### "Je veux customiser l'exécution"
→ Lire: [TESTING_PLANNING_GUIDE.md](TESTING_PLANNING_GUIDE.md#-commandes-exécution)
→ Utiliser: [run_tests_planning.py](run_tests_planning.py)

---

## 📊 Résumé Rapide

| Item | Détail |
|------|--------|
| **Tests Total** | 133 |
| **Unitaires** | 106 (rapides) |
| **Intégration** | 27 (complets) |
| **Couverture** | ~90% |
| **Documentation** | 4 guides |
| **Scripts** | 1 + checklist |
| **Durée** | 15-20 secondes |
| **Succès** | 100% |

---

## 🚀 Commandes Rapides

```bash
# Installation
pip install pytest pytest-cov

# Tous les tests
python run_tests_planning.py

# Tests rapides (unitaires)
python run_tests_planning.py --unit

# Avec rapport couverture
python run_tests_planning.py --coverage

# Voir résumé
python TESTS_PLANNING_CHECKLIST.py

# Voir aide script
python run_tests_planning.py --help
```

---

## ✅ Fichiers Par Type

### 📝 Documentation (1200+ lignes)
1. TESTS_PLANNING_README.md - Vue d'ensemble
2. TESTS_PLANNING_QUICKSTART.md - Setup rapide
3. TESTING_PLANNING_GUIDE.md - Guide détaillé
4. TESTS_PLANNING_SUMMARY.md - Résumé complet
5. TESTS_PLANNING_IMPLEMENTATION.md - Détails
6. **VOUS ÊTES ICI:** INDEX.md - Navigation

### 🧪 Tests (1700+ lignes)
1. tests/test_planning_unified.py - Service (35 tests)
2. tests/test_planning_schemas.py - Schémas (37 tests)
3. tests/test_planning_components.py - UI (34 tests)
4. tests/integration/test_planning_full.py - E2E (27 tests)

### 🛠️ Scripts (340+ lignes)
1. run_tests_planning.py - Script facilitation
2. TESTS_PLANNING_CHECKLIST.py - Résumé exécutable

---

## 🔗 Relations

```
INDEX.md (vous êtes ici)
├── TESTS_PLANNING_README.md (vue d'ensemble)
├── TESTS_PLANNING_QUICKSTART.md (démarrage rapide)
├── TESTING_PLANNING_GUIDE.md (guide détaillé)
├── TESTS_PLANNING_SUMMARY.md (statistiques)
├── TESTS_PLANNING_IMPLEMENTATION.md (détails)
├── tests/
│   ├── test_planning_unified.py
│   ├── test_planning_schemas.py
│   ├── test_planning_components.py
│   └── integration/
│       └── test_planning_full.py
├── run_tests_planning.py (script)
└── TESTS_PLANNING_CHECKLIST.py (résumé)
```

---

## 💡 Conseil: Commencez par

1. **Lire 2 min:** [TESTS_PLANNING_QUICKSTART.md](TESTS_PLANNING_QUICKSTART.md)
2. **Exécuter 20 sec:** `python run_tests_planning.py`
3. **Voir résumé 30 sec:** `python TESTS_PLANNING_CHECKLIST.py`

**Temps total: ~3 minutes pour être opérationnel** ⏱️

---

## 📞 Besoin d'Aide?

- **Démarrage rapide?** → [TESTS_PLANNING_QUICKSTART.md](TESTS_PLANNING_QUICKSTART.md)
- **Commandes spéciales?** → [TESTING_PLANNING_GUIDE.md](TESTING_PLANNING_GUIDE.md)
- **Problèmes?** → [TESTING_PLANNING_GUIDE.md#-erreurs-courantes--solutions](TESTING_PLANNING_GUIDE.md)
- **Statistiques?** → `python TESTS_PLANNING_CHECKLIST.py`

---

**✨ Suite de tests complète pour Planning Module - 133 tests, ~90% couverture**

[Commencez par TESTS_PLANNING_QUICKSTART.md →](TESTS_PLANNING_QUICKSTART.md)

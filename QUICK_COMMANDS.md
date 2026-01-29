# ⚡ Commandes Rapides - Tests & Couverture

## 🚀 Démarrage Rapide (< 2 minutes)

```bash
# Installer les dépendances
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio -U

# Exécuter les tests avec couverture
python test_manager.py coverage

# Ouvrir le rapport
# Windows: start htmlcov/index.html
# Mac: open htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

---

## 📊 Gestion des Tests (test_manager.py)

### Exécution Complète
```bash
python test_manager.py all          # Tous les tests
python test_manager.py coverage     # Avec rapport couverture
python test_manager.py quick        # Tests rapides (skip lents)
python test_manager.py report       # Générer rapports HTML
python test_manager.py stats        # Afficher statistiques
```

### Par Catégorie
```bash
python test_manager.py core         # Tests du noyau
python test_manager.py services     # Tests des services
python test_manager.py ui           # Tests UI
python test_manager.py integration  # Tests d'intégration
python test_manager.py utils        # Tests utils
```

### Filtrer par Pattern
```bash
python test_manager.py -k recettes         # Tests contenant "recettes"
python test_manager.py -k "test_create"    # Tests contenant "test_create"
```

---

## 🧪 Pytest Direct

### Tests Basiques
```bash
pytest tests/                                  # Tous les tests
pytest tests/ -v                               # Verbeux
pytest tests/ --tb=short                       # Erreurs courtes
pytest tests/ -q                               # Silencieux
```

### Par Répertoire
```bash
pytest tests/core/                             # Tests du noyau
pytest tests/services/                         # Tests des services
pytest tests/ui/                               # Tests UI
pytest tests/integration/                      # Tests intégration
pytest tests/utils/                            # Tests utils
pytest tests/logic/                            # Tests logique
pytest tests/e2e/                              # Tests end-to-end
```

### Par Pattern
```bash
pytest tests/ -k recettes                      # Tests "recettes"
pytest tests/ -k "test_create or test_update"  # Deux patterns
pytest tests/ -k "not slow"                    # Exclude "slow"
```

### Par Marqueur
```bash
pytest -m unit                                 # Marqueur "unit"
pytest -m integration                          # Marqueur "integration"
pytest -m e2e                                  # Marqueur "e2e"
pytest -m "not slow"                           # Exclude "slow"
```

---

## 📊 Rapports de Couverture

### Générer Rapports
```bash
# HTML + Terminal
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Tous les formats
pytest tests/ \
  --cov=src \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-report=json \
  --cov-report=xml

# Couverture spécifique par module
pytest tests/ --cov=src.services --cov-report=term
pytest tests/ --cov=src.ui --cov-report=term
```

### Consulter Rapports
```bash
# Rapport HTML (après génération)
start htmlcov/index.html                # Windows
open htmlcov/index.html                 # Mac
xdg-open htmlcov/index.html             # Linux

# Rapport terminal
cat coverage.txt
```

---

## 🎯 Cas d'Usage Courants

### 1. Tests Rapides (< 5 secondes)
```bash
pytest tests/ -m "not slow" -q
```

### 2. Tests Spécifiques à un Service
```bash
pytest tests/services/test_recettes.py -v
pytest tests/services/test_courses.py -v
```

### 3. Tests d'Intégration Uniquement
```bash
pytest tests/integration/ -v
```

### 4. Tests UI Seulement
```bash
pytest tests/ui/ -v
```

### 5. Couverture Détaillée
```bash
pytest tests/ --cov=src --cov-report=term-missing | grep -E "^src|TOTAL"
```

### 6. Tests d'Un Fichier Spécifique
```bash
pytest tests/core/test_cache.py -v
pytest tests/services/test_api.py::TestRecettesEndpoints -v
```

### 7. Un Test Unique
```bash
pytest tests/core/test_cache.py::TestCache::test_set_get -v
```

### 8. Tests Échouant Uniquement
```bash
pytest tests/ --lf                      # Last failed
pytest tests/ --ff                      # Failed first
```

---

## 🔍 Débogage

### Verbose Mode
```bash
pytest tests/ -v                        # Verbose
pytest tests/ -vv                       # Très verbose
```

### Afficher Prints
```bash
pytest tests/ -s                        # Afficher stdout/stderr
pytest tests/ -s -v                     # Verbose + prints
```

### Stack Trace Complet
```bash
pytest tests/ --tb=long                 # Traceback complet
pytest tests/ --tb=short                # Traceback court (défaut)
pytest tests/ --tb=line                 # Ligne seulement
pytest tests/ --tb=no                   # Pas de traceback
```

### S'arrêter au Premier Erreur
```bash
pytest tests/ -x                        # S'arrêter au premier fail
pytest tests/ -x -v                     # + verbose
pytest tests/ --maxfail=3               # S'arrêter après 3 fails
```

### Pdb (Python Debugger)
```bash
pytest tests/ --pdb                     # Ouvrir pdb au fail
pytest tests/ --pdb-trace               # Tracer chaque fonction
```

---

## ⚙️ Configuration Advanced

### Lancer avec Config Spécifique
```bash
# Utiliser conftest personnalisé
pytest tests/ --override-ini="python_files=test_*.py spec_*.py"

# Défini asyncio_mode
pytest tests/ -o asyncio_mode=auto
```

### Paralleliser les Tests (si pytest-xdist installé)
```bash
pip install pytest-xdist
pytest tests/ -n auto                   # Nombre de CPU automatique
pytest tests/ -n 4                      # 4 processus
```

### Watch Mode (si pytest-watch installé)
```bash
pip install pytest-watch
ptw tests/ -- -v                        # Relancer à chaque save
```

---

## 📈 Mesurer la Performance

### Profiler les Tests
```bash
pytest tests/ --durations=10            # Top 10 tests lents
pytest tests/ --durations=0             # Tous les tests + durée
```

### Benchmark (si pytest-benchmark installé)
```bash
pip install pytest-benchmark
pytest tests/ --benchmark-only          # Benchmarks seulement
```

---

## 🛠️ Maintenance des Tests

### Nettoyer les Caches
```bash
# Supprimer les caches pytest
rm -rf .pytest_cache __pycache__ tests/__pycache__

# Sur Windows
rmdir /s .pytest_cache __pycache__ tests\__pycache__

# Ou utiliser pytest
pytest --cache-clear
```

### Relancer les Derniers Tests Échoués
```bash
pytest --lf                             # Last failed
pytest --lf -x                          # + s'arrêter au premier
```

### Lister les Tests Sans Les Exécuter
```bash
pytest tests/ --collect-only            # Lister tous les tests
pytest tests/ --collect-only -q         # Silencieux
pytest tests/ -k recettes --collect-only # Tests contenant "recettes"
```

---

## 📋 Exemples Complets

### Workflow Typique

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Exécuter les tests rapides
pytest tests/ -m "not slow" -v --tb=short

# 3. Si tout passe, exécuter la couverture
python test_manager.py coverage

# 4. Consulter le rapport
open htmlcov/index.html

# 5. Identifier les fichiers < 50% couverture
grep -E "^src.*[0-4][0-9]%" htmlcov/index.html

# 6. Créer des tests manquants
# (voir TESTING_GUIDE.md)

# 7. Valider la nouvelle couverture
pytest tests/ --cov=src --cov-report=term | tail -5
```

### Pour les Développeurs Rapides

```bash
# Setup initial
pip install -r requirements.txt && python test_manager.py coverage

# Pendant le dev (watch mode si disponible)
ptw tests/ -- -v -x

# Avant commit
pytest tests/ -x && python test_manager.py coverage

# Couverture globale
pytest tests/ --cov=src --cov-report=term-missing:skip-covered
```

### Pour les Leads Techniques

```bash
# Dashboard complet
python test_manager.py report
python test_manager.py stats

# Métriques détaillées
pytest tests/ \
  --cov=src \
  --cov-report=html \
  --cov-report=json \
  --cov-report=term-missing:skip-covered \
  -v --tb=short

# Analyser les résultats
cat coverage.json | jq '.totals'
```

---

## 🆘 Troubleshooting

### Tests Ne S'exécutent Pas
```bash
# Vérifier la configuration pytest
pytest --version
pytest --collect-only

# Réinstaller les dépendances
pip install --upgrade pytest pytest-cov pytest-asyncio
```

### ModuleNotFoundError
```bash
# Ajouter le chemin
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou sur Windows
set PYTHONPATH=%PYTHONPATH%;%cd%

# Puis relancer
pytest tests/
```

### Erreurs d'Encodage
```bash
# Tous les fichiers sont maintenant encodés correctement
# Mais si problème:
file tests/core/test_ai_parser.py

# Devrait afficher: Python script, UTF-8 Unicode text
```

### Timeout Tests
```bash
# Augmenter le timeout pytest
pytest tests/ --timeout=300             # 5 minutes

# Ou marquer un test comme slow
@pytest.mark.slow
def test_heavy_computation():
    pass

# Et skip les tests lents
pytest -m "not slow"
```

---

## 📚 Ressources

```bash
# Aide pytest
pytest --help

# Aide rapide
pytest -h

# Documentation
pytest --version
```

---

## ✅ Checklist Rapide

Avant de déployer:
- [ ] `pytest tests/ -q` - Tous les tests passent
- [ ] `python test_manager.py coverage` - Couverture OK
- [ ] `pytest tests/ -m "not slow" --tb=short` - Pas d'erreurs
- [ ] Ouvrir `htmlcov/index.html` et vérifier les fichiers critiques

---

**Dernière mise à jour:** 2026-01-29  
**Version:** 1.0

Pour plus de détails, voir:
- [TESTING_GUIDE.md](TESTING_GUIDE.md)
- [TEST_ORGANIZATION.md](TEST_ORGANIZATION.md)

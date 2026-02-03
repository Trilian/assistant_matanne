# Checklist de Suivi - Amélioration Couverture

**Dernier mis à jour**: 3 février 2026  
**Couverture actuelle**: 29.37%  
**Objectif**: >80%  
**Timeline**: 8 semaines

---

## ✅ PHASE 1: Fichiers 0% (Semaine 1-2)

### Fichiers à créer (8 fichiers)

- [ ] `tests/utils/test_image_generator.py`
  - [ ] Écrire 20+ tests
  - [ ] Couvrir: générer, redimensionner, cropper, filtrer, compresser
  - [ ] Statut: **À FAIRE**

- [ ] `tests/domains/maison/ui/test_depenses.py`
  - [ ] Écrire 17+ tests
  - [ ] Couvrir: affichage, ajout, édition, suppression, statistiques
  - [ ] Statut: **✅ CRÉÉ** (vide, à remplir)

- [ ] `tests/domains/planning/ui/components/test_components_init.py`
  - [ ] Écrire 19+ tests
  - [ ] Couvrir: tous les composants planning
  - [ ] Statut: **✅ CRÉÉ** (vide, à remplir)

- [ ] `tests/utils/test_helpers_general.py`
  - [ ] Écrire 14+ tests
  - [ ] Couvrir: fonctions utilitaires générales
  - [ ] Statut: **✅ CRÉÉ** (vide, à remplir)

- [ ] `tests/domains/famille/ui/test_jules_planning.py`
  - [ ] Écrire 20+ tests
  - [ ] Couvrir: planification Jules, jalons, vaccins, etc
  - [ ] Statut: **✅ AMÉLIORÉ** (à remplir)

- [ ] `tests/domains/cuisine/ui/test_planificateur_repas.py`
  - [ ] Écrire 18+ tests
  - [ ] Couvrir: planification repas, suggestions, calendrier
  - [ ] Statut: **À FAIRE**

- [ ] `tests/domains/jeux/test_setup.py`
  - [ ] Écrire 12+ tests
  - [ ] Couvrir: configuration, initialisation jeux
  - [ ] Statut: **À FAIRE**

- [ ] `tests/domains/jeux/test_integration.py`
  - [ ] Écrire 10+ tests
  - [ ] Couvrir: intégration APIs jeux
  - [ ] Statut: **À FAIRE**

**Impact espéré**: +3-5% couverture  
**Effort**: 40-50 heures

---

## 🔄 PHASE 2: Fichiers <5% (Semaine 3-4)

### Top 4 fichiers volumineux (RÉÉCRIRE complètement)

- [ ] `src/domains/cuisine/ui/recettes.py` (825 statements, 2.48%)
  - [ ] Analyser code source complet
  - [ ] Identifier toutes les fonctions/classes
  - [ ] Écrire minimum 100+ tests (actuellement: ~20)
  - [ ] Statut: **À FAIRE** - PRIORITÉ 🚨

- [ ] `src/domains/cuisine/ui/inventaire.py` (825 statements, 3.86%)
  - [ ] Analyser code source complet
  - [ ] Identifier toutes les fonctions/classes
  - [ ] Écrire minimum 80+ tests (actuellement: ~20)
  - [ ] Statut: **À FAIRE** - PRIORITÉ 🚨

- [ ] `src/domains/cuisine/ui/courses.py` (659 statements, 3.06%)
  - [ ] Analyser code source complet
  - [ ] Identifier toutes les fonctions/classes
  - [ ] Écrire minimum 70+ tests (actuellement: ~15)
  - [ ] Statut: **À FAIRE** - PRIORITÉ 🚨

- [ ] `src/domains/jeux/ui/paris.py` (622 statements, 4.03%)
  - [ ] Analyser code source complet
  - [ ] Identifier toutes les fonctions/classes
  - [ ] Écrire minimum 60+ tests (actuellement: ~25)
  - [ ] Statut: **À FAIRE** - PRIORITÉ 🚨

### Autres fichiers <5% (8 fichiers)

- [ ] `src/utils/formatters/dates.py` (4.4%)
- [ ] `src/domains/planning/ui/vue_ensemble.py` (4.4%)
- [ ] `src/domains/cuisine/ui/batch_cooking_detaille.py` (4.7%)
- [ ] `src/domains/utils/ui/rapports.py` (4.7%)
- [ ] `src/domains/famille/ui/routines.py` (4.7%)
- [ ] `src/domains/cuisine/ui/recettes_import.py` (4.7%)
- [ ] `src/domains/jeux/logic/paris_logic.py` (4.8%)
- [ ] `src/domains/utils/ui/parametres.py` (5.0%)

**Impact espéré**: +5-8% couverture  
**Effort**: 60-80 heures (très gros, réparti sur 2 semaines)

---

## 🔌 PHASE 3: Services Critiques (Semaine 5-6)

### Services à améliorer (33 fichiers, actuellement 30.1%)

#### Top 5 prioritaires

- [ ] `src/services/base_ai_service.py` (13.54%) - 222 statements
  - [ ] Écrire 50+ tests
  - [ ] Couvrir: appels IA, cache, limitation débit
  - [ ] Statut: **À FAIRE**

- [ ] `src/services/base_service.py` (16.94%) - 168 statements
  - [ ] Écrire 40+ tests
  - [ ] Couvrir: classe de base services
  - [ ] Statut: **À FAIRE**

- [ ] `src/services/auth.py` (19.27%) - 381 statements 🚨 IMPORTANT
  - [ ] Écrire 80+ tests
  - [ ] Couvrir: authentification, tokens, permissions
  - [ ] Statut: **À FAIRE**

- [ ] `src/services/backup.py` (18.32%) - 319 statements
  - [ ] Écrire 60+ tests
  - [ ] Couvrir: sauvegarde, restauration
  - [ ] Statut: **À FAIRE**

- [ ] `src/services/calendar_sync.py` (16.97%) - 481 statements
  - [ ] Écrire 70+ tests
  - [ ] Couvrir: synchronisation calendrier
  - [ ] Statut: **À FAIRE**

#### Autres services

- [ ] `src/services/weather.py` (18.76%)
- [ ] `src/services/pdf_export.py` (25.50%)
- [ ] `src/services/notifications.py` (25.31%)
- [ ] `src/services/planning.py` (23.42%)
- [ ] Et 24 autres...

**Impact espéré**: +10-15% couverture  
**Effort**: 80-100 heures

---

## 🧩 PHASE 4: UI Composants (Semaine 5-6, parallèle à services)

### Modules UI faibles (37.5%)

- [ ] `src/ui/components/camera_scanner.py` (6.56%) - 182 statements
- [ ] `src/ui/components/layouts.py` (8.54%) - 56 statements
- [ ] `src/ui/core/base_form.py` (13.67%) - 101 statements
- [ ] `src/ui/core/base_module.py` (17.56%) - 192 statements
- [ ] `src/ui/layout/sidebar.py` (10.45%) - 47 statements
- [ ] Et 21 autres...

**Impact espéré**: +10-15% couverture  
**Effort**: 60-80 heures

---

## 🧪 PHASE 5: Tests E2E (Semaine 7-8)

### Fichier de structure créé

- [x] `tests/e2e/test_main_flows.py` - Structure de base

### Tests E2E à implémenter (5 flux principaux)

- [ ] `test_cuisine_flow_e2e`: Recette → Planning → Courses
  - [ ] Créer recette
  - [ ] Planifier recette
  - [ ] Générer liste courses
  - Statut: **À IMPLÉMENTER**

- [ ] `test_famille_flow_e2e`: Ajouter membre → Suivi
  - [ ] Ajouter membre famille
  - [ ] Suivi activités
  - [ ] Notifications
  - Statut: **À IMPLÉMENTER**

- [ ] `test_planning_flow_e2e`: Créer événement → Synchroniser
  - [ ] Créer événement
  - [ ] Synchroniser calendrier
  - [ ] Rappels
  - Statut: **À IMPLÉMENTER**

- [ ] `test_auth_flow_e2e`: Login → Multi-tenant
  - [ ] Authentification
  - [ ] Gestion sessions
  - [ ] Isolation data
  - Statut: **À IMPLÉMENTER**

- [ ] `test_maison_flow_e2e`: Projet → Budget
  - [ ] Ajouter projet
  - [ ] Gérer budget
  - [ ] Rapports
  - Statut: **À IMPLÉMENTER**

**Impact espéré**: +2-3% couverture  
**Effort**: 30-40 heures

---

## 🛠️ Tâches d'Infrastructure

### Configuration pytest

- [ ] Ajouter markers E2E dans `pytest.ini`
- [ ] Ajouter markers integration
- [ ] Configurer timeout tests E2E

### Configuration pyproject.toml

- [ ] Ajouter `[tool.pytest.ini_options]`
- [ ] Configurer markers
- [ ] Configurer testpaths

### Fixtures améliorées (conftest.py)

- [ ] Améliorer fixture test_db
- [ ] Ajouter fixture streamlit_mock
- [ ] Ajouter fixture API_mock
- [ ] Ajouter fixture sample_data

### CI/CD Integration

- [ ] Ajouter step GitHub Actions: coverage check
- [ ] Configurer fail-on-coverage <80%
- [ ] Ajouter badge couverture README

---

## 📊 Suivi des Métriques

### Baseline (3 février 2026)

```
Couverture globale: 29.37%
Fichiers testés: 66/209 (31.6%)
Fichiers >80%: 60/209 (28.7%)
Fichiers 0%: 8
Fichiers <30%: 100
```

### Semaine 1-2 (Après PHASE 1)

- [ ] Mesurer couverture (objectif: 32-35%)
- [ ] Documenter progrès
- [ ] Identifier blocages

### Semaine 3-4 (Après PHASE 2)

- [ ] Mesurer couverture (objectif: 40-45%)
- [ ] Comparer vs baseline
- [ ] Ajuster si besoin

### Semaine 5-6 (Après PHASE 3-4)

- [ ] Mesurer couverture (objectif: 55-65%)
- [ ] Analyser modules faibles
- [ ] Planifier dernière phase

### Semaine 7-8 (Après PHASE 5)

- [ ] Mesurer couverture (objectif: >80%)
- [ ] Rapport final
- [ ] Mise en place CI/CD strict

---

## 🎓 Ressources et Documentation

### À consulter

- [x] `COVERAGE_REPORT.md` - Rapport détaillé complet
- [x] `COVERAGE_EXECUTIVE_SUMMARY.md` - Résumé exécutif
- [x] `ACTION_PLAN.py` - Plan d'action détaillé
- [ ] `docs/ARCHITECTURE.md` - Architecture générale
- [ ] `tests/conftest.py` - Configuration tests actuelle
- [ ] `pytest.ini` - Configuration pytest

### Patterns à utiliser

```python
# TOUJOURS utiliser ces patterns

# 1. Test unit simple
@pytest.mark.unit
def test_function(test_db: Session):
    # Arrange
    data = create_test_data()

    # Act
    result = function_to_test(data)

    # Assert
    assert result.property == expected_value

# 2. Test avec mock
@pytest.mark.unit
@patch('module.external_function')
def test_with_mock(mock_external):
    mock_external.return_value = "mocked"
    result = function_to_test()
    assert result == "expected"

# 3. Test d'exception
def test_error_handling():
    with pytest.raises(ValueError):
        dangerous_function()

# 4. Test parametré
@pytest.mark.parametrize("input,expected", [
    ("a", 1),
    ("b", 2),
    ("c", 3),
])
def test_multiple_cases(input, expected):
    assert function(input) == expected
```

---

## 🚀 Commandes Utiles

```bash
# Générer couverture complète
pytest --cov=src --cov-report=html --cov-report=term

# Tester un fichier spécifique
pytest tests/domains/cuisine/ui/test_recettes.py -v

# Tester une classe
pytest tests/domains/cuisine/ui/test_recettes.py::TestRecettesUI -v

# Tester une fonction
pytest tests/domains/cuisine/ui/test_recettes.py::TestRecettesUI::test_create_recipe -v

# Tester seulement les E2E
pytest tests/e2e/ -v

# Tester seulement les units
pytest -m unit -v

# Tester seulement les intégration
pytest -m integration -v

# Obtenir couverture manquante
pytest --cov=src --cov-report=term-missing
```

---

## 📝 Notes et Observations

### Points Forts

- ✅ Module core bien couvert (76.6%)
- ✅ Infrastructure de tests existante et bonne
- ✅ Arborescence tests cohérente
- ✅ Fixtures déjà en place
- ✅ CI/CD possible

### Points à Améliorer

- ❌ UI pratiquement pas testée (37.5%)
- ❌ Services faiblement testés (30.1%)
- ❌ Fichiers volumineux (825+ statements)
- ❌ Pas de tests E2E
- ❌ Pas de CI/CD strict

### Risques et Mitigations

| Risque                      | Mitigation                      |
| --------------------------- | ------------------------------- |
| Fichiers trop gros          | Découper en modules + fixtures  |
| Streamlit mockage difficile | Utiliser `@patch` + `MagicMock` |
| Tests lents                 | Utiliser SQLite in-memory       |
| Couverture surface          | Vérifier branches + exceptions  |

---

## 👥 Responsabilités

- **Chef de projet**: Suivi timeline, priorités
- **Développeur 1**: PHASE 1 + PHASE 2 (fichiers 0-5%)
- **Développeur 2**: PHASE 3 + PHASE 4 (services + UI)
- **Développeur 3**: PHASE 5 + Infrastructure (E2E + CI/CD)

---

## ✨ Conclusion

**Status**: 🚨 **EN COURS**

Tous les outils, templates et documentation sont prêts.  
Prêt à commencer PHASE 1 immédiatement.

**Prochain jalon**: +3-5% couverture (Semaine 2)

---

**Dernière mise à jour**: 3 février 2026  
**Prochaine review**: Fin Semaine 2  
**Responsable**: Copilot (via automated analysis)

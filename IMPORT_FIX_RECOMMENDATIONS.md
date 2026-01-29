# RECOMMANDATIONS DE CORRECTION - IMPORTS MANQUANTS

## Fichier 1: tests/integration/test_planning_module.py

### Problème actuellement:
```python
from src.domains.cuisine.logic.planning_logic import (
    render_planning,      # ❌ N'EXISTE PAS
    render_generer,       # ❌ N'EXISTE PAS
    render_historique     # ❌ N'EXISTE PAS
)
```

### Options de correction:

#### Option A: Importer depuis l'interface utilisateur (UI)
Si ces fonctions se trouvent dans `src/domains/cuisine/ui/planning.py`:
```python
from src.domains.cuisine.ui.planning import (
    afficher_planning,    # À adapter selon les noms réels
    afficher_generer,
    afficher_historique
)
```

#### Option B: Utiliser la logique métier disponible
Utiliser les fonctions de `planning_logic.py` disponibles:
```python
from src.domains.cuisine.logic.planning_logic import (
    get_debut_semaine,
    get_fin_semaine,
    get_dates_semaine,
    organiser_repas_par_jour,
    organiser_repas_par_type,
    calculer_statistiques_planning,
    calculer_cout_planning,
    calculer_variete_planning,
    valider_repas
)
```

#### Option C: Corriger si c'est une couche intermédiaire
Si les fonctions `render_*` doivent exister, vérifier:
1. Qu'elles n'ont pas été renommées
2. Qu'elles ne se trouvent pas dans un autre fichier
3. Les créer si elles doivent exister

### Fichiers concernés à vérifier:
- `src/domains/cuisine/ui/planning.py` - Chercher les fonctions render_*
- `src/domains/cuisine/logic/planning_logic.py` - Fonctions disponibles
- `src/modules/cuisine/planning.py` - Module Streamlit principal

---

## Fichier 2: tests/integration/test_courses_module.py

### Problème actuellement:
```python
from src.domains.cuisine.logic.courses import (  # ❌ Mauvais chemin!
    render_liste_active,          # ❌ N'EXISTE PAS
    render_rayon_articles,        # ❌ N'EXISTE PAS
    render_ajouter_article,       # ❌ N'EXISTE PAS
    render_suggestions_ia,        # ❌ N'EXISTE PAS
    render_historique,            # ❌ N'EXISTE PAS
    render_modeles                # ❌ N'EXISTE PAS
)
```

### Problèmes identifiés:
1. Le chemin d'import est INCORRECT: `src.domains.cuisine.logic.courses`
   - Doit être: `src.domains.cuisine.logic.courses_logic`
2. Les fonctions `render_*` n'existent nulle part

### Options de correction:

#### Option A: Importer depuis l'interface utilisateur (UI)
Si ces fonctions se trouvent dans `src/domains/cuisine/ui/courses.py`:
```python
from src.domains.cuisine.ui.courses import (
    afficher_liste_active,          # À adapter selon les noms réels
    afficher_rayon_articles,
    afficher_ajouter_article,
    afficher_suggestions_ia,
    afficher_historique,
    afficher_modeles
)
```

#### Option B: Utiliser la logique métier disponible
Utiliser les fonctions de `courses_logic.py` disponibles:
```python
from src.domains.cuisine.logic.courses_logic import (
    filtrer_par_priorite,
    filtrer_par_rayon,
    filtrer_par_recherche,
    filtrer_articles,
    trier_par_priorite,
    trier_par_rayon,
    trier_par_nom,
    grouper_par_rayon,
    grouper_par_priorite,
    calculer_statistiques
)
```

#### Option C: Importer le module UI directement
```python
from src.modules.cuisine.courses import app as courses_app
```

### Fichiers concernés à vérifier:
- `src/domains/cuisine/ui/courses.py` - Chercher les fonctions render_*
- `src/domains/cuisine/logic/courses_logic.py` - Fonctions disponibles
- `src/modules/cuisine/courses.py` - Module Streamlit principal

---

## CHECKLIST DE CORRECTION

### ✅ Étape 1: Identifier l'emplacement correct des fonctions
- [ ] Ouvrir `src/domains/cuisine/ui/planning.py`
  - [ ] Chercher les fonctions `render_planning`, `render_generer`, `render_historique`
  - [ ] Noter les noms exacts s'ils existent
  
- [ ] Ouvrir `src/domains/cuisine/ui/courses.py`
  - [ ] Chercher les fonctions `render_*` du fichier de test
  - [ ] Noter les noms exacts s'ils existent

### ✅ Étape 2: Mettre à jour les imports
- [ ] Corriger `test_planning_module.py`
  - [ ] Utiliser le bon chemin d'import
  - [ ] Importer les bonnes fonctions
  
- [ ] Corriger `test_courses_module.py`
  - [ ] Utiliser `courses_logic` au lieu de `courses`
  - [ ] Importer les bonnes fonctions

### ✅ Étape 3: Valider les tests
- [ ] Exécuter: `pytest tests/integration/test_planning_module.py -v`
- [ ] Exécuter: `pytest tests/integration/test_courses_module.py -v`
- [ ] Corriger les assertions si nécessaire

### ✅ Étape 4: Valider l'ensemble
- [ ] Exécuter: `pytest tests/ -v`
- [ ] Vérifier la couverture: `pytest --cov=src tests/`

---

## NOTES IMPORTANTES

1. **Distinction Logic vs UI**:
   - `logic/` = Fonctions métier pures (sans Streamlit)
   - `ui/` = Fonctions d'affichage (avec Streamlit st.*)

2. **Nommage**: 
   - Les fonctions métier: `get_X()`, `calculer_X()`, `valider_X()`, `filtrer_X()`
   - Les fonctions UI: `afficher_X()`, `render_X()`, `display_X()`

3. **Imports de test**:
   - Les tests unitaires importent généralement la logique métier
   - Les tests d'intégrateur peuvent importer la UI
   - Les tests E2E testent les workflows complets via Streamlit

4. **Recherche rapide**:
   Utiliser `grep` ou `Find in Files` pour chercher:
   ```bash
   grep -r "def render_planning" src/
   grep -r "def render_liste_active" src/
   ```

---

## SUPPORT

Pour plus d'informations sur la structure du projet:
- Voir: `docs/ARCHITECTURE.md`
- Voir: `.github/copilot-instructions.md`

Pour les tests:
- Voir: `tests/conftest.py` pour les fixtures
- Voir: `tests/integration/` pour les exemples de tests d'intégration

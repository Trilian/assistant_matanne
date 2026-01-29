# Rapport de Refactoring des Imports

## Analyse de la situation actuelle

### Problème identifié
Les 21 fichiers `*_logic.py` ont été créés et testés (52 tests, 94% pass), mais **les modules UI ne les utilisent PAS**. Ils continuent d'importer depuis:
- ❌ `src.services.*` → OK pour accès BD, mais aussi utilisé pour logique pure
- ❌ `src.modules.*.helpers` → Mélange logique pure + accès BD + cache Streamlit

### Architecture cible
```
UI Module (*.py)
    ↓ imports
    ├── *_logic.py (logique pure, calculs, validations)  ← DOIT être utilisé
    └── services/* (accès BD uniquement)                 ← OK pour BD
```

---

## Modules à refactoriser (par priorité)

### 🔴 Priorité CRITIQUE - Modules racine (4 fichiers)

#### 1. `src/modules/accueil.py` (483 lignes)
**Imports actuels:**
```python
from src.services.recettes import get_recette_service
from src.services.inventaire import get_inventaire_service
from src.services.courses import get_courses_service
from src.services.planning import get_planning_service
```

**Fichier logic:** `accueil_logic.py` (273 lignes)
- ✅ Fonctions disponibles: `calculer_metriques_dashboard()`, `generer_notifications()`, `est_cette_semaine()`, `est_en_retard()`, `compter_alertes_critiques()`

**Action:** Ajouter import `from src.modules.accueil_logic import *` et remplacer les calculs inline par les fonctions logic

**Fonctions à refactoriser:**
- `render_critical_alerts()` → utiliser `generer_notifications()` + `compter_alertes_critiques()`
- `render_global_stats()` → utiliser `calculer_metriques_dashboard()`
- Ligne 113, 123, 150, 179, 230-234, 319, 356, 399, 445: remplacer appels services par logic

---

#### 2. `src/modules/barcode.py` (239 lignes)
**Imports actuels:**
```python
from src.services.barcode import BarcodeService
from src.services.inventaire import InventaireService
```

**Fichier logic:** `barcode_logic.py` (347 lignes)
- ✅ Fonctions: `valider_ean13()`, `calculer_checksum_ean13()`, `extraire_info_barcode()`

**Action:** Ajouter import logic pour validation, garder services pour BD

---

#### 3. `src/modules/parametres.py` (784 lignes)
**Imports actuels:**
```python
from src.services.budget import CategorieDepense  # ligne 621
from src.services.backup import get_backup_service  # ligne 659
from src.services.weather import get_weather_garden_service  # ligne 692
```

**Fichier logic:** `parametres_logic.py` (339 lignes)
- ✅ Fonctions: `valider_configuration()`, `obtenir_parametres_defaut()`, `verifier_sante_bd()`

**Action:** Ajouter import logic pour validations

---

#### 4. `src/modules/rapports.py` (? lignes)
**Imports actuels:**
```python
from src.services.rapports_pdf import RapportsPDFService
```

**Fichier logic:** `rapports_logic.py` (328 lignes)
- ✅ Fonctions: `generer_rapport_periode()`, `calculer_statistiques_rapport()`

---

### 🟠 Priorité HAUTE - Module Cuisine (4 fichiers + 1 import)

#### 5. `src/modules/cuisine/recettes.py` (1046 lignes)
**Import actuel:** ligne 7
```python
from src.services.recettes import get_recette_service
```

**Fichier logic:** `recettes_logic.py` (? lignes)
- ✅ Fonctions: `valider_recette()`, `calculer_cout_recette()`, `calculer_calories_portion()`
- ⚠️ **PROBLÈME**: recettes_logic.py importe AUSSI `get_recette_service` (ligne 10) → risque de circulaire

**Action:** 
1. Nettoyer recettes_logic.py pour qu'il soit 100% pur (retirer import service)
2. Ajouter imports dans recettes.py

---

#### 6. `src/modules/cuisine/inventaire.py` (566 lignes)
**Imports actuels:**
```python
from src.services.inventaire import get_inventaire_service  # ligne 15
from src.services.predictions import obtenir_service_predictions  # ligne 16
from src.services.notifications import obtenir_service_notifications  # lignes 221, 534
```

**Fichier logic:** `inventaire_logic.py` (752 lignes - le plus gros!)
- ✅ Fonctions disponibles: beaucoup!

---

#### 7. `src/modules/cuisine/courses.py` (971 lignes)
**Imports actuels:**
```python
from src.services.courses import get_courses_service
from src.services.inventaire import get_inventaire_service
from src.services.recettes import get_recette_service
from src.services.realtime_sync import get_realtime_sync_service
```

**Fichier logic:** `courses_logic.py` (613 lignes)

---

#### 8. `src/modules/cuisine/planning.py` (? lignes)
**Imports actuels:**
```python
from src.services.planning import get_planning_service
from src.services.recettes import get_recette_service
```

**Fichier logic:** `planning_logic.py` (? lignes)

---

#### 9. `src/modules/cuisine/recettes_import.py` (? lignes)
**Import actuel:**
```python
from src.services.recettes import get_recette_service
```

**Action:** Ajouter validation depuis recettes_logic

---

### 🟡 Priorité MOYENNE - Module Maison (4 fichiers)

#### 10-12. `src/modules/maison/{jardin,projets,entretien}.py`
**Tous importent depuis:**
```python
from src.services.base_ai_service import BaseAIService
from src.modules.maison.helpers import (  # ← PROBLÈME ICI
    charger_plantes, get_plantes_a_arroser, get_recoltes_proches,
    get_stats_jardin, get_saison, clear_maison_cache,
    charger_projets, get_projets_urgents, get_stats_projets,
    charger_routines, get_taches_today, get_stats_entretien
)
```

**Fichiers logic disponibles:**
- `jardin_logic.py` (236 lignes) → `get_saison_actuelle()`, `calculer_jours_avant_arrosage()`
- `projets_logic.py` (? lignes)
- `entretien_logic.py` (? lignes)

**PROBLÈME:** helpers.py mélange logique pure + accès BD + cache

**Action:** 
1. Identifier quelles fonctions de helpers sont pures → devraient être dans *_logic.py
2. Garder dans helpers seulement les fonctions avec accès BD/cache
3. Refactoriser imports

---

#### 13. `src/modules/maison/__init__.py`
Importe aussi depuis helpers (ligne 19)

---

### 🟢 Priorité BASSE - Module Famille (7 fichiers)

#### 14-20. Famille: `accueil.py`, `jules.py`, `activites.py`, `sante.py`, `shopping.py`, `integration_cuisine_courses.py`
**Tous importent depuis:**
```python
from src.modules.famille.helpers import (...)
```

**Fichiers logic disponibles:** 8 fichiers
- `accueil_logic.py`
- `jules_logic.py`
- `activites_logic.py`
- `sante_logic.py`
- `bien_etre_logic.py`
- `routines_logic.py`
- etc.

**Action:** Même stratégie que maison - nettoyer helpers, rediriger vers *_logic.py

---

### 🔵 Priorité INFO - Module Planning (3 fichiers)

#### 21-23. Planning: `calendrier.py`, `vue_ensemble.py`, `vue_semaine.py`
**Tous importent depuis:**
```python
from src.services.planning_unified import get_planning_service
```

**Fichiers logic disponibles:**
- `calendrier_logic.py`
- `vue_ensemble_logic.py`
- `vue_semaine_logic.py`

---

## Plan d'action détaillé

### Phase 1: Nettoyer les *_logic.py pour qu'ils soient PURS ✅
1. Vérifier que TOUS les *_logic.py n'importent PAS de services
2. Si un *_logic.py importe un service → le retirer et déplacer la fonction dans le module UI ou service

### Phase 2: Refactoriser les modules racine (4 fichiers) 🔴
1. accueil.py
2. barcode.py
3. parametres.py
4. rapports.py

### Phase 3: Refactoriser module Cuisine (5 fichiers) 🟠
1. recettes.py + recettes_import.py
2. inventaire.py
3. courses.py
4. planning.py

### Phase 4: Refactoriser module Maison (4 fichiers) 🟡
1. Nettoyer helpers.py (séparer pur vs BD)
2. Enrichir jardin_logic.py, projets_logic.py, entretien_logic.py
3. Refactoriser jardin.py, projets.py, entretien.py, __init__.py

### Phase 5: Refactoriser module Famille (7 fichiers) 🟢
1. Nettoyer helpers.py
2. Refactoriser tous les modules

### Phase 6: Refactoriser module Planning (3 fichiers) 🔵
1. calendrier.py
2. vue_ensemble.py
3. vue_semaine.py

---

## Métriques

**Fichiers à refactoriser:** 24 modules UI
**Fichiers logic disponibles:** 21 fichiers (~5000 lignes)
**Imports problématiques identifiés:** ~40 lignes d'imports

**Estimation temps:**
- Phase 1 (nettoyage logic): 1h
- Phase 2 (racine): 2h
- Phase 3 (cuisine): 3h
- Phase 4 (maison): 2h
- Phase 5 (famille): 2h
- Phase 6 (planning): 1h
**Total:** ~11h de refactoring

---

## Risques et précautions

⚠️ **Risques:**
1. Imports circulaires (recettes_logic.py importe déjà get_recette_service)
2. Tests peuvent casser si on change trop de choses
3. Logique dispersée entre helpers, services, logic

✅ **Précautions:**
1. Faire phase par phase
2. Tester après chaque phase
3. Vérifier couverture reste ~40%
4. Commiter après chaque module refactorisé

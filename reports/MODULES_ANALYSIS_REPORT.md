# Rapport d'analyse — src/modules/

**Date**: 2026-02-24  
**Scope**: `d:\Projet_streamlit\assistant_matanne\src\modules\`  
**Total fichiers .py**: 187 (+ 2 standalone: `design_system.py`, `__init__.py`)  
**Total LOC (estimé)**: ~28 230

---

## 1. Structure globale — Fichiers & sous-répertoires

| Module | Sous-dossiers | Fichiers .py | LOC |
|--------|--------------|-------------|-----|
| **accueil/** | — | 6 | 635 |
| **cuisine/** | `batch_cooking_detaille/`, `courses/`, `inventaire/`, `planificateur_repas/`, `recettes/` | 51 | 8 060 |
| **famille/** | `achats_famille/`, `jules/`, `suivi_perso/`, `weekend/` | 26 | 3 783 |
| **maison/** | `charges/`, `depenses/`, `entretien/`, `hub/`, `jardin/` | 34 | 4 507 |
| **jeux/** | `loto/`, `paris/` | 28 | 3 961 |
| **planning/** | `calendrier/` | 12 | 2 199 |
| **parametres/** | — | 9 | 998 |
| **utilitaires/** | `barcode/` | 13 | 2 838 |
| **_framework/** | — | 6 | 1 044 |
| *design_system.py* | — | 1 | 183 |
| *__init__.py* | — | 1 | 22 |
| **TOTAL** | | **187** | **28 230** |

---

## 2. Analyse détaillée par module

### 2.1 accueil/ (6 fichiers, 635 LOC)

| Critère | Valeur |
|---------|--------|
| `app()` entry point | ✅ `dashboard.py` (re-exporté par `__init__.py`) |
| `with error_boundary` | 1 (`dashboard.py:43`) |
| `@profiler_rerun` | 1 (`dashboard.py:37`) |
| `KeyNamespace` | 4 (`dashboard.py`, `summaries.py`, `stats.py`, `alerts.py` — namespace `"accueil"`) |
| `@cached_fragment` | 1 (`stats.py:14`) |
| `@lazy` | 0 |
| `tabs_with_url()` | 0 |
| `@auto_refresh` | 2 (`alerts.py:16` — 30s, `stats.py:50` — 60s) |
| `@ui_fragment` | 1 (`dashboard.py:195`) |
| Chat IA contextuel | ❌ Non intégré |
| Navigation inter-modules | ✅ 6 liens (`naviguer_vers` vers cuisine.recettes, courses, inventaire, planning) |

### 2.2 cuisine/ (51 fichiers, 8 060 LOC) — Plus gros domaine

| Critère | Valeur |
|---------|--------|
| `app()` entry points | ✅ ×5 : `recettes/__init__.py`, `inventaire/__init__.py`, `courses/__init__.py`, `planificateur_repas/__init__.py`, `batch_cooking_detaille/app.py` |
| `with error_boundary` | 22 (recettes: 5, inventaire: 12, courses: 6, planificateur: 1) |
| `@profiler_rerun` | 5 (`recettes`, `inventaire`, `courses`, `planificateur_repas`, `batch_cooking`) |
| `KeyNamespace` | 3 (`recettes/__init__`, `recettes/liste.py`, `inventaire/__init__`) |
| `@cached_fragment` | 0 |
| `@lazy` | 0 |
| `tabs_with_url()` | 4 (`recettes`, `inventaire`, `courses`, `planificateur_repas`) |
| `@auto_refresh` | 1 (`inventaire/alertes.py:14` — 120s) |
| `@ui_fragment` | 0 (aucun sous-composant fragmenté) |
| Chat IA contextuel | ✅ `recettes/__init__.py` → `afficher_chat_contextuel("recettes")` |
| Connections inter-modules | ✅ `batch_cooking_detaille` → `COURSES_DEPUIS_BATCH` (courses), `planificateur_repas` → `COURSES_DEPUIS_PLANNING` |

### 2.3 famille/ (26 fichiers, 3 783 LOC)

| Critère | Valeur |
|---------|--------|
| `app()` entry points | ✅ ×8 : `hub_famille.py`, `jules/__init__`, `jules_planning.py`, `suivi_perso/__init__`, `weekend/__init__`, `achats_famille/__init__`, `activites.py`, `routines.py` |
| `with error_boundary` | 26 (hub: 6, jules: 5, jules_planning: 4, suivi_perso: 5, weekend: 6, achats: 6) |
| `@profiler_rerun` | 8 (`famille`, `jules`, `jules_planning`, `suivi_perso`, `weekend`, `achats_famille`, `activites`, `routines`) |
| `KeyNamespace` | 1 (`hub_famille.py` — namespace `"famille"`) |
| `@cached_fragment` | 0 |
| `@lazy` | 0 |
| `tabs_with_url()` | 4 (`activites`, `weekend`, `suivi_perso`, `jules`) |
| `@auto_refresh` | 1 (`suivi_perso/tableau_bord.py:31` — 90s) |
| `@ui_fragment` | 6 (`jules/components.py`: 4, `weekend/components.py`: 2) |
| Chat IA contextuel | ✅ ×3 : `hub_famille.py`, `jules/__init__`, `weekend/__init__` |
| Fichiers utilitaires purs | `activites_utils.py`, `routines_utils.py`, `age_utils.py`, `utils.py` |

### 2.4 maison/ (34 fichiers, 4 507 LOC)

| Critère | Valeur |
|---------|--------|
| `app()` entry points | ✅ ×5 : `hub/__init__`, `jardin/__init__`, `entretien/__init__`, `depenses/__init__`, `charges/__init__` |
| `with error_boundary` | 23 (hub: 1, jardin: 7, entretien: 7, depenses: 3, charges: 5) |
| `@profiler_rerun` | 5 (`maison_hub`, `jardin`, `entretien`, `depenses`, `charges`) |
| `KeyNamespace` | 5 (`charges/__init__`, `charges/onglets`, `depenses/export`, `depenses/cards`, `depenses/charts`) |
| `@cached_fragment` | 2 (`entretien/onglets_analytics.py:171`, `jardin/onglets.py:409`) |
| `@lazy` | 1 (`jardin/onglets.py:540`) |
| `tabs_with_url()` | 0 |
| `@auto_refresh` | 2 (`hub/ui.py:102` — 60s, `hub/ui.py:197` — 120s) |
| `@ui_fragment` | 18 (`depenses/components`: 4, `entretien/onglets_*`: 7, `jardin/onglets`: 6, `charges/onglets`: 5) |
| Chat IA contextuel | ❌ Non intégré |
| Navigation interne | ✅ Hub navigue vers jardin, entretien, charges, depenses |

### 2.5 jeux/ (28 fichiers, 3 961 LOC)

| Critère | Valeur |
|---------|--------|
| `app()` entry points | ✅ ×2 : `paris/__init__`, `loto/__init__` |
| `with error_boundary` | 8 (paris: 1, loto: 7) |
| `@profiler_rerun` | 2 (`paris`, `loto`) |
| `KeyNamespace` | 3 (`paris/__init__`, `loto/__init__`, `paris/prediction.py`) |
| `@cached_fragment` | 2 (`loto/statistiques.py:50` — 5 min, `loto/statistiques.py:133` — 1h) |
| `@lazy` | 0 |
| `tabs_with_url()` | 1 (`paris/__init__`) |
| `@auto_refresh` | 0 |
| `@ui_fragment` | 5 (`paris/series`: 2, `paris/prediction`: 1, `paris/tableau_bord`: 1, `paris/gestion`: 1) |
| Chat IA contextuel | ❌ Non intégré |

### 2.6 planning/ (12 fichiers, 2 199 LOC)

| Critère | Valeur |
|---------|--------|
| `app()` entry points | ✅ ×3 : `calendrier/__init__`, `timeline_ui.py`, `templates_ui.py` |
| `with error_boundary` | 3 (`calendrier`: 1, `timeline_ui`: 1, `templates_ui`: 1) |
| `@profiler_rerun` | 3 (`calendrier`, `timeline_ui`, `templates_ui`) |
| `KeyNamespace` | 0 |
| `@cached_fragment` | 0 |
| `@lazy` | 0 |
| `tabs_with_url()` | 1 (`calendrier/__init__`) |
| `@auto_refresh` | 0 |
| `@ui_fragment` | 0 |
| Chat IA contextuel | ✅ `calendrier/__init__` → `afficher_chat_contextuel("planning")` |
| Navigation inter-modules | ✅ `calendrier/components` → `cuisine.courses`, `cuisine.batch_cooking`, `cuisine.planning_semaine` |

### 2.7 parametres/ (9 fichiers, 998 LOC)

| Critère | Valeur |
|---------|--------|
| `app()` entry point | ✅ `__init__.py` |
| `with error_boundary` | 8 (tous les onglets protégés) |
| `@profiler_rerun` | 1 (`parametres`) |
| `KeyNamespace` | 0 |
| `@cached_fragment` | 1 (`about.py:13` — 1h, contenu statique) |
| `@lazy` | 1 (`ia.py:15` — détails IA conditionnels) |
| `tabs_with_url()` | 0 |
| `@auto_refresh` | 0 |
| `@ui_fragment` | 6 (`affichage`, `ia`, `database`, `foyer`, `budget`, `cache`) |
| Chat IA contextuel | ❌ Non intégré |

### 2.8 utilitaires/ (13 fichiers, 2 838 LOC)

| Critère | Valeur |
|---------|--------|
| `app()` entry points | ✅ ×5 : `barcode/app.py`, `rapports.py`, `scan_factures.py`, `recherche_produits.py`, `notifications_push.py`, `chat_ia.py` (6 total) |
| `with error_boundary` | 12 (barcode: 5, rapports: 4, scan_factures: 2, notifications: 5, chat_ia: 1) |
| `@profiler_rerun` | 6 (`barcode`, `rapports`, `scan_factures`, `recherche_produits`, `notifications`, `chat_ia`) |
| `KeyNamespace` | 2 (`chat_ia.py`, `scan_factures.py` — usage dynamique) |
| `@cached_fragment` | 0 |
| `@lazy` | 1 (`notifications_push.py:397`) |
| `tabs_with_url()` | 0 |
| `@auto_refresh` | 1 (`notifications_push.py:321` — 120s) |
| `@ui_fragment` | 10 (`notifications`: 4, `barcode/operations`: 4, `barcode/scanner`: 1, `rapports`: 4) |
| Chat IA contextuel | ✅ `chat_ia.py` est le module dédié (ChatIAService + BaseAIService) |
| Connection scan→charges | ✅ `scan_factures.py` → enregistre via `KeyNamespace("charges")` dans session_state |

### 2.9 _framework/ (6 fichiers, 1 044 LOC)

| Critère | Valeur |
|---------|--------|
| `app()` entry point | ✅ `example_module.py` (démonstration) |
| `with error_boundary` | 8 (error_boundary.py: 6 exemples/implémentation, base_module: 2, example: 2) |
| `@profiler_rerun` | 0 (framework pur, pas de module métier) |
| Fournit | `error_boundary`, `auto_refresh_fragment`, `lazy_fragment`, `cached_fragment`, `ui_fragment`, `BaseModule`, `StateManager` |

---

## 3. Totaux agrégés

### 3.1 Compteurs globaux

| Pattern | Total instances (hors _framework) | Modules avec adoption | % adoption (sur 8 modules métier) |
|---------|-----------------------------------|----------------------|-----------------------------------|
| `with error_boundary` | **115** (hors _framework: 104) | 8/8 | **100%** |
| `@profiler_rerun` | **32** décorations (`app()`) | 8/8 | **100%** |
| `KeyNamespace` | **18** usages | 6/8 (absents: planning, _framework) | **75%** |
| `@cached_fragment` | **6** | 4/8 (accueil, maison, jeux, parametres) | **50%** |
| `@lazy` | **3** | 3/8 (maison, parametres, utilitaires) | **38%** |
| `tabs_with_url()` | **10** modules | 5/8 (cuisine, famille, jeux, planning, — absents: accueil, maison, parametres, utilitaires) | **63%** |
| `@auto_refresh` | **7** usages | 4/8 (accueil, cuisine, famille, maison, utilitaires) | **50%** |
| `@ui_fragment` | **50+** | 6/8 (absents: cuisine modules principaux, planning) | **75%** |
| Chat IA contextuel | **6** intégrations | 4/8 (cuisine, famille, planning, utilitaires) | **50%** |

### 3.2 app() entry points

| Module | Points d'entrée `app()` | Statut |
|--------|------------------------|--------|
| accueil | 1 | ✅ |
| cuisine | 5 (recettes, inventaire, courses, planificateur, batch_cooking) | ✅ |
| famille | 8 (hub, jules, jules_planning, suivi_perso, weekend, achats, activites, routines) | ✅ |
| maison | 5 (hub, jardin, entretien, depenses, charges) | ✅ |
| jeux | 2 (paris, loto) | ✅ |
| planning | 3 (calendrier, timeline, templates) | ✅ |
| parametres | 1 | ✅ |
| utilitaires | 6 (barcode, rapports, scan_factures, recherche_produits, notifications, chat_ia) | ✅ |
| **TOTAL** | **31** | **100% conforme** |

---

## 4. Connections inter-modules

| Connexion | Implémentée | Méthode |
|-----------|-------------|---------|
| **batch_cooking → courses** | ✅ | `SK.COURSES_DEPUIS_BATCH` → session_state |
| **planificateur → courses** | ✅ | `SK.COURSES_DEPUIS_PLANNING` → session_state |
| **scan_factures → charges** | ✅ | `KeyNamespace("charges")` → session_state factures |
| **calendrier → courses/batch/planning** | ✅ | `naviguer_vers()` vers cuisine.* |
| **accueil → cuisine (×4)** | ✅ | `naviguer_vers()` vers recettes, courses, inventaire, planning |
| **maison hub → sous-modules** | ✅ | `naviguer_vers()` vers jardin, entretien, charges, depenses |
| **batch_cooking → planificateur** | ✅ | `naviguer("cuisine.planificateur_repas")` |
| **courses → planificateur** | ✅ | `naviguer("cuisine.planning_semaine")` |

---

## 5. WIP / TODO / FIXME

| Fichier | Ligne | Contenu |
|---------|-------|---------|
| `maison/jardin/styles.py` | 12 | `# TODO: Migrate callers to use injecter_css_jardin() directly` |

**Total**: 1 seul TODO trouvé — codebase très propre.

---

## 6. MODULE_REGISTRY — Vérification complète

| Clé registre | Path cible | `app()` trouvé | Statut |
|-------------|-----------|----------------|--------|
| `accueil` | `src.modules.accueil` | ✅ | ✅ |
| `planning.calendrier` | `src.modules.planning.calendrier` | ✅ | ✅ |
| `planning.templates_ui` | `src.modules.planning.templates_ui` | ✅ | ✅ |
| `planning.timeline_ui` | `src.modules.planning.timeline_ui` | ✅ | ✅ |
| `cuisine.recettes` | `src.modules.cuisine.recettes` | ✅ | ✅ |
| `cuisine.inventaire` | `src.modules.cuisine.inventaire` | ✅ | ✅ |
| `cuisine.planificateur_repas` | `src.modules.cuisine.planificateur_repas` | ✅ | ✅ |
| `cuisine.batch_cooking_detaille` | `src.modules.cuisine.batch_cooking_detaille` | ✅ | ✅ |
| `cuisine.courses` | `src.modules.cuisine.courses` | ✅ | ✅ |
| `barcode` | `src.modules.utilitaires.barcode` | ✅ | ✅ |
| `rapports` | `src.modules.utilitaires.rapports` | ✅ | ✅ |
| `famille.hub` | `src.modules.famille.hub_famille` | ✅ | ✅ |
| `famille.jules` | `src.modules.famille.jules` | ✅ | ✅ |
| `famille.jules_planning` | `src.modules.famille.jules_planning` | ✅ | ✅ |
| `famille.suivi_perso` | `src.modules.famille.suivi_perso` | ✅ | ✅ |
| `famille.weekend` | `src.modules.famille.weekend` | ✅ | ✅ |
| `famille.achats_famille` | `src.modules.famille.achats_famille` | ✅ | ✅ |
| `famille.activites` | `src.modules.famille.activites` | ✅ | ✅ |
| `famille.routines` | `src.modules.famille.routines` | ✅ | ✅ |
| `maison.hub` | `src.modules.maison.hub` | ✅ | ✅ |
| `maison.jardin` | `src.modules.maison.jardin` | ✅ | ✅ |
| `maison.entretien` | `src.modules.maison.entretien` | ✅ | ✅ |
| `maison.depenses` | `src.modules.maison.depenses` | ✅ | ✅ |
| `maison.charges` | `src.modules.maison.charges` | ✅ | ✅ |
| `jeux.paris` | `src.modules.jeux.paris` | ✅ | ✅ |
| `jeux.loto` | `src.modules.jeux.loto` | ✅ | ✅ |
| `scan_factures` | `src.modules.utilitaires.scan_factures` | ✅ | ✅ |
| `recherche_produits` | `src.modules.utilitaires.recherche_produits` | ✅ | ✅ |
| `parametres` | `src.modules.parametres` | ✅ | ✅ |
| `notifications_push` | `src.modules.utilitaires.notifications_push` | ✅ | ✅ |
| `design_system` | `src.modules.design_system` | ✅ | ✅ |

**31/31 entrées — 100% concordance app() ↔ registre**

### Modules avec `app()` NON enregistrés dans le registre

| Module | Fichier |
|--------|---------|
| `chat_ia` | `utilitaires/chat_ia.py` — possède `app()` mais **absent du MODULE_REGISTRY** |

⚠️ **`chat_ia` n'est pas enregistré**. Il est probablement appelé via `afficher_chat_contextuel()` depuis d'autres modules, pas en tant que module autonome du routeur — mais si on veut le rendre navigable indépendamment, il faut l'ajouter.

---

## 7. Lazy loading — Imports inside app()

Les imports lourds sont effectués **à l'intérieur des fonctions `app()`** dans tous les modules, conformément au pattern de chargement différé. Exemples vérifiés :
- `cuisine/recettes/__init__.py` : imports de sous-modules dans les branches conditionnelles
- `famille/hub_famille.py` : imports conditionnels dans chaque branche d'onglet
- `cuisine/inventaire/__init__.py` : imports des sous-modules dans les onglets

**Conformité**: ✅ Respecté globalement. Seuls les imports légers (`streamlit`, `error_boundary`, `profiler_rerun`, `KeyNamespace`, `tabs_with_url`) sont au niveau module — ce qui est acceptable.

---

## 8. Résumé des lacunes identifiées

| # | Problème | Sévérité | Module(s) concerné(s) |
|---|----------|----------|----------------------|
| 1 | `chat_ia` non enregistré dans MODULE_REGISTRY | ⚠️ Minor | utilitaires |
| 2 | `KeyNamespace` absent dans planning/ | 🔵 Info | planning |
| 3 | `@cached_fragment` non adopté dans cuisine (51 fichiers, 0 usages) | 🔵 Info | cuisine |
| 4 | `tabs_with_url()` absent dans maison/ (5 sous-modules avec onglets) | 🟡 Medium | maison |
| 5 | `tabs_with_url()` absent dans parametres/ | 🔵 Info | parametres |
| 6 | Chat IA contextuel absent dans maison/, jeux/, parametres/ | 🔵 Info | 3 modules |
| 7 | `@lazy` très peu adopté (3 usages sur 187 fichiers) | 🔵 Info | global |
| 8 | 1 TODO résiduel dans `jardin/styles.py` | 🔵 Info | maison |

---

## 9. Score global

| Critère | Score | Poids | Pondéré |
|---------|-------|-------|---------|
| `app()` conformité | 10/10 | ×3 | 30 |
| MODULE_REGISTRY couverture | 9.5/10 | ×3 | 28.5 |
| `error_boundary` adoption | 10/10 | ×2 | 20 |
| `@profiler_rerun` adoption | 10/10 | ×2 | 20 |
| `KeyNamespace` adoption | 7.5/10 | ×1.5 | 11.25 |
| `tabs_with_url()` deep linking | 6/10 | ×1 | 6 |
| `@cached_fragment` adoption | 5/10 | ×1 | 5 |
| `@auto_refresh` usage | 5/10 | ×0.5 | 2.5 |
| `@lazy` decorator | 4/10 | ×0.5 | 2 |
| Chat IA contextuel | 5/10 | ×1 | 5 |
| Inter-module connections | 9/10 | ×1.5 | 13.5 |
| Lazy loading pattern | 9/10 | ×1 | 9 |
| Code cleanliness (TODO/WIP) | 10/10 | ×0.5 | 5 |

**Total pondéré**: 158.75 / 190 = **83.5%**

### **Score final: 8.4 / 10**

**Points forts**:
- 100% conformité `app()` + MODULE_REGISTRY
- 100% adoption `error_boundary` + `@profiler_rerun` (patterns critiques)
- Excellentes connexions inter-modules (batch→courses, scan→charges, planning→cuisine)
- Codebase très propre (1 seul TODO)

**Axes d'amélioration**:
- Adopter `tabs_with_url()` dans maison/ et parametres/ pour le deep linking
- Étendre `@cached_fragment` à cuisine/ (calculs lourds de planification)
- Intégrer le chat IA contextuel dans maison/ et jeux/
- Explorer `@lazy` pour les onglets rarement consultés (export, statistiques avancées)

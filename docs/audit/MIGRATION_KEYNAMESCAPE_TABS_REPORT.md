# Migration Report: KeyNamespace & tabs_with_url

## 1. API Reference

### KeyNamespace (`src/ui/keys.py`)

```python
class KeyNamespace:
    """Générateur de clés scopé avec préfixe automatique."""

    def __init__(self, prefix: str, *, register: bool = True) -> None: ...

    def __call__(self, name: str, *suffixes: Any) -> str:
        """Génère une clé: "{prefix}__{name}" ou "{prefix}__{name}_{suffix}" """

    def child(self, sub_prefix: str) -> KeyNamespace:
        """Crée un sous-namespace: "parent__child__name" """

    @property
    def prefix(self) -> str: ...
```

**Import:** `from src.ui.keys import KeyNamespace`

**Usage:**

```python
_keys = KeyNamespace("recettes")

st.text_input("Nom", key=_keys("nom"))           # → "recettes__nom"
st.button("Del", key=_keys("del", item.id))       # → "recettes__del_42"
st.session_state[_keys("detail_id")] = None        # scoped session_state key
```

---

### tabs_with_url (`src/ui/state/url.py`)

```python
def tabs_with_url(
    tabs: list[str],
    param: str = "tab",
    default: int = 0,
) -> int:
    """Index de l'onglet sélectionné, synchronisé avec URL query param."""
```

**Import:** `from src.ui.state.url import tabs_with_url`

**Usage:**

```python
TAB_LABELS = ["📊 Dashboard", "📄 Factures", "📈 Analyse"]
tab_index = tabs_with_url(TAB_LABELS, param="tab")
tab1, tab2, tab3 = st.tabs(TAB_LABELS)
```

---

## 2. Reference Pattern: `src/modules/maison/charges/__init__.py`

```python
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

_keys = KeyNamespace("charges")

def _charger_donnees_charges():
    if _keys("factures") not in st.session_state or ...:
        st.session_state[_keys("factures")] = charger_factures()
    return st.session_state[_keys("factures")]

def app():
    TAB_LABELS = ["📊 Dashboard", "📄 Factures", ...]
    tabs_with_url(TAB_LABELS, param="tab")        # ← sync URL BEFORE st.tabs
    tab1, tab2, ... = st.tabs(TAB_LABELS)          # ← then create tabs
```

---

## 3. Files Already Correctly Using BOTH

These files import both `KeyNamespace` AND `tabs_with_url`:

| File                                                  | KeyNamespace prefix                             |
| ----------------------------------------------------- | ----------------------------------------------- |
| `src/modules/maison/charges/__init__.py`              | `"charges"`                                     |
| `src/modules/maison/depenses/__init__.py`             | `"depenses"`                                    |
| `src/modules/maison/meubles/__init__.py`              | `"meubles"`                                     |
| `src/modules/maison/projets/__init__.py`              | `"projets"`                                     |
| `src/modules/maison/jardin/__init__.py`               | `"jardin"`                                      |
| `src/modules/maison/eco_tips/__init__.py`             | `"eco_tips"`                                    |
| `src/modules/maison/entretien/__init__.py`            | `"entretien"`                                   |
| `src/modules/maison/energie/__init__.py`              | `"energie"`                                     |
| `src/modules/planning/calendrier/__init__.py`         | `"calendrier"`                                  |
| `src/modules/jeux/paris/__init__.py`                  | `"paris"`                                       |
| `src/modules/jeux/loto/__init__.py`                   | `"loto"`                                        |
| `src/modules/famille/routines.py`                     | `"routines"`                                    |
| `src/modules/famille/activites.py`                    | `"activites"`                                   |
| `src/modules/famille/achats_famille/__init__.py`      | `"achats_famille"`                              |
| `src/modules/famille/jules/__init__.py`               | (tabs_with_url only, no \_keys usage for state) |
| `src/modules/famille/suivi_perso/__init__.py`         | (tabs_with_url only)                            |
| `src/modules/famille/weekend/__init__.py`             | (tabs_with_url only)                            |
| `src/modules/cuisine/recettes/__init__.py`            | `"recettes"`                                    |
| `src/modules/cuisine/courses/__init__.py`             | `"courses"`                                     |
| `src/modules/cuisine/inventaire/__init__.py`          | `"inventaire"`                                  |
| `src/modules/cuisine/planificateur_repas/__init__.py` | `"planificateur_repas"`                         |
| `src/modules/cuisine/batch_cooking_detaille/app.py`   | `"batch_cooking"`                               |
| `src/modules/design_system.py`                        | `"design_system"`                               |

---

## 4. Files Needing `tabs_with_url` Migration

These files call `st.tabs(` **without** a preceding `tabs_with_url()` call:

### Primary tabs (module-level — HIGH priority)

| File                                            | Line | Tab labels                                                                |
| ----------------------------------------------- | ---- | ------------------------------------------------------------------------- |
| `src/modules/utilitaires/scan_factures.py`      | L166 | `["📷 Scanner", "📋 Historique"]`                                         |
| `src/modules/utilitaires/recherche_produits.py` | L159 | `["🔍 Code-barre", "🔎 Recherche", "⭐ Favoris"]`                         |
| `src/modules/utilitaires/rapports.py`           | L49  | `["📦 Stocks", "💡 Budget", "🎯 Gaspillage", "🗑️ Historique"]`            |
| `src/modules/utilitaires/notifications_push.py` | L427 | `["📷 S'abonner", "⚙️ Configuration", "⏰ Tâches", "🧪 Test", "❓ Aide"]` |
| `src/modules/utilitaires/barcode/app.py`        | L51  | 5 tabs (barcode scanning)                                                 |
| `src/modules/planning/templates_ui.py`          | L36  | `["📋 Liste", "➕ Créer", "📅 Appliquer"]`                                |
| `src/modules/famille/jules_planning.py`         | L383 | `["🌟 Aujourd'hui", "📅 Semaine", "📊 Bilan", "📚 Catalogue"]`            |
| `src/modules/cuisine/recettes_import.py`        | L21  | 3 tabs (import methods)                                                   |

### Sub-tabs (nested inside another tab — MEDIUM priority)

| File                                                | Line       | Context                                    |
| --------------------------------------------------- | ---------- | ------------------------------------------ |
| `src/modules/jeux/paris/gestion.py`                 | L23        | 4 sub-tabs in gestion                      |
| `src/modules/cuisine/courses/outils.py`             | L20        | 4 sub-tabs (barcode, share, export, stats) |
| `src/modules/cuisine/courses/modeles.py`            | L29        | 2 sub-tabs (mes modèles, nouveau)          |
| `src/modules/cuisine/courses/suggestions_ia.py`     | L29        | 2 sub-tabs (inventaire, recettes)          |
| `src/modules/cuisine/inventaire/notifications.py`   | L87        | 2 sub-tabs                                 |
| `src/modules/cuisine/inventaire/photos.py`          | L49        | 2 sub-tabs                                 |
| `src/modules/cuisine/inventaire/predictions.py`     | L89        | 4 sub-tabs                                 |
| `src/modules/cuisine/inventaire/tools.py`           | L18, L80   | 2+2 sub-tabs                               |
| `src/modules/cuisine/inventaire/categories.py`      | L39        | dynamic category tabs                      |
| `src/modules/maison/jardin/onglets_stats.py`        | L148       | 3 sub-tabs                                 |
| `src/modules/maison/energie/__init__.py`            | L401       | 2 sub-tabs (inside visualisation)          |
| `src/modules/maison/entretien/onglets_analytics.py` | L185       | 3 sub-tabs                                 |
| `src/modules/maison/depenses/components.py`         | L90        | 4 sub-tabs                                 |
| `src/modules/maison/charges/onglets.py`             | L307       | 2 sub-tabs                                 |
| `src/modules/famille/jules_planning.py`             | L254, L303 | sub-tabs (jours, bibliothèque)             |
| `src/modules/famille/jules/components.py`           | L117       | 4 sub-tabs (vêtements, jouets, etc.)       |
| `src/modules/famille/suivi_perso/alimentation.py`   | L19        | 2 sub-tabs                                 |
| `src/modules/cuisine/recettes/detail.py`            | L234       | dynamic version tabs                       |

---

## 5. Files Needing `KeyNamespace` Migration

### Category A: Raw string literal keys (HIGHEST priority)

| File                                                     | Lines               | Raw keys used                                       |
| -------------------------------------------------------- | ------------------- | --------------------------------------------------- |
| `src/modules/parametres/foyer.py`                        | L91, L94, L97, L175 | `"foyer_config"`                                    |
| `src/modules/parametres/affichage.py`                    | L48                 | `"display_mode_selection"`                          |
| `src/modules/parametres/ia.py`                           | L15, L62            | `"show_ia_details"`, `st.session_state.rate_limit`  |
| `src/modules/cuisine/recettes_import.py`                 | L52, L160           | `"extracted_recipe"`, `"last_imported_recipe_name"` |
| `src/modules/cuisine/recettes/ajout.py`                  | L23, L25            | `"form_num_ingredients"`, `"form_num_etapes"`       |
| `src/modules/cuisine/planificateur_repas/preferences.py` | L131, L151          | `"recipe_feedbacks"`                                |

### Category B: Raw f-string keys (HIGH priority)

| File                                                    | Lines            | F-string pattern                                                                                        |
| ------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------- |
| `src/modules/cuisine/planificateur_repas/components.py` | L201, L222, L234 | `f"show_alternatives_{key_prefix}"`, `f"add_repas_{key_prefix}_midi"`, `f"add_repas_{key_prefix}_soir"` |
| `src/modules/cuisine/recettes/generation_image.py`      | L60, L80         | `f"generated_image_{recette.id}"`                                                                       |
| `src/modules/utilitaires/barcode/detection.py`          | L185, L202, L275 | `f"{key}_detected"`                                                                                     |
| `src/modules/jeux/utils.py`                             | L214             | `f"{cle}_updated"`                                                                                      |

### Category C: Dot-notation raw keys (HIGH priority)

| File                                            | Lines                                                                     | Dot-notation keys                                                                                                                                |
| ----------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/modules/utilitaires/rapports.py`           | L31-32, L103, L107, L202, L244, L248, L339, L381, L385, L473              | `.rapports_service`, `.preview_stocks`, `.download_stocks`, `.preview_budget`, `.download_budget`, `.preview_gaspillage`, `.download_gaspillage` |
| `src/modules/utilitaires/barcode/app.py`        | L19-21                                                                    | `.barcode_service`                                                                                                                               |
| `src/modules/planning/calendrier/__init__.py`   | L77, L81, L84, L185                                                       | `.cal_semaine_debut`                                                                                                                             |
| `src/modules/planning/calendrier/components.py` | L47, L53-54, L59, L70-71, L77, L94, L345, L446, L478                      | `.cal_semaine_debut`, `.ajouter_event_date`                                                                                                      |
| `src/modules/maison/jardin/__init__.py`         | L48-53                                                                    | `.mes_plantes_jardin`, `.recoltes_jardin`, `._jardin_reload`                                                                                     |
| `src/modules/maison/jardin/onglets_culture.py`  | L35, L62, L66, L102-105, L110-111, L150-151, L160-161, L169-170, L217-218 | `.jardin_mode_ajout`, `.jardin_plante_selectionnee`, `.mes_plantes_jardin`, `.recoltes_jardin`, `._jardin_reload`                                |
| `src/modules/maison/jardin/onglets_stats.py`    | L74-76                                                                    | `.historique_jardin`                                                                                                                             |
| `src/modules/maison/jardin/onglets_export.py`   | L26                                                                       | `"jardin_export_ready"`                                                                                                                          |
| `src/modules/maison/entretien/__init__.py`      | L42-49                                                                    | `.mes_objets_entretien`, `.historique_entretien`, `._entretien_reload`                                                                           |
| `src/modules/maison/entretien/onglets_core.py`  | L95-96, L110, L170-172, L177, L217-218, L274-275, L333-334                | `.historique_entretien`, `.entretien_mode_ajout`, `.mes_objets_entretien`, `._entretien_reload`                                                  |
| `src/modules/maison/charges/ui.py`              | L113                                                                      | `.badges_vus`                                                                                                                                    |
| `src/modules/maison/charges/onglets.py`         | L49, L165, L239                                                           | `.prev_eco_score`, `._charges_reload`                                                                                                            |
| `src/modules/maison/charges/__init__.py`        | L32, L34                                                                  | `"_charges_reload"`, `._charges_reload`                                                                                                          |
| `src/modules/parametres/foyer.py`               | L94, L175                                                                 | `.foyer_config`                                                                                                                                  |

### Category D: Files with KeyNamespace BUT also using raw string keys (MIXED — need cleanup)

| File                                                  | Has `_keys = KeyNamespace(...)` | Raw keys still present                                                           |
| ----------------------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------- |
| `src/modules/famille/activites.py`                    | `"activites"` (L34)             | `"activite_prefill_titre"`, `"activite_prefill_type"` at L238-239, L268-269      |
| `src/modules/cuisine/recettes/liste.py`               | `"recettes_liste"` (L16)        | `"recettes_page"`, `"recettes_page_size"` at L29, L32                            |
| `src/modules/cuisine/courses/__init__.py`             | `"courses"` (L40)               | `"courses_refresh"`, `"new_article_mode"` at L50, L52                            |
| `src/modules/cuisine/planificateur_repas/__init__.py` | `"planificateur_repas"` (L36)   | `"planning_data"`, `"planning_date_debut"` at L96, L99                           |
| `src/modules/cuisine/batch_cooking_detaille/app.py`   | `"batch_cooking"` (L32)         | `"batch_date"` at L240                                                           |
| `src/modules/planning/calendrier/__init__.py`         | `"calendrier"` (L59)            | `.cal_semaine_debut` at L77, L81, L84, L185                                      |
| `src/modules/maison/jardin/__init__.py`               | `"jardin"` (L41)                | `.mes_plantes_jardin`, `.recoltes_jardin`, `._jardin_reload` at L48-53           |
| `src/modules/maison/entretien/__init__.py`            | `"entretien"` (L35)             | `.mes_objets_entretien`, `.historique_entretien`, `._entretien_reload` at L42-49 |
| `src/modules/maison/charges/__init__.py`              | `"charges"` (L27)               | `"_charges_reload"`, `._charges_reload` at L32, L34                              |
| `src/modules/maison/charges/onglets.py`               | `"charges"` (L16)               | `.prev_eco_score`, `._charges_reload` at L49, L165, L239                         |

### Category E: Files using only SK constants (lower priority — formalized but not scoped)

These use `from src.core.session_keys import SK` which provides centralized string constants, but not KeyNamespace scoping. Migration is optional but recommended for consistency:

| File                                                  | SK keys used                                                                                                                            |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `src/modules/utilitaires/recherche_produits.py`       | `SK.PRODUITS_FAVORIS`                                                                                                                   |
| `src/modules/utilitaires/scan_factures.py`            | `SK.HISTORIQUE_FACTURES`                                                                                                                |
| `src/modules/utilitaires/notifications_push.py`       | `SK.NOTIF_CONFIG`, `SK.NOTIF_DEMO_HISTORY`, `SK.NOTIF_MODE_DEMO`                                                                        |
| `src/modules/utilitaires/barcode/scanner.py`          | `SK.LAST_WEBRTC_SCAN`                                                                                                                   |
| `src/modules/utilitaires/rapports.py`                 | `SK.PREVIEW_STOCKS`, `SK.DOWNLOAD_STOCKS`, `SK.PREVIEW_BUDGET`, `SK.DOWNLOAD_BUDGET`, `SK.PREVIEW_GASPILLAGE`, `SK.DOWNLOAD_GASPILLAGE` |
| `src/modules/planning/calendrier/components.py`       | `SK.SHOW_PRINT_MODAL`                                                                                                                   |
| `src/modules/maison/jardin/onglets_culture.py`        | `SK.JARDIN_MODE_AJOUT`, `SK.JARDIN_PLANTE_SELECTIONNEE`                                                                                 |
| `src/modules/maison/entretien/onglets_core.py`        | `SK.ENTRETIEN_MODE_AJOUT` (implied)                                                                                                     |
| `src/modules/maison/hub/data.py`                      | `SK.MES_PLANTES_JARDIN`, `SK.RECOLTES_JARDIN`, `SK.MES_OBJETS_ENTRETIEN`, `SK.HISTORIQUE_ENTRETIEN`, `SK.MES_PLANTES`                   |
| `src/modules/maison/depenses/cards.py`                | `SK.EDIT_DEPENSE_ID`                                                                                                                    |
| `src/modules/maison/depenses/__init__.py`             | `SK.EDIT_DEPENSE_ID`                                                                                                                    |
| `src/modules/maison/charges/ui.py`                    | `SK.BADGES_VUS`                                                                                                                         |
| `src/modules/maison/charges/onglets.py`               | `SK.PREV_ECO_SCORE`                                                                                                                     |
| `src/modules/famille/routines.py`                     | `SK.ADDING_TASK_TO`, `SK.RAPPELS_IA`                                                                                                    |
| `src/modules/famille/jules/components.py`             | `SK.JULES_SHOW_AI_ACTIVITIES`, `SK.JULES_CONSEIL_THEME`                                                                                 |
| `src/modules/famille/suivi_perso/settings.py`         | `SK.GARMIN_AUTH_USER`, `SK.GARMIN_REQUEST_TOKEN`                                                                                        |
| `src/modules/famille/suivi_perso/utils.py`            | `SK.SUIVI_USER`                                                                                                                         |
| `src/modules/famille/jules_planning.py`               | `SK.JULES_ACTIVITES_FAITES`                                                                                                             |
| `src/modules/famille/weekend/components.py`           | `SK.WEEKEND_ADD_DATE`                                                                                                                   |
| `src/modules/famille/hub_famille.py`                  | `SK.FAMILLE_PAGE`, `SK.SUIVI_USER`                                                                                                      |
| `src/modules/cuisine/planificateur_repas/__init__.py` | `SK.PLANNING_STOCK_CONTEXT`, `SK.COURSES_DEPUIS_PLANNING`                                                                               |
| `src/modules/cuisine/courses/planning.py`             | `SK.COURSES_PLANNING_RESULTAT`                                                                                                          |
| `src/modules/cuisine/batch_cooking_detaille/app.py`   | `SK.COURSES_DEPUIS_BATCH`                                                                                                               |

---

## 6. Summary Statistics

### tabs_with_url

| Status                                     | Count                       |
| ------------------------------------------ | --------------------------- |
| Already migrated (primary tabs)            | 23 files                    |
| **Needs migration (primary tabs)**         | **8 files**                 |
| Needs migration (sub-tabs, lower priority) | 18 occurrences in ~15 files |

### KeyNamespace

| Status                                             | Count        |
| -------------------------------------------------- | ------------ |
| Already using KeyNamespace correctly               | 23+ files    |
| **Cat A: Raw string keys (no KeyNamespace)**       | **6 files**  |
| **Cat B: Raw f-string keys (no KeyNamespace)**     | **4 files**  |
| **Cat C: Dot-notation raw keys (no KeyNamespace)** | **14 files** |
| **Cat D: Has KeyNamespace but mixed raw keys**     | **10 files** |
| Cat E: Uses SK only (lower priority)               | 23 files     |

### Total files needing work

- **tabs_with_url migration:** 8 primary + ~15 sub-tab files
- **KeyNamespace migration:** 34 files (Categories A-D)
- **SK→KeyNamespace migration:** 23 files (Category E, optional)

---

## 7. Correct Import Statements

```python
# KeyNamespace only
from src.ui.keys import KeyNamespace
_keys = KeyNamespace("module_name")

# tabs_with_url only
from src.ui.state.url import tabs_with_url

# Both (recommended for any module with tabs + state)
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url
_keys = KeyNamespace("module_name")
```

## 8. Excluded from Analysis

- `src/modules/_framework/` — infrastructure code (`state_manager.py`, `fragments.py`, `base_module.py`) manages session_state generically, not module-specific
- `src/modules/utilitaires/chat_ia.py` — already uses KeyNamespace (`"chat_ia"`)
- `src/modules/accueil/` submodules — already use KeyNamespace (`"accueil"`, `"resume_hebdo"`)

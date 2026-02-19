# 🎨 Module UI - Architecture

## Vue d'ensemble

Module d'interface utilisateur basé sur **Atomic Design** pour l'application Streamlit.

```
src/ui/
├── components/     # Widgets atomiques réutilisables
├── core/           # Classes de base (formulaires, CRUD, I/O)
├── feedback/       # Retour utilisateur (spinners, toasts)
├── integrations/   # Services tiers (Google Calendar)
├── layout/         # Mise en page (header, sidebar, footer)
├── tablet/         # Mode tablette/cuisine
└── views/          # Vues extraites des services
```

## 📦 Packages

### `components/` - Widgets Atomiques

| Fichier             | Description                                                                     |
| ------------------- | ------------------------------------------------------------------------------- |
| `atoms.py`          | Éléments de base: `badge`, `etat_vide`, `carte_metrique`, `notification`        |
| `forms.py`          | Champs de formulaire: `champ_formulaire`, `panneau_filtres`                     |
| `data.py`           | Affichage de données: `tableau_donnees`, `pagination`, `barre_recherche`        |
| `charts.py`         | Graphiques Plotly: `graphique_ligne`, `graphique_barres`, `graphique_camembert` |
| `dynamic.py`        | Composants dynamiques: `Modale`, `ListeDynamique`, `AssistantEtapes`            |
| `alertes.py`        | Alertes contextuelles: `alerte_stock`, `alerte_peremption`                      |
| `layouts.py`        | Mise en page: `carte_item`, `grille_cartes`, `accordeon`                        |
| `metrics.py`        | Métriques: `ligne_metriques`, `jauge_progression`                               |
| `system.py`         | Système: `indicateur_sante`, `info_version`                                     |
| `camera_scanner.py` | Scanner codes-barres (pyzbar/zxing)                                             |

### `core/` - Classes de Base

| Classe                   | Description                          | Alias français                                      |
| ------------------------ | ------------------------------------ | --------------------------------------------------- |
| `ConstructeurFormulaire` | Générateur de formulaires dynamiques | `ajouter_texte()`, `ajouter_nombre()`, `afficher()` |
| `ModuleUIBase`           | Renderer CRUD universel              | `afficher()`                                        |
| `ServiceIOBase`          | Import/Export CSV/JSON               | `vers_csv()`, `depuis_json()`                       |
| `ConfigurationModule`    | Configuration dataclass pour modules |

### `feedback/` - Retour Utilisateur

- `spinners.py`: `smart_spinner()` avec messages contextuels
- `toasts.py`: `afficher_succes()`, `afficher_erreur()`, `afficher_warning()`
- `progress.py`: `barre_progression()`, `indicateur_chargement()`

### `tablet/` - Mode Tablette

Mode optimisé pour tablettes en cuisine:

- `ModeTablette`: Enum des modes (NORMAL, TABLETTE, CUISINE)
- `appliquer_mode_tablette()`, `fermer_mode_tablette()`
- `afficher_vue_recette_cuisine()`: Vue recette pas-à-pas
- Widgets tactiles: `bouton_tablette()`, `grille_selection_tablette()`

### `views/` - Vues Extraites

Vues UI extraites des services pour séparation des responsabilités:

- `authentification.py`: `afficher_formulaire_connexion()`, `require_authenticated()`
- `meteo.py`: `afficher_meteo_jardin()`
- `pwa.py`: `afficher_invite_installation_pwa()`, `injecter_meta_pwa()`
- `notifications.py`: `afficher_preferences_notification()`
- `historique.py`: `afficher_timeline_activite()`
- `synchronisation.py`: `afficher_statut_synchronisation()`

### `integrations/` - Services Tiers

- `google_calendar.py`: Sync Google Calendar
  - `afficher_config_google_calendar()`
  - `afficher_statut_synchronisation()`
  - `afficher_bouton_sync_rapide()`

## 🔧 Utilisation

### Import centralisé

```python
# Tout depuis src.ui
from src.ui import (
    badge,
    etat_vide,
    ConstructeurFormulaire,
    afficher_succes,
    ModeTablette,
)
```

### Formulaire dynamique

```python
from src.ui.core import ConstructeurFormulaire

form = ConstructeurFormulaire("recette_form", title="Nouvelle Recette")
form.ajouter_texte("nom", "Nom", required=True)
form.ajouter_nombre("temps", "Temps (min)", min_value=1)
form.ajouter_selection("difficulte", "Difficulté", ["Facile", "Moyen", "Difficile"])

if form.afficher():
    data = form.obtenir_donnees()
    # Traiter les données...
```

### Module CRUD

```python
from src.ui.core import ConfigurationModule, creer_module_ui

config = ConfigurationModule(
    name="recettes",
    title="Mes Recettes",
    icon="🍽️",
    service=recette_service,
    search_fields=["nom", "description"],
)

module = creer_module_ui(config)
module.afficher()  # Génère automatiquement liste, recherche, pagination, actions
```

### Composants dynamiques

```python
from src.ui.components.dynamic import Modale, AssistantEtapes

# Modal de confirmation
modal = Modale("supprimer")
if modal.est_affichee():
    st.warning("Confirmer la suppression ?")
    if modal.confirmer():
        supprimer_item()
        modal.fermer()
    modal.annuler()

# Assistant multi-étapes
wizard = AssistantEtapes("import", ["Upload", "Validation", "Import"])
etape = wizard.afficher()
if etape == 0:
    # Contenu étape 1...
    if st.button("Suivant"):
        wizard.suivant()
```

## 🧪 Tests

```bash
# Tous les tests UI
pytest tests/ui/ -v

# Tests d'import uniquement
pytest tests/ui/test_imports_ui.py -v

# Tests mode tablette
pytest tests/ui/test_tablet_mode.py -v
```

## 📋 Conventions

1. **Nommage français** pour toutes les fonctions/classes publiques
2. **Docstrings** en français
3. **Point d'entrée unique**: `src.ui` re-exporte tous les symboles publics

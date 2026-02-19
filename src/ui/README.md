# 🎨 Module UI - Architecture

## Vue d'ensemble

Module d'interface utilisateur basé sur **Atomic Design** pour l'application Streamlit.

```
src/ui/
├── components/     # Widgets atomiques réutilisables
├── feedback/       # Retour utilisateur (spinners, toasts)
├── integrations/   # Services tiers (Google Calendar)
├── layout/         # Mise en page (header, sidebar, footer)
├── tablet/         # Mode tablette/cuisine
└── views/          # Vues extraites des services
```

## 📦 Packages

### `components/` - Widgets Atomiques

| Fichier      | Composants                                                                                |
| ------------ | ----------------------------------------------------------------------------------------- |
| `atoms.py`   | `badge`, `etat_vide`, `carte_metrique`, `notification`, `separateur`, `boite_info`        |
| `forms.py`   | `champ_formulaire`, `barre_recherche`, `panneau_filtres`, `filtres_rapides`               |
| `data.py`    | `tableau_donnees`, `pagination`, `boutons_export`, `ligne_metriques`, `barre_progression` |
| `charts.py`  | `graphique_repartition_repas`, `graphique_inventaire_categories`                          |
| `dynamic.py` | `Modale` (avec aliases français/anglais)                                                  |
| `alertes.py` | `alerte_stock`                                                                            |
| `layouts.py` | `carte_item`, `disposition_grille`                                                        |
| `metrics.py` | `carte_metrique_avancee`, `widget_jules_apercu`, `widget_meteo_jour`                      |
| `system.py`  | `indicateur_sante_systeme`, `afficher_sante_systeme`, `afficher_timeline_activites`       |

### `feedback/` - Retour Utilisateur

| Fichier       | Composants                                                                      |
| ------------- | ------------------------------------------------------------------------------- |
| `spinners.py` | `spinner_intelligent`, `indicateur_chargement`, `chargeur_squelette`            |
| `toasts.py`   | `afficher_succes`, `afficher_erreur`, `afficher_avertissement`, `afficher_info` |
| `progress.py` | `SuiviProgression`, `EtatChargement`                                            |

### `tablet/` - Mode Tablette

Mode optimisé pour tablettes en cuisine:

- `ModeTablette`: Enum des modes (NORMAL, TABLETTE, CUISINE)
- `appliquer_mode_tablette()`, `fermer_mode_tablette()`
- `afficher_vue_recette_cuisine()`: Vue recette pas-à-pas
- Widgets tactiles: `bouton_tablette()`, `grille_selection_tablette()`

### `views/` - Vues Extraites

| Fichier               | Composants                                                               |
| --------------------- | ------------------------------------------------------------------------ |
| `authentification.py` | `afficher_formulaire_connexion`, `require_authenticated`, `require_role` |
| `meteo.py`            | `afficher_meteo_jardin`                                                  |
| `synchronisation.py`  | `afficher_statut_synchronisation`, `afficher_indicateur_presence`        |
| `notifications.py`    | `afficher_preferences_notification`                                      |
| `historique.py`       | `afficher_timeline_activite`                                             |
| `jeux.py`             | `afficher_badge_notifications_jeux`, `afficher_notification_jeux`        |

### `integrations/` - Services Tiers

| Fichier              | Composants                                                                                      |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| `google_calendar.py` | `afficher_config_google_calendar`, `afficher_statut_sync_google`, `afficher_bouton_sync_rapide` |

## 🔧 Utilisation

### Import centralisé

```python
from src.ui import (
    badge,
    etat_vide,
    afficher_succes,
    ModeTablette,
    Modale,
)
```

### Modale de confirmation

```python
from src.ui import Modale

modal = Modale("supprimer")
if modal.est_affichee():
    st.warning("Confirmer la suppression ?")
    if modal.confirmer():
        supprimer_item()
        modal.fermer()
    modal.annuler()
```

### État vide standardisé

```python
from src.ui import etat_vide

# Au lieu de st.info("Aucun résultat")
etat_vide("Aucun résultat", icone="🔍", conseil="Essayez une autre recherche")
```

## 🧪 Tests

```bash
pytest tests/ui/ -v
```

## 📋 Conventions

1. **Nommage français** pour toutes les fonctions/classes publiques (`afficher_*`, `obtenir_*`)
2. **Docstrings** en français avec Args et Example
3. **Point d'entrée unique**: `src.ui` re-exporte tous les symboles publics
4. **Décorateurs Streamlit**: Utiliser `@st.cache_data(ttl=...)` pour les données cachées

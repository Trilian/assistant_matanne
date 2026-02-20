# 🎨 Module UI - Architecture Design System 2.0

## Vue d'ensemble

Module d'interface utilisateur basé sur **Atomic Design** pour l'application Streamlit.
Design system professionnel avec tokens sémantiques, accessibilité WCAG, animations
centralisées et hooks réutilisables.

```
src/ui/
├── components/     # Widgets atomiques réutilisables
├── feedback/       # Retour utilisateur (spinners, toasts)
├── integrations/   # Services tiers (Google Calendar)
├── layout/         # Mise en page (header, sidebar, footer)
├── tablet/         # Mode tablette/cuisine
├── views/          # Vues extraites des services
├── a11y.py         # Accessibilité (ARIA, contraste WCAG, sr-only)
├── animations.py   # Système d'animation centralisé (@keyframes)
├── hooks.py        # Hooks Streamlit (use_pagination, use_recherche…)
├── tokens.py       # Design tokens bruts (Couleur, Espacement…)
├── tokens_semantic.py # Tokens sémantiques (dark mode auto)
├── theme.py        # Thème dynamique (clair/sombre/auto)
├── registry.py     # Registre @composant_ui + catalogue
├── html_builder.py # Builder HTML fluide avec XSS + ARIA
└── utils.py        # Helpers (echapper_html)
```

## 📦 Packages

### `components/` - Widgets Atomiques

| Fichier      | Composants                                                                                |
| ------------ | ----------------------------------------------------------------------------------------- |
| `atoms.py`   | `badge`, `etat_vide`, `carte_metrique`, `separateur`, `boite_info`                        |
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

### Design System

| Fichier              | Rôle                                                              |
| -------------------- | ----------------------------------------------------------------- |
| `tokens.py`          | Couleurs, espacements, rayons, `Variante` sémantique              |
| `tokens_semantic.py` | CSS custom properties avec mappings light/dark automatiques       |
| `a11y.py`            | `A11y` : sr-only, ARIA attrs, landmarks, vérification contraste   |
| `animations.py`      | `Animation` StrEnum + `injecter_animations()` + `animer()`        |
| `hooks.py`           | `use_pagination`, `use_recherche`, `use_filtres`, `use_tri`, etc. |
| `html_builder.py`    | Builder HTML fluide avec `.aria()`, `.focusable()`                |

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
    Variante,
    Sem,
    A11y,
    Animation,
    Modale,
)
```

### Variantes sémantiques

```python
from src.ui import badge, boite_info, Variante

badge("Actif", variante=Variante.SUCCESS)
badge("Urgent", variante=Variante.DANGER)
boite_info("Attention", "Stock faible", "⚠️", variante=Variante.WARNING)
```

### Hooks réutilisables

```python
from src.ui.hooks import use_pagination, use_recherche

# Recherche + pagination composables
filtered, show_search = use_recherche(recipes, ["nom", "categorie"])
visible, show_pagination = use_pagination(filtered, per_page=12)

show_search()
for r in visible:
    display_recipe(r)
show_pagination()
```

### Tokens sémantiques (dark mode auto)

```python
from src.ui.tokens_semantic import Sem

# Les composants référencent des CSS vars qui s'adaptent au thème
html = f'<div style="background: {Sem.SURFACE}; color: {Sem.ON_SURFACE};">...'
```

### Accessibilité

```python
from src.ui import A11y, HtmlBuilder

# ARIA attributes helper
html = (HtmlBuilder("nav")
    .aria(role="navigation", label="Menu principal")
    .child("a", text="Accueil")
    .build())

# Vérification contraste
ratio = A11y.ratio_contraste("#212529", "#ffffff")
assert A11y.est_conforme_aa("#212529", "#ffffff")  # True
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

## 🧪 Tests

```bash
pytest tests/ui/ -v
```

## 📋 Conventions

1. **Nommage français** pour toutes les fonctions/classes publiques (`afficher_*`, `obtenir_*`)
2. **Docstrings** en français avec Args et Example
3. **Point d'entrée unique**: `src.ui` re-exporte tous les symboles publics
4. **@composant_ui** obligatoire sur tous les composants pour le registre Design System
5. **Variante** sémantique plutôt que couleurs brutes dans les composants
6. **Tokens sémantiques** (`Sem.*`) pour les composants custom — dark mode gratuit
7. **A11y** : `aria-label`, `role`, `sr-only` sur tous les composants interactifs

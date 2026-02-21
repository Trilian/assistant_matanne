# Migration UI v2.0 - Guide de Migration

## Vue d'ensemble

Cette version modernise complètement le système UI en utilisant les patterns natifs Streamlit 1.35+ :

- `st.dialog` pour les modales
- `st.fragment` pour les rerenders partiels
- `st.query_params` pour la synchronisation URL
- Layouts composables avec context managers

## Breaking Changes

### 1. Classe `Modale` dépréciée

**Ancien code :**

```python
from src.ui.components.dynamic import Modale

modale = Modale("ma_modale", "Titre")
if modale.ouvrir():
    st.write("Contenu")
    if st.button("Fermer"):
        modale.fermer()
```

**Nouveau code :**

```python
from src.ui import confirm_dialog, DialogBuilder

# Option 1 - Fonction helper (simple)
if confirm_dialog("Êtes-vous sûr ?", "Confirmation"):
    do_action()

# Option 2 - Builder (avancé)
dialog = (
    DialogBuilder("mon_dialog", "Titre")
    .content("Contenu de la modale")
    .actions(
        {"label": "Confirmer", "type": "primary", "on_click": do_action},
        {"label": "Annuler", "type": "secondary"}
    )
    .build()
)
dialog.show()
```

### 2. Reruns explicites remplacés par fragments

**Ancien code :**

```python
if st.button("Rafraîchir"):
    st.session_state["data"] = fetch_data()
    st.rerun()  # ⚠️ Recharge toute la page
```

**Nouveau code :**

```python
from src.ui import ui_fragment, auto_refresh

@ui_fragment  # Ne recharge que ce bloc
def data_section():
    if st.button("Rafraîchir"):
        st.session_state["data"] = fetch_data()
        # Pas besoin de rerun !

# Ou avec auto-refresh
@auto_refresh(seconds=30)
def live_metrics():
    return get_metrics()
```

### 3. Layouts manuels remplacés par composables

**Ancien code :**

```python
col1, col2 = st.columns(2)
with col1:
    st.write("Gauche")
with col2:
    st.write("Droite")
```

**Nouveau code :**

```python
from src.ui import Row, Grid, two_columns

# Option 1 - Context manager
with Row(gap="md") as row:
    with row.col(2):
        st.write("Gauche (2/3)")
    with row.col(1):
        st.write("Droite (1/3)")

# Option 2 - Helper fonction
with two_columns() as (left, right):
    with left:
        st.write("Gauche")
    with right:
        st.write("Droite")

# Grille responsive
with Grid(cols=3, gap="lg") as grid:
    for item in items:
        with grid.cell():
            render_card(item)
```

### 4. URL State pour deep linking

**Ancien code :**

```python
# État perdu au refresh
tab = st.selectbox("Tab", ["A", "B", "C"])
```

**Nouveau code :**

```python
from src.ui import selectbox_with_url, URLState

# Option 1 - Helper
tab = selectbox_with_url("Tab", ["A", "B", "C"], param="tab")
# URL devient: ?tab=A

# Option 2 - Décorateur
@url_state(namespace="mon_module")
def page():
    # Tous les widgets synchronisés automatiquement
    pass
```

### 5. Formulaires déclaratifs

**Ancien code :**

```python
with st.form("mon_form"):
    nom = st.text_input("Nom", max_chars=50)
    age = st.number_input("Âge", min_value=0, max_value=120)
    email = st.text_input("Email")
    if st.form_submit_button("Valider"):
        if not nom:
            st.error("Nom requis")
        elif not "@" in email:
            st.error("Email invalide")
        else:
            save(nom, age, email)
```

**Nouveau code :**

```python
from src.ui import FormBuilder

result = (
    FormBuilder("mon_form")
    .text("nom", "Nom", required=True, max_length=50)
    .number("age", "Âge", min_value=0, max_value=120)
    .email("email", "Email", required=True)
    .submit("Valider")
    .build()
)

if result.submitted and result.is_valid:
    save(**result.data)
elif result.submitted:
    for error in result.errors:
        st.error(error)
```

## Nouveaux Patterns

### FragmentGroup - Coordination de fragments

```python
from src.ui import FragmentGroup

# Groupe de fragments coordonnés
group = FragmentGroup("dashboard")

@group.register("metrics")
def metrics_panel():
    return get_metrics()

@group.register("chart")
def chart_panel():
    return render_chart()

# Rafraîchir tout le groupe
group.refresh_all()

# Rafraîchir un seul
group.refresh("metrics")
```

### Stack - Layout vertical avec gap

```python
from src.ui import Stack, Gap

with Stack(gap=Gap.LG, align="center"):
    st.title("Titre")
    st.write("Description")
    st.button("Action")
```

### Cached Fragment - Fragment avec cache

```python
from src.ui import cached_fragment

@cached_fragment(ttl=300)  # Cache 5 min
def expensive_chart(data_key):
    # Calcul coûteux mis en cache
    return render_complex_chart()
```

### Lazy Fragment - Chargement différé

```python
from src.ui import lazy_fragment

@lazy_fragment(condition=lambda: st.session_state.get("show_advanced"))
def advanced_options():
    # Rendu seulement si condition vraie
    st.checkbox("Option avancée 1")
    st.checkbox("Option avancée 2")
```

## Checklist de Migration

- [ ] Remplacer `Modale` par `DialogBuilder` ou helpers (`confirm_dialog`, `alert_dialog`)
- [ ] Supprimer les `st.rerun()` inutiles, utiliser `@ui_fragment`
- [ ] Convertir les `st.columns()` répétitifs en `Row`/`Grid`
- [ ] Ajouter `@url_state` aux pages avec paramètres
- [ ] Utiliser `FormBuilder` pour les formulaires complexes
- [ ] Remplacer les timers manuels par `@auto_refresh`

## Imports

```python
# Tous les nouveaux symboles disponibles via src.ui
from src.ui import (
    # Dialogs
    DialogBuilder, confirm_dialog, alert_dialog, form_dialog,
    ouvrir_dialog, fermer_dialog,

    # Fragments
    ui_fragment, auto_refresh, isolated, lazy_fragment,
    cached_fragment, FragmentGroup,

    # Layouts
    Row, Grid, Stack, Gap,
    two_columns, three_columns, metrics_row, card_grid, sidebar_main,

    # URL State
    URLState, url_state, sync_to_url, get_url_param, set_url_param,
    pagination_with_url, selectbox_with_url, tabs_with_url,

    # Forms
    FormBuilder, FormResult, creer_formulaire,
)
```

## Compatibilité

- **Streamlit minimum** : 1.35.0 (pour `st.dialog`)
- **Fallback gracieux** : Si version < 1.35, les dialogs utilisent `st.expander`
- **Classe Modale** : Reste fonctionnelle mais émet `DeprecationWarning`

## Support

En cas de problème de migration, consulter :

- [PATTERNS.md](PATTERNS.md) - Exemples de patterns
- [UI_COMPONENTS.md](UI_COMPONENTS.md) - Référence des composants
- [ARCHITECTURE.md](ARCHITECTURE.md) - Vue d'ensemble

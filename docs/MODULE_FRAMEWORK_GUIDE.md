# Module Framework - Guide

Ce guide montre comment structurer un module avec le framework.

## Architecture du Framework

```
src/modules/_framework/
├── __init__.py          # Exports principaux
├── base_module.py       # BaseModule + décorateur module_app
├── error_boundary.py    # Gestion d'erreurs unifiée
├── fragments.py         # Fragments auto-refresh et isolation
└── state_manager.py     # Gestion d'état avec préfixes (ModuleState)
```

## Exemple: Migration du Module Inventaire

### Avant (Code actuel)

```python
# src/modules/cuisine/inventaire/__init__.py (avant)
import streamlit as st

def app():
    st.title("📦 Inventaire")

    # Initialisation manuelle de l'état
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    if "refresh_counter" not in st.session_state:
        st.session_state.refresh_counter = 0

    # Gestion d'erreurs ad-hoc
    try:
        articles = db.query(Article).all()
    except Exception as e:
        st.error(f"Erreur: {e}")
        return

    # Affichage des tabs
    tab_stock, tab_alertes = st.tabs(["📊 Stock", "⚠️ Alertes"])

    with tab_stock:
        try:
            afficher_stock()
        except Exception as e:
            st.error(f"Erreur stock: {e}")
```

### Après (Avec Framework)

```python
# src/modules/cuisine/inventaire/__init__.py (après)
from src.modules._framework import (
    error_boundary,
    ModuleState,
    init_module_state,
)
from src.services.inventaire import obtenir_service_inventaire

import streamlit as st


def app():
    """Point d'entrée du module inventaire."""

    init_module_state("inventaire", {
        "show_form": False,
        "refresh_counter": 0,
    })

    state = ModuleState("inventaire")

    st.title("📦 Inventaire")
    st.caption("Gestion complète de votre stock d'ingrédients")

    tab_stock, tab_alertes = st.tabs(["📊 Stock", "⚠️ Alertes"])

    with tab_stock:
        with error_boundary(titre="Erreur dans l'onglet Stock"):
            service = obtenir_service_inventaire()
            articles = service.get_inventaire_complet() or []
            # Affichage...

    with tab_alertes:
        with error_boundary(titre="Erreur dans l'onglet Alertes"):
            alertes = service.get_alertes() or {}
            # Affichage...
```

## Patterns Clés

### 1. Gestion d'État avec Préfixes

```python
from src.modules._framework import ModuleState, init_module_state

# Initialisation une seule fois
init_module_state("mon_module", {
    "filtre": "tous",
    "page": 1,
})

# Utilisation partout dans le module
state = ModuleState("mon_module")
print(state.get("filtre"))  # "tous"
state.set("page", 2)
state.toggle("expanded")  # True/False
state.increment("compteur")
```

### 2. Data Fetching

```python
# Appels directs aux services avec gestion d'erreurs
service = obtenir_service_inventaire()

try:
    with st.spinner("Chargement..."):
        articles = service.get_inventaire_complet() or []
except Exception as e:
    st.error(f"Erreur: {e}")
    if st.button("🔄 Réessayer"):
        st.rerun()
    return

for article in articles:
    st.write(article)
```

### 3. Error Boundaries

```python
from src.modules._framework import error_boundary, avec_gestion_erreurs_ui

# Context manager
with error_boundary(titre="Une erreur est survenue"):
    operation_risquee()

# Décorateur
@avec_gestion_erreurs_ui(titre="Erreur de rendu")
def render_complexe():
    ...
```

### 4. Fragments Auto-Refresh

```python
from src.modules._framework import auto_refresh_fragment

@auto_refresh_fragment(interval_seconds=30)
def widget_temps_reel():
    """Se rafraîchit toutes les 30 secondes."""
    data = fetch_live_data()
    st.metric("Valeur", data["value"])
```

## Composants UI Réutilisables

### Barre de Filtres

```python
from src.ui.components import FilterConfig, afficher_barre_filtres

filtres = afficher_barre_filtres(
    key="mes_filtres",
    recherche=True,
    filtres=[
        FilterConfig("categorie", "Catégorie", ["Fruits", "Légumes", "Viandes"]),
        FilterConfig("statut", "Statut", ["Actif", "Archivé"]),
    ],
)

# Appliquer les filtres
articles_filtres = [
    a for a in articles
    if filtres["categorie"] in (None, a.categorie)
    and filtres["recherche"].lower() in a.nom.lower()
]
```

### Métriques

```python
from src.ui.components import MetricConfig, afficher_metriques_row

afficher_metriques_row([
    MetricConfig("Articles", 42, delta="+3"),
    MetricConfig("Alertes", 5, delta="-2", delta_color="inverse"),
    MetricConfig("Valeur", "150€"),
])
```

## Migration Progressive

1. **Phase 1**: Ajouter `error_boundary` autour des sections critiques
2. **Phase 2**: Migrer l'état vers `ModuleState` avec préfixes
3. **Phase 3**: Utiliser les services directement pour le data fetching
4. **Phase 4**: Créer une classe `BaseModule` si le module est complexe
5. **Phase 5**: Extraire les composants réutilisables vers `src/ui/components/`

## Bénéfices

| Aspect            | Avant                     | Après                       |
| ----------------- | ------------------------- | --------------------------- |
| Gestion d'erreurs | Try/except partout        | `error_boundary` centralisé |
| État              | `st.session_state` direct | `ModuleState` avec préfixes |
| Data fetching     | Code dupliqué             | Services directs + spinner  |
| Résilience        | Crash complet             | Fallback gracieux           |
| Testabilité       | Difficile                 | Services mockables          |

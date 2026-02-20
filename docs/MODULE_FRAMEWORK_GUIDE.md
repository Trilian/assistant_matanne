# Module Framework - Guide de Migration

Ce guide montre comment migrer un module existant vers le nouveau framework modulaire.

## Architecture du Framework

```
src/modules/_framework/
├── __init__.py          # Exports principaux
├── base_module.py       # BaseModule + décorateur module_app
├── error_boundary.py    # Gestion d'erreurs unifiée
├── fragments.py         # Fragments auto-refresh et isolation
├── hooks.py             # Hooks React-like (use_state, use_query...)
└── state_manager.py     # Gestion d'état avec préfixes
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
    BaseModule,
    error_boundary,
    use_state,
    use_query,
    ModuleState,
    init_module_state,
)
from src.services.inventaire import get_inventaire_service

import streamlit as st


class InventaireModule(BaseModule):
    """Module inventaire avec le nouveau framework."""

    # Configuration du module
    titre = "📦 Inventaire"
    description = "Gestion complète de votre stock d'ingrédients"

    def setup(self) -> None:
        """Initialise l'état du module."""
        # État géré automatiquement avec préfixes
        init_module_state("inventaire", {
            "show_form": False,
            "refresh_counter": 0,
            "filtre_categorie": None,
            "recherche": "",
        })

    def render(self) -> None:
        """Rendu principal du module."""
        # Header avec aide contextuelle
        self.render_header()

        # Tabs avec gestion d'erreurs automatique
        tab_stock, tab_alertes = st.tabs(["📊 Stock", "⚠️ Alertes"])

        with tab_stock:
            with error_boundary(fallback_message="Impossible de charger le stock"):
                self.render_stock()

        with tab_alertes:
            with error_boundary(fallback_message="Impossible de charger les alertes"):
                self.render_alertes()

    def render_stock(self) -> None:
        """Affiche le stock avec hooks."""
        state = ModuleState("inventaire")
        service = get_inventaire_service()

        # Hook use_query pour le chargement des données
        articles = use_query(
            "inventaire_articles",
            fetcher=service.obtenir_articles,
            stale_time=300,  # 5 minutes
        )

        if articles.is_loading:
            st.spinner("Chargement...")
            return

        if articles.is_error:
            st.error(f"Erreur: {articles.error}")
            if st.button("🔄 Réessayer"):
                articles.refetch()
            return

        # Filtres avec état géré
        recherche = use_state("recherche", "", prefix="inventaire")
        st.text_input("🔍 Rechercher", value=recherche.value, on_change=lambda: recherche.set(st.session_state.get("recherche_input", "")), key="recherche_input")

        # Affichage des articles
        for article in articles.data or []:
            if recherche.value.lower() in article.nom.lower():
                self.render_article_card(article)

    def render_article_card(self, article) -> None:
        """Carte d'article individuelle."""
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"**{article.nom}**")
            col2.write(f"{article.quantite} {article.unite}")
            col3.write(f"📅 {article.date_peremption}")


def app():
    """Point d'entrée du module."""
    module = InventaireModule()
    module()
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

### 2. Data Fetching avec use_query

```python
from src.modules._framework import use_query

# Chargement avec cache et états
result = use_query(
    "ma_query",
    fetcher=lambda: service.get_data(),
    stale_time=300,  # Durée de fraîcheur en secondes
    enabled=True,    # Peut être conditionnel
    on_success=lambda data: st.toast("Chargé!"),
    on_error=lambda e: logger.error(e),
)

if result.is_loading:
    st.spinner("...")
elif result.is_error:
    st.error(result.error)
elif result.is_success:
    for item in result.data:
        st.write(item)
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
3. **Phase 3**: Remplacer les requêtes DB par `use_query`
4. **Phase 4**: Créer une classe `BaseModule` si le module est complexe
5. **Phase 5**: Extraire les composants réutilisables vers `src/ui/components/`

## Bénéfices Attendus

| Aspect            | Avant                     | Après                       |
| ----------------- | ------------------------- | --------------------------- |
| Gestion d'erreurs | Try/except partout        | `error_boundary` centralisé |
| État              | `st.session_state` direct | `ModuleState` avec préfixes |
| Data fetching     | Code dupliqué             | `use_query` avec cache      |
| Résilience        | Crash complet             | Fallback gracieux           |
| Testabilité       | Difficile                 | Hooks mockables             |

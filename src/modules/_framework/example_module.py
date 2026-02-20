"""
Exemple de module migré vers le framework moderne.

Ce fichier est un template démontrant l'utilisation de:
- BaseModule pour structurer le module
- error_boundary pour la gestion d'erreurs
- use_state/use_query pour l'état et le data fetching
- ModuleState pour l'état avec préfixes
- Composants UI réutilisables (FilterConfig, MetricConfig)

Usage: Copier ce template et l'adapter pour votre module.
"""

from dataclasses import dataclass
from typing import Any

import streamlit as st

from src.modules._framework import (
    ModuleState,
    auto_refresh_fragment,
    avec_gestion_erreurs_ui,
    error_boundary,
    init_module_state,
    use_memo,
    use_query,
    use_state,
)
from src.ui.components import (
    FilterConfig,
    MetricConfig,
    afficher_barre_filtres,
    afficher_metriques_row,
)

# ============================================================================
# Types de données
# ============================================================================


@dataclass
class Article:
    """Exemple de modèle de données."""

    id: int
    nom: str
    categorie: str
    quantite: int
    unite: str
    prix: float


# ============================================================================
# Service (mock pour l'exemple)
# ============================================================================


class ArticleService:
    """Service de données (simulé pour l'exemple)."""

    def obtenir_articles(self) -> list[Article]:
        """Récupère tous les articles."""
        return [
            Article(1, "Pommes", "Fruits", 10, "kg", 2.50),
            Article(2, "Carottes", "Légumes", 5, "kg", 1.80),
            Article(3, "Poulet", "Viandes", 2, "kg", 8.00),
            Article(4, "Lait", "Laitages", 6, "L", 1.20),
            Article(5, "Pain", "Boulangerie", 3, "unités", 1.50),
        ]

    def obtenir_categories(self) -> list[str]:
        """Récupère les catégories."""
        return ["Fruits", "Légumes", "Viandes", "Laitages", "Boulangerie"]


def get_article_service() -> ArticleService:
    """Factory pour le service."""
    return ArticleService()


# ============================================================================
# Composants du module
# ============================================================================


@avec_gestion_erreurs_ui(titre="Impossible d'afficher les métriques")
def afficher_metriques_stock(articles: list[Article]) -> None:
    """Affiche les métriques du stock."""
    total_articles = len(articles)
    valeur_totale = sum(a.quantite * a.prix for a in articles)
    categories = len(set(a.categorie for a in articles))

    afficher_metriques_row(
        [
            MetricConfig("Total Articles", total_articles, icon="📦"),
            MetricConfig("Valeur Stock", f"{valeur_totale:.2f}€", icon="💰"),
            MetricConfig("Catégories", categories, icon="🏷️"),
        ]
    )


@avec_gestion_erreurs_ui(titre="Impossible d'afficher l'article")
def afficher_article_card(article: Article) -> None:
    """Carte individuelle d'article."""
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"**{article.nom}**")
            st.caption(f"Catégorie: {article.categorie}")

        with col2:
            st.metric(
                "Quantité",
                f"{article.quantite} {article.unite}",
            )

        with col3:
            st.metric(
                "Prix/u",
                f"{article.prix:.2f}€",
            )


@auto_refresh_fragment(interval_seconds=60)
def widget_statistiques_live() -> None:
    """Widget qui se rafraîchit automatiquement."""
    st.caption("🔄 Actualisé automatiquement")
    col1, col2 = st.columns(2)
    col1.metric("Articles sous seuil", 3, delta="+1")
    col2.metric("Péremption <7j", 2, delta="-1", delta_color="inverse")


# ============================================================================
# Module principal
# ============================================================================


def app() -> None:
    """Point d'entrée du module exemple."""

    # Header
    st.title("📦 Module Exemple (Framework)")
    st.caption("Démonstration du nouveau framework modulaire")

    # Initialisation de l'état avec préfixes
    init_module_state(
        "exemple",
        {
            "vue": "liste",
            "recherche": "",
            "categorie_filtre": None,
        },
    )

    # Service via factory
    service = get_article_service()

    # Chargement des données avec use_query
    articles_query = use_query(
        "exemple_articles",
        fetcher=service.obtenir_articles,
        stale_time=300,  # Cache 5 minutes
    )

    categories_query = use_query(
        "exemple_categories",
        fetcher=service.obtenir_categories,
        stale_time=600,  # Cache 10 minutes
    )

    # Gestion du chargement
    if articles_query.is_loading or categories_query.is_loading:
        with st.spinner("Chargement des données..."):
            st.info("Récupération en cours...")
        return

    # Gestion des erreurs
    if articles_query.is_error:
        st.error(f"Erreur de chargement: {articles_query.error}")
        if st.button("🔄 Réessayer"):
            articles_query.refetch()
        return

    articles = articles_query.data or []
    categories = categories_query.data or []

    # Section métriques avec error boundary
    with error_boundary(fallback_message="Erreur d'affichage des métriques"):
        afficher_metriques_stock(articles)

    st.divider()

    # Widget temps réel
    widget_statistiques_live()

    st.divider()

    # Filtres avec composant réutilisable
    filtres = afficher_barre_filtres(
        key="exemple_filtres",
        recherche=True,
        filtres=[
            FilterConfig(
                key="categorie",
                label="Catégorie",
                options=categories,
            ),
        ],
    )

    # Filtrage des articles avec use_memo pour performance
    articles_filtres = use_memo(
        "articles_filtres",
        lambda: [
            a
            for a in articles
            if (not filtres["recherche"] or filtres["recherche"].lower() in a.nom.lower())
            and (not filtres["categorie"] or filtres["categorie"] == a.categorie)
        ],
        deps=[filtres["recherche"], filtres["categorie"], len(articles)],
    )

    # Affichage de la liste avec gestion d'erreurs
    st.subheader(f"📋 Articles ({len(articles_filtres)} résultats)")

    if not articles_filtres:
        st.info("Aucun article ne correspond aux critères de recherche.")
    else:
        for article in articles_filtres:
            with error_boundary(fallback_message=f"Erreur article {article.id}"):
                afficher_article_card(article)

    # Section actions avec état local
    st.divider()
    show_actions, set_show_actions = use_state("show_actions", False, prefix="exemple")

    if st.button("⚙️ Actions avancées", key="toggle_actions"):
        set_show_actions(not show_actions)

    if show_actions:
        with st.container(border=True):
            st.subheader("Actions")
            col1, col2, col3 = st.columns(3)
            col1.button("📥 Importer", key="import_btn")
            col2.button("📤 Exporter", key="export_btn")
            col3.button("🗑️ Purger", key="purge_btn")


# Point d'entrée pour le test isolé
if __name__ == "__main__":
    app()

"""
Module Inventaire - Gestion du stock (version migrée vers le framework)

Migration du module inventaire vers le nouveau framework modulaire.
Fonctionnalités identiques avec:
- Gestion d'erreurs unifiée via error_boundary
- État managé via ModuleState (préfixes automatiques)
- Data fetching via use_query avec cache
- Composants UI réutilisables
"""

import logging

import streamlit as st

from src.core.errors_base import ErreurValidation
from src.modules._framework import (
    ModuleState,
    error_boundary,
    init_module_state,
    use_query,
    use_state,
)
from src.services.inventaire import obtenir_service_inventaire
from src.ui import etat_vide
from src.ui.components import MetricConfig, afficher_metriques_row

from .alertes import afficher_alertes
from .categories import afficher_categories
from .historique import afficher_historique
from .notifications import afficher_notifications
from .photos import afficher_photos
from .predictions import afficher_predictions
from .suggestions import afficher_suggestions_ia
from .tools import afficher_tools
from .utils import _prepare_inventory_dataframe

logger = logging.getLogger(__name__)


# ============================================================================
# Composants migres avec error_boundary
# ============================================================================


def afficher_header():
    """Header du module avec info-bulle d'aide."""
    col_title, col_help = st.columns([10, 1])
    with col_title:
        st.title("📦 Inventaire")
    with col_help:
        st.markdown(
            "<span title=\"Gérez votre stock d'ingrédients, suivez les dates de péremption, "
            "recevez des alertes et optimisez vos courses grâce à l'IA.\" "
            'style="cursor: help; font-size: 1.5rem;">❓</span>',
            unsafe_allow_html=True,
        )
    st.caption("Gestion complète de votre stock d'ingrédients")


def afficher_metriques_inventaire(inventaire: list, alertes: dict) -> None:
    """Affiche les métriques du stock avec le composant réutilisable."""
    stock_critique = len(alertes.get("critique", []))
    stock_bas = len(alertes.get("stock_bas", []))
    peremption = len(alertes.get("peremption_proche", []))

    # Icônes conditionnelles
    icon_critique = "❌" if stock_critique > 0 else "✅"
    icon_bas = "⚠" if stock_bas > 0 else "✅"
    icon_peremption = "⏰" if peremption > 0 else "✅"

    afficher_metriques_row(
        [
            MetricConfig("Articles", len(inventaire), icon="📦"),
            MetricConfig(f"{icon_critique} Critique", stock_critique),
            MetricConfig(f"{icon_bas} Faible", stock_bas),
            MetricConfig(f"{icon_peremption} Péremption", peremption),
        ]
    )


def afficher_filtres_stock(inventaire: list) -> dict:
    """Affiche les filtres et retourne les valeurs sélectionnées."""
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        emplacements = sorted(set(a["emplacement"] for a in inventaire if a["emplacement"]))
        selected_emplacements = st.multiselect(
            "📝 Emplacement", options=emplacements, default=[], key="inv_filtre_emplacement"
        )

    with col_filter2:
        categories = sorted(set(a["ingredient_categorie"] for a in inventaire))
        selected_categories = st.multiselect(
            "🏷️ Catégorie", options=categories, default=[], key="inv_filtre_categorie"
        )

    with col_filter3:
        status_filter = st.multiselect(
            "⚠️ Statut",
            options=["critique", "stock_bas", "peremption_proche", "ok"],
            default=[],
            key="inv_filtre_statut",
        )

    return {
        "emplacements": selected_emplacements,
        "categories": selected_categories,
        "statuts": status_filter,
    }


def appliquer_filtres_stock(inventaire: list, filtres: dict) -> list:
    """Applique les filtres au stock."""
    result = inventaire

    if filtres["emplacements"]:
        result = [a for a in result if a["emplacement"] in filtres["emplacements"]]

    if filtres["categories"]:
        result = [a for a in result if a["ingredient_categorie"] in filtres["categories"]]

    if filtres["statuts"]:
        result = [a for a in result if a["statut"] in filtres["statuts"]]

    return result


def afficher_tableau_stock(inventaire: list) -> None:
    """Affiche le tableau de stock."""
    if inventaire:
        df = _prepare_inventory_dataframe(inventaire)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Statut": st.column_config.TextColumn(width="small"),
                "Quantité": st.column_config.NumberColumn(width="small"),
                "Jours": st.column_config.NumberColumn(width="small"),
            },
        )
    else:
        etat_vide(
            "Aucun article ne correspond aux filtres",
            "🔍",
            "Modifiez les filtres pour voir plus d'articles",
        )


def afficher_actions_stock(state: ModuleState) -> None:
    """Affiche les boutons d'action."""
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("➕ Ajouter un article", use_container_width=True, key="btn_add_article"):
            state.set("show_form", True)
            st.rerun()

    with col_btn2:
        if st.button("🔄 Rafraîchir", use_container_width=True, key="btn_refresh"):
            state.increment("refresh_counter")
            st.rerun()

    with col_btn3:
        st.button("📥 Importer CSV", use_container_width=True, key="btn_import")


def afficher_formulaire_ajout(state: ModuleState) -> None:
    """Formulaire d'ajout d'un nouvel article avec gestion d'erreurs."""
    service = obtenir_service_inventaire()

    if service is None:
        st.error("❌ Service inventaire indisponible")
        return

    st.subheader("➕ Ajouter un nouvel article")

    col1, col2 = st.columns(2)

    with col1:
        ingredient_nom = st.text_input(
            "Nom de l'article *",
            placeholder="Ex: Tomates cerises",
            key="form_nom_article",
        )

    with col2:
        quantite = st.number_input("Quantité", value=1.0, min_value=0.0, key="form_quantite")

    col1, col2 = st.columns(2)

    with col1:
        emplacement = st.text_input(
            "Emplacement",
            placeholder="Frigo, Placard...",
            key="form_emplacement",
        )

    with col2:
        date_peremption = st.date_input("Date de péremption", value=None, key="form_date")

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("⏰ Ajouter", use_container_width=True, type="primary", key="btn_confirm_add"):
            if not ingredient_nom:
                st.error("❌ Le nom est obligatoire")
            else:
                with error_boundary(titre="Erreur lors de l'ajout"):
                    article = service.ajouter_article(
                        ingredient_nom=ingredient_nom,
                        quantite=quantite,
                        emplacement=emplacement if emplacement else None,
                        date_peremption=date_peremption if date_peremption else None,
                    )

                    if article:
                        st.success(f"✅ Article '{ingredient_nom}' ajouté avec succès!")
                        state.set("show_form", False)
                        state.increment("refresh_counter")
                        st.rerun()
                    else:
                        st.error("❌ Impossible d'ajouter l'article")

    with col2:
        if st.button("❌ Annuler", use_container_width=True, key="btn_cancel_add"):
            state.set("show_form", False)
            st.rerun()


def afficher_stock_complet() -> None:
    """Affiche l'onglet stock complet avec le nouveau framework."""
    state = ModuleState("inventaire")
    service = obtenir_service_inventaire()

    if service is None:
        st.error("❌ Service inventaire indisponible")
        return

    # Data fetching avec use_query
    inventaire_query = use_query(
        "inventaire_stock",
        fetcher=service.get_inventaire_complet,
        stale_time=60,  # Cache 1 minute
    )

    alertes_query = use_query(
        "inventaire_alertes",
        fetcher=service.get_alertes,
        stale_time=60,
    )

    # Gestion du chargement
    if inventaire_query.is_loading or alertes_query.is_loading:
        with st.spinner("Chargement de l'inventaire..."):
            st.info("Récupération des données...")
        return

    # Gestion des erreurs
    if inventaire_query.is_error:
        st.error(f"❌ Erreur: {inventaire_query.error}")
        if st.button("🔄 Réessayer", key="retry_stock"):
            inventaire_query.refetch()
        return

    inventaire = inventaire_query.data or []
    alertes = alertes_query.data or {}

    # Inventaire vide
    if not inventaire:
        st.info("📦 Inventaire vide. Commencez par ajouter des articles!")
        if st.button("➕ Ajouter un article", key="btn_add_empty"):
            state.set("show_form", True)
        return

    # Métriques
    with error_boundary(titre="Erreur d'affichage des métriques"):
        afficher_metriques_inventaire(inventaire, alertes)

    st.divider()

    # Filtres
    filtres = afficher_filtres_stock(inventaire)
    inventaire_filtre = appliquer_filtres_stock(inventaire, filtres)

    # Tableau
    with error_boundary(titre="Erreur d'affichage du tableau"):
        afficher_tableau_stock(inventaire_filtre)

    # Actions
    st.divider()
    afficher_actions_stock(state)


# ============================================================================
# Point d'entrée principal
# ============================================================================


def app():
    """Point d'entrée du module inventaire (version migrée)."""

    # Initialisation de l'état avec préfixes
    init_module_state(
        "inventaire",
        {
            "show_form": False,
            "refresh_counter": 0,
            "active_tab": 0,
        },
    )

    state = ModuleState("inventaire")

    # Header
    afficher_header()

    # Tabs principales avec error_boundary par onglet
    (
        tab_stock,
        tab_alertes,
        tab_categories,
        tab_suggestions,
        tab_historique,
        tab_photos,
        tab_notifications,
        tab_predictions,
        tab_tools,
    ) = st.tabs(
        [
            "📊 Stock",
            "⚠️ Alertes",
            "🏷️ Catégories",
            "🛒 Suggestions IA",
            "📋 Historique",
            "📷 Photos",
            "🔔 Notifications",
            "🔮 Prévisions",
            "🔧 Outils",
        ]
    )

    with tab_stock:
        with error_boundary(titre="Erreur dans l'onglet Stock"):
            afficher_stock_complet()

    with tab_alertes:
        with error_boundary(titre="Erreur dans l'onglet Alertes"):
            afficher_alertes()

    with tab_categories:
        with error_boundary(titre="Erreur dans l'onglet Catégories"):
            afficher_categories()

    with tab_suggestions:
        with error_boundary(titre="Erreur dans l'onglet Suggestions IA"):
            afficher_suggestions_ia()

    with tab_historique:
        with error_boundary(titre="Erreur dans l'onglet Historique"):
            afficher_historique()

    with tab_photos:
        with error_boundary(titre="Erreur dans l'onglet Photos"):
            afficher_photos()

    with tab_notifications:
        with error_boundary(titre="Erreur dans l'onglet Notifications"):
            afficher_notifications()

    with tab_predictions:
        with error_boundary(titre="Erreur dans l'onglet Prévisions"):
            afficher_predictions()

    with tab_tools:
        with error_boundary(titre="Erreur dans l'onglet Outils"):
            afficher_tools()

    # Formulaire d'ajout si demandé
    if state.get("show_form"):
        st.divider()
        with error_boundary(titre="Erreur dans le formulaire"):
            afficher_formulaire_ajout(state)


__all__ = ["app"]

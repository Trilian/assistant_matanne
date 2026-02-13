"""
Gestion du stock - Onglet principal de l'inventaire.
Affichage du stock avec filtres et formulaire d'ajout.
"""

import logging

import streamlit as st

from src.core.errors_base import ErreurValidation
from src.services.inventaire import get_inventaire_service

from .utils import _prepare_inventory_dataframe

logger = logging.getLogger(__name__)


def render_add_article_form():
    """Affiche le formulaire pour ajouter un nouvel article"""
    service = get_inventaire_service()

    if service is None:
        st.error("❌ Service inventaire indisponible")
        return

    st.subheader("➕ Ajouter un nouvel article")

    try:
        col1, col2 = st.columns(2)

        with col1:
            ingredient_nom = st.text_input("Nom de l'article *", placeholder="Ex: Tomates cerises")

        with col2:
            quantite = st.number_input("Quantité", value=1.0, min_value=0.0)

        col1, col2 = st.columns(2)

        with col1:
            emplacement = st.text_input("Emplacement", placeholder="Frigo, Placard...")

        with col2:
            date_peremption = st.date_input("Date de péremption", value=None)

        col1, col2 = st.columns([1, 4])

        with col1:
            if st.button("⏰ Ajouter", width="stretch", type="primary"):
                if not ingredient_nom:
                    st.error("❌ Le nom est obligatoire")
                else:
                    try:
                        article = service.ajouter_article(
                            ingredient_nom=ingredient_nom,
                            quantite=quantite,
                            emplacement=emplacement if emplacement else None,
                            date_peremption=date_peremption if date_peremption else None,
                        )

                        if article:
                            st.success(f"✅ Article '{ingredient_nom}' ajouté avec succès!")
                            st.session_state.show_form = False
                            st.session_state.refresh_counter += 1
                            st.rerun()
                        else:
                            st.error("❌ Impossible d'ajouter l'article")

                    except ErreurValidation as e:
                        st.error(f"❌ Erreur: {e}")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'ajout: {str(e)}")
                        logger.error(f"Erreur ajouter_article: {e}")

        with col2:
            if st.button("❌ Annuler", width="stretch"):
                st.session_state.show_form = False
                st.rerun()

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_add_article_form: {e}")


def render_stock():
    """Affiche le stock actuel avec filtres et statistiques"""
    service = get_inventaire_service()

    if service is None:
        st.error("❌ Service inventaire indisponible")
        return

    try:
        inventaire = service.get_inventaire_complet()

        if not inventaire:
            st.info("📝† Inventaire vide. Commencez par ajouter des articles!")
            if st.button("➕ Ajouter un article"):
                st.session_state.show_form = True
            return

        # STATISTIQUES GLOBALES
        col1, col2, col3, col4 = st.columns(4)

        alertes = service.get_alertes()
        stock_critique = len(alertes.get("critique", []))
        stock_bas = len(alertes.get("stock_bas", []))
        peremption = len(alertes.get("peremption_proche", []))

        with col1:
            st.metric("📦 Articles", len(inventaire), delta=None)
        with col2:
            color = "❌" if stock_critique > 0 else "✅"
            st.metric(f"{color} Critique", stock_critique)
        with col3:
            color = "âš " if stock_bas > 0 else "✅"
            st.metric(f"{color} Faible", stock_bas)
        with col4:
            color = "⏰" if peremption > 0 else "✅"
            st.metric(f"{color} Péremption", peremption)

        st.divider()

        # FILTRES ET TRI
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            emplacements = sorted(set(a["emplacement"] for a in inventaire if a["emplacement"]))
            selected_emplacements = st.multiselect(
                "📝 Emplacement", options=emplacements, default=[]
            )

        with col_filter2:
            categories = sorted(set(a["ingredient_categorie"] for a in inventaire))
            selected_categories = st.multiselect("🏷️ Catégorie", options=categories, default=[])

        with col_filter3:
            status_filter = st.multiselect(
                "⚠️ Statut",
                options=["critique", "stock_bas", "peremption_proche", "ok"],
                default=[],
            )

        # APPLIQUER LES FILTRES
        inventaire_filtres = inventaire

        if selected_emplacements:
            inventaire_filtres = [
                a for a in inventaire_filtres if a["emplacement"] in selected_emplacements
            ]

        if selected_categories:
            inventaire_filtres = [
                a for a in inventaire_filtres if a["ingredient_categorie"] in selected_categories
            ]

        if status_filter:
            inventaire_filtres = [a for a in inventaire_filtres if a["statut"] in status_filter]

        # AFFICHER LE TABLEAU
        if inventaire_filtres:
            df = _prepare_inventory_dataframe(inventaire_filtres)
            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Statut": st.column_config.TextColumn(width="small"),
                    "Quantité": st.column_config.NumberColumn(width="small"),
                    "Jours": st.column_config.NumberColumn(width="small"),
                },
            )
        else:
            st.info("Aucun article ne correspond aux filtres sélectionnés.")

        # BOUTONS D'ACTION
        st.divider()
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button("➕ Ajouter un article", width="stretch"):
                st.session_state.show_form = True
                st.rerun()

        with col_btn2:
            if st.button("🔄 Rafraîchir", width="stretch"):
                st.session_state.refresh_counter += 1
                st.rerun()

        with col_btn3:
            if st.button("📝¥ Importer CSV", width="stretch"):
                st.session_state.show_import = True

    except ErreurValidation as e:
        st.error(f"❌ Erreur de validation: {e}")
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


__all__ = ["render_stock", "render_add_article_form"]

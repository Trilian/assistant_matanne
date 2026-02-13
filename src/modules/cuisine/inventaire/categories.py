"""
Gestion des catégories - Onglet catégories de l'inventaire.
Affiche les articles groupés par catégorie.
"""

import streamlit as st

from src.services.inventaire import get_inventaire_service

from .utils import _prepare_inventory_dataframe


def render_categories():
    """Gestion des catégories d'ingrédients"""
    service = get_inventaire_service()

    if service is None:
        st.error("âŒ Service inventaire indisponible")
        return

    try:
        inventaire = service.get_inventaire_complet()

        if not inventaire:
            st.info("Inventaire vide")
            return

        # Grouper par catégorie
        categories = {}
        for article in inventaire:
            cat = article["ingredient_categorie"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)

        # Afficher par onglet
        tabs = st.tabs(
            [f"ðŸ·ï¸ {cat} ({len(articles)})" for cat, articles in sorted(categories.items())]
        )

        for (cat, articles), tab in zip(sorted(categories.items()), tabs, strict=False):
            with tab:
                # Statistiques catégorie
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Articles", len(articles))
                with col2:
                    total_qty = sum(a["quantite"] for a in articles)
                    st.metric("Quantité totale", f"{total_qty:.1f}")
                with col3:
                    alertes = service.get_alertes()
                    cat_alertes = len(
                        [a for a in articles if a["statut"] in ["critique", "stock_bas"]]
                    )
                    st.metric("âš ï¸ Alertes", cat_alertes)

                st.divider()

                # Tableau catégorie
                df = _prepare_inventory_dataframe(articles)
                st.dataframe(df, width="stretch", hide_index=True)

    except Exception as e:
        st.error(f"âŒ Erreur: {str(e)}")


__all__ = ["render_categories"]

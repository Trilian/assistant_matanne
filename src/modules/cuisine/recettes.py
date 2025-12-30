import streamlit as st
from src.services.recettes.recette_service import recette_service
from src.ui import search_bar, filter_panel, pagination, recipe_card, empty_state, toast, grid_layout
from src.core.cache import Cache

def app():
    st.title("🍽️ Recettes Intelligentes")

    tab1, tab2 = st.tabs(["📚 Mes Recettes", "➕ Ajouter"])

    with tab1:
        # Recherche
        search = search_bar(key="recettes_search")

        # Filtres
        filters = filter_panel({
            "saison": {"type": "select", "label": "Saison", "options": ["Toutes", "printemps", "été", "automne", "hiver"]},
            "rapide": {"type": "checkbox", "label": "⚡ Rapides"}
        }, "recettes_filters")

        # Charger recettes
        recettes = recette_service.advanced_search(
            search_term=search if search else None,
            search_fields=["nom", "description"],
            filters={"saison": filters["saison"]} if filters["saison"] != "Toutes" else None,
            limit=100
        )

        if not recettes:
            empty_state("Aucune recette", "🍽️")
            return

        # Pagination
        page, per_page = pagination(len(recettes), 12, "recettes_pagination")
        start = (page - 1) * per_page
        recettes_page = recettes[start:start + per_page]

        # Grille
        def render_card(recette, key):
            recipe_card(
                {"nom": recette.nom, "difficulte": recette.difficulte,
                 "temps_preparation": recette.temps_preparation,
                 "temps_cuisson": recette.temps_cuisson,
                 "portions": recette.portions,
                 "est_rapide": recette.est_rapide,
                 "url_image": recette.url_image},
                on_view=lambda: st.info(f"Voir {recette.id}"),
                on_delete=lambda: _delete_recette(recette.id),
                key=key
            )

        grid_layout(recettes_page, 3, render_card, "recettes_grid")

    with tab2:
        st.markdown("### ➕ Ajouter une recette")
        st.info("🚧 Formulaire à implémenter")

def _delete_recette(recette_id: int):
    if st.button(f"Confirmer suppression ?", key=f"confirm_{recette_id}"):
        recette_service.delete(recette_id)
        toast("🗑️ Supprimé", "success")
        Cache.invalidate("recette")
        st.rerun()
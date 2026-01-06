"""
Composants UI - Recettes
Cartes et widgets spécifiques recettes
"""
import streamlit as st
from typing import Dict, Optional, Callable


def recipe_card(
        recipe: Dict,
        on_view: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        mode: str = "list",
        key: str = "recipe"
):
    """
    Carte recette

    Args:
        recipe: Dict recette
        on_view: Callback voir
        on_edit: Callback éditer
        on_delete: Callback supprimer
        mode: "list" ou "grid"
        key: Clé unique
    """
    diff_colors = {
        "facile": "#4CAF50",
        "moyen": "#FF9800",
        "difficile": "#f44336"
    }
    border = diff_colors.get(recipe.get("difficulte", "moyen"), "#e0e0e0")

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {border}; padding: 1rem; '
            f'background: #fff; border-radius: 8px; margin-bottom: 1rem;"></div>',
            unsafe_allow_html=True
        )

        if recipe.get("url_image") and mode == "list":
            col_img, col_content = st.columns([1, 3])
            with col_img:
                st.image(recipe["url_image"], use_container_width=True)
            content_col = col_content
        else:
            content_col = st.container()

        with content_col:
            st.markdown(f"### {recipe['nom']}")

            temps = recipe.get("temps_preparation", 0) + recipe.get("temps_cuisson", 0)
            meta = [f"⏱️ {temps}min", f"🍽️ {recipe.get('portions', 4)}p"]
            st.caption(" • ".join(meta))

            badges = []
            if recipe.get("est_rapide"):
                badges.append("⚡ Rapide")
            if recipe.get("compatible_bebe"):
                badges.append("👶 Bébé")
            if badges:
                st.caption(" | ".join(badges))

        if on_view or on_edit or on_delete:
            cols = st.columns(3)
            if on_view:
                with cols[0]:
                    if st.button("👁️ Voir", key=f"{key}_view", use_container_width=True):
                        on_view()
            if on_edit:
                with cols[1]:
                    if st.button("✏️ Éditer", key=f"{key}_edit", use_container_width=True):
                        on_edit()
            if on_delete:
                with cols[2]:
                    if st.button("🗑️ Suppr.", key=f"{key}_del", use_container_width=True):
                        on_delete()


def recipe_detail(recipe: Dict):
    """
    Affichage détaillé recette

    Args:
        recipe: Dict recette complète
    """
    # Header
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title(recipe["nom"])

        if recipe.get("description"):
            st.markdown(recipe["description"])

    with col2:
        if recipe.get("url_image"):
            st.image(recipe["url_image"], use_container_width=True)

    # Métadonnées
    col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)

    with col_meta1:
        st.metric("Préparation", f"{recipe.get('temps_preparation', 0)}min")

    with col_meta2:
        st.metric("Cuisson", f"{recipe.get('temps_cuisson', 0)}min")

    with col_meta3:
        st.metric("Portions", recipe.get("portions", 4))

    with col_meta4:
        st.metric("Difficulté", recipe.get("difficulte", "moyen").capitalize())

    st.markdown("---")

    # Ingrédients
    if recipe.get("ingredients"):
        st.markdown("### 🥘 Ingrédients")
        for ing in recipe["ingredients"]:
            st.markdown(f"- **{ing['quantite']} {ing['unite']}** {ing['nom']}")

        st.markdown("---")

    # Étapes
    if recipe.get("etapes"):
        st.markdown("### 📝 Étapes")
        for idx, etape in enumerate(recipe["etapes"], 1):
            st.markdown(f"**{idx}.** {etape}")


def recipe_filter_bar(on_filter_change: Callable):
    """
    Barre de filtres recettes

    Args:
        on_filter_change: Callback (filters_dict)
    """
    from src.utils.constants import SAISONS, DIFFICULTES, TYPES_REPAS

    col1, col2, col3 = st.columns(3)

    with col1:
        saison = st.selectbox("Saison", ["Toutes"] + SAISONS, key="filter_saison")

    with col2:
        difficulte = st.selectbox("Difficulté", ["Toutes"] + DIFFICULTES, key="filter_diff")

    with col3:
        type_repas = st.selectbox("Type", ["Tous"] + TYPES_REPAS, key="filter_type")

    filters = {}
    if saison != "Toutes":
        filters["saison"] = saison
    if difficulte != "Toutes":
        filters["difficulte"] = difficulte
    if type_repas != "Tous":
        filters["type_repas"] = type_repas

    if filters:
        on_filter_change(filters)
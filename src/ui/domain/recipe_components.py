"""
Composants UI - RECETTES (Part 1: Cartes)
"""
import streamlit as st
from typing import Dict, Optional, Callable


def recipe_card(
        recipe: Dict,
        on_view: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_duplicate: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        mode: str = "list",
        key: str = "recipe"
):
    """
    Carte recette universelle

    Args:
        recipe: Dict recette
        on_view/edit/duplicate/delete: Callbacks
        mode: "list" (détaillé) ou "grid" (compact)
        key: Clé unique
    """
    # Badges
    badges = []
    if recipe.get("est_rapide"):
        badges.append(("⚡", "#FF9800"))
    if recipe.get("est_equilibre"):
        badges.append(("🥗", "#4CAF50"))
    if recipe.get("compatible_bebe"):
        badges.append(("👶", "#2196F3"))
    if recipe.get("genere_par_ia"):
        badges.append(("🤖", "#9C27B0"))

    # Couleur selon difficulté
    diff_colors = {"facile": "#4CAF50", "moyen": "#FF9800", "difficile": "#f44336"}
    border = diff_colors.get(recipe.get("difficulte", "moyen"), "#e0e0e0")

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {border}; padding: 1rem; '
            f'background: #fff; border-radius: 8px; margin-bottom: 1rem; '
            f'box-shadow: 0 2px 4px rgba(0,0,0,0.1);"></div>',
            unsafe_allow_html=True
        )

        if mode == "grid":
            _render_grid_mode(recipe, badges, on_view, on_edit, key)
        else:
            _render_list_mode(recipe, badges, on_view, on_edit, on_duplicate, on_delete, key)

def recipe_grid(
        recipes: List[Dict],
        on_click: Callable[[int], None],
        cols: int = 3,
        key: str = "grid"
):
    """
    Grille de recettes

    Args:
        recipes: Liste recettes
        on_click: Callback(recipe_id)
        cols: Colonnes par ligne
        key: Clé unique
    """
    if not recipes:
        st.info("Aucune recette")
        return

    for row_idx in range(0, len(recipes), cols):
        columns = st.columns(cols)

        for col_idx in range(cols):
            recipe_idx = row_idx + col_idx

            if recipe_idx < len(recipes):
                recipe = recipes[recipe_idx]

                with columns[col_idx]:
                    recipe_card(
                        recipe,
                        on_view=lambda r=recipe: on_click(r["id"]),
                        mode="grid",
                        key=f"{key}_{recipe_idx}"
                    )


def recipe_filters(
        on_filter: Callable[[Dict], None],
        key: str = "filters"
) -> Dict:
    """
    Panneau de filtres recettes

    Args:
        on_filter: Callback(filters_dict)
        key: Clé unique

    Returns:
        Dict des filtres sélectionnés
    """
    with st.expander("🔍 Filtres", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            saison = st.selectbox(
                "Saison",
                ["Toutes", "printemps", "été", "automne", "hiver", "toute_année"],
                key=f"{key}_saison"
            )

            difficulte = st.selectbox(
                "Difficulté",
                ["Toutes", "facile", "moyen", "difficile"],
                key=f"{key}_diff"
            )

            temps_max = st.slider(
                "Temps max (min)",
                0, 180, 180,
                key=f"{key}_temps"
            )

        with col2:
            type_repas = st.selectbox(
                "Type repas",
                ["Tous", "petit_déjeuner", "déjeuner", "dîner", "goûter"],
                key=f"{key}_type"
            )

            rapide = st.checkbox("⚡ Rapides", key=f"{key}_rapide")
            equilibre = st.checkbox("🥗 Équilibrées", key=f"{key}_eq")
            bebe = st.checkbox("👶 Bébé", key=f"{key}_bebe")

        filters = {
            "saison": None if saison == "Toutes" else saison,
            "difficulte": None if difficulte == "Toutes" else difficulte,
            "type_repas": None if type_repas == "Tous" else type_repas,
            "temps_max": temps_max if temps_max < 180 else None,
            "rapide": rapide if rapide else None,
            "equilibre": equilibre if equilibre else None,
            "bebe": bebe if bebe else None
        }

        if st.button("🔄 Appliquer", key=f"{key}_apply", use_container_width=True):
            on_filter(filters)

        return filters


def ingredients_list(ingredients: List[Dict], compact: bool = False):
    """
    Liste ingrédients formatée

    Args:
        ingredients: [{"nom": str, "quantite": float, "unite": str, "optionnel": bool}]
        compact: Mode compact
    """
    if not ingredients:
        st.info("Aucun ingrédient")
        return

    st.markdown("### 🥕 Ingrédients")

    for ing in ingredients:
        optional = " *(optionnel)*" if ing.get("optionnel") else ""

        if compact:
            st.caption(f"• {ing['quantite']} {ing['unite']} {ing['nom']}{optional}")
        else:
            st.markdown(f"- **{ing['quantite']} {ing['unite']}** {ing['nom']}{optional}")


def steps_list(steps: List[Dict], compact: bool = False):
    """
    Liste étapes formatée

    Args:
        steps: [{"ordre": int, "description": str, "duree": int}]
        compact: Mode compact
    """
    if not steps:
        st.info("Aucune étape")
        return

    st.markdown("### 📝 Préparation")

    sorted_steps = sorted(steps, key=lambda x: x["ordre"])

    for step in sorted_steps:
        duration = f" *({step['duree']}min)*" if step.get("duree") else ""

        if compact:
            st.caption(f"{step['ordre']}. {step['description']}{duration}")
        else:
            st.markdown(f"**{step['ordre']}.** {step['description']}{duration}")

def _render_grid_mode(recipe, badges, on_view, on_edit, key):
    """Mode grille (compact)"""
    if recipe.get("url_image"):
        st.image(recipe["url_image"], use_container_width=True)

    st.markdown(f"**{recipe['nom']}**")
    st.caption(
        f"⏱️ {recipe.get('temps_total', 0)}min • "
        f"🍽️ {recipe.get('portions', 4)}p"
    )

    # Badges
    if badges:
        html = " ".join([
            f'<span style="background:{c};color:white;padding:0.2rem 0.4rem;'
            f'border-radius:8px;font-size:0.8rem;">{l}</span>'
            for l, c in badges[:2]
        ])
        st.markdown(html, unsafe_allow_html=True)

    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if on_view and st.button("👁️", key=f"{key}_view", use_container_width=True):
            on_view()
    with col2:
        if on_edit and st.button("✏️", key=f"{key}_edit", use_container_width=True):
            on_edit()


def _render_list_mode(recipe, badges, on_view, on_edit, on_duplicate, on_delete, key):
    """Mode liste (détaillé)"""
    # Layout
    if recipe.get("url_image"):
        col_img, col_content = st.columns([1, 3])
        with col_img:
            st.image(recipe["url_image"], use_container_width=True)
        content_col = col_content
    else:
        content_col = st.container()

    with content_col:
        # Titre
        st.markdown(f"### {recipe['nom']}")

        # Description
        if recipe.get("description"):
            st.caption(recipe["description"][:150] + "..." if len(recipe["description"]) > 150 else recipe["description"])

        # Métadonnées
        meta = [
            f"⏱️ {recipe.get('temps_total', 0)} min",
            f"🍽️ {recipe.get('portions', 4)} portions",
            f"📊 {recipe.get('difficulte', 'moyen').capitalize()}"
        ]
        st.caption(" • ".join(meta))

        # Badges
        if badges:
            html = " ".join([
                f'<span style="background:{c};color:white;padding:0.25rem 0.5rem;'
                f'border-radius:12px;font-size:0.875rem;margin-right:0.25rem;">{l}</span>'
                for l, c in badges
            ])
            st.markdown(html, unsafe_allow_html=True)

    # Actions
    cols = st.columns(4)
    with cols[0]:
        if on_view and st.button("👁️ Voir", key=f"{key}_view", use_container_width=True):
            on_view()
    with cols[1]:
        if on_edit and st.button("✏️ Éditer", key=f"{key}_edit", use_container_width=True):
            on_edit()
    with cols[2]:
        if on_duplicate and st.button("📋 Dupliquer", key=f"{key}_dup", use_container_width=True):
            on_duplicate()
    with cols[3]:
        if on_delete and st.button("🗑️ Suppr.", key=f"{key}_del", use_container_width=True):
            on_delete()
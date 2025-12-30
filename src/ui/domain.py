"""
UI Domain Components
Composants métier spécialisés pour Recettes, Inventaire, Planning
"""

# RECETTES
def recipe_card(recipe: Dict, on_view: Callable = None, on_edit: Callable = None,
                on_delete: Callable = None, mode: str = "list", key: str = "recipe"):
    """Carte recette"""
    diff_colors = {"facile": "#4CAF50", "moyen": "#FF9800", "difficile": "#f44336"}
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

            meta = [
                f"⏱️ {recipe.get('temps_preparation', 0) + recipe.get('temps_cuisson', 0)} min",
                f"🍽️ {recipe.get('portions', 4)} portions"
            ]
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

# INVENTAIRE
def inventory_card(article: Dict, on_adjust: Callable = None, on_add_to_cart: Callable = None,
                   on_delete: Callable = None, key: str = "inv"):
    """Carte article inventaire"""
    statut_colors = {
        "ok": "#d4edda",
        "sous_seuil": "#fff3cd",
        "peremption_proche": "#f8d7da",
        "critique": "#dc3545",
    }
    couleur = statut_colors.get(article.get("statut", "ok"), "#f8f9fa")

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {couleur}; padding: 1rem; '
            f'background: {couleur}; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.markdown(f"### {article['nom']}")
            st.caption(f"{article['categorie']} • {article.get('emplacement', '—')}")

        with col2:
            st.metric("Stock", f"{article['quantite']:.1f} {article['unite']}")

        with col3:
            if on_adjust:
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button("➕", key=f"{key}_plus", help="Ajouter 1"):
                        on_adjust(article["id"], 1.0)
                with col_a2:
                    if st.button("➖", key=f"{key}_minus", help="Retirer 1"):
                        on_adjust(article["id"], -1.0)

# PLANNING
def meal_card(meal: Dict, on_edit: Callable = None, on_delete: Callable = None, key: str = "meal"):
    """Carte repas"""
    if not meal.get("recette"):
        st.info("🍽️ Aucun repas")
        return

    recette = meal["recette"]
    type_icons = {
        "petit_déjeuner": "🌅",
        "déjeuner": "☀️",
        "dîner": "🌙",
        "bébé": "👶"
    }
    icon = type_icons.get(meal.get("type", "dîner"), "🍽️")

    with st.container():
        st.markdown(f"### {icon} {recette['nom']}")
        st.caption(f"{meal['portions']}p • {recette.get('temps_total', 0)}min")

        if on_edit or on_delete:
            col1, col2 = st.columns(2)
            if on_edit:
                with col1:
                    if st.button("✏️ Modifier", key=f"{key}_edit", use_container_width=True):
                        on_edit(meal["id"])
            if on_delete:
                with col2:
                    if st.button("🗑️ Suppr.", key=f"{key}_del", use_container_width=True):
                        on_delete(meal["id"])
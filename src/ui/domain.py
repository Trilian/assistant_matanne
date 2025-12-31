"""
UI Domain Components - Composants Métier
Fusionne ui/domain/recipe_components.py + inventory_component.py + planning_component.py
"""
import streamlit as st
from typing import Dict, List, Optional, Callable
from datetime import date


# ════════════════════════════════════════════════════════════
# RECETTES
# ════════════════════════════════════════════════════════════

def recipe_card(recipe: Dict, on_view: Optional[Callable] = None, on_edit: Optional[Callable] = None,
                on_delete: Optional[Callable] = None, mode: str = "list", key: str = "recipe"):
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


# ════════════════════════════════════════════════════════════
# INVENTAIRE
# ════════════════════════════════════════════════════════════

STATUT_COLORS = {
    "ok": "#d4edda",
    "sous_seuil": "#fff3cd",
    "peremption_proche": "#f8d7da",
    "critique": "#dc3545",
}

STATUT_ICONS = {
    "ok": "✅",
    "sous_seuil": "⚠️",
    "peremption_proche": "⏳",
    "critique": "🔴",
}


def inventory_card(article: Dict, on_adjust: Optional[Callable[[int, float], None]] = None,
                   on_add_to_cart: Optional[Callable[[int], None]] = None, key: str = "inv"):
    """Carte article inventaire"""
    statut = article.get("statut", "ok")
    couleur = STATUT_COLORS.get(statut, "#f8f9fa")
    icone = STATUT_ICONS.get(statut, "📦")

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {couleur}; padding: 1rem; '
            f'background: {couleur}; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.markdown(f"### {icone} {article['nom']}")
            st.caption(f"{article['categorie']} • {article.get('emplacement', '—')}")

            jours = article.get("jours_peremption")
            if jours is not None:
                if jours <= 3:
                    st.error(f"⏳ Périme dans {jours} jour(s)")
                elif jours <= 7:
                    st.warning(f"⏳ Dans {jours} jours")

        with col2:
            qty = article['quantite']
            seuil = article.get('seuil', article.get('quantite_min', 1.0))
            delta_text = None
            if qty < seuil:
                delta_text = f"Seuil: {seuil}"
            st.metric("Stock", f"{qty:.1f} {article['unite']}", delta=delta_text, delta_color="inverse")

        with col3:
            if on_adjust:
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button("➕", key=f"{key}_plus", help="Ajouter 1"):
                        on_adjust(article["id"], 1.0)
                with col_a2:
                    if st.button("➖", key=f"{key}_minus", help="Retirer 1"):
                        on_adjust(article["id"], -1.0)


def stock_alert(articles_critiques: List[Dict], on_click: Optional[Callable[[int], None]] = None,
                key: str = "alert"):
    """Widget alertes stock critique"""
    if not articles_critiques:
        return

    st.warning(f"⚠️ **{len(articles_critiques)} article(s) en alerte**")

    with st.expander("Voir les alertes", expanded=False):
        for idx, article in enumerate(articles_critiques[:5]):
            col1, col2 = st.columns([3, 1])
            with col1:
                statut_icon = STATUT_ICONS.get(article.get("statut"), "⚠️")
                st.write(f"{statut_icon} **{article['nom']}** - {article['quantite']:.1f} {article['unite']}")
            with col2:
                if on_click and st.button("Voir", key=f"{key}_{idx}", use_container_width=True):
                    on_click(article["id"])

        if len(articles_critiques) > 5:
            st.caption(f"... et {len(articles_critiques) - 5} autre(s)")


# ════════════════════════════════════════════════════════════
# PLANNING
# ════════════════════════════════════════════════════════════

TYPES_REPAS_ICONS = {
    "petit_déjeuner": "🌅",
    "déjeuner": "☀️",
    "goûter": "🍪",
    "dîner": "🌙",
    "bébé": "👶",
}


def meal_card(meal: Dict, on_edit: Optional[Callable[[int], None]] = None,
              on_delete: Optional[Callable[[int], None]] = None, key: str = "meal"):
    """Carte repas"""
    if not meal.get("recette"):
        st.info("🍽️ Aucun repas planifié")
        return

    recette = meal["recette"]
    type_repas = meal.get("type", "dîner")
    icon = TYPES_REPAS_ICONS.get(type_repas, "🍽️")

    with st.container():
        st.markdown(f"### {icon} {recette['nom']}")
        st.caption(f"{meal['portions']}p • {recette.get('temps_total', 0)}min")

        if meal.get("est_adapte_bebe"):
            st.caption("👶 Adapté bébé")

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


def week_calendar(planning_data: Dict, on_day_click: Optional[Callable[[int], None]] = None, key: str = "calendar"):
    """Calendrier hebdomadaire"""
    semaine_debut = planning_data.get("semaine_debut")
    st.markdown(f"### 📅 Semaine du {semaine_debut.strftime('%d/%m/%Y')}")

    cols = st.columns(7)

    for jour_data in planning_data.get("jours", []):
        jour_idx = jour_data["jour_idx"]
        is_today = jour_data["date"] == date.today()

        with cols[jour_idx]:
            if is_today:
                st.markdown(f"**🔵 {jour_data['nom_jour'][:3]}**")
            else:
                st.markdown(f"**{jour_data['nom_jour'][:3]}**")

            st.caption(jour_data["date"].strftime("%d/%m"))

            repas = jour_data.get("repas", [])
            if repas:
                for idx, meal in enumerate(repas[:2]):
                    icon = TYPES_REPAS_ICONS.get(meal.get("type"), "🍽️")
                    recette_nom = meal.get("recette", {}).get("nom", "—")
                    st.caption(f"{icon} {recette_nom[:12]}...")
                if len(repas) > 2:
                    st.caption(f"+{len(repas) - 2}")
            else:
                st.caption("Vide")

            if on_day_click and st.button("➕", key=f"{key}_add_{jour_idx}", use_container_width=True):
                on_day_click(jour_idx)
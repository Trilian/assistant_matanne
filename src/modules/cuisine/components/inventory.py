"""
Composants UI - Inventaire
Cartes et widgets spécifiques inventaire
"""
import streamlit as st
from typing import Dict, List, Optional, Callable

from src.utils.constants import STATUT_COLORS


STATUT_ICONS = {
    "ok": "✅",
    "sous_seuil": "⚠️",
    "peremption_proche": "⏳",
    "critique": "🔴",
}


def inventory_card(
        article: Dict,
        on_adjust: Optional[Callable[[int, float], None]] = None,
        on_add_to_cart: Optional[Callable[[int], None]] = None,
        key: str = "inv"
):
    """
    Carte article inventaire

    Args:
        article: Dict article
        on_adjust: Callback (article_id, delta)
        on_add_to_cart: Callback (article_id)
        key: Clé unique
    """
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

            if on_add_to_cart:
                if st.button("🛒", key=f"{key}_cart", use_container_width=True):
                    on_add_to_cart(article["id"])


def stock_alert(
        articles_critiques: List[Dict],
        on_click: Optional[Callable[[int], None]] = None,
        key: str = "alert"
):
    """
    Widget alertes stock critique

    Args:
        articles_critiques: Liste articles en alerte
        on_click: Callback (article_id)
        key: Clé unique
    """
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


def inventory_stats_widget(stats: Dict):
    """
    Widget stats inventaire

    Args:
        stats: Dict stats {total, stock_bas, peremption, critiques}
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Articles", stats.get("total", 0))

    with col2:
        stock_bas = stats.get("stock_bas", 0)
        st.metric("Stock Bas", stock_bas, delta="⚠️" if stock_bas > 0 else None)

    with col3:
        peremption = stats.get("peremption", 0)
        st.metric("Péremption", peremption, delta="⏳" if peremption > 0 else None)

    with col4:
        critiques = stats.get("critiques", 0)
        st.metric("Critiques", critiques, delta="🔴" if critiques > 0 else None)


def inventory_category_filter(categories: List[str], on_change: Callable):
    """
    Filtre par catégorie

    Args:
        categories: Liste catégories
        on_change: Callback (selected_category)
    """
    selected = st.selectbox(
        "Catégorie",
        ["Toutes"] + categories,
        key="inventory_category_filter"
    )

    if selected != "Toutes":
        on_change(selected)
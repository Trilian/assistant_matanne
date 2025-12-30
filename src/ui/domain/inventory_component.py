"""
Composants UI - INVENTAIRE
Composants spécialisés pour l'inventaire
"""
import streamlit as st
from typing import Dict, List, Optional, Callable
from datetime import date


# Couleurs par statut
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


def inventory_card(
        article: Dict,
        on_adjust: Optional[Callable[[int, float], None]] = None,
        on_add_to_cart: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        show_actions: bool = True,
        key: str = "inv"
):
    """
    Carte article inventaire

    Args:
        article: {
            "id": int,
            "nom": str,
            "categorie": str,
            "quantite": float,
            "unite": str,
            "seuil": float,
            "emplacement": str,
            "statut": str,
            "jours_peremption": int,
            "date_peremption": date
        }
        on_adjust: Callback(article_id, delta)
        on_add_to_cart: Callback(article_id)
        on_delete: Callback(article_id)
        show_actions: Afficher actions
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

        # Colonne 1 : Infos
        with col1:
            st.markdown(f"### {icone} {article['nom']}")
            st.caption(f"{article['categorie']} • {article.get('emplacement', '—')}")

            # Alerte péremption
            jours = article.get("jours_peremption")
            if jours is not None:
                if jours <= 3:
                    st.error(f"⏳ Périme dans {jours} jour(s)")
                elif jours <= 7:
                    st.warning(f"⏳ Dans {jours} jours")

        # Colonne 2 : Stock
        with col2:
            qty = article['quantite']
            seuil = article.get('seuil', article.get('quantite_min', 1.0))

            delta_text = None
            delta_color = "off"

            if qty < seuil:
                delta_text = f"Seuil: {seuil}"
                delta_color = "inverse"

            st.metric(
                "Stock",
                f"{qty:.1f} {article['unite']}",
                delta=delta_text,
                delta_color=delta_color
            )

        # Colonne 3 : Actions
        with col3:
            if show_actions:
                col_a1, col_a2, col_a3 = st.columns(3)

                with col_a1:
                    if on_adjust and st.button("➕", key=f"{key}_plus", help="Ajouter 1"):
                        on_adjust(article["id"], 1.0)

                with col_a2:
                    if on_adjust and st.button("➖", key=f"{key}_minus", help="Retirer 1"):
                        on_adjust(article["id"], -1.0)

                with col_a3:
                    if on_add_to_cart and st.button("🛒", key=f"{key}_cart", help="→ Courses"):
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
        on_click: Callback(article_id)
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

                # Raison alerte
                if article.get("jours_peremption") and article["jours_peremption"] <= 7:
                    st.caption(f"⏳ Péremption dans {article['jours_peremption']}j")
                elif article['quantite'] < article.get('seuil', 1.0):
                    st.caption(f"📉 Stock bas (seuil: {article['seuil']:.1f})")

            with col2:
                if on_click and st.button("Voir", key=f"{key}_{idx}", use_container_width=True):
                    on_click(article["id"])

        if len(articles_critiques) > 5:
            st.caption(f"... et {len(articles_critiques) - 5} autre(s)")


def inventory_stats(stats: Dict, key: str = "stats"):
    """
    Widget stats inventaire

    Args:
        stats: {
            "total_articles": int,
            "total_stock_bas": int,
            "total_peremption": int,
            "total_critiques": int
        }
        key: Clé unique
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Articles", stats.get("total_articles", 0))

    with col2:
        st.metric(
            "Stock Bas",
            stats.get("total_stock_bas", 0),
            delta_color="inverse"
        )

    with col3:
        st.metric(
            "Péremption",
            stats.get("total_peremption", 0),
            delta_color="inverse"
        )

    with col4:
        st.metric(
            "⚠️ Critiques",
            stats.get("total_critiques", 0),
            delta_color="inverse"
        )


def inventory_filters(
        categories: List[str],
        emplacements: List[str],
        on_filter: Callable[[Dict], None],
        key: str = "inv_filters"
) -> Dict:
    """
    Filtres inventaire

    Args:
        categories: Liste catégories disponibles
        emplacements: Liste emplacements
        on_filter: Callback(filters)
        key: Clé unique

    Returns:
        Dict filtres sélectionnés
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        categorie = st.selectbox(
            "Catégorie",
            ["Toutes"] + categories,
            key=f"{key}_cat"
        )

    with col2:
        emplacement = st.selectbox(
            "Emplacement",
            ["Tous"] + emplacements,
            key=f"{key}_emp"
        )

    with col3:
        statut = st.selectbox(
            "Statut",
            ["Tous", "ok", "sous_seuil", "peremption_proche", "critique"],
            key=f"{key}_stat"
        )

    filters = {
        "categorie": None if categorie == "Toutes" else categorie,
        "emplacement": None if emplacement == "Tous" else emplacement,
        "statut": None if statut == "Tous" else statut
    }

    if st.button("🔄 Appliquer", key=f"{key}_apply"):
        on_filter(filters)

    return filters


def quick_add_form(
        categories: List[str],
        emplacements: List[str],
        on_submit: Callable[[Dict], None],
        key: str = "quick_add"
):
    """
    Formulaire ajout rapide

    Args:
        categories: Liste catégories
        emplacements: Liste emplacements
        on_submit: Callback(data)
        key: Clé unique
    """
    with st.form(f"{key}_form"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom *", key=f"{key}_nom")
            categorie = st.selectbox("Catégorie", categories, key=f"{key}_cat")
            quantite = st.number_input("Quantité *", 0.1, 1000.0, 1.0, 0.1, key=f"{key}_qty")

        with col2:
            unite = st.selectbox("Unité", ["pcs", "kg", "g", "L", "mL"], key=f"{key}_unit")
            emplacement = st.selectbox("Emplacement", emplacements, key=f"{key}_emp")
            seuil = st.number_input("Seuil", 0.1, 100.0, 1.0, 0.1, key=f"{key}_seuil")

        date_peremption = st.date_input("Péremption (optionnel)", value=None, key=f"{key}_date")

        submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)

        if submitted:
            if not nom:
                st.error("Le nom est obligatoire")
            else:
                data = {
                    "nom": nom,
                    "categorie": categorie,
                    "quantite": quantite,
                    "unite": unite,
                    "seuil": seuil,
                    "emplacement": emplacement,
                    "date_peremption": date_peremption
                }
                on_submit(data)
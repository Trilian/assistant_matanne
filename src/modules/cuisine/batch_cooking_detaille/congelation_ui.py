"""
Page Congélation — Gestion du stock congélateur et étiquettes.

Interface pour le suivi des articles congelés,
planification de décongélation et impression d'étiquettes.
"""

import logging
from datetime import date

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("congelation")


def afficher_congelation() -> None:
    """Affiche l'interface de gestion congélation."""
    st.subheader("🧊 Stock Congélateur")
    st.caption("Gérez votre congélateur et planifiez la décongélation")

    TAB_LABELS = ["📦 Stock", "📅 Décongélation", "🏷️ Étiquettes"]
    tab_stock, tab_decongel, tab_etiquettes = st.tabs(TAB_LABELS)

    with tab_stock:
        with error_boundary(titre="Erreur stock congélation"):
            _afficher_stock_congele()

    with tab_decongel:
        with error_boundary(titre="Erreur décongélation"):
            _afficher_plan_decongelation()

    with tab_etiquettes:
        with error_boundary(titre="Erreur étiquettes"):
            _afficher_etiquettes()


def _afficher_stock_congele() -> None:
    """Affiche le stock du congélateur."""
    from src.services.cuisine.batch_cooking.congelation import lister_articles_congeles

    articles = lister_articles_congeles()

    if not articles:
        st.info("🧊 Congélateur vide. Ajoutez des articles depuis le batch cooking !")

        # Formulaire d'ajout rapide
        _formulaire_ajout()
        return

    # Métriques
    urgents = [a for a in articles if a.urgence >= 2]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Articles congelés", len(articles))
    with col2:
        st.metric("À consommer bientôt", len(urgents))
    with col3:
        categories = set(getattr(a, "categorie", "Autre") for a in articles)
        st.metric("Catégories", len(categories))

    st.divider()

    # Articles triés par urgence
    articles_triees = sorted(articles, key=lambda a: a.jours_restants)

    for art in articles_triees:
        urgence_emoji = ["🟢", "🟡", "🟠", "🔴"][min(art.urgence, 3)]
        jours = art.jours_restants

        col_nom, col_date, col_jours = st.columns([3, 2, 1])
        with col_nom:
            st.markdown(f"{urgence_emoji} **{art.nom}** — {art.notes or ''}")
        with col_date:
            st.caption(f"Congelé le {art.date_congelation}")
        with col_jours:
            if jours <= 0:
                st.error("Expiré !")
            elif jours <= 30:
                st.warning(f"{jours}j")
            else:
                st.caption(f"{jours}j")

    st.divider()
    _formulaire_ajout()


def _formulaire_ajout() -> None:
    """Formulaire d'ajout d'un article congelé."""
    from src.services.cuisine.batch_cooking.congelation import creer_article_congele

    with st.expander("➕ Ajouter au congélateur"):
        col1, col2, col3 = st.columns(3)

        with col1:
            nom = st.text_input("Nom", placeholder="Ex: Soupe de légumes", key=_keys("ajout_nom"))
        with col2:
            quantite = st.text_input(
                "Quantité", placeholder="500g, 2 portions...", key=_keys("ajout_quantite")
            )
        with col3:
            categorie = st.selectbox(
                "Catégorie",
                ["viande", "poisson", "légumes", "plat_cuisine", "sauce", "pain", "autre"],
                key=_keys("ajout_cat"),
            )

        if st.button("🧊 Congeler", key=_keys("btn_congeler"), type="primary", disabled=not nom):
            try:
                creer_article_congele(
                    nom=nom,
                    quantite=quantite,
                    categorie=categorie,
                )
                st.success(f"✅ {nom} ajouté au congélateur !")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")


def _afficher_plan_decongelation() -> None:
    """Plan de décongélation pour la semaine."""
    from src.services.cuisine.batch_cooking.congelation import (
        generer_plan_decongelation,
        lister_articles_congeles,
    )

    stock = lister_articles_congeles()
    plan = generer_plan_decongelation(stock, jours_avance=7)

    if not plan or not plan.articles_a_sortir:
        st.info("Pas d'articles à décongeler cette semaine.")
        return

    # Afficher les articles urgents et à sortir
    if plan.articles_expires:
        st.error(f"❌ {len(plan.articles_expires)} article(s) expiré(s) à jeter")
        for art in plan.articles_expires:
            st.markdown(f"  🗑️ {art.nom} (expiré depuis {abs(art.jours_restants)}j)")

    if plan.articles_urgents:
        st.warning(f"⚠️ {len(plan.articles_urgents)} article(s) urgent(s) (< 7 jours)")
        for art in plan.articles_urgents:
            st.markdown(f"  🧊→🍽️ {art.nom} ({art.jours_restants}j restants)")

    if plan.articles_a_sortir:
        st.info(f"📅 {len(plan.articles_a_sortir)} article(s) à prévoir cette semaine")
        for art in plan.articles_a_sortir:
            st.markdown(f"  🧊 {art.nom} ({art.jours_restants}j restants)")


def _afficher_etiquettes() -> None:
    """Génère des étiquettes imprimables pour le congélateur."""
    from src.services.cuisine.batch_cooking.congelation import (
        generer_etiquettes_html,
        lister_articles_congeles,
    )

    articles = lister_articles_congeles()

    if not articles:  # noqa: SIM108
        st.info("Aucun article. Ajoutez d'abord des articles au congélateur.")
        return

    # Sélection des articles pour étiquettes
    noms = [a.nom for a in articles]
    selected = st.multiselect(
        "Articles à étiqueter",
        options=noms,
        default=noms[:5],
        key=_keys("etiq_select"),
    )

    if selected and st.button("🖨️ Générer étiquettes", key=_keys("btn_etiquettes")):
        articles_selects = [a for a in articles if a.nom in selected]
        html = generer_etiquettes_html(articles_selects)

        st.components.v1.html(html, height=400, scrolling=True)
        st.caption("Utilisez Ctrl+P pour imprimer (format A4, 3 colonnes).")


__all__ = ["afficher_congelation"]

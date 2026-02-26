"""
Page Producteurs Bio & Local — Annuaire et guide d'achat local.

Affiche les producteurs locaux disponibles, avec mise en relation
avec la liste de courses et recommandations par saison.
"""

import logging

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("producteurs_local")


def app():
    """Point d'entrée du module Bio & Local."""
    st.title("🌾 Bio & Local")
    st.caption("Découvrez les producteurs locaux et circuits courts")

    TAB_LABELS = ["📍 Producteurs", "🛒 Guide d'achat", "🌿 Saison"]

    tab_producteurs, tab_guide, tab_saison = st.tabs(TAB_LABELS)

    with tab_producteurs:
        with error_boundary(titre="Erreur producteurs"):
            _afficher_producteurs()

    with tab_guide:
        with error_boundary(titre="Erreur guide"):
            _afficher_guide_local()

    with tab_saison:
        with error_boundary(titre="Erreur saison"):
            _afficher_saison()


def _afficher_producteurs() -> None:
    """Liste des producteurs enregistrés."""
    from src.services.cuisine.local.producteurs import obtenir_producteurs_actifs

    producteurs = obtenir_producteurs_actifs()

    if not producteurs:
        st.info("Aucun producteur enregistré. Les producteurs par défaut seront utilisés.")

    from src.services.cuisine.local.producteurs import PRODUCTEURS_DEFAUT

    tous = PRODUCTEURS_DEFAUT + producteurs

    for p in tous:
        with st.container():
            col_info, col_tags, col_link = st.columns([3, 2, 1])

            with col_info:
                st.markdown(f"### {p.nom}")
                if hasattr(p, "adresse") and p.adresse:
                    st.caption(f"📍 {p.adresse}")

            with col_tags:
                tags = getattr(p, "tags", []) or []
                if tags:
                    st.markdown(" ".join(f"`{t}`" for t in tags))
                type_label = getattr(p, "type_magasin", "")
                if type_label:
                    st.markdown(f"🏷️ {type_label}")

            with col_link:
                url = getattr(p, "url", None)
                if url:
                    st.link_button("🔗 Site web", url)

            # Catégories disponibles
            categories = getattr(p, "categories", []) or []
            if categories:
                st.markdown(f"**Produits:** {', '.join(categories)}")

            st.divider()


def _afficher_guide_local() -> None:
    """Guide d'achat local — croise la liste de courses avec les producteurs."""
    from src.services.cuisine.local.producteurs import generer_guide_local

    with st.spinner("Génération du guide..."):
        guide = generer_guide_local()

    if not guide or not guide.recommandations:
        st.info("Pas de recommandation pour le moment. Ajoutez des articles à votre liste !")
        return

    st.metric("Articles trouvables en local", guide.nb_articles_locaux)

    for reco in guide.recommandations:
        st.markdown(
            f"🥕 **{reco.article}** → {reco.producteur_nom} "
            f"({'✅ disponible' if reco.disponible else '❓ à vérifier'})"
        )

    if guide.economie_estimee:
        st.success(f"💰 Économie estimée : {guide.economie_estimee:.0f} €")


def _afficher_saison() -> None:
    """Affiche les ingrédients de saison enrichis."""
    from src.services.cuisine.suggestions.saisons_enrichi import (
        obtenir_ingredients_saison_enrichis,
        obtenir_paires_saison,
    )

    ingredients = obtenir_ingredients_saison_enrichis()
    paires = obtenir_paires_saison()

    if ingredients:
        st.markdown("### 🌿 En saison actuellement")

        # Grouper par catégorie
        categories: dict[str, list] = {}
        for ing in ingredients:
            cat = getattr(ing, "categorie", "Autre")
            categories.setdefault(cat, []).append(ing)

        for cat, items in sorted(categories.items()):
            with st.expander(f"**{cat}** ({len(items)})", expanded=True):
                cols = st.columns(3)
                for i, item in enumerate(items):
                    with cols[i % 3]:
                        bio = "🌿" if getattr(item, "bio_local_courant", False) else ""
                        st.markdown(f"{bio} {item.nom}")

    if paires:
        st.markdown("### 🤝 Associations de saison")
        for p in paires[:8]:
            st.markdown(f"• **{p[0]}** + **{p[1]}**")


__all__ = ["app"]

"""
Génération automatique de courses — Planning, Inventaire, Recettes.

Fusionne les anciens planning.py et suggestions_ia.py.
"""

import logging
import time

import pandas as pd
import streamlit as st

from src.core.session_keys import SK
from src.core.state import naviguer, rerun
from src.services.cuisine.courses import (
    obtenir_service_courses,
    obtenir_service_courses_intelligentes,
)
from src.services.cuisine.recettes import obtenir_service_recettes
from src.services.inventaire import obtenir_service_inventaire
from src.ui.components.atoms import etat_vide
from src.ui.fragments import ui_fragment

logger = logging.getLogger(__name__)


@ui_fragment
def afficher_generation():
    """Point d'entrée — 3 sous-onglets de génération."""
    st.subheader("🤖 Génération automatique")

    tab_planning, tab_inventaire, tab_recettes = st.tabs(
        ["🍽️ Depuis Planning", "📦 Depuis Inventaire", "🍳 Depuis Recette"]
    )

    with tab_planning:
        _afficher_depuis_planning()

    with tab_inventaire:
        _afficher_depuis_inventaire()

    with tab_recettes:
        _afficher_depuis_recettes()


# ═══════════════════════════════════════════════════════════
# DEPUIS PLANNING
# ═══════════════════════════════════════════════════════════


def _afficher_depuis_planning():
    """Génère la liste de courses depuis le planning repas actif."""
    st.info(
        "**Génération automatique** basée sur votre planning de repas. "
        "Le système analyse les recettes, compare avec l'inventaire et génère une liste optimisée."
    )

    service = obtenir_service_courses_intelligentes()
    planning = service.obtenir_planning_actif()

    if not planning:
        st.warning("⚠️ Aucun planning actif trouvé.")
        st.caption("Créez d'abord un planning de repas dans 'Cuisine → Planning Semaine'")
        if st.button("📅 Aller au planning", use_container_width=True):
            naviguer("cuisine_repas")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.success(f"✅ Planning actif: **{planning.nom}**")
        nb_repas = len(planning.repas) if planning.repas else 0
        st.caption(
            f"📅 Du {planning.semaine_debut} au {planning.semaine_fin} • {nb_repas} repas planifiés"
        )
    with col2:
        if st.button("🔄 Générer la liste", type="primary", use_container_width=True):
            with st.spinner("Analyse du planning en cours..."):
                resultat = service.generer_liste_courses()
                st.session_state[SK.COURSES_PLANNING_RESULTAT] = resultat
                rerun()

    st.divider()

    resultat = st.session_state.get(SK.COURSES_PLANNING_RESULTAT)

    if resultat:
        _afficher_resultat_planning(service, resultat)
    else:
        st.markdown(
            """
        ### Comment ça marche ?

        1. **Analyse** — Le système parcourt toutes les recettes de votre planning
        2. **Extraction** — Les ingrédients sont extraits et regroupés
        3. **Comparaison** — Vérification avec votre inventaire actuel
        4. **Optimisation** — Seuls les articles manquants sont listés
        5. **Organisation** — Tri par rayon pour faciliter vos courses

        Cliquez sur **"Générer la liste"** pour commencer.
        """
        )


def _afficher_resultat_planning(service, resultat):
    """Affiche le résultat de la génération depuis le planning."""
    for alerte in resultat.alertes:
        if "✅" in alerte:
            st.success(alerte)
        elif "⚠️" in alerte:
            st.warning(alerte)
        else:
            st.info(alerte)

    if not resultat.articles:
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🛒 Articles à acheter", resultat.total_articles)
    with col2:
        st.metric("🍳 Recettes couvertes", len(resultat.recettes_couvertes))
    with col3:
        rayons = set(a.rayon for a in resultat.articles)
        st.metric("📦 Rayons", len(rayons))

    if resultat.recettes_couvertes:
        st.markdown("**Recettes concernées:**")
        st.caption(", ".join(resultat.recettes_couvertes[:5]))

    st.divider()
    st.subheader("📋 Articles à acheter")

    articles_par_rayon: dict[str, list] = {}
    for article in resultat.articles:
        articles_par_rayon.setdefault(article.rayon, []).append(article)

    articles_selectionnes = []
    for rayon in sorted(articles_par_rayon.keys()):
        articles = articles_par_rayon[rayon]
        priorite_emoji = {1: "🔴", 2: "🟡", 3: "🟢"}.get(articles[0].priorite, "⚪")

        with st.expander(f"{priorite_emoji} {rayon} ({len(articles)} articles)", expanded=True):
            for i, article in enumerate(articles):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    selected = st.checkbox(
                        f"**{article.nom}**", value=True, key=f"art_sel_{rayon}_{i}"
                    )
                    if selected:
                        articles_selectionnes.append(article)
                    sources = ", ".join(article.recettes_source[:2])
                    st.caption(f"📝 {sources}")
                with col2:
                    st.markdown(f"**{article.a_acheter:.0f}** {article.unite}")
                with col3:
                    if article.en_stock > 0:
                        st.caption(f"(en stock: {article.en_stock:.0f})")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            f"✅ Ajouter {len(articles_selectionnes)} articles à la liste",
            type="primary",
            use_container_width=True,
            disabled=len(articles_selectionnes) == 0,
        ):
            with st.spinner("Ajout en cours..."):
                ids = service.ajouter_a_liste_courses(articles_selectionnes)
                if ids:
                    st.success(f"✅ {len(ids)} articles ajoutés à votre liste de courses!")
                    del st.session_state[SK.COURSES_PLANNING_RESULTAT]
                    st.session_state[SK.COURSES_REFRESH] += 1
                    rerun()
    with col2:
        if st.button("🔄 Régénérer", use_container_width=True):
            del st.session_state[SK.COURSES_PLANNING_RESULTAT]
            rerun()


# ═══════════════════════════════════════════════════════════
# DEPUIS INVENTAIRE
# ═══════════════════════════════════════════════════════════


def _afficher_depuis_inventaire():
    """Génère des suggestions depuis le stock bas."""
    service = obtenir_service_courses()
    st.write("**Générer suggestions depuis stock bas**")

    if st.button("🤖 Analyser inventaire & générer suggestions"):
        with st.spinner("⏳ Analyse en cours..."):
            try:
                suggestions = service.generer_suggestions_ia_depuis_inventaire()

                if suggestions:
                    st.success(f"✅ {len(suggestions)} suggestions générées!")

                    df = pd.DataFrame(
                        [
                            {
                                "Article": s.nom,
                                "Quantité": f"{s.quantite} {s.unite}",
                                "Priorité": s.priorite,
                                "Rayon": s.rayon,
                            }
                            for s in suggestions
                        ]
                    )
                    st.dataframe(df, use_container_width=True)

                    if st.button("✅ Ajouter toutes les suggestions"):
                        try:
                            count = service.ajouter_suggestions_en_masse(suggestions)
                            st.success(f"✅ {count} articles ajoutés!")
                            st.session_state[SK.COURSES_REFRESH] += 1
                            time.sleep(0.5)
                        except Exception as e:
                            st.error(f"❌ Erreur sauvegarde: {str(e)}")
                else:
                    etat_vide("Aucune suggestion", "✅", "Votre inventaire est complet")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# DEPUIS RECETTES
# ═══════════════════════════════════════════════════════════


def _afficher_depuis_recettes():
    """Ajoute les ingrédients manquants pour une recette sélectionnée."""
    service = obtenir_service_courses()
    recettes_service = obtenir_service_recettes()

    st.write("**Ajouter ingrédients manquants pour recettes**")

    if recettes_service is None:
        st.warning("⚠️ Service recettes indisponible")
        return

    try:
        recettes = recettes_service.get_all()

        if not recettes:
            etat_vide(
                "Aucune recette disponible",
                "🍳",
                "Ajoutez des recettes pour générer des suggestions",
            )
            return

        recette_names = {r.id: r.nom for r in recettes}
        selected_recette_id = st.selectbox(
            "Sélectionner une recette",
            options=list(recette_names.keys()),
            format_func=lambda x: recette_names[x],
            key="select_recette_courses",
        )

        if not selected_recette_id:
            return

        recette = recettes_service.get_by_id_full(selected_recette_id)
        if not recette:
            return

        nb_ingredients = len(recette.ingredients) if recette.ingredients else 0
        st.caption(f"📝 {nb_ingredients} ingrédients")

        if st.button("🔍 Ajouter ingrédients manquants", key="btn_add_missing_ingredients"):
            try:
                ingredients_recette = recette.ingredients if recette.ingredients else []

                if not ingredients_recette:
                    st.warning("Aucun ingrédient dans cette recette")
                    return

                ingredients_data = []
                for ing_obj in ingredients_recette:
                    ing_nom = (
                        ing_obj.ingredient.nom if hasattr(ing_obj, "ingredient") else ing_obj.nom
                    )
                    ing_quantite = ing_obj.quantite if hasattr(ing_obj, "quantite") else 1
                    ing_unite = (
                        ing_obj.ingredient.unite
                        if hasattr(ing_obj, "ingredient") and hasattr(ing_obj.ingredient, "unite")
                        else "pièce"
                    )
                    if ing_nom:
                        ingredients_data.append(
                            {"nom": ing_nom, "quantite": ing_quantite, "unite": ing_unite}
                        )

                count_added = service.ajouter_ingredients_recette(
                    ingredients_data=ingredients_data,
                    recette_nom=recette.nom,
                )
                st.success(f"✅ {count_added} ingrédient(s) ajouté(s) à la liste!")
                st.session_state[SK.COURSES_REFRESH] += 1
                time.sleep(0.5)
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur ajout ingrédients recette: {e}")

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render tab recettes: {e}")


__all__ = ["afficher_generation"]

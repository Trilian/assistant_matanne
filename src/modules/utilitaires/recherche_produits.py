"""
Module Recherche Produits - Interface Streamlit

Recherche de produits alimentaires via OpenFoodFacts.
Scan code-barres ou recherche par nom avec détails nutritionnels.
"""

import logging

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.modules._framework import error_boundary
from src.ui import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

_keys = KeyNamespace("recherche_produits")

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def _afficher_nutriscore(grade: str | None):
    """Affiche le Nutri-Score avec couleur."""
    couleurs = {"a": "🟢", "b": "🟡", "c": "🟠", "d": "🔴", "e": "⛔"}
    if grade:
        icon = couleurs.get(grade.lower(), "⬜")
        st.markdown(f"**Nutri-Score:** {icon} **{grade.upper()}**")
    else:
        st.caption("Nutri-Score: non disponible")


def _afficher_nova(group: int | None):
    """Affiche le groupe NOVA de transformation."""
    descriptions = {
        1: "🥬 Non transformé",
        2: "🧂 Ingrédient culinaire",
        3: "🥫 Transformé",
        4: "🍕 Ultra-transformé",
    }
    if group and group in descriptions:
        st.markdown(f"**NOVA:** {descriptions[group]}")
    else:
        st.caption("NOVA: non disponible")


def _afficher_nutrition(nutrition):
    """Affiche le tableau nutritionnel."""
    if nutrition is None:
        st.info("Informations nutritionnelles non disponibles")
        return

    st.markdown("#### 📊 Valeurs nutritionnelles (100g)")

    col1, col2 = st.columns(2)
    with col1:
        if nutrition.energie_kcal is not None:
            st.metric("🔥 Énergie", f"{nutrition.energie_kcal:.0f} kcal")
        if nutrition.proteines_g is not None:
            st.metric("💪 Protéines", f"{nutrition.proteines_g:.1f} g")
        if nutrition.glucides_g is not None:
            st.metric("🍞 Glucides", f"{nutrition.glucides_g:.1f} g")
        if nutrition.fibres_g is not None:
            st.metric("🌾 Fibres", f"{nutrition.fibres_g:.1f} g")

    with col2:
        if nutrition.lipides_g is not None:
            st.metric("🫒 Lipides", f"{nutrition.lipides_g:.1f} g")
        if nutrition.satures_g is not None:
            st.metric("🧈 Saturés", f"{nutrition.satures_g:.1f} g")
        if nutrition.sucres_g is not None:
            st.metric("🍬 Sucres", f"{nutrition.sucres_g:.1f} g")
        if nutrition.sel_g is not None:
            st.metric("🧂 Sel", f"{nutrition.sel_g:.2f} g")


def _afficher_produit(produit):
    """Affiche les détails complets d'un produit."""
    # En-tête avec image
    col_info, col_img = st.columns([3, 1])

    with col_info:
        st.markdown(f"### {produit.nom}")
        if produit.marque:
            st.caption(f"🏷️ {produit.marque}")
        if produit.quantite:
            st.caption(f"📦 {produit.quantite}")
        st.caption(f"🔢 Code: {produit.code_barres}")

    with col_img:
        if produit.image_url:
            st.image(produit.image_url, width=150)

    # Scores
    col_ns, col_nova, col_eco = st.columns(3)
    with col_ns:
        _afficher_nutriscore(produit.nutrition.nutriscore if produit.nutrition else None)
    with col_nova:
        _afficher_nova(produit.nutrition.nova_group if produit.nutrition else None)
    with col_eco:
        if produit.nutrition and produit.nutrition.ecoscore:
            st.markdown(f"**Éco-Score:** {produit.nutrition.ecoscore.upper()}")

    st.markdown("---")

    # Nutrition
    _afficher_nutrition(produit.nutrition)

    # Informations supplémentaires
    with st.expander("📋 Détails", expanded=False):
        if produit.categories:
            st.markdown(f"**Catégories:** {', '.join(produit.categories[:5])}")

        if produit.labels:
            labels_str = " • ".join(f"🏷️ {l}" for l in produit.labels[:5])
            st.markdown(f"**Labels:** {labels_str}")

        if produit.ingredients_texte:
            st.markdown(f"**Ingrédients:** {produit.ingredients_texte[:300]}")

        if produit.allergenes:
            st.warning(f"⚠️ **Allergènes:** {', '.join(produit.allergenes)}")

        if produit.traces:
            st.caption(f"Traces possibles: {', '.join(produit.traces)}")


def _afficher_resultats_recherche(resultats: list):
    """Affiche une liste de résultats de recherche."""
    if not resultats:
        etat_vide("Aucun produit trouvé", "🔍")
        return

    st.success(f"✅ {len(resultats)} produit(s) trouvé(s)")

    for i, produit in enumerate(resultats):
        with st.expander(
            f"{produit.nom} {f'- {produit.marque}' if produit.marque else ''} "
            f"{f'({produit.quantite})' if produit.quantite else ''}",
            expanded=(i == 0),
        ):
            _afficher_produit(produit)


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("recherche_produits")
def app():
    """Point d'entrée module recherche produits."""
    st.title("🔍 Recherche Produits")
    st.caption("Informations nutritionnelles via OpenFoodFacts")

    # Onglets
    TAB_LABELS = ["🔢 Code-barres", "🔍 Recherche", "⭐ Favoris"]
    tabs_with_url(TAB_LABELS, param="tab")
    onglet_barcode, onglet_recherche, onglet_favoris = st.tabs(TAB_LABELS)

    # ─── Onglet Code-barres ───
    with onglet_barcode:
        with error_boundary(titre="Erreur recherche code-barres"):
            st.markdown("### 🔢 Recherche par code-barres")
            st.markdown(
                "Entrez le code-barres (EAN-13) d'un produit alimentaire "
                "pour obtenir ses informations nutritionnelles."
            )

            code = st.text_input(
                "Code-barres",
                placeholder="Ex: 3017620422003 (Nutella)",
                max_chars=14,
            )

            if st.button("🔍 Rechercher", key="btn_barcode", type="primary"):
                if not code or len(code) < 8:
                    st.warning("Veuillez entrer un code-barres valide (8-14 chiffres)")
                else:
                    with st.spinner("🔍 Recherche en cours..."):
                        try:
                            from src.services.integrations.produit import (
                                get_openfoodfacts_service,
                            )

                            service = get_openfoodfacts_service()
                            produit = service.rechercher_produit(code.strip())

                            if produit:
                                _afficher_produit(produit)

                                # Sauvegarder dans favoris
                                if st.button("⭐ Ajouter aux favoris"):
                                    if SK.PRODUITS_FAVORIS not in st.session_state:
                                        st.session_state[SK.PRODUITS_FAVORIS] = []
                                    st.session_state[SK.PRODUITS_FAVORIS].append(
                                        {
                                            "code": produit.code_barres,
                                            "nom": produit.nom,
                                            "marque": produit.marque,
                                            "nutriscore": (
                                                produit.nutrition.nutriscore
                                                if produit.nutrition
                                                else None
                                            ),
                                        }
                                    )
                                    st.success("⭐ Ajouté aux favoris !")
                            else:
                                st.warning(
                                    f"Produit non trouvé pour le code {code}. "
                                    "Vérifiez le code ou essayez la recherche par nom."
                                )
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                            logger.error(f"Erreur recherche produit: {e}")

    # ─── Onglet Recherche par nom ───
    with onglet_recherche:
        with error_boundary(titre="Erreur recherche produit"):
            st.markdown("### 🔍 Recherche par nom")

            terme = st.text_input(
                "Nom du produit",
                placeholder="Ex: yaourt nature, pâtes complètes...",
            )

            col_limite, col_btn = st.columns([1, 2])
            with col_limite:
                limite = st.selectbox("Résultats max", [5, 10, 20], index=1)

            if st.button("🔍 Rechercher", key="btn_nom", type="primary"):
                if not terme or len(terme) < 2:
                    st.warning("Entrez au moins 2 caractères")
                else:
                    with st.spinner(f"🔍 Recherche de '{terme}'..."):
                        try:
                            from src.services.integrations.produit import (
                                get_openfoodfacts_service,
                            )

                            service = get_openfoodfacts_service()
                            resultats = service.rechercher_par_nom(terme.strip(), limite=limite)
                            _afficher_resultats_recherche(resultats)
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                            logger.error(f"Erreur recherche par nom: {e}")

    # ─── Onglet Favoris ───
    with onglet_favoris:
        with error_boundary(titre="Erreur favoris produits"):
            st.markdown("### ⭐ Produits favoris")
            favoris = st.session_state.get(SK.PRODUITS_FAVORIS, [])

            if not favoris:
                st.info(
                    "Aucun produit favori. Recherchez un produit puis cliquez "
                    "sur ⭐ pour l'ajouter."
                )
            else:
                st.caption(f"{len(favoris)} produit(s) en favoris")

                for i, fav in enumerate(favoris):
                    col_info, col_action = st.columns([4, 1])
                    with col_info:
                        ns = fav.get("nutriscore", "")
                        ns_display = f" | Nutri-Score {ns.upper()}" if ns else ""
                        marque = fav.get("marque", "")
                        marque_display = f" ({marque})" if marque else ""
                        st.markdown(f"**{fav['nom']}**{marque_display}{ns_display}")
                        st.caption(f"Code: {fav['code']}")

                    with col_action:
                        if st.button("🗑️", key=f"del_fav_{i}"):
                            st.session_state[SK.PRODUITS_FAVORIS].pop(i)
                            st.rerun()

                if st.button("🗑️ Effacer tous les favoris"):
                    st.session_state[SK.PRODUITS_FAVORIS] = []
                    st.rerun()

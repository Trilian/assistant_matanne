"""
Widget "Ce soir on mange..." — suggestion rapide pour le dîner.

Variante du widget QCOM focalisée sur le repas du soir avec:
- Affichage recette planifiée avec temps de préparation
- Vérification des ingrédients manquants vs inventaire
- Bouton suggestion IA en fallback
"""

import logging
from datetime import date, datetime

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("ce_soir_on_mange")


# ═══════════════════════════════════════════════════════════
# LOGIQUE MÉTIER
# ═══════════════════════════════════════════════════════════


def _obtenir_diner_planifie() -> dict | None:
    """Récupère le dîner planifié pour ce soir."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import PlanningRepas

        aujourdhui = date.today()

        with obtenir_contexte_db() as session:
            planning = (
                session.query(PlanningRepas)
                .filter(
                    PlanningRepas.date_repas == aujourdhui,
                    PlanningRepas.type_repas == "diner",
                )
                .first()
            )

            if planning and planning.recette:
                recette = planning.recette
                return {
                    "recette_id": recette.id,
                    "nom": recette.nom,
                    "temps_preparation": getattr(recette, "temps_preparation", None),
                    "temps_cuisson": getattr(recette, "temps_cuisson", None),
                    "temps_total": getattr(recette, "temps_total", None),
                    "nb_personnes": getattr(recette, "nb_personnes", None),
                    "difficulte": getattr(recette, "difficulte", None),
                    "ingredients": [
                        {
                            "nom": ing.ingredient.nom
                            if hasattr(ing, "ingredient") and ing.ingredient
                            else getattr(ing, "nom", ""),
                            "quantite": getattr(ing, "quantite", 0),
                            "unite": getattr(ing, "unite", ""),
                        }
                        for ing in (recette.ingredients or [])
                    ],
                    "source": "planning",
                }
    except Exception as e:
        logger.debug(f"Dîner planifié non trouvé: {e}")

    return None


def _verifier_ingredients_disponibles(ingredients: list[dict]) -> dict:
    """Vérifie quels ingrédients sont disponibles dans l'inventaire.

    Returns:
        Dict avec 'disponibles', 'manquants', 'score_faisabilite'.
    """
    try:
        from src.services.inventaire import obtenir_service_inventaire

        inventaire = obtenir_service_inventaire().get_inventaire_complet()
        noms_inventaire = {
            a.get("ingredient_nom", a.get("nom", "")).lower()
            for a in inventaire
            if a.get("quantite", 0) > 0
        }

        disponibles = []
        manquants = []

        for ing in ingredients:
            nom_lower = ing.get("nom", "").lower()
            if nom_lower and any(nom_lower in inv or inv in nom_lower for inv in noms_inventaire):
                disponibles.append(ing["nom"])
            else:
                manquants.append(ing["nom"])

        total = len(ingredients) or 1
        score = (len(disponibles) / total) * 100

        return {
            "disponibles": disponibles,
            "manquants": manquants,
            "score_faisabilite": score,
        }
    except Exception as e:
        logger.debug(f"Vérification ingrédients impossible: {e}")
        return {"disponibles": [], "manquants": [], "score_faisabilite": 0}


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_widget_ce_soir():
    """Widget 'Ce soir on mange...' pour le dashboard."""
    diner = _obtenir_diner_planifie()

    # Container stylisé
    container_cls = StyleSheet.create_class(
        {
            "background": "linear-gradient(135deg, #FFF8E7, #FFEDD5)",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "border-left": f"4px solid {Couleur.ORANGE}",
            "margin-bottom": Espacement.MD,
        }
    )

    StyleSheet.inject()

    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)

    if diner:
        # ── Dîner planifié ──
        st.markdown("### 🍽️ Ce soir on mange...")
        st.markdown(f"## {diner['nom']}")

        # Infos rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            temps = diner.get("temps_total") or diner.get("temps_preparation")
            if temps:
                st.metric("⏱️ Temps", f"{temps} min")
        with col2:
            if diner.get("nb_personnes"):
                st.metric("👥 Personnes", diner["nb_personnes"])
        with col3:
            if diner.get("difficulte"):
                st.metric("📊 Difficulté", diner["difficulte"])

        # Vérification ingrédients
        if diner.get("ingredients"):
            check = _verifier_ingredients_disponibles(diner["ingredients"])

            if check["score_faisabilite"] >= 80:
                st.success(f"✅ {check['score_faisabilite']:.0f}% des ingrédients disponibles !")
            elif check["score_faisabilite"] >= 50:
                st.warning(
                    f"⚠️ Il manque {len(check['manquants'])} ingrédient(s) : "
                    f"{', '.join(check['manquants'][:3])}"
                )
            else:
                st.error(
                    f"❌ Plusieurs ingrédients manquants : {', '.join(check['manquants'][:4])}"
                )

        # Actions
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📖 Voir la recette", key=_keys("voir_recette"), width="stretch"):
                from src.core.state import naviguer

                naviguer("cuisine.recettes")
        with col_b:
            if st.button("🔄 Changer", key=_keys("changer_diner"), width="stretch"):
                st.session_state[_keys("demander_suggestion")] = True
                from src.core.state import rerun

                rerun()

        # Suggestion IA si demandée
        if st.session_state.get(_keys("demander_suggestion")):
            _afficher_suggestion_ia()

    else:
        # ── Pas de dîner planifié ──
        st.markdown("### 🍽️ Ce soir on mange...")
        st.markdown(
            f'<p style="color: {Sem.ON_SURFACE_SECONDARY}; font-style: italic;">'
            "Aucun dîner planifié pour ce soir</p>",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            try:
                from src.core.state import obtenir_etat

                _ia_dispo = obtenir_etat().agent_ia
            except Exception:
                _ia_dispo = False
            if _ia_dispo:
                if st.button(
                    "✨ Suggestion IA",
                    key=_keys("suggestion_ia"),
                    type="primary",
                    width="stretch",
                ):
                    _afficher_suggestion_ia()
            else:
                st.caption("💡 IA non configurée")
        with col_b:
            if st.button("📅 Planifier", key=_keys("planifier"), width="stretch"):
                from src.core.state import naviguer

                naviguer("cuisine_repas")

    st.markdown("</div>", unsafe_allow_html=True)


def _afficher_suggestion_ia():
    """Affiche une suggestion de dîner via IA."""
    with st.spinner("✨ L'IA cherche une idée..."):
        try:
            from src.core.ai import ClientIA

            client = ClientIA()

            # Contexte inventaire
            ingredients_dispo = ""
            try:
                from src.services.inventaire import obtenir_service_inventaire

                inventaire = obtenir_service_inventaire().get_inventaire_complet()
                noms = [a.get("ingredient_nom", a.get("nom", "")) for a in inventaire[:10]]
                if noms:
                    ingredients_dispo = f"\nIngrédients disponibles: {', '.join(noms)}"
            except Exception:
                pass

            prompt = (
                f"Suggère UN dîner rapide et équilibré pour une famille avec un bébé de 20 mois."
                f"{ingredients_dispo}"
                "\n\nFormat: Nom du plat (temps total en minutes)."
                "\nUne seule ligne, pas d'explication."
            )

            reponse = client.generer_texte(prompt, max_tokens=80)
            if reponse:
                st.success(f"💡 **Suggestion :** {reponse.strip()}")
            else:
                st.info("💡 Pas de suggestion disponible")
        except Exception as e:
            logger.debug(f"Suggestion IA indisponible: {e}")
            st.caption("💡 IA indisponible — vérifiez la configuration MISTRAL_API_KEY.")


__all__ = ["afficher_widget_ce_soir"]

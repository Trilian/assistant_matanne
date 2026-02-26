"""
Widget "Qu'est-ce qu'on mange ?" - Suggestion rapide de repas.

Bouton unique en accueil qui utilise le planning du jour
ou génère une suggestion IA instantanée.

Usage:
    from src.ui.components import widget_quest_ce_quon_mange

    widget_quest_ce_quon_mange()
"""

import logging
from datetime import date, datetime

import streamlit as st

from src.core.state import naviguer, rerun
from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("quest_ce_quon_mange")


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


def obtenir_repas_du_jour() -> dict | None:
    """
    Récupère le repas planifié pour aujourd'hui.

    Returns:
        Dict avec les infos du repas ou None
    """
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import PlanningRepas, Recette

        aujourdhui = date.today()

        with obtenir_contexte_db() as session:
            # Chercher le prochain repas (midi ou soir)
            heure_actuelle = datetime.now().hour

            # Si avant 14h, chercher le déjeuner, sinon le dîner
            type_repas = "dejeuner" if heure_actuelle < 14 else "diner"

            planning = (
                session.query(PlanningRepas)
                .filter(
                    PlanningRepas.date_repas == aujourdhui,
                    PlanningRepas.type_repas == type_repas,
                )
                .first()
            )

            if not planning:
                # Fallback: n'importe quel repas du jour
                planning = (
                    session.query(PlanningRepas)
                    .filter(PlanningRepas.date_repas == aujourdhui)
                    .first()
                )

            if planning and planning.recette:
                return {
                    "recette_id": planning.recette_id,
                    "recette_nom": planning.recette.nom,
                    "type_repas": planning.type_repas,
                    "temps_total": planning.recette.temps_total,
                    "nb_personnes": planning.recette.nb_personnes,
                    "ingredients": planning.recette.ingredients,
                    "source": "planning",
                }

    except Exception as e:
        logger.debug(f"Pas de planning trouvé: {e}")

    return None


def obtenir_suggestions_faisabilite() -> list[dict]:
    """
    Récupère les recettes faisables avec le stock actuel.

    Utilise le service de faisabilité (A1) pour scorer les recettes
    en fonction de l'inventaire courant.

    Returns:
        Liste de dicts {recette_id, nom, score, tier, manquants}
    """
    try:
        from src.services.cuisine.suggestions.faisabilite import (
            obtenir_recettes_faisables,
        )

        faisables = obtenir_recettes_faisables(limite=5)
        return [
            {
                "recette_id": f.recette_id,
                "recette_nom": f.nom_recette,
                "score": f.score,
                "tier": f.tier,
                "manquants": f.ingredients_manquants,
                "source": "faisabilite",
            }
            for f in faisables
        ]
    except Exception as e:
        logger.debug(f"Faisabilité non disponible: {e}")
        return []


def obtenir_produits_urgents_widget() -> list[dict]:
    """Récupère les produits à consommer en urgence (anti-gaspi)."""
    try:
        from src.services.cuisine.suggestions.anti_gaspillage import (
            obtenir_produits_urgents,
        )

        urgents = obtenir_produits_urgents(seuil_jours=5)
        return [
            {
                "nom": u.nom,
                "jours_restants": u.jours_restants,
                "urgence": u.urgence,
            }
            for u in urgents
        ]
    except Exception as e:
        logger.debug(f"Anti-gaspi non disponible: {e}")
        return []


def suggerer_repas_ia() -> dict | None:
    """
    Génère une suggestion de repas via IA.

    Returns:
        Dict avec suggestion IA ou None
    """
    try:
        from src.services.cuisine import get_recette_service

        service = get_recette_service()

        # Obtenir contexte (inventaire, préférences)
        contexte = _construire_contexte_suggestion()

        # Appel IA pour suggestion
        prompt = f"""Suggère UN repas rapide et équilibré pour ce soir.

Contexte: {contexte}

Réponds avec juste le nom du plat et une estimation du temps de préparation.
Format: NOM_PLAT (XX min)"""

        try:
            from src.core.ai import ClientIA

            client = ClientIA()
            reponse = client.generer_texte(prompt, max_tokens=100)

            if reponse:
                return {
                    "suggestion": reponse.strip(),
                    "source": "ia",
                }
        except Exception as e:
            logger.debug(f"IA non disponible: {e}")

    except Exception as e:
        logger.debug(f"Service recettes non disponible: {e}")

    return None


def _construire_contexte_suggestion() -> str:
    """Construit le contexte pour la suggestion IA."""
    contexte_parts = []

    # Heure du jour
    heure = datetime.now().hour
    if heure < 12:
        contexte_parts.append("repas de midi")
    elif heure < 18:
        contexte_parts.append("goûter/snack")
    else:
        contexte_parts.append("dîner")

    # Jour de la semaine
    jour = datetime.now().strftime("%A")
    contexte_parts.append(f"jour: {jour}")

    # Inventaire disponible (si possible)
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ProduitInventaire

        with obtenir_contexte_db() as session:
            produits = (
                session.query(ProduitInventaire.nom)
                .filter(ProduitInventaire.quantite > 0)
                .limit(10)
                .all()
            )
            if produits:
                noms = [p[0] for p in produits]
                contexte_parts.append(f"produits dispo: {', '.join(noms)}")
    except Exception:
        pass

    return " | ".join(contexte_parts)


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI
# ═══════════════════════════════════════════════════════════


@composant_ui("repas", tags=("ui", "widget", "accueil"))
def widget_quest_ce_quon_mange(compact: bool = False) -> None:
    """
    Widget "Qu'est-ce qu'on mange ?" pour l'accueil.

    Args:
        compact: Si True, affichage minimal
    """
    # CSS du widget
    st.markdown(
        """
        <style>
        .qcom-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 20px;
            color: white;
            text-align: center;
            margin: 10px 0;
        }
        .qcom-titre {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .qcom-reponse {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 12px 0;
        }
        .qcom-details {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Vérifier si on a un repas planifié
    repas = obtenir_repas_du_jour()

    if repas:
        # Afficher le repas planifié
        st.markdown(
            f"""
            <div class="qcom-container">
                <div class="qcom-titre">🍽️ Qu'est-ce qu'on mange ?</div>
                <div class="qcom-reponse">{repas['recette_nom']}</div>
                <div class="qcom-details">
                    {repas.get('type_repas', 'Repas')} •
                    {repas.get('temps_total', '?')} min •
                    {repas.get('nb_personnes', '?')} pers.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Boutons d'action
        if not compact:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 Voir la recette", key=_keys("voir_recette")):
                    st.session_state["recette_selectionnee"] = repas["recette_id"]
                    naviguer("cuisine.recettes")
            with col2:
                if st.button("🔄 Autre idée", key=_keys("autre_idee")):
                    # Forcer suggestion IA
                    st.session_state[_keys("force_ia")] = True
                    rerun()
            with col3:
                if st.button("🛒 Ingrédients", key=_keys("ingredients")):
                    st.session_state["ingredients_a_verifier"] = repas.get("ingredients", "")
                    naviguer("cuisine.courses")
    else:
        # Pas de planning - Proposer suggestion IA ou bouton
        st.markdown(
            """
            <div class="qcom-container">
                <div class="qcom-titre">🍽️ Qu'est-ce qu'on mange ?</div>
                <div class="qcom-reponse">Pas encore décidé...</div>
                <div class="qcom-details">Aucun repas planifié pour aujourd'hui</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not compact:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💡 Suggère-moi !", key=_keys("suggerer"), type="primary"):
                    with st.spinner("Réflexion en cours..."):
                        suggestion = suggerer_repas_ia()
                        if suggestion:
                            st.success(f"💡 **Suggestion:** {suggestion['suggestion']}")
                        else:
                            st.info("Pas d'idée pour l'instant. Consulte tes recettes favorites!")
            with col2:
                if st.button("📅 Planifier", key=_keys("planifier")):
                    naviguer("cuisine.planificateur_repas")

    # ── Section Faisabilité (recettes faisables avec le stock) ──
    if not compact:
        _afficher_section_faisabilite()
        _afficher_section_anti_gaspi()


def _afficher_section_faisabilite() -> None:
    """Affiche les recettes faisables avec le stock actuel."""
    faisables = obtenir_suggestions_faisabilite()
    if not faisables:
        return

    with st.expander("🎯 Faisable avec votre stock", expanded=False):
        for item in faisables[:5]:
            tier_emoji = {
                "complet": "🟢",
                "quasi_complet": "🟡",
                "partiel": "🟠",
            }.get(item["tier"], "⚪")

            col_nom, col_score, col_btn = st.columns([4, 2, 2])
            with col_nom:
                st.markdown(f"{tier_emoji} **{item['recette_nom']}**")
            with col_score:
                score_pct = int(item["score"] * 100)
                st.progress(item["score"], text=f"{score_pct}%")
            with col_btn:
                if st.button(
                    "🍳 Je cuisine ça !",
                    key=_keys(f"fais_{item['recette_id']}"),
                ):
                    st.session_state["recette_selectionnee"] = item["recette_id"]
                    naviguer("cuisine.recettes")

            if item.get("manquants"):
                st.caption(f"Manque: {', '.join(item['manquants'][:3])}")


def _afficher_section_anti_gaspi() -> None:
    """Affiche les produits à consommer en urgence."""
    urgents = obtenir_produits_urgents_widget()
    if not urgents:
        return

    with st.expander(f"⚠️ Anti-gaspi — {len(urgents)} produit(s) urgent(s)", expanded=False):
        for prod in urgents[:5]:
            urgence_emoji = "🔴" if prod["urgence"] >= 4 else "🟠" if prod["urgence"] >= 3 else "🟡"
            jours = prod["jours_restants"]
            texte_jours = "Aujourd'hui !" if jours <= 0 else f"{jours}j restants"
            st.markdown(f"{urgence_emoji} **{prod['nom']}** — {texte_jours}")


@composant_ui("repas", tags=("ui", "widget", "compact"))
def widget_qcom_compact() -> None:
    """Version compacte du widget pour la sidebar ou les petits espaces."""
    repas = obtenir_repas_du_jour()

    if repas:
        st.markdown(
            f"**🍽️ Ce soir:** {repas['recette_nom']}",
        )
    else:
        if st.button("🍽️ Qu'est-ce qu'on mange ?", key=_keys("compact_btn")):
            naviguer("cuisine.planificateur_repas")


__all__ = [
    "widget_quest_ce_quon_mange",
    "widget_qcom_compact",
    "obtenir_repas_du_jour",
    "suggerer_repas_ia",
    "obtenir_suggestions_faisabilite",
    "obtenir_produits_urgents_widget",
]

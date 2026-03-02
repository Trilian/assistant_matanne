"""
Widget économies réalisées ce mois.

Calcule et affiche les économies basées sur:
- Batch cooking (coût vs repas individuels)
- Recettes maison vs restaurant estimé
- Réduction gaspillage (anti-gaspi)
- Comparaison mois précédent
"""

import logging
from datetime import date, timedelta

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("economies")

# Estimations moyennes pour le calcul
COUT_MOYEN_REPAS_RESTAURANT = 15.0  # € par personne
COUT_MOYEN_REPAS_MAISON = 4.5  # € par personne
NB_PERSONNES_FAMILLE = 2  # Adultes (Jules ne compte pas en coût repas)
ECONOMIE_BATCH_COOKING_PCT = 0.25  # ~25% d'économie sur les ingrédients


# ═══════════════════════════════════════════════════════════
# CALCUL DES ÉCONOMIES
# ═══════════════════════════════════════════════════════════


def _calculer_economies_mois() -> dict:
    """Calcule les économies du mois courant.

    Returns:
        Dict avec détails des économies.
    """
    aujourdhui = date.today()
    debut_mois = aujourdhui.replace(day=1)
    mois_prec = (debut_mois - timedelta(days=1)).replace(day=1)

    economies = {
        "repas_maison": 0.0,
        "batch_cooking": 0.0,
        "anti_gaspi": 0.0,
        "total": 0.0,
        "nb_repas_planifies": 0,
        "nb_sessions_batch": 0,
        "mois_precedent_total": 0.0,
        "delta_pct": 0.0,
    }

    # ── Économies repas maison vs restaurant ──
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import PlanningRepas

        with obtenir_contexte_db() as session:
            # Repas planifiés ce mois
            repas_mois = (
                session.query(PlanningRepas)
                .filter(
                    PlanningRepas.date_repas >= debut_mois,
                    PlanningRepas.date_repas <= aujourdhui,
                )
                .count()
            )
            economies["nb_repas_planifies"] = repas_mois

            # Chaque repas maison économise la différence vs restaurant
            economie_par_repas = (
                COUT_MOYEN_REPAS_RESTAURANT - COUT_MOYEN_REPAS_MAISON
            ) * NB_PERSONNES_FAMILLE
            economies["repas_maison"] = repas_mois * economie_par_repas

            # Mois précédent
            repas_prec = (
                session.query(PlanningRepas)
                .filter(
                    PlanningRepas.date_repas >= mois_prec,
                    PlanningRepas.date_repas < debut_mois,
                )
                .count()
            )
            economies["mois_precedent_total"] = repas_prec * economie_par_repas
    except Exception as e:
        logger.debug(f"Calcul repas impossible: {e}")

    # ── Économies batch cooking ──
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import SessionBatchCooking

        with obtenir_contexte_db() as session:
            sessions = (
                session.query(SessionBatchCooking)
                .filter(
                    SessionBatchCooking.date_session >= debut_mois,
                    SessionBatchCooking.statut.in_(["termine", "en_cours"]),
                )
                .all()
            )
            economies["nb_sessions_batch"] = len(sessions)

            # Estimation: chaque session batch = ~4 repas x 25% économie
            for s in sessions:
                nb_repas_batch = getattr(s, "nb_portions", 4) or 4
                cout_sans_batch = nb_repas_batch * COUT_MOYEN_REPAS_MAISON * NB_PERSONNES_FAMILLE
                economies["batch_cooking"] += cout_sans_batch * ECONOMIE_BATCH_COOKING_PCT
    except Exception as e:
        logger.debug(f"Calcul batch cooking impossible: {e}")

    # ── Anti-gaspillage (produits utilisés avant péremption) ──
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import HistoriqueInventaire

        with obtenir_contexte_db() as session:
            # Produits consommés ce mois (non jetés)
            consommes = (
                session.query(HistoriqueInventaire)
                .filter(
                    HistoriqueInventaire.date_modification >= debut_mois,
                    HistoriqueInventaire.type_modification == "consomme",
                )
                .count()
            )
            # Estimation: chaque produit consommé au lieu de jeté = ~2€ économisés
            economies["anti_gaspi"] = consommes * 2.0
    except Exception as e:
        logger.debug(f"Calcul anti-gaspi impossible: {e}")

    # ── Total et delta ──
    economies["total"] = (
        economies["repas_maison"] + economies["batch_cooking"] + economies["anti_gaspi"]
    )

    # Ajout batch + anti-gaspi au mois précédent (estimation proportionnelle)
    economies["mois_precedent_total"] += economies["batch_cooking"] * 0.8  # Estimation
    economies["mois_precedent_total"] += economies["anti_gaspi"] * 0.8

    if economies["mois_precedent_total"] > 0:
        economies["delta_pct"] = (
            (economies["total"] - economies["mois_precedent_total"])
            / economies["mois_precedent_total"]
        ) * 100

    return economies


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@cached_fragment(ttl=3600)  # Cache 1h
def afficher_widget_economies():
    """Affiche le widget des économies du mois."""
    eco = _calculer_economies_mois()

    container_cls = StyleSheet.create_class(
        {
            "background": "linear-gradient(135deg, #E8F5E9, #C8E6C9)",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "border-left": f"4px solid {Couleur.SUCCESS}",
            "margin-bottom": Espacement.MD,
        }
    )

    StyleSheet.inject()

    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)

    st.markdown("### 💰 Économies du mois")

    # Montant total animé
    total = eco["total"]
    delta = eco["delta_pct"]
    delta_str = f"+{delta:.0f}%" if delta > 0 else f"{delta:.0f}%"

    col_total, col_details = st.columns([1, 2])

    with col_total:
        st.markdown(
            f'<div style="text-align:center;padding:10px;">'
            f'<p style="font-size:2.5rem;font-weight:700;color:{Couleur.SUCCESS};margin:0;">'
            f"{total:.0f}€</p>"
            f'<p style="font-size:0.85rem;color:{Sem.ON_SURFACE_SECONDARY};margin:0;">'
            f"économisés ce mois</p>",
            unsafe_allow_html=True,
        )
        if delta != 0:
            couleur_delta = Couleur.SUCCESS if delta > 0 else Couleur.RED_500
            st.markdown(
                f'<p style="text-align:center;color:{couleur_delta};font-weight:600;">'
                f"{'↑' if delta > 0 else '↓'} {delta_str} vs mois précédent</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("</div>", unsafe_allow_html=True)

    with col_details:
        # Décomposition
        st.markdown("**Détail des économies :**")

        # Repas maison
        if eco["repas_maison"] > 0:
            st.markdown(
                f"🍳 **Repas maison** : {eco['repas_maison']:.0f}€ "
                f"({eco['nb_repas_planifies']} repas planifiés)"
            )

        # Batch cooking
        if eco["batch_cooking"] > 0:
            st.markdown(
                f"🍱 **Batch cooking** : {eco['batch_cooking']:.0f}€ "
                f"({eco['nb_sessions_batch']} session(s))"
            )

        # Anti-gaspillage
        if eco["anti_gaspi"] > 0:
            st.markdown(f"♻️ **Anti-gaspillage** : {eco['anti_gaspi']:.0f}€")

        if total == 0:
            st.caption("📊 Les économies seront calculées à mesure que vous planifiez vos repas")

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["afficher_widget_economies"]

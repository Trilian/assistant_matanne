"""
Widget de résumé hebdomadaire IA pour le dashboard accueil.

Affiche un résumé automatique de la semaine écoulée avec:
- Métriques clés (repas, budget, activités, tâches)
- Score de la semaine
- Résumé narratif IA (streaming ou fallback)
- Recommandations
"""

from __future__ import annotations

import logging
from datetime import date

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur

logger = logging.getLogger(__name__)

_keys = KeyNamespace("resume_hebdo")


@cached_fragment(ttl=3600)  # Cache 1h
def afficher_resume_hebdomadaire():
    """
    Affiche le widget de résumé hebdomadaire.

    Génère le résumé via le service IA si c'est un lundi,
    sinon affiche le dernier résumé en cache.
    """
    with error_boundary("resume_hebdomadaire"):
        try:
            from src.services.famille.resume_hebdo import obtenir_service_resume_hebdo

            service = obtenir_service_resume_hebdo()
        except Exception as e:
            logger.warning(f"Service résumé hebdo indisponible: {e}")
            return

        st.subheader("📊 Résumé de la Semaine")

        # Bouton de génération manuelle
        col_title, col_btn = st.columns([4, 1])

        with col_btn:
            forcer_generation = st.button(
                "🔄 Générer",
                key=_keys("btn_generer"),
                help="Forcer la re-génération du résumé",
            )

        # Générer le résumé
        try:
            with st.spinner("Génération du résumé..."):
                resume = service.generer_resume_semaine_sync()
        except Exception as e:
            logger.error(f"Erreur génération résumé: {e}")
            st.warning("⚠️ Impossible de générer le résumé cette semaine.")
            return

        if not resume:
            st.info("📊 Aucune donnée disponible pour cette semaine.")
            return

        # ── Période ──
        if resume.date_debut and resume.date_fin:
            st.caption(
                f"📅 Semaine du {resume.date_debut.strftime('%d/%m')} "
                f"au {resume.date_fin.strftime('%d/%m/%Y')}"
            )

        # ── Score de la semaine ──
        _afficher_score(resume.score_semaine)

        # ── Métriques clés ──
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "🍽️ Repas",
                f"{resume.repas.nb_repas_realises}/{resume.repas.nb_repas_planifies}",
                delta=f"{resume.repas.taux_realisation:.0f}%",
                help="Repas réalisés / planifiés",
            )

        with col2:
            st.metric(
                "💰 Budget",
                f"{resume.budget.total_depenses:.0f}€",
                delta=resume.budget.tendance,
                delta_color=("inverse" if resume.budget.tendance == "hausse" else "normal"),
            )

        with col3:
            st.metric(
                "🎯 Activités",
                resume.activites.nb_activites,
                help="Activités réalisées",
            )

        with col4:
            retard = resume.taches.nb_taches_en_retard
            st.metric(
                "✅ Tâches",
                resume.taches.nb_taches_realisees,
                delta=f"-{retard} en retard" if retard > 0 else "À jour",
                delta_color="inverse" if retard > 0 else "normal",
            )

        # ── Résumé narratif ──
        if resume.resume_narratif:
            with st.expander("📝 Résumé détaillé", expanded=False):
                st.markdown(resume.resume_narratif)

        # ── Recommandations ──
        if resume.recommandations:
            with st.expander("💡 Recommandations", expanded=False):
                for i, reco in enumerate(resume.recommandations, 1):
                    st.markdown(f"{i}. {reco}")

        # ── Horodatage ──
        if resume.genere_le:
            st.caption(f"⏰ Généré le {resume.genere_le.strftime('%d/%m/%Y à %H:%M')}")


def _afficher_score(score: int):
    """Affiche le score de la semaine avec jauge visuelle."""
    # Couleur basée sur le score
    if score >= 80:
        couleur = Couleur.SUCCESS
        emoji = "🌟"
        label = "Excellente semaine !"
    elif score >= 60:
        couleur = Couleur.ORANGE
        emoji = "👍"
        label = "Bonne semaine"
    elif score >= 40:
        couleur = Couleur.WARNING
        emoji = "📊"
        label = "Semaine correcte"
    else:
        couleur = Couleur.RED_500
        emoji = "💪"
        label = "Semaine à améliorer"

    st.markdown(
        f'<div style="text-align:center; padding:10px; margin:10px 0; '
        f"background: linear-gradient(90deg, {couleur}33 0%, {couleur}11 100%); "
        f'border-radius: 8px; border-left: 4px solid {couleur};">'
        f'<span style="font-size:2rem;">{emoji}</span> '
        f'<strong style="font-size:1.3rem;">{score}/100</strong> '
        f'<span style="color:#888;"> — {label}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


__all__ = ["afficher_resume_hebdomadaire"]

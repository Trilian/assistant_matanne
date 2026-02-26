"""
Widget santé/fitness Garmin pour le dashboard.

Affiche un résumé compact des données Garmin:
- Pas du jour / objectif
- Sommeil la nuit dernière
- Calories brûlées
- Fréquence cardiaque au repos
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

_keys = KeyNamespace("sante_fitness")


# ═══════════════════════════════════════════════════════════
# DONNÉES
# ═══════════════════════════════════════════════════════════


def _obtenir_donnees_fitness() -> dict | None:
    """Récupère le résumé fitness du jour depuis Garmin.

    Returns:
        Dict avec pas, calories, sommeil, fc_repos, ou None.
    """
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ResumeQuotidienGarmin

        aujourdhui = date.today()
        hier = aujourdhui - timedelta(days=1)

        with obtenir_contexte_db() as session:
            # Résumé d'aujourd'hui
            resume = (
                session.query(ResumeQuotidienGarmin)
                .filter(ResumeQuotidienGarmin.date == aujourdhui)
                .first()
            )

            # Fallback sur hier si pas encore de données
            if not resume:
                resume = (
                    session.query(ResumeQuotidienGarmin)
                    .filter(ResumeQuotidienGarmin.date == hier)
                    .first()
                )
                if resume:
                    return {
                        "pas": resume.pas or 0,
                        "calories_actives": resume.calories_actives or 0,
                        "calories_totales": resume.calories_totales or 0,
                        "minutes_actives": (resume.minutes_actives or 0)
                        + (resume.minutes_tres_actives or 0),
                        "fc_repos": resume.fc_repos,
                        "stress_moyen": resume.stress_moyen,
                        "body_battery_max": resume.body_battery_max,
                        "date_donnees": hier,
                        "est_hier": True,
                    }

            if resume:
                return {
                    "pas": resume.pas or 0,
                    "calories_actives": resume.calories_actives or 0,
                    "calories_totales": resume.calories_totales or 0,
                    "minutes_actives": (resume.minutes_actives or 0)
                    + (resume.minutes_tres_actives or 0),
                    "fc_repos": resume.fc_repos,
                    "stress_moyen": resume.stress_moyen,
                    "body_battery_max": resume.body_battery_max,
                    "date_donnees": aujourdhui,
                    "est_hier": False,
                }
    except Exception as e:
        logger.debug(f"Données Garmin indisponibles: {e}")

    return None


def _calculer_streak_pas() -> int:
    """Calcule le nombre de jours consécutifs où l'objectif pas est atteint."""
    try:
        from src.core.constants import OBJECTIF_PAS_QUOTIDIEN_DEFAUT
        from src.core.db import obtenir_contexte_db
        from src.core.models import ResumeQuotidienGarmin

        with obtenir_contexte_db() as session:
            # Chercher les derniers 30 jours
            aujourdhui = date.today()
            streak = 0

            for i in range(30):
                jour = aujourdhui - timedelta(days=i)
                resume = (
                    session.query(ResumeQuotidienGarmin)
                    .filter(ResumeQuotidienGarmin.date == jour)
                    .first()
                )
                if resume and (resume.pas or 0) >= OBJECTIF_PAS_QUOTIDIEN_DEFAUT:
                    streak += 1
                else:
                    break

            return streak
    except Exception:
        return 0


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@cached_fragment(ttl=300)  # Cache 5 min
def afficher_widget_sante():
    """Affiche le widget santé/fitness compact."""
    from src.core.constants import OBJECTIF_CALORIES_BRULEES_DEFAUT, OBJECTIF_PAS_QUOTIDIEN_DEFAUT

    donnees = _obtenir_donnees_fitness()

    container_cls = StyleSheet.create_class(
        {
            "background": "linear-gradient(135deg, #E3F2FD, #BBDEFB)",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "border-left": f"4px solid {Couleur.INFO}",
            "margin-bottom": Espacement.MD,
        }
    )

    StyleSheet.inject()

    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)

    titre = "### 🏃 Santé & Fitness"
    if donnees and donnees.get("est_hier"):
        titre += " *(hier)*"
    st.markdown(titre)

    if donnees:
        # ── Métriques principales ──
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            pas = donnees["pas"]
            objectif_pas = OBJECTIF_PAS_QUOTIDIEN_DEFAUT
            pct_pas = min(100, (pas / objectif_pas) * 100) if objectif_pas else 0
            st.metric(
                "👟 Pas",
                f"{pas:,}".replace(",", " "),
                delta=f"{pct_pas:.0f}% objectif",
                delta_color="normal" if pct_pas >= 100 else "off",
            )

        with col2:
            cal = donnees["calories_actives"]
            st.metric(
                "🔥 Calories",
                f"{cal}",
                delta=f"/ {OBJECTIF_CALORIES_BRULEES_DEFAUT}",
            )

        with col3:
            minutes = donnees["minutes_actives"]
            st.metric("⏱️ Actif", f"{minutes} min")

        with col4:
            if donnees.get("fc_repos"):
                st.metric("❤️ FC repos", f"{donnees['fc_repos']} bpm")
            elif donnees.get("body_battery_max"):
                st.metric("🔋 Battery", f"{donnees['body_battery_max']}%")

        # Barre de progression pas
        pct_display = min(1.0, pas / objectif_pas) if objectif_pas else 0
        st.progress(
            pct_display, text=f"Objectif pas : {pas:,} / {objectif_pas:,}".replace(",", " ")
        )

        # Streak
        streak = _calculer_streak_pas()
        if streak > 0:
            st.caption(
                f"🔥 Streak : **{streak}** jour{'s' if streak > 1 else ''} d'objectif atteint !"
            )

    else:
        st.markdown(
            f'<p style="color: {Sem.ON_SURFACE_SECONDARY}; font-style: italic;">'
            "Connectez votre Garmin pour voir vos stats fitness"
            "</p>",
            unsafe_allow_html=True,
        )
        if st.button("⚙️ Configurer Garmin", key=_keys("config_garmin")):
            from src.core.state import naviguer

            naviguer("parametres")

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["afficher_widget_sante"]

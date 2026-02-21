"""
Hub Famille - Dashboard principal avec cards cliquables.

Structure:
┌─────────────┐ ┌─────────────┐
│ 👶 Jules    │ │ 🎉 Weekend  │
│ 19m         │ │ Idees IA    │
└─────────────┘ └─────────────┘
┌─────────────┐ ┌─────────────┐
│ 💪 Anne     │ │ 💪 Mathieu  │
│ 🔥 5j │ ⌚   │ │ 🔥 3j │ ⌚   │
└─────────────┘ └─────────────┘
┌─────────────────────────────┐
│ 🛍️ Achats Famille          │
└─────────────────────────────┘
"""

import logging
from datetime import date, timedelta

import streamlit as st

logger = logging.getLogger(__name__)

from src.core.constants import OBJECTIF_PAS_QUOTIDIEN_DEFAUT
from src.core.db import obtenir_contexte_db
from src.core.models import (
    ChildProfile,
    FamilyPurchase,
    GarminDailySummary,
    UserProfile,
    WeekendActivity,
)
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.services.integrations.garmin import init_family_users

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def calculer_age_jules() -> dict:
    """Calcule l'âge de Jules (délègue à age_utils)."""
    from src.modules.famille.age_utils import get_age_jules

    return get_age_jules()


def get_user_streak(username: str) -> int:
    """Recupère le streak d'un utilisateur"""
    try:
        with obtenir_contexte_db() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            if not user:
                return 0

            # Calculer le streak base sur les resumes quotidiens
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            summaries = (
                db.query(GarminDailySummary)
                .filter(
                    GarminDailySummary.user_id == user.id, GarminDailySummary.date >= start_date
                )
                .order_by(GarminDailySummary.date.desc())
                .all()
            )

            if not summaries:
                return 0

            streak = 0
            current_date = end_date
            summary_by_date = {s.date: s for s in summaries}
            objectif = user.objectif_pas_quotidien or OBJECTIF_PAS_QUOTIDIEN_DEFAUT

            while current_date >= start_date:
                summary = summary_by_date.get(current_date)
                if summary and summary.pas >= objectif:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break

            return streak
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return 0


def get_user_garmin_connected(username: str) -> bool:
    """Verifie si Garmin est connecte"""
    try:
        with obtenir_contexte_db() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            return user.garmin_connected if user else False
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return False


def count_weekend_activities() -> int:
    """Compte les activites weekend planifiees"""
    try:
        with obtenir_contexte_db() as db:
            today = date.today()
            # Prochain weekend
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0 and today.weekday() != 5:
                days_until_saturday = 7
            saturday = today + timedelta(days=days_until_saturday)
            sunday = saturday + timedelta(days=1)

            count = (
                db.query(WeekendActivity)
                .filter(
                    WeekendActivity.date_prevue.in_([saturday, sunday]),
                    WeekendActivity.statut == "planifie",
                )
                .count()
            )
            return count
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return 0


def count_pending_purchases() -> int:
    """Compte les achats en attente"""
    try:
        with obtenir_contexte_db() as db:
            return db.query(FamilyPurchase).filter_by(achete=False).count()
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return 0


def count_urgent_purchases() -> int:
    """Compte les achats urgents"""
    try:
        with obtenir_contexte_db() as db:
            return (
                db.query(FamilyPurchase)
                .filter(
                    FamilyPurchase.achete == False, FamilyPurchase.priorite.in_(["urgent", "haute"])
                )
                .count()
            )
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return 0


# ═══════════════════════════════════════════════════════════
# COMPOSANTS CARDS
# ═══════════════════════════════════════════════════════════


def afficher_card_jules():
    """Affiche la card Jules"""
    age = calculer_age_jules()

    if st.button("👶 **Jules**", key="card_jules", use_container_width=True, type="primary"):
        st.session_state[SK.FAMILLE_PAGE] = "jules"
        st.rerun()

    st.caption(f"🎂 {age['texte']} • 🎨 Activites adaptees")


def afficher_card_weekend():
    """Affiche la card Weekend"""
    count = count_weekend_activities()

    if st.button(
        "🎉 **Ce Weekend**", key="card_weekend", use_container_width=True, type="secondary"
    ):
        st.session_state[SK.FAMILLE_PAGE] = "weekend"
        st.rerun()

    if count > 0:
        st.caption(f"📅 {count} activite(s) planifiee(s)")
    else:
        st.caption("💡 Decouvrir des idees IA")


def afficher_card_user(username: str, display_name: str, emoji: str):
    """Affiche la card utilisateur (Anne ou Mathieu)"""
    streak = get_user_streak(username)
    garmin = get_user_garmin_connected(username)

    btn_type = "primary" if username == "anne" else "secondary"

    if st.button(
        f"{emoji} **{display_name}**",
        key=f"card_{username}",
        use_container_width=True,
        type=btn_type,
    ):
        st.session_state[SK.FAMILLE_PAGE] = "suivi"
        st.session_state[SK.SUIVI_USER] = username
        st.rerun()

    status_parts = []
    if streak > 0:
        status_parts.append(f"🔥 {streak}j")
    if garmin:
        status_parts.append("⌚ Garmin")
    else:
        status_parts.append("⌚ Non connecte")

    st.caption(" • ".join(status_parts))


def afficher_card_achats():
    """Affiche la card Achats"""
    pending = count_pending_purchases()
    urgent = count_urgent_purchases()

    if st.button(
        "🛍️ **Achats Famille**", key="card_achats", use_container_width=True, type="secondary"
    ):
        st.session_state[SK.FAMILLE_PAGE] = "achats"
        st.rerun()

    if urgent > 0:
        st.caption(f"⚠️ {urgent} urgent(s) • 📋 {pending} en attente")
    elif pending > 0:
        st.caption(f"📋 {pending} article(s) en attente")
    else:
        st.caption("✅ Rien en attente")


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("famille")
def app():
    """Point d'entree du Hub Famille"""
    st.title("👨‍👩‍👧 Hub Famille")

    # Initialiser les utilisateurs si necessaire
    try:
        init_family_users()
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")

    # Gerer la navigation
    page = st.session_state.get(SK.FAMILLE_PAGE, "hub")

    if page == "hub":
        afficher_hub()
    elif page == "jules":
        from src.modules.famille.jules import app as jules_app

        if st.button("⬅️ Retour au Hub"):
            st.session_state[SK.FAMILLE_PAGE] = "hub"
            st.rerun()
        jules_app()
    elif page == "weekend":
        from src.modules.famille.weekend import app as weekend_app

        if st.button("⬅️ Retour au Hub"):
            st.session_state[SK.FAMILLE_PAGE] = "hub"
            st.rerun()
        weekend_app()
    elif page == "suivi":
        from src.modules.famille.suivi_perso import app as suivi_app

        if st.button("⬅️ Retour au Hub"):
            st.session_state[SK.FAMILLE_PAGE] = "hub"
            st.rerun()
        suivi_app()
    elif page == "achats":
        from src.modules.famille.achats_famille import app as achats_app

        if st.button("⬅️ Retour au Hub"):
            st.session_state[SK.FAMILLE_PAGE] = "hub"
            st.rerun()
        achats_app()
    else:
        afficher_hub()


def afficher_hub():
    """Affiche le hub principal avec les cards"""

    st.markdown("---")

    # Première ligne: Jules + Weekend
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            afficher_card_jules()

    with col2:
        with st.container(border=True):
            afficher_card_weekend()

    # Deuxième ligne: Anne + Mathieu
    col3, col4 = st.columns(2)

    with col3:
        with st.container(border=True):
            afficher_card_user("anne", "Anne", "👩")

    with col4:
        with st.container(border=True):
            afficher_card_user("mathieu", "Mathieu", "👨")

    # Troisième ligne: Achats (pleine largeur)
    with st.container(border=True):
        afficher_card_achats()

    # Section rapide: Ce weekend
    st.markdown("---")
    st.subheader("🎯 Ce Weekend")

    afficher_weekend_preview()


def afficher_weekend_preview():
    """Aperçu rapide du weekend"""
    today = date.today()

    # Calculer le prochain weekend
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0 and today.weekday() not in [5, 6]:
        days_until_saturday = 7

    if today.weekday() == 5:  # Samedi
        saturday = today
    elif today.weekday() == 6:  # Dimanche
        saturday = today - timedelta(days=1)
    else:
        saturday = today + timedelta(days=days_until_saturday)

    sunday = saturday + timedelta(days=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**📅 Samedi {saturday.strftime('%d/%m')}**")
        _afficher_day_activities(saturday)

    with col2:
        st.markdown(f"**📅 Dimanche {sunday.strftime('%d/%m')}**")
        _afficher_day_activities(sunday)


def _afficher_day_activities(day: date):
    """Affiche les activites d'un jour"""
    try:
        with obtenir_contexte_db() as db:
            activities = (
                db.query(WeekendActivity)
                .filter(WeekendActivity.date_prevue == day, WeekendActivity.statut == "planifie")
                .all()
            )

            if activities:
                for act in activities:
                    heure = act.heure_debut or "?"
                    st.write(f"• {heure} - {act.titre}")
            else:
                st.caption("Rien de prevu")
                if st.button("💡 Suggerer", key=f"suggest_{day}"):
                    st.session_state[SK.FAMILLE_PAGE] = "weekend"
                    st.rerun()
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        st.caption("Rien de prevu")

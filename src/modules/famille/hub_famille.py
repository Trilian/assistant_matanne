"""
Hub Famille - Dashboard principal avec cards cliquables.

REFACTORISÉ: Les requêtes DB sont déléguées aux services dédiés:
- ``src.services.famille.suivi_perso`` pour le streak et Garmin
- ``src.services.famille.weekend`` pour les activités weekend
- ``src.services.famille.achats`` pour les achats en attente
- ``src.modules.famille.age_utils`` pour le calcul d'âge Jules

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

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.modules._framework import error_boundary
from src.modules.famille.age_utils import get_age_jules
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("famille")


def _naviguer_famille(page: str) -> None:
    """Navigation interne standardisée du hub famille."""
    st.session_state[SK.FAMILLE_PAGE] = page
    st.rerun()


# ═══════════════════════════════════════════════════════════
# LAZY SERVICE ACCESSORS
# ═══════════════════════════════════════════════════════════

_service_suivi = None
_service_weekend = None
_service_achats = None


def _get_service_suivi():
    """Accès lazy au ServiceSuiviPerso."""
    global _service_suivi
    if _service_suivi is None:
        from src.services.famille.suivi_perso import obtenir_service_suivi_perso

        _service_suivi = obtenir_service_suivi_perso()
    return _service_suivi


def _get_service_weekend():
    """Accès lazy au ServiceWeekend."""
    global _service_weekend
    if _service_weekend is None:
        from src.services.famille.weekend import obtenir_service_weekend

        _service_weekend = obtenir_service_weekend()
    return _service_weekend


def _get_service_achats():
    """Accès lazy au ServiceAchatsFamille."""
    global _service_achats
    if _service_achats is None:
        from src.services.famille.achats import obtenir_service_achats_famille

        _service_achats = obtenir_service_achats_famille()
    return _service_achats


# ═══════════════════════════════════════════════════════════
# HELPERS — délèguent aux services
# ═══════════════════════════════════════════════════════════


def calculer_age_jules() -> dict:
    """Calcule l'âge de Jules (délègue à age_utils)."""
    return get_age_jules()


def get_user_streak(username: str) -> int:
    """Récupère le streak d'un utilisateur via ServiceSuiviPerso."""
    try:
        data = _get_service_suivi().get_user_data(username)
        return data.get("streak", 0)
    except Exception as e:
        logger.debug("Erreur streak %s: %s", username, e)
        return 0


def get_user_garmin_connected(username: str) -> bool:
    """Vérifie si Garmin est connecté via ServiceSuiviPerso."""
    try:
        data = _get_service_suivi().get_user_data(username)
        return data.get("garmin_connected", False)
    except Exception as e:
        logger.debug("Erreur Garmin %s: %s", username, e)
        return False


def count_weekend_activities() -> int:
    """Compte les activités weekend planifiées via ServiceWeekend."""
    try:
        activities = _get_service_weekend().lister_activites_weekend()
        return len([a for a in activities if a.statut == "planifie"])
    except Exception as e:
        logger.debug("Erreur weekend: %s", e)
        return 0


def count_pending_purchases() -> int:
    """Compte les achats en attente via ServiceAchatsFamille."""
    try:
        stats = _get_service_achats().get_stats()
        return stats.get("en_attente", 0)
    except Exception as e:
        logger.debug("Erreur achats: %s", e)
        return 0


def count_urgent_purchases() -> int:
    """Compte les achats urgents via ServiceAchatsFamille."""
    try:
        stats = _get_service_achats().get_stats()
        return stats.get("urgents", 0)
    except Exception as e:
        logger.debug("Erreur achats urgents: %s", e)
        return 0


# ═══════════════════════════════════════════════════════════
# COMPOSANTS CARDS
# ═══════════════════════════════════════════════════════════


def afficher_card_jules():
    """Affiche la card Jules"""
    age = calculer_age_jules()

    if st.button("👶 **Jules**", key="card_jules", use_container_width=True, type="primary"):
        _naviguer_famille("jules")

    st.caption(f"🎂 {age['texte']} • 🎨 Activites adaptees")


def afficher_card_weekend():
    """Affiche la card Weekend"""
    count = count_weekend_activities()

    if st.button(
        "🎉 **Ce Weekend**", key="card_weekend", use_container_width=True, type="secondary"
    ):
        _naviguer_famille("weekend")

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
        st.session_state[SK.SUIVI_USER] = username
        _naviguer_famille("suivi")

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
        _naviguer_famille("achats")

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
    """Point d'entrée du Hub Famille."""
    st.title("👨‍👩‍👧 Hub Famille")

    # Initialiser les utilisateurs si nécessaire
    try:
        from src.services.integrations.garmin import init_family_users

        init_family_users()
    except Exception as e:
        logger.debug("Init utilisateurs: %s", e)

    # Gerer la navigation
    page = st.session_state.get(SK.FAMILLE_PAGE, "hub")

    if page == "hub":
        with error_boundary(titre="Erreur hub famille"):
            afficher_hub()
    elif page == "jules":
        from src.modules.famille.jules import app as jules_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Jules"):
            jules_app()
    elif page == "weekend":
        from src.modules.famille.weekend import app as weekend_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Weekend"):
            weekend_app()
    elif page == "suivi":
        from src.modules.famille.suivi_perso import app as suivi_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Suivi"):
            suivi_app()
    elif page == "achats":
        from src.modules.famille.achats_famille import app as achats_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Achats"):
            achats_app()
    else:
        with error_boundary(titre="Erreur hub famille"):
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

    # Chat IA contextuel famille
    st.markdown("---")
    with st.expander("💬 Assistant Famille", expanded=False):
        from src.ui.components import afficher_chat_contextuel

        afficher_chat_contextuel("famille")


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
    """Affiche les activités d'un jour via ServiceWeekend."""
    try:
        activities = _get_service_weekend().lister_activites_weekend()
        day_activities = [a for a in activities if a.date_prevue == day and a.statut == "planifie"]

        if day_activities:
            for act in day_activities:
                heure = act.heure_debut or "?"
                st.write(f"• {heure} - {act.titre}")
        else:
            st.caption("Rien de prévu")
            if st.button("💡 Suggérer", key=f"suggest_{day}"):
                _naviguer_famille("weekend")
    except Exception as e:
        logger.debug("Erreur activités jour: %s", e)
        st.caption("Rien de prévu")

"""
Hub Famille - Dashboard principal avec cards cliquables.

REFACTORISÉ: Les requêtes DB sont déléguées aux services dédiés:
- ``src.services.famille.suivi_perso`` pour le streak et Garmin
- ``src.services.famille.weekend`` pour les activités weekend
- ``src.services.famille.achats`` pour les achats en attente
- ``src.services.famille.anniversaires`` pour les prochains anniversaires
- ``src.services.famille.carnet_sante`` pour les alertes vaccins/RDV
- ``src.services.famille.documents`` pour les documents expirant
- ``src.services.famille.voyage`` pour les voyages en cours
- ``src.modules.famille.age_utils`` pour le calcul d'âge Jules

Structure:
┌─────────────┐ ┌─────────────┐
│ 👶 Jules    │ │ 🎉 Weekend  │
└─────────────┘ └─────────────┘
┌─────────────┐ ┌─────────────┐
│ 💪 Anne     │ │ 💪 Mathieu  │
└─────────────┘ └─────────────┘
┌─────────────────────────────┐
│ 🛍️ Achats Famille          │
└─────────────────────────────┘
── Vie de famille ────────────
┌─────────────┐ ┌─────────────┐
│ 🎂 Anniv    │ │ 🏥 Santé    │
└─────────────┘ └─────────────┘
┌─────────────┐ ┌─────────────┐
│ 📄 Documents│ │ ✈️ Voyages  │
└─────────────┘ └─────────────┘
┌────────┐ ┌────────┐ ┌────────┐
│📅 Cal  │ │📸 Album│ │💕 Soirée│
└────────┘ └────────┘ └────────┘
── Outils ────────────────────
🩺 Santé Globale │ 📓 Journal │ 👥 Contacts │ 🖨️ Routines PDF
"""

import logging
from datetime import date, timedelta
from typing import Any

import streamlit as st

from src.core.state import rerun

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
    rerun()


# ═══════════════════════════════════════════════════════════
# LAZY SERVICE ACCESSORS
# ═══════════════════════════════════════════════════════════

_service_suivi = None
_service_weekend = None
_service_achats = None
_service_anniversaires = None
_service_carnet_sante = None
_service_documents = None
_service_voyage = None


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


def _get_service_anniversaires():
    """Accès lazy au ServiceAnniversaires."""
    global _service_anniversaires
    if _service_anniversaires is None:
        from src.services.famille.anniversaires import obtenir_service_anniversaires

        _service_anniversaires = obtenir_service_anniversaires()
    return _service_anniversaires


def _get_service_carnet_sante():
    """Accès lazy au ServiceCarnetSante."""
    global _service_carnet_sante
    if _service_carnet_sante is None:
        from src.services.famille.carnet_sante import obtenir_service_carnet_sante

        _service_carnet_sante = obtenir_service_carnet_sante()
    return _service_carnet_sante


def _get_service_documents():
    """Accès lazy au ServiceDocuments."""
    global _service_documents
    if _service_documents is None:
        from src.services.famille.documents import obtenir_service_documents

        _service_documents = obtenir_service_documents()
    return _service_documents


def _get_service_voyage():
    """Accès lazy au ServiceVoyage."""
    global _service_voyage
    if _service_voyage is None:
        from src.services.famille.voyage import obtenir_service_voyage

        _service_voyage = obtenir_service_voyage()
    return _service_voyage


# ═══════════════════════════════════════════════════════════
# HELPERS — délèguent aux services
# ═══════════════════════════════════════════════════════════


def calculer_age_jules() -> dict[str, Any]:
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


def get_prochains_anniversaires(limite: int = 3) -> list[dict[str, Any]]:
    """Récupère les prochains anniversaires via ServiceAnniversaires."""
    try:
        annivs = _get_service_anniversaires().lister_prochains(limite=limite)
        return [
            {
                "nom": a.nom,
                "date": a.date_anniversaire,
                "jours_restants": (
                    a.date_anniversaire.replace(year=date.today().year) - date.today()
                ).days
                if hasattr(a, "date_anniversaire")
                else 0,
            }
            for a in annivs
        ]
    except Exception as e:
        logger.debug("Erreur anniversaires: %s", e)
        return []


def get_alertes_vaccins() -> dict[str, Any]:
    """Récupère les alertes vaccins/RDV via ServiceCarnetSante."""
    try:
        alertes = _get_service_carnet_sante().get_alertes()
        return alertes
    except Exception as e:
        logger.debug("Erreur alertes vaccins: %s", e)
        return {"vaccins_retard": 0, "rdv_prochain": None}


def get_documents_expirant(jours: int = 30) -> int:
    """Compte les documents expirant bientôt via ServiceDocuments."""
    try:
        docs = _get_service_documents().lister_expirant(jours=jours)
        return len(docs)
    except Exception as e:
        logger.debug("Erreur documents expirant: %s", e)
        return 0


def get_voyage_en_cours() -> dict[str, Any] | None:
    """Récupère le voyage en cours ou prochain via ServiceVoyage."""
    try:
        voyage = _get_service_voyage().get_prochain_voyage()
        if voyage:
            return {
                "destination": voyage.destination,
                "date_depart": voyage.date_depart,
                "preparation": getattr(voyage, "pourcentage_preparation", 0),
            }
        return None
    except Exception as e:
        logger.debug("Erreur voyage: %s", e)
        return None


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

    status_parts: list[str] = []
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


def afficher_card_anniversaires():
    """Affiche la card Anniversaires avec les prochains événements."""
    annivs = get_prochains_anniversaires(3)

    if st.button(
        "🎂 **Anniversaires**", key="card_anniversaires", use_container_width=True, type="secondary"
    ):
        _naviguer_famille("anniversaires")

    if annivs:
        prochain = annivs[0]
        jours = prochain["jours_restants"]
        if jours == 0:
            st.caption(f"🎉 Aujourd'hui: {prochain['nom']} !")
        elif jours <= 7:
            st.caption(f"🔔 {prochain['nom']} dans {jours}j")
        else:
            st.caption(f"📅 {prochain['nom']} dans {jours}j")
    else:
        st.caption("Aucun anniversaire enregistré")


def afficher_card_sante():
    """Affiche la card Santé (vaccins & RDV)."""
    alertes = get_alertes_vaccins()

    if st.button(
        "🏥 **Carnet de Santé**", key="card_sante", use_container_width=True, type="secondary"
    ):
        _naviguer_famille("carnet_sante")

    parts = []
    vaccins_retard = alertes.get("vaccins_retard", 0)
    rdv = alertes.get("rdv_prochain")
    if vaccins_retard > 0:
        parts.append(f"⚠️ {vaccins_retard} vaccin(s) en retard")
    if rdv:
        parts.append(f"📅 RDV: {rdv}")
    if parts:
        st.caption(" • ".join(parts))
    else:
        st.caption("✅ À jour")


def afficher_card_documents():
    """Affiche la card Documents (alertes expiration)."""
    expirant = get_documents_expirant(30)

    if st.button(
        "📄 **Documents**", key="card_documents", use_container_width=True, type="secondary"
    ):
        _naviguer_famille("documents")

    if expirant > 0:
        st.caption(f"⚠️ {expirant} document(s) expirent bientôt")
    else:
        st.caption("✅ Tous à jour")


def afficher_card_voyage():
    """Affiche la card Voyage (prochain voyage)."""
    voyage = get_voyage_en_cours()

    if st.button("✈️ **Voyages**", key="card_voyage", use_container_width=True, type="secondary"):
        _naviguer_famille("voyage")

    if voyage:
        prep = voyage.get("preparation", 0)
        st.caption(f"🗺️ {voyage['destination']} • {prep}% prêt")
    else:
        st.caption("Aucun voyage planifié")


def afficher_card_calendrier():
    """Affiche la card Calendrier Famille."""
    if st.button(
        "📅 **Calendrier**", key="card_calendrier", use_container_width=True, type="secondary"
    ):
        _naviguer_famille("calendrier")

    st.caption("Événements familiaux")


def afficher_card_album():
    """Affiche la card Album Souvenirs."""
    if st.button(
        "📸 **Album Souvenirs**", key="card_album", use_container_width=True, type="secondary"
    ):
        _naviguer_famille("album")

    st.caption("Nos plus beaux moments")


def afficher_card_soiree():
    """Affiche la card Soirée Couple."""
    if st.button(
        "💕 **Soirée Couple**", key="card_soiree", use_container_width=True, type="secondary"
    ):
        _naviguer_famille("soiree")

    st.caption("Idées de sorties IA")


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
    elif page == "carnet_sante":
        from src.modules.famille.carnet_sante import app as carnet_sante_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Carnet de Santé"):
            carnet_sante_app()
    elif page == "calendrier":
        from src.modules.famille.calendrier_famille import app as calendrier_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Calendrier"):
            calendrier_app()
    elif page == "anniversaires":
        from src.modules.famille.anniversaires import app as anniversaires_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Anniversaires"):
            anniversaires_app()
    elif page == "contacts":
        from src.modules.famille.contacts_famille import app as contacts_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Contacts"):
            contacts_app()
    elif page == "soiree":
        from src.modules.famille.soiree_couple import app as soiree_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Soirée Couple"):
            soiree_app()
    elif page == "album":
        from src.modules.famille.album import app as album_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Album"):
            album_app()
    elif page == "sante_globale":
        from src.modules.famille.sante_globale import app as sante_globale_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Santé Globale"):
            sante_globale_app()
    elif page == "journal":
        from src.modules.famille.journal_familial import app as journal_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Journal Familial"):
            journal_app()
    elif page == "documents":
        from src.modules.famille.documents_famille import app as documents_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Documents"):
            documents_app()
    elif page == "voyage":
        from src.modules.famille.voyage import app as voyage_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Voyage"):
            voyage_app()
    elif page == "routines_pdf":
        from src.modules.famille.routines_imprimables import app as routines_pdf_app

        if st.button("⬅️ Retour au Hub"):
            _naviguer_famille("hub")
        with error_boundary(titre="Erreur module Routines PDF"):
            routines_pdf_app()
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

    # ── Nouvelles cards ──────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Vie de famille")

    # Anniversaires + Santé
    col5, col6 = st.columns(2)
    with col5:
        with st.container(border=True):
            afficher_card_anniversaires()
    with col6:
        with st.container(border=True):
            afficher_card_sante()

    # Documents + Voyage
    col7, col8 = st.columns(2)
    with col7:
        with st.container(border=True):
            afficher_card_documents()
    with col8:
        with st.container(border=True):
            afficher_card_voyage()

    # Calendrier + Album + Soirée
    col9, col10, col11 = st.columns(3)
    with col9:
        with st.container(border=True):
            afficher_card_calendrier()
    with col10:
        with st.container(border=True):
            afficher_card_album()
    with col11:
        with st.container(border=True):
            afficher_card_soiree()

    # Raccourcis secondaires
    st.markdown("---")
    st.subheader("🔧 Outils")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🩺 Santé Globale", key="btn_sante_glob", use_container_width=True):
            _naviguer_famille("sante_globale")
    with c2:
        if st.button("📓 Journal IA", key="btn_journal", use_container_width=True):
            _naviguer_famille("journal")
    with c3:
        if st.button("👥 Contacts", key="btn_contacts", use_container_width=True):
            _naviguer_famille("contacts")
    with c4:
        if st.button("🖨️ Routines PDF", key="btn_routines_pdf", use_container_width=True):
            _naviguer_famille("routines_pdf")

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

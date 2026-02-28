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
    """Navigation vers une sous-page famille via st.switch_page.

    Utilise le routage natif Streamlit (pages cachées de la sidebar)
    au lieu du dispatch session_state interne.
    """
    from src.core.state import GestionnaireEtat

    # Mapping ancien nom interne → clé pages_config
    _KEYS: dict[str, str] = {
        "hub": "famille.hub",
        "jules": "famille.jules",
        "jules_planning": "famille.jules_planning",
        "weekend": "famille.weekend",
        "suivi": "famille.suivi_perso",
        "achats": "famille.achats_famille",
        "activites": "famille.activites",
        "routines": "famille.routines",
        "carnet_sante": "famille.carnet_sante",
        "calendrier": "famille.calendrier",
        "anniversaires": "famille.anniversaires",
        "contacts": "famille.contacts",
        "soiree": "famille.soiree_couple",
        "album": "famille.album",
        "sante_globale": "famille.sante_globale",
        "journal": "famille.journal",
        "documents": "famille.documents",
        "voyage": "famille.voyage",
        "routines_pdf": "famille.routines_pdf",
    }
    module_key = _KEYS.get(page, f"famille.{page}")
    GestionnaireEtat.naviguer_vers(module_key)
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
    """Point d'entrée du Hub Famille.

    Affiche directement le dashboard avec cartes de navigation.
    Les sous-pages famille sont désormais des pages Streamlit cachées
    (hidden=True dans pages_config) — le dispatch session_state
    n'est plus nécessaire. Le bouton « Retour » est géré
    automatiquement par navigation.py.
    """
    st.title("👨‍👩‍👧 Hub Famille")

    # Initialiser les utilisateurs si nécessaire
    try:
        from src.services.integrations.garmin import init_family_users

        init_family_users()
    except Exception as e:
        logger.debug("Init utilisateurs: %s", e)

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
    afficher_vacances_preview()

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


def afficher_vacances_preview():
    """Aperçu / alerte pour prochaines vacances / fermetures crèche.
    Propose de créer une checklist depuis template et de la télécharger (PDF + CSV).
    """
    try:
        from src.core.config import obtenir_parametres
        from src.core.state.persistent import PersistentState
        from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux
        from src.services.maison.checklists_crud_service import obtenir_service_checklists_crud
        from src.services.rapports.generation import ServiceRapportsPDF
    except Exception as e:
        logger.debug("Imports vacances preview: %s", e)
        return

    svc_js = obtenir_service_jours_speciaux()
    prochains = svc_js.prochains_jours_speciaux(5)
    # Filtrer fériés ou fermetures crèche
    candidats = [j for j in prochains if j.type in ("ferie", "creche")]
    if not candidats:
        return

    prochain = candidats[0]
    today = date.today()
    jours_restants = (prochain.date_jour - today).days

    # Seuil d'alerte configurable (priorité: PersistentState 'param_alerts' puis Parametres)
    try:
        default_seuil = obtenir_parametres().VACANCES_ALERT_DAYS
        pstate = PersistentState.get_instance("param_alerts")
        seuil = pstate.get("vacances_alert_days", default_seuil)
    except Exception:
        try:
            seuil = obtenir_parametres().VACANCES_ALERT_DAYS
        except Exception:
            seuil = 14

    if jours_restants <= int(seuil):
        st.markdown("---")
        st.subheader("🏖️ Vacances & Fermetures à venir")
        st.info(
            f"Prochain: **{prochain.nom}** le {prochain.date_jour.strftime('%d/%m')} (dans {jours_restants}j)"
        )

        with st.expander("Préparer la checklist de vacances", expanded=False):
            chk_svc = obtenir_service_checklists_crud()
            templates = chk_svc.get_templates_disponibles()
            options = [t["type_voyage"] for t in templates] if templates else ["vacances_ete"]
            tpl_index = 0 if "vacances_ete" in options else 0
            template_sel = st.selectbox(
                "Choisir un template", options, index=tpl_index, key="vac_tpl"
            )

            if st.button("Créer checklist vacances", key="create_chk_vac"):
                checklist = chk_svc.create_from_template(
                    nom=f"Checklist {prochain.nom}",
                    type_voyage=template_sel,
                    date_depart=prochain.date_jour,
                )
                st.success(f"Checklist créée (id={checklist.id})")

                # Télécharger CSV
                try:
                    import csv
                    import io

                    items = chk_svc.get_items(checklist.id)
                    sio = io.StringIO()
                    writer = csv.writer(sio)
                    writer.writerow(["libelle", "categorie", "quand", "fait"])
                    for it in items:
                        writer.writerow(
                            [
                                getattr(it, "libelle", ""),
                                getattr(it, "categorie", ""),
                                getattr(it, "quand", ""),
                                getattr(it, "fait", False),
                            ]
                        )

                    st.download_button(
                        "Télécharger CSV",
                        data=sio.getvalue(),
                        file_name=f"checklist_{checklist.id}.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    logger.debug("Erreur export CSV checklist: %s", e)
                    st.warning("Impossible de préparer le CSV.")

                # Télécharger PDF via ServiceRapportsPDF
                try:
                    rapports = ServiceRapportsPDF()
                    pdf_buf, fname = rapports.telecharger_checklist_pdf(checklist.id)
                    st.download_button(
                        "Télécharger PDF",
                        data=pdf_buf.getvalue(),
                        file_name=fname,
                        mime="application/pdf",
                    )
                except Exception as e:
                    logger.debug("Erreur génération PDF checklist: %s", e)
                    st.warning("Impossible de générer le PDF (dépendances manquantes ?).")

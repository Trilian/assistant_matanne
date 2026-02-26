"""
Composants Calendrier - Import de fichiers ICS

Permet l'import de fichiers .ics depuis:
- Doctolib (export gratuit natif)
- Google Calendar (export .ics)
- Apple Calendar / iCloud
- Outlook
- Tout calendrier compatible iCal

Fonctionnalités:
- Upload fichier .ics
- Import depuis URL iCal
- Prévisualisation avant import
- Statistiques d'import
"""

import logging
from datetime import datetime

import streamlit as st

from src.ui.feedback import afficher_erreur, afficher_succes
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("import_ics")


def afficher_import_ics():
    """Interface complète d'import de fichiers ICS.

    Propose deux méthodes:
    1. Upload de fichier .ics
    2. Import depuis URL iCal
    """

    st.subheader("📥 Importer un calendrier")
    st.caption(
        "Importez vos événements depuis Doctolib, Google Calendar, "
        "Outlook ou tout calendrier compatible iCal (.ics)"
    )

    # Onglets pour les deux méthodes
    tab_fichier, tab_url = st.tabs(["📄 Fichier .ics", "🔗 URL iCal"])

    with tab_fichier:
        _afficher_import_fichier()

    with tab_url:
        _afficher_import_url()


def _afficher_import_fichier():
    """Import via upload de fichier .ics."""

    # Sources connues avec aide
    st.markdown("#### Sources supportées")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🩺 Doctolib**\n\n" "Mes RDV → Exporter (.ics)\n\n" "*Gratuit, export natif*")
    with col2:
        st.markdown("**📅 Google Calendar**\n\n" "Paramètres → Exporter\n\n" "*Télécharge un .ics*")
    with col3:
        st.markdown(
            "**📧 Outlook**\n\n" "Calendrier → Partager → Exporter\n\n" "*Format .ics standard*"
        )

    st.divider()

    # Upload
    uploaded = st.file_uploader(
        "Choisir un fichier .ics",
        type=["ics"],
        key=_keys("fichier_ics"),
        help="Fichier iCalendar standard (.ics)",
    )

    if uploaded is not None:
        try:
            ical_content = uploaded.read().decode("utf-8")
        except UnicodeDecodeError:
            # Essayer latin-1 (certains exports Windows)
            uploaded.seek(0)
            ical_content = uploaded.read().decode("latin-1")

        # Parser et prévisualiser
        _previsualiser_et_importer(ical_content, source=uploaded.name)


def _afficher_import_url():
    """Import via URL iCal."""

    st.markdown(
        "Collez une URL iCal pour importer les événements. "
        "Fonctionne avec Google Calendar (URL secrète), Doctolib, etc."
    )

    with st.form("import_url_form"):
        url = st.text_input(
            "URL du calendrier iCal",
            placeholder="https://calendar.google.com/calendar/ical/.../basic.ics",
            key=_keys("ical_url_input"),
        )

        nom_calendrier = st.text_input(
            "Nom du calendrier",
            value="Calendrier importé",
            key=_keys("nom_cal_url"),
        )

        submitted = st.form_submit_button(
            "📥 Importer depuis l'URL",
            type="primary",
            use_container_width=True,
        )

        if submitted and url:
            with st.spinner("Téléchargement et import..."):
                try:
                    from src.services.famille.calendrier import (
                        get_calendar_sync_service,
                    )

                    service = get_calendar_sync_service()
                    result = service.import_from_ical_url(
                        user_id="default",
                        ical_url=url,
                        calendar_name=nom_calendrier,
                    )

                    if result and result.success:
                        afficher_succes(
                            f"✅ {result.events_imported} événement(s) importé(s) "
                            f"depuis {nom_calendrier}"
                        )
                    elif result:
                        afficher_erreur(f"Import échoué: {result.message}")
                    else:
                        afficher_erreur("Import échoué (pas de résultat)")

                except Exception as e:
                    afficher_erreur(f"Erreur: {e}")
                    logger.error(f"Erreur import URL iCal: {e}")


def _previsualiser_et_importer(ical_content: str, source: str = "fichier"):
    """Parse le contenu ICS, affiche une prévisualisation et propose l'import.

    Args:
        ical_content: Contenu brut du fichier .ics
        source: Nom de la source pour le logging
    """
    from src.services.famille.calendrier import ICalGenerator

    events = ICalGenerator.parse_ical(ical_content)

    if not events:
        afficher_erreur("Aucun événement trouvé dans le fichier .ics")
        return

    st.success(f"📋 {len(events)} événement(s) trouvé(s) dans **{source}**")

    # Prévisualisation
    st.markdown("#### Aperçu des événements")

    # Regrouper par mois pour lisibilité
    events_sorted = sorted(events, key=lambda e: e.start_time)

    mois_courant = None
    for evt in events_sorted[:50]:  # Limiter à 50 pour la preview
        mois = evt.start_time.strftime("%B %Y")
        if mois != mois_courant:
            st.markdown(f"**📅 {mois}**")
            mois_courant = mois

        # Formater l'événement
        if evt.all_day:
            date_str = evt.start_time.strftime("%d/%m")
        else:
            date_str = evt.start_time.strftime("%d/%m %H:%M")

        lieu = f" 📍 {evt.location}" if evt.location else ""
        st.markdown(f"- {date_str} — **{evt.title}**{lieu}")

    if len(events) > 50:
        st.caption(f"... et {len(events) - 50} autres événements")

    st.divider()

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total", len(events))
    with col2:
        nb_journee = sum(1 for e in events if e.all_day)
        st.metric("📅 Journée entière", nb_journee)
    with col3:
        nb_avec_lieu = sum(1 for e in events if e.location)
        st.metric("📍 Avec lieu", nb_avec_lieu)

    # Options d'import
    st.markdown("#### Options d'import")

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        nom_calendrier = st.text_input(
            "Nom du calendrier",
            value=source.replace(".ics", ""),
            key=_keys("nom_cal_fichier"),
        )
    with col_opt2:
        ignorer_passes = st.checkbox(
            "Ignorer les événements passés",
            value=True,
            key=_keys("ignorer_passes"),
        )

    # Bouton d'import
    if st.button(
        f"📥 Importer {len(events)} événement(s)",
        type="primary",
        use_container_width=True,
        key=_keys("btn_import_fichier"),
    ):
        with st.spinner("Import en cours..."):
            nb_importes = _executer_import(
                events=events,
                nom_calendrier=nom_calendrier,
                ignorer_passes=ignorer_passes,
                source=f"file:{source}",
            )

            if nb_importes > 0:
                afficher_succes(f"✅ {nb_importes} événement(s) importé(s) avec succès !")
            else:
                afficher_erreur("Aucun événement importé.")


def _executer_import(
    events: list,
    nom_calendrier: str,
    ignorer_passes: bool,
    source: str,
) -> int:
    """Exécute l'import des événements ICS dans la base de données.

    Args:
        events: Événements parsés (CalendarEventExternal).
        nom_calendrier: Nom du calendrier source.
        ignorer_passes: Si True, ignore les événements passés.
        source: Source de l'import (pour traçabilité).

    Returns:
        Nombre d'événements importés.
    """
    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import EvenementPlanning

    maintenant = datetime.now()
    nb_importes = 0

    try:
        with obtenir_contexte_db() as db:
            for event in events:
                # Filtrer les événements passés si demandé
                if ignorer_passes and event.start_time < maintenant:
                    continue

                try:
                    # Déduplication par external_id
                    if event.external_id:
                        existing = (
                            db.query(EvenementPlanning)
                            .filter(EvenementPlanning.external_id == event.external_id)
                            .first()
                        )

                        if existing:
                            # Mettre à jour
                            existing.titre = event.title
                            existing.description = event.description
                            existing.date_debut = event.start_time.date()
                            existing.date_fin = event.end_time.date() if event.end_time else None
                            nb_importes += 1
                            continue

                    # Créer un nouvel événement
                    cal_event = EvenementPlanning(
                        titre=event.title,
                        description=event.description or "",
                        date_debut=event.start_time.date(),
                        date_fin=(event.end_time.date() if event.end_time else None),
                        source_externe=source,
                        external_id=event.external_id or "",
                    )
                    db.add(cal_event)
                    nb_importes += 1

                except Exception as e:
                    logger.warning(f"Erreur import événement '{event.title}': {e}")

            db.commit()

    except Exception as e:
        logger.error(f"Erreur import ICS: {e}")

    return nb_importes


__all__ = [
    "afficher_import_ics",
]

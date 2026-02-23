"""
Module Calendrier Familial Unifié - Composants UI
"""

from datetime import date, datetime, time, timedelta

import streamlit as st

from src.core.session_keys import SK

from .utils import (
    JourCalendrier,
    SemaineCalendrier,
    TypeEvenement,
    generer_texte_semaine_pour_impression,
    get_debut_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
)

# Drag & drop (graceful fallback si pas installé)
try:
    from streamlit_sortables import sort_items

    HAS_SORTABLES = True
except ImportError:
    HAS_SORTABLES = False

# Accesseur lazy pour le service (singleton)
_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.calendrier_planning import (
            obtenir_service_calendrier_planning,
        )

        _service = obtenir_service_calendrier_planning()
    return _service


def afficher_navigation_semaine():
    """Affiche la navigation entre semaines."""
    if "cal_semaine_debut" not in st.session_state:
        st.session_state.cal_semaine_debut = get_debut_semaine(date.today())

    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])

    with col1:
        if st.button("◀ Précédente", use_container_width=True):
            st.session_state.cal_semaine_debut = get_semaine_precedente(
                st.session_state.cal_semaine_debut
            )
            st.rerun()

    with col2:
        semaine_debut = st.session_state.cal_semaine_debut
        semaine_fin = semaine_debut + timedelta(days=6)
        st.markdown(
            f"<h3 style='text-align: center; margin: 0;'>"
            f"📅 {semaine_debut.strftime('%d/%m')} — {semaine_fin.strftime('%d/%m/%Y')}"
            f"</h3>",
            unsafe_allow_html=True,
        )

    with col3:
        if st.button("Suivante ▶", use_container_width=True):
            st.session_state.cal_semaine_debut = get_semaine_suivante(
                st.session_state.cal_semaine_debut
            )
            st.rerun()

    with col4:
        if st.button("📅 Aujourd'hui", use_container_width=True):
            st.session_state.cal_semaine_debut = get_debut_semaine(date.today())
            st.rerun()


def afficher_jour_calendrier(jour: JourCalendrier):
    """Affiche un jour du calendrier dans une carte."""

    with st.container():
        # Header du jour
        col_titre, col_actions = st.columns([4, 1])

        with col_titre:
            marqueur = "⭐ " if jour.est_aujourdhui else ""
            st.markdown(f"**{marqueur}{jour.jour_semaine}** {jour.date_jour.strftime('%d/%m')}")

        with col_actions:
            if st.button("➕", key=f"add_{jour.date_jour}", help="Ajouter"):
                st.session_state.ajouter_event_date = jour.date_jour

        # Grille des repas
        col_midi, col_soir = st.columns(2)

        with col_midi:
            if jour.repas_midi:
                st.markdown(f"🌞 **{jour.repas_midi.titre}**")
                if jour.repas_midi.version_jules:
                    st.caption(f"👶 {jour.repas_midi.version_jules[:40]}...")
            else:
                st.markdown("🌞 *Midi: —*")

        with col_soir:
            if jour.repas_soir:
                st.markdown(f"🌙 **{jour.repas_soir.titre}**")
                if jour.repas_soir.version_jules:
                    st.caption(f"👶 {jour.repas_soir.version_jules[:40]}...")
            else:
                st.markdown("🌙 *Soir: —*")

        # Goûter si présent
        if jour.gouter:
            st.markdown(f"🍰 {jour.gouter.titre}")

        # Batch cooking
        if jour.batch_cooking:
            st.success(f"🍳 **BATCH COOKING** {jour.batch_cooking.heure_str}")

        # Courses
        for courses in jour.courses:
            st.info(f"🛒 {courses.magasin} {courses.heure_str}")

        # Activités
        for act in jour.activites:
            emoji = "👶" if act.pour_jules else "🎨"
            st.markdown(f"{emoji} {act.titre} {act.heure_str}")

        # RDV
        for rdv in jour.rdv:
            emoji = "🏥" if rdv.type == TypeEvenement.RDV_MEDICAL else "📅"
            lieu_str = f" @ {rdv.lieu}" if rdv.lieu else ""
            st.warning(f"{emoji} {rdv.titre} {rdv.heure_str}{lieu_str}")

        # Tâches ménage
        for tache in jour.taches_menage:
            en_retard = "⚠️ " if tache.notes and "RETARD" in tache.notes else ""
            duree_str = f" ({tache.description.split('•')[0].strip()})" if tache.description else ""
            st.markdown(f"{tache.emoji} {en_retard}{tache.titre}{duree_str}")

        # Autres événements
        for evt in jour.autres_evenements:
            st.caption(f"{evt.emoji} {evt.titre}")


def afficher_jour_sortable(jour: JourCalendrier):
    """Affiche les événements d'un jour avec réordonnancement drag & drop.

    Utilise streamlit-sortables pour permettre le réordonnancement
    visuel des activités et événements. Fallback sur l'affichage
    classique si le package n'est pas installé.
    """
    if not HAS_SORTABLES or not (jour.activites or jour.autres_evenements):
        # Fallback classique
        afficher_jour_calendrier(jour)
        return

    # Construire les labels pour les événements triables
    items = []
    for act in jour.activites:
        emoji = "👶" if act.pour_jules else "🎨"
        items.append(f"{emoji} {act.titre} {act.heure_str}")

    for evt in jour.autres_evenements:
        items.append(f"{evt.emoji} {evt.titre}")

    if items:
        st.caption("↕️ Glissez pour réorganiser")
        sorted_items = sort_items(items, key=f"sort_{jour.date_jour}")

        # Afficher dans le nouvel ordre
        for item in sorted_items:
            st.markdown(f"• {item}")


def afficher_vue_semaine_grille(semaine: SemaineCalendrier):
    """Affiche la semaine en grille 7 colonnes."""

    # En-têtes des jours
    cols = st.columns(7)
    for i, col in enumerate(cols):
        jour = semaine.jours[i]
        with col:
            prefix = "🔵 " if jour.est_aujourdhui else ""
            col.markdown(f"**{prefix}{jour.jour_semaine_court}**")

    st.divider()

    # Contenu des jours
    cols = st.columns(7)
    for i, col in enumerate(cols):
        jour = semaine.jours[i]
        with col:
            afficher_cellule_jour(jour)


def afficher_cellule_jour(jour: JourCalendrier):
    """Affiche une cellule de jour dans la grille."""

    # Date
    st.markdown(f"**{jour.date_jour.strftime('%d')}**")

    # Repas
    if jour.repas_midi:
        st.caption(f"🌞 {jour.repas_midi.titre[:15]}...")
    if jour.repas_soir:
        st.caption(f"🌙 {jour.repas_soir.titre[:15]}...")

    # Événements importants
    if jour.batch_cooking:
        st.success("🍳 Batch", icon="🍳")

    for c in jour.courses[:1]:  # Max 1 pour la place
        st.info("🛒", icon="🛒")

    for rdv in jour.rdv[:1]:
        st.warning("🏥", icon="🏥")

    # Indicateur si plus d'événements
    nb_autres = len(jour.activites) + len(jour.autres_evenements)
    if nb_autres > 0:
        st.caption(f"+{nb_autres} autres")


def afficher_vue_semaine_liste(semaine: SemaineCalendrier):
    """Affiche la semaine en liste (plus détaillée)."""

    for jour in semaine.jours:
        expanded = jour.est_aujourdhui

        # Construire le titre avec indicateurs
        indicateurs = []
        if jour.repas_midi or jour.repas_soir:
            indicateurs.append("🍽️")
        if jour.batch_cooking:
            indicateurs.append("🍳")
        if jour.courses:
            indicateurs.append("🛒")
        if jour.rdv:
            indicateurs.append("🏥")
        if jour.activites:
            indicateurs.append("🎨")

        marqueur = "⭐ " if jour.est_aujourdhui else ""
        indicateurs_str = " ".join(indicateurs) if indicateurs else "—"

        with st.expander(
            f"{marqueur}**{jour.jour_semaine}** {jour.date_jour.strftime('%d/%m')} │ {indicateurs_str}",
            expanded=expanded,
        ):
            afficher_jour_calendrier(jour)


def afficher_stats_semaine(semaine: SemaineCalendrier):
    """Affiche les statistiques de la semaine."""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🍽️ Repas planifiés", f"{semaine.nb_repas_planifies}/14")

    with col2:
        st.metric("🍳 Batch cooking", semaine.nb_sessions_batch)

    with col3:
        st.metric("🛒 Courses", semaine.nb_courses)

    with col4:
        st.metric("🎨 Activités", semaine.nb_activites)


def afficher_actions_rapides(semaine: SemaineCalendrier):
    """Affiche les boutons d'actions rapides."""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🍽️ Planifier repas", use_container_width=True, type="primary"):
            # Naviguer vers le planificateur
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.planning_semaine")
            st.rerun()

    with col2:
        if st.button("🍳 Nouveau batch", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.batch_cooking")
            st.rerun()

    with col3:
        if st.button("🛒 Mes courses", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.courses")
            st.rerun()

    with col4:
        if st.button("🖨️ Imprimer", use_container_width=True):
            _dialog_impression(semaine)


@st.dialog("🖨️ Imprimer le planning")
def _dialog_impression(semaine: SemaineCalendrier):
    """Dialog natif pour l'impression du planning."""
    texte = generer_texte_semaine_pour_impression(semaine)

    st.text_area(
        "Aperçu (copier-coller pour imprimer)",
        value=texte,
        height=400,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Télécharger .txt",
            data=texte,
            file_name=f"planning_{semaine.date_debut.strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )
    with col2:
        if st.button("Fermer", use_container_width=True):
            st.rerun()


def afficher_modal_impression(semaine: SemaineCalendrier):
    """Affiche le modal d'impression.

    DÉPRÉCIÉ — Utiliser _dialog_impression() via le bouton Imprimer.
    Conservé pour compatibilité arrière.
    """
    if st.session_state.get(SK.SHOW_PRINT_MODAL):
        _dialog_impression(semaine)


def afficher_formulaire_ajout_event():
    """Affiche le formulaire d'ajout d'événement."""

    if "ajouter_event_date" in st.session_state:
        date_selectionnee = st.session_state.ajouter_event_date

        with st.container():
            st.subheader(f"➕ Ajouter un événement - {date_selectionnee.strftime('%d/%m/%Y')}")

            with st.form("form_ajout_event"):
                type_event = st.selectbox(
                    "Type",
                    options=[
                        ("🏥 RDV Médical", "rdv_medical"),
                        ("📅 RDV Autre", "rdv_autre"),
                        ("🎨 Activité", "activite"),
                        ("🛒 Courses", "courses"),
                        ("📜 Autre", "autre"),
                    ],
                    format_func=lambda x: x[0],
                )

                titre = st.text_input("Titre *", placeholder="Ex: Pédiatre Jules")

                col1, col2 = st.columns(2)
                with col1:
                    heure = st.time_input("Heure", value=time(10, 0))
                with col2:
                    lieu = st.text_input("Lieu", placeholder="Ex: Cabinet Dr Martin")

                notes = st.text_area("Notes", placeholder="Informations supplémentaires...")

                # Rappel
                rappel = st.selectbox(
                    "🔔 Rappel",
                    options=[None, 15, 30, 60, 120, 1440],
                    format_func=lambda x: {
                        None: "Aucun rappel",
                        15: "15 min avant",
                        30: "30 min avant",
                        60: "1h avant",
                        120: "2h avant",
                        1440: "1 jour avant",
                    }.get(x, "Aucun"),
                    index=0,
                )

                # Récurrence
                st.markdown("---")
                st.markdown("**🔄 Récurrence**")

                recurrence_type = st.selectbox(
                    "Type de récurrence",
                    options=["none", "daily", "weekly", "monthly", "yearly"],
                    format_func=lambda x: {
                        "none": "Aucune",
                        "daily": "Quotidienne",
                        "weekly": "Hebdomadaire",
                        "monthly": "Mensuelle",
                        "yearly": "Annuelle",
                    }.get(x, "Aucune"),
                    index=0,
                )

                recurrence_interval = None
                recurrence_jours = None
                recurrence_fin = None

                if recurrence_type != "none":
                    col_int, col_fin = st.columns(2)
                    with col_int:
                        recurrence_interval = st.number_input(
                            "Tous les",
                            min_value=1,
                            max_value=30,
                            value=1,
                            help="Intervalle (ex: 2 = tous les 2 jours/semaines/mois)",
                        )
                    with col_fin:
                        recurrence_fin = st.date_input(
                            "Jusqu'au",
                            value=None,
                            help="Date de fin de la récurrence (optionnel)",
                        )

                    if recurrence_type == "weekly":
                        jours_selection = st.multiselect(
                            "Jours de la semaine",
                            options=[0, 1, 2, 3, 4, 5, 6],
                            default=[date_selectionnee.weekday()],
                            format_func=lambda x: ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"][
                                x
                            ],
                        )
                        recurrence_jours = (
                            ",".join(map(str, jours_selection)) if jours_selection else None
                        )

                col_submit, col_cancel = st.columns(2)

                with col_submit:
                    submitted = st.form_submit_button("✅ Créer", type="primary")

                with col_cancel:
                    if st.form_submit_button("❌ Annuler"):
                        del st.session_state.ajouter_event_date
                        st.rerun()

                if submitted and titre:
                    # Créer l'événement via le service
                    try:
                        if type_event[1] == "activite":
                            _get_service().creer_activite(
                                titre=titre,
                                date_prevue=date_selectionnee,
                                heure_debut=heure,
                                lieu=lieu,
                                notes=notes,
                            )
                        else:
                            _get_service().creer_event_calendrier(
                                titre=titre,
                                date_event=date_selectionnee,
                                type_event=type_event[1],
                                heure=heure,
                                lieu=lieu,
                                description=notes,
                                rappel_avant_minutes=rappel,
                                recurrence_type=recurrence_type
                                if recurrence_type != "none"
                                else None,
                                recurrence_interval=recurrence_interval,
                                recurrence_jours=recurrence_jours,
                                recurrence_fin=recurrence_fin,
                            )

                        st.success(f"✅ {titre} ajouté!")
                        del st.session_state.ajouter_event_date
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")


def afficher_legende():
    """Affiche la légende du calendrier."""
    with st.expander("ℹ️ Légende"):
        cols = st.columns(6)
        legendes = [
            ("🌞 Midi", "🌙 Soir", "🍰 Goûter"),
            ("🍳 Batch", "🛒 Courses"),
            ("🎨 Activité", "🏥 RDV médical"),
            ("📅 RDV", "👶 Pour Jules"),
            ("🧹 Ménage", "🌱 Jardin"),
            ("⭐ Aujourd'hui",),
        ]
        for i, col in enumerate(cols):
            with col:
                for item in legendes[i]:
                    st.caption(item)

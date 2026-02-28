"""
Composants Calendrier - Navigation, formulaires et légende

Composants UI : navigation entre semaines, formulaire d'ajout d'événement, légende.
"""

from datetime import date, time, timedelta

import streamlit as st

from src.core.date_utils import obtenir_debut_semaine as get_debut_semaine
from src.ui.keys import KeyNamespace

from .aggregation import get_semaine_precedente, get_semaine_suivante

_keys = KeyNamespace("calendrier")

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
    from src.core.state import rerun

    if _keys("semaine_debut") not in st.session_state:
        st.session_state[_keys("semaine_debut")] = get_debut_semaine(date.today())

    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])

    with col1:
        if st.button("Semaine", use_container_width=True):
            st.session_state[_keys("semaine_debut")] = get_semaine_precedente(
                st.session_state[_keys("semaine_debut")]
            )
            rerun()

    with col2:
        semaine_debut = st.session_state[_keys("semaine_debut")]
        semaine_fin = semaine_debut + timedelta(days=6)
        st.markdown(
            f"<h3 style='text-align: center; margin: 0;'>"
            f"📅 {semaine_debut.strftime('%d/%m')} — {semaine_fin.strftime('%d/%m/%Y')}"
            f"</h3>",
            unsafe_allow_html=True,
        )

    with col3:
        if st.button("Semaine", use_container_width=True):
            st.session_state[_keys("semaine_debut")] = get_semaine_suivante(
                st.session_state[_keys("semaine_debut")]
            )
            rerun()

    with col4:
        if st.button("📅 Aujourd'hui", use_container_width=True):
            st.session_state[_keys("semaine_debut")] = get_debut_semaine(date.today())
            rerun()


def afficher_formulaire_ajout_event():
    """Affiche le formulaire d'ajout d'événement."""
    from src.core.state import rerun

    if _keys("event_date") in st.session_state:
        date_selectionnee = st.session_state[_keys("event_date")]

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
                        del st.session_state[_keys("event_date")]
                        rerun()

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
                        del st.session_state[_keys("event_date")]
                        rerun()

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

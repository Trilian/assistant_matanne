"""
Calendrier Famille – Vue partagée semaine / mois avec événements familiaux.

Onglets:
  1. Vue Semaine (agenda 7 jours)
  2. Vue Mois (grille calendrier)
  3. Gestion événements (CRUD)
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.components.atoms import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("calendrier_famille")

_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.evenements import obtenir_service_evenements

        _service = obtenir_service_evenements()
    return _service


TYPES_EVENEMENTS = [
    "rdv_medical",
    "activite",
    "anniversaire",
    "ecole",
    "vacances",
    "sortie",
    "routine",
    "autre",
]
COULEURS = {
    "rdv_medical": "🔴",
    "activite": "🟢",
    "anniversaire": "🎂",
    "ecole": "📚",
    "vacances": "🏖️",
    "sortie": "🎭",
    "routine": "🔄",
    "autre": "⚪",
}


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – VUE SEMAINE
# ═══════════════════════════════════════════════════════════


def _onglet_semaine():
    """Vue semaine avec 7 colonnes."""
    st.subheader("📅 Vue Semaine")

    svc = _get_service()

    # Navigation semaine
    col_nav1, col_nav2, col_nav3 = st.columns([1, 3, 1])
    semaine_offset = st.session_state.get(_keys("semaine_offset"), 0)

    with col_nav1:
        if st.button("◀️ Semaine précédente", key=_keys("prev_week")):
            st.session_state[_keys("semaine_offset")] = semaine_offset - 1
            st.rerun()
    with col_nav3:
        if st.button("Semaine suivante ▶️", key=_keys("next_week")):
            st.session_state[_keys("semaine_offset")] = semaine_offset + 1
            st.rerun()

    today = date.today()
    lundi = today - timedelta(days=today.weekday()) + timedelta(weeks=semaine_offset)

    with col_nav2:
        st.markdown(
            f"**Semaine du {lundi.strftime('%d/%m')} au {(lundi + timedelta(days=6)).strftime('%d/%m/%Y')}**"
        )

    try:
        evenements = svc.lister_par_semaine(lundi)
    except Exception as e:
        st.error(f"Erreur : {e}")
        return

    jours_semaine = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    cols = st.columns(7)

    for i, col in enumerate(cols):
        jour = lundi + timedelta(days=i)
        events_jour = [e for e in evenements if e.date_debut and e.date_debut.date() == jour]

        with col:
            est_aujourdhui = jour == today
            header = (
                f"**{'📍 ' if est_aujourdhui else ''}{jours_semaine[i]} {jour.strftime('%d')}**"
            )
            st.markdown(header)

            if events_jour:
                for ev in events_jour:
                    emoji = COULEURS.get(ev.type_evenement, "⚪")
                    st.caption(f"{emoji} {ev.titre}")
            else:
                st.caption("—")

    # Légende
    with st.expander("🎨 Légende"):
        for type_ev, emoji in COULEURS.items():
            st.write(f"{emoji} {type_ev.replace('_', ' ').title()}")


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – VUE MOIS
# ═══════════════════════════════════════════════════════════


def _onglet_mois():
    """Vue mois avec grille."""
    st.subheader("🗓️ Vue Mois")

    svc = _get_service()

    mois_offset = st.session_state.get(_keys("mois_offset"), 0)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("◀️ Mois", key=_keys("prev_month")):
            st.session_state[_keys("mois_offset")] = mois_offset - 1
            st.rerun()
    with col3:
        if st.button("Mois ▶️", key=_keys("next_month")):
            st.session_state[_keys("mois_offset")] = mois_offset + 1
            st.rerun()

    today = date.today()
    mois = today.month + mois_offset
    annee = today.year
    while mois > 12:
        mois -= 12
        annee += 1
    while mois < 1:
        mois += 12
        annee -= 1

    with col2:
        try:
            nom_mois = date(annee, mois, 1).strftime("%B %Y").capitalize()
        except Exception:
            nom_mois = f"{mois}/{annee}"
        st.markdown(f"### {nom_mois}")

    try:
        premier_jour = date(annee, mois, 1)
        if mois == 12:
            dernier_jour = date(annee + 1, 1, 1) - timedelta(days=1)
        else:
            dernier_jour = date(annee, mois + 1, 1) - timedelta(days=1)

        evenements = svc.lister_par_mois(annee, mois)

        # Grille du mois
        jours_semaine = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        cols_header = st.columns(7)
        for i, col in enumerate(cols_header):
            with col:
                st.markdown(f"**{jours_semaine[i]}**")

        jour_courant = premier_jour - timedelta(days=premier_jour.weekday())
        while jour_courant <= dernier_jour + timedelta(days=6 - dernier_jour.weekday()):
            cols = st.columns(7)
            for i, col in enumerate(cols):
                with col:
                    if jour_courant.month == mois:
                        events_jour = [
                            e
                            for e in evenements
                            if e.date_debut and e.date_debut.date() == jour_courant
                        ]
                        est_aujourdhui = jour_courant == today
                        prefix = "📍" if est_aujourdhui else ""
                        nb_events = len(events_jour)
                        badge = f" ({nb_events})" if nb_events > 0 else ""
                        st.caption(f"{prefix}**{jour_courant.day}**{badge}")
                    else:
                        st.caption("")
                jour_courant += timedelta(days=1)

    except Exception as e:
        st.error(f"Erreur vue mois : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – GESTION ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


def _onglet_evenements():
    """CRUD événements familiaux."""
    st.subheader("✏️ Gestion des Événements")

    svc = _get_service()

    with st.expander("➕ Nouvel événement", expanded=False):
        with st.form(_keys("form_event")):
            titre = st.text_input("Titre", key=_keys("ev_titre"))
            col1, col2 = st.columns(2)
            with col1:
                type_ev = st.selectbox("Type", options=TYPES_EVENEMENTS, key=_keys("ev_type"))
                date_debut = st.date_input(
                    "Date début", value=date.today(), key=_keys("ev_date_debut")
                )
            with col2:
                recurrence = st.selectbox(
                    "Récurrence",
                    ["aucune", "quotidien", "hebdomadaire", "mensuel", "annuel"],
                    key=_keys("ev_recurrence"),
                )
                date_fin = st.date_input(
                    "Date fin (optionnel)", value=None, key=_keys("ev_date_fin")
                )
            description = st.text_area("Description", key=_keys("ev_desc"))

            if st.form_submit_button("💾 Créer", type="primary"):
                if not titre:
                    st.warning("Le titre est requis.")
                else:
                    try:
                        from datetime import datetime

                        svc.create(
                            {
                                "titre": titre,
                                "type_evenement": type_ev,
                                "date_debut": datetime.combine(date_debut, datetime.min.time()),
                                "date_fin": datetime.combine(date_fin, datetime.min.time())
                                if date_fin
                                else None,
                                "recurrence": recurrence,
                                "description": description or None,
                            }
                        )
                        st.success(f"✅ Événement « {titre} » créé !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

    # Liste des événements futurs
    st.markdown("#### 📋 Événements à venir")
    try:
        today = date.today()
        from datetime import datetime

        evenements = svc.lister_par_mois(today.year, today.month)
        futurs = [e for e in evenements if e.date_debut and e.date_debut.date() >= today]
        futurs.sort(key=lambda e: e.date_debut)

        if not futurs:
            etat_vide("Aucun événement à venir", icone="📅")
        else:
            for ev in futurs[:20]:
                emoji = COULEURS.get(ev.type_evenement, "⚪")
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"{emoji} **{ev.titre}**")
                        st.caption(f"📅 {ev.date_debut.strftime('%d/%m/%Y')} • {ev.type_evenement}")
                    with col2:
                        if st.button("🗑️", key=_keys(f"del_{ev.id}")):
                            try:
                                svc.delete(ev.id)
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
    except Exception as e:
        st.error(f"Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("calendrier_famille")
def app():
    """Point d'entrée Calendrier Famille."""
    st.title("📅 Calendrier Famille")
    st.caption("Planification partagée des événements familiaux")

    with error_boundary(titre="Erreur calendrier famille"):
        TAB_LABELS = ["📅 Semaine", "🗓️ Mois", "✏️ Événements"]
        _tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_semaine()
        with tabs[1]:
            _onglet_mois()
        with tabs[2]:
            _onglet_evenements()

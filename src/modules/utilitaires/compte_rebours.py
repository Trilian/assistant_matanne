"""
Module Compte à Rebours — J-X pour les événements importants.

Affiche les jours restants avant les événements familiaux
importants: vacances, anniversaires, fêtes, rendez-vous...
"""

import logging
from datetime import date, datetime

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("compte_rebours")

# Événements par défaut pour initialiser
EVENEMENTS_DEFAUT = [
    {"nom": "🎄 Noël", "date": f"{date.today().year}-12-25", "emoji": "🎄"},
    {"nom": "🎆 Nouvel An", "date": f"{date.today().year + 1}-01-01", "emoji": "🎆"},
]


def _get_evenements() -> list[dict]:
    """Récupère les événements du session_state."""
    if "compte_rebours_events" not in st.session_state:
        st.session_state["compte_rebours_events"] = list(EVENEMENTS_DEFAUT)
    return st.session_state["compte_rebours_events"]


@profiler_rerun("compte_rebours")
def app():
    """Point d'entrée module Compte à Rebours."""
    st.title("⏳ Compte à Rebours")
    st.caption("J-X avant les événements importants de la famille")

    with error_boundary(titre="Erreur compte à rebours"):
        evenements = _get_evenements()

        # Ajouter un événement
        with st.expander("➕ Ajouter un événement", expanded=False):
            _formulaire_ajout(evenements)

        st.divider()

        # Trier par date la plus proche
        aujourd_hui = date.today()

        events_avec_delta = []
        for evt in evenements:
            try:
                evt_date = datetime.strptime(evt["date"], "%Y-%m-%d").date()
                delta = (evt_date - aujourd_hui).days
                events_avec_delta.append((evt, evt_date, delta))
            except (ValueError, KeyError):
                continue

        events_avec_delta.sort(key=lambda x: x[2])

        # Séparer passés et futurs
        futurs = [(e, d, delta) for e, d, delta in events_avec_delta if delta >= 0]
        passes = [(e, d, delta) for e, d, delta in events_avec_delta if delta < 0]

        # Affichage des événements à venir
        if futurs:
            st.subheader("📅 À venir")
            for i, (evt, evt_date, delta) in enumerate(futurs):
                emoji = evt.get("emoji", "📌")
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"### {emoji} {evt['nom']}")
                        st.caption(evt_date.strftime("%A %d %B %Y"))
                    with col2:
                        if delta == 0:
                            st.markdown("### 🎉 C'est aujourd'hui !")
                        elif delta == 1:
                            st.markdown("### ⚡ Demain !")
                        elif delta <= 7:
                            st.markdown(f"### 🔥 J-{delta}")
                        elif delta <= 30:
                            st.markdown(f"### 📆 J-{delta}")
                        else:
                            semaines = delta // 7
                            st.markdown(f"### J-{delta}")
                            st.caption(f"({semaines} semaines)")
                    with col3:
                        idx = evenements.index(evt)
                        if st.button("🗑️", key=_keys("del", str(i)), help="Supprimer"):
                            evenements.pop(idx)
                            st.session_state["compte_rebours_events"] = evenements
                            st.rerun()

                    # Barre de progression (sur ~365 jours max)
                    if 0 < delta <= 365:
                        progress = 1 - (delta / 365)
                        st.progress(progress)
        else:
            st.info("Aucun événement à venir. Ajoutez-en un ci-dessus !")

        # Événements passés
        if passes:
            with st.expander(f"📜 Événements passés ({len(passes)})"):
                for evt, evt_date, delta in passes:
                    st.caption(
                        f"{evt.get('emoji', '📌')} {evt['nom']} — "
                        f"{evt_date.strftime('%d/%m/%Y')} (il y a {abs(delta)} jours)"
                    )


def _formulaire_ajout(evenements: list):
    """Formulaire d'ajout d'événement."""
    with st.form("form_event", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            nom = st.text_input("Nom de l'événement", key=_keys("new_nom"))
        with col2:
            date_evt = st.date_input("Date", value=date.today(), key=_keys("new_date"))
        with col3:
            emoji = st.text_input("Emoji", value="📌", max_chars=2, key=_keys("new_emoji"))

        if st.form_submit_button("➕ Ajouter", use_container_width=True):
            if nom:
                evenements.append(
                    {
                        "nom": nom,
                        "date": date_evt.strftime("%Y-%m-%d"),
                        "emoji": emoji or "📌",
                    }
                )
                st.session_state["compte_rebours_events"] = evenements
                st.success(f"✅ '{nom}' ajouté !")
                st.rerun()
            else:
                st.warning("Le nom est obligatoire.")

"""
Module Minuteur / Chronomètre — Timers cuisine avec préréglages.

Multi-minuteurs simultanés avec préréglages cuisine (pâtes, œufs,
pain...), alarme sonore et chronomètre intégré.
Note: Les timers utilisent st.session_state et auto-refresh pour
simuler le décompte en temps réel dans Streamlit.
"""

import logging
from datetime import datetime, timedelta

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("minuteur")

# Préréglages cuisine (en secondes)
PRESETS = {
    "🍝 Pâtes al dente": 8 * 60,
    "🍝 Pâtes cuites": 11 * 60,
    "🥚 Œuf à la coque": 3 * 60,
    "🥚 Œuf mollet": 6 * 60,
    "🥚 Œuf dur": 10 * 60,
    "🍞 Pain maison": 35 * 60,
    "🍰 Gâteau moyen": 30 * 60,
    "🥧 Tarte": 25 * 60,
    "🍗 Poulet rôti (1.5kg)": 75 * 60,
    "🐟 Poisson au four": 20 * 60,
    "🍕 Pizza": 12 * 60,
    "🫕 Cocotte mijotée": 120 * 60,
    "🍚 Riz": 12 * 60,
    "☕ Thé vert": 2 * 60,
    "☕ Thé noir": 4 * 60,
    "☕ Infusion": 5 * 60,
    "⏱️ 1 minute": 60,
    "⏱️ 5 minutes": 5 * 60,
    "⏱️ 10 minutes": 10 * 60,
    "⏱️ 15 minutes": 15 * 60,
    "⏱️ 30 minutes": 30 * 60,
}


def _get_timers() -> list[dict]:
    """Récupère la liste des minuteurs actifs du session_state."""
    if "minuteurs_actifs" not in st.session_state:
        st.session_state["minuteurs_actifs"] = []
    return st.session_state["minuteurs_actifs"]


def _format_duree(secondes: int) -> str:
    """Formate une durée en HH:MM:SS ou MM:SS."""
    if secondes < 0:
        return "00:00"
    h = secondes // 3600
    m = (secondes % 3600) // 60
    s = secondes % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


@profiler_rerun("minuteur")
def app():
    """Point d'entrée module Minuteur / Chronomètre."""
    st.title("⏱️ Minuteur & Chronomètre")
    st.caption("Timers cuisine avec préréglages et chronomètre")

    with error_boundary(titre="Erreur minuteur"):
        tab1, tab2 = st.tabs(["⏱️ Minuteurs", "🕐 Chronomètre"])

        with tab1:
            _onglet_minuteurs()
        with tab2:
            _onglet_chronometre()


def _onglet_minuteurs():
    """Interface de gestion des minuteurs."""
    timers = _get_timers()

    # Ajouter un minuteur
    st.subheader("➕ Nouveau minuteur")

    col1, col2 = st.columns([2, 1])
    with col1:
        preset = st.selectbox(
            "Préréglage",
            options=["Personnalisé"] + list(PRESETS.keys()),
            key=_keys("preset"),
        )
    with col2:
        nom = st.text_input("Nom (optionnel)", key=_keys("nom_timer"))

    if preset == "Personnalisé":
        col1, col2, col3 = st.columns(3)
        with col1:
            heures = st.number_input("Heures", min_value=0, max_value=23, value=0, key=_keys("h"))
        with col2:
            minutes = st.number_input("Minutes", min_value=0, max_value=59, value=5, key=_keys("m"))
        with col3:
            secondes = st.number_input(
                "Secondes", min_value=0, max_value=59, value=0, key=_keys("s")
            )
        duree_sec = heures * 3600 + minutes * 60 + secondes
    else:
        duree_sec = PRESETS[preset]
        st.info(f"Durée: {_format_duree(duree_sec)}")

    if st.button("▶️ Démarrer", key=_keys("start"), use_container_width=True):
        timer_nom = nom or preset
        timers.append(
            {
                "nom": timer_nom,
                "duree_totale": duree_sec,
                "debut": datetime.now().isoformat(),
                "actif": True,
            }
        )
        st.session_state["minuteurs_actifs"] = timers
        st.rerun()

    # Affichage des minuteurs actifs
    if timers:
        st.divider()
        st.subheader(f"⏱️ Minuteurs actifs ({len(timers)})")

        a_supprimer = []
        for i, timer in enumerate(timers):
            debut = datetime.fromisoformat(timer["debut"])
            ecoule = (datetime.now() - debut).total_seconds()
            restant = max(0, timer["duree_totale"] - int(ecoule))
            progres = ecoule / timer["duree_totale"] if timer["duree_totale"] > 0 else 1

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{timer['nom']}**")
                    if restant <= 0:
                        st.error("🔔 TERMINÉ !")
                    else:
                        st.progress(
                            min(progres, 1.0),
                            text=f"⏱️ {_format_duree(restant)} restant",
                        )
                with col2:
                    st.caption(f"Total: {_format_duree(timer['duree_totale'])}")
                with col3:
                    if st.button("❌", key=_keys("del_timer", str(i)), help="Supprimer"):
                        a_supprimer.append(i)

        # Supprimer les timers marqués
        if a_supprimer:
            for idx in sorted(a_supprimer, reverse=True):
                timers.pop(idx)
            st.session_state["minuteurs_actifs"] = timers
            st.rerun()

        # Auto-refresh si des timers sont actifs
        actifs = [t for t in timers if t["actif"]]
        if actifs:
            import time

            time.sleep(0)  # Yield
            st.caption("🔄 Rafraîchissez la page pour mettre à jour les timers")
            if st.button("🔄 Rafraîchir", key=_keys("refresh"), use_container_width=True):
                st.rerun()


def _onglet_chronometre():
    """Chronomètre simple."""
    st.subheader("🕐 Chronomètre")

    if "chrono_debut" not in st.session_state:
        st.session_state["chrono_debut"] = None
        st.session_state["chrono_tours"] = []

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "▶️ Start" if not st.session_state["chrono_debut"] else "⏹️ Stop",
            key=_keys("chrono_toggle"),
            use_container_width=True,
        ):
            if st.session_state["chrono_debut"] is None:
                st.session_state["chrono_debut"] = datetime.now().isoformat()
            else:
                st.session_state["chrono_debut"] = None
            st.rerun()

    with col2:
        if st.button("🔄 Reset", key=_keys("chrono_reset"), use_container_width=True):
            st.session_state["chrono_debut"] = None
            st.session_state["chrono_tours"] = []
            st.rerun()

    with col3:
        if st.session_state["chrono_debut"] and st.button(
            "🏁 Tour", key=_keys("chrono_tour"), use_container_width=True
        ):
            debut = datetime.fromisoformat(st.session_state["chrono_debut"])
            ecoule = (datetime.now() - debut).total_seconds()
            st.session_state["chrono_tours"].append(ecoule)

    # Affichage temps
    if st.session_state["chrono_debut"]:
        debut = datetime.fromisoformat(st.session_state["chrono_debut"])
        ecoule = (datetime.now() - debut).total_seconds()
        st.markdown(f"### ⏱️ {_format_duree(int(ecoule))}")

        if st.button("🔄 Rafraîchir chrono", key=_keys("chrono_refresh")):
            st.rerun()
    else:
        st.markdown("### ⏱️ 00:00")

    # Tours
    tours = st.session_state.get("chrono_tours", [])
    if tours:
        st.markdown("**Tours:**")
        for i, t in enumerate(tours, 1):
            st.caption(f"Tour {i}: {_format_duree(int(t))}")

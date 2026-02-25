"""
Paramètres - Configuration Foyer
Gestion des informations du foyer familial.
Persistée en base de données via PersistentState (sync session_state ↔ DB).
"""

import logging
from datetime import datetime

import streamlit as st

from src.core.state import obtenir_etat
from src.core.state.persistent import PersistentState, persistent_state
from src.ui.feedback import afficher_succes
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("foyer")


# ── PersistentState : sync automatique session_state ↔ DB ──


@persistent_state(key="foyer_config", sync_interval=30, auto_commit=True)
def _obtenir_config_foyer() -> dict:
    """Valeurs par défaut du foyer (appelé une seule fois si DB vide)."""
    return {
        "nom_utilisateur": "Anne",
        "nb_adultes": 2,
        "nb_enfants": 1,
        "a_bebe": True,
        "preferences_alimentaires": [],
        "allergies": "",
    }


@ui_fragment
def afficher_foyer_config():
    """Configuration du foyer"""

    st.markdown("### 👨‍👩‍👧‍👦 Configuration Foyer")
    st.caption("Configure les informations de ton foyer")

    # État actuel
    state = obtenir_etat()

    # PersistentState gère le cycle lecture DB → session_state → écriture DB
    pstate: PersistentState = _obtenir_config_foyer()
    config = pstate.get_all()

    # Injecter le nom_utilisateur depuis l'état global si absent
    if not config.get("nom_utilisateur"):
        config["nom_utilisateur"] = state.nom_utilisateur

    # Formulaire
    with st.form("foyer_form"):
        st.markdown("#### Composition du Foyer")

        col1, col2 = st.columns(2)

        with col1:
            nom_utilisateur = st.text_input(
                "Nom d'utilisateur", value=config.get("nom_utilisateur", "Anne"), max_chars=50
            )

            nb_adultes = st.number_input(
                "Nombre d'adultes", min_value=1, max_value=10, value=config.get("nb_adultes", 2)
            )

        with col2:
            nb_enfants = st.number_input(
                "Nombre d'enfants", min_value=0, max_value=10, value=config.get("nb_enfants", 1)
            )

            a_bebe = st.checkbox(
                "👶 Présence d'un jeune enfant (< 24 mois)", value=config.get("a_bebe", False)
            )

        st.markdown("#### Preferences Alimentaires")

        preferences = st.multiselect(
            "Regimes / Restrictions",
            [
                "Vegetarien",
                "Vegetalien",
                "Sans gluten",
                "Sans lactose",
                "Halal",
                "Casher",
                "Paleo",
                "Sans porc",
            ],
            default=config.get("preferences_alimentaires", []),
        )

        allergies = st.text_area(
            "Allergies alimentaires",
            value=config.get("allergies", ""),
            placeholder="Ex: Arachides, fruits de mer...",
            help="Liste des allergies à prendre en compte",
        )

        st.markdown("---")

        submitted = st.form_submit_button(
            "💾 Sauvegarder", type="primary", use_container_width=True
        )

        if submitted:
            # Mettre à jour via PersistentState (session_state + DB automatiquement)
            pstate.update(
                {
                    "nom_utilisateur": nom_utilisateur,
                    "nb_adultes": nb_adultes,
                    "nb_enfants": nb_enfants,
                    "a_bebe": a_bebe,
                    "preferences_alimentaires": preferences,
                    "allergies": allergies,
                    "updated_at": datetime.now().isoformat(),
                }
            )

            # Force la sauvegarde immédiate en DB
            saved = pstate.commit()

            # Mettre à jour state global
            state.nom_utilisateur = nom_utilisateur

            if saved:
                afficher_succes("✅ Configuration sauvegardée en base de données !")
            else:
                afficher_succes("✅ Configuration sauvegardée (session uniquement)")

            st.rerun()

    # Afficher config actuelle + statut sync
    with st.expander("📋 Configuration actuelle"):
        st.json(pstate.get_all())
        sync_status = pstate.get_sync_status()
        if sync_status["last_sync"]:
            st.caption(
                f"🔄 Dernière sync: {sync_status['last_sync'].strftime('%H:%M:%S')} "
                f"• {sync_status['sync_count']} sync(s)"
            )

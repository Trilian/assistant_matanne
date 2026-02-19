"""
Paramètres - Configuration Foyer
Gestion des informations du foyer familial
"""

from datetime import datetime

import streamlit as st

from src.core.state import obtenir_etat
from src.ui.feedback import afficher_succes


def afficher_foyer_config():
    """Configuration du foyer"""

    st.markdown("### 👨‍👩‍👧‍👦 Configuration Foyer")
    st.caption("Configure les informations de ton foyer")

    # État actuel
    state = obtenir_etat()

    # Recuperer config existante
    config = st.session_state.get(
        "foyer_config",
        {
            "nom_utilisateur": state.nom_utilisateur,
            "nb_adultes": 2,
            "nb_enfants": 1,
            "age_enfants": [2],
            "a_bebe": True,
            "preferences_alimentaires": [],
        },
    )

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
            # Sauvegarder config
            new_config = {
                "nom_utilisateur": nom_utilisateur,
                "nb_adultes": nb_adultes,
                "nb_enfants": nb_enfants,
                "a_bebe": a_bebe,
                "preferences_alimentaires": preferences,
                "allergies": allergies,
                "updated_at": datetime.now().isoformat(),
            }

            st.session_state.foyer_config = new_config

            # Mettre à jour state
            state.nom_utilisateur = nom_utilisateur

            afficher_succes("✅ Configuration sauvegardée !")
            st.rerun()

    # Afficher config actuelle
    with st.expander("📋 Configuration actuelle"):
        st.json(config)

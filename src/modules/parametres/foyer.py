"""
Paramètres - Configuration Foyer
Gestion des informations du foyer familial.
Persistée en base de données via le modèle UserPreference.
"""

import logging
from datetime import datetime

import streamlit as st

from src.core.state import obtenir_etat
from src.ui.feedback import afficher_succes

logger = logging.getLogger(__name__)


def _charger_config_db() -> dict | None:
    """Charge la config foyer depuis la DB (UserPreference)."""
    try:
        from src.core.db import obtenir_db_securise
        from src.core.models.user_preferences import UserPreference

        with obtenir_db_securise() as db:
            if db is None:
                return None
            pref = db.query(UserPreference).first()
            if pref is None:
                return None
            return {
                "nom_utilisateur": pref.user_id,
                "nb_adultes": pref.nb_adultes,
                "nb_enfants": 1,  # Non stocké dans le modèle actuel
                "a_bebe": pref.jules_present,
                "preferences_alimentaires": pref.aliments_exclus or [],
                "allergies": ", ".join(pref.aliments_exclus) if pref.aliments_exclus else "",
                "updated_at": pref.updated_at.isoformat() if pref.updated_at else None,
            }
    except Exception as e:
        logger.debug(f"Chargement config foyer DB: {e}")
        return None


def _sauvegarder_config_db(config: dict) -> bool:
    """Persiste la config foyer en DB via UserPreference."""
    try:
        from src.core.db import obtenir_db_securise
        from src.core.models.user_preferences import UserPreference

        with obtenir_db_securise() as db:
            if db is None:
                return False

            pref = db.query(UserPreference).first()
            if pref is None:
                pref = UserPreference(
                    user_id=config.get("nom_utilisateur", "default"),
                )
                db.add(pref)

            pref.user_id = config.get("nom_utilisateur", pref.user_id)
            pref.nb_adultes = config.get("nb_adultes", 2)
            pref.jules_present = config.get("a_bebe", True)

            allergies_str = config.get("allergies", "")
            prefs_alimentaires = config.get("preferences_alimentaires", [])
            if allergies_str:
                pref.aliments_exclus = [a.strip() for a in allergies_str.split(",") if a.strip()]
            elif prefs_alimentaires:
                pref.aliments_exclus = prefs_alimentaires

            # Commit automatique via le context manager
            return True
    except Exception as e:
        logger.warning(f"Sauvegarde config foyer DB: {e}")
        return False


def afficher_foyer_config():
    """Configuration du foyer"""

    st.markdown("### 👨‍👩‍👧‍👦 Configuration Foyer")
    st.caption("Configure les informations de ton foyer")

    # État actuel
    state = obtenir_etat()

    # Recuperer config: DB → session_state → defaults
    if "foyer_config" not in st.session_state:
        db_config = _charger_config_db()
        if db_config:
            st.session_state["foyer_config"] = db_config
            logger.debug("Config foyer chargée depuis la DB")

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

            # Persister en DB
            saved = _sauvegarder_config_db(new_config)
            if saved:
                afficher_succes("✅ Configuration sauvegardée en base de données !")
            else:
                afficher_succes("✅ Configuration sauvegardée (session uniquement)")

            st.rerun()

    # Afficher config actuelle
    with st.expander("📋 Configuration actuelle"):
        st.json(config)

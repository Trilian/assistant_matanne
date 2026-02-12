"""
Initialisation de l'application.
"""

import logging
import streamlit as st

from src.core.state import GestionnaireEtat, obtenir_etat
from src.core.database import verifier_connexion

logger = logging.getLogger(__name__)


def initialiser_app() -> bool:
    """
    Initialise l'application.
    
    Returns:
        True si l'initialisation a réussi, False sinon.
    """
    logger.info("ðŸš€ Initialisation app (lazy)...")

    # State Manager
    GestionnaireEtat.initialiser()
    logger.info("âœ… StateManager OK")

    # Database
    if not verifier_connexion():
        st.error("âŒ Connexion DB impossible")
        st.stop()
        return False

    logger.info("âœ… Database OK")

    # Client IA (lazy - chargé si besoin)
    etat = obtenir_etat()
    if not etat.agent_ia:
        try:
            from src.core.ai import obtenir_client_ia
            etat.agent_ia = obtenir_client_ia()
            logger.info("âœ… Client IA OK")
        except Exception as e:
            logger.warning(f"âš ï¸ Client IA indispo: {e}")

    logger.info("âœ… App initialisée (lazy mode)")
    return True

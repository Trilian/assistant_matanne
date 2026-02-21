"""
Initialisation de l'application.
"""

import logging

import streamlit as st

from src.core.db import verifier_connexion
from src.core.state import GestionnaireEtat, obtenir_etat

logger = logging.getLogger(__name__)


def initialiser_app() -> bool:
    """
    Initialise l'application.

    Returns:
        True si l'initialisation a réussi, False sinon.
    """
    logger.info("🚀 Initialisation app (lazy)...")

    # State Manager
    GestionnaireEtat.initialiser()
    logger.info("✅ StateManager OK")

    # Database
    if not verifier_connexion():
        st.error("❌ Connexion DB impossible")
        st.stop()
        return False

    logger.info("✅ Database OK")

    # Client IA (lazy - chargé si besoin)
    etat = obtenir_etat()
    if not etat.agent_ia:
        try:
            from src.core.ai import obtenir_client_ia

            etat.agent_ia = obtenir_client_ia()
            logger.info("✅ Client IA OK")
        except Exception as e:
            logger.warning(f"⚠️ Client IA indispo: {e}")

    # Validation cohérence menu / registry
    from src.core.lazy_loader import RouteurOptimise, valider_coherence_menu
    from src.ui.layout.sidebar import MODULES_MENU

    manquantes = valider_coherence_menu(MODULES_MENU, RouteurOptimise.MODULE_REGISTRY)
    if manquantes:
        logger.error(f"❌ Clés menu sans registry: {manquantes}")

    # Thème dynamique (clair/sombre/auto + CSS overrides)
    from src.ui.theme import appliquer_theme

    appliquer_theme()
    logger.info("✅ Thème appliqué")

    # Tokens sémantiques (CSS custom properties light/dark)
    from src.ui.tokens_semantic import injecter_tokens_semantiques

    injecter_tokens_semantiques()
    logger.info("✅ Tokens sémantiques injectés")

    # CSS accessibilité (sr-only, focus-visible, reduced-motion)
    from src.ui.a11y import A11y

    A11y.injecter_css()
    logger.info("✅ CSS accessibilité injecté")

    # Animations centralisées (@keyframes, micro-interactions)
    from src.ui.animations import injecter_animations

    injecter_animations()
    logger.info("✅ Animations injectées")

    logger.info("✅ App initialisée (lazy mode)")
    return True

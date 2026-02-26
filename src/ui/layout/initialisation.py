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

    # Validation cohérence navigation
    # Note: avec st.navigation(), la cohérence est assurée par construction
    # dans src.core.navigation.construire_pages()
    logger.info("✅ Navigation st.navigation() active")

    # ── Pipeline CSS unifié ──────────────────────────────
    # CSS critique (first paint) → inject_all() immédiat
    # CSS non-critique (a11y, animations) → inject_deferred() après le rendu
    from src.ui.engine import CSSManager

    # 0. Styles globaux (root vars, main-header, responsive, print)
    from src.ui.layout.styles import injecter_css

    injecter_css()
    logger.info("✅ Styles globaux enregistrés")

    # 1. Thème dynamique (clair/sombre/auto + CSS overrides)
    from src.ui.theme import appliquer_theme

    appliquer_theme()
    logger.info("✅ Thème appliqué")

    # 2. Tokens sémantiques (CSS custom properties light/dark)
    from src.ui.tokens_semantic import injecter_tokens_semantiques

    injecter_tokens_semantiques()
    logger.info("✅ Tokens sémantiques injectés")

    # ── Injection batch critique — styles visibles au 1er paint ──
    CSSManager.inject_all()
    logger.info("✅ CSS critique injecté (1 appel)")

    # ── CSS différé (non-critique, chargé après le 1er paint) ──
    # 3. CSS accessibilité (sr-only, focus-visible, reduced-motion)
    from src.ui.a11y import A11y

    A11y.injecter_css_differe()
    logger.info("✅ CSS accessibilité enregistré (différé)")

    # 4. Animations centralisées (@keyframes, micro-interactions)
    from src.ui.animations import injecter_animations_differees

    injecter_animations_differees()
    logger.info("✅ Animations enregistrées (différées)")

    # Injection batch différée — arrive après le rendu critique
    CSSManager.inject_deferred()
    logger.info("✅ CSS différé injecté")

    logger.info("✅ App initialisée (lazy mode)")
    return True

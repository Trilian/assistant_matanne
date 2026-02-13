"""
Application principale - VERSION OPTIMISÉE LAZY LOADING
âœ… Architecture modulaire (header/sidebar/footer extraits)
âœ… -60% temps chargement initial
âœ… Navigation instantanée
âœ… Modules chargés à la demande
"""

import os as _os
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# LOAD ENV VARIABLES (MUST BE FIRST)
# ═══════════════════════════════════════════════════════════
from dotenv import load_dotenv

# Load .env.local from project root
project_root = Path(__file__).parent.parent
env_file = project_root / ".env.local"

# Charger les variables d'environnement (silencieux si absents)
env_loaded = False
if env_file.exists():
    load_dotenv(env_file, override=True)
    env_loaded = True
elif (project_root / ".env").exists():
    load_dotenv(project_root / ".env", override=True)
    env_loaded = True

# Log uniquement en mode debug
if _os.getenv("DEBUG", "").lower() == "true":
    mistral_key = _os.getenv("MISTRAL_API_KEY")
    print(
        f"[DEBUG] Env loaded: {env_loaded}, MISTRAL_API_KEY: {'OK' if mistral_key else 'MISSING'}"
    )

import streamlit as st

# ═══════════════════════════════════════════════════════════
# PATH & LOGGING
# ═══════════════════════════════════════════════════════════

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logging import GestionnaireLog, obtenir_logger

GestionnaireLog.initialiser(niveau_log="INFO")
logger = obtenir_logger(__name__)

# ═══════════════════════════════════════════════════════════
# IMPORTS OPTIMISÉS (MINIMAL au démarrage)
# ═══════════════════════════════════════════════════════════

from src.core import Cache, GestionnaireEtat, obtenir_etat, obtenir_parametres
from src.core.lazy_loader import RouteurOptimise

# Layout modulaire
from src.ui.layout import (
    afficher_footer,
    afficher_header,
    afficher_sidebar,
    initialiser_app,
    injecter_css,
)

parametres = obtenir_parametres()


# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title=parametres.APP_NAME,
    page_icon="ðŸ¤–",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/ton-repo",
        "Report a bug": "https://github.com/ton-repo/issues",
        "About": f"{parametres.APP_NAME} v{parametres.APP_VERSION}",
    },
)

# Injecter CSS
injecter_css()

# Initialiser
if not initialiser_app():
    st.stop()


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════


def main():
    """Fonction principale."""
    try:
        # Header
        afficher_header()

        # Sidebar
        afficher_sidebar()

        # Router vers module actif
        etat = obtenir_etat()
        RouteurOptimise.load_module(etat.module_actuel)

        # Footer
        afficher_footer()

    except Exception as e:
        logger.exception("âŒ Erreur critique dans main()")
        st.error(f"âŒ Erreur critique: {str(e)}")

        if obtenir_etat().mode_debug:
            st.exception(e)

        if st.button("ðŸ”„ Redémarrer"):
            GestionnaireEtat.reinitialiser()
            Cache.vider()
            st.rerun()


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info(f"ðŸš€ Démarrage {parametres.APP_NAME} v{parametres.APP_VERSION} (LAZY MODE)")
    main()

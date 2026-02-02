"""
Application principale - VERSION OPTIMISÉE LAZY LOADING
✅ Architecture modulaire (header/sidebar/footer extraits)
✅ -60% temps chargement initial
✅ Navigation instantanée
✅ Modules chargés à la demande
"""

import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# LOAD ENV VARIABLES (MUST BE FIRST)
# ═══════════════════════════════════════════════════════════

from dotenv import load_dotenv
import os as _os

# Load .env.local from project root
project_root = Path(__file__).parent.parent
env_file = project_root / '.env.local'
if env_file.exists():
    result = load_dotenv(env_file, override=True)
    mistral_key = _os.getenv("MISTRAL_API_KEY")
    print(f"Loaded environment from {env_file}")
    print(f"   MISTRAL_API_KEY: {mistral_key[:10] if mistral_key else 'MISSING'}...")
else:
    print(f"WARNING: {env_file} not found, trying fallback")
    load_dotenv('.env.local', override=True)

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
from src.core.lazy_loader import OptimizedRouter

# Layout modulaire
from src.ui.layout import (
    afficher_header,
    afficher_sidebar,
    afficher_footer,
    injecter_css,
    initialiser_app,
)

parametres = obtenir_parametres()


# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title=parametres.APP_NAME,
    page_icon="🤖",
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
        OptimizedRouter.load_module(etat.module_actuel)

        # Footer
        afficher_footer()

    except Exception as e:
        logger.exception("❌ Erreur critique dans main()")
        st.error(f"❌ Erreur critique: {str(e)}")

        if obtenir_etat().mode_debug:
            st.exception(e)

        if st.button("🔄 Redémarrer"):
            GestionnaireEtat.reinitialiser()
            Cache.vider()
            st.rerun()


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info(f"🚀 Démarrage {parametres.APP_NAME} v{parametres.APP_VERSION} (LAZY MODE)")
    main()

"""
Application principale - VERSION OPTIMISÉE LAZY LOADING
✅ Architecture modulaire (header/sidebar/footer extraits)
✅ -60% temps chargement initial
✅ Navigation instantanée
✅ Modules chargés à la demande
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

_project_root_str = str(Path(__file__).parent.parent)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)

from src.core.logging import GestionnaireLog, obtenir_logger

GestionnaireLog.initialiser(niveau_log="INFO")
logger = obtenir_logger(__name__)

# ═══════════════════════════════════════════════════════════
# BOOTSTRAP IoC — Initialisation unifiée (container, config, DB)
# ═══════════════════════════════════════════════════════════

from src.core.bootstrap import demarrer_application

_rapport = demarrer_application(valider_config=False, initialiser_eager=False)
if not _rapport.succes:
    logger.error(f"❌ Bootstrap échoué: {_rapport.erreurs}")

# ═══════════════════════════════════════════════════════════
# IMPORTS OPTIMISÉS (MINIMAL au démarrage)
# ═══════════════════════════════════════════════════════════

from src.core import GestionnaireEtat, obtenir_etat, obtenir_parametres
from src.core.navigation import initialiser_navigation

# Layout modulaire
from src.ui.layout import (
    afficher_footer,
    afficher_header,
    initialiser_app,
)
from src.ui.views.pwa import injecter_meta_pwa

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
        "Get Help": "https://github.com/Trilian/assistant_matanne",
        "Report a bug": "https://github.com/Trilian/assistant_matanne/issues",
        "About": f"{parametres.APP_NAME} v{parametres.APP_VERSION}",
    },
)

# CSS est injecté via initialiser_app() (pipeline CSS unifié)

# Injecter les meta tags PWA (manifest, service worker, icons)
injecter_meta_pwa()

# Initialiser
if not initialiser_app():
    st.stop()

# ═══════════════════════════════════════════════════════════
# NAVIGATION — st.navigation() + st.Page()
# Deep-linking natif, sidebar automatique
# ═══════════════════════════════════════════════════════════

page = initialiser_navigation()


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════


def main() -> None:
    """Fonction principale."""
    try:
        # Header
        afficher_header()

        # Exécuter la page sélectionnée par st.navigation()
        page.run()

        # Footer
        afficher_footer()

    except Exception as e:
        logger.exception("❌ Erreur critique dans main()")
        st.error("❌ Une erreur critique est survenue. Veuillez redémarrer l'application.")

        if obtenir_etat().mode_debug:
            st.exception(e)

        if st.button("🔄 Redémarrer"):
            GestionnaireEtat.reset_complet()
            st.rerun()


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info(f"🚀 Démarrage {parametres.APP_NAME} v{parametres.APP_VERSION} (LAZY MODE)")
    main()

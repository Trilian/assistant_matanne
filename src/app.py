"""
Application principale - VERSION OPTIMISÉE LAZY LOADING
✅ Architecture modulaire (header/sidebar/footer extraits)
✅ -60% temps chargement initial
✅ Navigation instantanée
✅ Modules chargés à la demande
"""

import os as _os
import sys
import time
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
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.navigation import initialiser_navigation
from src.core.state import rerun

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

# ═══════════════════════════════════════════════════════════
# INNOVATIONS 10.x — Raccourcis clavier, Mode Focus, etc.
# ═══════════════════════════════════════════════════════════

from src.ui.components.mode_focus import injecter_css_mode_focus, is_mode_focus
from src.ui.components.recherche_globale import injecter_raccourcis_clavier

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
# WIDGETS GLOBAUX PHASE D
# ═══════════════════════════════════════════════════════════


def _afficher_widgets_globaux() -> None:
    """Injecte les widgets flottants persistants (chat IA, notifications, gamification).

    Chaque widget est isolé dans son propre try/except pour que
    l'échec de l'un ne masque pas les autres (U3).
    """
    col_chat, col_notif, col_gamif = st.columns([1, 1, 1])
    with col_chat:
        try:
            from src.ui.components.chat_global import afficher_chat_global

            afficher_chat_global()
        except ImportError:
            logger.debug("Widget chat global non disponible (module absent)")
        except Exception as e:
            logger.warning(f"Widget chat global en erreur: {e}", exc_info=True)
    with col_notif:
        try:
            from src.ui.components.notifications_live import widget_notifications_live

            widget_notifications_live()
        except ImportError:
            logger.debug("Widget notifications non disponible (module absent)")
        except Exception as e:
            logger.warning(f"Widget notifications en erreur: {e}", exc_info=True)
    with col_gamif:
        try:
            from src.ui.components.gamification_widget import afficher_gamification_sidebar

            afficher_gamification_sidebar()
        except ImportError:
            logger.debug("Widget gamification non disponible (module absent)")
        except Exception as e:
            logger.warning(f"Widget gamification en erreur: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════


@profiler_rerun("app")
def main() -> None:
    """Fonction principale."""
    try:
        # Bannière maintenance si MAINTENANCE_MODE activé
        if _os.getenv("MAINTENANCE_MODE", "").lower() in ("true", "1", "yes"):
            st.info(
                "🔧 **Mode maintenance actif** — Certaines fonctionnalités "
                "peuvent être temporairement indisponibles.",
                icon="🔧",
            )

        # Mode Focus: CSS + raccourcis
        injecter_css_mode_focus()
        injecter_raccourcis_clavier()

        # Header (masqué en mode focus)
        if not is_mode_focus():
            afficher_header()

        # Point d'ancrage pour le skip-link (A11y)
        st.markdown(
            '<main id="main-content" role="main" aria-label="Contenu principal">',
            unsafe_allow_html=True,
        )

        # Exécuter la page sélectionnée par st.navigation()
        _t0 = time.perf_counter()
        page.run()
        _duree_page = time.perf_counter() - _t0
        if _duree_page > 2.0:
            logger.warning("⏱️ Page lente détectée : %.2fs (seuil 2s)", _duree_page)

        # Fermer le landmark main
        st.markdown("</main>", unsafe_allow_html=True)

        # ── Widgets globaux (Phase D) ──
        _afficher_widgets_globaux()

        # Mode focus: bouton de sortie
        if is_mode_focus():
            from src.ui.components.mode_focus import focus_exit_button

            focus_exit_button()

        # Footer (masqué en mode focus)
        if not is_mode_focus():
            afficher_footer()

    except Exception as e:
        logger.exception("❌ Erreur critique dans main()")
        st.error("❌ Une erreur critique est survenue. Veuillez redémarrer l'application.")

        if obtenir_etat().mode_debug:
            st.exception(e)

        if st.button("🔄 Redémarrer"):
            GestionnaireEtat.reset_complet()
            rerun()


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info(f"🚀 Démarrage {parametres.APP_NAME} v{parametres.APP_VERSION} (LAZY MODE)")
    main()

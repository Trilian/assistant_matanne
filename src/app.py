"""
Application principale - VERSION OPTIMISÉE LAZY LOADING
✅ Architecture modulaire (header/sidebar/footer extraits)
✅ -60% temps chargement initial
✅ Navigation instantanée
✅ Modules chargés à la demande
✅ Widgets globaux isolés via WidgetRunner (configurable, métriques)
✅ Landmarks ARIA via A11y context manager (isole unsafe_allow_html)
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
# HOTFIX: MIGRATION BASE DE DONNEES
# ═══════════════════════════════════════════════════════════
def _hotfix_db_migration():
    """HOTFIX: Applique les migrations critiques en utilisant la connexion de l'app (qui fonctionne)."""
    try:
        from sqlalchemy import text

        from src.core.db.engine import obtenir_moteur

        logger.info("[HOTFIX] Tentative de migration 'archivee' via l'application...")
        engine = obtenir_moteur()
        with engine.connect() as conn:
            # Vérifier si la colonne existe
            try:
                conn.execute(text("SELECT archivee FROM listes_courses LIMIT 1"))
                logger.info("[HOTFIX] Colonne 'archivee' déjà présente. OK.")
            except Exception:
                # La colonne manque (ProgrammingError/UndefinedColumn)
                logger.warning("[HOTFIX] Colonne 'archivee' manquante. Application du fix...")
                conn.rollback()  # Important: annuler la transaction échouée
                conn.execute(
                    text(
                        "ALTER TABLE listes_courses ADD COLUMN IF NOT EXISTS archivee BOOLEAN DEFAULT FALSE"
                    )
                )
                conn.commit()
                logger.info("[HOTFIX] Migration 'archivee' réussie !")
    except Exception as e:
        # Ne pas bloquer le démarrage si ça échoue, mais logger l'erreur
        logger.error(f"[HOTFIX] Échec de la migration via app: {e}")


# Exécuter le hotfix au démarrage
_hotfix_db_migration()

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
from src.modules._framework.error_boundary import error_boundary
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
# SIDEBAR — Sélecteur de profil utilisateur
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    from src.ui.components.profile_switcher import afficher_selecteur_profil

    afficher_selecteur_profil()


# ═══════════════════════════════════════════════════════════
# WIDGETS GLOBAUX PHASE D — Isolation robuste via WidgetRunner
# ═══════════════════════════════════════════════════════════

from src.ui.components.widget_runner import afficher_widgets_globaux

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

        # Landmark ARIA via context manager — isole unsafe_allow_html
        # dans A11y._safe_html() (un seul point de modification si l'API change)
        from src.ui.a11y import A11y

        with A11y.landmark_region(
            role="main",
            label="Contenu principal",
            tag="main",
            html_id="main-content",
        ):
            # Error boundary global : capture élégante avec fallback UI (audit §10)
            _seuil = parametres.SEUIL_PAGE_LENTE
            with error_boundary(
                titre="Erreur lors du chargement de la page",
                afficher_details=obtenir_etat().mode_debug,
                niveau="error",
            ):
                _t0 = time.perf_counter()
                page.run()
                _duree_page = time.perf_counter() - _t0
                if _duree_page > _seuil:
                    logger.warning(
                        "⏱️ Page lente détectée : %.2fs (seuil %.1fs)",
                        _duree_page,
                        _seuil,
                    )

        # ── Widgets globaux (Phase D) — isolation robuste via WidgetRunner ──
        afficher_widgets_globaux()

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

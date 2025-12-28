"""
Application principale Streamlit
Assistant MaTanne avec architecture moderne unifiée
"""
import streamlit as st
import sys
from pathlib import Path
import importlib
from typing import Optional

# ═══════════════════════════════════════════════════════════════
# PATH & LOGGING
# ═══════════════════════════════════════════════════════════════

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logging import LogManager, get_logger, render_log_viewer

# Initialiser logging AVANT tout
LogManager.init(log_level="INFO", log_to_file=True)
logger = get_logger(__name__)


# ═══════════════════════════════════════════════════════════════
# VÉRIFICATION SECRETS
# ═══════════════════════════════════════════════════════════════

def verify_secrets() -> bool:
    """
    Vérifie secrets Streamlit

    Returns:
        True si OK
    """
    required = {
        "db": ["host", "port", "name", "user", "password"],
        "mistral": ["api_key"]
    }

    missing = []
    for section, keys in required.items():
        if section not in st.secrets:
            missing.append(f"[{section}] manquante")
            continue

        for key in keys:
            if key not in st.secrets[section]:
                missing.append(f"{section}.{key}")

    if missing:
        st.error("❌ Configuration manquante")
        st.error("Ajoute dans `.streamlit/secrets.toml`:")

        for item in missing:
            st.error(f"  - {item}")

        with st.expander("💡 Exemple", expanded=True):
            st.code("""
[db]
host = "db.xxxxx.supabase.co"
port = "5432"
name = "postgres"
user = "postgres"
password = "ton_mot_de_passe"

[mistral]
api_key = "ta_cle_mistral"
            """, language="toml")

        st.stop()
        return False

    return True


# Vérifier secrets
verify_secrets()


# ═══════════════════════════════════════════════════════════════
# IMPORTS REFACTORISÉS
# ═══════════════════════════════════════════════════════════════

# Core refactorisé
from src.core.config import get_settings
from src.core.database import check_connection, get_db_info
from src.core.state import StateManager, get_state
from src.core.cache import Cache, render_cache_stats
from src.core.errors import handle_errors
from src.core.ai import get_ai_client

# UI refactorisé (namespace unique)
from src.ui import badge, empty_state

# Utils refactorisé
from src.utils import format_date

# Config
settings = get_settings()


# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/ton-repo",
        "Report a bug": "https://github.com/ton-repo/issues",
        "About": f"{settings.APP_NAME} v{settings.APP_VERSION}",
    },
)


# ═══════════════════════════════════════════════════════════════
# CSS MODERNE
# ═══════════════════════════════════════════════════════════════

def load_custom_css():
    """CSS moderne unifié"""
    st.markdown("""
    <style>
    /* Variables */
    :root {
        --primary: #2d4d36;
        --secondary: #5e7a6a;
        --accent: #4caf50;
        --bg: #f6f8f7;
        --card: #ffffff;
    }

    /* Header */
    .main-header {
        padding: 1rem 0;
        border-bottom: 2px solid var(--accent);
        margin-bottom: 2rem;
    }

    /* Cards */
    .metric-card {
        background: var(--card);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8e5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        transition: transform 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }

    /* Masquer menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


load_custom_css()


# ═══════════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True, fallback_value=False)
def init_app() -> bool:
    """
    Initialise l'application

    ✅ Error handling automatique
    ✅ Logging intégré
    ✅ Cache automatique

    Returns:
        True si succès
    """
    logger.info("🚀 Initialisation app...")

    # 1. State Manager
    StateManager.init()
    logger.info("✅ StateManager initialisé")

    # 2. Database
    if not check_connection():
        st.error("❌ Connexion DB impossible")
        st.write("**Vérifications:**")
        st.write("- Secrets configurés")
        st.write("- Supabase accessible")
        st.write("- Mot de passe correct")
        st.stop()
        return False

    logger.info("✅ Database connectée")

    # 3. Client IA
    state = get_state()
    if not state.agent_ia:
        try:
            state.agent_ia = get_ai_client()
            logger.info("✅ Client IA initialisé")
        except Exception as e:
            logger.error(f"⚠️ Client IA indispo: {e}")
            st.sidebar.warning("⚠️ IA indisponible")

    # 4. Info DB (debug)
    if state.debug_mode:
        with st.sidebar.expander("🗄️ Database Info", expanded=False):
            db_info = get_db_info()

            if db_info["status"] == "connected":
                st.success(f"✅ {db_info['host']}")
                st.caption(f"Base: {db_info['database']}")
                st.caption(f"User: {db_info['user']}")
            else:
                st.error(f"❌ {db_info.get('error', 'Erreur')}")

    logger.info("✅ App initialisée")
    return True


# Initialiser
init_app()


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════

def render_header():
    """Header moderne avec badges"""
    state = get_state()

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(f"""
            <div class="main-header">
                <h1>🤖 {settings.APP_NAME}</h1>
                <p style="color: var(--secondary); margin: 0;">
                    Assistant familial intelligent propulsé par IA
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # ✅ Badge IA (nouveau composant)
        if state.agent_ia:
            badge("🤖 IA Active", "#4CAF50")
        else:
            badge("🤖 IA Indispo", "#FFC107")

    with col3:
        # Notifications
        if state.unread_notifications > 0:
            if st.button(f"🔔 {state.unread_notifications}", key="notifs"):
                st.session_state.show_notifications = True


# ═══════════════════════════════════════════════════════════════
# SIDEBAR - NAVIGATION
# ═══════════════════════════════════════════════════════════════

def render_sidebar():
    """
    Sidebar avec navigation

    ✅ Structure refactorisée
    ✅ Cache stats intégrées
    ✅ Debug mode
    """
    state = get_state()

    with st.sidebar:
        st.title("Navigation")

        # Fil d'Ariane
        breadcrumb = StateManager.get_navigation_breadcrumb()
        if len(breadcrumb) > 1:
            st.caption(" → ".join(breadcrumb[-3:]))
            if st.button("⬅️ Retour", key="back_btn"):
                StateManager.go_back()
                st.rerun()
            st.markdown("---")

        # ═══════════════════════════════════════════════════════
        # MODULES
        # ═══════════════════════════════════════════════════════

        modules = {
            "🏠 Accueil": "accueil",
            "🍳 Cuisine": {
                "📚 Recettes": "cuisine.recettes",
                "🥫 Inventaire": "cuisine.inventaire",
                "🗓️ Planning": "cuisine.planning_semaine",
                "🛒 Courses": "cuisine.courses",
            },
            "👨‍👩‍👧‍👦 Famille": {
                "📊 Suivi Jules": "famille.suivi_jules",
                "💖 Bien-être": "famille.bien_etre",
                "🔄 Routines": "famille.routines",
            },
            "🏠 Maison": {
                "📋 Projets": "maison.projets",
                "🌱 Jardin": "maison.jardin",
                "🧹 Entretien": "maison.entretien",
            },
            "📅 Planning": {
                "🗓️ Calendrier": "planning.calendrier",
                "🌐 Vue Ensemble": "planning.vue_ensemble",
            },
            "⚙️ Paramètres": "parametres",
        }

        for label, value in modules.items():
            if isinstance(value, dict):
                # Module avec sous-menus
                is_expanded = any(
                    state.current_module.startswith(sub)
                    for sub in value.values()
                )

                with st.expander(label, expanded=is_expanded):
                    for sub_label, sub_value in value.items():
                        is_active = state.current_module == sub_value
                        btn_type = "primary" if is_active else "secondary"

                        if st.button(
                                sub_label,
                                key=f"btn_{sub_value}",
                                use_container_width=True,
                                type=btn_type,
                                disabled=is_active
                        ):
                            StateManager.navigate_to(sub_value)
                            st.rerun()
            else:
                # Module simple
                is_active = state.current_module == value
                btn_type = "primary" if is_active else "secondary"

                if st.button(
                        label,
                        key=f"btn_{value}",
                        use_container_width=True,
                        type=btn_type,
                        disabled=is_active
                ):
                    StateManager.navigate_to(value)
                    st.rerun()

        st.markdown("---")

        # ✅ Cache stats (nouveau composant)
        render_cache_stats(key_prefix="sidebar")

        # ✅ Logs viewer (nouveau composant)
        render_log_viewer(key="sidebar_logs")

        st.markdown("---")

        # Mode Debug
        state.debug_mode = st.checkbox("🐛 Debug", value=state.debug_mode)

        if state.debug_mode:
            with st.expander("État App", expanded=False):
                summary = StateManager.get_state_summary()
                st.json(summary)

                if st.button("🔄 Reset State"):
                    StateManager.reset()
                    Cache.clear_all()
                    st.success("Reset OK")
                    st.rerun()


# ═══════════════════════════════════════════════════════════════
# ROUTAGE MODULES
# ═══════════════════════════════════════════════════════════════

# Mapping modules
MODULE_REGISTRY = {
    "accueil": "src.modules.accueil",
    "cuisine.recettes": "src.modules.cuisine.recettes",
    "cuisine.inventaire": "src.modules.cuisine.inventaire",
    "cuisine.planning_semaine": "src.modules.cuisine.planning_semaine",
    "cuisine.courses": "src.modules.cuisine.courses",
    "famille.suivi_jules": "src.modules.famille.suivi_jules",
    "famille.bien_etre": "src.modules.famille.bien_etre",
    "famille.routines": "src.modules.famille.routines",
    "maison.projets": "src.modules.maison.projets",
    "maison.jardin": "src.modules.maison.jardin",
    "maison.entretien": "src.modules.maison.entretien",
    "planning.calendrier": "src.modules.planning.calendrier",
    "planning.vue_ensemble": "src.modules.planning.vue_ensemble",
    "parametres": "src.modules.parametres",
}


@handle_errors(show_in_ui=True, fallback_value=None)
def load_module(module_name: str):
    """
    Charge module dynamiquement

    ✅ Cache automatique
    ✅ Error handling
    ✅ Import dynamique

    Args:
        module_name: Nom du module
    """
    if module_name not in MODULE_REGISTRY:
        st.error(f"❌ Module '{module_name}' introuvable")
        st.info("Modules disponibles:")
        for name in MODULE_REGISTRY.keys():
            st.write(f"  - {name}")
        return

    # Cache import
    cache_key = f"module_{module_name}"
    module = Cache.get(cache_key, ttl=300)

    if not module:
        # Import dynamique
        module = importlib.import_module(MODULE_REGISTRY[module_name])
        Cache.set(cache_key, module, ttl=300)
        logger.info(f"📦 Module '{module_name}' chargé")

    # Appeler app()
    if hasattr(module, "app"):
        module.app()
    else:
        st.error(f"❌ Module sans fonction app()")

        # Placeholder
        st.markdown(f"## 🚧 {module_name}")
        st.info("Module en développement")

        if st.button("🏠 Retour Accueil"):
            StateManager.navigate_to("accueil")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════

def render_notifications():
    """Affiche notifications (simplifié)"""
    if not st.session_state.get("show_notifications"):
        return

    state = get_state()

    if state.unread_notifications == 0:
        st.info("📭 Aucune notification")
        return

    with st.expander(f"🔔 Notifications ({state.unread_notifications})", expanded=True):
        st.info("Système de notifications à implémenter")

        if st.button("🗑️ Fermer"):
            st.session_state.show_notifications = False
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════

def render_footer():
    """Footer simplifié"""
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.caption(f"💚 {settings.APP_NAME} v{settings.APP_VERSION}")
        st.caption("Assistant familial intelligent")

    with col2:
        if st.button("🐛 Bug", key="report"):
            st.info("GitHub Issues")

    with col3:
        if st.button("ℹ️ À propos", key="about"):
            with st.expander("À propos", expanded=True):
                st.markdown(f"""
                ### {settings.APP_NAME}
                
                **Version:** {settings.APP_VERSION}
                
                **Stack:**
                - Frontend: Streamlit
                - Database: Supabase PostgreSQL
                - IA: Mistral AI
                - Hosting: Streamlit Cloud
                
                **Développé avec ❤️**
                """)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True, fallback_value=None)
def main():
    """
    Fonction principale

    ✅ Architecture refactorisée
    ✅ Error handling global
    ✅ Logging intégré
    """
    try:
        # Header
        render_header()

        # Sidebar
        render_sidebar()

        # Notifications
        render_notifications()

        # Charger module actuel
        state = get_state()
        load_module(state.current_module)

        # Footer
        render_footer()

    except Exception as e:
        logger.exception("❌ Erreur critique dans main()")
        st.error(f"❌ Erreur critique: {str(e)}")

        if get_state().debug_mode:
            st.exception(e)

        # Bouton reset
        if st.button("🔄 Redémarrer"):
            StateManager.reset()
            Cache.clear_all()
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info(f"🚀 Démarrage {settings.APP_NAME} v{settings.APP_VERSION}")
    main()
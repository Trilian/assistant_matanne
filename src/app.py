"""
Application principale Streamlit - Version Refactorisée
Assistant MaTanne v2 avec architecture moderne
"""
import streamlit as st
import sys
from pathlib import Path
import logging
import importlib
from typing import Optional

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ===================================
# VÉRIFICATION DES SECRETS
# ===================================


def verify_secrets() -> bool:
    """
    Vérifie que tous les secrets nécessaires sont présents

    Returns:
        True si OK, False sinon
    """
    required_secrets = {"db": ["host", "port", "name", "user", "password"], "mistral": ["api_key"]}

    missing = []

    for section, keys in required_secrets.items():
        if section not in st.secrets:
            missing.append(f"Section [{section}] manquante")
            continue

        for key in keys:
            if key not in st.secrets[section]:
                missing.append(f"{section}.{key} manquant")

    if missing:
        st.error("❌ Configuration manquante dans les secrets Streamlit")
        st.error(
            "Ajoute ces éléments dans `.streamlit/secrets.toml` (local) ou dans les Settings (cloud) :"
        )
        for item in missing:
            st.error(f"  - {item}")

        with st.expander("💡 Exemple de configuration", expanded=True):
            st.code(
                """
[db]
host = "db.xxxxx.supabase.co"
port = "5432"
name = "postgres"
user = "postgres"
password = "ton_mot_de_passe"

[mistral]
api_key = "ta_cle_api_mistral"
            """,
                language="toml",
            )

        st.stop()
        return False

    return True


# Vérifier les secrets au démarrage
verify_secrets()


# ===================================
# IMPORTS APRÈS VÉRIFICATION
# ===================================

from src.core.config import settings
from src.core.database import check_connection, get_db_info
from src.core.ai_agent import AgentIA
from src.core.state_manager import StateManager, get_state
from src.ui.components import render_stat_row, render_badge
from src.core.ai_cache import render_cache_stats


# ===================================
# CONFIGURATION STREAMLIT
# ===================================

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


# ===================================
# CSS PERSONNALISÉ
# ===================================


def load_custom_css():
    """Charge le CSS personnalisé pour une interface moderne"""
    st.markdown(
        """
    <style>
    /* Variables */
    :root {
        --primary-color: #2d4d36;
        --secondary-color: #5e7a6a;
        --accent-color: #4caf50;
        --background: #f6f8f7;
        --card-bg: #ffffff;
    }

    /* Header personnalisé */
    .main-header {
        padding: 1rem 0;
        border-bottom: 2px solid var(--accent-color);
        margin-bottom: 2rem;
    }

    /* Cards modernes */
    .metric-card {
        background: var(--card-bg);
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

    /* Sidebar */
    .css-1d391kg {
        background-color: var(--background);
    }

    /* Masquer menu hamburger en production */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Notifications */
    .notification-badge {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #dc3545;
        color: white;
        border-radius: 50%;
        padding: 2px 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


load_custom_css()


# ===================================
# INITIALISATION
# ===================================


def init_app():
    """Initialise l'application au démarrage"""
    try:
        # 1. Initialiser StateManager
        StateManager.init()
        logger.info("✅ StateManager initialisé")

        # 2. Vérifier connexion DB
        if not check_connection():
            st.error("❌ Impossible de se connecter à la base de données")
            st.write("**Vérifications :**")
            st.write("- Les secrets sont bien configurés")
            st.write("- Le projet Supabase est accessible")
            st.write("- Le mot de passe est correct")
            st.stop()

        logger.info("✅ Base de données connectée")

        # 3. Initialiser l'agent IA
        state = get_state()
        if not state.agent_ia:
            try:
                state.agent_ia = AgentIA()
                logger.info("✅ Agent IA initialisé")
            except Exception as e:
                logger.error(f"⚠️ Agent IA non disponible: {e}")
                st.sidebar.warning("⚠️ Agent IA non disponible")

        # 4. Afficher infos DB dans sidebar (mode debug)
        if state.debug_mode:
            with st.sidebar.expander("🗄️ Info Base de Données", expanded=False):
                db_info = get_db_info()
                if db_info["status"] == "connected":
                    st.success(f"✅ Connecté à {db_info['host']}")
                    st.caption(f"Base: {db_info['database']}")
                    st.caption(f"User: {db_info['user']}")
                else:
                    st.error(f"❌ Erreur: {db_info.get('error', 'Inconnue')}")

    except Exception as e:
        logger.exception("❌ Erreur d'initialisation")
        st.error(f"❌ Erreur d'initialisation: {str(e)}")
        st.stop()


# Initialiser l'app
init_app()


# ===================================
# HEADER
# ===================================


def render_header():
    """Affiche l'en-tête de l'application"""
    state = get_state()

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(
            f"""
            <div class="main-header">
                <h1>🤖 {settings.APP_NAME}</h1>
                <p style="color: var(--secondary-color); margin: 0;">
                    Ton copilote quotidien propulsé par l'IA
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        # Status IA
        if state.agent_ia:
            render_badge("🤖 IA Active", color="#4CAF50")
        else:
            render_badge("🤖 IA Indispo", color="#FFC107")

    with col3:
        # Notifications
        if state.unread_notifications > 0:
            if st.button(f"🔔 {state.unread_notifications}", key="notifs"):
                st.session_state.show_notifications = True


# ===================================
# SIDEBAR - NAVIGATION
# ===================================


def render_sidebar():
    """Affiche la sidebar avec navigation"""
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

        # Modules principaux
        modules = {
            "🏠 Accueil": "accueil",
            "🍳 Cuisine": {
                "📚 Recettes": "cuisine.recettes",
                "🥫 Inventaire": "cuisine.inventaire",
                "🗓️ Planning Semaine": "cuisine.planning_semaine",
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
                "🌐 Vue d'ensemble": "planning.vue_ensemble",
            },
            "⚙️ Paramètres": "parametres",
        }

        for label, value in modules.items():
            if isinstance(value, dict):
                # Module avec sous-menus
                is_expanded = any(
                    state.current_module.startswith(sub_value) for sub_value in value.values()
                )

                with st.expander(label, expanded=is_expanded):
                    for sub_label, sub_value in value.items():
                        # Highlight si actif
                        is_active = state.current_module == sub_value
                        button_type = "primary" if is_active else "secondary"

                        if st.button(
                            sub_label,
                            key=f"btn_{sub_value}",
                            use_container_width=True,
                            type=button_type,
                            disabled=is_active,
                        ):
                            StateManager.navigate_to(sub_value)
                            st.rerun()
            else:
                # Module simple
                is_active = state.current_module == value
                button_type = "primary" if is_active else "secondary"

                if st.button(
                    label,
                    key=f"btn_{value}",
                    use_container_width=True,
                    type=button_type,
                    disabled=is_active,
                ):
                    StateManager.navigate_to(value)
                    st.rerun()

        st.markdown("---")

        # Stats IA (si agent disponible)
        if state.agent_ia:
            render_cache_stats(key_prefix="sidebar")

        st.markdown("---")

        # Mode Debug
        if st.checkbox("🐛 Mode Debug", key="debug_toggle"):
            state.debug_mode = True

            with st.expander("État de l'App", expanded=False):
                summary = StateManager.get_state_summary()
                st.json(summary)

                if st.button("🔄 Reset State"):
                    StateManager.reset()
                    st.success("State reset")
                    st.rerun()
        else:
            state.debug_mode = False


# ===================================
# ROUTAGE DES MODULES
# ===================================

# Mapping des modules
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


def load_module(module_name: str):
    """
    Charge et affiche le module demandé

    Args:
        module_name: Nom du module (ex: "cuisine.recettes")
    """
    if module_name not in MODULE_REGISTRY:
        st.error(f"❌ Module '{module_name}' non trouvé")
        st.info("Modules disponibles :")
        for name in MODULE_REGISTRY.keys():
            st.write(f"  - {name}")
        return

    try:
        # Import dynamique avec cache
        state = get_state()
        cache_key = f"module_{module_name}"

        # Vérifier cache
        module = StateManager.cache_get(cache_key, ttl=300)

        if not module:
            # Import
            module = importlib.import_module(MODULE_REGISTRY[module_name])
            StateManager.cache_set(cache_key, module)
            logger.info(f"📦 Module '{module_name}' chargé")

        # Appeler la fonction app()
        if hasattr(module, "app"):
            module.app()
        else:
            st.error(f"❌ Le module {module_name} n'a pas de fonction app()")

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        st.error(f"❌ Impossible de charger le module: {e}")

        st.info("ℹ️ Ce module est peut-être en cours de développement")

        # Module placeholder
        st.markdown(f"## 🚧 Module {module_name}")
        st.info("Ce module sera bientôt disponible !")

        if st.button("🏠 Retour à l'accueil"):
            StateManager.navigate_to("accueil")
            st.rerun()

    except Exception as e:
        logger.exception(f"❌ Erreur dans le module {module_name}")
        st.error(f"❌ Erreur dans le module: {e}")

        if state.debug_mode:
            st.exception(e)


# ===================================
# NOTIFICATIONS
# ===================================


def render_notifications():
    """Affiche les notifications non lues"""
    state = get_state()

    if (
        not hasattr(st.session_state, "show_notifications")
        or not st.session_state.show_notifications
    ):
        return

    notifs = StateManager.get_unread_notifications()

    if not notifs:
        st.info("📭 Aucune notification")
        return

    with st.expander(f"🔔 Notifications ({len(notifs)})", expanded=True):
        for notif in notifs:
            icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(
                notif["type"], "ℹ️"
            )

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"{icon} **{notif['message']}**")
                if notif.get("module"):
                    st.caption(f"Module: {notif['module']}")
                st.caption(notif["timestamp"].strftime("%H:%M"))

            with col2:
                if notif.get("action_link"):
                    if st.button("Aller", key=f"notif_action_{notif['id']}"):
                        StateManager.navigate_to(notif["action_link"])
                        StateManager.mark_notification_read(notif["id"])
                        st.rerun()

                if st.button("✓", key=f"notif_read_{notif['id']}"):
                    StateManager.mark_notification_read(notif["id"])
                    st.rerun()

            st.markdown("---")

        if st.button("🗑️ Tout effacer", use_container_width=True):
            StateManager.clear_notifications()
            st.session_state.show_notifications = False
            st.rerun()


# ===================================
# FOOTER
# ===================================


def render_footer():
    """Affiche le footer"""
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.caption(f"💚 {settings.APP_NAME} v{settings.APP_VERSION}")
        st.caption("Assistant familial intelligent")

    with col2:
        if st.button("🐛 Reporter un bug", key="report_bug"):
            st.info("Ouvrir une issue sur GitHub")

    with col3:
        if st.button("ℹ️ À propos", key="about"):
            with st.expander("À propos", expanded=True):
                st.markdown(
                    f"""
                ### {settings.APP_NAME}
                
                **Version:** {settings.APP_VERSION}
                
                **Stack:**
                - Frontend: Streamlit
                - Database: Supabase PostgreSQL
                - IA: Mistral AI
                - Hosting: Streamlit Cloud
                
                **Développé avec ❤️**
                """
                )


# ===================================
# PAGE PRINCIPALE
# ===================================


def main():
    """Fonction principale de l'application"""
    try:
        # Header
        render_header()

        # Sidebar
        render_sidebar()

        # Notifications
        render_notifications()

        # Charger le module actuel
        state = get_state()
        load_module(state.current_module)

        # Footer
        render_footer()

    except Exception as e:
        logger.exception("❌ Erreur critique dans main()")
        st.error(f"❌ Erreur critique: {str(e)}")

        if get_state().debug_mode:
            st.exception(e)

        # Bouton de reset
        if st.button("🔄 Redémarrer l'application"):
            StateManager.reset()
            st.rerun()


# ===================================
# POINT D'ENTRÉE
# ===================================

if __name__ == "__main__":
    main()

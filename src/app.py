"""
Application principale Streamlit - Version adaptée pour Streamlit Cloud + Supabase
Assistant MaTanne v2 avec Agent IA intégré
"""
import streamlit as st
import sys
from pathlib import Path
import logging
from contextlib import contextmanager

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_supabase_connection():
    """Teste la connexion à Supabase avec psycopg2"""
    try:
        import psycopg2
        from psycopg2 import OperationalError

        conn = psycopg2.connect(
            host=st.secrets['db']['host'],
            port=st.secrets['db']['port'],
            dbname=st.secrets['db']['name'],
            user=st.secrets['db']['user'],
            password=st.secrets['db']['password'],
            sslmode='require',  # ✅ Force SSL
            connect_timeout=10  # ✅ Timeout de 10 secondes
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        st.success(f"✅ Connexion réussie ! Version PostgreSQL: {version[0]}")
        conn.close()

    except OperationalError as e:
        st.error(f"❌ Échec de la connexion: {e}")
        st.info("Vérifie que :")
        st.info("- Le host commence bien par 'db.'")
        st.info("- Le mot de passe est correct")
        st.info("- Les règles réseau Supabase autorisent Streamlit Cloud")
        st.info("- IPv6 est activé dans Supabase")
    except Exception as e:
        st.error(f"❌ Erreur inattendue: {e}")

# Appelle cette fonction au début de ton app
test_supabase_connection()
# ===================================
# VÉRIFICATION DES SECRETS
# ===================================
def verify_secrets():
    """Vérifie que tous les secrets nécessaires sont présents"""
    required_secrets = {
        'db': ['host', 'port', 'name', 'user', 'password'],
        'mistral': ['api_key']
    }

    missing = []
    for section, keys in required_secrets.items():
        if section not in st.secrets:
            missing.append(f"Section [{section}] manquante")
            continue

        for key in keys:
            if key not in st.secrets[section]:
                missing.append(f"{section}.{key} manquant")

    if missing:
        st.error("❌ Configuration manquante :")
        for item in missing:
            st.error(f"- {item}")
        st.stop()

# ===================================
# IMPORTS APRES VERIFICATION
# ===================================
verify_secrets()

from src.core.config import settings
from src.core.database import (
    get_db_context,
    check_connection,
    get_db_info,
    SessionLocal,
    create_all_tables
)
from src.core.ai_agent import AgentIA

# ===================================
# CONFIGURATION STREAMLIT
# ===================================
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ton-repo',
        'Report a bug': 'https://github.com/ton-repo/issues',
        'About': f"{settings.APP_NAME} v{settings.APP_VERSION}"
    }
)

# ===================================
# STYLE CSS PERSONNALISÉ
# ===================================
def load_custom_css():
    """Charge le CSS personnalisé pour une interface moderne"""
    st.markdown("""
    <style>
    /* Variables */
    :root {
        --primary-color: #2d4d36;
        --secondary-color: #5e7a6a;
        --accent-color: #4caf50;
        --background: #f6f8f7;
        --card-bg: #ffffff;
        --error-color: #f8d7da;
        --success-color: #d4edda;
    }

    /* Header personnalisé */
    .main-header {
        padding: 1rem 0;
        border-bottom: 2px solid var(--accent-color);
        margin-bottom: 2rem;
    }

    .main-header h1 {
        color: var(--primary-color);
        font-weight: 700;
        margin: 0;
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

    /* Boutons AI */
    .ai-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-weight: 600;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .status-success {
        background: var(--success-color);
        color: #155724;
    }

    .status-warning {
        background: #fff3cd;
        color: #856404;
    }

    .status-error {
        background: var(--error-color);
        color: #721c24;
    }

    /* Animation de chargement IA */
    .ai-thinking {
        display: inline-block;
        animation: pulse 1.5s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: var(--background);
    }

    /* Cache le menu hamburger en production */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Nouveaux styles pour les messages d'erreur/succès */
    .alert {
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        border-radius: 0.25rem;
    }

    .alert-success {
        color: #155724;
        background-color: var(--success-color);
        border-color: #c3e6cb;
    }

    .alert-error {
        color: #721c24;
        background-color: var(--error-color);
        border-color: #f5c6cb;
    }

    /* Style pour les onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.25rem;
        border-radius: 6px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# ===================================
# INITIALISATION ROBUSTE
# ===================================
def init_app():
    """Initialise l'application au démarrage avec gestion des erreurs"""
    try:
        # Vérifier la connexion DB
        if not check_connection():
            st.error("❌ Impossible de se connecter à la base de données")
            st.write("Vérifie que :")
            st.write("- Les secrets sont bien configurés dans Streamlit Cloud")
            st.write("- Le projet Supabase est accessible")
            st.write("- Le mot de passe est correct")
            st.stop()

        # Afficher les infos de connexion dans la sidebar
        db_info = get_db_info()
        if db_info["status"] == "connected":
            st.sidebar.markdown("### 🔌 Base de données")
            st.sidebar.markdown(f"""
            <div class="status-badge status-success">
                ✅ Connecté à {db_info['host']}
            </div>
            <small>Utilisateur: {db_info['user']}</small>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div class="status-badge status-error">
                ❌ Erreur: {db_info['error']}
            </div>
            """, unsafe_allow_html=True)

        # Créer les tables si nécessaire (dev uniquement)
        if settings.ENV == "development":
            try:
                from src.core.database import create_all_tables
                create_all_tables()
                st.sidebar.success("✅ Tables vérifiées/créées")
            except Exception as e:
                logger.error(f"Erreur création tables: {e}")
                st.sidebar.warning(f"⚠️ Erreur tables: {str(e)[:50]}...")

        # Initialiser l'agent IA dans la session
        if "agent_ia" not in st.session_state:
            try:
                st.session_state.agent_ia = AgentIA()
                logger.info("🤖 Agent IA initialisé")
                st.sidebar.markdown("""
                <div class="status-badge status-success">
                    🤖 IA Prête
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.sidebar.error(f"❌ Erreur IA: {str(e)[:50]}...")
                logger.exception("Erreur initialisation IA")

        # Initialiser l'état de navigation
        if "current_module" not in st.session_state:
            st.session_state.current_module = "accueil"

        # Historique de chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

    except Exception as e:
        st.error(f"❌ Erreur d'initialisation: {str(e)}")
        logger.exception("Erreur init_app")
        st.stop()

# Initialiser l'app
init_app()

# ===================================
# HEADER AMÉLIORÉ
# ===================================
def render_header():
    """Affiche l'en-tête de l'application avec infos supplémentaires"""
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"""
            <div class="main-header">
                <h1>🤖 {settings.APP_NAME}</h1>
                <p style="color: var(--secondary-color); margin: 0;">
                    Assistant intelligent pour le quotidien familial
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # Status IA amélioré
        if "agent_ia" in st.session_state:
            st.markdown("""
            <div class="status-badge status-success">
                🤖 IA Active
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge status-warning">
                🤖 IA Indisponible
            </div>
            """, unsafe_allow_html=True)

    with col3:
        # Infos environnement et DB
        if settings.DEBUG:
            st.caption(f"🔧 {settings.ENV.upper()}")
            db_info = get_db_info()
            if db_info["status"] == "connected":
                st.caption(f"✅ DB: {db_info['database']}")

# ===================================
# SIDEBAR AMÉLIORÉE
# ===================================
def render_sidebar():
    """Affiche la sidebar avec navigation et infos supplémentaires"""
    with st.sidebar:
        st.title("Navigation")

        # Modules principaux avec icônes améliorées
        modules = {
            "🏠 Accueil": "accueil",
            "🍳 Cuisine": {
                "📚 Recettes": "cuisine.recettes",
                "🥫 Inventaire": "cuisine.inventaire",
                "👨‍🍳 Batch Cooking": "cuisine.batch_cooking",
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

        # Afficher les modules avec expanders
        for label, value in modules.items():
            if isinstance(value, dict):
                with st.expander(label, expanded=(label == "🍳 Cuisine")):
                    for sub_label, sub_value in value.items():
                        if st.button(
                                sub_label,
                                key=f"btn_{sub_value}",
                                use_container_width=True,
                                help=f"Accéder à {sub_label}"
                        ):
                            st.session_state.current_module = sub_value
                            st.rerun()
            else:
                if st.button(
                        label,
                        key=f"btn_{value}",
                        use_container_width=True,
                        help=f"Accéder à {label}"
                ):
                    st.session_state.current_module = value
                    st.rerun()

        # Séparateur et stats
        st.markdown("---")
        st.subheader("📊 Aperçu rapide")

        # Stats avec cards modernes
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("""
            <div class="metric-card">
                <h4>Recettes</h4>
                <p style="font-size: 1.5rem; margin: 0;">42</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="metric-card">
                <h4>Projets</h4>
                <p style="font-size: 1.5rem; margin: 0;">5</p>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown("""
            <div class="metric-card">
                <h4>Stock bas</h4>
                <p style="font-size: 1.5rem; margin: 0;">3</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="metric-card">
                <h4>Tâches</h4>
                <p style="font-size: 1.5rem; margin: 0;">12</p>
            </div>
            """, unsafe_allow_html=True)

        # Bouton urgences IA amélioré
        st.markdown("---")
        if st.button(
                "⚡ Actions urgentes IA",
                key="urgences_ia",
                use_container_width=True,
                help="Demander à l'IA de gérer les urgences"
        ):
            st.session_state.current_module = "urgences_ia"
            st.rerun()

# ===================================
# ROUTAGE DES MODULES AVEC GESTION D'ERREURS
# ===================================
def load_module(module_name: str):
    """Charge et affiche le module demandé avec gestion des erreurs"""
    try:
        # Mapping des modules
        module_map = {
            "accueil": "src.modules.accueil",
            "cuisine.recettes": "src.modules.cuisine.recettes",
            "cuisine.inventaire": "src.modules.cuisine.inventaire",
            "cuisine.batch_cooking": "src.modules.cuisine.batch_cooking",
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
            "urgences_ia": "src.modules.urgences_ia",
        }

        if module_name not in module_map:
            st.error(f"Module '{module_name}' non trouvé")
            return

        # Import dynamique avec gestion des erreurs
        try:
            import importlib
            module = importlib.import_module(module_map[module_name])

            # Appeler la fonction app() du module
            if hasattr(module, "app"):
                module.app()
            else:
                st.error(f"Le module {module_name} n'a pas de fonction app()")

        except ImportError as e:
            st.error(f"Impossible de charger le module: {e}")
            st.info("Module en cours de développement...")
            st.markdown(f"## 🚧 Module {module_name}")
            st.info("Ce module sera bientôt disponible !")

        except Exception as e:
            st.error(f"Erreur dans le module: {e}")
            if settings.DEBUG:
                st.exception(e)

    except Exception as e:
        st.error(f"Erreur inattendue: {e}")
        logger.exception("Erreur dans load_module")

# ===================================
# FOOTER AMÉLIORÉ
# ===================================
def render_footer():
    """Affiche le footer avec infos supplémentaires"""
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])

    with footer_col1:
        st.caption(f"💚 {settings.APP_NAME} v{settings.APP_VERSION}")
        st.caption("Assistant familial intelligent propulsé par IA")

    with footer_col2:
        if st.button("🐛 Reporter un bug", key="report_bug"):
            st.info("Ouvrir une issue sur GitHub")

    with footer_col3:
        if st.button("ℹ️ À propos", key="about"):
            st.info("""
            **Assistant MaTanne v2**
            Développé avec ❤️ pour réduire la charge mentale familiale.
            """)

# ===================================
# PAGE PRINCIPALE AVEC GESTION DES ERREURS
# ===================================
def main():
    """Fonction principale de l'application avec gestion des erreurs"""
    try:
        # Affichage du header et sidebar
        render_header()
        render_sidebar()

        # Chargement du module actuel
        current = st.session_state.current_module
        load_module(current)

        # Affichage du footer
        render_footer()

    except Exception as e:
        st.error(f"❌ Erreur critique dans l'application: {str(e)}")
        logger.exception("Erreur dans main()")
        if settings.DEBUG:
            st.exception(e)

# ===================================
# POINT D'ENTRÉE
# ===================================
if __name__ == "__main__":
    main()

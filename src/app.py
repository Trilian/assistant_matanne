"""
Application principale - VERSION OPTIMISÉE LAZY LOADING
✅ FIX: Import OptimizedRouter au lieu de AppRouter
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
    result = load_dotenv(env_file, override=True)  # Force override!
    mistral_key = _os.getenv("MISTRAL_API_KEY")
    print(f"Loaded environment from {env_file}")
    print(f"   load_dotenv() returned: {result}")
    print(f"   MISTRAL_API_KEY after load_dotenv: {mistral_key[:10] if mistral_key else 'MISSING'}...")
else:
    # Fallback: try current directory
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

from src.core import Cache, GestionnaireEtat, obtenir_etat, obtenir_parametres, verifier_connexion

# ✅ FIX: Import OptimizedRouter au lieu de l'ancien AppRouter
from src.core.lazy_loader import OptimizedRouter, render_lazy_loading_stats
from src.ui import badge

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


# ═══════════════════════════════════════════════════════════
# CSS MODERNE
# ═══════════════════════════════════════════════════════════

st.markdown(
    """
<style>
:root {
    --primary: #2d4d36;
    --secondary: #5e7a6a;
    --accent: #4caf50;
}

.main-header {
    padding: 1rem 0;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    transition: transform 0.2s;
}

.metric-card:hover {
    transform: translateY(-2px);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════


def initialiser_app() -> bool:
    """Initialise l'application"""
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

    logger.info("✅ App initialisée (lazy mode)")
    return True


# Initialiser
if not initialiser_app():
    st.stop()


# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════


def afficher_header():
    """Header avec badges"""
    etat = obtenir_etat()

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(
            f"<div class='main-header'>"
            f"<h1>🤖 {parametres.APP_NAME}</h1>"
            f"<p style='color: var(--secondary); margin: 0;'>"
            f"Assistant familial intelligent"
            f"</p></div>",
            unsafe_allow_html=True,
        )

    with col2:
        if etat.agent_ia:
            badge("🤖 IA Active", "#4CAF50")
        else:
            badge("🤖 IA Indispo", "#FFC107")

    with col3:
        if etat.notifications_non_lues > 0:
            if st.button(f"🔔 {etat.notifications_non_lues}"):
                st.session_state.show_notifications = True


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════


def afficher_sidebar():
    """Sidebar avec navigation"""
    etat = obtenir_etat()

    with st.sidebar:
        st.title("Navigation")

        # Fil d'Ariane
        fil_ariane = GestionnaireEtat.obtenir_fil_ariane_navigation()
        if len(fil_ariane) > 1:
            st.caption(" → ".join(fil_ariane[-3:]))
            if st.button("⬅️ Retour"):
                GestionnaireEtat.revenir()
                st.rerun()
            st.markdown("---")

        # ═══════════════════════════════════════════════════════
        # MODULES - ORGANISÉS PAR WORKFLOW FAMILIAL
        # ═══════════════════════════════════════════════════════

        MODULES_MENU = {
            "🏠 Accueil": "accueil",
            
            # Calendrier unifié - VUE CENTRALE
            "📅 Calendrier Familial": "planning.calendrier_unifie",
            
            # Cuisine - Workflow: Plan → Batch → Courses
            "🍳 Cuisine": {
                "🍽️ Planifier Repas": "cuisine.planificateur_repas",  # Nouveau: Jow-like
                "🍳 Batch Cooking": "cuisine.batch_cooking_detaille",  # Nouveau: Instructions détaillées
                "🛒 Courses": "cuisine.courses",
                "───────────": None,  # Séparateur
                "📚 Recettes": "cuisine.recettes",
                "🥫 Inventaire": "cuisine.inventaire",
                "📊 Planning (ancien)": "cuisine.planning_semaine",  # Ancien planning
            },
            
            # Famille - NOUVEAU HUB
            "👨‍👩‍👧‍👦 Famille": {
                "🏠 Hub Famille": "famille.hub",  # Nouveau hub avec cards
                "👶 Jules": "famille.jules_nouveau",
                "💪 Mon Suivi": "famille.suivi_perso",
                "🎉 Weekend": "famille.weekend",
                "🛍️ Achats": "famille.achats_famille",
            },
            
            # Maison
            "🏠 Maison": {
                "📋 Projets": "maison.projets",
                "🌱 Jardin": "maison.jardin",
                "🧹 Entretien": "maison.entretien",
            },
            
            # Planning (ancien - à migrer vers calendrier unifié)
            "📅 Planning (ancien)": {
                "🗓️ Calendrier": "planning.calendrier",
                "🌐 Vue Ensemble": "planning.vue_ensemble",
            },
            
            # Jeux
            "🎲 Jeux": {
                "⚽ Paris Sportifs": "jeux.paris",
                "🎰 Loto": "jeux.loto",
            },
            
            # Outils & Config
            "🔧 Outils": {
                "📱 Code-barres": "barcode",
                "📊 Rapports": "rapports",
            },
            "⚙️ Paramètres": "parametres",
        }

        for label, value in MODULES_MENU.items():
            if isinstance(value, dict):
                # Module avec sous-menus
                est_actif = any(
                    etat.module_actuel.startswith(sub) 
                    for sub in value.values() 
                    if sub  # Skip None values
                )

                with st.expander(label, expanded=est_actif):
                    for sub_label, sub_value in value.items():
                        # Skip séparateurs
                        if sub_value is None:
                            st.divider()
                            continue

                        est_sous_menu_actif = etat.module_actuel == sub_value

                        if st.button(
                            sub_label,
                            key=f"btn_{sub_value}",
                            use_container_width=True,
                            type="primary" if est_sous_menu_actif else "secondary",
                            disabled=est_sous_menu_actif,
                        ):
                            GestionnaireEtat.naviguer_vers(sub_value)
                            st.rerun()
            else:
                # Module simple
                est_actif = etat.module_actuel == value

                if st.button(
                    label,
                    key=f"btn_{value}",
                    use_container_width=True,
                    type="primary" if est_actif else "secondary",
                    disabled=est_actif,
                ):
                    GestionnaireEtat.naviguer_vers(value)
                    st.rerun()

        st.markdown("---")

        # ✅ Stats Lazy Loading
        render_lazy_loading_stats()

        st.markdown("---")

        # Debug
        etat.mode_debug = st.checkbox("🐛 Debug", value=etat.mode_debug)

        if etat.mode_debug:
            with st.expander("État App"):
                st.json(GestionnaireEtat.obtenir_resume_etat())

                if st.button("🔄 Reset"):
                    GestionnaireEtat.reinitialiser()
                    Cache.vider()
                    # ✅ Vider cache lazy loader
                    from src.core.lazy_loader import LazyModuleLoader

                    LazyModuleLoader.clear_cache()
                    st.success("Reset OK")
                    st.rerun()


# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════


def afficher_footer():
    """Footer simplifié"""
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.caption(f"💚 {parametres.APP_NAME} v{parametres.APP_VERSION} | Lazy Loading Active")

    with col2:
        if st.button("🐛 Bug"):
            st.info("GitHub Issues")

    with col3:
        if st.button("ℹ️ À propos"):
            with st.expander("À propos", expanded=True):
                st.markdown(
                    f"""
                ### {parametres.APP_NAME}
                **Version:** {parametres.APP_VERSION}
                
                **Stack:**
                - Frontend: Streamlit
                - Database: Supabase PostgreSQL
                - IA: Mistral AI
                - ⚡ Lazy Loading: Active
                """
                )


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════


def main():
    """Fonction principale"""
    try:
        # ✅ AUTHENTIFICATION DÉSACTIVÉE POUR LE MOMENT
        
        # Header
        afficher_header()

        # Sidebar
        afficher_sidebar()

        # ✅ FIX: Utiliser OptimizedRouter au lieu de AppRouter
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

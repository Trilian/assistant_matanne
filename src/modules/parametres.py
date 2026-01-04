"""
Module Paramètres - Configuration Application
Gestion configuration foyer, IA, base de données, cache
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Optional

# Core
from src.core.config import get_settings
from src.core.database import (
    get_db_info,
    health_check,
    MigrationManager,
    vacuum_database
)
from src.core.cache import Cache
from src.core.ai.semantic_cache import SemanticCache

# State
from src.core.state import get_state, StateManager

# UI
from src.ui.feedback import show_success, show_error, smart_spinner
from src.ui.components import Modal


# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module paramètres"""

    st.title("⚙️ Paramètres")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👨‍👩‍👧‍👦 Foyer",
        "🤖 IA",
        "💾 Base de Données",
        "🗄️ Cache",
        "ℹ️ À Propos"
    ])

    with tab1:
        render_foyer_config()

    with tab2:
        render_ia_config()

    with tab3:
        render_database_config()

    with tab4:
        render_cache_config()

    with tab5:
        render_about()


# ═══════════════════════════════════════════════════════════
# TAB 1: CONFIGURATION FOYER
# ═══════════════════════════════════════════════════════════

def render_foyer_config():
    """Configuration du foyer"""

    st.markdown("### 👨‍👩‍👧‍👦 Configuration Foyer")
    st.caption("Configure les informations de ton foyer")

    # État actuel
    state = get_state()

    # Récupérer config existante
    config = st.session_state.get("foyer_config", {
        "nom_utilisateur": state.user_name,
        "nb_adultes": 2,
        "nb_enfants": 1,
        "age_enfants": [2],
        "a_bebe": True,
        "preferences_alimentaires": []
    })

    # Formulaire
    with st.form("foyer_form"):
        st.markdown("#### Composition du Foyer")

        col1, col2 = st.columns(2)

        with col1:
            nom_utilisateur = st.text_input(
                "Nom d'utilisateur",
                value=config.get("nom_utilisateur", "Anne"),
                max_chars=50
            )

            nb_adultes = st.number_input(
                "Nombre d'adultes",
                min_value=1,
                max_value=10,
                value=config.get("nb_adultes", 2)
            )

        with col2:
            nb_enfants = st.number_input(
                "Nombre d'enfants",
                min_value=0,
                max_value=10,
                value=config.get("nb_enfants", 1)
            )

            a_bebe = st.checkbox(
                "👶 Présence d'un bébé (< 18 mois)",
                value=config.get("a_bebe", False)
            )

        st.markdown("#### Préférences Alimentaires")

        preferences = st.multiselect(
            "Régimes / Restrictions",
            [
                "Végétarien",
                "Végétalien",
                "Sans gluten",
                "Sans lactose",
                "Halal",
                "Casher",
                "Paléo",
                "Sans porc"
            ],
            default=config.get("preferences_alimentaires", [])
        )

        allergies = st.text_area(
            "Allergies alimentaires",
            value=config.get("allergies", ""),
            placeholder="Ex: Arachides, fruits de mer...",
            help="Liste des allergies à prendre en compte"
        )

        st.markdown("---")

        submitted = st.form_submit_button(
            "💾 Sauvegarder",
            type="primary",
            use_container_width=True
        )

        if submitted:
            # Sauvegarder config
            new_config = {
                "nom_utilisateur": nom_utilisateur,
                "nb_adultes": nb_adultes,
                "nb_enfants": nb_enfants,
                "a_bebe": a_bebe,
                "preferences_alimentaires": preferences,
                "allergies": allergies,
                "updated_at": datetime.now().isoformat()
            }

            st.session_state.foyer_config = new_config

            # Mettre à jour state
            state.user_name = nom_utilisateur

            show_success("✅ Configuration sauvegardée !")
            st.rerun()

    # Afficher config actuelle
    with st.expander("📋 Configuration Actuelle"):
        st.json(config)


# ═══════════════════════════════════════════════════════════
# TAB 2: CONFIGURATION IA
# ═══════════════════════════════════════════════════════════

def render_ia_config():
    """Configuration IA"""

    st.markdown("### 🤖 Configuration IA")
    st.caption("Paramètres du service d'intelligence artificielle")

    settings = get_settings()

    # Infos modèle
    st.markdown("#### Modèle Actuel")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Modèle:** {settings.MISTRAL_MODEL}")
        st.info(f"**Provider:** Mistral AI")

    with col2:
        st.info(f"**Température:** 0.7 (défaut)")
        st.info(f"**Max Tokens:** 1000 (défaut)")

    st.markdown("---")

    # Rate Limiting
    st.markdown("#### ⏳ Rate Limiting")

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            "Limite Quotidienne",
            f"{settings.RATE_LIMIT_DAILY} appels/jour"
        )

    with col4:
        st.metric(
            "Limite Horaire",
            f"{settings.RATE_LIMIT_HOURLY} appels/heure"
        )

    # Utilisation actuelle
    state = get_state()

    if "rate_limit" in st.session_state:
        rate_info = st.session_state.rate_limit

        st.markdown("**Utilisation Actuelle:**")

        col5, col6 = st.columns(2)

        with col5:
            calls_today = rate_info.get("calls_today", 0)
            progress_day = calls_today / settings.RATE_LIMIT_DAILY

            st.progress(progress_day)
            st.caption(f"{calls_today}/{settings.RATE_LIMIT_DAILY} appels aujourd'hui")

        with col6:
            calls_hour = rate_info.get("calls_hour", 0)
            progress_hour = calls_hour / settings.RATE_LIMIT_HOURLY

            st.progress(progress_hour)
            st.caption(f"{calls_hour}/{settings.RATE_LIMIT_HOURLY} appels cette heure")

    st.markdown("---")

    # Cache Sémantique
    st.markdown("#### 🧠 Cache Sémantique")

    cache_stats = SemanticCache.get_stats()

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Taux de Hit",
            f"{cache_stats['hit_rate']:.1f}%",
            help="Pourcentage de réponses servies depuis le cache"
        )

    with col8:
        st.metric(
            "Entrées Cachées",
            cache_stats['total_entries']
        )

    with col9:
        st.metric(
            "Appels Économisés",
            cache_stats['saved_api_calls']
        )

    mode = "🧠 Sémantique" if cache_stats['embeddings_available'] else "🔤 MD5"
    st.info(f"**Mode:** {mode}")

    if cache_stats['embeddings_available']:
        st.success("✅ Embeddings actifs (similarité sémantique)")
    else:
        st.warning("⚠️ Embeddings indisponibles (fallback MD5)")

    # Actions cache IA
    col10, col11 = st.columns(2)

    with col10:
        if st.button("🗑️ Vider Cache IA", use_container_width=True):
            SemanticCache.clear()
            show_success("Cache IA vidé !")
            st.rerun()

    with col11:
        if st.button("📊 Détails Cache", use_container_width=True):
            with st.expander("📊 Statistiques Détaillées", expanded=True):
                st.json(cache_stats)


# ═══════════════════════════════════════════════════════════
# TAB 3: BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════

def render_database_config():
    """Configuration base de données"""

    st.markdown("### 💾 Base de Données")
    st.caption("Informations et maintenance de la base de données")

    # Infos DB
    db_info = get_db_info()

    if db_info.get("status") == "connected":
        st.success("✅ Connexion active")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Host:** {db_info.get('host', '—')}")
            st.info(f"**Database:** {db_info.get('database', '—')}")
            st.info(f"**User:** {db_info.get('user', '—')}")

        with col2:
            st.info(f"**Version:** {db_info.get('version', '—')}")
            st.info(f"**Taille:** {db_info.get('size', '—')}")
            st.info(f"**Schéma:** v{db_info.get('schema_version', 0)}")

    else:
        st.error(f"❌ Erreur: {db_info.get('error', 'Inconnue')}")

    st.markdown("---")

    # Health Check
    st.markdown("#### 🏥 Health Check")

    if st.button("🔍 Vérifier l'état", use_container_width=True):
        with smart_spinner("Vérification en cours...", estimated_seconds=2):
            health = health_check()

        if health.get("healthy"):
            st.success("✅ Base de données en bonne santé")

            col3, col4 = st.columns(2)

            with col3:
                st.metric(
                    "Connexions Actives",
                    health.get("active_connections", 0)
                )

            with col4:
                db_size_mb = health.get("database_size_bytes", 0) / 1024 / 1024
                st.metric(
                    "Taille DB",
                    f"{db_size_mb:.2f} MB"
                )
        else:
            st.error(f"❌ Problème détecté: {health.get('error')}")

    st.markdown("---")

    # Migrations
    st.markdown("#### 🔄 Migrations")

    current_version = MigrationManager.get_current_version()
    st.info(f"**Version du schéma:** v{current_version}")

    col5, col6 = st.columns(2)

    with col5:
        if st.button("🔄 Exécuter Migrations", use_container_width=True):
            with smart_spinner("Exécution des migrations...", estimated_seconds=5):
                try:
                    MigrationManager.run_migrations()
                    show_success("✅ Migrations exécutées !")
                    st.rerun()
                except Exception as e:
                    show_error(f"❌ Erreur: {str(e)}")

    with col6:
        if st.button("ℹ️ Voir Historique", use_container_width=True):
            st.session_state.show_migrations_history = True

    st.markdown("---")

    # Maintenance
    st.markdown("#### 🧹 Maintenance")

    st.warning("⚠️ Ces opérations peuvent être longues")

    col7, col8 = st.columns(2)

    with col7:
        if st.button("🧹 Optimiser (VACUUM)", use_container_width=True):
            modal = Modal("vacuum_db")

            if not modal.is_showing():
                modal.show()
            else:
                st.warning("Cela peut prendre plusieurs minutes. Continuer ?")

                if modal.confirm("✅ Optimiser"):
                    with smart_spinner("Optimisation en cours...", estimated_seconds=10):
                        try:
                            vacuum_database()
                            show_success("✅ Optimisation terminée !")
                            modal.close()
                        except Exception as e:
                            show_error(f"❌ Erreur: {str(e)}")

                modal.cancel("❌ Annuler")

    with col8:
        if st.button("💾 Backup (TODO)", use_container_width=True):
            st.info("Fonctionnalité à implémenter")


# ═══════════════════════════════════════════════════════════
# TAB 4: CACHE
# ═══════════════════════════════════════════════════════════

def render_cache_config():
    """Configuration cache"""

    st.markdown("### 🗄️ Gestion du Cache")
    st.caption("Cache applicatif et cache IA")

    # Cache applicatif
    st.markdown("#### 📦 Cache Applicatif")

    if "cache_data" in st.session_state:
        cache_size = len(st.session_state.cache_data)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Entrées", cache_size)

        with col2:
            if "cache_stats" in st.session_state:
                stats = st.session_state.cache_stats
                total = stats.get("hits", 0) + stats.get("misses", 0)
                hit_rate = (stats.get("hits", 0) / total * 100) if total > 0 else 0

                st.metric("Taux de Hit", f"{hit_rate:.1f}%")

        if st.button("🗑️ Vider Cache Applicatif", use_container_width=True):
            Cache.clear_all()
            show_success("Cache applicatif vidé !")
            st.rerun()

    else:
        st.info("Cache vide")

    st.markdown("---")

    # Cache IA
    st.markdown("#### 🤖 Cache IA")

    cache_stats = SemanticCache.get_stats()

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Entrées", cache_stats['total_entries'])

    with col4:
        st.metric("Hits", cache_stats['hits'])

    with col5:
        st.metric("Misses", cache_stats['misses'])

    if st.button("🗑️ Vider Cache IA", use_container_width=True):
        SemanticCache.clear()
        show_success("Cache IA vidé !")
        st.rerun()

    st.markdown("---")

    # Actions groupées
    st.markdown("#### 🧹 Actions Groupées")

    if st.button(
            "🗑️ TOUT Vider (Cache App + IA)",
            type="primary",
            use_container_width=True
    ):
        Cache.clear_all()
        SemanticCache.clear()
        show_success("✅ Tous les caches vidés !")
        st.rerun()


# ═══════════════════════════════════════════════════════════
# TAB 5: À PROPOS
# ═══════════════════════════════════════════════════════════

def render_about():
    """Informations sur l'application"""

    settings = get_settings()

    st.markdown("### ℹ️ À Propos")

    # Infos app
    st.markdown(f"""
    ## 🤖 {settings.APP_NAME}
    
    **Version:** {settings.APP_VERSION}
    
    **Description:**  
    Assistant familial intelligent pour gérer :
    - 🍽️ Recettes et planning repas
    - 📦 Inventaire alimentaire
    - 🛒 Liste de courses
    - 📅 Planning hebdomadaire
    
    **Technologies:**
    - Frontend: Streamlit
    - Backend: Python
    - Database: PostgreSQL (Supabase)
    - IA: Mistral AI
    """)

    st.markdown("---")

    # Environnement
    st.markdown("#### 🔧 Environnement")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Mode:** {settings.ENV}")
        st.info(f"**Debug:** {'Activé' if settings.DEBUG else 'Désactivé'}")

    with col2:
        db_configured = "✅ Configurée" if settings._check_db_configured() else "❌ Non configurée"
        ai_configured = "✅ Configurée" if settings._check_mistral_configured() else "❌ Non configurée"

        st.info(f"**Base de données:** {db_configured}")
        st.info(f"**IA:** {ai_configured}")

    st.markdown("---")

    # Configuration sécurisée (sans secrets)
    st.markdown("#### ⚙️ Configuration")

    with st.expander("Voir la configuration (sans secrets)"):
        safe_config = settings.get_safe_config()
        st.json(safe_config)

    st.markdown("---")

    # Support
    st.markdown("#### 💬 Support")

    st.info("""
    **Besoin d'aide ?**
    - 📧 Contact: support@example.com
    - 🐛 Bugs: GitHub Issues
    - 📚 Documentation: /docs
    """)

    st.markdown("---")

    # État système
    st.markdown("#### 🖥️ État Système")

    state_summary = StateManager.get_state_summary()

    with st.expander("État de l'application"):
        st.json(state_summary)
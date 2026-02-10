"""
Module Paramètres - Configuration Application
Gestion configuration foyer, IA, base de données, cache
"""

from datetime import datetime

import streamlit as st

from src.core.ai.cache import CacheIA as SemanticCache
from src.core.cache import Cache

# Core
from src.core.config import obtenir_parametres as get_settings
from src.core.database import GestionnaireMigrations as MigrationManager
from src.core.database import obtenir_infos_db as get_db_info
from src.core.database import verifier_sante as health_check

# State
from src.core.state import StateManager, get_state
from src.ui.components import Modal

# Logique métier pure
from src.domains.utils.logic.parametres_logic import (
    valider_parametres,
    generer_config_defaut,
    verifier_sante_config
)

# UI
from src.ui.feedback import show_error, show_success, smart_spinner

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODULE PRINCIPAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def app():
    """Point d'entrée module paramètres"""

    st.title("⚙️ Paramètres")

    # Tabs - Ajout des nouvelles fonctionnalités
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["👶📉⚫📷 Foyer", "– IA", "👧 Base de Données", "💡 Cache", "🔔 Affichage", "🟢 Budget", "ℹ️ À Propos"]
    )

    with tab1:
        render_foyer_config()

    with tab2:
        render_ia_config()

    with tab3:
        render_database_config()

    with tab4:
        render_cache_config()

    with tab5:
        render_display_config()

    with tab6:
        render_budget_config()

    with tab7:
        render_about()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 1: CONFIGURATION FOYER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_foyer_config():
    """Configuration du foyer"""

    st.markdown("### 👶 📊 📺 📸 Configuration Foyer")
    st.caption("Configure les informations de ton foyer")

    # État actuel
    state = get_state()

    # Récupérer config existante
    config = st.session_state.get(
        "foyer_config",
        {
            "nom_utilisateur": state.nom_utilisateur,
            "nb_adultes": 2,
            "nb_enfants": 1,
            "age_enfants": [2],
            "a_bebe": True,
            "preferences_alimentaires": [],
        },
    )

    # Formulaire
    with st.form("foyer_form"):
        st.markdown("#### Composition du Foyer")

        col1, col2 = st.columns(2)

        with col1:
            nom_utilisateur = st.text_input(
                "Nom d'utilisateur", value=config.get("nom_utilisateur", "Anne"), max_chars=50
            )

            nb_adultes = st.number_input(
                "Nombre d'adultes", min_value=1, max_value=10, value=config.get("nb_adultes", 2)
            )

        with col2:
            nb_enfants = st.number_input(
                "Nombre d'enfants", min_value=0, max_value=10, value=config.get("nb_enfants", 1)
            )

            a_bebe = st.checkbox(
                "👶 Présence d'un jeune enfant (< 24 mois)", value=config.get("a_bebe", False)
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
                "Sans porc",
            ],
            default=config.get("preferences_alimentaires", []),
        )

        allergies = st.text_area(
            "Allergies alimentaires",
            value=config.get("allergies", ""),
            placeholder="Ex: Arachides, fruits de mer...",
            help="Liste des allergies à prendre en compte",
        )

        st.markdown("---")

        submitted = st.form_submit_button(
            "👧 Sauvegarder", type="primary", use_container_width=True
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
                "updated_at": datetime.now().isoformat(),
            }

            st.session_state.foyer_config = new_config

            # Mettre à jour state
            state.nom_utilisateur = nom_utilisateur

            show_success("✅ Configuration sauvegardée !")
            st.rerun()

    # Afficher config actuelle
    with st.expander("📥 Configuration Actuelle"):
        st.json(config)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 2: CONFIGURATION IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_ia_config():
    """Configuration IA"""

    st.markdown("### – Configuration IA")
    st.caption("Paramètres du service d'intelligence artificielle")

    settings = get_settings()

    # Infos modèle
    st.markdown("#### Modèle Actuel")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Modèle:** {settings.MISTRAL_MODEL}")
        st.info("**Provider:** Mistral AI")

    with col2:
        st.info("**Température:** 0.7 (défaut)")
        st.info("**Max Tokens:** 1000 (défaut)")

    st.markdown("---")

    # Rate Limiting
    st.markdown("#### ⏳ Rate Limiting")

    col3, col4 = st.columns(2)

    with col3:
        st.metric("Limite Quotidienne", f"{settings.RATE_LIMIT_DAILY} appels/jour")

    with col4:
        st.metric("Limite Horaire", f"{settings.RATE_LIMIT_HOURLY} appels/heure")

    # Utilisation actuelle
    _state = get_state()

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
    st.markdown("#### 🎯 Cache Sémantique")

    cache_stats = SemanticCache.obtenir_statistiques()

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Taux de Hit",
            f"{cache_stats.get('taux_hit', 0):.1f}%",
            help="Pourcentage de réponses servies depuis le cache",
        )

    with col8:
        st.metric("Entrées Cachées", cache_stats.get("entrees_ia", 0))

    with col9:
        st.metric("Appels Économisés", cache_stats.get("saved_api_calls", 0))

    mode = "🎯 Sémantique" if cache_stats.get("embeddings_available", False) else "📤 MD5"
    st.info(f"**Mode:** {mode}")
    if cache_stats.get("embeddings_available", False):
        st.success("✅ Embeddings actifs (similarité sémantique)")
    else:
        st.warning("âš ï¸ Embeddings indisponibles (fallback MD5)")

    # Actions cache IA
    col10, col11 = st.columns(2)

    with col10:
        if st.button("📋 Vider Cache IA", key="btn_clear_semantic_cache", use_container_width=True):
            SemanticCache.invalider_tout()
            show_success("Cache IA vidé !")
            st.rerun()

    with col11:
        if st.button("📊 Détails Cache", key="btn_cache_details", use_container_width=True):
            with st.expander("📊 Statistiques Détaillées", expanded=True):
                st.json(cache_stats)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 3: BASE DE DONNÉES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_database_config():
    """Configuration base de données"""

    st.markdown("### 👧 Base de Données")
    st.caption("Informations et maintenance de la base de données")

    # Infos DB
    db_info = get_db_info()

    if db_info.get("statut") == "connected":
        st.success("✅ Connexion active")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Host:** {db_info.get('hote', 'â€”')}")
            st.info(f"**Database:** {db_info.get('base_donnees', 'â€”')}")
            st.info(f"**User:** {db_info.get('utilisateur', 'â€”')}")

        with col2:
            st.info(f"**Version:** {db_info.get('version', 'â€”')}")
            st.info(f"**Taille:** {db_info.get('taille', 'â€”')}")
            st.info(f"**Schéma:** v{db_info.get('version_schema', 0)}")

    else:
        st.error(f"❌ Erreur: {db_info.get('erreur', 'Inconnue')}")

    st.markdown("---")

    # Health Check
    st.markdown("#### 📅 Health Check")

    if st.button("📍Vérifier l'état", key="btn_check_db_status", use_container_width=True):
        with smart_spinner("Vérification en cours...", estimated_seconds=2):
            health = health_check()

        if health.get("sain"):
            st.success("✅ Base de données en bonne santé")

            col3, col4 = st.columns(2)

            with col3:
                st.metric("Connexions Actives", health.get("connexions_actives", 0))

            with col4:
                db_size_mb = health.get("taille_base_octets", 0) / 1024 / 1024
                st.metric("Taille DB", f"{db_size_mb:.2f} MB")
        else:
            st.error(f"❌ Problème détecté: {health.get('erreur')}")

    st.markdown("---")

    # Migrations
    st.markdown("#### 🔄 Migrations")

    current_version = MigrationManager.obtenir_version_courante()
    st.info(f"**Version du schéma:** v{current_version}")

    col5, col6 = st.columns(2)

    with col5:
        if st.button("🔄 Exécuter Migrations", key="btn_run_migrations", use_container_width=True):
            with smart_spinner("Exécution des migrations...", estimated_seconds=5):
                try:
                    MigrationManager.executer_migrations()
                    show_success("✅ Migrations exécutées !")
                    st.rerun()
                except Exception as e:
                    show_error(f"❌ Erreur: {str(e)}")

    with col6:
        if st.button("ℹ️ Voir Historique", key="btn_show_migration_history", use_container_width=True):
            st.session_state.show_migrations_history = True

    st.markdown("---")

    # Maintenance
    st.markdown("#### 🧹 Maintenance")

    st.warning("âš ï¸ Ces opérations peuvent être longues")

    col7, col8 = st.columns(2)

    with col7:
        if st.button("🧹 Optimiser (VACUUM)", key="btn_optimize_db", use_container_width=True):
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
        if st.button("👧 Backup (TODO)", key="btn_backup_db", use_container_width=True):
            st.info("Fonctionnalité à implémenter")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 4: CACHE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_cache_config():
    """Configuration cache"""

    st.markdown("### 💡¸ Gestion du Cache")
    st.caption("Cache applicatif et cache IA")

    # Cache applicatif
    st.markdown("#### [PKG] Cache Applicatif")

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

            if st.button("🗑️ Vider Cache Applicatif", key="btn_clear_cache_app", use_container_width=True):
                Cache.clear_all()
                show_success("Cache applicatif vidé !")
                st.rerun()

    else:
        st.info("Cache vide")

    st.markdown("---")

    # Cache IA
    st.markdown("#### 🤖 Cache IA")

    cache_stats = SemanticCache.obtenir_statistiques()

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Entrées", cache_stats.get("entrees_ia", 0))

    with col4:
        st.metric("Hits", cache_stats.get("entrees_ia", 0))

    with col5:
        st.metric("Misses", 0)

    if st.button("📋 Vider Cache IA", key="btn_clear_cache_ia", use_container_width=True):
        SemanticCache.invalider_tout()
        show_success("Cache IA vidé !")
        st.rerun()

    st.markdown("---")

    # Actions groupées
    st.markdown("#### 🧹 Actions Groupées")

    if st.button("📋¸ TOUT Vider (Cache App + IA)", key="btn_clear_all", type="primary", use_container_width=True):
        Cache.clear_all()
        SemanticCache.invalider_tout()
        show_success("✅ Tous les caches vidés !")
        st.rerun()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 5: À PROPOS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_about():
    """Informations sur l'application"""

    settings = get_settings()

    st.markdown("### ℹ️ À Propos")

    # Infos app
    st.markdown(
        f"""
    ## – {settings.APP_NAME}
    
    **Version:** {settings.APP_VERSION}
    
    **Description:**  
    Assistant familial intelligent pour gérer :
    - 💰 Recettes et planning repas
    - [PKG] Inventaire alimentaire
    - 🍽️ Liste de courses
    - 🧹 Planning hebdomadaire
    
    **Technologies:**
    - Frontend: Streamlit
    - Backend: Python
    - Database: PostgreSQL (Supabase)
    - IA: Mistral AI
    """
    )

    st.markdown("---")

    # Environnement
    st.markdown("#### 🚀 Environnement")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Mode:** {settings.ENV}")
        st.info(f"**Debug:** {'Activé' if settings.DEBUG else 'Désactivé'}")

    with col2:
        db_configured = (
            "✅ Configurée" if settings._verifier_db_configuree() else "❌ Non configurée"
        )
        ai_configured = (
            "✅ Configurée" if settings._verifier_mistral_configure() else "❌ Non configurée"
        )

        st.info(f"**Base de données:** {db_configured}")
        st.info(f"**IA:** {ai_configured}")

    st.markdown("---")

    # Configuration sécurisée (sans secrets)
    st.markdown("#### ⚙️ Configuration")

    with st.expander("Voir la configuration (sans secrets)"):
        safe_config = settings.obtenir_config_publique()
        st.json(safe_config)

    st.markdown("---")

    # Support
    st.markdown("#### 📋 Support")

    st.info(
        """
    **Besoin d'aide ?**
    - [WATER] Contact: support@example.com
    - 🍽️ Bugs: GitHub Issues
    - 🤖 Documentation: /docs
    """
    )

    st.markdown("---")

    # État système
    st.markdown("#### 🟡¸ État Système")

    state_summary = StateManager.get_state_summary()

    with st.expander("État de l'application"):
        st.json(state_summary)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 5: CONFIGURATION AFFICHAGE (Mode Tablette)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_display_config():
    """Configuration de l'affichage et mode tablette."""
    
    st.markdown("### 🔔 Configuration Affichage")
    st.caption("Personnalise l'interface selon ton appareil")
    
    try:
        from src.ui.tablet_mode import (
            TabletMode, get_tablet_mode, set_tablet_mode, render_mode_selector
        )
        
        current_mode = get_tablet_mode()
        
        st.markdown("#### Mode d'affichage")
        
        mode_options = {
            TabletMode.NORMAL: ("🟡¸ Normal", "Interface standard pour ordinateur"),
            TabletMode.TABLET: ("🔔 Tablette", "Boutons plus grands, interface tactile"),
            TabletMode.KITCHEN: ("👶€💰 Cuisine", "Mode cuisine avec navigation par étapes"),
        }
        
        for mode, (label, description) in mode_options.items():
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(
                    label, 
                    key=f"mode_{mode.value}",
                    type="primary" if current_mode == mode else "secondary",
                    use_container_width=True
                ):
                    set_tablet_mode(mode)
                    show_success(f"Mode {label} activé !")
                    st.rerun()
            with col2:
                st.caption(description)
        
        st.markdown("---")
        
        st.markdown("#### Prévisualisation")
        
        if current_mode == TabletMode.NORMAL:
            st.info("🟡¸ Mode normal actif - Interface optimisée pour ordinateur")
        elif current_mode == TabletMode.TABLET:
            st.warning("🔔 Mode tablette actif - Boutons et textes agrandis")
        else:
            st.success("👶€💰 Mode cuisine actif - Interface simplifiée pour cuisiner")
        
    except ImportError:
        st.error("Module tablet_mode non disponible")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 6: CONFIGURATION BUDGET
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_budget_config():
    """Configuration du budget et backup."""
    
    st.markdown("### 🟢 Budget & Sauvegarde")
    
    # Section Budget
    st.markdown("#### 📤 Configuration Budget")
    
    try:
        from src.services.budget import CategorieDepense
        
        st.markdown("**Catégories de dépenses disponibles:**")
        
        cols = st.columns(3)
        categories = list(CategorieDepense)
        
        for i, cat in enumerate(categories):
            with cols[i % 3]:
                emoji_map = {
                    "alimentation": "�️",
                    "transport": "🚗",
                    "logement": "🏠",
                    "sante": "⚕️",
                    "loisirs": "🎮",
                    "vetements": "👕",
                    "education": "📚",
                    "cadeaux": "🎁",
                    "abonnements": "📦",
                    "restaurant": "🍴",
                    "vacances": "✈️",
                    "bebe": "👶",
                    "autre": "📋",
                }
                emoji = emoji_map.get(cat.value, "[PKG]")
                st.checkbox(f"{emoji} {cat.value.capitalize()}", value=True, disabled=True)
        
        st.info("🗑️ Accède au module Budget dans le menu Famille pour gérer tes dépenses")
        
    except ImportError:
        st.warning("Module budget non disponible")
    
    st.markdown("---")
    
    # Section Backup
    st.markdown("#### 👧 Sauvegarde des données")
    
    try:
        from src.services.backup import get_backup_service, render_backup_ui
        
        backup_service = get_backup_service()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔔 Créer une sauvegarde", type="primary", use_container_width=True):
                with smart_spinner("Sauvegarde en cours..."):
                    result = backup_service.create_backup()
                    if result.success:
                        show_success(f"✅ {result.message}")
                    else:
                        show_error(f"❌ {result.message}")
        
        with col2:
            if st.button("📥 Voir les sauvegardes", use_container_width=True):
                backups = backup_service.list_backups()
                if backups:
                    for b in backups[:5]:
                        st.text(f"📷 {b.filename} ({b.size_bytes // 1024} KB)")
                else:
                    st.info("Aucune sauvegarde trouvée")
        
    except ImportError:
        st.warning("Module backup non disponible")
    
    st.markdown("---")
    
    # Section Météo
    st.markdown("#### 🗑️¸ Configuration Météo Jardin")
    
    try:
        from src.services.weather import get_weather_garden_service
        
        weather = get_weather_garden_service()
        
        with st.form("meteo_config"):
            ville = st.text_input("Ville", value="Paris")
            surface = st.number_input("Surface jardin (m²)", min_value=1, max_value=1000, value=50)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                notif_gel = st.checkbox("Alertes gel", value=True)
            with col2:
                notif_canicule = st.checkbox("Alertes canicule", value=True)
            with col3:
                notif_pluie = st.checkbox("Alertes pluie", value=True)
            
            if st.form_submit_button("👧 Sauvegarder", use_container_width=True):
                if weather.set_location_from_city(ville):
                    st.session_state.meteo_config = {
                        "ville": ville,
                        "surface": surface,
                        "notif_gel": notif_gel,
                        "notif_canicule": notif_canicule,
                        "notif_pluie": notif_pluie,
                    }
                    show_success("✅ Configuration météo sauvegardée")
                else:
                    show_error("Ville non trouvée")
                    
    except ImportError:
        st.warning("Module météo non disponible")

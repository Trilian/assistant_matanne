"""
Module ParamÃ¨tres - Configuration Application
Gestion configuration foyer, IA, base de donnÃ©es, cache
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

# Logique mÃ©tier pure
from src.domains.shared.logic.parametres_logic import (
    valider_parametres,
    generer_config_defaut,
    verifier_sante_config
)

# UI
from src.ui.feedback import show_error, show_success, smart_spinner

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODULE PRINCIPAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def app():
    """Point d'entrÃ©e module paramÃ¨tres"""

    st.title("âš™ï¸ ParamÃ¨tres")

    # Tabs - Ajout des nouvelles fonctionnalitÃ©s
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["ðŸ‘¨â€ðŸ‘©â€ðŸ‘§â€ðŸ‘¦ Foyer", "ðŸ¤– IA", "ðŸ’¾ Base de DonnÃ©es", "ðŸ—„ï¸ Cache", "ðŸ“± Affichage", "ðŸ’° Budget", "â„¹ï¸ Ã€ Propos"]
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 1: CONFIGURATION FOYER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_foyer_config():
    """Configuration du foyer"""

    st.markdown("### ðŸ‘¨â€ðŸ‘©â€ðŸ‘§â€ðŸ‘¦ Configuration Foyer")
    st.caption("Configure les informations de ton foyer")

    # Ã‰tat actuel
    state = get_state()

    # RÃ©cupÃ©rer config existante
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
                "ðŸ‘¶ PrÃ©sence d'un jeune enfant (< 24 mois)", value=config.get("a_bebe", False)
            )

        st.markdown("#### PrÃ©fÃ©rences Alimentaires")

        preferences = st.multiselect(
            "RÃ©gimes / Restrictions",
            [
                "VÃ©gÃ©tarien",
                "VÃ©gÃ©talien",
                "Sans gluten",
                "Sans lactose",
                "Halal",
                "Casher",
                "PalÃ©o",
                "Sans porc",
            ],
            default=config.get("preferences_alimentaires", []),
        )

        allergies = st.text_area(
            "Allergies alimentaires",
            value=config.get("allergies", ""),
            placeholder="Ex: Arachides, fruits de mer...",
            help="Liste des allergies Ã  prendre en compte",
        )

        st.markdown("---")

        submitted = st.form_submit_button(
            "ðŸ’¾ Sauvegarder", type="primary", use_container_width=True
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

            # Mettre Ã  jour state
            state.nom_utilisateur = nom_utilisateur

            show_success("âœ… Configuration sauvegardÃ©e !")
            st.rerun()

    # Afficher config actuelle
    with st.expander("ðŸ“‹ Configuration Actuelle"):
        st.json(config)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 2: CONFIGURATION IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_ia_config():
    """Configuration IA"""

    st.markdown("### ðŸ¤– Configuration IA")
    st.caption("ParamÃ¨tres du service d'intelligence artificielle")

    settings = get_settings()

    # Infos modÃ¨le
    st.markdown("#### ModÃ¨le Actuel")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**ModÃ¨le:** {settings.MISTRAL_MODEL}")
        st.info("**Provider:** Mistral AI")

    with col2:
        st.info("**TempÃ©rature:** 0.7 (dÃ©faut)")
        st.info("**Max Tokens:** 1000 (dÃ©faut)")

    st.markdown("---")

    # Rate Limiting
    st.markdown("#### â³ Rate Limiting")

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

    # Cache SÃ©mantique
    st.markdown("#### ðŸ§  Cache SÃ©mantique")

    cache_stats = SemanticCache.obtenir_statistiques()

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Taux de Hit",
            f"{cache_stats.get('taux_hit', 0):.1f}%",
            help="Pourcentage de rÃ©ponses servies depuis le cache",
        )

    with col8:
        st.metric("EntrÃ©es CachÃ©es", cache_stats.get("entrees_ia", 0))

    with col9:
        st.metric("Appels Ã‰conomisÃ©s", cache_stats.get("saved_api_calls", 0))

    mode = "ðŸ§  SÃ©mantique" if cache_stats.get("embeddings_available", False) else "ðŸ”¤ MD5"
    st.info(f"**Mode:** {mode}")
    if cache_stats.get("embeddings_available", False):
        st.success("âœ… Embeddings actifs (similaritÃ© sÃ©mantique)")
    else:
        st.warning("âš ï¸ Embeddings indisponibles (fallback MD5)")

    # Actions cache IA
    col10, col11 = st.columns(2)

    with col10:
        if st.button("ðŸ—‘ï¸ Vider Cache IA", key="btn_clear_semantic_cache", use_container_width=True):
            SemanticCache.invalider_tout()
            show_success("Cache IA vidÃ© !")
            st.rerun()

    with col11:
        if st.button("ðŸ“Š DÃ©tails Cache", key="btn_cache_details", use_container_width=True):
            with st.expander("ðŸ“Š Statistiques DÃ©taillÃ©es", expanded=True):
                st.json(cache_stats)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 3: BASE DE DONNÃ‰ES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_database_config():
    """Configuration base de donnÃ©es"""

    st.markdown("### ðŸ’¾ Base de DonnÃ©es")
    st.caption("Informations et maintenance de la base de donnÃ©es")

    # Infos DB
    db_info = get_db_info()

    if db_info.get("statut") == "connected":
        st.success("âœ… Connexion active")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Host:** {db_info.get('hote', 'â€”')}")
            st.info(f"**Database:** {db_info.get('base_donnees', 'â€”')}")
            st.info(f"**User:** {db_info.get('utilisateur', 'â€”')}")

        with col2:
            st.info(f"**Version:** {db_info.get('version', 'â€”')}")
            st.info(f"**Taille:** {db_info.get('taille', 'â€”')}")
            st.info(f"**SchÃ©ma:** v{db_info.get('version_schema', 0)}")

    else:
        st.error(f"âŒ Erreur: {db_info.get('erreur', 'Inconnue')}")

    st.markdown("---")

    # Health Check
    st.markdown("#### ðŸ¥ Health Check")

    if st.button("ðŸ” VÃ©rifier l'Ã©tat", key="btn_check_db_status", use_container_width=True):
        with smart_spinner("VÃ©rification en cours...", estimated_seconds=2):
            health = health_check()

        if health.get("sain"):
            st.success("âœ… Base de donnÃ©es en bonne santÃ©")

            col3, col4 = st.columns(2)

            with col3:
                st.metric("Connexions Actives", health.get("connexions_actives", 0))

            with col4:
                db_size_mb = health.get("taille_base_octets", 0) / 1024 / 1024
                st.metric("Taille DB", f"{db_size_mb:.2f} MB")
        else:
            st.error(f"âŒ ProblÃ¨me dÃ©tectÃ©: {health.get('erreur')}")

    st.markdown("---")

    # Migrations
    st.markdown("#### ðŸ”„ Migrations")

    current_version = MigrationManager.obtenir_version_courante()
    st.info(f"**Version du schÃ©ma:** v{current_version}")

    col5, col6 = st.columns(2)

    with col5:
        if st.button("ðŸ”„ ExÃ©cuter Migrations", key="btn_run_migrations", use_container_width=True):
            with smart_spinner("ExÃ©cution des migrations...", estimated_seconds=5):
                try:
                    MigrationManager.executer_migrations()
                    show_success("âœ… Migrations exÃ©cutÃ©es !")
                    st.rerun()
                except Exception as e:
                    show_error(f"âŒ Erreur: {str(e)}")

    with col6:
        if st.button("â„¹ï¸ Voir Historique", key="btn_show_migration_history", use_container_width=True):
            st.session_state.show_migrations_history = True

    st.markdown("---")

    # Maintenance
    st.markdown("#### ðŸ§¹ Maintenance")

    st.warning("âš ï¸ Ces opÃ©rations peuvent Ãªtre longues")

    col7, col8 = st.columns(2)

    with col7:
        if st.button("ðŸ§¹ Optimiser (VACUUM)", key="btn_optimize_db", use_container_width=True):
            modal = Modal("vacuum_db")

            if not modal.is_showing():
                modal.show()
            else:
                st.warning("Cela peut prendre plusieurs minutes. Continuer ?")

                if modal.confirm("âœ… Optimiser"):
                    with smart_spinner("Optimisation en cours...", estimated_seconds=10):
                        try:
                            vacuum_database()
                            show_success("âœ… Optimisation terminÃ©e !")
                            modal.close()
                        except Exception as e:
                            show_error(f"âŒ Erreur: {str(e)}")

                modal.cancel("âŒ Annuler")

    with col8:
        if st.button("ðŸ’¾ Backup (TODO)", key="btn_backup_db", use_container_width=True):
            st.info("FonctionnalitÃ© Ã  implÃ©menter")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 4: CACHE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_cache_config():
    """Configuration cache"""

    st.markdown("### ðŸ—„ï¸ Gestion du Cache")
    st.caption("Cache applicatif et cache IA")

    # Cache applicatif
    st.markdown("#### ðŸ“¦ Cache Applicatif")

    if "cache_data" in st.session_state:
        cache_size = len(st.session_state.cache_data)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("EntrÃ©es", cache_size)

        with col2:
            if "cache_stats" in st.session_state:
                stats = st.session_state.cache_stats
                total = stats.get("hits", 0) + stats.get("misses", 0)
                hit_rate = (stats.get("hits", 0) / total * 100) if total > 0 else 0

                st.metric("Taux de Hit", f"{hit_rate:.1f}%")

        if st.button("ðŸ—‘ï¸ Vider Cache Applicatif", key="btn_clear_cache_app", use_container_width=True):
            Cache.clear_all()
            show_success("Cache applicatif vidÃ© !")
            st.rerun()

    else:
        st.info("Cache vide")

    st.markdown("---")

    # Cache IA
    st.markdown("#### ðŸ¤– Cache IA")

    cache_stats = SemanticCache.obtenir_statistiques()

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("EntrÃ©es", cache_stats.get("entrees_ia", 0))

    with col4:
        st.metric("Hits", cache_stats.get("entrees_ia", 0))

    with col5:
        st.metric("Misses", 0)

    if st.button("ðŸ—‘ï¸ Vider Cache IA", key="btn_clear_cache_ia", use_container_width=True):
        SemanticCache.invalider_tout()
        show_success("Cache IA vidÃ© !")
        st.rerun()

    st.markdown("---")

    # Actions groupÃ©es
    st.markdown("#### ðŸ§¹ Actions GroupÃ©es")

    if st.button("ðŸ—‘ï¸ TOUT Vider (Cache App + IA)", key="btn_clear_all", type="primary", use_container_width=True):
        Cache.clear_all()
        SemanticCache.invalider_tout()
        show_success("âœ… Tous les caches vidÃ©s !")
        st.rerun()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 5: Ã€ PROPOS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_about():
    """Informations sur l'application"""

    settings = get_settings()

    st.markdown("### â„¹ï¸ Ã€ Propos")

    # Infos app
    st.markdown(
        f"""
    ## ðŸ¤– {settings.APP_NAME}
    
    **Version:** {settings.APP_VERSION}
    
    **Description:**  
    Assistant familial intelligent pour gÃ©rer :
    - ðŸ½ï¸ Recettes et planning repas
    - ðŸ“¦ Inventaire alimentaire
    - ðŸ›’ Liste de courses
    - ðŸ“… Planning hebdomadaire
    
    **Technologies:**
    - Frontend: Streamlit
    - Backend: Python
    - Database: PostgreSQL (Supabase)
    - IA: Mistral AI
    """
    )

    st.markdown("---")

    # Environnement
    st.markdown("#### ðŸ”§ Environnement")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Mode:** {settings.ENV}")
        st.info(f"**Debug:** {'ActivÃ©' if settings.DEBUG else 'DÃ©sactivÃ©'}")

    with col2:
        db_configured = (
            "âœ… ConfigurÃ©e" if settings._verifier_db_configuree() else "âŒ Non configurÃ©e"
        )
        ai_configured = (
            "âœ… ConfigurÃ©e" if settings._verifier_mistral_configure() else "âŒ Non configurÃ©e"
        )

        st.info(f"**Base de donnÃ©es:** {db_configured}")
        st.info(f"**IA:** {ai_configured}")

    st.markdown("---")

    # Configuration sÃ©curisÃ©e (sans secrets)
    st.markdown("#### âš™ï¸ Configuration")

    with st.expander("Voir la configuration (sans secrets)"):
        safe_config = settings.obtenir_config_publique()
        st.json(safe_config)

    st.markdown("---")

    # Support
    st.markdown("#### ðŸ’¬ Support")

    st.info(
        """
    **Besoin d'aide ?**
    - ðŸ“§ Contact: support@example.com
    - ðŸ› Bugs: GitHub Issues
    - ðŸ“š Documentation: /docs
    """
    )

    st.markdown("---")

    # Ã‰tat systÃ¨me
    st.markdown("#### ðŸ–¥ï¸ Ã‰tat SystÃ¨me")

    state_summary = StateManager.get_state_summary()

    with st.expander("Ã‰tat de l'application"):
        st.json(state_summary)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 5: CONFIGURATION AFFICHAGE (Mode Tablette)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_display_config():
    """Configuration de l'affichage et mode tablette."""
    
    st.markdown("### ðŸ“± Configuration Affichage")
    st.caption("Personnalise l'interface selon ton appareil")
    
    try:
        from src.ui.tablet_mode import (
            TabletMode, get_tablet_mode, set_tablet_mode, render_mode_selector
        )
        
        current_mode = get_tablet_mode()
        
        st.markdown("#### Mode d'affichage")
        
        mode_options = {
            TabletMode.NORMAL: ("ðŸ–¥ï¸ Normal", "Interface standard pour ordinateur"),
            TabletMode.TABLET: ("ðŸ“± Tablette", "Boutons plus grands, interface tactile"),
            TabletMode.KITCHEN: ("ðŸ‘¨â€ðŸ³ Cuisine", "Mode cuisine avec navigation par Ã©tapes"),
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
                    show_success(f"Mode {label} activÃ© !")
                    st.rerun()
            with col2:
                st.caption(description)
        
        st.markdown("---")
        
        st.markdown("#### PrÃ©visualisation")
        
        if current_mode == TabletMode.NORMAL:
            st.info("ðŸ–¥ï¸ Mode normal actif - Interface optimisÃ©e pour ordinateur")
        elif current_mode == TabletMode.TABLET:
            st.warning("ðŸ“± Mode tablette actif - Boutons et textes agrandis")
        else:
            st.success("ðŸ‘¨â€ðŸ³ Mode cuisine actif - Interface simplifiÃ©e pour cuisiner")
        
    except ImportError:
        st.error("Module tablet_mode non disponible")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 6: CONFIGURATION BUDGET
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_budget_config():
    """Configuration du budget et backup."""
    
    st.markdown("### ðŸ’° Budget & Sauvegarde")
    
    # Section Budget
    st.markdown("#### ðŸ’µ Configuration Budget")
    
    try:
        from src.services.budget import CategorieDepense
        
        st.markdown("**CatÃ©gories de dÃ©penses disponibles:**")
        
        cols = st.columns(3)
        categories = list(CategorieDepense)
        
        for i, cat in enumerate(categories):
            with cols[i % 3]:
                emoji_map = {
                    "alimentation": "ðŸŽ",
                    "transport": "ðŸš—",
                    "logement": "ðŸ ",
                    "sante": "ðŸ’Š",
                    "loisirs": "ðŸŽ®",
                    "vetements": "ðŸ‘•",
                    "education": "ðŸ“š",
                    "cadeaux": "ðŸŽ",
                    "abonnements": "ðŸ“º",
                    "restaurant": "ðŸ½ï¸",
                    "vacances": "âœˆï¸",
                    "bebe": "ðŸ‘¶",
                    "autre": "ðŸ“¦",
                }
                emoji = emoji_map.get(cat.value, "ðŸ“¦")
                st.checkbox(f"{emoji} {cat.value.capitalize()}", value=True, disabled=True)
        
        st.info("ðŸ’¡ AccÃ¨de au module Budget dans le menu Famille pour gÃ©rer tes dÃ©penses")
        
    except ImportError:
        st.warning("Module budget non disponible")
    
    st.markdown("---")
    
    # Section Backup
    st.markdown("#### ðŸ’¾ Sauvegarde des donnÃ©es")
    
    try:
        from src.services.backup import get_backup_service, render_backup_ui
        
        backup_service = get_backup_service()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("ðŸ“¥ CrÃ©er une sauvegarde", type="primary", use_container_width=True):
                with smart_spinner("Sauvegarde en cours..."):
                    result = backup_service.create_backup()
                    if result.success:
                        show_success(f"âœ… {result.message}")
                    else:
                        show_error(f"âŒ {result.message}")
        
        with col2:
            if st.button("ðŸ“‹ Voir les sauvegardes", use_container_width=True):
                backups = backup_service.list_backups()
                if backups:
                    for b in backups[:5]:
                        st.text(f"ðŸ“„ {b.filename} ({b.size_bytes // 1024} KB)")
                else:
                    st.info("Aucune sauvegarde trouvÃ©e")
        
    except ImportError:
        st.warning("Module backup non disponible")
    
    st.markdown("---")
    
    # Section MÃ©tÃ©o
    st.markdown("#### ðŸŒ¤ï¸ Configuration MÃ©tÃ©o Jardin")
    
    try:
        from src.services.weather import get_weather_garden_service
        
        weather = get_weather_garden_service()
        
        with st.form("meteo_config"):
            ville = st.text_input("Ville", value="Paris")
            surface = st.number_input("Surface jardin (mÂ²)", min_value=1, max_value=1000, value=50)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                notif_gel = st.checkbox("Alertes gel", value=True)
            with col2:
                notif_canicule = st.checkbox("Alertes canicule", value=True)
            with col3:
                notif_pluie = st.checkbox("Alertes pluie", value=True)
            
            if st.form_submit_button("ðŸ’¾ Sauvegarder", use_container_width=True):
                if weather.set_location_from_city(ville):
                    st.session_state.meteo_config = {
                        "ville": ville,
                        "surface": surface,
                        "notif_gel": notif_gel,
                        "notif_canicule": notif_canicule,
                        "notif_pluie": notif_pluie,
                    }
                    show_success("âœ… Configuration mÃ©tÃ©o sauvegardÃ©e")
                else:
                    show_error("Ville non trouvÃ©e")
                    
    except ImportError:
        st.warning("Module mÃ©tÃ©o non disponible")

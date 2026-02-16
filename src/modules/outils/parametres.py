"""
Module Paramètres - Configuration Application
Gestion configuration foyer, IA, base de donnees, cache
"""

from datetime import datetime

import streamlit as st

from src.core.ai.cache import CacheIA as SemanticCache
from src.core.cache import Cache

# Core
from src.core.config import obtenir_parametres as get_settings
from src.core.database import GestionnaireMigrations as GestionnaireMigrations
from src.core.database import obtenir_infos_db as get_db_info
from src.core.database import vacuum_database
from src.core.database import verifier_sante as health_check

# State
from src.core.state import GestionnaireEtat, obtenir_etat

# Logique metier pure
from src.ui.components import Modale as Modal

# UI
from src.ui.feedback import afficher_erreur, afficher_succes, spinner_intelligent

# -----------------------------------------------------------
# MODULE PRINCIPAL
# -----------------------------------------------------------


def app():
    """Point d'entree module paramètres"""

    st.title("⚙️ Paramètres")

    # Noms des onglets
    tab_names = [
        "👨‍👩‍👧‍👦 Foyer",
        "🤖 IA",
        "🗄️ Base de Données",
        "💾 Cache",
        "🖥️ Affichage",
        "💰 Budget",
        "ℹ️ À Propos",
    ]

    # Sélecteur d'onglet persistant
    if "parametres_tab" not in st.session_state:
        st.session_state.parametres_tab = tab_names[0]

    # Navigation par selectbox (persiste entre reruns)
    selected_tab = st.selectbox(
        "Section",
        tab_names,
        index=tab_names.index(st.session_state.parametres_tab),
        label_visibility="collapsed",
    )
    st.session_state.parametres_tab = selected_tab

    st.markdown("---")

    # Afficher le contenu selon l'onglet sélectionné
    if selected_tab == tab_names[0]:
        render_foyer_config()
    elif selected_tab == tab_names[1]:
        render_ia_config()
    elif selected_tab == tab_names[2]:
        render_database_config()
    elif selected_tab == tab_names[3]:
        render_cache_config()
    elif selected_tab == tab_names[4]:
        render_display_config()
    elif selected_tab == tab_names[5]:
        render_budget_config()
    elif selected_tab == tab_names[6]:
        render_about()


# -----------------------------------------------------------
# TAB 1: CONFIGURATION FOYER
# -----------------------------------------------------------


def render_foyer_config():
    """Configuration du foyer"""

    st.markdown("### 👨‍👩‍👧‍👦 Configuration Foyer")
    st.caption("Configure les informations de ton foyer")

    # État actuel
    state = obtenir_etat()

    # Recuperer config existante
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

        st.markdown("#### Preferences Alimentaires")

        preferences = st.multiselect(
            "Regimes / Restrictions",
            [
                "Vegetarien",
                "Vegetalien",
                "Sans gluten",
                "Sans lactose",
                "Halal",
                "Casher",
                "Paleo",
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
            "💾 Sauvegarder", type="primary", use_container_width=True
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

            afficher_succes("✅ Configuration sauvegardée !")
            st.rerun()

    # Afficher config actuelle
    with st.expander("📋 Configuration actuelle"):
        st.json(config)


# -----------------------------------------------------------
# TAB 2: CONFIGURATION IA
# -----------------------------------------------------------


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
        st.info("**Provider:** Mistral AI")

    with col2:
        st.info("**Temperature:** 0.7 (defaut)")
        st.info("**Max Tokens:** 1000 (defaut)")

    st.markdown("---")

    # Rate Limiting
    st.markdown("#### ⚡ Rate Limiting")

    col3, col4 = st.columns(2)

    with col3:
        st.metric("Limite Quotidienne", f"{settings.RATE_LIMIT_DAILY} appels/jour")

    with col4:
        st.metric("Limite Horaire", f"{settings.RATE_LIMIT_HOURLY} appels/heure")

    # Utilisation actuelle
    _state = obtenir_etat()

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

    # Cache Semantique
    st.markdown("#### 🧠 Cache Sémantique")

    cache_stats = SemanticCache.obtenir_statistiques()

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Taux de Hit",
            f"{cache_stats.get('taux_hit', 0):.1f}%",
            help="Pourcentage de reponses servies depuis le cache",
        )

    with col8:
        st.metric("Entrees Cachees", cache_stats.get("entrees_ia", 0))

    with col9:
        st.metric("Appels Économises", cache_stats.get("saved_api_calls", 0))

    mode = "🔑 Hachage MD5"
    st.info(f"**Mode:** {mode} (correspondance exacte des prompts)")

    # Actions cache IA
    col10, col11 = st.columns(2)

    with col10:
        if st.button("🗑️ Vider Cache IA", key="btn_clear_semantic_cache", use_container_width=True):
            SemanticCache.invalider_tout()
            afficher_succes("Cache IA vidé !")

    with col11:
        if st.button("📊 Détails Cache", key="btn_cache_details", use_container_width=True):
            with st.expander("📈 Statistiques Détaillées", expanded=True):
                st.json(cache_stats)


# -----------------------------------------------------------
# TAB 3: BASE DE DONNÉES
# -----------------------------------------------------------


def render_database_config():
    """Configuration base de donnees"""

    st.markdown("### 🗄️ Base de Données")
    st.caption("Informations et maintenance de la base de données")

    # Infos DB
    db_info = get_db_info()

    if db_info.get("statut") == "connected":
        st.success("✅ Connexion active")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Host:** {db_info.get('hote', '—')}")
            st.info(f"**Database:** {db_info.get('base_donnees', '—')}")
            st.info(f"**User:** {db_info.get('utilisateur', '—')}")

        with col2:
            st.info(f"**Version:** {db_info.get('version', '—')}")
            st.info(f"**Taille:** {db_info.get('taille', '—')}")
            st.info(f"**Schema:** v{db_info.get('version_schema', 0)}")

    else:
        st.error(f"❌ Erreur: {db_info.get('erreur', 'Inconnue')}")

    st.markdown("---")

    # Health Check
    st.markdown("#### 🟢 Health Check")

    if st.button("🔍 Vérifier l'état", key="btn_check_db_status", use_container_width=True):
        with spinner_intelligent("Verification en cours...", secondes_estimees=2):
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

    current_version = GestionnaireMigrations.obtenir_version_courante()
    st.info(f"**Version du schema:** v{current_version}")

    col5, col6 = st.columns(2)

    with col5:
        if st.button("▶️ Exécuter Migrations", key="btn_run_migrations", use_container_width=True):
            with spinner_intelligent("Execution des migrations...", secondes_estimees=5):
                try:
                    GestionnaireMigrations.executer_migrations()
                    afficher_succes("✅ Migrations exécutées !")
                    st.rerun()
                except Exception as e:
                    afficher_erreur(f"❌ Erreur: {str(e)}")

    with col6:
        if st.button(
            "📜 Voir Historique", key="btn_show_migration_history", use_container_width=True
        ):
            st.session_state.show_migrations_history = not st.session_state.get(
                "show_migrations_history", False
            )

    # Afficher l'historique si demandé
    if st.session_state.get("show_migrations_history", False):
        with st.expander("📜 Historique des Migrations", expanded=True):
            migrations_disponibles = GestionnaireMigrations.obtenir_migrations_disponibles()
            if migrations_disponibles:
                for m in migrations_disponibles:
                    status = "✅" if m["version"] <= current_version else "⏳"
                    st.markdown(f"{status} **v{m['version']}** - {m['name']}")
            else:
                st.info("Aucune migration définie")

    st.markdown("---")

    # Maintenance
    st.markdown("#### 🛠️ Maintenance")

    st.warning("⚠️ Ces opérations peuvent être longues")

    col7, col8 = st.columns(2)

    with col7:
        if st.button("🧹 Optimiser (VACUUM)", key="btn_optimize_db", use_container_width=True):
            modal = Modal("vacuum_db")

            if not modal.is_showing():
                modal.show()
            else:
                st.warning("Cela peut prendre plusieurs minutes. Continuer ?")

                if modal.confirm("✅ Optimiser"):
                    with spinner_intelligent("Optimisation en cours...", secondes_estimees=10):
                        try:
                            vacuum_database()
                            afficher_succes("✅ Optimisation terminée !")
                            modal.close()
                        except Exception as e:
                            afficher_erreur(f"❌ Erreur: {str(e)}")

                modal.cancel("❌ Annuler")

    with col8:
        if st.button("💾 Backup", key="btn_backup_db", use_container_width=True):
            try:
                from src.services.backup import get_backup_service

                backup_service = get_backup_service()
                with spinner_intelligent("Sauvegarde en cours..."):
                    result = backup_service.create_backup()
                    if result.success:
                        afficher_succes(f"✅ {result.message}")
                    else:
                        afficher_erreur(f"❌ {result.message}")
            except ImportError:
                st.warning("Module backup non disponible")


# -----------------------------------------------------------
# TAB 4: CACHE
# -----------------------------------------------------------


def render_cache_config():
    """Configuration cache"""

    st.markdown("### 💾 Gestion du Cache")
    st.caption("Cache applicatif et cache IA")

    # Cache applicatif
    st.markdown("#### 📦 Cache Applicatif")

    if "cache_data" in st.session_state:
        cache_size = len(st.session_state.cache_data)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Entrees", cache_size)

        with col2:
            if "cache_stats" in st.session_state:
                stats = st.session_state.cache_stats
                total = stats.get("hits", 0) + stats.get("misses", 0)
                hit_rate = (stats.get("hits", 0) / total * 100) if total > 0 else 0

                st.metric("Taux de Hit", f"{hit_rate:.1f}%")

            if st.button(
                "🗑️ Vider Cache Applicatif", key="btn_clear_cache_app", use_container_width=True
            ):
                Cache.clear()
                afficher_succes("Cache applicatif vidé !")

    else:
        st.info("Cache vide")

    st.markdown("---")

    # Cache IA
    st.markdown("#### 🤖 Cache IA")

    cache_stats = SemanticCache.obtenir_statistiques()

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Entrees", cache_stats.get("entrees_ia", 0))

    with col4:
        st.metric("Hits", cache_stats.get("entrees_ia", 0))

    with col5:
        st.metric("Misses", 0)

    if st.button("🗑️ Vider Cache IA", key="btn_clear_cache_ia", use_container_width=True):
        SemanticCache.invalider_tout()
        afficher_succes("Cache IA vidé !")

    st.markdown("---")

    # Actions groupees
    st.markdown("#### ⚡ Actions Groupées")

    if st.button(
        "🗑️ TOUT Vider (Cache App + IA)",
        key="btn_clear_all",
        type="primary",
        use_container_width=True,
    ):
        Cache.clear()
        SemanticCache.invalider_tout()
        afficher_succes("✅ Tous les caches vidés !")


# -----------------------------------------------------------
# TAB 5: À PROPOS
# -----------------------------------------------------------


def render_about():
    """Informations sur l'application"""

    settings = get_settings()

    # Header avec logo/titre
    col_logo, col_info = st.columns([1, 3])

    with col_logo:
        st.markdown("# 🏠")

    with col_info:
        st.markdown(f"## {settings.APP_NAME}")
        st.caption(f"Version {settings.APP_VERSION}")

    st.markdown("---")

    # Description
    st.markdown("#### 📋 Description")
    st.markdown("""
Assistant familial intelligent pour gérer le quotidien :
- 🍳 **Recettes** et planning des repas
- 📦 **Inventaire** alimentaire
- 🛒 **Listes** de courses
- 📅 **Planning** hebdomadaire
- 👶 **Suivi** de Jules
- 💪 **Santé** et bien-être
""")

    st.markdown("---")

    # Stack technique en colonnes
    st.markdown("#### 🛠️ Stack Technique")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Frontend", "Streamlit", delta=None)
    with col2:
        st.metric("Database", "Supabase", delta=None)
    with col3:
        st.metric("IA", "Mistral AI", delta=None)
    with col4:
        lazy_status = "✅ Actif" if True else "❌"
        st.metric("Lazy Loading", lazy_status, delta=None)

    st.markdown("---")

    # Environnement
    st.markdown("#### 💻 Environnement")

    col1, col2 = st.columns(2)

    with col1:
        env_color = "🟢" if settings.ENV == "production" else "🟡"
        st.markdown(f"{env_color} **Mode:** {settings.ENV}")
        debug_icon = "🔧" if settings.DEBUG else "🔒"
        st.markdown(f"{debug_icon} **Debug:** {'Activé' if settings.DEBUG else 'Désactivé'}")

    with col2:
        db_ok = settings._verifier_db_configuree()
        ai_ok = settings._verifier_mistral_configure()
        st.markdown(f"{'✅' if db_ok else '❌'} **Base de données**")
        st.markdown(f"{'✅' if ai_ok else '❌'} **IA Mistral**")

    st.markdown("---")

    # Configuration (collapsible)
    with st.expander("🔐 Configuration (sans secrets)"):
        safe_config = settings.obtenir_config_publique()
        st.json(safe_config)

    # État système (collapsible)
    state_summary = GestionnaireEtat.obtenir_resume_etat()

    with st.expander("⚙️ État Système"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Module:** {state_summary.get('module_actuel', '—')}")
            st.markdown(f"**Utilisateur:** {state_summary.get('nom_utilisateur', '—')}")
            st.markdown(f"**Cache:** {'✅' if state_summary.get('cache_active') else '❌'}")
        with col2:
            st.markdown(f"**IA:** {'✅' if state_summary.get('ia_disponible') else '❌'}")
            st.markdown(f"**Debug:** {'✅' if state_summary.get('mode_debug') else '❌'}")
            notifs = state_summary.get("notifications_non_lues", 0)
            st.markdown(f"**Notifications:** {notifs}")
            notifs = state_summary.get("notifications_non_lues", 0)
            st.markdown(f"**Notifications:** {notifs}")


# -----------------------------------------------------------
# TAB 5: CONFIGURATION AFFICHAGE (Mode Tablette)
# -----------------------------------------------------------


def render_display_config():
    """Configuration de l'affichage et mode tablette."""

    st.markdown("### 🖥️ Configuration Affichage")
    st.caption("Personnalise l'interface selon ton appareil")

    try:
        from src.ui.tablet_mode import (
            TabletMode,
            get_tablet_mode,
            set_tablet_mode,
        )

        current_mode = get_tablet_mode()

        st.markdown("#### Mode d'affichage")

        mode_options = {
            "💻 Normal": TabletMode.NORMAL,
            "📱 Tablette": TabletMode.TABLET,
            "🍳 Cuisine": TabletMode.KITCHEN,
        }

        mode_descriptions = {
            TabletMode.NORMAL: "Interface standard pour ordinateur",
            TabletMode.TABLET: "Boutons plus grands, interface tactile",
            TabletMode.KITCHEN: "Mode cuisine avec navigation par étapes",
        }

        # Trouver le label actuel
        current_label = next(
            (label for label, mode in mode_options.items() if mode == current_mode), "💻 Normal"
        )

        selected_label = st.radio(
            "Choisir le mode",
            options=list(mode_options.keys()),
            index=list(mode_options.keys()).index(current_label),
            horizontal=True,
            label_visibility="collapsed",
        )

        selected_mode = mode_options[selected_label]

        # Appliquer si changement
        if selected_mode != current_mode:
            set_tablet_mode(selected_mode)
            afficher_succes(f"Mode {selected_label} activé !")

        st.caption(mode_descriptions[selected_mode])

        st.markdown("---")

        st.markdown("#### Prévisualisation")

        if selected_mode == TabletMode.NORMAL:
            st.info("💻 Mode normal actif - Interface optimisée pour ordinateur")
        elif selected_mode == TabletMode.TABLET:
            st.warning("📱 Mode tablette actif - Boutons et textes agrandis")
        else:
            st.success("🍳 Mode cuisine actif - Interface simplifiée pour cuisiner")

    except ImportError:
        st.error("Module tablet_mode non disponible")


# -----------------------------------------------------------
# TAB 6: CONFIGURATION BUDGET
# -----------------------------------------------------------


def render_budget_config():
    """Configuration du budget."""

    st.markdown("### 💰 Budget")

    # Section Budget
    st.markdown("#### 📈 Catégories de dépenses")

    try:
        from src.services.budget import CategorieDepense

        # Mapping complet avec accents
        emoji_map = {
            "alimentation": "🍞",
            "courses": "🛒",
            "maison": "🏠",
            "santé": "🏥",
            "transport": "🚗",
            "loisirs": "🎮",
            "vêtements": "👕",
            "enfant": "👶",
            "éducation": "📚",
            "services": "🔧",
            "impôts": "📋",
            "épargne": "💰",
            "gaz": "🔥",
            "electricite": "⚡",
            "eau": "💧",
            "internet": "🌐",
            "loyer": "🏘️",
            "assurance": "🛡️",
            "taxe_fonciere": "🏛️",
            "creche": "🧒",
            "autre": "📦",
        }

        # Affichage en grille
        categories = list(CategorieDepense)
        cols = st.columns(4)
        for i, cat in enumerate(categories):
            with cols[i % 4]:
                emoji = emoji_map.get(cat.value, "📦")
                st.markdown(f"{emoji} {cat.value.replace('_', ' ').capitalize()}")

        st.info("👉 Accède au module **Budget** dans le menu Famille pour gérer tes dépenses")

    except ImportError:
        st.warning("Module budget non disponible")

    st.markdown("---")

    # Section Backup
    st.markdown("#### 💾 Sauvegarde des données")

    try:
        from src.services.backup import get_backup_service

        backup_service = get_backup_service()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Créer une sauvegarde", type="primary", use_container_width=True):
                with spinner_intelligent("Sauvegarde en cours..."):
                    result = backup_service.create_backup()
                    if result.success:
                        afficher_succes(f"✅ {result.message}")
                    else:
                        afficher_erreur(f"❌ {result.message}")

        with col2:
            if st.button("📂 Voir les sauvegardes", use_container_width=True):
                backups = backup_service.list_backups()
                if backups:
                    for b in backups[:5]:
                        st.text(f"📄 {b.filename} ({b.size_bytes // 1024} KB)")
                else:
                    st.info("Aucune sauvegarde trouvée")

    except ImportError:
        st.warning("Module backup non disponible")

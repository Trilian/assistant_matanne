"""
Paramètres - Configuration Base de Données
Gestion et maintenance de la base PostgreSQL/Supabase
"""

import streamlit as st

from src.core.db import GestionnaireMigrations, vacuum_database
from src.core.db import obtenir_infos_db as get_db_info
from src.core.db import verifier_sante as health_check
from src.ui.components import Modale as Modal
from src.ui.feedback import afficher_erreur, afficher_succes, spinner_intelligent


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
                from src.services.core.backup import get_backup_service

                backup_service = get_backup_service()
                with spinner_intelligent("Sauvegarde en cours..."):
                    result = backup_service.create_backup()
                    if result.success:
                        afficher_succes(f"✅ {result.message}")
                    else:
                        afficher_erreur(f"❌ {result.message}")
            except ImportError:
                st.warning("Module backup non disponible")

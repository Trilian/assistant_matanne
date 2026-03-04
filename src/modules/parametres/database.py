"""
Paramètres - Configuration Base de Données
Gestion et maintenance de la base PostgreSQL/Supabase
"""

import streamlit as st
from sqlalchemy import text

from src.core.db import GestionnaireMigrations, obtenir_moteur, vacuum_database
from src.core.db import obtenir_infos_db as get_db_info
from src.core.db import verifier_sante as health_check
from src.core.monitoring.health import StatutSante, verifier_sante_globale
from src.core.session_keys import SK
from src.core.state import rerun
from src.ui import etat_vide
from src.ui.feedback import afficher_erreur, afficher_succes, spinner_intelligent
from src.ui.fragments import lazy, ui_fragment


def _trouver_doublons_planning() -> list[dict]:
    """Trouve les semaines avec plusieurs plannings actifs."""
    engine = obtenir_moteur()
    doublons = []

    with engine.connect() as conn:
        # Périodes avec > 1 planning actif
        stmt = text("""
            SELECT semaine_debut, COUNT(*) as cnt
            FROM plannings
            WHERE actif = TRUE
            GROUP BY semaine_debut
            HAVING COUNT(*) > 1
            ORDER BY semaine_debut DESC
        """)
        result = conn.execute(stmt).fetchall()

        for row in result:
            doublons.append({"semaine_debut": row[0], "count": row[1]})

    return doublons


def _reparer_doublons_planning():
    """Désactive les plannings en doublon, en gardant le plus récent par ID."""
    engine = obtenir_moteur()

    with engine.connect() as conn:
        # Trouver les doublons
        stmt = text("""
            SELECT semaine_debut
            FROM plannings
            WHERE actif = TRUE
            GROUP BY semaine_debut
            HAVING COUNT(*) > 1
        """)
        semaines = conn.execute(stmt).fetchall()

        count_fixed = 0

        for (semaine_debut,) in semaines:
            # Récupérer tous les IDs actifs pour cette semaine, triés par ID desc (le plus récent en premier)
            ids_stmt = text("""
                SELECT id
                FROM plannings
                WHERE semaine_debut = :semaine_debut AND actif = TRUE
                ORDER BY id DESC
            """)
            ids = [
                row[0]
                for row in conn.execute(ids_stmt, {"semaine_debut": semaine_debut}).fetchall()
            ]

            if len(ids) > 1:
                # Garder le premier (le plus récent), désactiver les autres
                ids_to_deactivate = ids[1:]

                upd_stmt = text("""
                    UPDATE plannings
                    SET actif = FALSE
                    WHERE id = ANY(:ids)
                """)
                conn.execute(upd_stmt, {"ids": ids_to_deactivate})
                count_fixed += len(ids_to_deactivate)

        conn.commit()
        return count_fixed


@lazy(condition=lambda: st.session_state.get(SK.SHOW_MIGRATIONS_HISTORY, False), show_skeleton=True)
def _afficher_historique_migrations():
    """Historique des migrations SQL (chargé à la demande)."""
    with st.expander("📜 Historique des Migrations", expanded=True):
        appliquees = GestionnaireMigrations.obtenir_migrations_appliquees()
        disponibles = GestionnaireMigrations.obtenir_migrations_disponibles()

        if disponibles:
            for m in disponibles:
                v = m["version"]
                if v in appliquees:
                    date_app = appliquees[v].get("applied_at", "")
                    date_str = f" ({date_app:%Y-%m-%d})" if date_app else ""
                    st.markdown(f"✅ **v{v}** - {m['name']} (`{m['fichier']}`){date_str}")
                else:
                    st.markdown(f"⏳ **v{v}** - {m['name']} (`{m['fichier']}`) — en attente")

            modifiees = GestionnaireMigrations.verifier_checksums()
            if modifiees:
                st.warning(f"⚠️ {len(modifiees)} migration(s) modifiée(s) après application")
        else:
            etat_vide("Aucun fichier SQL dans sql/migrations/", "🗄️")


@st.dialog("🧹 Confirmer Optimisation")
def _dialog_vacuum():
    """Dialog natif pour confirmer l'optimisation VACUUM."""
    st.warning("⚠️ Cela peut prendre plusieurs minutes.")
    st.markdown(
        "L'optimisation **VACUUM** libère l'espace inutilisé et met à jour les statistiques."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Optimiser", type="primary", use_container_width=True, key="dlg_vacuum_ok"):
            with spinner_intelligent("Optimisation en cours...", secondes_estimees=10):
                try:
                    vacuum_database()
                    afficher_succes("✅ Optimisation terminée !")
                except Exception as e:
                    afficher_erreur(f"❌ Erreur: {str(e)}")
            rerun()
    with col2:
        if st.button("❌ Annuler", use_container_width=True, key="dlg_vacuum_cancel"):
            rerun()


@ui_fragment
def afficher_database_config():
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

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        if st.button("🔍 Vérifier DB", key="btn_check_db_status", use_container_width=True):
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

    with col_h2:
        if st.button(
            "🩺 Santé Globale Système",
            key="btn_check_system_health",
            use_container_width=True,
        ):
            with spinner_intelligent("Vérification globale...", secondes_estimees=5):
                rapport = verifier_sante_globale(inclure_db=True)

            if rapport.sain:
                st.success("✅ Tous les systèmes opérationnels")
            else:
                st.error("❌ Problème détecté sur un ou plusieurs composants")

            for nom, comp in rapport.composants.items():
                icone = {
                    StatutSante.SAIN: "✅",
                    StatutSante.DEGRADE: "⚠️",
                    StatutSante.CRITIQUE: "❌",
                    StatutSante.INCONNU: "❓",
                }.get(comp.statut, "❓")
                st.markdown(
                    f"{icone} **{nom.capitalize()}** — {comp.message} "
                    f"({comp.duree_verification_ms:.0f} ms)"
                )

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
                    rerun()
                except Exception as e:
                    afficher_erreur(f"❌ Erreur: {str(e)}")

    with col6:
        if st.button(
            "📜 Voir Historique", key="btn_show_migration_history", use_container_width=True
        ):
            st.session_state.show_migrations_history = not st.session_state.get(
                SK.SHOW_MIGRATIONS_HISTORY, False
            )

    # Afficher l'historique si demandé
    _afficher_historique_migrations()

    st.markdown("---")

    # Maintenance
    st.markdown("#### 🛠️ Maintenance")

    st.warning("⚠️ Ces opérations peuvent être longues")

    col7, col8 = st.columns(2)

    with col7:
        if st.button("🧹 Optimiser (VACUUM)", key="btn_optimize_db", use_container_width=True):
            _dialog_vacuum()

    with col8:
        if st.button("💾 Backup", key="btn_backup_db", use_container_width=True):
            try:
                from src.services.core.backup import obtenir_service_backup

                backup_service = obtenir_service_backup()
                with spinner_intelligent("Sauvegarde en cours..."):
                    result = backup_service.create_backup()
                    if result.success:
                        afficher_succes(f"✅ {result.message}")
                    else:
                        afficher_erreur(f"❌ {result.message}")
            except ImportError:
                st.warning("Module backup non disponible")

    st.markdown("---")

    # Nettoyage Planning
    st.markdown("#### 🗓️ Nettoyage Planning")
    st.caption("Détection et suppression des plannings actifs en doublon (garde le plus récent)")

    col_net_1, col_net_2 = st.columns([3, 1])

    with col_net_1:
        if st.button("🔍 Analyser les doublons", key="btn_check_duplicates"):
            with spinner_intelligent("Analyse en cours..."):
                st.session_state["_planning_doublons"] = _trouver_doublons_planning()

    if "_planning_doublons" in st.session_state:
        doublons = st.session_state["_planning_doublons"]
        if not doublons:
            st.success("✅ Aucun doublon détecté (Planning sain)")
        else:
            st.warning(f"⚠️ {len(doublons)} semaines ont plusieurs plannings actifs simultanés.")
            for item in doublons:
                st.write(f"- Semaine du {item['semaine_debut']}: {item['count']} plannings actifs")

            if st.button("🧹 Réparer (Garder le plus récent)", type="primary"):
                with spinner_intelligent("Réparation..."):
                    count = _reparer_doublons_planning()
                st.success(f"✅ {count} plannings obsolètes désactivés !")
                del st.session_state["_planning_doublons"]
                rerun()

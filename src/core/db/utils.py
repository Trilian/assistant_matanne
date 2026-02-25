"""
Utils - Utilitaires de base de données.

Fonctions pour:
- Vérification de connexion
- Informations sur la DB
- Initialisation et maintenance
- Health checks

Découplé de Streamlit — cache géré via @avec_cache.
"""

import logging
import time

from sqlalchemy import text

from ..config import obtenir_parametres
from ..exceptions import ErreurBaseDeDonnees
from .engine import obtenir_moteur, obtenir_moteur_securise
from .migrations import GestionnaireMigrations

logger = logging.getLogger(__name__)

__all__ = [
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "creer_toutes_tables",
    "verifier_sante",
    "vacuum_database",
]


def verifier_connexion() -> tuple[bool, str]:
    """
    Vérifie la connexion à la base de données.

    Returns:
        Tuple (succès, message)
    """
    try:
        moteur = obtenir_moteur_securise()
        if not moteur:
            return False, "Engine non disponible"

        with moteur.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True, "Connexion OK"

    except ErreurBaseDeDonnees as e:
        return False, f"Erreur connexion: {e.message}"

    except Exception as e:
        logger.error(f"[ERROR] Test connexion échoué: {e}")
        return False, f"Erreur: {str(e)}"


def obtenir_infos_db() -> dict:
    """
    Retourne les informations sur la base de données.

    Returns:
        Dictionnaire avec informations DB
    """
    try:
        moteur = obtenir_moteur()

        with moteur.connect() as conn:
            resultat = conn.execute(
                text(
                    """
                SELECT
                    version() as version,
                    current_database() as database,
                    current_user as user,
                    pg_size_pretty(pg_database_size(current_database())) as size
            """
                )
            ).fetchone()

            parametres = obtenir_parametres()
            db_url = parametres.DATABASE_URL

            hote = "unknown"
            if "@" in db_url:
                hote = db_url.split("@")[1].split(":")[0]

            return {
                "statut": "connected",
                "version": resultat[0].split(",")[0],
                "base_donnees": resultat[1],
                "utilisateur": resultat[2],
                "taille": resultat[3],
                "hote": hote,
                "version_schema": GestionnaireMigrations.obtenir_version_courante(),
                "erreur": None,
            }

    except Exception as e:
        logger.error(f"obtenir_infos_db erreur: {e}")
        return {
            "statut": "error",
            "erreur": str(e),
            "version": None,
            "base_donnees": None,
            "utilisateur": None,
            "version_schema": 0,
        }


def initialiser_database(executer_migrations: bool = True):
    """
    Initialise la base de données.

    Args:
        executer_migrations: Si True, exécute les migrations automatiquement

    Returns:
        True si succès
    """
    parametres = obtenir_parametres()

    if parametres.est_production():
        logger.info("Mode production: vérification schéma uniquement")

    try:
        moteur = obtenir_moteur()

        # Vérifier connexion
        with moteur.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("[OK] Connexion DB OK")

        # Exécuter migrations si demandé
        if executer_migrations:
            logger.info("🔄 Exécution migrations...")
            GestionnaireMigrations.executer_migrations()

        return True

    except Exception as e:
        logger.error(f"[ERROR] Erreur initialisation DB: {e}")
        return False


def creer_toutes_tables():
    """
    Crée toutes les tables (dev/setup uniquement).

    [!] ATTENTION: Ne pas appeler en production.
    """
    parametres = obtenir_parametres()

    if parametres.est_production():
        logger.warning("creer_toutes_tables ignoré en production")
        return

    try:
        from ..models import Base

        moteur = obtenir_moteur()
        Base.metadata.create_all(bind=moteur)
        logger.info("[OK] Tables créées/vérifiées")

    except Exception as e:
        logger.error(f"Erreur création tables: {e}")
        raise


def verifier_sante() -> dict:
    """
    Health check complet de la DB.

    Returns:
        Dictionnaire avec statut et métriques
    """
    try:
        moteur = obtenir_moteur()

        with moteur.connect() as conn:
            connexions_actives = conn.execute(
                text(
                    """
                SELECT count(*)
                FROM pg_stat_activity
                WHERE state = 'active'
            """
                )
            ).scalar()

            taille_db = conn.execute(text("SELECT pg_database_size(current_database())")).scalar()

            return {
                "sain": True,
                "connexions_actives": connexions_actives,
                "taille_base_octets": taille_db,
                "version_schema": GestionnaireMigrations.obtenir_version_courante(),
                "timestamp": time.time(),
            }

    except Exception as e:
        logger.error(f"Health check échoué: {e}")
        return {"sain": False, "erreur": str(e), "timestamp": time.time()}


def vacuum_database() -> bool:
    """
    Exécute VACUUM sur la base de données PostgreSQL pour optimiser l'espace.

    Returns:
        True si succès, False sinon
    """
    try:
        moteur = obtenir_moteur()

        # VACUUM nécessite autocommit
        with moteur.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("VACUUM ANALYZE"))
            logger.info("✅ VACUUM ANALYZE exécuté avec succès")
            return True

    except Exception as e:
        logger.error(f"❌ Erreur VACUUM: {e}")
        raise

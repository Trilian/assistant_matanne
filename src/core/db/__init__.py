"""
Database - Module de gestion de la base de données.

Ce module fournit:
- Création et gestion de l'engine SQLAlchemy
- Gestion des sessions avec context managers
- Gestionnaire de migrations
- Health checks et utilitaires
"""

from .engine import obtenir_moteur, obtenir_moteur_securise
from .migrations import GestionnaireMigrations
from .session import (
    obtenir_contexte_db,
    obtenir_db_securise,
    obtenir_fabrique_session,
)
from .utils import (
    creer_toutes_tables,
    initialiser_database,
    obtenir_infos_db,
    vacuum_database,
    verifier_connexion,
    verifier_sante,
)

__all__ = [
    # Engine
    "obtenir_moteur",
    "obtenir_moteur_securise",
    # Session
    "obtenir_contexte_db",
    "obtenir_db_securise",
    "obtenir_fabrique_session",
    # Migrations
    "GestionnaireMigrations",
    # Utils
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "creer_toutes_tables",
    "verifier_sante",
    "vacuum_database",
]

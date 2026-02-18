"""
Database - Module de rétrocompatibilité.

DEPRECATED: Importer depuis src.core.db à la place.
Ce fichier existe uniquement pour la rétrocompatibilité.

Exemple de migration:
    # Ancien import (toujours supporté)
    from src.core.database import obtenir_moteur

    # Nouvel import (recommandé)
    from src.core.db import obtenir_moteur
    # ou
    from src.core import obtenir_moteur
"""

import warnings

import streamlit as st  # noqa: F401 - nécessaire pour les tests patchant src.core.database.st

# Import obtenir_parametres pour les tests qui patchent src.core.database.obtenir_parametres
from .config import obtenir_parametres

# Avertissement de dépréciation (désactivé par défaut pour ne pas polluer les logs)
# warnings.warn(
#     "Le module src.core.database est déprécié. "
#     "Utilisez src.core.db à la place.",
#     DeprecationWarning,
#     stacklevel=2
# )
# Ré-exports depuis le nouveau module
from .db import (
    GestionnaireMigrations,
    creer_toutes_tables,
    get_db_context,
    initialiser_database,
    obtenir_contexte_db,
    obtenir_db_securise,
    obtenir_fabrique_session,
    obtenir_infos_db,
    obtenir_moteur,
    obtenir_moteur_securise,
    vacuum_database,
    verifier_connexion,
    verifier_sante,
)

__all__ = [
    "obtenir_moteur",
    "obtenir_moteur_securise",
    "obtenir_contexte_db",
    "obtenir_db_securise",
    "obtenir_fabrique_session",
    "get_db_context",
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "creer_toutes_tables",
    "verifier_sante",
    "vacuum_database",
    "GestionnaireMigrations",
]

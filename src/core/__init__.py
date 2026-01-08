"""
Module Core - Exports centralisés.

Ce module exporte toutes les fonctions principales du core
avec des alias pour la compatibilité avec le code existant.
"""

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

from .logging import (
    GestionnaireLog,
    obtenir_logger,
    LogManager,
    get_logger,
)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

from .config import (
    Parametres,
    obtenir_parametres,
)

# Alias pour compatibilité
get_settings = obtenir_parametres

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════

from .database import (
    obtenir_moteur,
    obtenir_contexte_db,
    obtenir_session,
    verifier_connexion,
    obtenir_infos_db,
    initialiser_database,
)

# Alias pour compatibilité
get_engine = obtenir_moteur
get_db_context = obtenir_contexte_db
get_session = obtenir_session
check_connection = verifier_connexion
get_db_info = obtenir_infos_db

# ═══════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════

from .models import Base, metadata

# ═══════════════════════════════════════════════════════════
# ERRORS
# ═══════════════════════════════════════════════════════════

from .errors import (
    ErreurBase,
    ErreurBaseDeDonnees,
    ErreurValidation,
    ErreurIA,
    ErreurConfiguration,
)

# ═══════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════

from .cache import Cache

# ═══════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════

from .state import StateManager, get_state

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Logging
    "GestionnaireLog",
    "obtenir_logger",
    "LogManager",
    "get_logger",
    # Config
    "Parametres",
    "obtenir_parametres",
    "get_settings",
    # Database
    "obtenir_moteur",
    "obtenir_contexte_db",
    "obtenir_session",
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "get_engine",
    "get_db_context",
    "get_session",
    "check_connection",
    "get_db_info",
    # Models
    "Base",
    "metadata",
    # Errors
    "ErreurBase",
    "ErreurBaseDeDonnees",
    "ErreurValidation",
    "ErreurIA",
    "ErreurConfiguration",
    # Cache
    "Cache",
    # State
    "StateManager",
    "get_state",
]


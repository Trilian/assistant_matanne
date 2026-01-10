"""
Core - Module central de l'application.

Expose les composants essentiels pour l'ensemble de l'application.
"""

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

from .config import Parametres, obtenir_parametres

# Alias anglais
get_settings = obtenir_parametres

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

from .logging import (
    GestionnaireLog,
    LogManager,
    obtenir_logger,
    get_logger
)

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════

from .database import (
    obtenir_moteur,
    obtenir_contexte_db,
    obtenir_db_securise,
    verifier_connexion,
    obtenir_infos_db,
    initialiser_database,
    GestionnaireMigrations
)

# Alias anglais
get_engine = obtenir_moteur
get_db_context = obtenir_contexte_db
get_safe_db = obtenir_db_securise
check_connection = verifier_connexion
get_db_info = obtenir_infos_db
init_database = initialiser_database
MigrationManager = GestionnaireMigrations

# ═══════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════

from .state import (
    EtatApp,
    GestionnaireEtat,
    obtenir_etat,
    naviguer,
    revenir
)

# Alias anglais
AppState = EtatApp
StateManager = GestionnaireEtat
get_state = obtenir_etat
navigate = naviguer
go_back = revenir

# ═══════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════

from .cache import (
    Cache,
    cached,
    LimiteDebit,
    RateLimit
)

# ═══════════════════════════════════════════════════════════
# ERRORS
# ═══════════════════════════════════════════════════════════

from .errors import (
    ExceptionApp,
    ErreurValidation,
    ErreurNonTrouve,
    ErreurBaseDeDonnees,
    ErreurServiceIA,
    ErreurLimiteDebit,
    gerer_erreurs,
    handle_errors
)

# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

from .validation import (
    NettoyeurEntrees,
    InputSanitizer,
    valider_modele,
    validate_model
)

# ═══════════════════════════════════════════════════════════
# AI
# ═══════════════════════════════════════════════════════════

from .ai import (
    ClientIA,
    obtenir_client_ia,
    AnalyseurIA,
    CacheIA
)

# Alias anglais
AIClient = ClientIA
get_ai_client = obtenir_client_ia
AIParser = AnalyseurIA
AICache = CacheIA

# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════

from .constants import *

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Config
    "Parametres",
    "obtenir_parametres",
    "get_settings",

    # Logging
    "GestionnaireLog",
    "LogManager",
    "obtenir_logger",
    "get_logger",

    # Database
    "obtenir_moteur",
    "obtenir_contexte_db",
    "obtenir_db_securise",
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "GestionnaireMigrations",
    "get_engine",
    "get_db_context",
    "get_safe_db",
    "check_connection",
    "get_db_info",
    "init_database",
    "MigrationManager",

    # State
    "EtatApp",
    "GestionnaireEtat",
    "obtenir_etat",
    "naviguer",
    "revenir",
    "AppState",
    "StateManager",
    "get_state",
    "navigate",
    "go_back",

    # Cache
    "Cache",
    "cached",
    "LimiteDebit",
    "RateLimit",

    # Errors
    "ExceptionApp",
    "ErreurValidation",
    "ErreurNonTrouve",
    "ErreurBaseDeDonnees",
    "ErreurServiceIA",
    "ErreurLimiteDebit",
    "gerer_erreurs",
    "handle_errors",

    # Validation
    "NettoyeurEntrees",
    "InputSanitizer",
    "valider_modele",
    "validate_model",

    # AI
    "ClientIA",
    "obtenir_client_ia",
    "AnalyseurIA",
    "CacheIA",
    "AIClient",
    "get_ai_client",
    "AIParser",
    "AICache",
]
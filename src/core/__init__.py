"""
Core - Module central de l'application.

Expose les composants essentiels pour l'ensemble de l'application.
Convention : Noms français en priorité, alias anglais disponibles.
"""

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

from .config import Parametres, obtenir_parametres

# Alias anglais
Settings = Parametres
get_settings = obtenir_parametres

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

from .logging import (
    GestionnaireLog,
    obtenir_logger,
)

# Alias anglais
LogManager = GestionnaireLog
get_logger = obtenir_logger

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
)

# Alias anglais
RateLimit = LimiteDebit

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
)

# Alias anglais
AppException = ExceptionApp
ValidationError = ErreurValidation
NotFoundError = ErreurNonTrouve
DatabaseError = ErreurBaseDeDonnees
AIServiceError = ErreurServiceIA
RateLimitError = ErreurLimiteDebit
handle_errors = gerer_erreurs

# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

from .validation import (
    NettoyeurEntrees,
    valider_modele,
)

# Alias anglais
InputSanitizer = NettoyeurEntrees
validate_model = valider_modele

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
    "Settings",
    "get_settings",

    # Logging
    "GestionnaireLog",
    "obtenir_logger",
    "LogManager",
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
    "AppException",
    "ValidationError",
    "NotFoundError",
    "DatabaseError",
    "AIServiceError",
    "RateLimitError",
    "handle_errors",

    # Validation
    "NettoyeurEntrees",
    "valider_modele",
    "InputSanitizer",
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
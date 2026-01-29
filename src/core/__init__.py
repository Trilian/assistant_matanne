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
    GestionnaireMigrations,
    initialiser_database,
    obtenir_contexte_db,
    obtenir_db_securise,
    obtenir_infos_db,
    obtenir_moteur,
    verifier_connexion,
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

from .state import EtatApp, GestionnaireEtat, naviguer, obtenir_etat, revenir

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
    LimiteDebit,
    cached,
)

# Cache multi-niveaux (nouveau)
from .cache_multi import (
    MultiLevelCache,
    get_cache,
    cached as cached_multi,
    CacheEntry,
    CacheStats,
)

# Mode offline
from .offline import (
    ConnectionStatus,
    ConnectionManager,
    OperationType,
    PendingOperation,
    OfflineQueue,
    OfflineSynchronizer,
    offline_aware,
    render_connection_status,
    render_sync_panel,
)

# Alias anglais
RateLimit = LimiteDebit

# ═══════════════════════════════════════════════════════════
# ERRORS BASE (pures, sans UI)
# ═══════════════════════════════════════════════════════════

from .errors_base import (
    ExceptionApp,
    ErreurValidation,
    ErreurNonTrouve,
    ErreurBaseDeDonnees,
    ErreurServiceIA,
    ErreurLimiteDebit,
    ErreurServiceExterne,
    ErreurConfiguration,
    exiger_champs,
    valider_type,
    valider_plage,
)

# ═══════════════════════════════════════════════════════════
# ERRORS (avec UI Streamlit)
# ═══════════════════════════════════════════════════════════

from .errors import (
    gerer_erreurs,
    afficher_erreur_streamlit,
    GestionnaireErreurs,
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
# DECORATORS
# ═══════════════════════════════════════════════════════════

from .decorators import (
    with_db_session,
    with_cache,
    with_error_handling,
    with_validation,
)

# ═══════════════════════════════════════════════════════════
# VALIDATORS PYDANTIC
# ═══════════════════════════════════════════════════════════

from .validators_pydantic import (
    RecetteInput,
    IngredientInput,
    EtapeInput,
    IngredientStockInput,
    RepasInput,
    RoutineInput,
    TacheRoutineInput,
    EntreeJournalInput,
    ProjetInput,
)

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

from .ai import AnalyseurIA, CacheIA, ClientIA, obtenir_client_ia

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
# PERFORMANCE
# ═══════════════════════════════════════════════════════════

from .performance import (
    FunctionProfiler,
    MemoryMonitor,
    SQLOptimizer,
    PerformanceDashboard,
    ComponentLoader,
    profile,
    debounce,
    throttle,
    measure_time,
    track_query,
    render_performance_panel,
    render_mini_performance_badge,
)

# ═══════════════════════════════════════════════════════════
# SQL OPTIMIZER
# ═══════════════════════════════════════════════════════════

from .sql_optimizer import (
    SQLAlchemyListener,
    N1Detector,
    BatchLoader,
    OptimizedQueryBuilder,
    render_sql_analysis,
)

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
    # Errors Base (pures)
    "ExceptionApp",
    "ErreurValidation",
    "ErreurNonTrouve",
    "ErreurBaseDeDonnees",
    "ErreurServiceIA",
    "ErreurLimiteDebit",
    "ErreurServiceExterne",
    "ErreurConfiguration",
    "exiger_champs",
    "valider_type",
    "valider_plage",
    # Errors (avec UI)
    "gerer_erreurs",
    "afficher_erreur_streamlit",
    "GestionnaireErreurs",
    # Alias anglais (errors)
    "AppException",
    "ValidationError",
    "NotFoundError",
    "DatabaseError",
    "AIServiceError",
    "RateLimitError",
    "handle_errors",
    # Decorators
    "with_db_session",
    "with_cache",
    "with_error_handling",
    "with_validation",
    # Validators Pydantic
    "RecetteInput",
    "IngredientInput",
    "EtapeInput",
    "IngredientStockInput",
    "RepasInput",
    "RoutineInput",
    "TacheRoutineInput",
    "EntreeJournalInput",
    "ProjetInput",
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
    # Cache multi-niveaux
    "MultiLevelCache",
    "get_cache",
    "cached_multi",
    "CacheEntry",
    "CacheStats",
    # Mode offline
    "ConnectionStatus",
    "ConnectionManager",
    "OperationType",
    "PendingOperation",
    "OfflineQueue",
    "OfflineSynchronizer",
    "offline_aware",
    "render_connection_status",
    "render_sync_panel",
    # Performance
    "FunctionProfiler",
    "MemoryMonitor",
    "SQLOptimizer",
    "PerformanceDashboard",
    "ComponentLoader",
    "profile",
    "debounce",
    "throttle",
    "measure_time",
    "track_query",
    "render_performance_panel",
    "render_mini_performance_badge",
    # SQL Optimizer
    "SQLAlchemyListener",
    "N1Detector",
    "BatchLoader",
    "OptimizedQueryBuilder",
    "render_sql_analysis",
]

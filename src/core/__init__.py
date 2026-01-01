"""
Core - Point d'Entrée Unifié
"""

# Config
from .config import get_settings, Settings

# Database
from .database import (
    get_db_context,
    get_db_safe,
    check_connection,
    get_db_info,
    health_check,
    init_database,
    create_all_tables,
    MigrationManager
)

# Models
from .models import (
    Base,
    Ingredient,
    Recette,
    RecetteIngredient,
    EtapeRecette,
    ArticleInventaire,
    ArticleCourses,
    PlanningHebdomadaire,
    RepasPlanning,
    VersionRecette,
    ProfilEnfant,
    EntreeBienEtre,
    Routine,
    TacheRoutine,
    Projet,
    TacheProjet,
    ElementJardin,
    LogJardin,
    EvenementCalendrier,
    Utilisateur,
    ProfilUtilisateur,
    Notification
)

# AI
from .ai import (
    AIClient,
    get_ai_client,
    AIParser,
    parse_list_response,
    AICache,
    SemanticCache,
    SemanticCacheConfig,
    EmbeddingEngine
)

# Cache
from .cache import Cache, RateLimit

# Errors
from .errors import (
    AppException,
    ValidationError,
    NotFoundError,
    DatabaseError,
    AIServiceError,
    RateLimitError,
    handle_errors
)

# Validation (Unified)
from .validation_unified import (
    # Sanitization
    InputSanitizer,

    # Pydantic Models
    IngredientInput,
    EtapeInput,
    RecetteInput,
    ArticleInventaireInput,
    ArticleCoursesInput,
    RepasInput,

    # Schémas Dict
    RECETTE_SCHEMA,
    INVENTAIRE_SCHEMA,
    COURSES_SCHEMA,

    # Helpers
    validate_model,
    validate_streamlit_form,
    validate_and_sanitize_form,
    show_validation_errors,
    require_fields,
    require_positive,
    require_exists,

    # Decorator
    validate_input,
)

# Logging
from .logging import LogManager, get_logger

# State
from .state import (
    StateManager,
    AppState,
    get_state,
    navigate,
    go_back,
    get_breadcrumb,
    is_debug_mode,
    clear_ui_states
)

__all__ = [
    # Config
    "get_settings",
    "Settings",

    # Database
    "get_db_context",
    "get_db_safe",
    "check_connection",
    "get_db_info",
    "health_check",
    "init_database",
    "create_all_tables",
    "MigrationManager",

    # Models
    "Base",
    "Ingredient",
    "Recette",
    "RecetteIngredient",
    "EtapeRecette",
    "ArticleInventaire",
    "ArticleCourses",
    "PlanningHebdomadaire",
    "RepasPlanning",
    "VersionRecette",
    "ProfilEnfant",
    "EntreeBienEtre",
    "Routine",
    "TacheRoutine",
    "Projet",
    "TacheProjet",
    "ElementJardin",
    "LogJardin",
    "EvenementCalendrier",
    "Utilisateur",
    "ProfilUtilisateur",
    "Notification",

    # AI
    "AIClient",
    "get_ai_client",
    "AIParser",
    "parse_list_response",
    "AICache",
    "SemanticCache",
    "SemanticCacheConfig",
    "EmbeddingEngine",

    # Cache
    "Cache",
    "RateLimit",

    # Errors
    "AppException",
    "ValidationError",
    "NotFoundError",
    "DatabaseError",
    "AIServiceError",
    "RateLimitError",
    "handle_errors",

    # Validation
    "InputSanitizer",
    "IngredientInput",
    "EtapeInput",
    "RecetteInput",
    "ArticleInventaireInput",
    "ArticleCoursesInput",
    "RepasInput",
    "RECETTE_SCHEMA",
    "INVENTAIRE_SCHEMA",
    "COURSES_SCHEMA",
    "validate_model",
    "validate_streamlit_form",
    "validate_and_sanitize_form",
    "show_validation_errors",
    "require_fields",
    "require_positive",
    "require_exists",
    "validate_input",

    # Logging
    "LogManager",
    "get_logger",

    # State
    "StateManager",
    "AppState",
    "get_state",
    "navigate",
    "go_back",
    "get_breadcrumb",
    "is_debug_mode",
    "clear_ui_states",
]
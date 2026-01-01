"""
Core - Point d'Entrée Unifié avec Nouvelles Features
"""

# Config
from .config import get_settings, Settings

# Database
from .database import (
    get_db_context,
    check_connection,
    get_db_info,
    init_db
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
    VersionRecette
)

# AI
from .ai import (
    AIClient,
    get_ai_client,
    AIParser,
    parse_list_response,
    AICache
)

# Cache
from .cache import Cache, AICache as AICache2, RateLimit

# Errors
from .errors import (
    AppException,
    ValidationError,
    NotFoundError,
    DatabaseError,
    AIServiceError,
    RateLimitError,
    handle_errors,
    require_fields,
    require_positive,
    require_exists
)

# Validation
from .validation import (
    IngredientInput,
    EtapeInput,
    RecetteInput,
    ArticleInventaireInput,
    ArticleCoursesInput,
    RepasInput,
    validate_model
)

# 🆕 Validation Middleware (Sécurité)
from .validation_middleware import (
    InputSanitizer,
    validate_input,
    validate_streamlit_form,
    validate_and_sanitize_form,
    show_validation_errors,
    RECETTE_SCHEMA,
    INVENTAIRE_SCHEMA,
    COURSES_SCHEMA
)

# Logging
from .logging import LogManager, get_logger

# State
from .state import StateManager, AppState, get_state, navigate

__all__ = [
    # Config
    "get_settings", "Settings",

    # Database
    "get_db_context", "check_connection", "get_db_info", "init_db",

    # Models
    "Base", "Ingredient", "Recette", "RecetteIngredient", "EtapeRecette",
    "ArticleInventaire", "ArticleCourses", "PlanningHebdomadaire",
    "RepasPlanning", "VersionRecette",

    # AI
    "AIClient", "get_ai_client", "AIParser", "parse_list_response", "AICache",

    # Cache
    "Cache", "RateLimit",

    # Errors
    "AppException", "ValidationError", "NotFoundError", "DatabaseError",
    "AIServiceError", "RateLimitError", "handle_errors",
    "require_fields", "require_positive", "require_exists",

    # Validation
    "IngredientInput", "EtapeInput", "RecetteInput",
    "ArticleInventaireInput", "ArticleCoursesInput", "RepasInput",
    "validate_model",

    # 🆕 Validation Middleware
    "InputSanitizer",
    "validate_input",
    "validate_streamlit_form",
    "validate_and_sanitize_form",
    "show_validation_errors",
    "RECETTE_SCHEMA",
    "INVENTAIRE_SCHEMA",
    "COURSES_SCHEMA",

    # Logging
    "LogManager", "get_logger",

    # State
    "StateManager", "AppState", "get_state", "navigate"
]

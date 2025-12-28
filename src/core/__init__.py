"""
Core Module - Point d'entrée unifié
Expose les composants essentiels de manière cohérente
"""

# Configuration
from .config import Settings, get_settings

# Database
from .database import (
    get_db_context,
    get_db_safe,
    check_connection,
    get_db_info,
    create_all_tables
)

# Modèles
from .models import Base

# IA
from .ai import AIClient, AIParser, AICache

# Cache
from .cache import Cache, RateLimit

# Erreurs
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

# State
from .state import StateManager, get_state

# Validation
from .validation import (
    RecetteInput,
    IngredientInput,
    EtapeInput,
    validate_model
)

__all__ = [
    # Config
    "Settings",
    "get_settings",

    # Database
    "get_db_context",
    "get_db_safe",
    "check_connection",
    "get_db_info",
    "create_all_tables",
    "Base",

    # IA
    "AIClient",
    "AIParser",
    "AICache",

    # Cache
    "Cache",
    "RateLimit",

    # Erreurs
    "AppException",
    "ValidationError",
    "NotFoundError",
    "DatabaseError",
    "AIServiceError",
    "RateLimitError",
    "handle_errors",
    "require_fields",
    "require_positive",
    "require_exists",

    # State
    "StateManager",
    "get_state",

    # Validation
    "RecetteInput",
    "IngredientInput",
    "EtapeInput",
    "validate_model",
]

__version__ = "2.0.0"
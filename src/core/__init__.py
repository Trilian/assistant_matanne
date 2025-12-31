"""
Core Module - Point d'entrée unifié
Exports simplifiés
"""

# Configuration
from .config import Settings, get_settings

# Database
from .database import get_db_context, check_connection, get_db_info

# Modèles
from .models import Base

# IA
from .ai import AIClient, AIParser, get_ai_client

# Cache
from .cache import Cache, AICache, RateLimit

# Erreurs
from .errors import (
    AppException, ValidationError, NotFoundError, DatabaseError,
    AIServiceError, RateLimitError, handle_errors, require_fields,
    require_positive, require_exists
)

# State
from .state import StateManager, get_state

# Validation
from .validation import (
    RecetteInput, IngredientInput, EtapeInput,
    ArticleInventaireInput, ArticleCoursesInput, RepasInput,
    validate_model, clean_text
)

# Logging
from .logging import get_logger, LogManager

__all__ = [
    # Config
    "Settings", "get_settings",
    # Database
    "get_db_context", "check_connection", "get_db_info", "Base",
    # IA
    "AIClient", "AIParser", "get_ai_client",
    # Cache
    "Cache", "AICache", "RateLimit",
    # Erreurs
    "AppException", "ValidationError", "NotFoundError", "DatabaseError",
    "AIServiceError", "RateLimitError", "handle_errors", "require_fields",
    "require_positive", "require_exists",
    # State
    "StateManager", "get_state",
    # Validation
    "RecetteInput", "IngredientInput", "EtapeInput",
    "ArticleInventaireInput", "ArticleCoursesInput", "RepasInput",
    "validate_model", "clean_text",
    # Logging
    "get_logger", "LogManager"
]

__version__ = "2.0.0"
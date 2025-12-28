"""
Module Erreurs - Exceptions et Handlers
"""
from .exceptions import (
    AppException,
    ValidationError,
    NotFoundError,
    DatabaseError,
    AIServiceError,
    RateLimitError,
    AuthorizationError,
    BusinessLogicError,
    ExternalServiceError
)

from .handlers import (
    handle_errors,
    require_fields,
    require_positive,
    require_exists,
    require_permission,
    error_context
)

__all__ = [
    # Exceptions
    "AppException",
    "ValidationError",
    "NotFoundError",
    "DatabaseError",
    "AIServiceError",
    "RateLimitError",
    "AuthorizationError",
    "BusinessLogicError",
    "ExternalServiceError",

    # Handlers
    "handle_errors",
    "require_fields",
    "require_positive",
    "require_exists",
    "require_permission",
    "error_context"
]

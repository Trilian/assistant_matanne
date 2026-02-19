"""
Schémas Pydantic pour l'API REST.

Centralise tous les schémas de validation et sérialisation.
"""

from .common import (
    ErreurResponse,
    MessageResponse,
    PaginationParams,
    ReponsePaginee,
)

__all__ = [
    # Common
    "PaginationParams",
    "ReponsePaginee",
    "MessageResponse",
    "ErreurResponse",
]

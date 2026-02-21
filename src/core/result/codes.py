"""
Codes d'erreur et ErrorInfo — Types structurés pour les erreurs.

Usage::
    from src.core.result import ErrorCode, ErrorInfo

    info = ErrorInfo(
        code=ErrorCode.NOT_FOUND,
        message="Recette #42 introuvable",
        message_utilisateur="Recette non trouvée",
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any


class ErrorCode(StrEnum):
    """Codes d'erreur standardisés pour les Result."""

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Base de données
    NOT_FOUND = "NOT_FOUND"
    DUPLICATE = "DUPLICATE"
    DATABASE_ERROR = "DATABASE_ERROR"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"

    # IA
    AI_ERROR = "AI_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    PARSING_ERROR = "PARSING_ERROR"
    AI_UNAVAILABLE = "AI_UNAVAILABLE"

    # Externe
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"

    # Système
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # Métier
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"


@dataclass(frozen=True, slots=True)
class ErrorInfo:
    """
    Détails d'erreur structurés et immutables.

    Attributes:
        code: Code d'erreur standardisé
        message: Message technique pour les logs
        message_utilisateur: Message friendly pour l'UI
        details: Détails supplémentaires
        timestamp: Horodatage de l'erreur
        source: Service/fonction source de l'erreur
        stack_trace: Stack trace optionnelle
    """

    code: ErrorCode
    message: str
    message_utilisateur: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    stack_trace: str = ""

    def __post_init__(self) -> None:
        if not self.message_utilisateur:
            object.__setattr__(self, "message_utilisateur", self.message)

    def to_dict(self) -> dict[str, Any]:
        """Sérialise en dictionnaire."""
        return {
            "code": self.code.value,
            "message": self.message,
            "message_utilisateur": self.message_utilisateur,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"


__all__ = ["ErrorCode", "ErrorInfo"]

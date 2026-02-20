"""
Commands — Opérations d'écriture (validées, auditées).

Les commands:
- Modifient l'état du système
- Sont validées avant exécution
- Génèrent des événements pour l'audit
- Retournent un Result[T, ErrorInfo]

Example:
    @dataclass
    class CreerRecetteCommand(Command[Recette]):
        nom: str
        ingredients: list[dict]
        user_id: str | None = None

        def validate(self) -> Result[None, ErrorInfo]:
            if not self.nom or len(self.nom) < 2:
                return Failure(ErrorInfo(
                    code=ErrorCode.VALIDATION_ERROR,
                    message="Le nom doit contenir au moins 2 caractères"
                ))
            return Success(None)

        def execute(self) -> Result[Recette, ErrorInfo]:
            with obtenir_contexte_db() as db:
                recette = Recette(nom=self.nom)
                db.add(recette)
                db.commit()
                return Success(recette)

    # Usage
    command = CreerRecetteCommand(nom="Tarte aux pommes", ingredients=[...])
    result = dispatcher.dispatch_command(command)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable
from uuid import uuid4

from src.services.core.base.result import ErrorCode, ErrorInfo, Failure, Result, Success

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Type du résultat de la command


# ═══════════════════════════════════════════════════════════
# COMMAND PROTOCOL
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class CommandProtocol(Protocol[T]):
    """Protocol pour les commands (PEP 544)."""

    id: str
    timestamp: datetime
    user_id: str | None

    def validate(self) -> Result[None, ErrorInfo]: ...

    def execute(self) -> Result[T, ErrorInfo]: ...


# ═══════════════════════════════════════════════════════════
# COMMAND BASE CLASS
# ═══════════════════════════════════════════════════════════


@dataclass
class Command(ABC, Generic[T]):
    """
    Command de base — Écriture avec validation et audit.

    Chaque command a un ID unique et un timestamp pour l'audit.
    La validation est exécutée AVANT l'exécution.

    Attributes:
        id: Identifiant unique de la command (UUID auto-généré).
        timestamp: Horodatage de création.
        user_id: Utilisateur exécutant la command (optionnel).
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str | None = None

    @abstractmethod
    def validate(self) -> Result[None, ErrorInfo]:
        """
        Valide la command avant exécution.

        Doit vérifier:
        - Présence des champs requis
        - Format des données
        - Règles métier simples

        Returns:
            Success(None) si valide, Failure(ErrorInfo) sinon.
        """
        ...

    @abstractmethod
    def execute(self) -> Result[T, ErrorInfo]:
        """
        Exécute la command. Peut modifier l'état.

        Appelé uniquement si validate() retourne Success.

        Returns:
            Result[T, ErrorInfo]: Succès avec le résultat ou Failure.
        """
        ...

    def __str__(self) -> str:
        """Représentation lisible de la command."""
        return f"{self.__class__.__name__}(id={self.id[:8]}..., user={self.user_id})"


# ═══════════════════════════════════════════════════════════
# COMMAND HANDLER
# ═══════════════════════════════════════════════════════════


@dataclass
class CommandHandler(ABC, Generic[T]):
    """
    Handler de command avec injection de dépendances.

    Utile pour les commands nécessitant des services externes
    ou une logique transactionnelle complexe.
    """

    @abstractmethod
    def handle(self, command: Command[T]) -> Result[T, ErrorInfo]:
        """
        Traite la command.

        Args:
            command: La command à traiter.

        Returns:
            Result[T, ErrorInfo]: Résultat de la command.
        """
        ...


# ═══════════════════════════════════════════════════════════
# COMMAND RESULT
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class CommandResult(Generic[T]):
    """
    Résultat d'une command avec métadonnées d'audit.

    Attributes:
        result: Le Result[T, ErrorInfo] de l'exécution.
        command_id: ID de la command exécutée.
        command_type: Type de la command (nom de classe).
        executed_at: Horodatage d'exécution.
        duration_ms: Durée d'exécution en millisecondes.
        user_id: Utilisateur qui a exécuté la command.
    """

    result: Result[T, ErrorInfo]
    command_id: str
    command_type: str
    executed_at: datetime
    duration_ms: float
    user_id: str | None = None

    @property
    def is_success(self) -> bool:
        return self.result.is_success

    @property
    def is_failure(self) -> bool:
        return self.result.is_failure

    @property
    def value(self) -> T | None:
        """Retourne la valeur si succès, None sinon."""
        return self.result.value if self.is_success else None

    @property
    def error(self) -> ErrorInfo | None:
        """Retourne l'erreur si échec, None sinon."""
        return self.result.error if self.is_failure else None

    def to_audit_dict(self) -> dict[str, Any]:
        """Sérialise pour l'audit trail."""
        return {
            "command_id": self.command_id,
            "command_type": self.command_type,
            "executed_at": self.executed_at.isoformat(),
            "duration_ms": self.duration_ms,
            "user_id": self.user_id,
            "success": self.is_success,
            "error": self.error.to_dict() if self.error else None,
        }


# ═══════════════════════════════════════════════════════════
# VALIDATION HELPERS
# ═══════════════════════════════════════════════════════════


def validate_required(value: Any, field_name: str) -> Result[None, ErrorInfo]:
    """Valide qu'un champ est présent et non vide."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return Failure(
            ErrorInfo(
                code=ErrorCode.MISSING_FIELD,
                message=f"Le champ '{field_name}' est requis",
                message_utilisateur=f"Veuillez renseigner {field_name}",
                details={"field": field_name},
            )
        )
    return Success(None)


def validate_min_length(value: str, min_len: int, field_name: str) -> Result[None, ErrorInfo]:
    """Valide la longueur minimale d'une chaîne."""
    if len(value) < min_len:
        return Failure(
            ErrorInfo(
                code=ErrorCode.VALIDATION_ERROR,
                message=f"'{field_name}' doit contenir au moins {min_len} caractères",
                message_utilisateur=f"{field_name} trop court (min {min_len} caractères)",
                details={"field": field_name, "min_length": min_len, "actual": len(value)},
            )
        )
    return Success(None)


def validate_positive(value: int | float, field_name: str) -> Result[None, ErrorInfo]:
    """Valide qu'un nombre est positif."""
    if value <= 0:
        return Failure(
            ErrorInfo(
                code=ErrorCode.VALIDATION_ERROR,
                message=f"'{field_name}' doit être positif",
                message_utilisateur=f"{field_name} doit être supérieur à 0",
                details={"field": field_name, "value": value},
            )
        )
    return Success(None)


def validate_in_range(
    value: int | float,
    min_val: int | float,
    max_val: int | float,
    field_name: str,
) -> Result[None, ErrorInfo]:
    """Valide qu'un nombre est dans une plage."""
    if not min_val <= value <= max_val:
        return Failure(
            ErrorInfo(
                code=ErrorCode.VALIDATION_ERROR,
                message=f"'{field_name}' doit être entre {min_val} et {max_val}",
                message_utilisateur=f"{field_name} hors limites ({min_val}-{max_val})",
                details={"field": field_name, "value": value, "min": min_val, "max": max_val},
            )
        )
    return Success(None)


def validate_enum(value: str, allowed: list[str], field_name: str) -> Result[None, ErrorInfo]:
    """Valide qu'une valeur est dans une liste autorisée."""
    if value not in allowed:
        return Failure(
            ErrorInfo(
                code=ErrorCode.VALIDATION_ERROR,
                message=f"'{field_name}' doit être parmi: {allowed}",
                message_utilisateur=f"Valeur invalide pour {field_name}",
                details={"field": field_name, "value": value, "allowed": allowed},
            )
        )
    return Success(None)


def collect_validations(*results: Result[None, ErrorInfo]) -> Result[None, ErrorInfo]:
    """
    Collecte plusieurs validations et retourne la première erreur.

    Usage:
        return collect_validations(
            validate_required(self.nom, "nom"),
            validate_min_length(self.nom, 2, "nom"),
            validate_positive(self.portions, "portions"),
        )
    """
    for result in results:
        if result.is_failure:
            return result
    return Success(None)

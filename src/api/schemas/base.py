"""
Schémas de base et mixins partagés.

Fournit des validateurs et classes de base réutilisables.
"""

from datetime import datetime

from pydantic import BaseModel, field_validator

# ═══════════════════════════════════════════════════════════
# MIXINS VALIDATEURS
# ═══════════════════════════════════════════════════════════


class NomValidatorMixin:
    """Mixin pour valider le champ 'nom'."""

    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        """Valide que le nom n'est pas vide."""
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()


class QuantiteValidatorMixin:
    """Mixin pour valider le champ 'quantite'."""

    @field_validator("quantite")
    @classmethod
    def validate_quantite(cls, v: float) -> float:
        """Valide que la quantité est positive."""
        if v < 0:
            raise ValueError("La quantité ne peut pas être négative")
        return v


class QuantiteStricteValidatorMixin(QuantiteValidatorMixin):
    """Mixin pour valider que la quantité est strictement positive."""

    @field_validator("quantite")
    @classmethod
    def validate_quantite(cls, v: float) -> float:
        """Valide que la quantité est strictement positive."""
        if v < 0:
            raise ValueError("La quantité ne peut pas être négative")
        if v == 0:
            raise ValueError("La quantité doit être supérieure à 0")
        return v


# ═══════════════════════════════════════════════════════════
# CLASSES DE BASE
# ═══════════════════════════════════════════════════════════


class TimestampedResponse(BaseModel):
    """Réponse avec timestamps."""

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class IdentifiedResponse(TimestampedResponse):
    """Réponse avec ID et timestamps."""

    id: int


# ═══════════════════════════════════════════════════════════
# SCHÉMAS UTILITAIRES
# ═══════════════════════════════════════════════════════════


class TypeRepasValidator:
    """Validateur pour le type de repas."""

    # Normalise les variantes accentuées vers les valeurs canoniques sans accents.
    # Garantit que la DB stocke toujours la forme sans accent attendue par le frontend.
    _NORMALISATION: dict[str, str] = {
        "petit_déjeuner": "petit_dejeuner",
        "déjeuner": "dejeuner",
        "dîner": "diner",
        "goûter": "gouter",
    }

    TYPES_VALIDES = [
        "petit_dejeuner",
        "dejeuner",
        "diner",
        "gouter",
    ]

    @field_validator("type_repas")
    @classmethod
    def validate_type_repas(cls, v: str) -> str:
        """Valide et normalise le type de repas (retire les accents)."""
        v = cls._NORMALISATION.get(v, v)
        if v not in cls.TYPES_VALIDES:
            raise ValueError(f"Type de repas invalide: {v!r}")
        return v

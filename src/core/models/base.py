"""
Base SQLAlchemy et énumérations communes.

Ce module contient :
- Base SQLAlchemy avec conventions de nommage
- Énumérations partagées (PrioriteEnum, SaisonEnum, etc.)
- Helper pour récupérer les valeurs d'enum
"""

import enum
from datetime import UTC, datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


def utc_now() -> datetime:
    """Retourne datetime UTC aware (remplace datetime.utcnow déprécié)."""
    return datetime.now(UTC)


# ═══════════════════════════════════════════════════════════
# BASE SQLALCHEMY
# ═══════════════════════════════════════════════════════════

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy."""

    metadata = metadata


# ═══════════════════════════════════════════════════════════
# ÉNUMÉRATIONS
# ═══════════════════════════════════════════════════════════


class PrioriteEnum(enum.StrEnum):
    """Niveaux de priorité utilisés dans plusieurs modèles."""

    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"


class SaisonEnum(enum.StrEnum):
    """Saisons pour les recettes et le jardinage."""

    PRINTEMPS = "printemps"
    ETE = "été"
    AUTOMNE = "automne"
    HIVER = "hiver"
    TOUTE_ANNEE = "toute_année"


class TypeRepasEnum(enum.StrEnum):
    """Types de repas pour le planning."""

    PETIT_DEJEUNER = "petit_déjeuner"
    DEJEUNER = "déjeuner"
    DINER = "dîner"
    GOUTER = "goûter"


class TypeVersionRecetteEnum(enum.StrEnum):
    """Types de versions de recettes."""

    STANDARD = "standard"
    BEBE = "bébé"
    BATCH_COOKING = "batch_cooking"

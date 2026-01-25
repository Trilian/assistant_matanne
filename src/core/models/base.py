"""
Base SQLAlchemy et énumérations communes.

Ce module contient :
- Base SQLAlchemy avec conventions de nommage
- Énumérations partagées (PrioriteEnum, SaisonEnum, etc.)
- Helper pour récupérer les valeurs d'enum
"""

import enum
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

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


class PrioriteEnum(str, enum.Enum):
    """Niveaux de priorité utilisés dans plusieurs modèles."""
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"


class SaisonEnum(str, enum.Enum):
    """Saisons pour les recettes et le jardinage."""
    PRINTEMPS = "printemps"
    ETE = "été"
    AUTOMNE = "automne"
    HIVER = "hiver"
    TOUTE_ANNEE = "toute_année"


class TypeRepasEnum(str, enum.Enum):
    """Types de repas pour le planning."""
    PETIT_DEJEUNER = "petit_déjeuner"
    DEJEUNER = "déjeuner"
    DINER = "dîner"
    GOUTER = "goûter"


class TypeVersionRecetteEnum(str, enum.Enum):
    """Types de versions de recettes."""
    STANDARD = "standard"
    BEBE = "bébé"
    BATCH_COOKING = "batch_cooking"


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def obtenir_valeurs_enum(enum_class: type[enum.Enum]) -> list[str]:
    """Récupère toutes les valeurs d'un enum.
    
    Args:
        enum_class: Classe d'énumération
        
    Returns:
        Liste des valeurs de l'enum
        
    Example:
        >>> obtenir_valeurs_enum(PrioriteEnum)
        ['basse', 'moyenne', 'haute']
    """
    return [e.value for e in enum_class]

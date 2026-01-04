"""
Models Base - Base SQLAlchemy et énumérations communes.

Ce module définit la base déclarative pour tous les modèles
ainsi que les énumérations utilisées dans toute l'application.
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
import enum


# ═══════════════════════════════════════════════════════════
# BASE SQLALCHEMY
# ═══════════════════════════════════════════════════════════

# Convention de nommage pour les contraintes
# (améliore la compatibilité avec Alembic/migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


# ═══════════════════════════════════════════════════════════
# ÉNUMÉRATIONS COMMUNES
# ═══════════════════════════════════════════════════════════

class PrioriteEnum(str, enum.Enum):
    """
    Niveaux de priorité.

    Utilisé pour : courses, projets, tâches, notifications.
    """
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"
    URGENTE = "urgente"  # Seulement pour projets


class StatutEnum(str, enum.Enum):
    """
    Statuts génériques pour entités avec workflow.

    Utilisé pour : projets, tâches, routines.
    """
    A_FAIRE = "à faire"
    EN_COURS = "en cours"
    TERMINE = "terminé"
    ANNULE = "annulé"


class HumeurEnum(str, enum.Enum):
    """
    Niveaux d'humeur avec emojis.

    Utilisé pour : suivi bien-être famille.
    """
    BIEN = "😊 Bien"
    MOYEN = "😐 Moyen"
    MAL = "😞 Mal"


class TypeVersionRecetteEnum(str, enum.Enum):
    """
    Types de versions adaptées de recettes.

    Utilisé pour : versions recettes (bébé, batch cooking).
    """
    STANDARD = "standard"
    BEBE = "bébé"
    BATCH_COOKING = "batch_cooking"


class SaisonEnum(str, enum.Enum):
    """
    Saisons pour recettes.

    Utilisé pour : filtrage et suggestion de recettes.
    """
    PRINTEMPS = "printemps"
    ETE = "été"
    AUTOMNE = "automne"
    HIVER = "hiver"
    TOUTE_ANNEE = "toute_année"


class TypeRepasEnum(str, enum.Enum):
    """
    Types de repas dans une journée.

    Utilisé pour : recettes, planning hebdomadaire.
    """
    PETIT_DEJEUNER = "petit_déjeuner"
    DEJEUNER = "déjeuner"
    DINER = "dîner"
    GOUTER = "goûter"
    BEBE = "bébé"  # Repas spécifique bébé


# ═══════════════════════════════════════════════════════════
# HELPERS POUR ENUMS
# ═══════════════════════════════════════════════════════════

def obtenir_valeurs_enum(enum_class: type[enum.Enum]) -> list[str]:
    """
    Récupère toutes les valeurs d'un enum.

    Args:
        enum_class: Classe d'énumération

    Returns:
        Liste des valeurs

    Example:
        >>> obtenir_valeurs_enum(PrioriteEnum)
        ['basse', 'moyenne', 'haute', 'urgente']
    """
    return [e.value for e in enum_class]


def valider_valeur_enum(valeur: str, enum_class: type[enum.Enum]) -> bool:
    """
    Vérifie si une valeur appartient à un enum.

    Args:
        valeur: Valeur à vérifier
        enum_class: Classe d'énumération

    Returns:
        True si valide

    Example:
        >>> valider_valeur_enum("haute", PrioriteEnum)
        True
    """
    return valeur in obtenir_valeurs_enum(enum_class)


def obtenir_enum_depuis_valeur(valeur: str, enum_class: type[enum.Enum]) -> enum.Enum:
    """
    Récupère un membre d'enum depuis sa valeur.

    Args:
        valeur: Valeur recherchée
        enum_class: Classe d'énumération

    Returns:
        Membre de l'enum

    Raises:
        ValueError: Si la valeur n'existe pas

    Example:
        >>> obtenir_enum_depuis_valeur("haute", PrioriteEnum)
        <PrioriteEnum.HAUTE: 'haute'>
    """
    for membre in enum_class:
        if membre.value == valeur:
            return membre
    raise ValueError(f"Valeur '{valeur}' introuvable dans {enum_class.__name__}")
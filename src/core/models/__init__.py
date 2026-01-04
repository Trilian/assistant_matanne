"""
Models - Modèles SQLAlchemy de l'application.

Ce package centralise tous les modèles de base de données organisés par domaine.

Structure:
    - base.py: Base SQLAlchemy et enums communs
    - cuisine.py: Modèles Recettes, Inventaire, Courses (refactorisés)
    - legacy.py: Modèles Famille, Maison, Planning (inchangés pour l'instant)
"""

# Base SQLAlchemy et Enums
from .base import Base, metadata

# Enums
from .base import (
    PrioriteEnum,
    StatutEnum,
    HumeurEnum,
    TypeVersionRecetteEnum,
    SaisonEnum,
    TypeRepasEnum
)

# Modèles Cuisine (refactorisés)
from .cuisine import (
    Ingredient,
    Recette,
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
    ArticleInventaire,
    ArticleCourses
)

# Modèles Legacy (non refactorisés)
from .legacy import (
    # Planning
    PlanningHebdomadaire,
    RepasPlanning,
    ConfigPlanningUtilisateur,

    # Famille
    ProfilEnfant,
    EntreeBienEtre,
    Routine,
    TacheRoutine,

    # Maison
    Projet,
    TacheProjet,
    ElementJardin,
    LogJardin,

    # Calendrier
    EvenementCalendrier,

    # Utilisateurs
    Utilisateur,
    ProfilUtilisateur,
    Notification
)

__all__ = [
    # Base
    "Base",
    "metadata",

    # Enums
    "PrioriteEnum",
    "StatutEnum",
    "HumeurEnum",
    "TypeVersionRecetteEnum",
    "SaisonEnum",
    "TypeRepasEnum",

    # Cuisine
    "Ingredient",
    "Recette",
    "RecetteIngredient",
    "EtapeRecette",
    "VersionRecette",
    "ArticleInventaire",
    "ArticleCourses",

    # Planning
    "PlanningHebdomadaire",
    "RepasPlanning",
    "ConfigPlanningUtilisateur",

    # Famille
    "ProfilEnfant",
    "EntreeBienEtre",
    "Routine",
    "TacheRoutine",

    # Maison
    "Projet",
    "TacheProjet",
    "ElementJardin",
    "LogJardin",

    # Calendrier
    "EvenementCalendrier",

    # Utilisateurs
    "Utilisateur",
    "ProfilUtilisateur",
    "Notification",
]
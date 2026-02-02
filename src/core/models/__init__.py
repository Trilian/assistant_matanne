"""
Models - Point d'entrée unifié pour tous les modèles SQLAlchemy.

Architecture modulaire :
- base.py      : Base, MetaData, Enums
- recettes.py  : Recette, Ingredient, EtapeRecette, etc.
- inventaire.py: ArticleInventaire, HistoriqueInventaire
- courses.py   : ArticleCourses, ModeleCourses
- planning.py  : Planning, Repas, CalendarEvent
- famille.py   : ChildProfile, Milestone, FamilyActivity, etc.
- sante.py     : HealthRoutine, HealthObjective, HealthEntry
- maison.py    : Project, Routine, GardenItem, etc.

Usage:
    from src.core.models import Recette, Ingredient, Planning
    # ou
    from src.core.models import Base, metadata
"""

# Base et énumérations
from .base import (
    Base,
    metadata,
    PrioriteEnum,
    SaisonEnum,
    TypeRepasEnum,
    TypeVersionRecetteEnum,
    obtenir_valeurs_enum,
)

# Recettes et cuisine
from .recettes import (
    Ingredient,
    Recette,
    Recipe,  # Alias
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
    HistoriqueRecette,
    BatchMeal,
)

# Inventaire
from .inventaire import (
    ArticleInventaire,
    HistoriqueInventaire,
)

# Courses
from .courses import (
    ArticleCourses,
    ModeleCourses,
    ArticleModele,
)

# Planning et calendrier
from .planning import (
    Planning,
    Repas,
    CalendarEvent,
)

# Famille et bien-être
from .famille import (
    ChildProfile,
    WellbeingEntry,
    Milestone,
    FamilyActivity,
    FamilyBudget,
    ShoppingItem,
)

# Santé
from .sante import (
    HealthRoutine,
    HealthObjective,
    HealthEntry,
)

# Maison (projets, routines, jardin)
from .maison import (
    Project,
    ProjectTask,
    Routine,
    RoutineTask,
    GardenItem,
    GardenLog,
)

# Nouvelles fonctionnalités (budget étendu, météo, calendrier, notifications)
from .nouveaux import (
    Depense,
    BudgetMensuelDB,
    AlerteMeteo,
    ConfigMeteo,
    Backup,
    CalendrierExterne,
    EvenementCalendrier,
    PushSubscription,
    NotificationPreference,
    # Enums
    CategorieDepenseDB,
    RecurrenceType,
    NiveauAlerte,
    TypeAlerteMeteo,
    CalendarProvider,
    SyncDirection,
)

# Jeux (Paris sportifs & Loto)
from .jeux import (
    Equipe,
    Match,
    PariSportif,
    TirageLoto,
    GrilleLoto,
    StatistiquesLoto,
    HistoriqueJeux,
    # Enums
    ResultatMatchEnum,
    StatutPariEnum,
    TypePariEnum,
    ChampionnatEnum,
)

# Batch Cooking
from .batch_cooking import (
    ConfigBatchCooking,
    SessionBatchCooking,
    EtapeBatchCooking,
    PreparationBatch,
    # Enums
    StatutSessionEnum,
    StatutEtapeEnum,
    TypeRobotEnum,
    LocalisationStockageEnum,
)

# Préférences utilisateur et apprentissage IA (NOUVEAU)
from .user_preferences import (
    UserPreference,
    RecipeFeedback,
    OpenFoodFactsCache,
    ExternalCalendarConfig,
    FeedbackType,
    CalendarProvider as CalendarProviderNew,
)

# Utilisateurs et Garmin (NOUVEAU)
from .users import (
    UserProfile,
    GarminToken,
    GarminActivity,
    GarminDailySummary,
    FoodLog,
    WeekendActivity,
    FamilyPurchase,
    # Enums
    GarminActivityType,
    PurchaseCategory,
    PurchasePriority,
)

# Maison étendu (meubles, dépenses, éco, jardin zones) (NOUVEAU)
from .maison_extended import (
    Furniture,
    HouseExpense,
    EcoAction,
    GardenZone,
    MaintenanceTask,
    HouseStock,
    # Enums
    FurnitureStatus,
    FurniturePriority,
    ExpenseCategory,
    GardenZoneType,
    EcoActionType,
    RoomType,
)


# Export explicite de tous les symboles
__all__ = [
    # Base
    "Base",
    "metadata",
    "PrioriteEnum",
    "SaisonEnum",
    "TypeRepasEnum",
    "TypeVersionRecetteEnum",
    "obtenir_valeurs_enum",
    # Recettes
    "Ingredient",
    "Recette",
    "Recipe",
    "RecetteIngredient",
    "EtapeRecette",
    "VersionRecette",
    "HistoriqueRecette",
    "BatchMeal",
    # Inventaire
    "ArticleInventaire",
    "HistoriqueInventaire",
    # Courses
    "ArticleCourses",
    "ModeleCourses",
    "ArticleModele",
    # Planning
    "Planning",
    "Repas",
    "CalendarEvent",
    # Famille
    "ChildProfile",
    "WellbeingEntry",
    "Milestone",
    "FamilyActivity",
    "FamilyBudget",
    "ShoppingItem",
    # Santé
    "HealthRoutine",
    "HealthObjective",
    "HealthEntry",
    # Maison
    "Project",
    "ProjectTask",
    "Routine",
    "RoutineTask",
    "GardenItem",
    "GardenLog",
    # Nouvelles fonctionnalités
    "Depense",
    "BudgetMensuelDB",
    "AlerteMeteo",
    "ConfigMeteo",
    "Backup",
    "CalendrierExterne",
    "EvenementCalendrier",
    "PushSubscription",
    "NotificationPreference",
    # Enums nouveaux
    "CategorieDepenseDB",
    "RecurrenceType",
    "NiveauAlerte",
    "TypeAlerteMeteo",
    "CalendarProvider",
    "SyncDirection",
    # Jeux
    "Equipe",
    "Match",
    "PariSportif",
    "TirageLoto",
    "GrilleLoto",
    "StatistiquesLoto",
    "HistoriqueJeux",
    "ResultatMatchEnum",
    "StatutPariEnum",
    "TypePariEnum",
    "ChampionnatEnum",
    # Batch Cooking
    "ConfigBatchCooking",
    "SessionBatchCooking",
    "EtapeBatchCooking",
    "PreparationBatch",
    "StatutSessionEnum",
    "StatutEtapeEnum",
    "TypeRobotEnum",
    "LocalisationStockageEnum",
    # Préférences utilisateur
    "UserPreference",
    "RecipeFeedback",
    "OpenFoodFactsCache",
    "ExternalCalendarConfig",
    "FeedbackType",
    # Utilisateurs et Garmin (NOUVEAU)
    "UserProfile",
    "GarminToken",
    "GarminActivity",
    "GarminDailySummary",
    "FoodLog",
    "WeekendActivity",
    "FamilyPurchase",
    "GarminActivityType",
    "PurchaseCategory",
    "PurchasePriority",
    # Maison étendu (NOUVEAU)
    "Furniture",
    "HouseExpense",
    "EcoAction",
    "GardenZone",
    "MaintenanceTask",
    "HouseStock",
    "FurnitureStatus",
    "FurniturePriority",
    "ExpenseCategory",
    "GardenZoneType",
    "EcoActionType",
    "RoomType",
]

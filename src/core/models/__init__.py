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

Usage recommandé par domaine (imports explicites):
    # Recettes
    from src.core.models.recettes import Recette, Ingredient, EtapeRecette
    # Planning
    from src.core.models.planning import Planning, Repas, CalendarEvent
    # Famille
    from src.core.models.famille import ChildProfile, Milestone
    # Santé
    from src.core.models.sante import HealthRoutine, HealthEntry
    # Courses
    from src.core.models.courses import ArticleCourses, ListeCourses

Usage général (tous les modèles):
    from src.core.models import Recette, Ingredient, Planning
    from src.core.models import Base, metadata
"""

# Base et énumérations
from .base import (
    Base,
    PrioriteEnum,
    SaisonEnum,
    TypeRepasEnum,
    TypeVersionRecetteEnum,
    metadata,
    utc_now,
)

# Batch Cooking
from .batch_cooking import (
    ConfigBatchCooking,
    EtapeBatchCooking,
    LocalisationStockageEnum,
    PreparationBatch,
    SessionBatchCooking,
    StatutEtapeEnum,
    # Enums
    StatutSessionEnum,
    TypeRobotEnum,
)

# Calendrier externe
from .calendrier import (
    # Enums
    CalendarProvider,
    CalendrierExterne,
    EvenementCalendrier,
    SyncDirection,
)

# Courses
from .courses import (
    ArticleCourses,
    ArticleModele,
    ListeCourses,
    ModeleCourses,
)

# Famille et bien-être
from .famille import (
    ChildProfile,
    FamilyActivity,
    FamilyBudget,
    Milestone,
    ShoppingItem,
    WellbeingEntry,
)

# Finances et budget
from .finances import (
    BudgetMensuelDB,
    # Enums
    CategorieDepenseDB,
    Depense,
    ExpenseCategory,
    HouseExpense,
    RecurrenceType,
)

# Habitat (meubles, stocks, entretien, éco)
from .habitat import (
    EcoAction,
    EcoActionType,
    Furniture,
    FurniturePriority,
    # Enums
    FurnitureStatus,
    HouseStock,
    MaintenanceTask,
    RoomType,
)

# Inventaire
from .inventaire import (
    ArticleInventaire,
    HistoriqueInventaire,
)

# Jardin et météo
from .jardin import (
    AlerteMeteo,
    ConfigMeteo,
    # Enums
    NiveauAlerte,
    TypeAlerteMeteo,
)

# Jeux (Paris sportifs & Loto)
from .jeux import (
    AlerteJeux,
    ChampionnatEnum,
    ConfigurationJeux,
    Equipe,
    GrilleLoto,
    HistoriqueJeux,
    Match,
    PariSportif,
    # Enums
    ResultatMatchEnum,
    SerieJeux,
    StatistiquesLoto,
    StatutPariEnum,
    TirageLoto,
    TypeJeuEnum,
    TypeMarcheParisEnum,
    TypePariEnum,
)

# Maison (projets, routines, jardin)
from .maison import (
    GardenItem,
    GardenLog,
    Project,
    ProjectTask,
    Routine,
    RoutineTask,
)

# Notifications
from .notifications import (
    NotificationPreference,
    PushSubscription,
)

# Planning et calendrier
from .planning import (
    CalendarEvent,
    Planning,
    Repas,
    TemplateItem,
    TemplateSemaine,
)

# Recettes et cuisine
from .recettes import (
    BatchMeal,
    EtapeRecette,
    HistoriqueRecette,
    Ingredient,
    Recette,
    RecetteIngredient,
    VersionRecette,
)

# Santé
from .sante import (
    HealthEntry,
    HealthObjective,
    HealthRoutine,
)

# Système
from .systeme import (
    ActionHistory,
    Backup,
)

# Temps d'entretien et jardin
from .temps_entretien import (
    ActionPlante,
    CoutTravaux,
    LogStatutObjet,
    ObjetMaison,
    PieceMaison,
    PlanJardin,
    PlanteJardin,
    PrioriteRemplacement,
    # Modèles
    SessionTravail,
    StatutObjet,
    # Enums
    TypeActiviteEntretien,
    TypeModificationPiece,
    VersionPiece,
    ZoneJardin,
)

# Préférences utilisateur et apprentissage IA (NOUVEAU)
from .user_preferences import (
    ExternalCalendarConfig,
    FeedbackType,
    OpenFoodFactsCache,
    RecipeFeedback,
    UserPreference,
)

# Utilisateurs et Garmin (NOUVEAU)
from .users import (
    FamilyPurchase,
    FoodLog,
    GarminActivity,
    # Enums
    GarminActivityType,
    GarminDailySummary,
    GarminToken,
    PurchaseCategory,
    PurchasePriority,
    UserProfile,
    WeekendActivity,
)

# Export explicite de tous les symboles
__all__ = [
    # Base
    "Base",
    "metadata",
    "utc_now",
    "PrioriteEnum",
    "SaisonEnum",
    "TypeRepasEnum",
    "TypeVersionRecetteEnum",
    # Recettes
    "Ingredient",
    "Recette",
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
    "ListeCourses",
    "ModeleCourses",
    "ArticleModele",
    # Planning
    "Planning",
    "Repas",
    "CalendarEvent",
    "TemplateSemaine",
    "TemplateItem",
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
    # Finances
    "Depense",
    "BudgetMensuelDB",
    "HouseExpense",
    "CategorieDepenseDB",
    "RecurrenceType",
    "ExpenseCategory",
    # Jardin
    "AlerteMeteo",
    "ConfigMeteo",
    "NiveauAlerte",
    "TypeAlerteMeteo",
    # Calendrier
    "CalendrierExterne",
    "EvenementCalendrier",
    "CalendarProvider",
    "SyncDirection",
    # Notifications
    "PushSubscription",
    "NotificationPreference",
    # Système
    "Backup",
    "ActionHistory",
    # Jeux
    "Equipe",
    "Match",
    "PariSportif",
    "TirageLoto",
    "GrilleLoto",
    "StatistiquesLoto",
    "HistoriqueJeux",
    "SerieJeux",
    "AlerteJeux",
    "ConfigurationJeux",
    "ResultatMatchEnum",
    "StatutPariEnum",
    "TypePariEnum",
    "ChampionnatEnum",
    "TypeJeuEnum",
    "TypeMarcheParisEnum",
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
    # Habitat
    "Furniture",
    "HouseStock",
    "MaintenanceTask",
    "EcoAction",
    "FurnitureStatus",
    "FurniturePriority",
    "EcoActionType",
    "RoomType",
    # Temps d'entretien et jardin
    "TypeActiviteEntretien",
    "TypeModificationPiece",
    "StatutObjet",
    "PrioriteRemplacement",
    "SessionTravail",
    "VersionPiece",
    "CoutTravaux",
    "LogStatutObjet",
    "PieceMaison",
    "ObjetMaison",
    "ZoneJardin",
    "PlanteJardin",
    "PlanJardin",
    "ActionPlante",
]

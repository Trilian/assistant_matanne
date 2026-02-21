"""
Models - Point d'entrée unifié pour tous les modèles SQLAlchemy.

Architecture modulaire avec chargement paresseux (PEP 562).
Seuls ``Base`` et ``metadata`` sont chargés eagerly (nécessaires
pour la création de tables et les migrations).

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

Usage général (chargement lazy à la demande):
    from src.core.models import Recette, Ingredient, Planning
    from src.core.models import Base, metadata
"""

from __future__ import annotations

import importlib
from typing import Any

# ═══════════════════════════════════════════════════════════
# EAGER: Base & metadata — requis pour la création de tables
# ═══════════════════════════════════════════════════════════
from .base import (
    Base,
    PrioriteEnum,
    SaisonEnum,
    TypeRepasEnum,
    TypeVersionRecetteEnum,
    metadata,
    utc_now,
)

# ═══════════════════════════════════════════════════════════
# LAZY: Mapping symbole → (sous-module, nom_dans_module)
# ═══════════════════════════════════════════════════════════
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Batch Cooking
    "ConfigBatchCooking": (".batch_cooking", "ConfigBatchCooking"),
    "EtapeBatchCooking": (".batch_cooking", "EtapeBatchCooking"),
    "LocalisationStockageEnum": (".batch_cooking", "LocalisationStockageEnum"),
    "PreparationBatch": (".batch_cooking", "PreparationBatch"),
    "SessionBatchCooking": (".batch_cooking", "SessionBatchCooking"),
    "StatutEtapeEnum": (".batch_cooking", "StatutEtapeEnum"),
    "StatutSessionEnum": (".batch_cooking", "StatutSessionEnum"),
    "TypeRobotEnum": (".batch_cooking", "TypeRobotEnum"),
    # Calendrier externe
    "CalendarProvider": (".calendrier", "CalendarProvider"),
    "CalendrierExterne": (".calendrier", "CalendrierExterne"),
    "EvenementCalendrier": (".calendrier", "EvenementCalendrier"),
    "SyncDirection": (".calendrier", "SyncDirection"),
    # Courses
    "ArticleCourses": (".courses", "ArticleCourses"),
    "ArticleModele": (".courses", "ArticleModele"),
    "ListeCourses": (".courses", "ListeCourses"),
    "ModeleCourses": (".courses", "ModeleCourses"),
    # Famille
    "ChildProfile": (".famille", "ChildProfile"),
    "FamilyActivity": (".famille", "FamilyActivity"),
    "FamilyBudget": (".famille", "FamilyBudget"),
    "Milestone": (".famille", "Milestone"),
    "ShoppingItem": (".famille", "ShoppingItem"),
    "WellbeingEntry": (".famille", "WellbeingEntry"),
    # Finances
    "BudgetMensuelDB": (".finances", "BudgetMensuelDB"),
    "CategorieDepenseDB": (".finances", "CategorieDepenseDB"),
    "Depense": (".finances", "Depense"),
    "ExpenseCategory": (".finances", "ExpenseCategory"),
    "HouseExpense": (".finances", "HouseExpense"),
    "RecurrenceType": (".finances", "RecurrenceType"),
    # Habitat
    "EcoAction": (".habitat", "EcoAction"),
    "EcoActionType": (".habitat", "EcoActionType"),
    "Furniture": (".habitat", "Furniture"),
    "FurniturePriority": (".habitat", "FurniturePriority"),
    "FurnitureStatus": (".habitat", "FurnitureStatus"),
    "HouseStock": (".habitat", "HouseStock"),
    "MaintenanceTask": (".habitat", "MaintenanceTask"),
    "RoomType": (".habitat", "RoomType"),
    # Inventaire
    "ArticleInventaire": (".inventaire", "ArticleInventaire"),
    "HistoriqueInventaire": (".inventaire", "HistoriqueInventaire"),
    # Jardin / Météo
    "AlerteMeteo": (".jardin", "AlerteMeteo"),
    "ConfigMeteo": (".jardin", "ConfigMeteo"),
    "NiveauAlerte": (".jardin", "NiveauAlerte"),
    "TypeAlerteMeteo": (".jardin", "TypeAlerteMeteo"),
    # Jeux
    "AlerteJeux": (".jeux", "AlerteJeux"),
    "ChampionnatEnum": (".jeux", "ChampionnatEnum"),
    "ConfigurationJeux": (".jeux", "ConfigurationJeux"),
    "Equipe": (".jeux", "Equipe"),
    "GrilleLoto": (".jeux", "GrilleLoto"),
    "HistoriqueJeux": (".jeux", "HistoriqueJeux"),
    "Match": (".jeux", "Match"),
    "PariSportif": (".jeux", "PariSportif"),
    "ResultatMatchEnum": (".jeux", "ResultatMatchEnum"),
    "SerieJeux": (".jeux", "SerieJeux"),
    "StatistiquesLoto": (".jeux", "StatistiquesLoto"),
    "StatutPariEnum": (".jeux", "StatutPariEnum"),
    "TirageLoto": (".jeux", "TirageLoto"),
    "TypeJeuEnum": (".jeux", "TypeJeuEnum"),
    "TypeMarcheParisEnum": (".jeux", "TypeMarcheParisEnum"),
    "TypePariEnum": (".jeux", "TypePariEnum"),
    # Maison
    "GardenItem": (".maison", "GardenItem"),
    "GardenLog": (".maison", "GardenLog"),
    "Project": (".maison", "Project"),
    "ProjectTask": (".maison", "ProjectTask"),
    "Routine": (".maison", "Routine"),
    "RoutineTask": (".maison", "RoutineTask"),
    # Notifications
    "NotificationPreference": (".notifications", "NotificationPreference"),
    "PushSubscription": (".notifications", "PushSubscription"),
    # Planning
    "CalendarEvent": (".planning", "CalendarEvent"),
    "Planning": (".planning", "Planning"),
    "Repas": (".planning", "Repas"),
    "TemplateItem": (".planning", "TemplateItem"),
    "TemplateSemaine": (".planning", "TemplateSemaine"),
    # Recettes
    "BatchMeal": (".recettes", "BatchMeal"),
    "EtapeRecette": (".recettes", "EtapeRecette"),
    "HistoriqueRecette": (".recettes", "HistoriqueRecette"),
    "Ingredient": (".recettes", "Ingredient"),
    "Recette": (".recettes", "Recette"),
    "RecetteIngredient": (".recettes", "RecetteIngredient"),
    "VersionRecette": (".recettes", "VersionRecette"),
    # Santé
    "HealthEntry": (".sante", "HealthEntry"),
    "HealthObjective": (".sante", "HealthObjective"),
    "HealthRoutine": (".sante", "HealthRoutine"),
    # Système
    "ActionHistory": (".systeme", "ActionHistory"),
    "Backup": (".systeme", "Backup"),
    # Temps d'entretien et jardin
    "ActionPlante": (".temps_entretien", "ActionPlante"),
    "CoutTravaux": (".temps_entretien", "CoutTravaux"),
    "LogStatutObjet": (".temps_entretien", "LogStatutObjet"),
    "ObjetMaison": (".temps_entretien", "ObjetMaison"),
    "PieceMaison": (".temps_entretien", "PieceMaison"),
    "PlanJardin": (".temps_entretien", "PlanJardin"),
    "PlanteJardin": (".temps_entretien", "PlanteJardin"),
    "PrioriteRemplacement": (".temps_entretien", "PrioriteRemplacement"),
    "SessionTravail": (".temps_entretien", "SessionTravail"),
    "StatutObjet": (".temps_entretien", "StatutObjet"),
    "TypeActiviteEntretien": (".temps_entretien", "TypeActiviteEntretien"),
    "TypeModificationPiece": (".temps_entretien", "TypeModificationPiece"),
    "VersionPiece": (".temps_entretien", "VersionPiece"),
    "ZoneJardin": (".temps_entretien", "ZoneJardin"),
    # Préférences utilisateur
    "ExternalCalendarConfig": (".user_preferences", "ExternalCalendarConfig"),
    "FeedbackType": (".user_preferences", "FeedbackType"),
    "OpenFoodFactsCache": (".user_preferences", "OpenFoodFactsCache"),
    "RecipeFeedback": (".user_preferences", "RecipeFeedback"),
    "UserPreference": (".user_preferences", "UserPreference"),
    # Utilisateurs et Garmin
    "FamilyPurchase": (".users", "FamilyPurchase"),
    "FoodLog": (".users", "FoodLog"),
    "GarminActivity": (".users", "GarminActivity"),
    "GarminActivityType": (".users", "GarminActivityType"),
    "GarminDailySummary": (".users", "GarminDailySummary"),
    "GarminToken": (".users", "GarminToken"),
    "PurchaseCategory": (".users", "PurchaseCategory"),
    "PurchasePriority": (".users", "PurchasePriority"),
    "UserProfile": (".users", "UserProfile"),
    "WeekendActivity": (".users", "WeekendActivity"),
}

# Export explicite de tous les symboles
__all__ = [
    # Base (eager)
    "Base",
    "metadata",
    "utc_now",
    "PrioriteEnum",
    "SaisonEnum",
    "TypeRepasEnum",
    "TypeVersionRecetteEnum",
    # Helper
    "charger_tous_modeles",
    # Tous les symboles lazy
    *_LAZY_IMPORTS.keys(),
]


# ═══════════════════════════════════════════════════════════
# SOUS-MODULES à charger pour enregistrer tous les modèles
# ═══════════════════════════════════════════════════════════
_MODEL_MODULES = (
    ".batch_cooking",
    ".calendrier",
    ".courses",
    ".famille",
    ".finances",
    ".habitat",
    ".inventaire",
    ".jardin",
    ".jeux",
    ".maison",
    ".notifications",
    ".planning",
    ".recettes",
    ".sante",
    ".systeme",
    ".temps_entretien",
    ".user_preferences",
    ".users",
)


def charger_tous_modeles() -> None:
    """Force le chargement de tous les fichiers modèles.

    Nécessaire avant ``Base.metadata.create_all()`` pour que
    SQLAlchemy connaisse toutes les tables.

    Usage::

        from src.core.models import charger_tous_modeles, Base
        charger_tous_modeles()
        Base.metadata.create_all(bind=engine)
    """
    for mod in _MODEL_MODULES:
        importlib.import_module(mod, __name__)


def __getattr__(name: str) -> Any:
    """Chargement paresseux des modèles (PEP 562)."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path, __name__)
        value = getattr(module, attr_name)
        # Cache dans le namespace du package pour éviter les appels répétés
        globals()[name] = value
        return value
    raise AttributeError(f"module 'src.core.models' has no attribute {name!r}")

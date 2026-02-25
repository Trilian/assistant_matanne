"""
Models - Point d'entrée unifié pour tous les modèles SQLAlchemy.

Architecture modulaire avec chargement paresseux (PEP 562).
Seuls ``Base`` et ``metadata`` sont chargés eagerly (nécessaires
pour la création de tables et les migrations).

Usage recommandé par domaine (imports explicites):
    # Recettes
    from src.core.models.recettes import Recette, Ingredient, EtapeRecette
    # Planning
    from src.core.models.planning import Planning, Repas, EvenementPlanning
    # Famille
    from src.core.models.famille import ProfilEnfant, Jalon
    # Santé
    from src.core.models.sante import RoutineSante, EntreeSante
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
from .mixins import (
    CreeLeMixin,
    TimestampMixin,
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
    "FournisseurCalendrier": (".calendrier", "FournisseurCalendrier"),
    "CalendrierExterne": (".calendrier", "CalendrierExterne"),
    "EvenementCalendrier": (".calendrier", "EvenementCalendrier"),
    "DirectionSync": (".calendrier", "DirectionSync"),
    # Courses
    "ArticleCourses": (".courses", "ArticleCourses"),
    "ArticleModele": (".courses", "ArticleModele"),
    "ListeCourses": (".courses", "ListeCourses"),
    "ModeleCourses": (".courses", "ModeleCourses"),
    # Famille
    "ProfilEnfant": (".famille", "ProfilEnfant"),
    "ActiviteFamille": (".famille", "ActiviteFamille"),
    "BudgetFamille": (".famille", "BudgetFamille"),
    "Jalon": (".famille", "Jalon"),
    "ArticleAchat": (".famille", "ArticleAchat"),
    "EntreeBienEtre": (".famille", "EntreeBienEtre"),
    # Finances
    "BudgetMensuelDB": (".finances", "BudgetMensuelDB"),
    "CategorieDepenseDB": (".finances", "CategorieDepenseDB"),
    "Depense": (".finances", "Depense"),
    "CategorieDepense": (".finances", "CategorieDepense"),
    "DepenseMaison": (".finances", "DepenseMaison"),
    "TypeRecurrence": (".finances", "TypeRecurrence"),
    # Habitat
    "ActionEcologique": (".habitat", "ActionEcologique"),
    "TypeActionEcologique": (".habitat", "TypeActionEcologique"),
    "Meuble": (".habitat", "Meuble"),
    "PrioriteMeuble": (".habitat", "PrioriteMeuble"),
    "StatutMeuble": (".habitat", "StatutMeuble"),
    "StockMaison": (".habitat", "StockMaison"),
    "TacheEntretien": (".habitat", "TacheEntretien"),
    "TypePiece": (".habitat", "TypePiece"),
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
    "ElementJardin": (".maison", "ElementJardin"),
    "JournalJardin": (".maison", "JournalJardin"),
    "Projet": (".maison", "Projet"),
    "Project": (".maison", "Project"),  # Alias rétrocompatibilité
    "TacheProjet": (".maison", "TacheProjet"),
    "Routine": (".maison", "Routine"),
    "TacheRoutine": (".maison", "TacheRoutine"),
    # Notifications
    "PreferenceNotification": (".notifications", "PreferenceNotification"),
    "AbonnementPush": (".notifications", "AbonnementPush"),
    # Planning
    "EvenementPlanning": (".planning", "EvenementPlanning"),
    "Planning": (".planning", "Planning"),
    "Repas": (".planning", "Repas"),
    "ElementTemplate": (".planning", "ElementTemplate"),
    "TemplateSemaine": (".planning", "TemplateSemaine"),
    # Recettes
    "RepasBatch": (".recettes", "RepasBatch"),
    "EtapeRecette": (".recettes", "EtapeRecette"),
    "HistoriqueRecette": (".recettes", "HistoriqueRecette"),
    "Ingredient": (".recettes", "Ingredient"),
    "Recette": (".recettes", "Recette"),
    "RecetteIngredient": (".recettes", "RecetteIngredient"),
    "VersionRecette": (".recettes", "VersionRecette"),
    # Santé
    "EntreeSante": (".sante", "EntreeSante"),
    "ObjectifSante": (".sante", "ObjectifSante"),
    "RoutineSante": (".sante", "RoutineSante"),
    # Système
    "HistoriqueAction": (".systeme", "HistoriqueAction"),
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
    "ConfigCalendrierExterne": (".user_preferences", "ConfigCalendrierExterne"),
    "TypeRetour": (".user_preferences", "TypeRetour"),
    "OpenFoodFactsCache": (".user_preferences", "OpenFoodFactsCache"),
    "RetourRecette": (".user_preferences", "RetourRecette"),
    "PreferenceUtilisateur": (".user_preferences", "PreferenceUtilisateur"),
    # État persistant
    "EtatPersistantDB": (".persistent_state", "EtatPersistantDB"),
    # Utilisateurs et Garmin
    "AchatFamille": (".users", "AchatFamille"),
    "JournalAlimentaire": (".users", "JournalAlimentaire"),
    "ActiviteGarmin": (".users", "ActiviteGarmin"),
    "GarminActivityType": (".users", "GarminActivityType"),
    "ResumeQuotidienGarmin": (".users", "ResumeQuotidienGarmin"),
    "GarminToken": (".users", "GarminToken"),
    "CategorieAchat": (".users", "CategorieAchat"),
    "PrioriteAchat": (".users", "PrioriteAchat"),
    "ProfilUtilisateur": (".users", "ProfilUtilisateur"),
    "ActiviteWeekend": (".users", "ActiviteWeekend"),
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
    ".persistent_state",
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

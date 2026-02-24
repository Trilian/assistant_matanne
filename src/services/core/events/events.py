"""
Événements domaine — Définitions typées des événements métier.

Chaque événement est un dataclass immutable avec des données structurées.
Les services émettent ces événements via le bus pour communiquer
sans couplage direct.

Conventions de nommage:
- "recette.*" : Événements liés aux recettes
- "stock.*" : Événements liés à l'inventaire/stock
- "courses.*" : Événements liés aux courses
- "planning.*" : Événements liés au planning
- "batch_cooking.*" : Événements batch cooking
- "service.*" : Événements système (erreurs, métriques)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS RECETTES
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementRecettePlanifiee:
    """Émis quand une recette est planifiée dans le planning repas."""

    TYPE: str = "recette.planifiee"

    recette_id: int = 0
    recette_nom: str = ""
    date_planification: date | None = None
    repas: str = ""  # "dejeuner", "diner", etc.
    nb_personnes: int = 0


@dataclass(frozen=True, slots=True)
class EvenementRecetteImportee:
    """Émis quand une recette est importée (URL, PDF, CSV)."""

    TYPE: str = "recette.importee"

    recette_id: int = 0
    recette_nom: str = ""
    source: str = ""  # "url", "pdf", "csv", "manual"
    url: str = ""


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS STOCK / INVENTAIRE
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementStockModifie:
    """Émis quand le stock d'un article change."""

    TYPE: str = "stock.modifie"

    article_id: int = 0
    ingredient_nom: str = ""
    ancienne_quantite: float = 0.0
    nouvelle_quantite: float = 0.0
    raison: str = ""  # "consommation", "ajout", "correction", "peremption"
    emplacement: str = ""


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS COURSES
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementCoursesGenerees:
    """Émis quand une liste de courses est générée."""

    TYPE: str = "courses.generees"

    nb_articles: int = 0
    source: str = ""  # "planning", "manuel", "ia", "stock_bas"
    montant_estime: float = 0.0


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS BATCH COOKING
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementBatchCookingTermine:
    """Émis quand une session de batch cooking est terminée."""

    TYPE: str = "batch_cooking.termine"

    session_id: int = 0
    nb_recettes: int = 0
    nb_portions: int = 0
    duree_minutes: int = 0


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS ENTRETIEN / MAISON
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementEntretienRoutineCreee:
    """Émis quand une routine d'entretien est créée."""

    TYPE: str = "entretien.routine_creee"

    nom: str = ""
    categorie: str = ""


@dataclass(frozen=True, slots=True)
class EvenementEntretienSemaineOptimisee:
    """Émis quand la semaine d'entretien est optimisée."""

    TYPE: str = "entretien.semaine_optimisee"

    nb_taches: int = 0
    nb_jours: int = 0


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS FAMILLE
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementActiviteFamille:
    """Émis quand une activité famille est créée/modifiée."""

    TYPE: str = "activites.modifiee"

    activite_id: int = 0
    nom: str = ""
    action: str = ""  # "creee", "modifiee", "supprimee"


@dataclass(frozen=True, slots=True)
class EvenementRoutineModifiee:
    """Émis quand une routine famille est créée/modifiée."""

    TYPE: str = "routines.modifiee"

    routine_id: int = 0
    nom: str = ""
    action: str = ""  # "creee", "modifiee", "supprimee", "tache_ajoutee"


@dataclass(frozen=True, slots=True)
class EvenementWeekendModifie:
    """Émis quand une activité weekend est créée/modifiée."""

    TYPE: str = "weekend.modifie"

    activite_id: int = 0
    nom: str = ""
    action: str = ""  # "creee", "modifiee", "supprimee"


@dataclass(frozen=True, slots=True)
class EvenementAchatFamille:
    """Émis quand un achat famille est ajouté/modifié."""

    TYPE: str = "achats.modifie"

    achat_id: int = 0
    nom: str = ""
    action: str = ""  # "ajoute", "modifie", "supprime"


@dataclass(frozen=True, slots=True)
class EvenementJournalAlimentaire:
    """Émis quand une entrée journal alimentaire est ajoutée."""

    TYPE: str = "food_log.ajoute"

    entree_id: int = 0
    utilisateur_id: int = 0
    action: str = ""  # "ajoute", "supprime"


@dataclass(frozen=True, slots=True)
class EvenementPlanningModifie:
    """Émis quand le planning est modifié."""

    TYPE: str = "planning.modifie"

    planning_id: int = 0
    semaine: str = ""
    action: str = ""  # "cree", "modifie", "supprime"


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS SYSTÈME
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementErreurService:
    """Émis quand une erreur survient dans un service."""

    TYPE: str = "service.error"

    service: str = ""
    method: str = ""
    error_type: str = ""
    message: str = ""
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# REGISTRY — Pour auto-discovery des types d'événements
# ═══════════════════════════════════════════════════════════

REGISTRE_EVENEMENTS: dict[str, type] = {
    "recette.planifiee": EvenementRecettePlanifiee,
    "recette.importee": EvenementRecetteImportee,
    "stock.modifie": EvenementStockModifie,
    "courses.generees": EvenementCoursesGenerees,
    "batch_cooking.termine": EvenementBatchCookingTermine,
    "entretien.routine_creee": EvenementEntretienRoutineCreee,
    "entretien.semaine_optimisee": EvenementEntretienSemaineOptimisee,
    "activites.modifiee": EvenementActiviteFamille,
    "routines.modifiee": EvenementRoutineModifiee,
    "weekend.modifie": EvenementWeekendModifie,
    "achats.modifie": EvenementAchatFamille,
    "food_log.ajoute": EvenementJournalAlimentaire,
    "planning.modifie": EvenementPlanningModifie,
    "service.error": EvenementErreurService,
}


__all__ = [
    # Événements
    "EvenementRecettePlanifiee",
    "EvenementRecetteImportee",
    "EvenementStockModifie",
    "EvenementCoursesGenerees",
    "EvenementBatchCookingTermine",
    "EvenementEntretienRoutineCreee",
    "EvenementEntretienSemaineOptimisee",
    "EvenementActiviteFamille",
    "EvenementRoutineModifiee",
    "EvenementWeekendModifie",
    "EvenementAchatFamille",
    "EvenementJournalAlimentaire",
    "EvenementPlanningModifie",
    "EvenementErreurService",
    # Registry
    "REGISTRE_EVENEMENTS",
]

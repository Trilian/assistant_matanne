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


@dataclass(frozen=True, slots=True)
class EvenementDepenseModifiee:
    """Émis quand une dépense maison est créée/modifiée/supprimée."""

    TYPE: str = "depenses.modifiee"

    depense_id: int = 0
    categorie: str = ""
    montant: float = 0.0
    action: str = ""  # "creee", "modifiee", "supprimee"


@dataclass(frozen=True, slots=True)
class EvenementJardinModifie:
    """Émis quand un élément du jardin est modifié."""

    TYPE: str = "jardin.modifie"

    element_id: int = 0
    nom: str = ""
    action: str = ""  # "plante_ajoutee", "arrosage", "recolte", "supprime"


@dataclass(frozen=True, slots=True)
class EvenementProjetModifie:
    """Émis quand un projet maison est créé/modifié."""

    TYPE: str = "projets.modifie"

    projet_id: int = 0
    nom: str = ""
    action: str = ""  # "cree", "modifie", "archive", "tache_ajoutee"


@dataclass(frozen=True, slots=True)
class EvenementMeubleModifie:
    """Émis quand un meuble (wishlist) est créé/modifié/supprimé."""

    TYPE: str = "meubles.modifie"

    meuble_id: int = 0
    nom: str = ""
    action: str = ""  # "cree", "modifie", "supprime"


@dataclass(frozen=True, slots=True)
class EvenementEcoTipModifie:
    """Émis quand une action écologique est créée/modifiée/supprimée."""

    TYPE: str = "eco_tips.modifie"

    action_id: int = 0
    nom: str = ""
    action: str = ""  # "cree", "modifie", "supprime"


@dataclass(frozen=True, slots=True)
class EvenementCoursesModifiees:
    """Émis quand la liste de courses est modifiée (ajout, suppression, modèle)."""

    TYPE: str = "courses.modifiees"

    nb_articles: int = 0
    action: str = ""  # "articles_ajoutes", "modele_cree", "modele_supprime", "recette_ajoutee"
    source: str = ""  # "ia", "manuel", "recette", "modele"


@dataclass(frozen=True, slots=True)
class EvenementRecetteCreee:
    """Émis quand une recette est créée."""

    TYPE: str = "recette.creee"

    recette_id: int = 0
    nom: str = ""
    type_repas: str = ""
    source: str = ""  # "manual", "ia", "import"


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS BUDGET / SANTÉ
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementBudgetModifie:
    """Émis quand le budget familial est modifié (dépense/budget défini)."""

    TYPE: str = "budget.modifie"

    depense_id: int = 0
    categorie: str = ""
    montant: float = 0.0
    action: str = ""  # "depense_ajoutee", "depense_modifiee", "depense_supprimee", "budget_defini"


@dataclass(frozen=True, slots=True)
class EvenementSanteModifie:
    """Émis quand une entrée santé/fitness est créée/modifiée/supprimée."""

    TYPE: str = "sante.modifie"

    entree_id: int = 0
    type_donnee: str = ""  # "entree", "objectif", "mesure"
    action: str = ""  # "creee", "modifiee", "supprimee"


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS JEUX (LOTO / PARIS)
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementLotoModifie:
    """Émis quand une grille/tirage loto est ajouté/modifié."""

    TYPE: str = "loto.modifie"

    element_id: int = 0
    type_element: str = ""  # "grille", "tirage"
    action: str = ""  # "sauvegardee", "enregistree", "ajoute"


@dataclass(frozen=True, slots=True)
class EvenementParisModifie:
    """Émis quand un pari/match/équipe est ajouté/modifié."""

    TYPE: str = "paris.modifie"

    element_id: int = 0
    type_element: str = ""  # "pari", "equipe", "match", "resultat"
    action: str = ""  # "enregistre", "ajoutee", "resultat_enregistre", "supprime"


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
# ÉVÉNEMENTS JEUX
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementJeuxSyncTerminee:
    """Émis quand une synchronisation jeux (paris/loto) est terminée."""

    TYPE: str = "jeux.sync_terminee"

    domaine: str = ""  # "paris", "loto", "tout"
    nb_elements: int = 0
    nb_alertes: int = 0


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
    "recette.creee": EvenementRecetteCreee,
    "stock.modifie": EvenementStockModifie,
    "courses.generees": EvenementCoursesGenerees,
    "courses.modifiees": EvenementCoursesModifiees,
    "batch_cooking.termine": EvenementBatchCookingTermine,
    "entretien.routine_creee": EvenementEntretienRoutineCreee,
    "entretien.semaine_optimisee": EvenementEntretienSemaineOptimisee,
    "depenses.modifiee": EvenementDepenseModifiee,
    "jardin.modifie": EvenementJardinModifie,
    "projets.modifie": EvenementProjetModifie,
    "meubles.modifie": EvenementMeubleModifie,
    "eco_tips.modifie": EvenementEcoTipModifie,
    "budget.modifie": EvenementBudgetModifie,
    "sante.modifie": EvenementSanteModifie,
    "loto.modifie": EvenementLotoModifie,
    "paris.modifie": EvenementParisModifie,
    "activites.modifiee": EvenementActiviteFamille,
    "routines.modifiee": EvenementRoutineModifiee,
    "weekend.modifie": EvenementWeekendModifie,
    "achats.modifie": EvenementAchatFamille,
    "food_log.ajoute": EvenementJournalAlimentaire,
    "planning.modifie": EvenementPlanningModifie,
    "jeux.sync_terminee": EvenementJeuxSyncTerminee,
    "service.error": EvenementErreurService,
}


__all__ = [
    # Événements
    "EvenementRecettePlanifiee",
    "EvenementRecetteImportee",
    "EvenementRecetteCreee",
    "EvenementStockModifie",
    "EvenementCoursesGenerees",
    "EvenementCoursesModifiees",
    "EvenementBatchCookingTermine",
    "EvenementEntretienRoutineCreee",
    "EvenementEntretienSemaineOptimisee",
    "EvenementDepenseModifiee",
    "EvenementJardinModifie",
    "EvenementProjetModifie",
    "EvenementMeubleModifie",
    "EvenementEcoTipModifie",
    "EvenementBudgetModifie",
    "EvenementSanteModifie",
    "EvenementLotoModifie",
    "EvenementParisModifie",
    "EvenementActiviteFamille",
    "EvenementRoutineModifiee",
    "EvenementWeekendModifie",
    "EvenementAchatFamille",
    "EvenementJournalAlimentaire",
    "EvenementPlanningModifie",
    "EvenementJeuxSyncTerminee",
    "EvenementErreurService",
    # Registry
    "REGISTRE_EVENEMENTS",
]

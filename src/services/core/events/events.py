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
class EvenementJardinRecolte:
    """Émis quand une récolte jardin est validée (Sprint D.1)."""

    TYPE: str = "jardin.recolte"

    element_id: int = 0
    nom: str = ""
    quantite: float = 0.0


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
class EvenementBudgetDepassement:
    """Émis quand une catégorie budgétaire dépasse son seuil (Sprint D.3)."""

    TYPE: str = "budget.depassement"

    categorie: str = ""
    depense: float = 0.0
    budget: float = 0.0
    pourcentage: float = 0.0


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


@dataclass(frozen=True, slots=True)
class EvenementRecetteFeedback:
    """Émis quand un feedback recette utilisateur est enregistré (Sprint D.5)."""

    TYPE: str = "recette.feedback"

    recette_id: int = 0
    user_id: str = ""
    feedback: str = ""  # like/dislike/neutral


@dataclass(frozen=True, slots=True)
class EvenementEnergieAnomalie:
    """Émis quand une anomalie énergie est détectée (Sprint D.2)."""

    TYPE: str = "energie.anomalie"

    nb_alertes: int = 0
    details: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class EvenementInventaireModificationImportante:
    """Émis quand un changement inventaire impacte les courses (Sprint D.4)."""

    TYPE: str = "inventaire.modification_importante"

    nb_articles_impactes: int = 0
    source_declenchement: str = ""


@dataclass(frozen=True, slots=True)
class EvenementContratRenouvellement:
    """Émis quand des contrats arrivent en échéance (Sprint D.6)."""

    TYPE: str = "contrat.renouvellement"

    nb_contrats: int = 0
    nb_garanties: int = 0
    message: str = ""


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


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS PRÉDICTIONS & BRIDGES IA
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementPredictionCourses:
    """Émis quand une liste prédictive de courses est générée (B4.1)."""

    TYPE: str = "prediction.courses_generees"

    nb_articles: int = 0
    source: str = "historique"


@dataclass(frozen=True, slots=True)
class EvenementResumeHebdo:
    """Émis quand le résumé hebdomadaire IA est généré (B4.3)."""

    TYPE: str = "resume.hebdo_genere"

    semaine: str = ""
    nb_sections: int = 0


@dataclass(frozen=True, slots=True)
class EvenementPrevisionBudget:
    """Émis quand une prévision budget est calculée (B4.9)."""

    TYPE: str = "budget.prevision_calculee"

    montant_prevu: float = 0.0
    nb_anomalies: int = 0


@dataclass(frozen=True, slots=True)
class EvenementDiagnosticMaison:
    """Émis quand un diagnostic maison est produit (B4.5)."""

    TYPE: str = "maison.diagnostic"

    type_diagnostic: str = ""  # "photo", "texte"
    probleme: str = ""


@dataclass(frozen=True, slots=True)
class EvenementBridgeRecolteRecettes:
    """Émis quand une récolte jardin génère des suggestions recettes (B5.1)."""

    TYPE: str = "bridge.recolte_recettes"

    nb_recettes_suggerees: int = 0
    ingredients: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class EvenementBridgeMeteoEntretien:
    """Émis quand la météo déclenche des tâches entretien (B5.8)."""

    TYPE: str = "bridge.meteo_entretien"

    nb_taches: int = 0
    condition_meteo: str = ""
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
    "jardin.recolte": EvenementJardinRecolte,
    "projets.modifie": EvenementProjetModifie,
    "meubles.modifie": EvenementMeubleModifie,
    "eco_tips.modifie": EvenementEcoTipModifie,
    "budget.modifie": EvenementBudgetModifie,
    "budget.depassement": EvenementBudgetDepassement,
    "sante.modifie": EvenementSanteModifie,
    "loto.modifie": EvenementLotoModifie,
    "paris.modifie": EvenementParisModifie,
    "activites.modifiee": EvenementActiviteFamille,
    "routines.modifiee": EvenementRoutineModifiee,
    "weekend.modifie": EvenementWeekendModifie,
    "achats.modifie": EvenementAchatFamille,
    "food_log.ajoute": EvenementJournalAlimentaire,
    "planning.modifie": EvenementPlanningModifie,
    "recette.feedback": EvenementRecetteFeedback,
    "energie.anomalie": EvenementEnergieAnomalie,
    "inventaire.modification_importante": EvenementInventaireModificationImportante,
    "contrat.renouvellement": EvenementContratRenouvellement,
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
    "EvenementJardinRecolte",
    "EvenementProjetModifie",
    "EvenementMeubleModifie",
    "EvenementEcoTipModifie",
    "EvenementBudgetModifie",
    "EvenementBudgetDepassement",
    "EvenementSanteModifie",
    "EvenementLotoModifie",
    "EvenementParisModifie",
    "EvenementActiviteFamille",
    "EvenementRoutineModifiee",
    "EvenementWeekendModifie",
    "EvenementAchatFamille",
    "EvenementJournalAlimentaire",
    "EvenementPlanningModifie",
    "EvenementRecetteFeedback",
    "EvenementEnergieAnomalie",
    "EvenementInventaireModificationImportante",
    "EvenementContratRenouvellement",
    "EvenementJeuxSyncTerminee",
    "EvenementErreurService",
    # Registry
    "REGISTRE_EVENEMENTS",
]

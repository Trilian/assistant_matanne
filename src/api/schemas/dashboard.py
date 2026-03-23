"""
Schémas Pydantic pour le tableau de bord.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class StatistiquesRapides(BaseModel):
    """Compteurs rapides pour le dashboard."""

    recettes_total: int = 0
    repas_planifies_semaine: int = 0
    articles_courses: int = 0
    taches_entretien_en_retard: int = 0
    activites_a_venir: int = 0
    stocks_en_alerte: int = 0


class ResumeBudget(BaseModel):
    """Résumé du budget mensuel."""

    total_mois: float = 0.0
    par_categorie: dict[str, float] = Field(default_factory=dict)


class DonneesTableauBord(BaseModel):
    """Réponse agrégée du tableau de bord."""

    statistiques: StatistiquesRapides
    budget_mois: ResumeBudget
    prochaines_activites: list[dict] = Field(default_factory=list)
    alertes: list[dict] = Field(default_factory=list)

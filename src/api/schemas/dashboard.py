"""
Schémas Pydantic pour le tableau de bord.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StatistiquesRapides(BaseModel):
    """Compteurs rapides pour le dashboard."""

    recettes_total: int = 0
    repas_planifies_semaine: int = 0
    articles_courses: int = 0
    taches_entretien_en_retard: int = 0
    activites_a_venir: int = 0
    stocks_en_alerte: int = 0

    model_config = {
        "json_schema_extra": {
            "example": {
                "recettes_total": 186,
                "repas_planifies_semaine": 12,
                "articles_courses": 18,
                "taches_entretien_en_retard": 2,
                "activites_a_venir": 4,
                "stocks_en_alerte": 3,
            }
        }
    }


class ResumeBudget(BaseModel):
    """Résumé du budget mensuel."""

    total_mois: float = 0.0
    par_categorie: dict[str, float] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_mois": 842.5,
                "par_categorie": {"courses": 420.0, "maison": 150.0, "famille": 272.5},
            }
        }
    }


class DonneesTableauBord(BaseModel):
    """Réponse agrégée du tableau de bord."""

    statistiques: StatistiquesRapides
    budget_mois: ResumeBudget
    prochaines_activites: list[dict[str, Any]] = Field(default_factory=list)
    alertes: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "statistiques": {
                    "recettes_total": 186,
                    "repas_planifies_semaine": 12,
                    "articles_courses": 18,
                    "taches_entretien_en_retard": 2,
                    "activites_a_venir": 4,
                    "stocks_en_alerte": 3,
                },
                "budget_mois": {
                    "total_mois": 842.5,
                    "par_categorie": {"courses": 420.0, "maison": 150.0, "famille": 272.5},
                },
                "prochaines_activites": [{"titre": "Vaccin Jules", "date": "2026-04-08"}],
                "alertes": [{"type": "entretien", "message": "Filtre chaudière à vérifier"}],
            }
        }
    }

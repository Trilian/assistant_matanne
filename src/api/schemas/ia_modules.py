"""Schémas API pour les services IA des modules IA."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PredictionConsommationRequest(BaseModel):
    """Requête de prédiction de consommation inventaire."""

    ingredient_nom: str = Field(..., min_length=1, max_length=120)
    stock_actuel_kg: float = Field(..., ge=0)
    historique_achat_mensuel: list[dict[str, Any]] = Field(default_factory=list)


class AnalyseVarietePlanningRequest(BaseModel):
    """Requête d'analyse de variété du planning."""

    planning_repas: list[dict[str, Any]] = Field(..., min_length=1)


class AnalyseImpactsMeteoRequest(BaseModel):
    """Requête d'analyse des impacts météo."""

    previsions_7j: list[dict[str, Any]] = Field(..., min_length=1)
    saison: Literal["printemps", "ete", "automne", "hiver"]


class AnalyseHabitudeRequest(BaseModel):
    """Requête d'analyse d'une habitude."""

    habitude_nom: str = Field(..., min_length=1, max_length=120)
    historique_7j: list[dict[str, Any]] = Field(..., min_length=1)
    description_contexte: str = Field(default="", max_length=500)


class EstimationProjetMaisonRequest(BaseModel):
    """Requête d'estimation de projet maison."""

    projet_description: str = Field(..., min_length=3, max_length=4000)
    surface_m2: float | None = Field(default=None, ge=0)
    type_maison: str = Field(default="maison_2020", max_length=50)
    contraintes: list[str] = Field(default_factory=list)


class AnalyseNutritionPersonneRequest(BaseModel):
    """Requête d'analyse nutritionnelle individuelle."""

    personne_nom: str = Field(..., min_length=1, max_length=120)
    age_ans: int = Field(..., ge=0, le=120)
    sexe: Literal["M", "F"]
    activite_niveau: Literal["sedentaire", "leger", "modere", "actif", "tres_actif"]
    donnees_garmin_semaine: dict[str, Any] | None = None
    recettes_semaine: list[str] = Field(default_factory=list)
    objectif_sante: str = Field(default="maintien", max_length=50)
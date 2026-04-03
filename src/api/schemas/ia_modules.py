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


class DiagnosticPlanteJardinRequest(BaseModel):
    """Requête de diagnostic plante via photo."""

    image_base64: str = Field(..., min_length=16)
    description: str = Field(default="", max_length=1000)


class DiagnosticPlanteJardinResponse(BaseModel):
    """Réponse structurée pour le diagnostic d'une plante."""

    plante_identifiee: str | None = None
    etat: str = "attention"
    problemes_detectes: list[str] = Field(default_factory=list)
    traitements_suggeres: list[str] = Field(default_factory=list)
    confiance: float = Field(default=0.0, ge=0.0, le=1.0)


class BilanMensuelNarratifResponse(BaseModel):
    """Réponse du bilan mensuel narratif Sprint 4."""

    mois: str
    donnees: dict[str, Any] = Field(default_factory=dict)
    synthese_ia: str = ""


class PredictionEnergieResponse(BaseModel):
    """Réponse IA-10: prédiction de consommation énergie + conseils."""

    mois_reference: str
    predictions: dict[str, dict[str, Any]] = Field(default_factory=dict)
    nb_anomalies: int = 0
    score_risque_global: float = 0.0
    conseils: list[str] = Field(default_factory=list)


class CalendrierSemisPersonnaliseResponse(BaseModel):
    """Réponse IA-2: calendrier semis/récolte personnalisé selon météo locale."""

    mois: int
    region: str
    meteo_resume: dict[str, Any] = Field(default_factory=dict)
    a_semer: list[dict[str, Any]] = Field(default_factory=list)
    a_planter: list[dict[str, Any]] = Field(default_factory=list)
    a_recolter: list[dict[str, Any]] = Field(default_factory=list)
    conseils_personnalises: list[str] = Field(default_factory=list)


class EstimationRoiHabitatResponse(BaseModel):
    """Réponse IA-4: estimation prix bien et ROI rénovation."""

    prix_m2_reference: float = 0.0
    valeur_estimee_bien: float = 0.0
    budget_travaux: float = 0.0
    plus_value_estimee: float = 0.0
    roi_pct: float = 0.0
    verdict: str = "neutre"
    recommandations: list[str] = Field(default_factory=list)


class EstimationComparaisonDevisResponse(BaseModel):
    """Réponse IA-7: estimation et comparaison de devis artisans."""

    projet_id: int | None = None
    estimation_reference: dict[str, Any] = Field(default_factory=dict)
    devis_analyses: list[dict[str, Any]] = Field(default_factory=list)
    recommandation: dict[str, Any] = Field(default_factory=dict)
"""
Schémas Pydantic pour les routes Innovations — Phase 10.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Requests ──


class BilanAnnuelRequest(BaseModel):
    """Requête bilan annuel."""

    annee: int | None = Field(None, description="Année du bilan (défaut: année précédente)")


class IdeesCadeauxRequest(BaseModel):
    """Déjà dans ia_avancee — réexport."""

    pass


class VeilleEmploiRequest(BaseModel):
    """Critères de veille emploi."""

    domaine: str = Field("RH", description="Domaine de recherche")
    mots_cles: list[str] = Field(default_factory=lambda: ["RH", "ressources humaines"])
    type_contrat: list[str] = Field(default_factory=lambda: ["CDI", "consultant"])
    mode_travail: list[str] = Field(default_factory=lambda: ["télétravail", "hybride"])
    rayon_km: int = Field(30, ge=5, le=200)
    frequence: str = Field("quotidien")


class LienInviteRequest(BaseModel):
    """Requête de création de lien invité."""

    nom_invite: str = Field(..., min_length=2, max_length=100)
    modules: list[str] = Field(
        default_factory=lambda: ["repas", "routines", "contacts_urgence"],
        description="Modules accessibles par l'invité",
    )
    duree_heures: int = Field(48, ge=1, le=720)


class ParcoursOptimiseRequest(BaseModel):
    """Requête optimisation parcours magasin."""

    liste_id: int | None = Field(None, description="ID de la liste de courses (défaut: dernière active)")


class MangeCeSoirRequest(BaseModel):
    """Contexte utilisateur pour la suggestion dîner express."""

    temps_disponible_min: int = Field(30, ge=10, le=180)
    humeur: str = Field("rapide", min_length=2, max_length=50)


class ComparateurEnergieRequest(BaseModel):
    """Paramètres comparateur énergie."""

    prix_kwh_actuel_eur: float = Field(0.2516, ge=0.05, le=2.0)
    abonnement_mensuel_eur: float = Field(14.0, ge=0.0, le=200.0)


# ── Responses (re-exports depuis types) ──

from src.services.innovations.types import (  # noqa: E402
    AlertesContextuellesResponse,
    AnalyseTendancesLotoResponse,
    AnomaliesEnergieResponse,
    ApprentissageHabitudesResponse,
    BilanAnnuelResponse,
    CoachRoutinesResponse,
    ComparateurEnergieResponse,
    DonneesInviteResponse,
    EnrichissementContactsResponse,
    LienInviteResponse,
    PatternsAlimentairesResponse,
    ParcoursOptimiseResponse,
    PlanningJulesAdaptatifResponse,
    ResumeMensuelIAResponse,
    SaisonnaliteIntelligenteResponse,
    ScoreEcoResponsableResponse,
    ScoreBienEtreResponse,
    SuggestionRepasSoirResponse,
    VeilleEmploiResponse,
)

__all__ = [
    "BilanAnnuelRequest",
    "BilanAnnuelResponse",
    "VeilleEmploiRequest",
    "VeilleEmploiResponse",
    "LienInviteRequest",
    "LienInviteResponse",
    "DonneesInviteResponse",
    "ScoreBienEtreResponse",
    "EnrichissementContactsResponse",
    "AnalyseTendancesLotoResponse",
    "ParcoursOptimiseRequest",
    "ParcoursOptimiseResponse",
    "MangeCeSoirRequest",
    "SuggestionRepasSoirResponse",
    "PatternsAlimentairesResponse",
    "CoachRoutinesResponse",
    "AnomaliesEnergieResponse",
    "ResumeMensuelIAResponse",
    "PlanningJulesAdaptatifResponse",
    "ComparateurEnergieRequest",
    "ComparateurEnergieResponse",
    "ScoreEcoResponsableResponse",
    "SaisonnaliteIntelligenteResponse",
    "ApprentissageHabitudesResponse",
    "AlertesContextuellesResponse",
]

"""
Schémas Pydantic pour les routes Fonctionnalités Avancées.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Requests ──


class BilanAnnuelRequest(BaseModel):
    """Requête bilan annuel."""

    annee: int | None = Field(None, description="Année du bilan (défaut: année précédente)")

    model_config = {"json_schema_extra": {"example": {"annee": 2025}}}


class IdeesCadeauxRequest(BaseModel):
    """Déjà dans ia_avancee — réexport."""

    pass


class VeilleEmploiRequest(BaseModel):
    """Critères de veille emploi."""

    domaine: str = Field("RH", description="Domaine de recherche", max_length=100)
    mots_cles: list[str] = Field(default_factory=lambda: ["RH", "ressources humaines"])
    type_contrat: list[str] = Field(default_factory=lambda: ["CDI", "consultant"])
    mode_travail: list[str] = Field(default_factory=lambda: ["télétravail", "hybride"])
    rayon_km: int = Field(30, ge=5, le=200)
    frequence: str = Field("quotidien", max_length=30)

    model_config = {
        "json_schema_extra": {
            "example": {
                "domaine": "product management",
                "mots_cles": ["product manager", "saas"],
                "type_contrat": ["CDI"],
                "mode_travail": ["télétravail", "hybride"],
                "rayon_km": 25,
                "frequence": "quotidien",
            }
        }
    }


class LienInviteRequest(BaseModel):
    """Requête de création de lien invité."""

    nom_invite: str = Field(..., min_length=2, max_length=100)
    modules: list[str] = Field(
        default_factory=lambda: ["repas", "routines", "contacts_urgence"],
        description="Modules accessibles par l'invité",
    )
    duree_heures: int = Field(48, ge=1, le=720)

    model_config = {
        "json_schema_extra": {
            "example": {"nom_invite": "Mamie", "modules": ["repas", "contacts_urgence"], "duree_heures": 72}
        }
    }


class ParcoursOptimiseRequest(BaseModel):
    """Requête optimisation parcours magasin."""

    liste_id: int | None = Field(None, description="ID de la liste de courses (défaut: dernière active)")


class MangeCeSoirRequest(BaseModel):
    """Contexte utilisateur pour la suggestion dîner express."""

    temps_disponible_min: int = Field(30, ge=10, le=180)
    humeur: str = Field("rapide", min_length=2, max_length=50)

    model_config = {
        "json_schema_extra": {
            "example": {"temps_disponible_min": 25, "humeur": "réconfort"}
        }
    }


class ComparateurEnergieRequest(BaseModel):
    """Paramètres comparateur énergie."""

    prix_kwh_actuel_eur: float = Field(0.2516, ge=0.05, le=2.0)
    abonnement_mensuel_eur: float = Field(14.0, ge=0.0, le=200.0)

    model_config = {
        "json_schema_extra": {
            "example": {"prix_kwh_actuel_eur": 0.248, "abonnement_mensuel_eur": 15.2}
        }
    }


class ModePiloteConfigurationRequest(BaseModel):
    """Configuration du mode pilote automatique."""

    actif: bool = Field(True, description="Active ou desactive le mode pilote")
    niveau_autonomie: str = Field(
        "validation_requise",
        description="off|proposee|validation_requise|semi_auto|auto",
        max_length=30,
    )

    model_config = {
        "json_schema_extra": {
            "example": {"actif": True, "niveau_autonomie": "validation_requise"}
        }
    }


class ModeVacancesConfigurationRequest(BaseModel):
    """Configuration du mode vacances."""

    actif: bool = Field(True, description="Active ou desactive le mode vacances")
    checklist_voyage_auto: bool = Field(
        True,
        description="Active la checklist voyage automatique en mode vacances",
    )

    model_config = {
        "json_schema_extra": {
            "example": {"actif": True, "checklist_voyage_auto": True}
        }
    }


class CarteVisuelleRequest(BaseModel):
    """Paramètres de génération d'une carte visuelle partageable."""

    type_carte: str = Field("planning", pattern="^(planning|recette|batch|maison)$")
    titre: str | None = Field(None, min_length=2, max_length=120)

    model_config = {
        "json_schema_extra": {
            "example": {"type_carte": "planning", "titre": "Menus de la semaine"}
        }
    }


# ── Responses (re-exports depuis types) ──

from src.services.experimental.types import (  # noqa: E402
    ModePiloteAutomatiqueResponse,
    ScoreFamilleHebdoResponse,
    JournalFamilialAutoResponse,
    RapportMensuelPdfResponse,
    BatchCookingIntelligentResponse,
    CarteVisuellePartageableResponse,
    ModeTabletteMagazineResponse,
    PlanificationHebdoCompleteResponse,
    ApprentissagePreferencesResponse,
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
    InsightsQuotidiensResponse,
    MeteoContextuelleResponse,
    ModeVacancesResponse,
    ComparateurPrixAutomatiqueResponse,
    EnergieTempsReelResponse,
    TelegramConversationnelResponse,
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
    "ScoreFamilleHebdoResponse",
    "ModePiloteAutomatiqueResponse",
    "JournalFamilialAutoResponse",
    "RapportMensuelPdfResponse",
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
    "ModePiloteConfigurationRequest",
    "ModeVacancesConfigurationRequest",
    "CarteVisuelleRequest",
    "ComparateurEnergieResponse",
    "ApprentissagePreferencesResponse",
    "PlanificationHebdoCompleteResponse",
    "BatchCookingIntelligentResponse",
    "CarteVisuellePartageableResponse",
    "ModeTabletteMagazineResponse",
    "ScoreEcoResponsableResponse",
    "SaisonnaliteIntelligenteResponse",
    "ApprentissageHabitudesResponse",
    "AlertesContextuellesResponse",
    "ModeVacancesResponse",
    "InsightsQuotidiensResponse",
    "MeteoContextuelleResponse",
    "TelegramConversationnelResponse",
    "ComparateurPrixAutomatiqueResponse",
    "EnergieTempsReelResponse",
]

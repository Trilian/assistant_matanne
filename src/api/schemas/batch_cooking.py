"""
Schémas Pydantic pour le batch cooking.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class SessionBatchBase(BaseModel):
    """Champs communs pour une session batch cooking."""

    nom: str = Field(..., min_length=1, max_length=200)
    date_session: date
    duree_estimee: int | None = Field(None, ge=0, description="Durée estimée en minutes")
    avec_jules: bool = False
    recettes_selectionnees: list[int] = Field(default_factory=list)
    robots_utilises: list[str] = Field(default_factory=list)


class SessionBatchCreate(SessionBatchBase):
    """Création d'une session batch cooking."""

    planning_id: int | None = None


class GenererSessionDepuisPlanningRequest(BaseModel):
    """Requête pour générer une session depuis un planning."""

    planning_id: int = Field(..., description="ID du planning source")
    date_session: date = Field(..., description="Date de la session batch")
    nom: str | None = Field(None, description="Nom personnalisé (sinon auto-généré)")
    avec_jules: bool = Field(False, description="Jules participe ?")


class GenererSessionDepuisPlanningResponse(BaseModel):
    """Résultat de la génération."""

    session_id: int
    nom: str
    nb_recettes: int
    recettes: list[dict[str, str | int]]  # [{id, nom, portions}]
    duree_estimee: int
    robots_utilises: list[str]


class SessionBatchPatch(BaseModel):
    """Mise à jour partielle d'une session."""

    nom: str | None = Field(None, min_length=1, max_length=200)
    date_session: date | None = None
    statut: str | None = Field(None, pattern=r"^(planifiee|en_cours|terminee|annulee)$")
    duree_estimee: int | None = None
    avec_jules: bool | None = None


class SessionBatchResponse(BaseModel):
    """Réponse d'une session batch cooking."""

    id: int
    nom: str
    date_session: str
    heure_debut: str | None = None
    heure_fin: str | None = None
    duree_estimee: int | None = None
    duree_reelle: int | None = None
    statut: str
    avec_jules: bool
    planning_id: int | None = None
    recettes_selectionnees: list[int] = Field(default_factory=list)
    robots_utilises: list[str] = Field(default_factory=list)
    genere_par_ia: bool = False
    etapes_count: int = 0
    progression: float = 0.0


class EtapeBatchResponse(BaseModel):
    """Réponse d'une étape de batch cooking."""

    id: int
    ordre: int
    groupe_parallele: int | None = None
    titre: str
    duree_minutes: int | None = None
    robots_requis: list[str] = Field(default_factory=list)
    statut: str
    est_terminee: bool = False


class PreparationBatchResponse(BaseModel):
    """Réponse d'une préparation stockée."""

    id: int
    nom: str
    portions_initiales: int
    portions_restantes: int
    date_preparation: str | None = None
    date_peremption: str | None = None
    localisation: str | None = None
    container: str | None = None
    consomme: bool = False
    jours_avant_peremption: int | None = None
    alerte_peremption: bool = False


class ConfigBatchResponse(BaseModel):
    """Config batch cooking de l'utilisateur."""

    jours_batch: list[str] = Field(default_factory=list)
    heure_debut_preferee: str | None = None
    duree_max_session: int | None = None
    avec_jules_par_defaut: bool = False
    robots_disponibles: list[str] = Field(default_factory=list)
    objectif_portions_semaine: int = 0

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

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Batch du dimanche",
                "date_session": "2026-04-05",
                "duree_estimee": 120,
                "avec_jules": True,
                "recettes_selectionnees": [12, 18, 27],
                "robots_utilises": ["Thermomix", "Air fryer"],
            }
        }
    }


class SessionBatchCreate(SessionBatchBase):
    """Création d'une session batch cooking."""

    planning_id: int | None = None


class GenererSessionDepuisPlanningRequest(BaseModel):
    """Requête pour générer une session depuis un planning."""

    planning_id: int = Field(..., description="ID du planning source")
    date_session: date = Field(..., description="Date de la session batch")
    nom: str | None = Field(
        None, description="Nom personnalisé (sinon auto-généré)", max_length=200
    )
    avec_jules: bool = Field(False, description="Jules participe ?")

    model_config = {
        "json_schema_extra": {
            "example": {
                "planning_id": 7,
                "date_session": "2026-04-06",
                "nom": "Préparation semaine 15",
                "avec_jules": False,
            }
        }
    }


class GenererSessionDepuisPlanningResponse(BaseModel):
    """Résultat de la génération."""

    session_id: int
    nom: str = Field(max_length=200)
    nb_recettes: int
    recettes: list[dict[str, str | int]]  # [{id, nom, portions}]
    duree_estimee: int
    robots_utilises: list[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": 21,
                "nom": "Préparation semaine 15",
                "nb_recettes": 3,
                "recettes": [{"id": 12, "nom": "Lasagnes", "portions": 6}],
                "duree_estimee": 135,
                "robots_utilises": ["Thermomix"],
            }
        }
    }


class SessionBatchPatch(BaseModel):
    """Mise à jour partielle d'une session."""

    nom: str | None = Field(None, min_length=1, max_length=200)
    date_session: date | None = None
    statut: str | None = Field(
        None, pattern=r"^(planifiee|en_cours|terminee|annulee)$", max_length=20
    )
    duree_estimee: int | None = None
    avec_jules: bool | None = None
    recettes_selectionnees: list[int] | None = Field(None, description="IDs des recettes sélectionnées")


class SessionBatchResponse(BaseModel):
    """Réponse d'une session batch cooking."""

    id: int
    nom: str = Field(max_length=200)
    date_session: str
    heure_debut: str | None = Field(None, max_length=8)
    heure_fin: str | None = Field(None, max_length=8)
    duree_estimee: int | None = None
    duree_reelle: int | None = None
    statut: str = Field(max_length=20)
    avec_jules: bool
    planning_id: int | None = None
    recettes_selectionnees: list[int] = Field(default_factory=list)
    robots_utilises: list[str] = Field(default_factory=list)
    genere_par_ia: bool = False
    etapes_count: int = 0
    progression: float = 0.0

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 21,
                "nom": "Préparation semaine 15",
                "date_session": "2026-04-06",
                "heure_debut": "14:00",
                "heure_fin": None,
                "duree_estimee": 135,
                "duree_reelle": None,
                "statut": "planifiee",
                "avec_jules": False,
                "planning_id": 7,
                "recettes_selectionnees": [12, 18, 27],
                "robots_utilises": ["Thermomix"],
                "genere_par_ia": True,
                "etapes_count": 9,
                "progression": 0.0,
            }
        }
    }


class EtapeBatchResponse(BaseModel):
    """Réponse d'une étape de batch cooking."""

    id: int
    ordre: int
    groupe_parallele: int | None = None
    titre: str = Field(max_length=200)
    duree_minutes: int | None = None
    robots_requis: list[str] = Field(default_factory=list)
    statut: str = Field(max_length=20)
    est_terminee: bool = False


class PreparationBatchResponse(BaseModel):
    """Réponse d'une préparation stockée."""

    id: int
    nom: str = Field(max_length=200)
    portions_initiales: int
    portions_restantes: int
    date_preparation: str | None = None
    date_peremption: str | None = None
    localisation: str | None = Field(None, max_length=200)
    container: str | None = Field(None, max_length=100)
    consomme: bool = False
    jours_avant_peremption: int | None = None
    alerte_peremption: bool = False


class ConfigBatchResponse(BaseModel):
    """Config batch cooking de l'utilisateur."""

    jours_batch: list[str] = Field(default_factory=list)
    heure_debut_preferee: str | None = Field(None, max_length=8)
    duree_max_session: int | None = None
    avec_jules_par_defaut: bool = False
    robots_disponibles: list[str] = Field(default_factory=list)
    objectif_portions_semaine: int = 0

    model_config = {
        "json_schema_extra": {
            "example": {
                "jours_batch": ["dimanche"],
                "heure_debut_preferee": "14:00",
                "duree_max_session": 180,
                "avec_jules_par_defaut": True,
                "robots_disponibles": ["Thermomix", "Air fryer"],
                "objectif_portions_semaine": 12,
            }
        }
    }

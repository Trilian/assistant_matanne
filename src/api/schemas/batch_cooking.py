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
    preparations_simples: list[str] = Field(default_factory=list, description="Préparations sans recette (accompagnements, etc.)")

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


class RecetteDepuisPlanningItem(BaseModel):
    """Recette issue du planning, retournée par GET /recettes-depuis-planning."""

    id: int
    nom: str = Field(max_length=200)
    type_repas: str = Field(max_length=50)
    compatible_batch: bool = False


class RecettesDepuisPlanningResponse(BaseModel):
    """Résultat de GET /recettes-depuis-planning."""

    recettes: list[RecetteDepuisPlanningItem]
    preparations_simples: list[str]


class GenererSessionDepuisPlanningRequest(BaseModel):
    """Requête pour générer une session depuis un planning."""

    planning_id: int = Field(..., description="ID du planning source")
    date_session: date = Field(..., description="Date de la session batch")
    nom: str | None = Field(
        None, description="Nom personnalisé (sinon auto-généré)", max_length=200
    )
    avec_jules: bool = Field(False, description="Jules participe ?")
    recettes_selectionnees: list[int] | None = Field(
        None,
        description="IDs des recettes sélectionnées par l'utilisateur. "
        "Si fourni, remplace la requête planning.",
    )
    preparations_simples: list[str] | None = Field(
        None,
        description="Préparations sans recette à inclure (accompagnements, etc.)",
    )
    jours_cibles: list[int] | None = Field(
        None,
        description="[Déprécié] Jours de la semaine (0=lun…6=dim). Ignoré si recettes_selectionnees fourni.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "planning_id": 7,
                "date_session": "2026-04-09",
                "nom": "Batch mercredi — jeu/ven",
                "avec_jules": False,
                "jours_cibles": [2, 3, 4],
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
    robots_utilises: list[str] | None = Field(None, description="Robots/appareils utilisés")
    preparations_simples: list[str] | None = Field(None, description="Préparations sans recette (accompagnements, etc.)")


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
    description: str | None = None
    est_supervision: bool = False
    temperature: int | None = None


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
    preparations_simples: list[str] = Field(default_factory=list)
    genere_par_ia: bool = False
    etapes_count: int = 0
    progression: float = 0.0
    etapes: list[EtapeBatchResponse] = Field(default_factory=list)

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

    jours_batch: list[int] = Field(default_factory=list, description="Jours batch (0=lun… 6=dim)")
    heure_debut_preferee: str | None = Field(None, max_length=8)
    duree_max_session: int | None = None
    avec_jules_par_defaut: bool = False
    robots_disponibles: list[str] = Field(default_factory=list)
    objectif_portions_semaine: int = 0
    couverture_jours: dict | None = Field(
        None,
        description="Mapping jour_batch → jours couverts. Ex: {'2': [2, 3, 4], '6': [6, 0, 1, 2]}",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "jours_batch": [2, 6],
                "heure_debut_preferee": "10:00",
                "duree_max_session": 180,
                "avec_jules_par_defaut": True,
                "robots_disponibles": ["four", "plaques", "cookeo"],
                "objectif_portions_semaine": 20,
                "couverture_jours": {"2": [2, 3, 4], "6": [6, 0, 1, 2]},
            }
        }
    }


class ConfigBatchUpdate(BaseModel):
    """Mise à jour de la configuration batch cooking (tous champs optionnels)."""

    jours_batch: list[int] | None = Field(None, description="Jours batch (0=lundi…6=dimanche)")
    heure_debut_preferee: str | None = Field(None, max_length=8, description="Heure de début HH:MM")
    duree_max_session: int | None = Field(None, ge=30, le=720, description="Durée max en minutes")
    avec_jules_par_defaut: bool | None = None
    robots_disponibles: list[str] | None = None
    objectif_portions_semaine: int | None = Field(None, ge=1, le=100)
    notes: str | None = None
    couverture_jours: dict | None = Field(
        None,
        description="Mapping jour_batch → jours couverts. Ex: {'2': [2, 3, 4], '6': [6, 0, 1, 2]}",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "jours_batch": [2, 6],
                "couverture_jours": {"2": [2, 3, 4], "6": [6, 0, 1, 2]},
                "robots_disponibles": ["four", "plaques", "cookeo"],
            }
        }
    }

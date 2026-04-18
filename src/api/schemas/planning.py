"""
Schémas Pydantic pour le planning.
"""

from datetime import date as DateType
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .base import IdentifiedResponse, TypeRepasValidator


class RepasBase(BaseModel, TypeRepasValidator):
    """Schéma de base pour un repas.

    Le champ ``date`` utilise l'alias ``date_repas`` pour la sérialisation
    depuis les objets ORM (modèle ``Repas.date_repas``).  Les clients API
    peuvent envoyer le champ sous les deux noms (``date`` ou ``date_repas``)
    grâce à ``populate_by_name=True``.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "type_repas": "diner",
                "date": "2026-04-06",
                "recette_id": 42,
                "notes": "Prévoir une portion Jules sans sel.",
            }
        },
    )

    type_repas: str = Field(..., max_length=30)
    date: DateType = Field(alias="date_repas")
    recette_id: int | None = None
    notes: str | None = Field(None, max_length=1000)


class RepasCreate(RepasBase):
    """Création d'un repas — hérite tous les champs de RepasBase."""

    # Entrée et dessert (déjeuner / dîner)
    entree: str | None = Field(None, max_length=200)
    entree_recette_id: int | None = None
    dessert: str | None = Field(None, max_length=200)
    dessert_recette_id: int | None = None
    # Accompagnements équilibre assiette
    legumes: str | None = Field(None, max_length=200)
    legumes_recette_id: int | None = None
    feculents: str | None = Field(None, max_length=200)
    feculents_recette_id: int | None = None
    proteine_accompagnement: str | None = Field(None, max_length=200)
    proteine_accompagnement_recette_id: int | None = None
    # Laitage + goûter
    laitage: str | None = Field(None, max_length=200)
    fruit_gouter: str | None = Field(None, max_length=100)
    gateau_gouter: str | None = Field(None, max_length=100)


class RepasUpdate(RepasCreate):
    """Mise à jour partielle d'un repas — tous les champs optionnels."""

    type_repas: str | None = Field(None, max_length=30)  # type: ignore[assignment]
    date: DateType | None = Field(None, alias="date_repas")  # type: ignore[assignment]


class RepasResponse(RepasBase, IdentifiedResponse):
    """Schéma de réponse pour un repas."""

    recette_nom: str | None = Field(None, max_length=200)
    plat_jules: str | None = Field(None, max_length=200)
    notes_jules: str | None = Field(None, max_length=1000)
    adaptation_auto: bool = True
    compatible_cookeo: bool = False
    compatible_monsieur_cuisine: bool = False
    compatible_airfryer: bool = False
    est_reste: bool = False
    reste_description: str | None = Field(None, max_length=200)
    # Entrée et dessert
    entree: str | None = Field(None, max_length=200)
    entree_recette_id: int | None = None
    dessert: str | None = Field(None, max_length=200)
    dessert_recette_id: int | None = None
    # Champs équilibre nutritionnel
    fruit: str | None = Field(None, max_length=200)  # legacy migration 005
    legumes: str | None = Field(None, max_length=200)
    legumes_recette_id: int | None = None
    feculents: str | None = Field(None, max_length=200)
    feculents_recette_id: int | None = None
    proteine_accompagnement: str | None = Field(None, max_length=200)
    proteine_accompagnement_recette_id: int | None = None
    laitage: str | None = Field(None, max_length=200)
    fruit_gouter: str | None = Field(None, max_length=100)
    gateau_gouter: str | None = Field(None, max_length=100)
    score_equilibre: int | None = Field(None, ge=0, le=100)
    alertes_equilibre: list[str] | None = None


class SuggestionAccompagnementResponse(BaseModel):
    """Réponse IA pour les suggestions d'accompagnements."""

    legumes: list[str] = Field(default_factory=list)
    feculents: list[str] = Field(default_factory=list)
    proteines: list[str] = Field(default_factory=list)
    categorie_detectee: str | None = None


class PlanningSemaineResponse(BaseModel):
    """Réponse du planning hebdomadaire."""

    date_debut: str
    date_fin: str
    planning: dict[str, dict[str, Any]]
    planning_id: int | None = None
    genere_par_ia: bool = False
    repas: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "date_debut": "2026-04-06",
                "date_fin": "2026-04-12",
                "planning_id": 1,
                "genere_par_ia": True,
                "planning": {
                    "2026-04-06": {
                        "dejeuner": {"recette_id": 12, "recette_nom": "Pâtes au pesto"},
                        "diner": {"recette_id": 42, "recette_nom": "Gratin de courgettes"},
                    }
                },
            }
        }
    }


class GenererPlanningRequest(BaseModel):
    """Paramètres pour générer un planning IA."""

    date_debut: DateType | None = Field(
        None, description="Début de semaine (défaut: lundi courant)"
    )
    nb_personnes: int = Field(4, ge=1, le=20, description="Nombre de personnes")
    preferences: dict[str, Any] | None = Field(
        None, description="Préférences (allergies, régime, etc.)"
    )
    legumes_souhaites: list[str] = Field(
        default_factory=list,
        description="Légumes à privilégier cette semaine (forte préférence)",
    )
    feculents_souhaites: list[str] = Field(
        default_factory=list,
        description="Féculents à privilégier cette semaine (forte préférence)",
    )
    plats_souhaites: list[str] = Field(
        default_factory=list,
        description="Plats à inclure cette semaine (forte préférence)",
    )
    ingredients_interdits: list[str] = Field(
        default_factory=list,
        description="Ingrédients à exclure pour cette génération (s'ajoute aux allergies permanentes)",
    )
    autoriser_restes: bool = Field(
        True, description="Proposer des repas 'reste réchauffé' (soir → midi lendemain)"
    )
    cuisines_souhaitees: list[str] = Field(
        default_factory=list,
        description="Cuisines du monde à intégrer (ex: français, italien, japonais, chinois, mexicain, espagnol, américain, breton, basque, alsacien, savoyard, provençal)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "date_debut": "2026-04-06",
                "nb_personnes": 3,
                "preferences": {"allergies": ["arachides"], "temps_max": 30, "jules": True},
                "legumes_souhaites": ["courgettes", "brocoli"],
                "feculents_souhaites": ["pommes de terre vapeur"],
                "plats_souhaites": ["poulet rôti"],
                "ingredients_interdits": ["concombre"],
                "autoriser_restes": True,
                "cuisines_souhaitees": ["italien", "japonais"],
            }
        }
    }


class RepasRapideSuggestion(BaseModel):
    """Une suggestion de repas rapide."""

    id: int
    nom: str = Field(max_length=200)
    description: str | None = Field(None, max_length=500)
    temps_total: int = 0
    categorie: str | None = Field(None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 9,
                "nom": "Omelette aux herbes",
                "description": "Repas prêt en moins de 15 minutes.",
                "temps_total": 12,
                "categorie": "rapide",
            }
        }
    }

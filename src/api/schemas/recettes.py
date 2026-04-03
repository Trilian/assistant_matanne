"""
Schémas Pydantic pour les recettes.
"""

from pydantic import BaseModel, Field, field_validator

from .base import IdentifiedResponse, NomValidatorMixin


# ═══════════════════════════════════════════════════════════
# SOUS-SCHÉMAS INGRÉDIENTS & ÉTAPES
# ═══════════════════════════════════════════════════════════


class IngredientItem(BaseModel):
    """Un ingrédient dans une recette (entrée)."""

    nom: str = Field(..., min_length=1, max_length=200)
    quantite: float = Field(1, ge=0)
    unite: str = Field("pièce", max_length=30)

    model_config = {
        "json_schema_extra": {
            "example": {"nom": "Courgette", "quantite": 2, "unite": "pièce"}
        }
    }


class IngredientResponse(BaseModel):
    """Un ingrédient dans une recette (sortie)."""

    id: int
    nom: str
    quantite: float
    unite: str
    optionnel: bool = False

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 12,
                "nom": "Parmesan",
                "quantite": 40,
                "unite": "g",
                "optionnel": False,
            }
        },
    }


class EtapeResponse(BaseModel):
    """Une étape de recette (sortie)."""

    id: int
    ordre: int
    description: str = Field(max_length=2000)
    titre: str | None = Field(None, max_length=200)
    duree: int | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "ordre": 1,
                "description": "Faire revenir l'oignon 3 minutes avec un filet d'huile.",
                "titre": "Préparer la base",
                "duree": 3,
            }
        },
    }


# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════


class RecetteBase(BaseModel, NomValidatorMixin):
    """Schéma de base pour une recette."""

    nom: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    temps_preparation: int = Field(15, description="Minutes", ge=0)
    temps_cuisson: int = Field(0, description="Minutes", ge=0)
    portions: int = Field(4, ge=1)
    difficulte: str = Field("moyen", max_length=30)
    categorie: str | None = Field(None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Gratin de courgettes",
                "description": "Un gratin léger pour le soir.",
                "temps_preparation": 15,
                "temps_cuisson": 30,
                "portions": 4,
                "difficulte": "facile",
                "categorie": "plat",
            }
        }
    }


class RecetteCreate(RecetteBase):
    """Schéma pour créer une recette."""

    ingredients: list[IngredientItem] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @field_validator("instructions", mode="before")
    @classmethod
    def normaliser_instructions(cls, v: str | list[str] | None) -> list[str]:
        """Accepte une chaîne (split par lignes) ou une liste."""
        if v is None:
            return []
        if isinstance(v, str):
            return [line.strip() for line in v.splitlines() if line.strip()]
        return v

    @field_validator("ingredients", mode="before")
    @classmethod
    def normaliser_ingredients(cls, v: list | None) -> list:
        """Accepte les dicts bruts et les convertit en IngredientItem."""
        if v is None:
            return []
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Gratin de courgettes",
                "description": "Un gratin léger pour le soir.",
                "temps_preparation": 15,
                "temps_cuisson": 30,
                "portions": 4,
                "difficulte": "facile",
                "categorie": "plat",
                "ingredients": [
                    {"nom": "Courgette", "quantite": 3, "unite": "pièce"},
                    {"nom": "Crème fraîche", "quantite": 20, "unite": "cl"}
                ],
                "instructions": [
                    "Préchauffer le four à 180°C.",
                    "Cuire 30 minutes jusqu'à coloration."
                ],
                "tags": ["été", "végétarien"],
            }
        }
    }


class RecettePatch(BaseModel):
    """Schéma pour mise à jour partielle (PATCH) d'une recette.

    Tous les champs sont optionnels. Seuls les champs fournis
    seront modifiés, les autres restent inchangés.

    Example:
        ```json
        {"nom": "Nouveau nom", "temps_cuisson": 45}
        ```
    """

    nom: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    temps_preparation: int | None = Field(None, description="Minutes", ge=0)
    temps_cuisson: int | None = Field(None, description="Minutes", ge=0)
    portions: int | None = Field(None, ge=1)
    difficulte: str | None = Field(None, max_length=30)
    categorie: str | None = Field(None, max_length=100)
    ingredients: list[IngredientItem] | None = None
    instructions: list[str] | None = None
    tags: list[str] | None = None

    @field_validator("instructions", mode="before")
    @classmethod
    def normaliser_instructions(cls, v: str | list[str] | None) -> list[str] | None:
        """Accepte une chaîne (split par lignes) ou une liste."""
        if v is None:
            return None
        if isinstance(v, str):
            return [line.strip() for line in v.splitlines() if line.strip()]
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "temps_cuisson": 35,
                "instructions": [
                    "Préchauffer le four à 180°C.",
                    "Cuire jusqu'à ce que le dessus soit doré."
                ],
                "tags": ["batch cooking"],
            }
        }
    }


class RecetteResponse(RecetteBase, IdentifiedResponse):
    """Schéma de réponse pour une recette."""

    ingredients: list[IngredientResponse] = Field(default_factory=list)
    etapes: list[EtapeResponse] = Field(default_factory=list)
    est_favori: bool = False
    url_source: str | None = Field(None, max_length=500)
    compatible_cookeo: bool = False
    compatible_monsieur_cuisine: bool = False
    compatible_airfryer: bool = False
    jours_depuis_derniere_cuisson: int | None = None
    calories: int | None = None
    proteines: float | None = None
    lipides: float | None = None
    glucides: float | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 42,
                "nom": "Gratin de courgettes",
                "description": "Un gratin léger pour le soir.",
                "temps_preparation": 15,
                "temps_cuisson": 30,
                "portions": 4,
                "difficulte": "facile",
                "categorie": "plat",
                "ingredients": [
                    {"id": 1, "nom": "Courgette", "quantite": 3, "unite": "pièce", "optionnel": False}
                ],
                "etapes": [
                    {
                        "id": 1,
                        "ordre": 1,
                        "description": "Préchauffer le four à 180°C.",
                        "titre": "Préchauffage",
                        "duree": 5,
                    }
                ],
                "est_favori": True,
                "url_source": None,
                "compatible_cookeo": False,
                "compatible_monsieur_cuisine": False,
                "compatible_airfryer": True,
                "jours_depuis_derniere_cuisson": 9,
                "calories": 420,
                "proteines": 18.5,
                "lipides": 22.0,
                "glucides": 31.0,
            }
        }
    }


class VersionRecetteResponse(BaseModel):
    """Réponse pour une version Jules d'une recette (CT-09)."""

    id: int
    recette_base_id: int
    type_version: str = Field(max_length=50)
    instructions_modifiees: str | None = Field(None, max_length=4000)
    ingredients_modifies: dict | None = None
    notes_bebe: str | None = Field(None, max_length=1000)
    modifications_resume: list[str] = Field(default_factory=list)
    recette_nom: str | None = Field(None, max_length=200)
    age_mois_jules: int | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 3,
                "recette_base_id": 42,
                "type_version": "jules",
                "instructions_modifiees": "Mixer finement la préparation et retirer le sel.",
                "ingredients_modifies": {"sel": "supprimé", "texture": "mixée"},
                "notes_bebe": "Servir tiède en petites portions.",
                "modifications_resume": ["sans sel", "texture mixée"],
                "recette_nom": "Gratin de courgettes",
                "age_mois_jules": 18,
            }
        },
    }

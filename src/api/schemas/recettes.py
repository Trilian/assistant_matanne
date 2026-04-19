"""
Schémas Pydantic pour les recettes.
"""

from pydantic import BaseModel, Field, field_validator

from .base import IdentifiedResponse, NomValidatorMixin


# ═══════════════════════════════════════════════════════════
# NORMALISATION CATÉGORIES
# ═══════════════════════════════════════════════════════════

_MAP_CATEGORIES: dict[str, str] = {
    "plat": "Plat", "plats": "Plat", "principal": "Plat", "plat principal": "Plat",
    "entrée": "Entrée", "entree": "Entrée", "entrées": "Entrée", "entrees": "Entrée", "starter": "Entrée",
    "dessert": "Dessert", "desserts": "Dessert",
    "accompagnement": "Accompagnement", "accompagnements": "Accompagnement", "garniture": "Accompagnement",
    "boisson": "Boisson", "boissons": "Boisson", "drink": "Boisson",
    "petit-déjeuner": "Petit-déjeuner", "petit déjeuner": "Petit-déjeuner",
    "petit_dejeuner": "Petit-déjeuner", "breakfast": "Petit-déjeuner",
    "goûter": "Goûter", "gouter": "Goûter", "goûters": "Goûter",
    "snack": "Snack", "snacks": "Snack", "apéro": "Snack", "apero": "Snack", "amuse-bouche": "Snack",
}


def normaliser_categorie(cat: str | None) -> str:
    """Normalise une valeur de catégorie vers la forme canonique capitalisée.

    Accepte toutes les variantes (casse, accents, pluriel) et retourne
    la forme canonique. Retourne "Plat" par défaut si non reconnue.
    """
    if not cat or not cat.strip():
        return "Plat"
    return _MAP_CATEGORIES.get(cat.strip().lower(), "Plat")


# ═══════════════════════════════════════════════════════════
# SOUS-SCHÉMAS INGRÉDIENTS & ÉTAPES
# ═══════════════════════════════════════════════════════════


class IngredientItem(BaseModel):
    """Un ingrédient dans une recette (entrée)."""

    nom: str = Field(..., min_length=1, max_length=200)
    quantite: float = Field(1, ge=0)
    unite: str = Field("pièce", max_length=30)

    model_config = {
        "json_schema_extra": {"example": {"nom": "Courgette", "quantite": 2, "unite": "pièce"}}
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
    instructions_cookeo: str | None = Field(None, max_length=4000)
    instructions_monsieur_cuisine: str | None = Field(None, max_length=4000)
    instructions_airfryer: str | None = Field(None, max_length=4000)

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

    categorie: str = Field("Plat", max_length=100)
    ingredients: list[IngredientItem] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    compatible_cookeo: bool = False
    compatible_monsieur_cuisine: bool = False
    compatible_airfryer: bool = False

    @field_validator("categorie", mode="before")
    @classmethod
    def normaliser_cat(cls, v: str | None) -> str:
        return normaliser_categorie(v)

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
                    {"nom": "Crème fraîche", "quantite": 20, "unite": "cl"},
                ],
                "instructions": [
                    "Préchauffer le four à 180°C.",
                    "Cuire 30 minutes jusqu'à coloration.",
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
    compatible_cookeo: bool | None = None
    compatible_monsieur_cuisine: bool | None = None
    compatible_airfryer: bool | None = None
    instructions_cookeo: str | None = None
    instructions_monsieur_cuisine: str | None = None
    instructions_airfryer: str | None = None
    url_image: str | None = None

    @field_validator("categorie", mode="before")
    @classmethod
    def normaliser_cat(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return normaliser_categorie(v)

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
                    "Cuire jusqu'à ce que le dessus soit doré.",
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
    genere_par_ia: bool = False
    url_source: str | None = Field(None, max_length=500)
    # Adaptation Jules (si enregistrée)
    version_jules: "VersionRecetteResponse | None" = None
    # Adaptations robots (si enregistrées)
    versions_robots: "list[VersionRecetteResponse]" = Field(default_factory=list)
    image_url: str | None = None
    compatible_cookeo: bool = False
    compatible_monsieur_cuisine: bool = False
    compatible_airfryer: bool = False
    instructions_cookeo: str | None = None
    instructions_monsieur_cuisine: str | None = None
    instructions_airfryer: str | None = None
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
                    {
                        "id": 1,
                        "nom": "Courgette",
                        "quantite": 3,
                        "unite": "pièce",
                        "optionnel": False,
                    }
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
    """Réponse pour une version Jules d'une recette."""

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


# ═══════════════════════════════════════════════════════════
# ADAPTATIONS MANUELLES (Jules + Robots)
# ═══════════════════════════════════════════════════════════


class AdaptationJulesManuelle(BaseModel):
    """Payload pour sauvegarder manuellement la version Jules d'une recette."""

    instructions_modifiees: str | None = Field(
        None,
        max_length=4000,
        description="Instructions adaptées pour Jules (texte libre, étape par étape)",
    )
    ingredients_modifies: dict[str, str] | None = Field(
        None,
        description="Modifications par ingrédient, ex: {'champignons': 'mixés', 'sel': 'supprimé'}",
    )
    notes_bebe: str | None = Field(
        None, max_length=1000, description="Notes de service (texture, température, portion)"
    )
    modifications_resume: list[str] = Field(
        default_factory=list,
        description="Résumé des adaptations, ex: ['sans sel', 'champignons mixés']",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "instructions_modifiees": (
                    "Mixer les champignons finement. "
                    "Ne pas ajouter de sel. Servir tiède."
                ),
                "ingredients_modifies": {
                    "champignons": "mixés finement",
                    "sel": "supprimé",
                    "fromage": "en petite quantité",
                },
                "notes_bebe": "Portions réduites, servir tiède.",
                "modifications_resume": ["sans sel", "champignons mixés", "fromage adapté"],
            }
        }
    }


ROBOTS_VALIDES = {"cookeo", "monsieur_cuisine", "airfryer"}


class AdaptationRobotManuelle(BaseModel):
    """Payload pour sauvegarder les instructions robot d'une recette."""

    robot: str = Field(
        ...,
        description="Nom du robot : cookeo, monsieur_cuisine ou airfryer",
        max_length=50,
    )
    instructions_modifiees: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Instructions spécifiques au robot (étape par étape)",
    )
    modifications_resume: list[str] = Field(
        default_factory=list,
        description="Points clés par rapport à la recette classique",
    )
    notes_bebe: str | None = Field(
        None,
        max_length=1000,
        description="Notes complémentaires (optionnel)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "robot": "cookeo",
                "instructions_modifiees": (
                    "1. Faire revenir les champignons avec la touche Dorer, 5 min.\n"
                    "2. Ajouter les œufs battus, mode Mijoter 3 min."
                ),
                "modifications_resume": ["cuisson Cookeo", "mode Dorer + Mijoter"],
            }
        }
    }

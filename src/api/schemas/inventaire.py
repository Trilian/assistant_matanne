"""
Schémas Pydantic pour l'inventaire.

Aligné avec le modèle ORM ``ArticleInventaire`` qui utilise
``ingredient_id`` (FK vers ``ingredients``) et non pas ``nom`` directement.
"""

from datetime import datetime

from pydantic import BaseModel, Field, computed_field, field_validator

from src.core.constants import EMPLACEMENTS_INVENTAIRE

from .base import IdentifiedResponse, QuantiteStricteValidatorMixin

# ═══════════════════════════════════════════════════════════
# BASE (compatibilité tests)
# ═══════════════════════════════════════════════════════════


class InventaireItemBase(BaseModel, QuantiteStricteValidatorMixin):
    """Schéma de base pour validation standalone (tests).

    Utilisé pour tester la validation sans dépendance FK.
    """

    nom: str
    quantite: float = 1.0

    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()


# ═══════════════════════════════════════════════════════════
# CREATE
# ═══════════════════════════════════════════════════════════


class InventaireItemCreate(BaseModel, QuantiteStricteValidatorMixin):
    """Schéma pour créer un article d'inventaire.

    Utilise ``ingredient_id`` (FK) conformément au modèle ORM.
    ``nom``, ``unite`` et ``categorie`` sont résolus via la relation Ingredient.
    """

    ingredient_id: int
    quantite: float = 1.0
    quantite_min: float = 1.0
    emplacement: str | None = None
    date_peremption: datetime | None = None
    code_barres: str | None = None
    prix_unitaire: float | None = None

    @field_validator("ingredient_id")
    @classmethod
    def validate_ingredient_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("ingredient_id doit être un entier positif")
        return v

    @field_validator("emplacement")
    @classmethod
    def validate_emplacement(cls, v: str | None) -> str | None:
        if v is None:
            return v

        normalisations = {
            "frigo": "Frigo",
            "refrigerateur": "Frigo",
            "réfrigérateur": "Frigo",
            "congelateur tiroir": "Congélateur Tiroir",
            "congélateur tiroir": "Congélateur Tiroir",
            "congelateur coffre": "Congélateur Coffre",
            "congélateur coffre": "Congélateur Coffre",
            "cellier": "Cellier",
            "placard": "Placard",
        }
        emplacement_normalise = normalisations.get(v.strip().lower(), v)

        if emplacement_normalise not in EMPLACEMENTS_INVENTAIRE:
            raise ValueError(
                f"Emplacement invalide: '{v}'. "
                f"Valeurs acceptées: {', '.join(EMPLACEMENTS_INVENTAIRE)}"
            )
        return emplacement_normalise


# ═══════════════════════════════════════════════════════════
# UPDATE (PATCH partiel)
# ═══════════════════════════════════════════════════════════


class InventaireItemUpdate(BaseModel):
    """Schéma pour mettre à jour un article d'inventaire.

    Tous les champs sont optionnels : seuls les champs fournis sont appliqués.
    Les champs inconnus (ex. nom, unite, categorie) provoquent une erreur 422
    car ils appartiennent au modèle Ingredient, pas à ArticleInventaire.
    """

    model_config = {"extra": "forbid"}

    ingredient_id: int | None = None
    quantite: float | None = None
    quantite_min: float | None = None
    emplacement: str | None = None
    date_peremption: datetime | None = None
    code_barres: str | None = None
    prix_unitaire: float | None = None

    @field_validator("quantite")
    @classmethod
    def validate_quantite(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("La quantité ne peut pas être négative")
        return v

    @field_validator("emplacement")
    @classmethod
    def validate_emplacement(cls, v: str | None) -> str | None:
        if v is None:
            return v

        normalisations = {
            "frigo": "Frigo",
            "refrigerateur": "Frigo",
            "réfrigérateur": "Frigo",
            "congelateur tiroir": "Congélateur Tiroir",
            "congélateur tiroir": "Congélateur Tiroir",
            "congelateur coffre": "Congélateur Coffre",
            "congélateur coffre": "Congélateur Coffre",
            "cellier": "Cellier",
            "placard": "Placard",
        }
        emplacement_normalise = normalisations.get(v.strip().lower(), v)

        if emplacement_normalise not in EMPLACEMENTS_INVENTAIRE:
            raise ValueError(
                f"Emplacement invalide: '{v}'. "
                f"Valeurs acceptées: {', '.join(EMPLACEMENTS_INVENTAIRE)}"
            )
        return emplacement_normalise


# ═══════════════════════════════════════════════════════════
# RESPONSE
# ═══════════════════════════════════════════════════════════


class InventaireItemResponse(BaseModel):
    """Schéma de réponse pour un article d'inventaire.

    Résout ``nom``, ``unite`` et ``categorie`` depuis la relation Ingredient
    via ``from_attributes``.
    """

    id: int
    ingredient_id: int
    quantite: float
    quantite_min: float
    emplacement: str | None = None
    date_peremption: datetime | None = None
    code_barres: str | None = None
    prix_unitaire: float | None = None
    derniere_maj: datetime | None = None

    # Champs résolus depuis la relation Ingredient
    nom: str | None = None
    unite: str | None = None
    categorie: str | None = None

    # Données OpenFoodFacts (si code_barres enrichi)
    nutriscore: str | None = None
    ecoscore: str | None = None
    nova_group: int | None = None

    model_config = {"from_attributes": True}


class ArticleConsolideResponse(BaseModel):
    """Vue consolidée des stocks cuisine + cellier."""

    nom: str
    nom_normalise: str
    quantite_totale: float
    unite: str
    categories: list[str] = Field(default_factory=list)
    emplacements: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)  # cuisine | cellier
    details_sources: list[dict] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SCAN BATCH
# ═══════════════════════════════════════════════════════════


class ScanBatchRequest(BaseModel):
    """Requête pour résoudre plusieurs codes-barres en une passe."""

    codes: list[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Liste de codes-barres (max 50)",
    )


class ArticleBatchTrouve(BaseModel):
    """Article d'inventaire trouvé pour un code-barres donné."""

    code: str
    article: InventaireItemResponse


class ScanBatchResponse(BaseModel):
    """Résultat d'un scan multi-codes."""

    trouves: list[ArticleBatchTrouve]
    inconnus: list[str]

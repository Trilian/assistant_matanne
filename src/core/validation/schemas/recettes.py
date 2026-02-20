"""Schémas de validation pour les recettes."""

from pydantic import BaseModel, Field, field_validator, model_validator

from ...constants import (
    MAX_ETAPES,
    MAX_INGREDIENTS,
    MAX_LENGTH_LONG,
    MAX_LENGTH_MEDIUM,
    MAX_LENGTH_TEXT,
    MAX_PORTIONS,
    MAX_QUANTITE,
    MAX_TEMPS_CUISSON,
    MAX_TEMPS_PREPARATION,
    MIN_ETAPES,
    MIN_INGREDIENTS,
)
from ._helpers import nettoyer_texte


class IngredientInput(BaseModel):
    """
    Validation d'un ingrédient.

    Attributes:
        nom: Nom de l'ingrédient
        quantite: Quantité nécessaire (optionnel)
        unite: Unité de mesure (optionnel)
        optionnel: Est-ce optionnel
    """

    nom: str = Field(..., min_length=1, max_length=MAX_LENGTH_MEDIUM)
    quantite: float | None = Field(None, ge=0.01, le=MAX_QUANTITE)
    unite: str | None = Field(None, max_length=50)
    optionnel: bool = False

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        """Nettoie et normalise le nom"""
        return v.strip().capitalize()


class EtapeInput(BaseModel):
    """
    Validation d'une étape de recette.

    Attributes:
        numero: Numéro de l'étape (alias: ordre)
        ordre: Ordre de l'étape (alias de numero)
        description: Description de l'étape
        duree: Durée en minutes (optionnelle)
    """

    numero: int | None = Field(None, ge=1, le=MAX_ETAPES, description="Numéro de l'étape")
    ordre: int | None = Field(
        None, ge=1, le=MAX_ETAPES, description="Ordre de l'étape (alias de numero)"
    )
    description: str = Field(..., min_length=1, max_length=MAX_LENGTH_LONG)
    duree: int | None = Field(None, ge=0, le=MAX_TEMPS_CUISSON)

    model_config = {"populate_by_name": True}

    @field_validator("description")
    @classmethod
    def nettoyer_description(cls, v):
        return nettoyer_texte(v) if v else v

    @model_validator(mode="after")
    def valider_numero_ou_ordre(self) -> "EtapeInput":
        """Assure qu'au moins un de numero ou ordre est fourni"""
        if self.numero is None and self.ordre is None:
            raise ValueError("Soit 'numero' soit 'ordre' doit être fourni")
        # Utiliser ordre si numero n'est pas fourni
        if self.numero is None and self.ordre is not None:
            self.numero = self.ordre
        return self


class RecetteInput(BaseModel):
    """
    Validation complète d'une recette.

    Attributes:
        nom: Nom de la recette
        description: Description (optionnelle)
        temps_preparation: Temps de préparation en minutes
        temps_cuisson: Temps de cuisson en minutes
        portions: Nombre de portions
        difficulte: Niveau de difficulté
        type_repas: Type de repas
        saison: Saison recommandée
        ingredients: Liste des ingrédients
        etapes: Liste des étapes
    """

    nom: str = Field(..., min_length=1, max_length=MAX_LENGTH_MEDIUM)
    description: str | None = Field(None, max_length=MAX_LENGTH_TEXT)
    temps_preparation: int = Field(..., ge=1, le=MAX_TEMPS_PREPARATION)
    temps_cuisson: int = Field(..., ge=0, le=MAX_TEMPS_CUISSON)
    portions: int = Field(default=4, ge=1, le=MAX_PORTIONS)
    difficulte: str = Field(default="moyen", description="Niveau de difficulté")
    type_repas: str = Field(..., description="Type de repas")
    saison: str | None = Field(None, description="Saison (printemps, été, automne, hiver)")
    url_image: str | None = Field(None, max_length=500, description="URL ou chemin de l'image")
    ingredients: list[IngredientInput] = Field(
        ..., min_length=MIN_INGREDIENTS, max_length=MAX_INGREDIENTS
    )
    etapes: list[EtapeInput] = Field(..., min_length=MIN_ETAPES, max_length=MAX_ETAPES)

    @field_validator("nom")
    @classmethod
    def valider_nom(cls, v: str) -> str:
        """Nettoie et valide le nom"""
        cleaned = v.strip()
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned.upper()
        if len(cleaned) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
        return cleaned

    @field_validator("difficulte")
    @classmethod
    def valider_difficulte(cls, v: str) -> str:
        """Valide la difficulté"""
        difficultes_valides = {"facile", "moyen", "difficile"}
        if v.lower() not in difficultes_valides:
            raise ValueError(
                f"Difficulté invalide. Doit être parmi: {', '.join(difficultes_valides)}"
            )
        return v.lower()

    @field_validator("type_repas")
    @classmethod
    def valider_type_repas(cls, v: str) -> str:
        """Valide le type de repas"""
        types_valides = {"petit_déjeuner", "déjeuner", "dîner", "goûter", "apéritif", "dessert"}
        if v.lower() not in types_valides:
            raise ValueError(f"Type de repas invalide. Doit être parmi: {', '.join(types_valides)}")
        return v.lower()

    @field_validator("saison")
    @classmethod
    def valider_saison(cls, v: str | None) -> str | None:
        """Valide la saison"""
        if v:
            saisons_valides = {"printemps", "été", "automne", "hiver", "toute_année"}
            if v.lower() not in saisons_valides:
                raise ValueError(f"Saison invalide. Doit être parmi: {', '.join(saisons_valides)}")
            return v.lower()
        return None

    @model_validator(mode="after")
    def valider_temps_total(self) -> "RecetteInput":
        """Valide que le temps total n'est pas trop long"""
        temps_total = self.temps_preparation + self.temps_cuisson
        if temps_total > 1440:  # 24 heures
            raise ValueError("Temps total ne peut pas dépasser 24 heures")
        return self


# Schéma dict-based pour formulaires simples
SCHEMA_RECETTE = {
    "nom": {"type": "string", "max_length": MAX_LENGTH_MEDIUM, "required": True, "label": "Nom"},
    "description": {"type": "string", "max_length": MAX_LENGTH_TEXT, "label": "Description"},
    "temps_preparation": {
        "type": "number",
        "min": 1,
        "max": MAX_TEMPS_PREPARATION,
        "required": True,
        "label": "Temps préparation",
    },
    "temps_cuisson": {
        "type": "number",
        "min": 0,
        "max": MAX_TEMPS_CUISSON,
        "required": True,
        "label": "Temps cuisson",
    },
    "portions": {
        "type": "number",
        "min": 1,
        "max": MAX_PORTIONS,
        "required": True,
        "label": "Portions",
    },
}

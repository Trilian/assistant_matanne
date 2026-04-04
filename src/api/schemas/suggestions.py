"""
Schémas Pydantic pour les suggestions IA.

Modèles de réponse pour les endpoints de suggestions de recettes et planning.
"""

from typing import Any

from pydantic import BaseModel, Field


class SuggestionRecetteItem(BaseModel):
    """Un item de suggestion de recette."""

    nom: str = Field(description="Nom de la recette suggérée", max_length=200)
    description: str | None = Field(None, description="Description courte", max_length=500)
    temps_preparation: int | None = Field(None, description="Temps de préparation en minutes")
    raison: str | None = Field(None, description="Justification IA de la suggestion", max_length=300)

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "One pot pâtes saumon épinards",
                "description": "Un dîner rapide en une seule casserole.",
                "temps_preparation": 20,
                "raison": "Saumon en stock, recette rapide pour un soir de semaine.",
            }
        }
    }


class SuggestionsRecettesResponse(BaseModel):
    """Réponse pour les suggestions de recettes IA."""

    suggestions: list[Any] = Field(description="Liste des recettes suggérées")
    contexte: str = Field(description="Contexte utilisé pour la génération", max_length=1000)
    nombre: int = Field(description="Nombre de suggestions demandées")

    model_config = {
        "json_schema_extra": {
            "example": {
                "suggestions": [
                    {
                        "nom": "One pot pâtes saumon épinards",
                        "description": "Un dîner rapide en une seule casserole.",
                        "temps_preparation": 20,
                        "raison": "Saumon en stock, recette rapide pour un soir de semaine.",
                    }
                ],
                "contexte": "Soirs de semaine, 3 personnes, recettes rapides avec Jules.",
                "nombre": 3,
            }
        }
    }


class SuggestionsPlanningResponse(BaseModel):
    """Réponse pour les suggestions de planning IA."""

    planning: dict[str, Any] = Field(description="Planning structuré par jour")
    jours: int = Field(description="Nombre de jours planifiés")
    personnes: int = Field(description="Nombre de personnes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "planning": {
                    "lundi": {"midi": "Salade de pâtes", "soir": "Gratin de courgettes"},
                    "mardi": {"midi": "Restes", "soir": "Omelette aux herbes"},
                },
                "jours": 5,
                "personnes": 3,
            }
        }
    }


class IngredientDetecteResponse(BaseModel):
    """Ingrédient détecté dans une photo."""

    nom: str = Field(description="Nom de l'ingrédient", max_length=200)
    quantite_estimee: str | None = Field(None, description="Quantité estimée", max_length=100)
    confiance: float = Field(description="Score de confiance 0-1")

    model_config = {
        "json_schema_extra": {
            "example": {"nom": "Courgette", "quantite_estimee": "2 pièces", "confiance": 0.94}
        }
    }


class RecetteSuggestionResponse(BaseModel):
    """Recette suggérée à partir d'ingrédients."""

    nom: str = Field(description="Nom de la recette", max_length=200)
    description: str = Field(description="Description courte", max_length=500)
    temps_preparation: int | None = Field(None, description="Temps en minutes")
    ingredients_utilises: list[str] = Field(default_factory=list)
    ingredients_manquants: list[str] = Field(default_factory=list)


class PhotoFrigoResponse(BaseModel):
    """Réponse de l'analyse photo frigo."""

    ingredients_detectes: list[IngredientDetecteResponse] = Field(default_factory=list)
    recettes_suggerees: list[RecetteSuggestionResponse] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "ingredients_detectes": [
                    {"nom": "Courgette", "quantite_estimee": "2 pièces", "confiance": 0.94},
                    {"nom": "Crème fraîche", "quantite_estimee": "1 pot", "confiance": 0.81}
                ],
                "recettes_suggerees": [
                    {
                        "nom": "Gratin de courgettes",
                        "description": "Une recette simple pour utiliser les légumes du frigo.",
                        "temps_preparation": 15,
                        "ingredients_utilises": ["Courgette", "Crème fraîche"],
                        "ingredients_manquants": ["Parmesan"],
                    }
                ],
            }
        }
    }


class SubstitutionIngredientResponse(BaseModel):
    """Une alternative proposée pour remplacer un ingrédient manquant."""

    ingredient_original: str = Field(description="Ingrédient initialement prévu")
    ingredient_substitut: str = Field(description="Alternative recommandée")
    ratio: float = Field(default=1.0, description="Ratio d'équivalence à appliquer")
    impact_gout: str = Field(default="leger", description="neutre|leger|notable")
    tags: list[str] = Field(default_factory=list)
    note: str = Field(default="")
    disponible_en_stock: bool = Field(default=False)


class AdaptationRecetteResponse(BaseModel):
    """Réponse d'adaptation d'une recette quand il manque un ingrédient."""

    ingredient_manquant: str = Field(description="Ingrédient à remplacer")
    quantite_requise: float = Field(default=1.0)
    unite: str = Field(default="")
    substitutions: list[SubstitutionIngredientResponse] = Field(default_factory=list)
    meilleure_en_stock: SubstitutionIngredientResponse | None = Field(default=None)
    message: str = Field(default="")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ingredient_manquant": "crème fraîche",
                "quantite_requise": 20,
                "unite": "cl",
                "substitutions": [
                    {
                        "ingredient_original": "crème fraîche",
                        "ingredient_substitut": "yaourt nature",
                        "ratio": 1.0,
                        "impact_gout": "leger",
                        "tags": ["sans_lactose_possible"],
                        "note": "",
                        "disponible_en_stock": True,
                    }
                ],
                "meilleure_en_stock": {
                    "ingredient_original": "crème fraîche",
                    "ingredient_substitut": "yaourt nature",
                    "ratio": 1.0,
                    "impact_gout": "leger",
                    "tags": ["sans_lactose_possible"],
                    "note": "",
                    "disponible_en_stock": True,
                },
                "message": "Utilise yaourt nature à la même quantité pour conserver une sauce douce.",
            }
        }
    }

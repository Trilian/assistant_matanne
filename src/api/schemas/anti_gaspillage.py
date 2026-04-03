"""
Schémas Pydantic pour l'anti-gaspillage.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ArticlePerissable(BaseModel):
    """Article bientôt périmé."""

    id: int
    nom: str = Field(max_length=200)
    date_peremption: str
    jours_restants: int
    quantite: float | None = None
    unite: str | None = Field(None, max_length=20)

    model_config = {
        "json_schema_extra": {
            "example": {"id": 4, "nom": "Yaourts nature", "date_peremption": "2026-04-05", "jours_restants": 2, "quantite": 4, "unite": "pots"}
        }
    }


class RecetteRescue(BaseModel):
    """Recette suggérée pour utiliser les produits bientôt périmés."""

    id: int
    nom: str = Field(max_length=200)
    ingredients_utilises: list[str] = Field(default_factory=list)
    temps_total: int | None = None
    difficulte: str | None = Field(None, max_length=30)

    model_config = {
        "json_schema_extra": {
            "example": {"id": 12, "nom": "Clafoutis aux fruits", "ingredients_utilises": ["yaourts", "pommes"], "temps_total": 40, "difficulte": "facile"}
        }
    }


class ScoreAntiGaspillage(BaseModel):
    """Score global anti-gaspillage."""

    score: int = Field(ge=0, le=100, description="Score sur 100")
    articles_perimes_mois: int = 0
    articles_sauves_mois: int = 0
    economie_estimee: float = 0.0

    model_config = {
        "json_schema_extra": {
            "example": {"score": 82, "articles_perimes_mois": 1, "articles_sauves_mois": 7, "economie_estimee": 18.5}
        }
    }


class ReponseAntiGaspillage(BaseModel):
    """Réponse complète de l'endpoint anti-gaspillage."""

    score: ScoreAntiGaspillage
    articles_urgents: list[ArticlePerissable] = Field(default_factory=list)
    recettes_rescue: list[RecetteRescue] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "score": {"score": 82, "articles_perimes_mois": 1, "articles_sauves_mois": 7, "economie_estimee": 18.5},
                "articles_urgents": [{"id": 4, "nom": "Yaourts nature", "date_peremption": "2026-04-05", "jours_restants": 2, "quantite": 4, "unite": "pots"}],
                "recettes_rescue": [{"id": 12, "nom": "Clafoutis aux fruits", "ingredients_utilises": ["yaourts", "pommes"], "temps_total": 40, "difficulte": "facile"}],
            }
        }
    }

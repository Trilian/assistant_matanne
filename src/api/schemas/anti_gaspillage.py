"""
Schémas Pydantic pour l'anti-gaspillage.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ArticlePerissable(BaseModel):
    """Article bientôt périmé."""

    id: int
    nom: str
    date_peremption: str
    jours_restants: int
    quantite: float | None = None
    unite: str | None = None


class RecetteRescue(BaseModel):
    """Recette suggérée pour utiliser les produits bientôt périmés."""

    id: int
    nom: str
    ingredients_utilises: list[str] = Field(default_factory=list)
    temps_total: int | None = None
    difficulte: str | None = None


class ScoreAntiGaspillage(BaseModel):
    """Score global anti-gaspillage."""

    score: int = Field(ge=0, le=100, description="Score sur 100")
    articles_perimes_mois: int = 0
    articles_sauves_mois: int = 0
    economie_estimee: float = 0.0


class ReponseAntiGaspillage(BaseModel):
    """Réponse complète de l'endpoint anti-gaspillage."""

    score: ScoreAntiGaspillage
    articles_urgents: list[ArticlePerissable] = Field(default_factory=list)
    recettes_rescue: list[RecetteRescue] = Field(default_factory=list)

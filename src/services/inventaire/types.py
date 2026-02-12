"""
Types et schémas Pydantic pour le service inventaire.

Ce module contient les modèles de validation utilisés pour:
- Suggestions IA de courses
- Import d'articles en batch
"""

from pydantic import BaseModel, Field


class SuggestionCourses(BaseModel):
    """Suggestion d'achat générée par l'IA.
    
    Attributes:
        nom: Nom de l'article suggéré
        quantite: Quantité recommandée
        unite: Unité de mesure
        priorite: Niveau de priorité (haute, moyenne, basse)
        rayon: Rayon du magasin
    """
    nom: str = Field(..., min_length=2)
    quantite: float = Field(..., gt=0)
    unite: str = Field(..., min_length=1)
    priorite: str = Field(..., pattern="^(haute|moyenne|basse)$")
    rayon: str = Field(..., min_length=3)


class ArticleImport(BaseModel):
    """Modèle pour importer un article en batch.
    
    Attributes:
        nom: Nom de l'article
        quantite: Quantité en stock
        quantite_min: Seuil minimum de stock
        unite: Unité de mesure
        categorie: Catégorie de l'article (optionnel)
        emplacement: Lieu de stockage (optionnel)
        date_peremption: Date de péremption au format YYYY-MM-DD (optionnel)
    """
    nom: str = Field(..., min_length=2)
    quantite: float = Field(..., ge=0)
    quantite_min: float = Field(..., ge=0)
    unite: str = Field(..., min_length=1)
    categorie: str | None = None
    emplacement: str | None = None
    date_peremption: str | None = None  # Format: YYYY-MM-DD


__all__ = [
    "SuggestionCourses",
    "ArticleImport",
]

"""
Schémas Pydantic pour le service de suggestions IA.

Définit les modèles de données:
- ProfilCulinaire: Profil déduit de l'historique
- ContexteSuggestion: Contexte pour générer des suggestions
- SuggestionRecette: Suggestion scorée
"""

from pydantic import BaseModel, Field


class ProfilCulinaire(BaseModel):
    """Profil culinaire déduit de l'historique."""
    
    categories_preferees: list[str] = Field(default_factory=list)
    ingredients_frequents: list[str] = Field(default_factory=list)
    ingredients_evites: list[str] = Field(default_factory=list)
    difficulte_moyenne: str = "moyen"
    temps_moyen_minutes: int = 45
    nb_portions_habituel: int = 4
    recettes_favorites: list[int] = Field(default_factory=list)
    jours_depuis_derniere_recette: dict = Field(default_factory=dict)


class ContexteSuggestion(BaseModel):
    """Contexte pour générer des suggestions."""
    
    type_repas: str = "dîner"
    nb_personnes: int = 4
    temps_disponible_minutes: int = 60
    ingredients_disponibles: list[str] = Field(default_factory=list)
    ingredients_a_utiliser: list[str] = Field(default_factory=list)  # À consommer en priorité
    contraintes: list[str] = Field(default_factory=list)  # végétarien, sans gluten, etc.
    saison: str = ""
    budget: str = "normal"  # économique, normal, gastronomique


class SuggestionRecette(BaseModel):
    """Suggestion de recette avec scoring."""
    
    recette_id: int | None = None
    nom: str = ""
    raison: str = ""  # Pourquoi cette suggestion
    score: float = 0.0
    tags: list[str] = Field(default_factory=list)
    temps_preparation: int = 0
    difficulte: str = ""
    ingredients_manquants: list[str] = Field(default_factory=list)
    est_nouvelle: bool = False  # Jamais préparée


__all__ = [
    "ProfilCulinaire",
    "ContexteSuggestion",
    "SuggestionRecette",
]

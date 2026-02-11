"""
Types et schémas Pydantic pour le package courses.

Module unifié avec tous les modèles de données pour les services de courses.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SuggestionCourses(BaseModel):
    """Suggestion de course depuis l'IA."""
    nom: str = Field(..., min_length=2)
    quantite: float = Field(..., gt=0)
    unite: str = Field(..., min_length=1)
    priorite: str = Field(..., pattern="^(haute|moyenne|basse)$")
    rayon: str = Field(..., min_length=3)
    
    @classmethod
    def model_validate(cls, obj):
        """Normalise les noms de champs alternatifs avant validation."""
        if isinstance(obj, dict):
            # Normaliser variantes de champs
            field_aliases = {
                'article': 'nom',
                'name': 'nom',
                'item': 'nom',
                'product': 'nom',
                'quantity': 'quantite',
                'amount': 'quantite',
                'unit': 'unite',
                'priority': 'priorite',
                'section': 'rayon',
                'department': 'rayon',
            }
            
            for alias, canonical in field_aliases.items():
                if alias in obj and canonical not in obj:
                    obj[canonical] = obj.pop(alias)
            
            # Normaliser les valeurs de priorite
            if 'priorite' in obj:
                priorite = str(obj['priorite']).lower().strip()
                if 'haut' in priorite or 'high' in priorite:
                    obj['priorite'] = 'haute'
                elif 'moyen' in priorite or 'medium' in priorite:
                    obj['priorite'] = 'moyenne'
                elif 'bas' in priorite or 'low' in priorite:
                    obj['priorite'] = 'basse'
        
        return super().model_validate(obj)


class ArticleCourse(BaseModel):
    """Article a ajouter a la liste de courses."""
    nom: str = Field(description="Nom de l'ingredient")
    quantite: float = Field(description="Quantite necessaire")
    unite: str = Field(default="", description="Unite de mesure")
    rayon: str = Field(default="Autre", description="Rayon du magasin")
    recettes_source: list[str] = Field(default_factory=list, description="Recettes necessitant cet ingredient")
    priorite: int = Field(default=2, description="Priorite 1-3")
    en_stock: float = Field(default=0, description="Quantite deja en stock")
    a_acheter: float = Field(default=0, description="Quantite a acheter")
    notes: str = Field(default="", description="Notes")


class ListeCoursesIntelligente(BaseModel):
    """Liste de courses generee intelligemment."""
    articles: list[ArticleCourse] = Field(default_factory=list)
    total_articles: int = Field(default=0)
    recettes_couvertes: list[str] = Field(default_factory=list)
    estimation_budget: Optional[float] = Field(default=None)
    alertes: list[str] = Field(default_factory=list)


class SuggestionSubstitution(BaseModel):
    """Suggestion de substitution d'ingredient."""
    ingredient_original: str
    suggestion: str
    raison: str
    economie_estimee: Optional[float] = None


# Aliases pour compatibilite
ShoppingSuggestion = SuggestionCourses
ShoppingItem = ArticleCourse
SmartShoppingList = ListeCoursesIntelligente
SubstitutionSuggestion = SuggestionSubstitution

__all__ = [
    # Noms francais
    "SuggestionCourses",
    "ArticleCourse", 
    "ListeCoursesIntelligente",
    "SuggestionSubstitution",
    # Aliases anglais
    "ShoppingSuggestion",
    "ShoppingItem",
    "SmartShoppingList",
    "SubstitutionSuggestion",
]

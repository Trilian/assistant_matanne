"""
DTOs pour le domaine Courses.

Fournit les objets de transfert entre ServiceCourses et les modules UI.
"""

from datetime import datetime

from pydantic import Field

from .base import BaseDTO, IdentifiedDTO


class ArticleCoursesDTO(IdentifiedDTO):
    """Article dans une liste de courses."""

    liste_id: int = 0
    ingredient_id: int = 0
    ingredient_nom: str = ""
    quantite_necessaire: float = 0.0
    unite: str = ""
    priorite: str = "moyenne"
    achete: bool = False
    achete_le: datetime | None = None
    suggere_par_ia: bool = False
    rayon_magasin: str | None = None
    magasin_cible: str | None = None
    notes: str | None = None
    categorie: str | None = None


class ListeCoursesDTO(IdentifiedDTO):
    """Liste de courses avec ses articles."""

    nom: str = ""
    archivee: bool = False
    articles: list[ArticleCoursesDTO] = Field(default_factory=list)

    @property
    def nb_articles(self) -> int:
        """Nombre total d'articles."""
        return len(self.articles)

    @property
    def nb_achetes(self) -> int:
        """Nombre d'articles achetés."""
        return sum(1 for a in self.articles if a.achete)

    @property
    def progression(self) -> float:
        """Pourcentage de progression (0.0 à 1.0)."""
        if not self.articles:
            return 0.0
        return self.nb_achetes / self.nb_articles


__all__ = [
    "ArticleCoursesDTO",
    "ListeCoursesDTO",
]

"""
DTOs pour le domaine Inventaire.

Fournit les objets de transfert entre ServiceInventaire et les modules UI.
"""

from datetime import date, datetime

from .base import BaseDTO, IdentifiedDTO


class ArticleInventaireResumeDTO(IdentifiedDTO):
    """Vue résumée d'un article en stock."""

    ingredient_nom: str = ""
    quantite: float = 0.0
    quantite_min: float = 1.0
    emplacement: str | None = None
    date_peremption: date | None = None
    derniere_maj: datetime | None = None

    @property
    def stock_bas(self) -> bool:
        """Vérifie si le stock est sous le seuil minimum."""
        return self.quantite < self.quantite_min

    @property
    def perime(self) -> bool:
        """Vérifie si l'article est périmé."""
        if self.date_peremption is None:
            return False
        return self.date_peremption < date.today()


class ArticleInventaireDTO(ArticleInventaireResumeDTO):
    """Vue complète d'un article en stock."""

    ingredient_id: int = 0
    unite: str = "pcs"
    categorie: str | None = None
    code_barres: str | None = None
    prix_unitaire: float | None = None
    photo_url: str | None = None


__all__ = [
    "ArticleInventaireResumeDTO",
    "ArticleInventaireDTO",
]

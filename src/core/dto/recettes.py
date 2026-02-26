"""
DTOs pour le domaine Recettes.

Fournit les objets de transfert entre ServiceRecettes et les modules UI.
"""

from datetime import datetime

from pydantic import Field

from .base import BaseDTO, IdentifiedDTO


class IngredientDTO(BaseDTO):
    """Ingrédient dans une recette."""

    nom: str
    quantite: float | None = None
    unite: str | None = None
    categorie: str | None = None
    optionnel: bool = False


class RecetteResumeDTO(IdentifiedDTO):
    """Vue résumée d'une recette (pour les listes)."""

    nom: str
    description: str | None = None
    temps_preparation: int = 0
    temps_cuisson: int = 0
    portions: int = 4
    difficulte: str = "moyen"
    type_repas: str = "dîner"
    saison: str = "toute_année"
    categorie: str | None = None

    # Flags
    est_rapide: bool = False
    est_equilibre: bool = False
    compatible_bebe: bool = False
    compatible_batch: bool = False
    congelable: bool = False
    est_vegetarien: bool = False

    # Bio
    est_bio: bool = False
    est_local: bool = False
    score_bio: int = 0
    score_local: int = 0

    # Robots
    compatible_cookeo: bool = False
    compatible_monsieur_cuisine: bool = False
    compatible_airfryer: bool = False

    # Nutrition
    calories: int | None = None
    proteines: float | None = None
    lipides: float | None = None
    glucides: float | None = None

    # IA
    genere_par_ia: bool = False
    url_image: str | None = None

    @property
    def temps_total(self) -> int:
        """Temps total de préparation + cuisson."""
        return self.temps_preparation + self.temps_cuisson


class EtapeRecetteDTO(BaseDTO):
    """Étape de préparation d'une recette."""

    numero: int
    description: str
    duree_minutes: int | None = None


class RecetteDTO(RecetteResumeDTO):
    """Vue complète d'une recette avec ingrédients et étapes."""

    ingredients: list[IngredientDTO] = Field(default_factory=list)
    etapes: list[EtapeRecetteDTO] = Field(default_factory=list)
    type_proteines: str | None = None
    score_ia: float | None = None


__all__ = [
    "IngredientDTO",
    "RecetteResumeDTO",
    "RecetteDTO",
    "EtapeRecetteDTO",
]

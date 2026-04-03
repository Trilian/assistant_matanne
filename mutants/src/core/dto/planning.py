"""
DTOs pour le domaine Planning.

Fournit les objets de transfert entre ServicePlanning et les modules UI.
"""

from datetime import date

from pydantic import Field

from .base import BaseDTO, IdentifiedDTO


class RepasDTO(IdentifiedDTO):
    """Repas planifié dans un planning."""

    planning_id: int = 0
    recette_id: int | None = None
    recette_nom: str = ""
    date_repas: date | None = None
    type_repas: str = "dîner"
    portion_ajustee: int | None = None
    prepare: bool = False
    notes: str | None = None


class PlanningResumeDTO(IdentifiedDTO):
    """Vue résumée d'un planning hebdomadaire."""

    nom: str = ""
    semaine_debut: date | None = None
    semaine_fin: date | None = None
    actif: bool = True
    genere_par_ia: bool = False
    notes: str | None = None
    repas: list[RepasDTO] = Field(default_factory=list)

    @property
    def nb_repas(self) -> int:
        """Nombre total de repas planifiés."""
        return len(self.repas)

    @property
    def nb_prepares(self) -> int:
        """Nombre de repas préparés."""
        return sum(1 for r in self.repas if r.prepare)


__all__ = [
    "PlanningResumeDTO",
    "RepasDTO",
]

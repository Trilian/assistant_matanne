"""
DTOs pour le domaine Maison.

Fournit les objets de transfert entre les services maison et les modules UI.
"""

import datetime as dt
from datetime import date
from decimal import Decimal

from pydantic import Field

from .base import BaseDTO, IdentifiedDTO

# ═══════════════════════════════════════════════════════════
# PROJETS DOMESTIQUES
# ═══════════════════════════════════════════════════════════


class TacheProjetDTO(BaseDTO):
    """Tâche d'un projet domestique."""

    id: int = 0
    nom: str = ""
    description: str | None = None
    statut: str = "à_faire"
    priorite: str = "moyenne"
    date_echeance: date | None = None
    assigne_a: str | None = None


class ProjetDTO(IdentifiedDTO):
    """Vue d'un projet domestique avec ses tâches."""

    nom: str = ""
    description: str | None = None
    statut: str = "en_cours"
    priorite: str = "moyenne"
    date_debut: date | None = None
    date_fin_prevue: date | None = None
    date_fin_reelle: date | None = None
    taches: list[TacheProjetDTO] = Field(default_factory=list)

    @property
    def nb_taches(self) -> int:
        """Nombre de tâches."""
        return len(self.taches)

    @property
    def nb_terminees(self) -> int:
        """Nombre de tâches terminées."""
        return sum(1 for t in self.taches if t.statut == "terminé")

    @property
    def progression(self) -> float:
        """Progression du projet (0.0 à 1.0)."""
        if not self.taches:
            return 0.0
        return self.nb_terminees / self.nb_taches


# ═══════════════════════════════════════════════════════════
# ROUTINES D'ENTRETIEN
# ═══════════════════════════════════════════════════════════


class RoutineEntretienDTO(IdentifiedDTO):
    """Vue d'une routine d'entretien maison."""

    nom: str = ""
    description: str | None = None
    categorie: str | None = None
    frequence: str = "quotidien"
    actif: bool = True


# ═══════════════════════════════════════════════════════════
# JARDIN
# ═══════════════════════════════════════════════════════════


class ElementJardinDTO(IdentifiedDTO):
    """Vue d'un élément du jardin."""

    nom: str = ""
    type: str = ""
    location: str | None = None
    statut: str = "actif"
    date_plantation: date | None = None
    date_recolte_prevue: date | None = None
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# DÉPENSES
# ═══════════════════════════════════════════════════════════


class DepenseDTO(IdentifiedDTO):
    """Vue d'une dépense familiale."""

    montant: float = 0.0
    categorie: str = "autre"
    description: str | None = None
    date: dt.date | None = None
    recurrence: str | None = None
    tags: list[str] = Field(default_factory=list)

    @property
    def est_recurrente(self) -> bool:
        """Vérifie si la dépense est récurrente."""
        return self.recurrence is not None and self.recurrence != "ponctuel"


__all__ = [
    "TacheProjetDTO",
    "ProjetDTO",
    "RoutineEntretienDTO",
    "ElementJardinDTO",
    "DepenseDTO",
]

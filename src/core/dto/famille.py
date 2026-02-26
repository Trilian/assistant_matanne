"""
DTOs pour le domaine Famille.

Fournit les objets de transfert entre les services famille et les modules UI.
"""

from datetime import date, datetime

from pydantic import Field

from .base import BaseDTO, IdentifiedDTO

# ═══════════════════════════════════════════════════════════
# PROFIL ENFANT
# ═══════════════════════════════════════════════════════════


class ProfilEnfantDTO(IdentifiedDTO):
    """Vue d'un profil enfant."""

    name: str = ""
    date_of_birth: date | None = None
    gender: str | None = None
    notes: str | None = None
    actif: bool = True

    @property
    def age_mois(self) -> int | None:
        """Âge en mois (approximatif)."""
        if self.date_of_birth is None:
            return None
        today = date.today()
        return (today.year - self.date_of_birth.year) * 12 + (
            today.month - self.date_of_birth.month
        )


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS FAMILLE
# ═══════════════════════════════════════════════════════════


class ActiviteFamilleDTO(IdentifiedDTO):
    """Vue d'une activité familiale."""

    titre: str = ""
    description: str | None = None
    type_activite: str = ""
    date_prevue: date | None = None
    duree_heures: float | None = None
    lieu: str | None = None
    qui_participe: list[str] = Field(default_factory=list)
    age_minimal_recommande: int | None = None
    cout_estime: float | None = None
    cout_reel: float | None = None
    statut: str = "planifié"
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS WEEKEND
# ═══════════════════════════════════════════════════════════


class ActiviteWeekendDTO(IdentifiedDTO):
    """Vue d'une activité weekend."""

    titre: str = ""
    description: str | None = None
    type_activite: str = ""
    date_prevue: date | None = None
    heure_debut: str | None = None
    duree_estimee_h: float | None = None
    lieu: str | None = None
    adresse: str | None = None
    adapte_jules: bool = True
    age_min_mois: int | None = None
    cout_estime: float | None = None
    cout_reel: float | None = None
    meteo_requise: str | None = None
    statut: str = "planifié"
    note_lieu: int | None = None
    commentaire: str | None = None
    a_refaire: bool | None = None
    participants: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# ROUTINES FAMILLE
# ═══════════════════════════════════════════════════════════


class TacheRoutineDTO(BaseDTO):
    """Tâche dans une routine."""

    id: int = 0
    nom: str = ""
    description: str | None = None
    ordre: int = 1
    heure_prevue: str | None = None
    fait_le: date | None = None
    notes: str | None = None


class RoutineFamilleDTO(IdentifiedDTO):
    """Vue d'une routine familiale avec ses tâches."""

    nom: str = ""
    description: str | None = None
    categorie: str | None = None
    frequence: str = "quotidien"
    actif: bool = True
    taches: list[TacheRoutineDTO] = Field(default_factory=list)

    @property
    def nb_taches(self) -> int:
        """Nombre total de tâches."""
        return len(self.taches)


__all__ = [
    "ProfilEnfantDTO",
    "ActiviteFamilleDTO",
    "ActiviteWeekendDTO",
    "RoutineFamilleDTO",
    "TacheRoutineDTO",
]

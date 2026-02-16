"""
Types et dataclasses pour le Calendrier Familial Unifié.

Contient:
- TypeEvenement (enum)
- Mappings EMOJI_TYPE et COULEUR_TYPE
- Dataclasses: EvenementCalendrier, JourCalendrier, SemaineCalendrier
"""

from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import StrEnum

from src.modules.shared.constantes import JOURS_SEMAINE, JOURS_SEMAINE_COURT

# ═══════════════════════════════════════════════════════════
# CONSTANTES LOCALES
# ═══════════════════════════════════════════════════════════


class TypeEvenement(StrEnum):
    """Types d'evenements dans le calendrier unifie."""

    REPAS_MIDI = "repas_midi"
    REPAS_SOIR = "repas_soir"
    GOUTER = "gouter"
    BATCH_COOKING = "batch_cooking"
    COURSES = "courses"
    ACTIVITE = "activite"
    RDV_MEDICAL = "rdv_medical"
    RDV_AUTRE = "rdv_autre"
    ROUTINE = "routine"
    MENAGE = "menage"  # 🧹 Tâches menage
    JARDIN = "jardin"  # 🌱 Tâches jardin
    ENTRETIEN = "entretien"  # 🔧 Entretien maison
    EVENEMENT = "evenement"


# Emojis par type d'evenement
EMOJI_TYPE = {
    TypeEvenement.REPAS_MIDI: "🌞",
    TypeEvenement.REPAS_SOIR: "🌙",
    TypeEvenement.GOUTER: "🍰",
    TypeEvenement.BATCH_COOKING: "🍳",
    TypeEvenement.COURSES: "🛒",
    TypeEvenement.ACTIVITE: "🎨",
    TypeEvenement.RDV_MEDICAL: "🏥",
    TypeEvenement.RDV_AUTRE: "📅",
    TypeEvenement.ROUTINE: "⏰",
    TypeEvenement.MENAGE: "🧹",
    TypeEvenement.JARDIN: "🌱",
    TypeEvenement.ENTRETIEN: "🔧",
    TypeEvenement.EVENEMENT: "📜",
}

# Couleurs par type (pour l'affichage)
COULEUR_TYPE = {
    TypeEvenement.REPAS_MIDI: "#FFB74D",  # Orange clair
    TypeEvenement.REPAS_SOIR: "#7986CB",  # Bleu/violet
    TypeEvenement.GOUTER: "#F48FB1",  # Rose
    TypeEvenement.BATCH_COOKING: "#81C784",  # Vert
    TypeEvenement.COURSES: "#4DD0E1",  # Cyan
    TypeEvenement.ACTIVITE: "#BA68C8",  # Violet
    TypeEvenement.RDV_MEDICAL: "#E57373",  # Rouge clair
    TypeEvenement.RDV_AUTRE: "#90A4AE",  # Gris
    TypeEvenement.ROUTINE: "#A1887F",  # Marron
    TypeEvenement.MENAGE: "#FFCC80",  # Orange pâle
    TypeEvenement.JARDIN: "#A5D6A7",  # Vert pâle
    TypeEvenement.ENTRETIEN: "#BCAAA4",  # Marron clair
    TypeEvenement.EVENEMENT: "#64B5F6",  # Bleu
}


# ═══════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════


@dataclass
class EvenementCalendrier:
    """Évenement unifie dans le calendrier."""

    id: str  # Format: "{type}_{id_source}"
    type: TypeEvenement
    titre: str
    date_jour: date
    heure_debut: time | None = None
    heure_fin: time | None = None
    description: str | None = None
    lieu: str | None = None
    participants: list[str] = field(default_factory=list)
    pour_jules: bool = False
    version_jules: str | None = None  # Instructions adaptees Jules
    budget: float | None = None
    magasin: str | None = None  # Pour courses
    recette_id: int | None = None  # Pour repas
    session_id: int | None = None  # Pour batch
    termine: bool = False
    notes: str | None = None

    @property
    def emoji(self) -> str:
        return EMOJI_TYPE.get(self.type, "📜")

    @property
    def couleur(self) -> str:
        return COULEUR_TYPE.get(self.type, "#90A4AE")

    @property
    def heure_str(self) -> str:
        if self.heure_debut:
            return self.heure_debut.strftime("%H:%M")
        return ""


@dataclass
class JourCalendrier:
    """Representation d'un jour dans le calendrier."""

    date_jour: date
    evenements: list[EvenementCalendrier] = field(default_factory=list)

    @property
    def est_aujourdhui(self) -> bool:
        return self.date_jour == date.today()

    @property
    def jour_semaine(self) -> str:
        return JOURS_SEMAINE[self.date_jour.weekday()]

    @property
    def jour_semaine_court(self) -> str:
        return JOURS_SEMAINE_COURT[self.date_jour.weekday()]

    @property
    def repas_midi(self) -> EvenementCalendrier | None:
        for evt in self.evenements:
            if evt.type == TypeEvenement.REPAS_MIDI:
                return evt
        return None

    @property
    def repas_soir(self) -> EvenementCalendrier | None:
        for evt in self.evenements:
            if evt.type == TypeEvenement.REPAS_SOIR:
                return evt
        return None

    @property
    def gouter(self) -> EvenementCalendrier | None:
        for evt in self.evenements:
            if evt.type == TypeEvenement.GOUTER:
                return evt
        return None

    @property
    def batch_cooking(self) -> EvenementCalendrier | None:
        for evt in self.evenements:
            if evt.type == TypeEvenement.BATCH_COOKING:
                return evt
        return None

    @property
    def courses(self) -> list[EvenementCalendrier]:
        return [evt for evt in self.evenements if evt.type == TypeEvenement.COURSES]

    @property
    def activites(self) -> list[EvenementCalendrier]:
        return [evt for evt in self.evenements if evt.type == TypeEvenement.ACTIVITE]

    @property
    def rdv(self) -> list[EvenementCalendrier]:
        return [
            evt
            for evt in self.evenements
            if evt.type in (TypeEvenement.RDV_MEDICAL, TypeEvenement.RDV_AUTRE)
        ]

    @property
    def taches_menage(self) -> list[EvenementCalendrier]:
        """Tâches menage du jour."""
        return [
            evt
            for evt in self.evenements
            if evt.type in (TypeEvenement.MENAGE, TypeEvenement.ENTRETIEN)
        ]

    @property
    def taches_jardin(self) -> list[EvenementCalendrier]:
        """Tâches jardin du jour."""
        return [evt for evt in self.evenements if evt.type == TypeEvenement.JARDIN]

    @property
    def autres_evenements(self) -> list[EvenementCalendrier]:
        types_principaux = {
            TypeEvenement.REPAS_MIDI,
            TypeEvenement.REPAS_SOIR,
            TypeEvenement.GOUTER,
            TypeEvenement.BATCH_COOKING,
            TypeEvenement.COURSES,
            TypeEvenement.ACTIVITE,
            TypeEvenement.RDV_MEDICAL,
            TypeEvenement.RDV_AUTRE,
            TypeEvenement.MENAGE,
            TypeEvenement.JARDIN,
            TypeEvenement.ENTRETIEN,
        }
        return [evt for evt in self.evenements if evt.type not in types_principaux]

    @property
    def nb_evenements(self) -> int:
        return len(self.evenements)

    @property
    def est_vide(self) -> bool:
        return len(self.evenements) == 0

    @property
    def a_repas_planifies(self) -> bool:
        return self.repas_midi is not None or self.repas_soir is not None


@dataclass
class SemaineCalendrier:
    """Representation d'une semaine dans le calendrier."""

    date_debut: date  # Toujours un lundi
    jours: list[JourCalendrier] = field(default_factory=list)

    @property
    def date_fin(self) -> date:
        return self.date_debut + timedelta(days=6)

    @property
    def titre(self) -> str:
        return f"{self.date_debut.strftime('%d/%m')} — {self.date_fin.strftime('%d/%m/%Y')}"

    @property
    def nb_repas_planifies(self) -> int:
        count = 0
        for jour in self.jours:
            if jour.repas_midi:
                count += 1
            if jour.repas_soir:
                count += 1
        return count

    @property
    def nb_sessions_batch(self) -> int:
        return sum(1 for jour in self.jours if jour.batch_cooking)

    @property
    def nb_courses(self) -> int:
        return sum(len(jour.courses) for jour in self.jours)

    @property
    def nb_activites(self) -> int:
        return sum(len(jour.activites) for jour in self.jours)


__all__ = [
    "TypeEvenement",
    "EMOJI_TYPE",
    "COULEUR_TYPE",
    "EvenementCalendrier",
    "JourCalendrier",
    "SemaineCalendrier",
]

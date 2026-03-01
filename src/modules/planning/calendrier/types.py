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

from src.core.constants import JOURS_SEMAINE, JOURS_SEMAINE_COURT
from src.ui.tokens import Couleur

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
    FERIE = "ferie"  # ⭐ Jour férié
    CRECHE = "creche"  # 🏫 Fermeture crèche
    PONT = "pont"  # 🌉 Jour de pont


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
    TypeEvenement.FERIE: "⭐",
    TypeEvenement.CRECHE: "🏫",
    TypeEvenement.PONT: "🌉",
}

# Couleurs par type (pour l'affichage)
COULEUR_TYPE = {
    TypeEvenement.REPAS_MIDI: Couleur.CHART_BREAKFAST,
    TypeEvenement.REPAS_SOIR: Couleur.CAL_REPAS_SOIR,
    TypeEvenement.GOUTER: Couleur.CAL_GOUTER,
    TypeEvenement.BATCH_COOKING: Couleur.CAL_BATCH,
    TypeEvenement.COURSES: Couleur.CAL_COURSES,
    TypeEvenement.ACTIVITE: Couleur.CAL_ACTIVITE,
    TypeEvenement.RDV_MEDICAL: Couleur.CAL_RDV_MEDICAL,
    TypeEvenement.RDV_AUTRE: Couleur.CAL_RDV_AUTRE,
    TypeEvenement.ROUTINE: Couleur.CAL_ROUTINE,
    TypeEvenement.MENAGE: Couleur.CAL_MENAGE,
    TypeEvenement.JARDIN: Couleur.CAL_JARDIN,
    TypeEvenement.ENTRETIEN: Couleur.CAL_ENTRETIEN,
    TypeEvenement.EVENEMENT: Couleur.CAL_EVENEMENT,
    TypeEvenement.FERIE: Couleur.CAL_FERIE,
    TypeEvenement.CRECHE: Couleur.CAL_CRECHE,
    TypeEvenement.PONT: Couleur.CAL_PONT,
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
    def jours_speciaux(self) -> list[EvenementCalendrier]:
        """Jours fériés, fermetures crèche et ponts du jour."""
        return [
            evt
            for evt in self.evenements
            if evt.type in (TypeEvenement.FERIE, TypeEvenement.CRECHE, TypeEvenement.PONT)
        ]

    @property
    def est_jour_special(self) -> bool:
        """True si le jour contient un jour férié, crèche ou pont."""
        return len(self.jours_speciaux) > 0

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
            TypeEvenement.FERIE,
            TypeEvenement.CRECHE,
            TypeEvenement.PONT,
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

    @property
    def charge_score(self) -> int:
        """Score de charge du jour (0-100) basé sur le nombre et type d'événements.

        Pondération:
        - Repas: 5 pts chacun (routine quotidienne)
        - RDV médical: 20 pts (stressant/contraignant)
        - Batch cooking: 15 pts (effort conséquent)
        - Activité: 10 pts
        - Courses: 10 pts
        - Tâches ménage: 5 pts chacune
        - Autres: 5 pts
        """
        score = 0
        for evt in self.evenements:
            if evt.type in (
                TypeEvenement.REPAS_MIDI,
                TypeEvenement.REPAS_SOIR,
                TypeEvenement.GOUTER,
            ):
                score += 5
            elif evt.type == TypeEvenement.RDV_MEDICAL:
                score += 20
            elif evt.type == TypeEvenement.BATCH_COOKING:
                score += 15
            elif evt.type in (TypeEvenement.ACTIVITE, TypeEvenement.COURSES):
                score += 10
            elif evt.type in (TypeEvenement.MENAGE, TypeEvenement.ENTRETIEN, TypeEvenement.JARDIN):
                score += 5
            elif evt.type == TypeEvenement.RDV_AUTRE:
                score += 10
            else:
                score += 5
        return min(score, 100)


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

    @property
    def stats(self) -> dict:
        """Statistiques agrégées de la semaine (calculées dynamiquement)."""
        activites_jules = sum(1 for jour in self.jours for evt in jour.evenements if evt.pour_jules)
        budget_total = sum(evt.budget or 0 for jour in self.jours for evt in jour.evenements)
        charges = [jour.charge_score for jour in self.jours] if self.jours else [0]
        charge_moyenne = sum(charges) / len(charges) if charges else 0

        if charge_moyenne >= 70:
            charge_globale = "intense"
        elif charge_moyenne >= 40:
            charge_globale = "normal"
        else:
            charge_globale = "faible"

        return {
            "repas": self.nb_repas_planifies,
            "activites": self.nb_activites,
            "events": sum(len(jour.evenements) for jour in self.jours),
            "projets": 0,
            "activites_jules": activites_jules,
            "budget": budget_total,
            "charge_moyenne": int(charge_moyenne),
            "charge_globale": charge_globale,
        }


__all__ = [
    "TypeEvenement",
    "EMOJI_TYPE",
    "COULEUR_TYPE",
    "EvenementCalendrier",
    "JourCalendrier",
    "SemaineCalendrier",
]

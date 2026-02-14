"""
Logique metier du Calendrier Familial Unifie

Agrège TOUS les evenements familiaux dans une vue unique:
- Repas (planning cuisine)
- Sessions batch cooking
- Courses planifiees
- Activites famille
- RDV medicaux et evenements
- Routines

Separee de l'UI pour être testable sans Streamlit.
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any

from src.modules.shared.constantes import JOURS_SEMAINE, JOURS_SEMAINE_COURT
from src.modules.shared.date_utils import (
    obtenir_debut_semaine as get_debut_semaine,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES LOCALES
# ═══════════════════════════════════════════════════════════


class TypeEvenement(str, Enum):
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
    TypeEvenement.RDV_AUTRE: "📝…",
    TypeEvenement.ROUTINE: "⏰",
    TypeEvenement.MENAGE: "🧹",
    TypeEvenement.JARDIN: "🌱",
    TypeEvenement.ENTRETIEN: "🔧",
    TypeEvenement.EVENEMENT: "📝Œ",
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
        return EMOJI_TYPE.get(self.type, "📝Œ")

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


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE CALCUL (importees de shared/date_utils.py)
# get_debut_semaine, get_fin_semaine importes en haut du fichier


def get_jours_semaine(date_debut: date) -> list[date]:
    """Retourne les 7 jours de la semaine a partir du lundi."""
    lundi = get_debut_semaine(date_debut)
    return [lundi + timedelta(days=i) for i in range(7)]


def get_semaine_precedente(date_debut: date) -> date:
    """Retourne le lundi de la semaine precedente."""
    return get_debut_semaine(date_debut) - timedelta(days=7)


def get_semaine_suivante(date_debut: date) -> date:
    """Retourne le lundi de la semaine suivante."""
    return get_debut_semaine(date_debut) + timedelta(days=7)


# ═══════════════════════════════════════════════════════════
# AGRÉGATION DES ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


def convertir_repas_en_evenement(repas: Any) -> EvenementCalendrier | None:
    """Convertit un objet Repas SQLAlchemy en EvenementCalendrier."""
    if not repas:
        return None

    try:
        type_evt = (
            TypeEvenement.REPAS_SOIR if repas.type_repas == "dîner" else TypeEvenement.REPAS_MIDI
        )

        # Recuperer le nom de la recette si disponible
        titre = "Repas non defini"
        version_jules = None
        recette_id = None

        if hasattr(repas, "recette") and repas.recette:
            titre = repas.recette.nom
            recette_id = repas.recette.id
            # Version Jules si disponible
            if hasattr(repas.recette, "instructions_bebe") and repas.recette.instructions_bebe:
                version_jules = repas.recette.instructions_bebe

        return EvenementCalendrier(
            id=f"repas_{repas.id}",
            type=type_evt,
            titre=titre,
            date_jour=repas.date_repas,
            pour_jules=True,  # Toujours inclure Jules
            version_jules=version_jules,
            recette_id=recette_id,
            termine=repas.prepare if hasattr(repas, "prepare") else False,
            notes=repas.notes if hasattr(repas, "notes") else None,
        )
    except Exception as e:
        logger.error(f"Erreur conversion repas: {e}")
        return None


def convertir_session_batch_en_evenement(session: Any) -> EvenementCalendrier | None:
    """Convertit une SessionBatchCooking en EvenementCalendrier."""
    if not session:
        return None

    try:
        heure = session.heure_debut if hasattr(session, "heure_debut") else time(14, 0)

        # Construire titre avec les recettes
        titre = "Session Batch Cooking"
        if hasattr(session, "recettes_planifiees") and session.recettes_planifiees:
            nb_recettes = (
                len(session.recettes_planifiees)
                if isinstance(session.recettes_planifiees, list)
                else 0
            )
            titre = f"Batch Cooking ({nb_recettes} plats)"

        return EvenementCalendrier(
            id=f"batch_{session.id}",
            type=TypeEvenement.BATCH_COOKING,
            titre=titre,
            date_jour=session.date_session,
            heure_debut=heure,
            pour_jules=session.avec_jules if hasattr(session, "avec_jules") else False,
            session_id=session.id,
            termine=session.statut == "terminee" if hasattr(session, "statut") else False,
            notes=session.notes if hasattr(session, "notes") else None,
        )
    except Exception as e:
        logger.error(f"Erreur conversion session batch: {e}")
        return None


def convertir_activite_en_evenement(activite: Any) -> EvenementCalendrier | None:
    """Convertit une FamilyActivity en EvenementCalendrier."""
    if not activite:
        return None

    try:
        # Determiner si c'est un RDV medical
        type_evt = TypeEvenement.ACTIVITE
        if hasattr(activite, "type_activite"):
            if activite.type_activite in ("medical", "medical", "sante", "rdv_medical"):
                type_evt = TypeEvenement.RDV_MEDICAL

        return EvenementCalendrier(
            id=f"activite_{activite.id}",
            type=type_evt,
            titre=activite.titre if hasattr(activite, "titre") else "Activite",
            date_jour=activite.date_prevue if hasattr(activite, "date_prevue") else date.today(),
            heure_debut=activite.heure_debut if hasattr(activite, "heure_debut") else None,
            lieu=activite.lieu if hasattr(activite, "lieu") else None,
            pour_jules=activite.pour_jules if hasattr(activite, "pour_jules") else False,
            budget=activite.cout_estime if hasattr(activite, "cout_estime") else None,
            termine=activite.statut == "termine" if hasattr(activite, "statut") else False,
            notes=activite.notes if hasattr(activite, "notes") else None,
        )
    except Exception as e:
        logger.error(f"Erreur conversion activite: {e}")
        return None


def convertir_event_calendrier_en_evenement(event: Any) -> EvenementCalendrier | None:
    """Convertit un CalendarEvent en EvenementCalendrier."""
    if not event:
        return None

    try:
        # Determiner le type
        type_evt = TypeEvenement.EVENEMENT
        if hasattr(event, "type_event"):
            if event.type_event in ("medical", "medical", "sante"):
                type_evt = TypeEvenement.RDV_MEDICAL
            elif event.type_event in ("courses", "shopping"):
                type_evt = TypeEvenement.COURSES

        heure = None
        if hasattr(event, "date_debut") and isinstance(event.date_debut, datetime):
            heure = event.date_debut.time()

        date_jour = date.today()
        if hasattr(event, "date_debut"):
            if isinstance(event.date_debut, datetime):
                date_jour = event.date_debut.date()
            elif isinstance(event.date_debut, date):
                date_jour = event.date_debut

        return EvenementCalendrier(
            id=f"event_{event.id}",
            type=type_evt,
            titre=event.titre if hasattr(event, "titre") else "Évenement",
            date_jour=date_jour,
            heure_debut=heure,
            lieu=event.lieu if hasattr(event, "lieu") else None,
            description=event.description if hasattr(event, "description") else None,
            termine=event.termine if hasattr(event, "termine") else False,
        )
    except Exception as e:
        logger.error(f"Erreur conversion event: {e}")
        return None


def convertir_tache_menage_en_evenement(tache: Any) -> EvenementCalendrier | None:
    """
    Convertit une MaintenanceTask (tâche menage/entretien) en EvenementCalendrier.

    Args:
        tache: Objet MaintenanceTask SQLAlchemy

    Returns:
        EvenementCalendrier ou None si erreur
    """
    if not tache:
        return None

    try:
        # Determiner le type selon la categorie
        categorie = getattr(tache, "categorie", "menage")
        if categorie in ("menage", "nettoyage", "rangement"):
            type_evt = TypeEvenement.MENAGE
        elif categorie in ("jardin", "exterieur", "pelouse"):
            type_evt = TypeEvenement.JARDIN
        else:
            type_evt = TypeEvenement.ENTRETIEN

        # Recuperer la date de prochaine execution
        date_jour = getattr(tache, "prochaine_fois", None) or date.today()

        # Construire le titre avec responsable si present
        titre = getattr(tache, "nom", "Tâche")
        responsable = getattr(tache, "responsable", None)
        if responsable:
            titre = f"{titre} ({responsable})"

        # Duree en description
        duree = getattr(tache, "duree_minutes", None)
        description = getattr(tache, "description", "")
        if duree:
            description = f"~{duree}min • {description}"

        # Calculer si en retard
        est_en_retard = False
        prochaine = getattr(tache, "prochaine_fois", None)
        if prochaine and prochaine < date.today():
            est_en_retard = True

        return EvenementCalendrier(
            id=f"menage_{tache.id}",
            type=type_evt,
            titre=titre,
            date_jour=date_jour,
            description=description,
            termine=getattr(tache, "fait", False),
            notes="⚠️ EN RETARD!" if est_en_retard else getattr(tache, "notes", None),
        )
    except Exception as e:
        logger.error(f"Erreur conversion tâche menage: {e}")
        return None


def generer_taches_menage_semaine(
    taches: list[Any], date_debut: date, date_fin: date
) -> dict[date, list[EvenementCalendrier]]:
    """
    Genère les evenements menage pour une semaine en se basant sur frequence_jours.

    Logique:
    - Si prochaine_fois dans la semaine → afficher ce jour
    - Si frequence_jours defini → calculer les occurrences dans la semaine
    - Sinon → afficher uniquement si prochaine_fois dans la semaine

    Returns:
        Dict[date, List[EvenementCalendrier]] pour chaque jour de la semaine
    """
    taches_par_jour: dict[date, list[EvenementCalendrier]] = {}

    for tache in taches:
        if not getattr(tache, "integrer_planning", False):
            continue  # Ne pas afficher les tâches non integrees au planning

        prochaine = getattr(tache, "prochaine_fois", None)
        frequence = getattr(tache, "frequence_jours", None)

        # Cas 1: Tâche avec prochaine_fois dans la semaine
        if prochaine and date_debut <= prochaine <= date_fin:
            evt = convertir_tache_menage_en_evenement(tache)
            if evt:
                if prochaine not in taches_par_jour:
                    taches_par_jour[prochaine] = []
                taches_par_jour[prochaine].append(evt)

        # Cas 2: Tâche recurrente sans prochaine_fois → generer par jour de semaine
        elif frequence and frequence <= 7:
            # Tâches hebdomadaires: on les met sur des jours fixes bases sur leur ID
            # Pour eviter tout le menage le même jour!
            jour_offset = (tache.id or 0) % 7  # Distribuer sur la semaine
            jour_cible = date_debut + timedelta(days=jour_offset)

            evt = convertir_tache_menage_en_evenement(tache)
            if evt:
                evt.date_jour = jour_cible
                if jour_cible not in taches_par_jour:
                    taches_par_jour[jour_cible] = []
                taches_par_jour[jour_cible].append(evt)

    return taches_par_jour


def creer_evenement_courses(
    date_jour: date, magasin: str, heure: time | None = None, id_source: int | None = None
) -> EvenementCalendrier:
    """Cree un evenement courses."""
    return EvenementCalendrier(
        id=f"courses_{id_source or hash(f'{date_jour}_{magasin}')}",
        type=TypeEvenement.COURSES,
        titre=f"Courses {magasin}",
        date_jour=date_jour,
        heure_debut=heure,
        magasin=magasin,
    )


def agreger_evenements_jour(
    date_jour: date,
    repas: list[Any] = None,
    sessions_batch: list[Any] = None,
    activites: list[Any] = None,
    events: list[Any] = None,
    courses_planifiees: list[dict] = None,
    taches_menage: list[EvenementCalendrier] = None,
) -> JourCalendrier:
    """
    Agrège tous les evenements d'un jour dans une structure unifiee.

    Args:
        date_jour: Date du jour
        repas: Liste des objets Repas SQLAlchemy
        sessions_batch: Liste des SessionBatchCooking
        activites: Liste des FamilyActivity
        events: Liste des CalendarEvent
        courses_planifiees: Liste de dicts {magasin, heure}
        taches_menage: Liste d'EvenementCalendrier dejà convertis pour ce jour

    Returns:
        JourCalendrier avec tous les evenements
    """
    evenements = []

    # Convertir les repas
    if repas:
        for r in repas:
            if hasattr(r, "date_repas") and r.date_repas == date_jour:
                evt = convertir_repas_en_evenement(r)
                if evt:
                    evenements.append(evt)

    # Convertir les sessions batch
    if sessions_batch:
        for s in sessions_batch:
            if hasattr(s, "date_session") and s.date_session == date_jour:
                evt = convertir_session_batch_en_evenement(s)
                if evt:
                    evenements.append(evt)

    # Convertir les activites
    if activites:
        for a in activites:
            evt = convertir_activite_en_evenement(a)
            if evt and evt.date_jour == date_jour:
                evenements.append(evt)

    # Convertir les evenements calendrier
    if events:
        for e in events:
            evt = convertir_event_calendrier_en_evenement(e)
            if evt and evt.date_jour == date_jour:
                evenements.append(evt)

    # Ajouter les courses planifiees
    if courses_planifiees:
        for c in courses_planifiees:
            if c.get("date") == date_jour:
                evt = creer_evenement_courses(
                    date_jour=date_jour,
                    magasin=c.get("magasin", "Courses"),
                    heure=c.get("heure"),
                )
                evenements.append(evt)

    # Ajouter les tâches menage (dejà converties)
    if taches_menage:
        evenements.extend(taches_menage)

    # Trier par heure puis par type
    evenements.sort(key=lambda e: (e.heure_debut or time(23, 59), e.type.value))

    return JourCalendrier(date_jour=date_jour, evenements=evenements)


def construire_semaine_calendrier(
    date_debut: date,
    repas: list[Any] = None,
    sessions_batch: list[Any] = None,
    activites: list[Any] = None,
    events: list[Any] = None,
    courses_planifiees: list[dict] = None,
    taches_menage: list[Any] = None,
) -> SemaineCalendrier:
    """
    Construit une semaine complète de calendrier.

    Args:
        date_debut: Date de debut (sera alignee sur le lundi)
        repas, sessions_batch, activites, events: Donnees brutes
        courses_planifiees: Liste de {date, magasin, heure}
        taches_menage: Liste des MaintenanceTask à integrer

    Returns:
        SemaineCalendrier avec les 7 jours
    """
    lundi = get_debut_semaine(date_debut)
    dimanche = lundi + timedelta(days=6)
    jours = []

    # Pre-traiter les tâches menage pour toute la semaine
    taches_par_jour: dict[date, list[EvenementCalendrier]] = {}
    if taches_menage:
        taches_par_jour = generer_taches_menage_semaine(taches_menage, lundi, dimanche)

    for i in range(7):
        jour_date = lundi + timedelta(days=i)
        jour = agreger_evenements_jour(
            date_jour=jour_date,
            repas=repas,
            sessions_batch=sessions_batch,
            activites=activites,
            events=events,
            courses_planifiees=courses_planifiees,
            taches_menage=taches_par_jour.get(jour_date, []),
        )
        jours.append(jour)

    return SemaineCalendrier(date_debut=lundi, jours=jours)


# ═══════════════════════════════════════════════════════════
# IMPRESSION / EXPORT
# ═══════════════════════════════════════════════════════════


def generer_texte_semaine_pour_impression(semaine: SemaineCalendrier) -> str:
    """
    Genère un texte formate de la semaine pour impression.

    Returns:
        Texte formate pour être colle sur le frigo
    """
    lignes = []
    lignes.append(f"═══ SEMAINE DU {semaine.titre} ═══")
    lignes.append("")

    for jour in semaine.jours:
        lignes.append(f"â–¶ {jour.jour_semaine.upper()} {jour.date_jour.strftime('%d/%m')}")
        lignes.append("-" * 30)

        if jour.repas_midi:
            lignes.append(f"  🌞 Midi: {jour.repas_midi.titre}")
            if jour.repas_midi.version_jules:
                lignes.append(f"     👶 Jules: {jour.repas_midi.version_jules[:50]}...")

        if jour.repas_soir:
            lignes.append(f"  🌙 Soir: {jour.repas_soir.titre}")
            if jour.repas_soir.version_jules:
                lignes.append(f"     👶 Jules: {jour.repas_soir.version_jules[:50]}...")

        if jour.gouter:
            lignes.append(f"  🍰 Goûter: {jour.gouter.titre}")

        if jour.batch_cooking:
            lignes.append(f"  🍳 BATCH COOKING {jour.batch_cooking.heure_str}")

        for courses in jour.courses:
            lignes.append(f"  🛒 Courses: {courses.magasin} {courses.heure_str}")

        for activite in jour.activites:
            lignes.append(f"  🎨 {activite.titre} {activite.heure_str}")

        for rdv in jour.rdv:
            emoji = "🏥" if rdv.type == TypeEvenement.RDV_MEDICAL else "📝…"
            lignes.append(f"  {emoji} {rdv.titre} {rdv.heure_str}")

        if jour.est_vide:
            lignes.append("  (rien de planifie)")

        lignes.append("")

    lignes.append("═" * 35)
    lignes.append(
        f"📊 {semaine.nb_repas_planifies} repas | {semaine.nb_sessions_batch} batch | {semaine.nb_courses} courses"
    )

    return "\n".join(lignes)


def generer_html_semaine_pour_impression(semaine: SemaineCalendrier) -> str:
    """
    Genère un HTML formate de la semaine pour impression.

    Returns:
        HTML prêt à imprimer
    """
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 12px; }}
            h1 {{ text-align: center; font-size: 16px; margin-bottom: 10px; }}
            .jour {{ margin-bottom: 15px; page-break-inside: avoid; }}
            .jour-titre {{ font-weight: bold; background: #f0f0f0; padding: 5px; }}
            .repas {{ margin-left: 20px; }}
            .event {{ margin-left: 20px; color: #555; }}
            .jules {{ color: #e91e63; font-size: 10px; }}
        </style>
    </head>
    <body>
        <h1>📝… SEMAINE DU {semaine.titre}</h1>
    """

    for jour in semaine.jours:
        html += f"""
        <div class="jour">
            <div class="jour-titre">{jour.jour_semaine} {jour.date_jour.strftime('%d/%m')}</div>
        """

        if jour.repas_midi:
            html += f'<div class="repas">🌞 Midi: <b>{jour.repas_midi.titre}</b></div>'
            if jour.repas_midi.version_jules:
                html += f'<div class="jules">👶 {jour.repas_midi.version_jules[:60]}...</div>'

        if jour.repas_soir:
            html += f'<div class="repas">🌙 Soir: <b>{jour.repas_soir.titre}</b></div>'
            if jour.repas_soir.version_jules:
                html += f'<div class="jules">👶 {jour.repas_soir.version_jules[:60]}...</div>'

        if jour.batch_cooking:
            html += f'<div class="event">🍳 Batch Cooking {jour.batch_cooking.heure_str}</div>'

        for courses in jour.courses:
            html += f'<div class="event">🛒 {courses.magasin} {courses.heure_str}</div>'

        for rdv in jour.rdv:
            html += f'<div class="event">🏥 {rdv.titre} {rdv.heure_str}</div>'

        html += "</div>"

    html += """
    </body>
    </html>
    """

    return html

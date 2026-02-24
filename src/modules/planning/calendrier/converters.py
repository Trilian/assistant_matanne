"""
Fonctions de conversion pour le Calendrier Familial Unifié.

Convertit les objets SQLAlchemy en EvenementCalendrier:
- Repas
- Sessions batch cooking
- Activités
- Événements calendrier
- Tâches ménage/entretien
- Courses
"""

import logging
from datetime import date, datetime, time
from typing import Any

from .types import EvenementCalendrier, TypeEvenement

logger = logging.getLogger(__name__)


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
    """Convertit une ActiviteFamille en EvenementCalendrier."""
    if not activite:
        return None

    try:
        # Determiner si c'est un RDV medical
        type_evt = TypeEvenement.ACTIVITE
        if hasattr(activite, "type_activite"):
            if activite.type_activite in ("medical", "sante", "rdv_medical"):
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
    """Convertit un EvenementPlanning en EvenementCalendrier."""
    if not event:
        return None

    try:
        # Determiner le type
        type_evt = TypeEvenement.EVENEMENT
        if hasattr(event, "type_event"):
            if event.type_event in ("medical", "sante"):
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
    Convertit une TacheEntretien (tâche menage/entretien) en EvenementCalendrier.

    Args:
        tache: Objet TacheEntretien SQLAlchemy

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


__all__ = [
    "convertir_repas_en_evenement",
    "convertir_session_batch_en_evenement",
    "convertir_activite_en_evenement",
    "convertir_event_calendrier_en_evenement",
    "convertir_tache_menage_en_evenement",
    "creer_evenement_courses",
]

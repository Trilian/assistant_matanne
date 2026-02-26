"""
Agrégation des événements pour le Calendrier Familial Unifié.

Fonctions pour:
- Calcul des jours de la semaine
- Navigation entre semaines
- Génération des tâches ménage
- Injection des jours spéciaux (fériés, crèche, ponts)
- Agrégation des événements par jour
- Construction d'une semaine calendrier complète
"""

import logging
from datetime import date, time, timedelta
from typing import Any

from src.core.date_utils import obtenir_debut_semaine as get_debut_semaine

from .converters import (
    convertir_activite_en_evenement,
    convertir_event_calendrier_en_evenement,
    convertir_repas_en_evenement,
    convertir_session_batch_en_evenement,
    convertir_tache_menage_en_evenement,
    creer_evenement_courses,
)
from .types import EvenementCalendrier, JourCalendrier, SemaineCalendrier, TypeEvenement

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# FONCTIONS DE CALCUL
# ═══════════════════════════════════════════════════════════


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
# GÉNÉRATION DES TÂCHES MÉNAGE
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# JOURS SPÉCIAUX (fériés, crèche, ponts)
# ═══════════════════════════════════════════════════════════

# Mapping type jour spécial → TypeEvenement
_TYPE_JOUR_SPECIAL = {
    "ferie": TypeEvenement.FERIE,
    "creche": TypeEvenement.CRECHE,
    "pont": TypeEvenement.PONT,
}


def generer_jours_speciaux_semaine(
    date_debut: date,
) -> dict[date, list[EvenementCalendrier]]:
    """Génère les événements jours spéciaux pour une semaine.

    Interroge le ServiceJoursSpeciaux et crée des EvenementCalendrier
    pour chaque jour spécial trouvé dans la période.

    Returns:
        Dict[date, List[EvenementCalendrier]] pour chaque jour de la semaine.
    """
    speciaux_par_jour: dict[date, list[EvenementCalendrier]] = {}

    try:
        from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

        service = obtenir_service_jours_speciaux()
        jours = service.jours_speciaux_semaine(date_debut)

        for jour in jours:
            type_evt = _TYPE_JOUR_SPECIAL.get(jour.type, TypeEvenement.EVENEMENT)
            evt = EvenementCalendrier(
                id=f"{jour.type}_{jour.date_jour.isoformat()}",
                type=type_evt,
                titre=jour.nom,
                date_jour=jour.date_jour,
                heure_debut=None,
                heure_fin=None,
                description=f"Jour spécial: {jour.nom}",
            )

            if jour.date_jour not in speciaux_par_jour:
                speciaux_par_jour[jour.date_jour] = []
            speciaux_par_jour[jour.date_jour].append(evt)

    except Exception as e:
        logger.warning(f"Impossible de charger les jours spéciaux: {e}")

    return speciaux_par_jour


# ═══════════════════════════════════════════════════════════
# AGRÉGATION DES ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


def agreger_evenements_jour(
    date_jour: date,
    repas: list[Any] = None,
    sessions_batch: list[Any] = None,
    activites: list[Any] = None,
    events: list[Any] = None,
    courses_planifiees: list[dict] = None,
    taches_menage: list[EvenementCalendrier] = None,
    jours_speciaux: list[EvenementCalendrier] = None,
) -> JourCalendrier:
    """
    Agrège tous les evenements d'un jour dans une structure unifiee.

    Args:
        date_jour: Date du jour
        repas: Liste des objets Repas SQLAlchemy
        sessions_batch: Liste des SessionBatchCooking
        activites: Liste des ActiviteFamille
        events: Liste des EvenementPlanning
        courses_planifiees: Liste de dicts {magasin, heure}
        taches_menage: Liste d'EvenementCalendrier dejà convertis pour ce jour
        jours_speciaux: Liste d'EvenementCalendrier fériés/crèche/ponts pour ce jour

    Returns:
        JourCalendrier avec tous les evenements
    """
    evenements = []

    # Ajouter les jours spéciaux en premier (toujours visibles en haut)
    if jours_speciaux:
        evenements.extend(jours_speciaux)

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
        taches_menage: Liste des TacheEntretien à integrer

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

    # Charger les jours spéciaux (fériés, crèche, ponts)
    speciaux_par_jour = generer_jours_speciaux_semaine(lundi)

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
            jours_speciaux=speciaux_par_jour.get(jour_date, []),
        )
        jours.append(jour)

    return SemaineCalendrier(date_debut=lundi, jours=jours)


__all__ = [
    "get_jours_semaine",
    "get_semaine_precedente",
    "get_semaine_suivante",
    "generer_taches_menage_semaine",
    "generer_jours_speciaux_semaine",
    "agreger_evenements_jour",
    "construire_semaine_calendrier",
]

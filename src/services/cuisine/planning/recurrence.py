"""
Service de gestion des événements récurrents.

Permet de:
- Générer les occurrences d'un événement récurrent
- Créer des événements avec récurrence
- Mettre à jour les séries d'événements
"""

from datetime import date, datetime, timedelta
from enum import Enum, StrEnum

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import CalendarEvent


class TypeRecurrence(StrEnum):
    """Types de récurrence disponibles."""

    AUCUNE = "none"
    QUOTIDIEN = "daily"
    HEBDOMADAIRE = "weekly"
    MENSUEL = "monthly"
    ANNUEL = "yearly"


OPTIONS_RECURRENCE = [
    (TypeRecurrence.AUCUNE, "Aucune récurrence"),
    (TypeRecurrence.QUOTIDIEN, "Tous les jours"),
    (TypeRecurrence.HEBDOMADAIRE, "Toutes les semaines"),
    (TypeRecurrence.MENSUEL, "Tous les mois"),
    (TypeRecurrence.ANNUEL, "Tous les ans"),
]

JOURS_SEMAINE_INDEX = [
    (0, "Lun"),
    (1, "Mar"),
    (2, "Mer"),
    (3, "Jeu"),
    (4, "Ven"),
    (5, "Sam"),
    (6, "Dim"),
]


def format_recurrence(event: CalendarEvent) -> str:
    """Formate la récurrence pour affichage."""
    if not event.recurrence_type or event.recurrence_type == TypeRecurrence.AUCUNE.value:
        return ""

    interval = event.recurrence_interval or 1
    labels = {
        "daily": f"Tous les {interval} jour(s)" if interval > 1 else "Tous les jours",
        "weekly": f"Toutes les {interval} semaine(s)" if interval > 1 else "Toutes les semaines",
        "monthly": f"Tous les {interval} mois" if interval > 1 else "Tous les mois",
        "yearly": f"Tous les {interval} an(s)" if interval > 1 else "Tous les ans",
    }

    result = labels.get(event.recurrence_type, "")

    # Ajouter les jours pour weekly
    if event.recurrence_type == "weekly" and event.recurrence_jours:
        jours_idx = [int(j) for j in event.recurrence_jours.split(",")]
        jours_noms = [nom for idx, nom in JOURS_SEMAINE_INDEX if idx in jours_idx]
        if jours_noms:
            result += f" ({', '.join(jours_noms)})"

    # Ajouter la date de fin
    if event.recurrence_fin:
        result += f" jusqu'au {event.recurrence_fin.strftime('%d/%m/%Y')}"

    return result


class ServiceRecurrence:
    """Service de gestion des événements récurrents."""

    def __init__(self, db: Session | None = None):
        """Initialise le service."""
        self._db = db

    def generer_occurrences(
        self,
        event: CalendarEvent,
        date_debut: date,
        date_fin: date,
    ) -> list[dict]:
        """
        Génère les occurrences d'un événement récurrent dans une plage de dates.

        Args:
            event: Événement avec récurrence
            date_debut: Date de début de la plage
            date_fin: Date de fin de la plage

        Returns:
            Liste des occurrences (dicts avec date_debut, date_fin, etc.)
        """
        if not event.recurrence_type or event.recurrence_type == TypeRecurrence.AUCUNE.value:
            return []

        occurrences = []
        interval = event.recurrence_interval or 1
        current = event.date_debut

        # Durée de l'événement
        duree = timedelta(0)
        if event.date_fin:
            duree = event.date_fin - event.date_debut

        # Date de fin de récurrence
        recurrence_end = event.recurrence_fin
        if recurrence_end:
            recurrence_end = datetime.combine(recurrence_end, datetime.max.time())
        else:
            recurrence_end = datetime.combine(date_fin, datetime.max.time())

        # Jours de la semaine pour weekly
        jours_semaine = None
        if event.recurrence_type == "weekly" and event.recurrence_jours:
            jours_semaine = [int(j) for j in event.recurrence_jours.split(",")]

        max_iterations = 1000  # Sécurité
        iterations = 0

        while current <= recurrence_end and iterations < max_iterations:
            iterations += 1
            current_date = current.date() if isinstance(current, datetime) else current

            # Vérifier si dans la plage demandée
            if date_debut <= current_date <= date_fin:
                # Pour weekly, vérifier le jour
                if event.recurrence_type == "weekly" and jours_semaine:
                    if current.weekday() not in jours_semaine:
                        current += timedelta(days=1)
                        continue

                occurrences.append(
                    {
                        "parent_id": event.id,
                        "titre": event.titre,
                        "description": event.description,
                        "date_debut": current,
                        "date_fin": current + duree if duree else None,
                        "lieu": event.lieu,
                        "type_event": event.type_event,
                        "couleur": event.couleur,
                        "est_occurrence": True,
                    }
                )

            # Avancer selon le type de récurrence
            if event.recurrence_type == "daily":
                current += timedelta(days=interval)
            elif event.recurrence_type == "weekly":
                if jours_semaine:
                    # Trouver le prochain jour de la semaine
                    current += timedelta(days=1)
                    while current.weekday() not in jours_semaine and iterations < max_iterations:
                        current += timedelta(days=1)
                        iterations += 1
                else:
                    current += timedelta(weeks=interval)
            elif event.recurrence_type == "monthly":
                # Même jour du mois prochain
                month = current.month + interval
                year = current.year + (month - 1) // 12
                month = ((month - 1) % 12) + 1
                try:
                    current = current.replace(year=year, month=month)
                except ValueError:
                    # Jour invalide (ex: 31 février), aller au dernier jour du mois
                    import calendar

                    last_day = calendar.monthrange(year, month)[1]
                    current = current.replace(
                        year=year, month=month, day=min(current.day, last_day)
                    )
            elif event.recurrence_type == "yearly":
                try:
                    current = current.replace(year=current.year + interval)
                except ValueError:
                    # 29 février sur année non bissextile
                    current = current.replace(year=current.year + interval, day=28)

        return occurrences

    @avec_session_db
    def get_events_avec_occurrences(
        self,
        date_debut: date,
        date_fin: date,
        *,
        db: Session,
    ) -> list[dict]:
        """
        Récupère tous les événements (simples + occurrences récurrentes) pour une période.

        Args:
            date_debut: Date de début
            date_fin: Date de fin
            db: Session SQLAlchemy

        Returns:
            Liste combinée des événements
        """
        from datetime import datetime as dt

        debut_dt = dt.combine(date_debut, dt.min.time())
        fin_dt = dt.combine(date_fin, dt.max.time())

        # Événements simples dans la période
        events_simples = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.date_debut >= debut_dt,
                CalendarEvent.date_debut <= fin_dt,
                (CalendarEvent.recurrence_type.is_(None))
                | (CalendarEvent.recurrence_type == "none"),
            )
            .all()
        )

        # Événements récurrents (dont la date de début est avant la fin de période)
        events_recurrents = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.date_debut <= fin_dt,
                CalendarEvent.recurrence_type.isnot(None),
                CalendarEvent.recurrence_type != "none",
            )
            .all()
        )

        resultats = []

        # Ajouter les événements simples
        for event in events_simples:
            resultats.append(
                {
                    "id": event.id,
                    "titre": event.titre,
                    "description": event.description,
                    "date_debut": event.date_debut,
                    "date_fin": event.date_fin,
                    "lieu": event.lieu,
                    "type_event": event.type_event,
                    "couleur": event.couleur,
                    "est_occurrence": False,
                    "recurrence": None,
                }
            )

        # Générer les occurrences
        for event in events_recurrents:
            occurrences = self.generer_occurrences(event, date_debut, date_fin)
            resultats.extend(occurrences)

        # Trier par date
        resultats.sort(key=lambda e: e["date_debut"])

        return resultats


# Factory
_service_recurrence: ServiceRecurrence | None = None


def obtenir_service_recurrence() -> ServiceRecurrence:
    """Retourne l'instance singleton du service de récurrence."""
    global _service_recurrence
    if _service_recurrence is None:
        _service_recurrence = ServiceRecurrence()
    return _service_recurrence


__all__ = [
    "TypeRecurrence",
    "OPTIONS_RECURRENCE",
    "JOURS_SEMAINE_INDEX",
    "format_recurrence",
    "ServiceRecurrence",
    "obtenir_service_recurrence",
]

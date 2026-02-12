"""
Générateur et parseur de fichiers iCal (.ics).

Fonctionnalités:
- Génération de fichiers iCal Ã  partir d'événements
- Parsing de fichiers iCal vers événements
"""

import logging
from datetime import datetime
from uuid import uuid4

from .schemas import CalendarEventExternal

logger = logging.getLogger(__name__)


class ICalGenerator:
    """Génère des fichiers iCal (.ics) Ã  partir des événements."""
    
    @staticmethod
    def generate_ical(events: list[CalendarEventExternal], calendar_name: str = "Assistant Matanne") -> str:
        """
        Génère un fichier iCal complet.
        
        Args:
            events: Liste d'événements Ã  inclure
            calendar_name: Nom du calendrier
            
        Returns:
            Contenu du fichier .ics
        """
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Assistant Matanne//Planning Familial//FR",
            f"X-WR-CALNAME:{calendar_name}",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]
        
        for event in events:
            lines.extend(ICalGenerator._event_to_vevent(event))
        
        lines.append("END:VCALENDAR")
        
        return "\r\n".join(lines)
    
    @staticmethod
    def _event_to_vevent(event: CalendarEventExternal) -> list[str]:
        """Convertit un événement en VEVENT iCal."""
        uid = event.external_id or str(uuid4())
        
        lines = [
            "BEGIN:VEVENT",
            f"UID:{uid}@assistant-matanne",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        ]
        
        if event.all_day:
            lines.append(f"DTSTART;VALUE=DATE:{event.start_time.strftime('%Y%m%d')}")
            lines.append(f"DTEND;VALUE=DATE:{event.end_time.strftime('%Y%m%d')}")
        else:
            lines.append(f"DTSTART:{event.start_time.strftime('%Y%m%dT%H%M%S')}")
            lines.append(f"DTEND:{event.end_time.strftime('%Y%m%dT%H%M%S')}")
        
        # Échapper les caractères spéciaux
        summary = event.title.replace(",", "\\,").replace(";", "\\;")
        lines.append(f"SUMMARY:{summary}")
        
        if event.description:
            desc = event.description.replace("\n", "\\n").replace(",", "\\,")
            lines.append(f"DESCRIPTION:{desc}")
        
        if event.location:
            lines.append(f"LOCATION:{event.location}")
        
        # Catégorie basée sur le type
        if event.source_type == "meal":
            lines.append("CATEGORIES:Repas")
        elif event.source_type == "activity":
            lines.append("CATEGORIES:Activité Familiale")
        
        lines.append("END:VEVENT")
        
        return lines
    
    @staticmethod
    def parse_ical(ical_content: str) -> list[CalendarEventExternal]:
        """
        Parse un fichier iCal et extrait les événements.
        
        Args:
            ical_content: Contenu du fichier .ics
            
        Returns:
            Liste d'événements extraits
        """
        events = []
        current_event = None
        
        for line in ical_content.split("\n"):
            line = line.strip()
            
            if line == "BEGIN:VEVENT":
                current_event = {}
            elif line == "END:VEVENT" and current_event is not None:
                # Créer l'événement
                try:
                    event = CalendarEventExternal(
                        external_id=current_event.get("UID", ""),
                        title=current_event.get("SUMMARY", "Sans titre"),
                        description=current_event.get("DESCRIPTION", ""),
                        start_time=ICalGenerator._parse_ical_datetime(current_event.get("DTSTART", "")),
                        end_time=ICalGenerator._parse_ical_datetime(current_event.get("DTEND", "")),
                        all_day=";VALUE=DATE" in current_event.get("DTSTART_RAW", ""),
                        location=current_event.get("LOCATION", ""),
                    )
                    events.append(event)
                except Exception as e:
                    logger.warning(f"Erreur parsing événement: {e}")
                
                current_event = None
            elif current_event is not None and ":" in line:
                key, value = line.split(":", 1)
                
                # Gérer les paramètres (ex: DTSTART;VALUE=DATE:20260101)
                if ";" in key:
                    current_event[key.split(";")[0]] = value
                    current_event[key.split(";")[0] + "_RAW"] = key
                else:
                    current_event[key] = value.replace("\\n", "\n").replace("\\,", ",")
        
        return events
    
    @staticmethod
    def _parse_ical_datetime(value: str) -> datetime:
        """Parse une date/heure iCal."""
        value = value.strip()
        
        # Format date seule: 20260101
        if len(value) == 8:
            return datetime.strptime(value, "%Y%m%d")
        
        # Format datetime: 20260101T120000 ou 20260101T120000Z
        if "T" in value:
            value = value.rstrip("Z")
            return datetime.strptime(value, "%Y%m%dT%H%M%S")
        
        return datetime.now()

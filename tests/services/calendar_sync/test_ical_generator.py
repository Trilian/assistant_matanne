"""
Tests du package calendar_sync - Générateur iCal.

Tests de génération et parsing de fichiers .ics.
"""

import pytest
from datetime import datetime
from src.services.calendar_sync.ical_generator import ICalGenerator
from src.services.calendar_sync.schemas import CalendarEventExternal


class TestICalGeneratorGenerate:
    """Tests pour la génération de fichiers iCal."""
    
    def test_generate_calendrier_vide(self):
        """Génère un calendrier vide valide."""
        ical = ICalGenerator.generate_ical([], "Test")
        
        assert "BEGIN:VCALENDAR" in ical
        assert "END:VCALENDAR" in ical
        assert "VERSION:2.0" in ical
        assert "X-WR-CALNAME:Test" in ical
    
    def test_generate_evenement_simple(self):
        """Génère un calendrier avec un événement."""
        event = CalendarEventExternal(
            title="Réunion",
            start_time=datetime(2026, 2, 10, 14, 0),
            end_time=datetime(2026, 2, 10, 15, 0)
        )
        
        ical = ICalGenerator.generate_ical([event])
        
        assert "BEGIN:VEVENT" in ical
        assert "END:VEVENT" in ical
        assert "SUMMARY:Réunion" in ical
        assert "DTSTART:20260210T140000" in ical
        assert "DTEND:20260210T150000" in ical
    
    def test_generate_evenement_journee_entiere(self):
        """Génère un événement journée entière."""
        event = CalendarEventExternal(
            title="Vacances",
            start_time=datetime(2026, 7, 15),
            end_time=datetime(2026, 7, 22),
            all_day=True
        )
        
        ical = ICalGenerator.generate_ical([event])
        
        assert "DTSTART;VALUE=DATE:20260715" in ical
        assert "DTEND;VALUE=DATE:20260722" in ical
    
    def test_generate_evenement_avec_description(self):
        """Génère un événement avec description."""
        event = CalendarEventExternal(
            title="Dîner",
            description="Avec les grands-parents\nPrévoir dessert",
            start_time=datetime(2026, 2, 14, 19, 0),
            end_time=datetime(2026, 2, 14, 21, 0)
        )
        
        ical = ICalGenerator.generate_ical([event])
        
        assert "DESCRIPTION:" in ical
        assert "\\n" in ical  # Newlines échappées
    
    def test_generate_evenement_avec_lieu(self):
        """Génère un événement avec lieu."""
        event = CalendarEventExternal(
            title="Sport",
            start_time=datetime(2026, 2, 11, 18, 0),
            end_time=datetime(2026, 2, 11, 19, 30),
            location="Salle de sport, 15 rue des Lilas"
        )
        
        ical = ICalGenerator.generate_ical([event])
        
        assert "LOCATION:Salle de sport, 15 rue des Lilas" in ical
    
    def test_generate_evenement_repas(self):
        """Génère un événement de type repas avec catégorie."""
        event = CalendarEventExternal(
            title="Déjeuner: Poulet rôti",
            start_time=datetime(2026, 2, 10, 12, 0),
            end_time=datetime(2026, 2, 10, 13, 0),
            source_type="meal"
        )
        
        ical = ICalGenerator.generate_ical([event])
        
        assert "CATEGORIES:Repas" in ical
    
    def test_generate_evenement_activite(self):
        """Génère un événement de type activité."""
        event = CalendarEventExternal(
            title="Sortie au parc",
            start_time=datetime(2026, 2, 15, 14, 0),
            end_time=datetime(2026, 2, 15, 17, 0),
            source_type="activity"
        )
        
        ical = ICalGenerator.generate_ical([event])
        
        assert "CATEGORIES:Activité Familiale" in ical
    
    def test_generate_plusieurs_evenements(self):
        """Génère un calendrier avec plusieurs événements."""
        events = [
            CalendarEventExternal(
                title="Événement 1",
                start_time=datetime(2026, 2, 10, 10, 0),
                end_time=datetime(2026, 2, 10, 11, 0)
            ),
            CalendarEventExternal(
                title="Événement 2",
                start_time=datetime(2026, 2, 10, 14, 0),
                end_time=datetime(2026, 2, 10, 15, 0)
            ),
            CalendarEventExternal(
                title="Événement 3",
                start_time=datetime(2026, 2, 11, 9, 0),
                end_time=datetime(2026, 2, 11, 10, 0)
            ),
        ]
        
        ical = ICalGenerator.generate_ical(events)
        
        assert ical.count("BEGIN:VEVENT") == 3
        assert ical.count("END:VEVENT") == 3
        assert "Événement 1" in ical
        assert "Événement 2" in ical
        assert "Événement 3" in ical
    
    def test_generate_uid_avec_external_id(self):
        """Utilise l'external_id comme UID si fourni."""
        event = CalendarEventExternal(
            external_id="custom_uid_123",
            title="Test",
            start_time=datetime(2026, 2, 10, 10, 0),
            end_time=datetime(2026, 2, 10, 11, 0)
        )
        
        ical = ICalGenerator.generate_ical([event])
        
        assert "UID:custom_uid_123@assistant-matanne" in ical
    
    def test_generate_escape_caracteres_speciaux(self):
        """Échappe les caractères spéciaux dans le titre."""
        event = CalendarEventExternal(
            title="Rendez-vous; Dr Martin, clinique",
            start_time=datetime(2026, 2, 12, 9, 30),
            end_time=datetime(2026, 2, 12, 10, 0)
        )
        
        ical = ICalGenerator.generate_ical([event])
        
        # Les ; et , doivent être échappés
        assert "\\;" in ical or "\\," in ical


class TestICalGeneratorParse:
    """Tests pour le parsing de fichiers iCal."""
    
    def test_parse_calendrier_vide(self):
        """Parse un calendrier sans événements."""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical)
        
        assert len(events) == 0
    
    def test_parse_evenement_simple(self):
        """Parse un événement simple."""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:test123@example.com
DTSTART:20260210T140000
DTEND:20260210T150000
SUMMARY:Réunion de travail
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical)
        
        assert len(events) == 1
        assert events[0].title == "Réunion de travail"
        assert events[0].external_id == "test123@example.com"
        assert events[0].start_time == datetime(2026, 2, 10, 14, 0)
        assert events[0].end_time == datetime(2026, 2, 10, 15, 0)
    
    def test_parse_evenement_journee_entiere(self):
        """Parse un événement journée entière."""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:allday@example.com
DTSTART;VALUE=DATE:20260315
DTEND;VALUE=DATE:20260316
SUMMARY:Anniversaire
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical)
        
        assert len(events) == 1
        assert events[0].all_day is True
        assert events[0].start_time.date() == datetime(2026, 3, 15).date()
    
    def test_parse_evenement_avec_description(self):
        """Parse un événement avec description."""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:desc@example.com
DTSTART:20260210T190000
DTEND:20260210T210000
SUMMARY:Dîner
DESCRIPTION:Apporter le dessert\\nPrévoir 10 personnes
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical)
        
        assert len(events) == 1
        assert "dessert" in events[0].description
        assert "\n" in events[0].description  # Newlines décodées
    
    def test_parse_evenement_avec_lieu(self):
        """Parse un événement avec lieu."""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:loc@example.com
DTSTART:20260211T180000
DTEND:20260211T193000
SUMMARY:Sport
LOCATION:Gymnase municipal
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical)
        
        assert len(events) == 1
        assert events[0].location == "Gymnase municipal"
    
    def test_parse_plusieurs_evenements(self):
        """Parse plusieurs événements."""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:e1@example.com
DTSTART:20260210T100000
DTEND:20260210T110000
SUMMARY:Événement 1
END:VEVENT
BEGIN:VEVENT
UID:e2@example.com
DTSTART:20260210T140000
DTEND:20260210T150000
SUMMARY:Événement 2
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical)
        
        assert len(events) == 2
        titles = [e.title for e in events]
        assert "Événement 1" in titles
        assert "Événement 2" in titles
    
    def test_parse_datetime_utc(self):
        """Parse les dates en UTC (avec Z)."""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:utc@example.com
DTSTART:20260210T140000Z
DTEND:20260210T150000Z
SUMMARY:Test UTC
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical)
        
        assert len(events) == 1
        assert events[0].start_time == datetime(2026, 2, 10, 14, 0)
    
    def test_parse_evenement_sans_titre(self):
        """Parse un événement sans SUMMARY."""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:notitle@example.com
DTSTART:20260210T100000
DTEND:20260210T110000
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical)
        
        assert len(events) == 1
        assert events[0].title == "Sans titre"


class TestICalRoundTrip:
    """Tests de round-trip (génération puis parsing)."""
    
    def test_roundtrip_evenement_simple(self):
        """Génère puis parse un événement."""
        original = CalendarEventExternal(
            external_id="roundtrip123",
            title="Test Round Trip",
            start_time=datetime(2026, 2, 10, 14, 0),
            end_time=datetime(2026, 2, 10, 15, 30),
            description="Description du test",
            location="Bureau"
        )
        
        # Générer
        ical = ICalGenerator.generate_ical([original])
        
        # Parser
        parsed = ICalGenerator.parse_ical(ical)
        
        assert len(parsed) == 1
        assert parsed[0].title == original.title
        assert parsed[0].start_time == original.start_time
        assert parsed[0].end_time == original.end_time
        assert parsed[0].location == original.location
    
    def test_roundtrip_plusieurs_evenements(self):
        """Génère puis parse plusieurs événements."""
        originals = [
            CalendarEventExternal(
                external_id=f"rt{i}",
                title=f"Événement {i}",
                start_time=datetime(2026, 2, 10 + i, 10, 0),
                end_time=datetime(2026, 2, 10 + i, 11, 0)
            )
            for i in range(5)
        ]
        
        ical = ICalGenerator.generate_ical(originals)
        parsed = ICalGenerator.parse_ical(ical)
        
        assert len(parsed) == 5
        parsed_titles = {e.title for e in parsed}
        for orig in originals:
            assert orig.title in parsed_titles

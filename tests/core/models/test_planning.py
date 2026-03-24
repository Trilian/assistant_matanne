"""
Tests unitaires pour planning.py

Module: src.core.models.planning
"""

from datetime import date, datetime

from src.core.models.planning import (
    Planning,
    Repas,
    EvenementPlanning,
    TemplateSemaine,
    ElementTemplate,
)


class TestPlanning:
    """Tests pour le module planning."""

    class TestPlanningModel:
        """Tests pour la classe Planning."""

        def test_planning_creation(self):
            planning = Planning(
                nom="Semaine 4",
                semaine_debut=date(2025, 1, 20),
                semaine_fin=date(2025, 1, 26),
            )
            assert planning.nom == "Semaine 4"
            assert planning.semaine_debut == date(2025, 1, 20)

        def test_planning_tablename(self):
            assert Planning.__tablename__ == "plannings"

    class TestRepas:
        """Tests pour la classe Repas."""

        def test_repas_creation(self):
            repas = Repas(
                planning_id=1,
                date_repas=date(2025, 1, 20),
                type_repas="dejeuner",
            )
            assert repas.type_repas == "dejeuner"
            assert repas.date_repas == date(2025, 1, 20)

        def test_repas_tablename(self):
            assert Repas.__tablename__ == "repas"

    class TestCalendarEvent:
        """Tests pour la classe EvenementPlanning."""

        def test_calendarevent_creation(self):
            evt = EvenementPlanning(
                titre="Réunion parents",
                date_debut=datetime(2025, 1, 20, 18, 0),
                type_event="reunion",
            )
            assert evt.titre == "Réunion parents"
            assert evt.type_event == "reunion"

        def test_calendarevent_tablename(self):
            assert EvenementPlanning.__tablename__ == "evenements_planning"

    class TestTemplateSemaine:
        """Tests pour la classe TemplateSemaine."""

        def test_template_creation(self):
            tpl = TemplateSemaine(nom="Semaine type")
            assert tpl.nom == "Semaine type"

        def test_template_tablename(self):
            assert TemplateSemaine.__tablename__ == "templates_semaine"

    class TestElementTemplate:
        """Tests pour la classe ElementTemplate."""

        def test_element_creation(self):
            elem = ElementTemplate(
                template_id=1,
                jour_semaine=0,
                heure_debut="08:00",
                titre="Sport",
                type_event="activite",
            )
            assert elem.jour_semaine == 0
            assert elem.heure_debut == "08:00"

        def test_element_tablename(self):
            assert ElementTemplate.__tablename__ == "elements_templates"

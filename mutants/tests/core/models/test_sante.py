"""
Tests unitaires pour sante.py

Module: src.core.models.sante
"""

from datetime import date

from src.core.models.sante import RoutineSante, ObjectifSante, EntreeSante


class TestSante:
    """Tests pour le module sante."""

    class TestHealthRoutine:
        """Tests pour la classe RoutineSante."""

        def test_healthroutine_creation(self):
            routine = RoutineSante(
                nom="Jogging matinal",
                type_routine="cardio",
                frequence="quotidien",
                duree_minutes=30,
                intensite="moderee",
            )
            assert routine.nom == "Jogging matinal"
            assert routine.duree_minutes == 30

        def test_healthroutine_tablename(self):
            assert RoutineSante.__tablename__ == "routines_sante"

    class TestHealthObjective:
        """Tests pour la classe ObjectifSante."""

        def test_healthobjective_creation(self):
            obj = ObjectifSante(
                titre="Perdre 5kg",
                categorie="poids",
                valeur_cible=75.0,
                unite="kg",
                date_debut=date(2025, 1, 1),
                date_cible=date(2025, 6, 1),
                priorite="haute",
                statut="en_cours",
            )
            assert obj.titre == "Perdre 5kg"
            assert obj.valeur_cible == 75.0

        def test_healthobjective_tablename(self):
            assert ObjectifSante.__tablename__ == "objectifs_sante"

    class TestHealthEntry:
        """Tests pour la classe EntreeSante."""

        def test_healthentry_creation(self):
            entree = EntreeSante(
                date=date(2025, 1, 20),
                type_activite="jogging",
                duree_minutes=30,
                calories_brulees=250,
                note_energie=7,
            )
            assert entree.type_activite == "jogging"
            assert entree.calories_brulees == 250
            assert entree.note_energie == 7

        def test_healthentry_tablename(self):
            assert EntreeSante.__tablename__ == "entrees_sante"

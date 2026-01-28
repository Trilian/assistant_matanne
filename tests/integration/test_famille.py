# -*- coding: utf-8 -*-
"""
Tests d'integration pour le module Famille.
"""

import pytest
from datetime import date, timedelta

from src.core.models import (
    Routine,
    RoutineTask,
    WellbeingEntry,
    ChildProfile,
)


@pytest.mark.integration
class TestWorkflowRoutines:
    """Tests du workflow de gestion des routines."""

    def test_creer_routine_complete(self, int_db):
        """Creer une routine avec ses taches."""
        routine = Routine(
            nom="Routine weekend",
            description="Activites du samedi matin",
            frequence="hebdomadaire",
            categorie="weekend",
            actif=True,
        )
        int_db.add(routine)
        int_db.flush()
        
        taches = [
            RoutineTask(routine_id=routine.id, nom="Grasse matinee", ordre=1),
            RoutineTask(routine_id=routine.id, nom="Brunch en famille", ordre=2),
            RoutineTask(routine_id=routine.id, nom="Sortie parc", ordre=3),
        ]
        for tache in taches:
            int_db.add(tache)
        
        int_db.commit()
        
        routine_db = int_db.query(Routine).filter_by(nom="Routine weekend").first()
        assert routine_db is not None
        
        taches_db = int_db.query(RoutineTask).filter_by(routine_id=routine_db.id).all()
        assert len(taches_db) == 3

    def test_modifier_ordre_taches(self, int_db, routines_base):
        """Reorganiser l'ordre des taches."""
        routine = routines_base[0]
        
        taches = int_db.query(RoutineTask).filter_by(
            routine_id=routine.id
        ).order_by(RoutineTask.ordre).all()
        
        if len(taches) >= 2:
            taches[0].ordre = 2
            taches[1].ordre = 1
            int_db.commit()
            
            taches_reordonnees = int_db.query(RoutineTask).filter_by(
                routine_id=routine.id
            ).order_by(RoutineTask.ordre).all()
            
            assert taches_reordonnees[0].id == taches[1].id

    def test_desactiver_routine(self, int_db, routines_base):
        """Desactiver une routine."""
        routine = routines_base[0]
        routine.actif = False
        int_db.commit()
        
        routine_db = int_db.query(Routine).filter_by(id=routine.id).first()
        assert routine_db.actif is False

    def test_filtrer_routines_actives(self, int_db, routines_base):
        """Filtrer les routines actives."""
        routines_actives = int_db.query(Routine).filter_by(actif=True).all()
        
        assert len(routines_actives) >= 1


@pytest.mark.integration
class TestWorkflowBienEtre:
    """Tests du workflow de suivi du bien-etre."""

    def test_ajouter_entree_bienetre(self, int_db):
        """Ajouter une nouvelle entree bien-etre."""
        entree = WellbeingEntry(
            date=date.today(),
            mood="excellent",
            activity="Bonne nuit",
            notes="Jules a dormi 12 heures sans reveil",
        )
        int_db.add(entree)
        int_db.commit()
        
        entree_db = int_db.query(WellbeingEntry).filter_by(activity="Bonne nuit").first()
        assert entree_db is not None
        assert entree_db.mood == "excellent"

    def test_historique_par_periode(self, int_db, wellbeing_base):
        """Consulter l'historique sur une periode."""
        date_debut = date.today() - timedelta(days=7)
        date_fin = date.today()
        
        entrees_periode = int_db.query(WellbeingEntry).filter(
            WellbeingEntry.date >= date_debut,
            WellbeingEntry.date <= date_fin
        ).all()
        
        assert len(entrees_periode) >= 1


@pytest.mark.integration
class TestWorkflowProfilsEnfants:
    """Tests du workflow de gestion des profils enfants."""

    def test_creer_profil_enfant(self, int_db):
        """Creer un nouveau profil enfant."""
        enfant = ChildProfile(
            name="Emma",
            date_of_birth=date.today() - timedelta(days=365),
            notes="Petite soeur de Jules",
        )
        int_db.add(enfant)
        int_db.commit()
        
        enfant_db = int_db.query(ChildProfile).filter_by(name="Emma").first()
        assert enfant_db is not None

    def test_calculer_age_enfant(self, int_db, child_profile):
        """Calculer l'age d'un enfant."""
        today = date.today()
        naissance = child_profile.date_of_birth
        
        age_mois = (today.year - naissance.year) * 12 + (today.month - naissance.month)
        
        assert age_mois >= 18

    def test_mettre_a_jour_notes(self, int_db, child_profile):
        """Mettre a jour les notes du profil."""
        child_profile.notes = "Notes mises a jour"
        int_db.commit()
        
        profil_db = int_db.query(ChildProfile).filter_by(id=child_profile.id).first()
        assert "mises a jour" in profil_db.notes


@pytest.mark.integration
class TestStatistiquesFamille:
    """Tests des statistiques du module famille."""

    def test_compter_routines_par_categorie(self, int_db, routines_base):
        """Compter les routines par categorie."""
        categories = {}
        
        routines = int_db.query(Routine).all()
        for routine in routines:
            cat = routine.categorie or "autre"
            categories[cat] = categories.get(cat, 0) + 1
        
        assert len(categories) >= 1

    def test_statistiques_humeur(self, int_db, wellbeing_base):
        """Analyser les humeurs sur une periode."""
        entrees = int_db.query(WellbeingEntry).all()
        
        humeurs = {}
        for entree in entrees:
            mood = entree.mood or "non_defini"
            humeurs[mood] = humeurs.get(mood, 0) + 1
        
        assert len(humeurs) >= 1

"""
Tests pour le module Famille - Helpers, models, et fonctionnalités
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.models import Base, ChildProfile, Milestone, FamilyActivity, HealthRoutine, HealthObjective, HealthEntry, FamilyBudget
from src.modules.famille.helpers import (
    calculer_progression_objectif,
    get_stats_santé_semaine
)


# ════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def db():
    """Fixture pour DB SQLite en mémoire"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def child_profile(db):
    """Fixture pour créer un profil enfant"""
    child = ChildProfile(
        name="Jules",
        date_of_birth=date(2024, 6, 22),
        gender="M",
        notes="Test",
        actif=True
    )
    db.add(child)
    db.commit()
    return child


# ════════════════════════════════════════════════════════════════════════════
# TESTS - CHILD PROFILE
# ════════════════════════════════════════════════════════════════════════════

class TestChildProfile:
    
    def test_create_child_profile(self, db):
        """Test création d'un profil enfant"""
        child = ChildProfile(
            name="Jules",
            date_of_birth=date(2024, 6, 22),
            gender="M"
        )
        db.add(child)
        db.commit()
        
        assert child.id is not None
        assert child.name == "Jules"
        assert child.gender == "M"
    
    def test_child_profile_repr(self, child_profile):
        """Test repr du profil"""
        assert "Jules" in repr(child_profile)
        assert "ChildProfile" in repr(child_profile)


# ════════════════════════════════════════════════════════════════════════════
# TESTS - MILESTONES
# ════════════════════════════════════════════════════════════════════════════

class TestMilestones:
    
    def test_create_milestone(self, db, child_profile):
        """Test création d'un jalon"""
        milestone = Milestone(
            child_id=child_profile.id,
            titre="Premiers pas",
            description="Jules a marché 5 pas!",
            categorie="motricité",
            date_atteint=date.today()
        )
        db.add(milestone)
        db.commit()
        
        assert milestone.id is not None
        assert milestone.child_id == child_profile.id
        assert milestone.categorie == "motricité"
    
    def test_milestone_categories(self, db, child_profile):
        """Test catégories de jalons"""
        categories = ["langage", "motricité", "social", "cognitif", "alimentation", "sommeil"]
        
        for cat in categories:
            milestone = Milestone(
                child_id=child_profile.id,
                titre=f"Jalon {cat}",
                categorie=cat,
                date_atteint=date.today()
            )
            db.add(milestone)
        
        db.commit()
        
        assert db.query(Milestone).count() == len(categories)
    
    def test_milestone_with_photo(self, db, child_profile):
        """Test jalon avec photo"""
        milestone = Milestone(
            child_id=child_profile.id,
            titre="Photo milestone",
            categorie="social",
            date_atteint=date.today(),
            photo_url="https://example.com/photo.jpg"
        )
        db.add(milestone)
        db.commit()
        
        assert milestone.photo_url == "https://example.com/photo.jpg"


# ════════════════════════════════════════════════════════════════════════════
# TESTS - FAMILY ACTIVITIES
# ════════════════════════════════════════════════════════════════════════════

class TestFamilyActivities:
    
    def test_create_activity(self, db):
        """Test création d'une activité"""
        activity = FamilyActivity(
            titre="Parc",
            type_activite="parc",
            date_prevue=date.today() + timedelta(days=1),
            duree_heures=2.0,
            lieu="Parc local",
            cout_estime=0.0
        )
        db.add(activity)
        db.commit()
        
        assert activity.id is not None
        assert activity.type_activite == "parc"
        assert activity.statut == "planifié"
    
    def test_activity_cost_calculation(self, db):
        """Test calcul des coûts"""
        activity = FamilyActivity(
            titre="Restaurant",
            type_activite="sortie",
            date_prevue=date.today(),
            cout_estime=50.0,
            cout_reel=48.50
        )
        db.add(activity)
        db.commit()
        
        savings = activity.cout_estime - activity.cout_reel
        assert savings == 1.50
    
    def test_activity_participants(self, db):
        """Test participants (JSONB)"""
        participants = ["Jules", "Papa", "Maman"]
        activity = FamilyActivity(
            titre="Sortie famille",
            type_activite="parc",
            date_prevue=date.today(),
            qui_participe=participants
        )
        db.add(activity)
        db.commit()
        
        assert activity.qui_participe == participants


# ════════════════════════════════════════════════════════════════════════════
# TESTS - HEALTH ROUTINES
# ════════════════════════════════════════════════════════════════════════════

class TestHealthRoutines:
    
    def test_create_routine(self, db):
        """Test création d'une routine"""
        routine = HealthRoutine(
            nom="Course 30min",
            type_routine="course",
            frequence="3x/semaine",
            duree_minutes=30,
            intensite="modérée",
            calories_brulees_estimees=300
        )
        db.add(routine)
        db.commit()
        
        assert routine.id is not None
        assert routine.duree_minutes == 30
        assert routine.actif is True
    
    def test_routine_with_jours(self, db):
        """Test routine avec jours de la semaine"""
        jours = ["lundi", "mercredi", "vendredi"]
        routine = HealthRoutine(
            nom="Yoga",
            type_routine="yoga",
            frequence="3x/semaine",
            duree_minutes=45,
            jours_semaine=jours
        )
        db.add(routine)
        db.commit()
        
        assert routine.jours_semaine == jours


# ════════════════════════════════════════════════════════════════════════════
# TESTS - HEALTH OBJECTIVES
# ════════════════════════════════════════════════════════════════════════════

class TestHealthObjectives:
    
    def test_create_objective(self, db):
        """Test création d'un objectif"""
        objective = HealthObjective(
            titre="Courir 10km",
            categorie="endurance",
            valeur_cible=10.0,
            unite="km",
            date_cible=date.today() + timedelta(days=30)
        )
        db.add(objective)
        db.commit()
        
        assert objective.id is not None
        assert objective.statut == "en_cours"
        assert objective.priorite == "moyenne"
    
    def test_objective_progression(self, db):
        """Test calcul de progression"""
        objective = HealthObjective(
            titre="Perdre 5kg",
            categorie="poids",
            valeur_cible=5.0,
            unite="kg",
            valeur_actuelle=3.0,
            date_cible=date.today() + timedelta(days=60)
        )
        db.add(objective)
        db.commit()
        
        progression = calculer_progression_objectif(objective)
        assert progression == 60.0  # 3/5 * 100


# ════════════════════════════════════════════════════════════════════════════
# TESTS - HEALTH ENTRIES
# ════════════════════════════════════════════════════════════════════════════

class TestHealthEntries:
    
    def test_create_entry(self, db):
        """Test création d'une entrée santé"""
        routine = HealthRoutine(
            nom="Course",
            type_routine="course",
            frequence="3x/semaine",
            duree_minutes=30
        )
        db.add(routine)
        db.commit()
        
        entry = HealthEntry(
            routine_id=routine.id,
            type_activite="course",
            duree_minutes=35,
            intensite="modérée",
            calories_brulees=320,
            note_energie=8,
            note_moral=9
        )
        db.add(entry)
        db.commit()
        
        assert entry.routine_id == routine.id
        assert entry.note_energie == 8
    
    def test_entry_energy_range(self, db):
        """Test que énergie/moral sont entre 1-10"""
        routine = HealthRoutine(
            nom="Yoga",
            type_routine="yoga",
            frequence="quotidien",
            duree_minutes=45
        )
        db.add(routine)
        db.commit()
        
        # Valeurs valides
        for value in [1, 5, 10]:
            entry = HealthEntry(
                routine_id=routine.id,
                type_activite="yoga",
                duree_minutes=45,
                intensite="modérée",  # Champ requis
                note_energie=value,
                note_moral=value
            )
            db.add(entry)
        
        db.commit()
        assert db.query(HealthEntry).count() == 3


# ════════════════════════════════════════════════════════════════════════════
# TESTS - FAMILY BUDGET
# ════════════════════════════════════════════════════════════════════════════

class TestFamilyBudget:
    
    def test_create_budget_entry(self, db):
        """Test création d'une entrée budget"""
        budget = FamilyBudget(
            date=date.today(),
            categorie="Jules_jouets",
            montant=25.50,
            description="Jouet éducatif"
        )
        db.add(budget)
        db.commit()
        
        assert budget.id is not None
        assert budget.montant == 25.50
    
    def test_budget_categories(self, db):
        """Test catégories de budget"""
        categories = [
            "Jules_jouets",
            "Jules_vetements",
            "Jules_couches",
            "Nous_sport",
            "Nous_nutrition",
            "Activités",
            "Autre"
        ]
        
        for cat in categories:
            budget = FamilyBudget(
                date=date.today(),
                categorie=cat,
                montant=10.0
            )
            db.add(budget)
        
        db.commit()
        assert db.query(FamilyBudget).count() == len(categories)
    
    def test_monthly_budget_total(self, db):
        """Test calcul du budget mensuel"""
        # Ajouter plusieurs entrées
        for i in range(5):
            budget = FamilyBudget(
                date=date.today(),
                categorie="Jules_jouets",
                montant=20.0
            )
            db.add(budget)
        
        db.commit()
        
        total = db.query(FamilyBudget).count()
        assert total == 5


# ════════════════════════════════════════════════════════════════════════════
# TESTS - INTEGRATION
# ════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    
    def test_full_family_workflow(self, db, child_profile):
        """Test scénario complet semaine de la famille"""
        # Jour 1: Jules fait un jalon
        milestone = Milestone(
            child_id=child_profile.id,
            titre="Marche seul",
            categorie="motricité",
            date_atteint=date.today()
        )
        db.add(milestone)
        
        # Activité familiale
        activity = FamilyActivity(
            titre="Parc",
            type_activite="parc",
            date_prevue=date.today(),
            qui_participe=["Jules", "Papa", "Maman"],
            cout_estime=0.0
        )
        db.add(activity)
        
        # Routine santé
        routine = HealthRoutine(
            nom="Promenade",
            type_routine="marche",
            frequence="quotidien",
            duree_minutes=30
        )
        db.add(routine)
        db.commit()
        
        # Entrée santé
        entry = HealthEntry(
            routine_id=routine.id,
            type_activite="marche",
            duree_minutes=35,
            note_energie=9,
            note_moral=10
        )
        db.add(entry)
        
        # Budget
        budget = FamilyBudget(
            date=date.today(),
            categorie="Activités",
            montant=15.0
        )
        db.add(budget)
        
        db.commit()
        
        # Vérifications
        assert db.query(Milestone).count() == 1
        assert db.query(FamilyActivity).count() == 1
        assert db.query(HealthRoutine).count() == 1
        assert db.query(HealthEntry).count() == 1
        assert db.query(FamilyBudget).count() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

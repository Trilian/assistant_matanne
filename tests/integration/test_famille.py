"""
Tests pour le module Famille
Teste Jules, Santé, Activités et Shopping
"""

import pytest
from datetime import date, timedelta


# Marquer tout le fichier comme tests d'intégration (nécessite une base de données)
pytestmark = pytest.mark.skip(reason="Tests d'intégration - nécessite une connexion BD")


from src.core.database import get_db_context
from src.core.models import (
    ChildProfile,
    Milestone,
    FamilyActivity,
    HealthRoutine,
    HealthObjective,
    HealthEntry,
    FamilyBudget,
)


# ===================================
# FIXTURES
# ===================================


@pytest.fixture
def child_profile():
    """Crée un profil enfant pour les tests"""
    with get_db_context() as db:
        child = ChildProfile(
            name="Jules",
            date_of_birth=date(2024, 6, 22),
            gender="M",
            notes="Test Jules",
        )
        db.add(child)
        db.commit()
        db.refresh(child)
        yield child
        db.delete(child)
        db.commit()


# ===================================
# TESTS JULES / MILESTONES
# ===================================


class TestMilestones:
    """Tests pour les jalons de Jules"""

    def test_create_milestone(self, child_profile):
        """Test création d'un jalon"""
        with get_db_context() as db:
            milestone = Milestone(
                child_id=child_profile.id,
                titre="Premier mot",
                description="A dit 'maman'",
                categorie="langage",
                date_atteint=date.today(),
                notes="Moment magique!",
            )
            db.add(milestone)
            db.commit()
            db.refresh(milestone)

            assert milestone.id is not None
            assert milestone.titre == "Premier mot"
            assert milestone.categorie == "langage"

    def test_milestone_with_photo(self, child_profile):
        """Test jalon avec photo"""
        with get_db_context() as db:
            milestone = Milestone(
                child_id=child_profile.id,
                titre="Premier pas",
                categorie="motricité",
                date_atteint=date.today(),
                photo_url="https://example.com/photo.jpg",
            )
            db.add(milestone)
            db.commit()
            db.refresh(milestone)

            assert milestone.photo_url == "https://example.com/photo.jpg"

    def test_get_milestones_by_category(self, child_profile):
        """Test récupération des jalons par catégorie"""
        with get_db_context() as db:
            # Ajouter plusieurs jalons
            for i in range(3):
                milestone = Milestone(
                    child_id=child_profile.id,
                    titre=f"Jalon {i}",
                    categorie="langage",
                    date_atteint=date.today() - timedelta(days=i),
                )
                db.add(milestone)

            db.commit()

            # Vérifier
            milestones = (
                db.query(Milestone)
                .filter(Milestone.child_id == child_profile.id)
                .all()
            )
            assert len(milestones) == 3


# ===================================
# TESTS ACTIVITÃ‰S
# ===================================


class TestFamilyActivities:
    """Tests pour les activités familiales"""

    def test_create_activity(self):
        """Test création d'une activité"""
        with get_db_context() as db:
            activity = FamilyActivity(
                titre="Parc dimanche",
                description="Jeux et pique-nique",
                type_activite="parc",
                date_prevue=date.today() + timedelta(days=3),
                duree_heures=2.0,
                lieu="Parc de la ville",
                qui_participe=["Jules", "Maman", "Papa"],
                cout_estime=0.0,
                statut="planifié",
            )
            db.add(activity)
            db.commit()
            db.refresh(activity)

            assert activity.id is not None
            assert activity.titre == "Parc dimanche"
            assert activity.statut == "planifié"

    def test_mark_activity_complete(self):
        """Test marquer activité comme terminée"""
        with get_db_context() as db:
            activity = FamilyActivity(
                titre="Test activité",
                type_activite="parc",
                date_prevue=date.today(),
                statut="planifié",
            )
            db.add(activity)
            db.commit()
            db.refresh(activity)

            # Marquer terminé
            activity.statut = "terminé"
            activity.cout_reel = 10.0
            db.commit()

            # Vérifier
            updated = db.query(FamilyActivity).filter(FamilyActivity.id == activity.id).first()
            assert updated.statut == "terminé"
            assert updated.cout_reel == 10.0

    def test_activity_budget(self):
        """Test suivi budget activités"""
        with get_db_context() as db:
            # Ajouter plusieurs activités
            total_estime = 0
            for i in range(3):
                activity = FamilyActivity(
                    titre=f"Activité {i}",
                    type_activite="parc",
                    date_prevue=date.today() + timedelta(days=i),
                    cout_estime=10.0 + (i * 5),
                )
                db.add(activity)
                total_estime += 10.0 + (i * 5)

            db.commit()

            # Vérifier
            activities = db.query(FamilyActivity).all()
            assert len(activities) >= 3
            assert sum([a.cout_estime or 0 for a in activities]) >= total_estime


# ===================================
# TESTS SANTÃ‰ & SPORT
# ===================================


class TestHealthRoutines:
    """Tests pour les routines de santé"""

    def test_create_routine(self):
        """Test création d'une routine"""
        with get_db_context() as db:
            routine = HealthRoutine(
                nom="Yoga le matin",
                description="30 min de yoga",
                type_routine="yoga",
                frequence="3x/semaine",
                duree_minutes=30,
                intensite="modérée",
                jours_semaine=["lundi", "mercredi", "vendredi"],
                calories_brulees_estimees=150,
                actif=True,
            )
            db.add(routine)
            db.commit()
            db.refresh(routine)

            assert routine.id is not None
            assert routine.nom == "Yoga le matin"
            assert routine.duree_minutes == 30

    def test_routine_with_entries(self):
        """Test routine avec entrées de suivi"""
        with get_db_context() as db:
            routine = HealthRoutine(
                nom="Course",
                type_routine="course",
                frequence="3x/semaine",
                duree_minutes=40,
                intensite="haute",
            )
            db.add(routine)
            db.commit()
            db.refresh(routine)

            # Ajouter entrées
            for i in range(3):
                entry = HealthEntry(
                    routine_id=routine.id,
                    date=date.today() - timedelta(days=i),
                    type_activite="course",
                    duree_minutes=40,
                    intensite="haute",
                    calories_brulees=500,
                    note_energie=8,
                    note_moral=9,
                )
                db.add(entry)

            db.commit()

            # Vérifier
            entries = db.query(HealthEntry).filter(HealthEntry.routine_id == routine.id).all()
            assert len(entries) == 3
            assert entries[0].calories_brulees == 500


class TestHealthObjectives:
    """Tests pour les objectifs de santé"""

    def test_create_objective(self):
        """Test création d'un objectif"""
        with get_db_context() as db:
            objective = HealthObjective(
                titre="Courir 5km",
                description="ÃŠtre capable de courir 5km sans arrêt",
                categorie="endurance",
                valeur_cible=5.0,
                unite="km",
                valeur_actuelle=2.0,
                date_debut=date.today(),
                date_cible=date.today() + timedelta(days=60),
                priorite="haute",
                statut="en_cours",
            )
            db.add(objective)
            db.commit()
            db.refresh(objective)

            assert objective.id is not None
            assert objective.titre == "Courir 5km"
            assert objective.priorite == "haute"

    def test_objective_progression(self):
        """Test progression objectif"""
        with get_db_context() as db:
            objective = HealthObjective(
                titre="Perte poids",
                categorie="poids",
                valeur_cible=75.0,
                unite="kg",
                valeur_actuelle=85.0,
                date_debut=date.today(),
                date_cible=date.today() + timedelta(days=90),
            )
            db.add(objective)
            db.commit()
            db.refresh(objective)

            # Calculer progression
            progression = (objective.valeur_actuelle / objective.valeur_cible) * 100

            # Mettre à jour valeur
            objective.valeur_actuelle = 80.0
            db.commit()

            # Vérifier
            updated = db.query(HealthObjective).filter(HealthObjective.id == objective.id).first()
            assert updated.valeur_actuelle == 80.0


# ===================================
# TESTS BUDGET FAMILLE
# ===================================


class TestFamilyBudget:
    """Tests pour le budget famille"""

    def test_create_budget_entry(self):
        """Test création entrée budget"""
        with get_db_context() as db:
            entry = FamilyBudget(
                date=date.today(),
                categorie="Jules_jouets",
                description="Blocs Duplo",
                montant=30.0,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)

            assert entry.id is not None
            assert entry.montant == 30.0
            assert entry.categorie == "Jules_jouets"

    def test_budget_by_category(self):
        """Test budget par catégorie"""
        with get_db_context() as db:
            categories = [
                ("Jules_jouets", 30.0),
                ("Jules_vetements", 50.0),
                ("Nous_sport", 25.0),
            ]

            total = 0
            for cat, amount in categories:
                entry = FamilyBudget(
                    date=date.today(),
                    categorie=cat,
                    montant=amount,
                )
                db.add(entry)
                total += amount

            db.commit()

            # Vérifier
            entries = db.query(FamilyBudget).all()
            assert sum([e.montant for e in entries]) >= total

    def test_budget_monthly(self):
        """Test budget mensuel"""
        with get_db_context() as db:
            # Ajouter entries du mois
            month_start = date.today().replace(day=1)
            total = 0

            for i in range(5):
                entry = FamilyBudget(
                    date=month_start + timedelta(days=i * 5),
                    categorie="Test",
                    montant=20.0,
                )
                db.add(entry)
                total += 20.0

            db.commit()

            # Vérifier
            entries = (
                db.query(FamilyBudget)
                .filter(FamilyBudget.date >= month_start)
                .all()
            )
            assert sum([e.montant for e in entries]) >= total


# ===================================
# TESTS INTÃ‰GRATION
# ===================================


class TestIntegration:
    """Tests d'intégration entre modules"""

    def test_full_week_scenario(self, child_profile):
        """Test scénario complet semaine"""
        with get_db_context() as db:
            # 1. Ajouter jalon Jules
            milestone = Milestone(
                child_id=child_profile.id,
                titre="Nouveau mot",
                categorie="langage",
                date_atteint=date.today(),
            )
            db.add(milestone)

            # 2. Planifier activité
            activity = FamilyActivity(
                titre="Parc samedi",
                type_activite="parc",
                date_prevue=date.today() + timedelta(days=1),
                qui_participe=["Jules", "Maman", "Papa"],
                cout_estime=0.0,
            )
            db.add(activity)

            # 3. Créer routine sport
            routine = HealthRoutine(
                nom="Course",
                type_routine="course",
                frequence="3x/semaine",
                duree_minutes=40,
            )
            db.add(routine)

            # 4. Ajouter entries budget
            budget = FamilyBudget(
                date=date.today(),
                categorie="Jules_jouets",
                montant=25.0,
            )
            db.add(budget)

            db.commit()

            # Vérifier
            assert db.query(Milestone).filter(Milestone.child_id == child_profile.id).count() > 0
            assert db.query(FamilyActivity).count() > 0
            assert db.query(HealthRoutine).count() > 0
            assert db.query(FamilyBudget).count() > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


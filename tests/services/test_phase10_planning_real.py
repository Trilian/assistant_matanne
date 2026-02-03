"""
PHASE 10: Planning Service - Real Business Logic Tests
Tests for actual planning creation, modification, and validation
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from src.services.planning import PlanningService
from src.core.models.planning import Planning, PlanningJour
from src.core.models.recettes import Recette
from src.core.errors import ErreurBaseDeDonnees


class TestPlanningCreation:
    """Test planning service creation with real data"""

    def test_create_planning_complet_7_days(self, db: Session):
        """Create a complete 7-day meal plan"""
        service = PlanningService(db)
        
        # Create test recipes first
        recettes = []
        for i in range(14):
            recette = Recette(
                nom=f"Recette {i}",
                type_plat="plat",
                temps_preparation=30,
                portions=4,
                ingredients=[],
            )
            db.add(recette)
            recettes.append(recette)
        db.commit()
        
        # Create planning
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7,
            inclure_petit_dejeuner=True,
            inclure_desserts=True
        )
        
        # Assertions
        assert planning is not None
        assert planning.date_debut == date(2026, 2, 1)
        assert planning.duree_jours == 7
        assert len(planning.jours) == 7
        assert all(isinstance(jour, PlanningJour) for jour in planning.jours)

    def test_planning_respects_preferences(self, db: Session):
        """Verify planning respects user preferences"""
        service = PlanningService(db)
        
        # Create recipes with allergens
        recette_gluten = Recette(
            nom="Pain complet",
            type_plat="plat",
            temps_preparation=20,
            portions=4,
            ingredients=["farine"],
            allergens="gluten"
        )
        recette_safe = Recette(
            nom="Salade",
            type_plat="plat",
            temps_preparation=10,
            portions=4,
            ingredients=["laitue"],
            allergens=None
        )
        db.add_all([recette_gluten, recette_safe])
        db.commit()
        
        # Create planning with gluten-free preference
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=3,
            preferences={"allergies": ["gluten"]}
        )
        
        # Verify no gluten recipes included
        assert planning is not None
        for jour in planning.jours:
            for repas in [jour.petit_dejeuner, jour.midi, jour.soir]:
                if repas:
                    assert "gluten" not in (repas.allergens or "")

    def test_planning_calculates_nutrition(self, db: Session):
        """Verify planning calculates nutritional values"""
        service = PlanningService(db)
        
        recette = Recette(
            nom="Poulet riz",
            type_plat="plat",
            temps_preparation=30,
            portions=4,
            ingredients=["poulet", "riz"],
            calories_par_portion=500,
            proteines_g=25,
            glucides_g=60,
            lipides_g=10
        )
        db.add(recette)
        db.commit()
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=1
        )
        
        # Check nutrition calculations
        assert planning is not None
        assert hasattr(planning, 'calories_totales')
        assert hasattr(planning, 'proteines_totales')
        assert planning.calories_totales > 0

    def test_planning_validates_equilibre(self, db: Session):
        """Verify planning validates nutritional balance"""
        service = PlanningService(db)
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        
        # Should have balance validation method
        assert hasattr(service, 'valider_equilibre_nutritionnel')
        
        is_balanced = service.valider_equilibre_nutritionnel(planning)
        assert isinstance(is_balanced, bool)


class TestPlanningModification:
    """Test planning modification and updates"""

    def test_modifier_recette_jour_specific(self, db: Session):
        """Modify recipe for specific day"""
        service = PlanningService(db)
        
        recette1 = Recette(
            nom="Pâtes",
            type_plat="plat",
            temps_preparation=20,
            portions=4
        )
        recette2 = Recette(
            nom="Riz",
            type_plat="plat",
            temps_preparation=25,
            portions=4
        )
        db.add_all([recette1, recette2])
        db.commit()
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        
        # Modify recipe
        planning_modifie = service.remplacer_recette(
            planning=planning,
            jour_index=0,
            repas_type="midi",
            nouvelle_recette=recette2
        )
        
        assert planning_modifie is not None
        assert planning_modifie.jours[0].midi.id == recette2.id

    def test_duplicate_planning_day(self, db: Session):
        """Duplicate a planning day"""
        service = PlanningService(db)
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        
        # Duplicate day 0 to day 5
        planning_modifie = service.dupliquer_jour(
            planning=planning,
            jour_source=0,
            jour_cible=5
        )
        
        assert planning_modifie is not None
        # Same recipes should be used
        assert planning_modifie.jours[5].midi == planning_modifie.jours[0].midi


class TestPlanningValidation:
    """Test planning validation and constraints"""

    def test_planning_rejects_invalid_dates(self, db: Session):
        """Reject planning with invalid dates"""
        service = PlanningService(db)
        
        with pytest.raises((ValueError, ErreurBaseDeDonnees)):
            service.create_planning_complet(
                date_debut=date(2026, 2, 1),
                duree_jours=-1  # Invalid
            )

    def test_planning_requires_minimum_duration(self, db: Session):
        """Planning requires minimum 1 day"""
        service = PlanningService(db)
        
        with pytest.raises((ValueError, ErreurBaseDeDonnees)):
            service.create_planning_complet(
                date_debut=date(2026, 2, 1),
                duree_jours=0
            )

    def test_planning_enforces_max_duration(self, db: Session):
        """Planning limited to reasonable duration"""
        service = PlanningService(db)
        
        # Should succeed (e.g., max 365 days)
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=30
        )
        assert planning is not None
        
        # Should fail if over max
        with pytest.raises((ValueError, ErreurBaseDeDonnees)):
            service.create_planning_complet(
                date_debut=date(2026, 2, 1),
                duree_jours=1000
            )

    def test_planning_validates_recipe_availability(self, db: Session):
        """Verify planning uses available recipes only"""
        service = PlanningService(db)
        
        # Create with specific recipe set
        recette = Recette(
            nom="Unique",
            type_plat="plat",
            temps_preparation=30,
            portions=4
        )
        db.add(recette)
        db.commit()
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=2
        )
        
        # All recipes should exist in DB
        for jour in planning.jours:
            for repas in [jour.petit_dejeuner, jour.midi, jour.soir]:
                if repas:
                    assert db.query(Recette).filter_by(id=repas.id).first() is not None


class TestPlanningPersistence:
    """Test planning persistence to database"""

    def test_save_planning_to_db(self, db: Session):
        """Save planning to database"""
        service = PlanningService(db)
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        
        # Save to DB
        db.add(planning)
        db.commit()
        
        # Retrieve and verify
        retrieved = db.query(Planning).filter_by(
            date_debut=date(2026, 2, 1)
        ).first()
        
        assert retrieved is not None
        assert retrieved.duree_jours == 7
        assert len(retrieved.jours) == 7

    def test_update_planning_in_db(self, db: Session):
        """Update existing planning"""
        service = PlanningService(db)
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        db.add(planning)
        db.commit()
        
        original_id = planning.id
        
        # Modify
        planning.notes = "Modified"
        db.commit()
        
        # Verify update
        retrieved = db.query(Planning).filter_by(id=original_id).first()
        assert retrieved.notes == "Modified"

    def test_delete_planning_from_db(self, db: Session):
        """Delete planning from database"""
        service = PlanningService(db)
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        db.add(planning)
        db.commit()
        
        planning_id = planning.id
        
        # Delete
        db.delete(planning)
        db.commit()
        
        # Verify deletion
        retrieved = db.query(Planning).filter_by(id=planning_id).first()
        assert retrieved is None


class TestPlanningQueries:
    """Test planning retrieval and filtering"""

    def test_get_planning_by_date_range(self, db: Session):
        """Retrieve plannings for date range"""
        service = PlanningService(db)
        
        # Create multiple plannings
        for i in range(3):
            planning = service.create_planning_complet(
                date_debut=date(2026, 2, 1) + timedelta(days=i*7),
                duree_jours=7
            )
            db.add(planning)
        db.commit()
        
        # Query by date range
        plannings = db.query(Planning).filter(
            Planning.date_debut >= date(2026, 2, 1),
            Planning.date_debut <= date(2026, 2, 15)
        ).all()
        
        assert len(plannings) >= 2

    def test_get_planning_with_filters(self, db: Session):
        """Retrieve plannings with filters"""
        service = PlanningService(db)
        
        planning1 = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        db.add(planning1)
        db.commit()
        
        # Add filter criteria
        planning1.tags = ["vegetarien"]
        db.commit()
        
        # Query with filter
        filtered = db.query(Planning).filter(
            Planning.tags.contains(["vegetarien"])
        ).all()
        
        assert len(filtered) > 0


class TestPlanningEdgeCases:
    """Test edge cases and error scenarios"""

    def test_planning_with_no_recipes(self, db: Session):
        """Handle planning creation with no recipes available"""
        service = PlanningService(db)
        
        # Should either create empty or raise error
        try:
            planning = service.create_planning_complet(
                date_debut=date(2026, 2, 1),
                duree_jours=7
            )
            # If created, should be empty or have placeholders
            assert planning is not None
        except ErreurBaseDeDonnees:
            # Expected if recipes required
            pass

    def test_planning_with_duplicate_recipes(self, db: Session):
        """Planning can use same recipe multiple days"""
        service = PlanningService(db)
        
        recette = Recette(
            nom="Favorite",
            type_plat="plat",
            temps_preparation=30,
            portions=4
        )
        db.add(recette)
        db.commit()
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        
        # It's OK to have same recipe multiple times
        assert planning is not None

    def test_planning_timezone_handling(self, db: Session):
        """Planning handles date boundaries correctly"""
        service = PlanningService(db)
        
        planning = service.create_planning_complet(
            date_debut=date(2026, 2, 1),
            duree_jours=7
        )
        
        # All days should be consecutive
        for i, jour in enumerate(planning.jours):
            expected_date = date(2026, 2, 1) + timedelta(days=i)
            assert jour.date == expected_date


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

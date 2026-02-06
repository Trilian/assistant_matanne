"""
PHASE 10: Planning Service - Real Business Logic Tests
Tests for actual planning creation, modification, and validation

Uses patch_db_context fixture for test DB.
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from src.services.planning import PlanningService, get_planning_service
from src.core.models.planning import Planning, Repas
from src.core.models.recettes import Recette
from src.core.errors import ErreurBaseDeDonnees


# Mark all tests to use patch_db_context
@pytest.fixture(autouse=True)
def auto_patch_db(patch_db_context):
    """Auto-use patch_db_context for all tests in this module."""
    pass


class TestPlanningCreation:
    """Test planning service creation with real data"""

    def test_create_planning_via_ia(self, db: Session):
        """Create planning via AI generation"""
        service = get_planning_service()
        
        # Create test recipes first
        recettes = []
        for i in range(14):
            recette = Recette(
                nom=f"Recette {i}",
                type_repas="dîner",
                temps_preparation=30,
                portions=4,
            )
            db.add(recette)
            recettes.append(recette)
        db.commit()
        
        # Create planning via IA
        semaine_debut = date(2026, 2, 1)
        planning = service.generer_planning_ia(semaine_debut)
        
        # Assertions
        assert planning is not None
        assert planning.semaine_debut == semaine_debut
        # Planning has 7 days of meals (at least déjeuner/dîner)
        assert len(planning.repas) >= 7

    def test_create_planning_custom(self, db: Session):
        """Create custom planning from recipe selections"""
        service = get_planning_service()
        
        # Create recipes
        recettes = []
        for i in range(7):
            recette = Recette(
                nom=f"Recette {i}",
                type_repas="dîner",
                temps_preparation=30,
                portions=4,
            )
            db.add(recette)
            recettes.append(recette)
        db.commit()
        
        # Create planning with recipe selections
        semaine_debut = date(2026, 2, 1)
        recettes_selection = {f"jour_{i}": recettes[i].id for i in range(7)}
        
        planning = service.creer_planning_avec_choix(
            semaine_debut=semaine_debut,
            recettes_selection=recettes_selection
        )
        
        assert planning is not None
        assert planning.semaine_debut == semaine_debut
        assert len(planning.repas) > 0


class TestPlanningModification:
    """Test planning modification and updates"""

    def test_planning_persistence_crud(self, db: Session):
        """Test create, read, update, delete operations"""
        # We test CRUD directly with db operations
        # (PlanningService is a singleton without db parameter)
        
        # Create planning
        semaine_debut = date(2026, 2, 1)
        semaine_fin = semaine_debut + timedelta(days=6)
        
        planning = Planning(
            nom="Test Planning",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            actif=True
        )
        db.add(planning)
        db.commit()
        
        # Read
        retrieved = db.query(Planning).filter_by(id=planning.id).first()
        assert retrieved is not None
        assert retrieved.nom == "Test Planning"
        
        # Update
        retrieved.nom = "Modified Planning"
        db.commit()
        
        # Verify update
        updated = db.query(Planning).filter_by(id=planning.id).first()
        assert updated.nom == "Modified Planning"
        
        # Delete
        db.delete(updated)
        db.commit()
        
        deleted = db.query(Planning).filter_by(id=planning.id).first()
        assert deleted is None

    def test_repas_creation_in_planning(self, db: Session):
        """Test adding repas (meals) to a planning"""
        # Create recipe
        recette = Recette(
            nom="Test Recipe",
            type_repas="dîner",
            temps_preparation=30,
            portions=4
        )
        db.add(recette)
        db.flush()
        
        # Create planning
        planning = Planning(
            nom="Test Planning",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7),
            actif=True
        )
        db.add(planning)
        db.flush()
        
        # Add repas
        repas = Repas(
            planning_id=planning.id,
            recette_id=recette.id,
            date_repas=date(2026, 2, 1),
            type_repas="dîner",
            notes="Test meal"
        )
        db.add(repas)
        db.commit()
        
        # Verify
        retrieved_planning = db.query(Planning).filter_by(id=planning.id).first()
        assert len(retrieved_planning.repas) == 1
        assert retrieved_planning.repas[0].type_repas == "dîner"


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


class TestPlanningValidation:
    """Test planning validation and constraints"""

    def test_planning_requires_valid_dates(self, db: Session):
        """Planning must have valid date range"""
        semaine_debut = date(2026, 2, 1)
        semaine_fin = semaine_debut + timedelta(days=6)
        
        planning = Planning(
            nom="Valid Planning",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            actif=True
        )
        db.add(planning)
        
        # Should not raise
        db.commit()
        
        assert planning.id is not None
        assert planning.semaine_debut < planning.semaine_fin

    def test_planning_stores_date_correctly(self, db: Session):
        """Planning stores dates correctly"""
        semaine_debut = date(2026, 2, 1)
        semaine_fin = date(2026, 2, 7)
        
        planning = Planning(
            nom="Date Test",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin
        )
        db.add(planning)
        db.commit()
        
        retrieved = db.query(Planning).filter_by(id=planning.id).first()
        assert retrieved.semaine_debut == semaine_debut
        assert retrieved.semaine_fin == semaine_fin


class TestPlanningPersistence:
    """Test planning persistence to database"""

    def test_save_planning_to_db(self, db: Session):
        """Save planning to database"""
        planning = Planning(
            nom="Test Planning",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7),
            actif=True
        )
        db.add(planning)
        db.commit()
        
        # Retrieve and verify
        retrieved = db.query(Planning).filter_by(id=planning.id).first()
        
        assert retrieved is not None
        assert retrieved.nom == "Test Planning"

    def test_update_planning_in_db(self, db: Session):
        """Update existing planning"""
        planning = Planning(
            nom="Original",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7)
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
        planning = Planning(
            nom="To Delete",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7)
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

    def test_cascade_delete_repas(self, db: Session):
        """Deleting planning deletes associated repas"""
        # Create planning
        planning = Planning(
            nom="Cascade Test",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7)
        )
        db.add(planning)
        db.flush()
        
        # Create repas
        repas = Repas(
            planning_id=planning.id,
            date_repas=date(2026, 2, 1),
            type_repas="dîner"
        )
        db.add(repas)
        db.commit()
        
        repas_id = repas.id
        planning_id = planning.id
        
        # Delete planning
        db.delete(planning)
        db.commit()
        
        # Verify repas also deleted
        deleted_repas = db.query(Repas).filter_by(id=repas_id).first()
        assert deleted_repas is None


class TestPlanningQueries:
    """Test planning retrieval and filtering"""

    def test_get_planning_by_date_range(self, db: Session):
        """Retrieve plannings for date range"""
        # Create multiple plannings
        for i in range(3):
            planning = Planning(
                nom=f"Planning {i}",
                semaine_debut=date(2026, 2, 1) + timedelta(days=i*7),
                semaine_fin=date(2026, 2, 7) + timedelta(days=i*7)
            )
            db.add(planning)
        db.commit()
        
        # Query by date range
        plannings = db.query(Planning).filter(
            Planning.semaine_debut >= date(2026, 2, 1),
            Planning.semaine_debut <= date(2026, 2, 15)
        ).all()
        
        assert len(plannings) >= 2

    def test_get_active_plannings(self, db: Session):
        """Retrieve only active plannings"""
        planning_active = Planning(
            nom="Active",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7),
            actif=True
        )
        planning_inactive = Planning(
            nom="Inactive",
            semaine_debut=date(2026, 1, 1),
            semaine_fin=date(2026, 1, 7),
            actif=False
        )
        db.add_all([planning_active, planning_inactive])
        db.commit()
        
        # Query active only
        active = db.query(Planning).filter(Planning.actif == True).all()
        
        assert len(active) >= 1
        assert all(p.actif for p in active)

    def test_get_plannings_by_week(self, db: Session):
        """Retrieve plannings for specific week"""
        semaine_debut = date(2026, 2, 1)
        
        planning = Planning(
            nom="Week Planning",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_debut + timedelta(days=6)
        )
        db.add(planning)
        db.commit()
        
        retrieved = db.query(Planning).filter_by(
            semaine_debut=semaine_debut
        ).first()
        
        assert retrieved is not None
        assert retrieved.nom == "Week Planning"


class TestPlanningEdgeCases:
    """Test edge cases and error scenarios"""

    def test_planning_with_empty_repas(self, db: Session):
        """Planning can have no repas"""
        planning = Planning(
            nom="Empty Planning",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7)
        )
        db.add(planning)
        db.commit()
        
        retrieved = db.query(Planning).filter_by(id=planning.id).first()
        assert len(retrieved.repas) == 0

    def test_repas_without_recipe(self, db: Session):
        """Repas can be created without recipe"""
        planning = Planning(
            nom="Test",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7)
        )
        db.add(planning)
        db.flush()
        
        repas = Repas(
            planning_id=planning.id,
            date_repas=date(2026, 2, 1),
            type_repas="dîner",
            notes="To be filled later"
        )
        db.add(repas)
        db.commit()
        
        assert repas.recette_id is None

    def test_multiple_repas_same_day(self, db: Session):
        """Can have multiple repas on same day"""
        planning = Planning(
            nom="Multi-repas",
            semaine_debut=date(2026, 2, 1),
            semaine_fin=date(2026, 2, 7)
        )
        db.add(planning)
        db.flush()
        
        repas_list = []
        for type_repas in ["déjeuner", "dîner", "goûter"]:
            repas = Repas(
                planning_id=planning.id,
                date_repas=date(2026, 2, 1),
                type_repas=type_repas
            )
            db.add(repas)
            repas_list.append(repas)
        db.commit()
        
        retrieved_planning = db.query(Planning).filter_by(id=planning.id).first()
        assert len(retrieved_planning.repas) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


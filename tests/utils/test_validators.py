"""
Unit tests for Pydantic Validators.

Tests cover validation of all 9 Pydantic schemas from Phase 1.
"""

import pytest
from pydantic import ValidationError

from src.core.validators_pydantic import (
    RecetteInput,
    IngredientInput,
    EtapeInput,
    IngredientStockInput,
    RepasInput,
    RoutineInput,
    TacheRoutineInput,
    EntreeJournalInput,
    ProjetInput,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 1: RecetteInput TESTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestRecetteInput:
    """Test RecetteInput validator."""
    
    def test_recette_input_validates_required_fields(self):
        """Test that required fields are validated."""
        # Missing nom should fail
        with pytest.raises(ValidationError):
            RecetteInput(description="test")
    
    def test_recette_input_validates_constraints(self):
        """Test field constraints."""
        # nom must have min_length
        with pytest.raises(ValidationError):
            RecetteInput(
                nom="x",  # Too short
                description="Valid description",
            )
    
    def test_recette_input_accepts_valid_data(self):
        """Test valid recipe input."""
        recipe = RecetteInput(
            nom="PÃ¢tes Carbonara",
            description="PÃ¢tes Ã  la sauce carbonara",
            temps_preparation=15,
            temps_cuisson=20,
            portions=4,
            difficulte="moyen",
            type_repas="dÃ®ner",
            saison="Ã©tÃ©",
            ingredients=[
                IngredientInput(nom="PÃ¢tes", quantite=400, unite="g"),
            ],
            etapes=[
                EtapeInput(numero=1, description="Faire bouillir l'eau"),
            ],
        )
        
        assert recipe.portions == 4
        assert len(recipe.ingredients) == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 2: IngredientInput TESTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestIngredientInput:
    """Test IngredientInput validator."""
    
    def test_ingredient_input_validates_quantity(self):
        """Test quantity validation (must be positive)."""
        with pytest.raises(ValidationError):
            IngredientInput(
                nom="Tomate",
                quantite=-5,  # Negative
                unite="g",
            )
    
    def test_ingredient_input_accepts_valid_data(self):
        """Test valid ingredient input."""
        ing = IngredientInput(
            nom="Tomate",
            quantite=500,
            unite="g",
        )
        
        assert ing.nom == "Tomate"
        assert ing.quantite == 500


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 3: EtapeInput TESTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestEtapeInput:
    """Test EtapeInput validator."""
    
    def test_etape_input_validates_required_fields(self):
        """Test required fields."""
        with pytest.raises(ValidationError):
            EtapeInput(ordre=1)  # Missing description
    
    def test_etape_input_accepts_valid_data(self):
        """Test valid step input."""
        step = EtapeInput(
            numero=1,
            description="Faire bouillir l'eau",
        )
        
        assert step.numero == 1
        assert step.description == "Faire bouillir l'eau"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 4: RepasInput TESTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestRepasInput:
    """Test RepasInput validator."""
    
    def test_repas_input_validates_meal_type(self):
        """Test meal type validation."""
        # Should accept valid meal types
        repas = RepasInput(
            date_repas="2026-01-11",
            type_repas="dÃ®ner",
            notes="Test",
        )
        
        assert repas.type_repas == "dÃ®ner"
    
    def test_repas_input_rejects_invalid_meal_type(self):
        """Test invalid meal type."""
        with pytest.raises(ValidationError):
            RepasInput(
                date_repas="2026-01-11",
                type_repas="invalid_type",  # Invalid
                notes="Test",
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 5: RoutineInput TESTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestRoutineInput:
    """Test RoutineInput validator."""
    
    def test_routine_input_validates_required_fields(self):
        """Test required fields for routine."""
        with pytest.raises(ValidationError):
            RoutineInput(description="Routine matinale")  # Missing nom


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 6: TacheRoutineInput TESTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestTacheRoutineInput:
    """Test TacheRoutineInput validator."""
    
    def test_tache_routine_input_validates_ordre(self):
        """Test ordre validation."""
        with pytest.raises(ValidationError):
            TacheRoutineInput(
                ordre=0,  # Must be > 0
                description="TÃ¢che",
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 7: EntreeJournalInput TESTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestEntreeJournalInput:
    """Test EntreeJournalInput validator."""
    
    def test_entree_journal_input_validates_required_fields(self):
        """Test required fields."""
        with pytest.raises(ValidationError):
            EntreeJournalInput(description="EntrÃ©e sans date")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 8: ProjetInput TESTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestProjetInput:
    """Test ProjetInput validator."""
    
    def test_projet_input_validates_required_fields(self):
        """Test required fields."""
        with pytest.raises(ValidationError):
            ProjetInput(description="Projet sans nom")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 9: ALL VALIDATORS INTEGRATION TEST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.mark.unit
class TestAllValidators:
    """Test all validators work together."""
    
    def test_all_validators_importable(self):
        """Test all validators can be imported."""
        validators = [
            RecetteInput,
            IngredientInput,
            EtapeInput,
            IngredientStockInput,
            RepasInput,
            RoutineInput,
            TacheRoutineInput,
            EntreeJournalInput,
            ProjetInput,
        ]
        
        assert len(validators) == 9
        for validator in validators:
            assert hasattr(validator, 'model_validate')


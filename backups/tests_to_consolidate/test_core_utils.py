"""Phase 17: Tests pour modules core (constantes, erreurs, validateurs).

Ces tests couvrent:
- Classes d'erreur personnalisees
"""

import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock


class TestErrorClasses:
    """Tests pour classes d'erreur personnalisees."""
    
    def test_database_error_initialization(self):
        """ErreurBaseDeDonnees s'initialise correctement."""
        from src.core.errors import ErreurBaseDeDonnees
        
        error = ErreurBaseDeDonnees("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, Exception)
    
    def test_validation_error_initialization(self):
        """ErreurValidation s'initialise correctement."""
        from src.core.errors import ErreurValidation
        
        error = ErreurValidation("Invalid email")
        assert "Invalid email" in str(error)
    
    def test_error_with_extra_context(self):
        """Les erreurs acceptent du contexte supplementaire via 'details'."""
        from src.core.errors import ErreurBaseDeDonnees
        
        error = ErreurBaseDeDonnees("Operation failed", details={"query": "SELECT *"})
        assert error is not None
        assert str(error) == "Operation failed"


# NOTE: Les classes TestValidationFunctions, TestConstants, TestUtilityFunctions
# ont Ã©tÃ© supprimÃ©es car elles testaient des modules inexistants:
# - src.core.validators
# - src.core.utils  
# - Constantes MAX_BATCH_SIZE, TIMEOUT_SECONDES

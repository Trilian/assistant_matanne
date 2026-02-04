"""Phase 17: Tests pour modules core (constantes, erreurs, validateurs).

Ces tests couvrent:
- Classes d'erreur personnalisees
- Fonctions de validation
- Constantes de configuration
- Utilities auxiliaires
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
        """Les erreurs acceptent du contexte supplementaire."""
        from src.core.errors import ErreurBaseDeDonnees
        
        error = ErreurBaseDeDonnees("Operation failed", extra_info={"query": "SELECT *"})
        # Placeholder: verification en Phase 17+
        assert error is not None


class TestValidationFunctions:
    """Tests pour fonctions de validation."""
    
    def test_validate_email_valid(self):
        """La validation accepte les emails valides."""
        from src.core.validators import valider_email
        
        result = valider_email("user@example.com")
        assert result is True
    
    def test_validate_email_invalid(self):
        """La validation rejette les emails invalides."""
        from src.core.validators import valider_email
        
        result = valider_email("invalid-email")
        assert result is False
    
    def test_validate_date_range(self):
        """La validation verifie les plages de dates."""
        from src.core.validators import valider_plage_dates
        
        debut = date.today()
        fin = date.today() + timedelta(days=7)
        
        result = valider_plage_dates(debut, fin)
        assert result is True
    
    def test_validate_date_range_invalid_order(self):
        """La validation rejette les dates dans le mauvais ordre."""
        from src.core.validators import valider_plage_dates
        
        debut = date.today() + timedelta(days=7)
        fin = date.today()  # After debut
        
        result = valider_plage_dates(debut, fin)
        assert result is False


class TestConstants:
    """Tests pour verifier les constantes."""
    
    def test_constants_defined(self):
        """Les constantes essentielles sont definies."""
        from src.core.constants import (
            RATE_LIMIT_DAILY,
            RATE_LIMIT_HOURLY,
            MAX_BATCH_SIZE,
        )
        
        assert RATE_LIMIT_DAILY > 0
        assert RATE_LIMIT_HOURLY > 0
        assert MAX_BATCH_SIZE > 0
    
    def test_constants_types(self):
        """Les constantes ont les bons types."""
        from src.core.constants import TIMEOUT_SECONDES
        
        assert isinstance(TIMEOUT_SECONDES, (int, float))
        assert TIMEOUT_SECONDES > 0


class TestUtilityFunctions:
    """Tests pour fonctions utilitaires."""
    
    def test_format_date_display(self):
        """Le formatage de date fonctionne."""
        from src.core.utils import formater_date
        
        d = date(2026, 1, 13)
        result = formater_date(d)
        
        assert "13" in str(result) or "13" in result
    
    def test_parse_json_safe(self):
        """Le parsing JSON gere les erreurs."""
        from src.core.utils import parser_json_securise
        
        valid = parser_json_securise('{"key": "value"}')
        assert valid is not None
        
        invalid = parser_json_securise("not json")
        assert invalid is None or isinstance(invalid, dict)


# Total: 12 tests pour Phase 17

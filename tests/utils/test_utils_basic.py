"""
UTILS & HELPERS IMPORT TESTS  
Test all utility modules can be imported
Pattern: Import modules only (not specific functions)
"""

import pytest

# ==============================================================================
# FORMATTERS TESTS
# ==============================================================================

class TestFormatters:
    """Test formatter module imports"""
    
    def test_import_dates_formatter(self):
        """Test importing dates formatter module"""
        from src.utils.formatters import dates
        assert dates is not None
    
    def test_import_numbers_formatter(self):
        """Test importing numbers formatter module"""
        from src.utils.formatters import numbers
        assert numbers is not None
    
    def test_import_text_formatter(self):
        """Test importing text formatter module"""
        from src.utils.formatters import text
        assert text is not None
    
    def test_import_units_formatter(self):
        """Test importing units formatter module"""
        from src.utils.formatters import units
        assert units is not None
    
    def test_import_formatters_module(self):
        """Test importing formatters package"""
        from src.utils import formatters
        assert formatters is not None


# ==============================================================================
# VALIDATORS TESTS
# ==============================================================================

class TestValidators:
    """Test validator module imports"""
    
    def test_import_common_validators(self):
        """Test importing common validators"""
        from src.utils.validators import common
        assert common is not None
    
    def test_import_date_validators(self):
        """Test importing date validators"""
        from src.utils.validators import dates
        assert dates is not None
    
    def test_import_food_validators(self):
        """Test importing food validators"""
        from src.utils.validators import food
        assert food is not None
    
    def test_import_validators_module(self):
        """Test importing validators package"""
        from src.utils import validators
        assert validators is not None


# ==============================================================================
# HELPERS TESTS
# ==============================================================================

class TestHelpers:
    """Test helper module imports"""
    
    def test_import_data_helpers(self):
        """Test importing data helpers"""
        from src.utils.helpers import data
        assert data is not None
    
    def test_import_date_helpers(self):
        """Test importing date helpers"""
        from src.utils.helpers import dates
        assert dates is not None
    
    def test_import_food_helpers(self):
        """Test importing food helpers"""
        from src.utils.helpers import food
        assert food is not None
    
    def test_import_stats_helpers(self):
        """Test importing stats helpers"""
        from src.utils.helpers import stats
        assert stats is not None
    
    def test_import_string_helpers(self):
        """Test importing string helpers"""
        from src.utils.helpers import strings
        assert strings is not None
    
    def test_import_helpers_module(self):
        """Test importing helpers package"""
        from src.utils import helpers
        assert helpers is not None


# ==============================================================================
# UTILITIES CORE TESTS
# ==============================================================================

class TestUtilityCore:
    """Test core utility imports"""
    
    def test_import_constants(self):
        """Test importing constants"""
        from src.utils import constants
        assert constants is not None
    
    def test_import_media(self):
        """Test importing media utilities"""
        from src.utils import media
        assert media is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

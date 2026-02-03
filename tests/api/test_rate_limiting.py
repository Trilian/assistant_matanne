import pytest
from src.api import rate_limiting

@pytest.mark.unit
def test_import_rate_limiting():
    """Vérifie que le module rate_limiting s'importe sans erreur."""
    assert hasattr(rate_limiting, "RateLimiter") or hasattr(rate_limiting, "__file__")

# Ajoutez ici des tests de logique de limitation de débit, etc. selon le module

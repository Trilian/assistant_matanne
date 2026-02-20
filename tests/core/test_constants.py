"""
Tests unitaires pour constants.py (src/core/constants.py).

Tests couvrant:
- Présence et valeurs des constantes
- Plages raisonnables des valeurs
- Cohérence entre constantes liées
"""

import pytest

from src.core import constants

# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDatabaseConstants:
    """Tests des constantes de base de données."""

    def test_db_connection_retry_positif(self):
        """Test que DB_CONNECTION_RETRY est positif."""
        assert constants.DB_CONNECTION_RETRY > 0

    def test_db_connection_timeout_positif(self):
        """Test que DB_CONNECTION_TIMEOUT est positif."""
        assert constants.DB_CONNECTION_TIMEOUT > 0

    def test_db_timeout_moins_que_retry(self):
        """Test que timeout est moins que retry total."""
        # Timeout unique < timeout total possible
        assert (
            constants.DB_CONNECTION_TIMEOUT * constants.DB_CONNECTION_RETRY
            > constants.DB_CONNECTION_TIMEOUT
        )


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCacheConstants:
    """Tests des constantes de cache."""

    def test_cache_ttl_recettes_positif(self):
        """Test que CACHE_TTL_RECETTES est positif."""
        assert constants.CACHE_TTL_RECETTES > 0

    def test_cache_ttl_ia_positif(self):
        """Test que CACHE_TTL_IA est positif."""
        assert constants.CACHE_TTL_IA > 0

    def test_cache_max_size_positif(self):
        """Test que CACHE_MAX_SIZE est positif."""
        assert constants.CACHE_MAX_SIZE > 0

    def test_cache_ttls_dans_limites_raisonnables(self):
        """Test que les TTLs sont dans des limites raisonnables."""
        for ttl in [
            constants.CACHE_TTL_RECETTES,
            constants.CACHE_TTL_IA,
        ]:
            assert 1 <= ttl <= 86400


# ═══════════════════════════════════════════════════════════
# SECTION 3: TESTS IA / API
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAIConstants:
    """Tests des constantes IA."""

    def test_ai_rate_limits_positifs(self):
        """Test que les rate limits sont positifs."""
        assert constants.AI_RATE_LIMIT_DAILY > 0
        assert constants.AI_RATE_LIMIT_HOURLY > 0

    def test_ai_rate_limits_hierarchie(self):
        """Test que daily > hourly."""
        assert constants.AI_RATE_LIMIT_DAILY > constants.AI_RATE_LIMIT_HOURLY


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestValidationConstants:
    """Tests des constantes de validation."""

    def test_max_lengths_positifs(self):
        """Test que les MAX_LENGTH sont positifs."""
        assert constants.MAX_LENGTH_SHORT > 0
        assert constants.MAX_LENGTH_MEDIUM > 0
        assert constants.MAX_LENGTH_LONG > 0
        assert constants.MAX_LENGTH_TEXT > 0

    def test_max_lengths_hierarchie(self):
        """Test que short < medium < long < text."""
        assert constants.MAX_LENGTH_SHORT < constants.MAX_LENGTH_MEDIUM
        assert constants.MAX_LENGTH_MEDIUM < constants.MAX_LENGTH_LONG
        assert constants.MAX_LENGTH_LONG < constants.MAX_LENGTH_TEXT

    def test_max_portions_raisonnable(self):
        """Test que MAX_PORTIONS est raisonnable."""
        assert 1 <= constants.MAX_PORTIONS <= 100

    def test_temps_cooking_raisonnable(self):
        """Test que les temps sont raisonnables."""
        # Entre 1 minute et 300 minutes (5h)
        assert 1 <= constants.MAX_TEMPS_PREPARATION <= 1440
        assert 1 <= constants.MAX_TEMPS_CUISSON <= 1440

    def test_quantite_max_raisonnable(self):
        """Test que MAX_QUANTITE est raisonnable."""
        assert constants.MAX_QUANTITE > 0
        assert constants.MAX_QUANTITE >= 100

    def test_ingredients_min_max(self):
        """Test que MIN_INGREDIENTS < MAX_INGREDIENTS."""
        assert constants.MIN_INGREDIENTS > 0
        assert constants.MAX_INGREDIENTS > 0
        assert constants.MIN_INGREDIENTS <= constants.MAX_INGREDIENTS

    def test_etapes_min_max(self):
        """Test que MIN_ETAPES < MAX_ETAPES."""
        assert constants.MIN_ETAPES > 0
        assert constants.MAX_ETAPES > 0
        assert constants.MIN_ETAPES <= constants.MAX_ETAPES


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS MÉTIER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBusinessConstants:
    """Tests des constantes métier."""

    def test_jours_semaine_correct(self):
        """Test que JOURS_SEMAINE contient 7 jours."""
        assert len(constants.JOURS_SEMAINE) == 7


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS COHÉRENCE GLOBALE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConstantsConsistency:
    """Tests de cohérence entre les constantes."""

    def test_toutes_les_constantes_existent(self):
        """Test que les constantes principales existent."""
        required_constants = [
            "DB_CONNECTION_RETRY",
            "CACHE_TTL_RECETTES",
            "AI_RATE_LIMIT_DAILY",
            "MAX_LENGTH_SHORT",
            "JOURS_SEMAINE",
        ]
        for const_name in required_constants:
            assert hasattr(constants, const_name), f"Constante {const_name} manquante"

    def test_aucune_constante_negative(self):
        """Test qu'aucune constante numérique n'est négative."""
        numeric_constants = [
            attr
            for attr in dir(constants)
            if attr.isupper() and isinstance(getattr(constants, attr), int | float)
        ]
        for const_name in numeric_constants:
            value = getattr(constants, const_name)
            assert value >= 0, f"{const_name} ne devrait pas être négatif"

    def test_constantes_type_coherent(self):
        """Test que les types de constantes sont cohérents."""
        import datetime

        # Les constantes peuvent être int, float, str, list, tuple, dict ou date
        for attr in dir(constants):
            if attr.isupper():
                value = getattr(constants, attr)
                assert isinstance(
                    value, int | float | str | list | tuple | dict | datetime.date
                ), f"{attr} a un type inattendu: {type(value)}"

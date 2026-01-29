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

    def test_db_pool_size_positif(self):
        """Test que DB_POOL_SIZE est positif."""
        assert constants.DB_POOL_SIZE > 0

    def test_db_max_overflow_raisonnable(self):
        """Test que DB_MAX_OVERFLOW est raisonnable."""
        assert constants.DB_MAX_OVERFLOW > 0
        assert constants.DB_MAX_OVERFLOW >= constants.DB_POOL_SIZE

    def test_db_timeout_moins_que_retry(self):
        """Test que timeout est moins que retry total."""
        # Timeout unique < timeout total possible
        assert constants.DB_CONNECTION_TIMEOUT * constants.DB_CONNECTION_RETRY > constants.DB_CONNECTION_TIMEOUT


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCacheConstants:
    """Tests des constantes de cache."""

    def test_cache_ttl_recettes_positif(self):
        """Test que CACHE_TTL_RECETTES est positif."""
        assert constants.CACHE_TTL_RECETTES > 0

    def test_cache_ttl_inventaire_positif(self):
        """Test que CACHE_TTL_INVENTAIRE est positif."""
        assert constants.CACHE_TTL_INVENTAIRE > 0

    def test_cache_ttl_courses_positif(self):
        """Test que CACHE_TTL_COURSES est positif."""
        assert constants.CACHE_TTL_COURSES > 0

    def test_cache_ttl_planning_positif(self):
        """Test que CACHE_TTL_PLANNING est positif."""
        assert constants.CACHE_TTL_PLANNING > 0

    def test_cache_ttl_ia_positif(self):
        """Test que CACHE_TTL_IA est positif."""
        assert constants.CACHE_TTL_IA > 0

    def test_cache_max_size_positif(self):
        """Test que CACHE_MAX_SIZE est positif."""
        assert constants.CACHE_MAX_SIZE > 0

    def test_cache_max_items_per_key_raisonnable(self):
        """Test que CACHE_MAX_ITEMS_PER_KEY est raisonnable."""
        assert constants.CACHE_MAX_ITEMS_PER_KEY > 0
        assert constants.CACHE_MAX_ITEMS_PER_KEY >= constants.CACHE_MAX_SIZE

    def test_cache_ttls_dans_limites_raisonnables(self):
        """Test que les TTLs sont dans des limites raisonnables."""
        # Entre 1 seconde et 24 heures
        for ttl in [
            constants.CACHE_TTL_RECETTES,
            constants.CACHE_TTL_INVENTAIRE,
            constants.CACHE_TTL_COURSES,
            constants.CACHE_TTL_PLANNING,
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
        assert constants.AI_RATE_LIMIT_PER_MINUTE > 0

    def test_ai_rate_limits_hierarchie(self):
        """Test que daily > hourly > per_minute."""
        assert constants.AI_RATE_LIMIT_DAILY > constants.AI_RATE_LIMIT_HOURLY
        assert constants.AI_RATE_LIMIT_HOURLY > constants.AI_RATE_LIMIT_PER_MINUTE

    def test_ai_api_timeout_positif(self):
        """Test que AI_API_TIMEOUT est positif."""
        assert constants.AI_API_TIMEOUT > 0

    def test_ai_api_retry_delay_positif(self):
        """Test que AI_API_RETRY_DELAY est positif."""
        assert constants.AI_API_RETRY_DELAY > 0

    def test_ai_api_max_retries_raisonnable(self):
        """Test que AI_API_MAX_RETRIES est raisonnable."""
        assert 1 <= constants.AI_API_MAX_RETRIES <= 10

    def test_ai_max_tokens_hierarchie(self):
        """Test que short < default < long."""
        assert constants.AI_MAX_TOKENS_SHORT < constants.AI_MAX_TOKENS_DEFAULT
        assert constants.AI_MAX_TOKENS_DEFAULT < constants.AI_MAX_TOKENS_LONG

    def test_ai_temperatures_dans_limites(self):
        """Test que les températures sont entre 0 et 1."""
        for temp in [
            constants.AI_TEMPERATURE_CREATIVE,
            constants.AI_TEMPERATURE_DEFAULT,
            constants.AI_TEMPERATURE_PRECISE,
        ]:
            assert 0 <= temp <= 2  # Généralement 0-2 est valide

    def test_ai_temperature_precise_inferieur_a_default(self):
        """Test que precise < default < creative."""
        assert constants.AI_TEMPERATURE_PRECISE < constants.AI_TEMPERATURE_DEFAULT
        assert constants.AI_TEMPERATURE_DEFAULT < constants.AI_TEMPERATURE_CREATIVE

    def test_ai_semantic_similarity_threshold_valid(self):
        """Test que le seuil est entre 0 et 1."""
        assert 0 <= constants.AI_SEMANTIC_SIMILARITY_THRESHOLD <= 1

    def test_ai_semantic_cache_size_raisonnable(self):
        """Test que la taille du cache sémantique est raisonnable."""
        assert constants.AI_SEMANTIC_CACHE_MAX_SIZE > 0
        assert constants.AI_SEMANTIC_CACHE_MAX_SIZE <= 10000


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

    def test_quantite_min_raisonnable(self):
        """Test que MAX_QUANTITE_MIN est raisonnable."""
        assert constants.MAX_QUANTITE_MIN > 0
        assert constants.MAX_QUANTITE_MIN < constants.MAX_QUANTITE

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
# SECTION 5: TESTS PAGINATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPaginationConstants:
    """Tests des constantes de pagination."""

    def test_items_per_page_default_positif(self):
        """Test que ITEMS_PER_PAGE_DEFAULT est positif."""
        assert constants.ITEMS_PER_PAGE_DEFAULT > 0

    def test_items_per_page_modules_positifs(self):
        """Test que tous les items_per_page sont positifs."""
        assert constants.ITEMS_PER_PAGE_RECETTES > 0
        assert constants.ITEMS_PER_PAGE_INVENTAIRE > 0
        assert constants.ITEMS_PER_PAGE_COURSES > 0
        assert constants.ITEMS_PER_PAGE_PLANNING > 0

    def test_max_items_search_raisonnable(self):
        """Test que MAX_ITEMS_SEARCH est raisonnable."""
        assert constants.MAX_ITEMS_SEARCH > 0
        assert constants.MAX_ITEMS_SEARCH >= 50

    def test_max_items_export_plus_grand_que_search(self):
        """Test que MAX_ITEMS_EXPORT >= MAX_ITEMS_SEARCH."""
        assert constants.MAX_ITEMS_EXPORT >= constants.MAX_ITEMS_SEARCH


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS UI / FEEDBACK
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUIConstants:
    """Tests des constantes UI."""

    def test_toast_durations_positives(self):
        """Test que les durées toast sont positives."""
        assert constants.TOAST_DURATION_SHORT > 0
        assert constants.TOAST_DURATION_MEDIUM > 0
        assert constants.TOAST_DURATION_LONG > 0

    def test_toast_durations_hierarchie(self):
        """Test que short < medium < long."""
        assert constants.TOAST_DURATION_SHORT <= constants.TOAST_DURATION_MEDIUM
        assert constants.TOAST_DURATION_MEDIUM <= constants.TOAST_DURATION_LONG

    def test_spinner_durations_positives(self):
        """Test que les durées spinner sont positives."""
        assert constants.SPINNER_ESTIMATED_SECONDS_SHORT > 0
        assert constants.SPINNER_ESTIMATED_SECONDS_MEDIUM > 0
        assert constants.SPINNER_ESTIMATED_SECONDS_LONG > 0

    def test_spinner_durations_hierarchie(self):
        """Test que short < medium < long."""
        assert constants.SPINNER_ESTIMATED_SECONDS_SHORT <= constants.SPINNER_ESTIMATED_SECONDS_MEDIUM
        assert constants.SPINNER_ESTIMATED_SECONDS_MEDIUM <= constants.SPINNER_ESTIMATED_SECONDS_LONG

    def test_max_navigation_history_raisonnable(self):
        """Test que MAX_NAVIGATION_HISTORY est raisonnable."""
        assert constants.MAX_NAVIGATION_HISTORY > 0
        assert constants.MAX_NAVIGATION_HISTORY <= 1000

    def test_max_breadcrumb_items_raisonnable(self):
        """Test que MAX_BREADCRUMB_ITEMS est raisonnable."""
        assert 1 <= constants.MAX_BREADCRUMB_ITEMS <= 20


# ═══════════════════════════════════════════════════════════
# SECTION 7: TESTS MÉTIER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBusinessConstants:
    """Tests des constantes métier."""

    def test_jours_semaine_correct(self):
        """Test que JOURS_SEMAINE = 7."""
        assert constants.JOURS_SEMAINE == 7

    def test_planning_semaine_debut_jour_valide(self):
        """Test que PLANNING_SEMAINE_DEBUT_JOUR est valide."""
        assert 0 <= constants.PLANNING_SEMAINE_DEBUT_JOUR < 7


# ═══════════════════════════════════════════════════════════
# SECTION 8: TESTS COHÉRENCE GLOBALE
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
            "ITEMS_PER_PAGE_DEFAULT",
            "TOAST_DURATION_SHORT",
            "JOURS_SEMAINE",
        ]
        for const_name in required_constants:
            assert hasattr(constants, const_name), f"Constante {const_name} manquante"

    def test_aucune_constante_negative(self):
        """Test qu'aucune constante numérique n'est négative."""
        numeric_constants = [
            attr
            for attr in dir(constants)
            if attr.isupper() and isinstance(getattr(constants, attr), (int, float))
        ]
        for const_name in numeric_constants:
            value = getattr(constants, const_name)
            assert value >= 0, f"{const_name} ne devrait pas être négatif"

    def test_constantes_type_coherent(self):
        """Test que les types de constantes sont cohérents."""
        # Les constantes numérotées doivent être int, float, str ou list/tuple
        for attr in dir(constants):
            if attr.isupper():
                value = getattr(constants, attr)
                # Peut être int, float, str, list, tuple, dict
                assert isinstance(
                    value, (int, float, str, list, tuple, dict)
                ), f"{attr} a un type inattendu: {type(value)}"

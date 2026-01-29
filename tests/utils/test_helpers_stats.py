"""
Tests pour les helpers statistiques
"""

import pytest

from src.utils.helpers.stats import (
    calculate_average,
    calculate_median,
    calculate_variance,
    calculate_std_dev,
    calculate_percentile,
    calculate_mode,
    calculate_range,
    moving_average,
)


class TestCalculateAverage:
    """Tests pour calculate_average"""

    def test_average_basic(self):
        """Test moyenne basique"""
        result = calculate_average([1, 2, 3, 4, 5])
        assert result == 3.0

    def test_average_single(self):
        """Test un Ã©lÃ©ment"""
        result = calculate_average([5])
        assert result == 5.0

    def test_average_empty(self):
        """Test liste vide"""
        result = calculate_average([])
        assert result == 0.0

    def test_average_floats(self):
        """Test avec floats"""
        result = calculate_average([1.5, 2.5, 3.5])
        assert result == 2.5


class TestCalculateMedian:
    """Tests pour calculate_median"""

    def test_median_odd(self):
        """Test mÃ©diane avec nombre impair"""
        result = calculate_median([1, 2, 3, 4, 5])
        assert result == 3.0

    def test_median_even(self):
        """Test mÃ©diane avec nombre pair"""
        result = calculate_median([1, 2, 3, 4])
        assert result == 2.5

    def test_median_empty(self):
        """Test liste vide"""
        result = calculate_median([])
        assert result == 0.0

    def test_median_unsorted(self):
        """Test liste non triÃ©e"""
        result = calculate_median([5, 1, 3, 2, 4])
        assert result == 3.0


class TestCalculateVariance:
    """Tests pour calculate_variance"""

    def test_variance_basic(self):
        """Test variance basique"""
        result = calculate_variance([1, 2, 3, 4, 5])
        assert result == 2.5  # Variance d'Ã©chantillon

    def test_variance_empty(self):
        """Test liste vide"""
        result = calculate_variance([])
        assert result == 0.0

    def test_variance_single(self):
        """Test un Ã©lÃ©ment"""
        result = calculate_variance([5])
        assert result == 0.0


class TestCalculateStdDev:
    """Tests pour calculate_std_dev"""

    def test_std_dev_basic(self):
        """Test Ã©cart-type basique"""
        result = calculate_std_dev([1, 2, 3, 4, 5])
        # Ã‰cart-type d'Ã©chantillon de [1,2,3,4,5] â‰ˆ 1.58
        assert result > 1.5 and result < 1.6

    def test_std_dev_empty(self):
        """Test liste vide"""
        result = calculate_std_dev([])
        assert result == 0.0

    def test_std_dev_single(self):
        """Test un Ã©lÃ©ment"""
        result = calculate_std_dev([5])
        assert result == 0.0


class TestCalculatePercentile:
    """Tests pour calculate_percentile"""

    def test_percentile_50(self):
        """Test 50e percentile (mÃ©diane)"""
        result = calculate_percentile([1, 2, 3, 4, 5], 50)
        assert result == 3.0

    def test_percentile_0(self):
        """Test 0e percentile (min)"""
        result = calculate_percentile([1, 2, 3, 4, 5], 0)
        assert result == 1.0

    def test_percentile_100(self):
        """Test 100e percentile (max)"""
        result = calculate_percentile([1, 2, 3, 4, 5], 100)
        assert result == 5.0

    def test_percentile_25(self):
        """Test 25e percentile"""
        result = calculate_percentile([1, 2, 3, 4, 5], 25)
        assert result == 2.0

    def test_percentile_empty(self):
        """Test liste vide"""
        result = calculate_percentile([], 50)
        assert result == 0.0


class TestCalculateMode:
    """Tests pour calculate_mode"""

    def test_mode_basic(self):
        """Test mode basique"""
        result = calculate_mode([1, 2, 2, 3, 3, 3])
        assert result == 3

    def test_mode_single(self):
        """Test un Ã©lÃ©ment"""
        result = calculate_mode([5])
        assert result == 5

    def test_mode_empty(self):
        """Test liste vide"""
        result = calculate_mode([])
        assert result is None

    def test_mode_strings(self):
        """Test avec strings"""
        result = calculate_mode(["a", "b", "b", "c"])
        assert result == "b"


class TestCalculateRange:
    """Tests pour calculate_range"""

    def test_range_basic(self):
        """Test Ã©tendue basique"""
        result = calculate_range([1, 2, 3, 4, 5])
        assert result == 4.0

    def test_range_single(self):
        """Test un Ã©lÃ©ment"""
        result = calculate_range([5])
        assert result == 0.0

    def test_range_empty(self):
        """Test liste vide"""
        result = calculate_range([])
        assert result == 0.0

    def test_range_negative(self):
        """Test avec nÃ©gatifs"""
        result = calculate_range([-5, 0, 5])
        assert result == 10.0


class TestMovingAverage:
    """Tests pour moving_average"""

    def test_moving_average_basic(self):
        """Test moyenne mobile basique"""
        result = moving_average([1, 2, 3, 4, 5], 3)
        assert result == [2.0, 3.0, 4.0]

    def test_moving_average_window_2(self):
        """Test fenÃªtre de 2"""
        result = moving_average([1, 2, 3, 4], 2)
        assert result == [1.5, 2.5, 3.5]

    def test_moving_average_window_too_large(self):
        """Test fenÃªtre trop grande"""
        result = moving_average([1, 2], 3)
        assert result == []

    def test_moving_average_exact_size(self):
        """Test fenÃªtre = taille liste"""
        result = moving_average([1, 2, 3], 3)
        assert result == [2.0]


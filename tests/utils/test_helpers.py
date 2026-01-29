"""
Tests pour src/utils/helpers/ - data, strings, stats
Ces tests couvrent ~170 statements de fonctions pures
"""

import pytest
from typing import Any


# =============================================================================
# Tests helpers/strings.py (~37 statements)
# =============================================================================

class TestGenerateId:
    """Tests pour generate_id"""
    
    def test_generate_id_dict(self):
        from src.utils.helpers.strings import generate_id
        result = generate_id({"nom": "test", "value": 123})
        assert len(result) == 16
        assert result.isalnum()
    
    def test_generate_id_deterministic(self):
        from src.utils.helpers.strings import generate_id
        data = {"key": "value"}
        assert generate_id(data) == generate_id(data)
    
    def test_generate_id_different_data(self):
        from src.utils.helpers.strings import generate_id
        id1 = generate_id({"a": 1})
        id2 = generate_id({"b": 2})
        assert id1 != id2


class TestNormalizeWhitespace:
    """Tests pour normalize_whitespace"""
    
    def test_normalize_multiple_spaces(self):
        from src.utils.helpers.strings import normalize_whitespace
        assert normalize_whitespace("  hello    world  ") == "hello world"
    
    def test_normalize_tabs_newlines(self):
        from src.utils.helpers.strings import normalize_whitespace
        assert normalize_whitespace("hello\n\tworld") == "hello world"
    
    def test_normalize_empty(self):
        from src.utils.helpers.strings import normalize_whitespace
        assert normalize_whitespace("") == ""


class TestRemoveAccents:
    """Tests pour remove_accents"""
    
    def test_remove_accents_french(self):
        from src.utils.helpers.strings import remove_accents
        assert remove_accents("café crème") == "cafe creme"
    
    def test_remove_accents_uppercase(self):
        from src.utils.helpers.strings import remove_accents
        result = remove_accents("CAFÃ‰ CRÃˆME")
        assert "Ã‰" not in result
        assert "Ãˆ" not in result
    
    def test_remove_accents_spanish(self):
        from src.utils.helpers.strings import remove_accents
        result = remove_accents("niño")
        assert "ñ" not in result


class TestCamelToSnake:
    """Tests pour camel_to_snake"""
    
    def test_camel_to_snake_simple(self):
        from src.utils.helpers.strings import camel_to_snake
        assert camel_to_snake("myVariableName") == "my_variable_name"
    
    def test_camel_to_snake_single_word(self):
        from src.utils.helpers.strings import camel_to_snake
        assert camel_to_snake("word") == "word"


class TestSnakeToCamel:
    """Tests pour snake_to_camel"""
    
    def test_snake_to_camel_simple(self):
        from src.utils.helpers.strings import snake_to_camel
        assert snake_to_camel("my_variable_name") == "myVariableName"
    
    def test_snake_to_camel_single_word(self):
        from src.utils.helpers.strings import snake_to_camel
        assert snake_to_camel("word") == "word"


class TestPluralize:
    """Tests pour pluralize"""
    
    def test_pluralize_singular(self):
        from src.utils.helpers.strings import pluralize
        assert pluralize("item", 1) == "1 item"
    
    def test_pluralize_plural(self):
        from src.utils.helpers.strings import pluralize
        assert pluralize("item", 5) == "5 items"
    
    def test_pluralize_custom_plural(self):
        from src.utils.helpers.strings import pluralize
        assert pluralize("cheval", 2, "chevaux") == "2 chevaux"
    
    def test_pluralize_y_ending(self):
        from src.utils.helpers.strings import pluralize
        assert pluralize("berry", 3) == "3 berries"
    
    def test_pluralize_s_ending(self):
        from src.utils.helpers.strings import pluralize
        assert pluralize("class", 2) == "2 classes"


class TestMaskSensitive:
    """Tests pour mask_sensitive"""
    
    def test_mask_sensitive_normal(self):
        from src.utils.helpers.strings import mask_sensitive
        assert mask_sensitive("1234567890", 4) == "1234******"
    
    def test_mask_sensitive_short(self):
        from src.utils.helpers.strings import mask_sensitive
        assert mask_sensitive("1234", 4) == "1234"
    
    def test_mask_sensitive_default(self):
        from src.utils.helpers.strings import mask_sensitive
        result = mask_sensitive("password123")
        assert result.startswith("pass")
        assert "*" in result


# =============================================================================
# Tests helpers/data.py (~50 statements)
# =============================================================================

class TestSafeGet:
    """Tests pour safe_get"""
    
    def test_safe_get_nested(self):
        from src.utils.helpers.data import safe_get
        data = {"a": {"b": {"c": 1}}}
        assert safe_get(data, "a", "b", "c") == 1
    
    def test_safe_get_missing(self):
        from src.utils.helpers.data import safe_get
        data = {"a": 1}
        assert safe_get(data, "b", "c", default=0) == 0
    
    def test_safe_get_none(self):
        from src.utils.helpers.data import safe_get
        data = {"a": None}
        assert safe_get(data, "a", "b", default="default") == "default"
    
    def test_safe_get_not_dict(self):
        from src.utils.helpers.data import safe_get
        data = {"a": "string"}
        assert safe_get(data, "a", "b", default="default") == "default"


class TestGroupBy:
    """Tests pour group_by"""
    
    def test_group_by_simple(self):
        from src.utils.helpers.data import group_by
        items = [
            {"type": "A", "val": 1}, 
            {"type": "A", "val": 2}, 
            {"type": "B", "val": 3}
        ]
        result = group_by(items, "type")
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1
    
    def test_group_by_empty(self):
        from src.utils.helpers.data import group_by
        assert group_by([], "type") == {}


class TestCountBy:
    """Tests pour count_by"""
    
    def test_count_by_simple(self):
        from src.utils.helpers.data import count_by
        items = [{"type": "A"}, {"type": "A"}, {"type": "B"}]
        result = count_by(items, "type")
        assert result["A"] == 2
        assert result["B"] == 1
    
    def test_count_by_empty(self):
        from src.utils.helpers.data import count_by
        assert count_by([], "type") == {}


class TestDeduplicate:
    """Tests pour deduplicate"""
    
    def test_deduplicate_simple(self):
        from src.utils.helpers.data import deduplicate
        assert deduplicate([1, 2, 2, 3]) == [1, 2, 3]
    
    def test_deduplicate_with_key(self):
        from src.utils.helpers.data import deduplicate
        items = [{"id": 1}, {"id": 1}, {"id": 2}]
        result = deduplicate(items, key=lambda x: x["id"])
        assert len(result) == 2
    
    def test_deduplicate_empty(self):
        from src.utils.helpers.data import deduplicate
        assert deduplicate([]) == []


# =============================================================================
# Tests helpers/stats.py (~48 statements)
# =============================================================================

class TestCalculateAverage:
    """Tests pour calculate_average"""
    
    def test_average_normal(self):
        from src.utils.helpers.stats import calculate_average
        assert calculate_average([1, 2, 3, 4, 5]) == 3.0
    
    def test_average_empty(self):
        from src.utils.helpers.stats import calculate_average
        assert calculate_average([]) == 0.0
    
    def test_average_single(self):
        from src.utils.helpers.stats import calculate_average
        assert calculate_average([5]) == 5.0


class TestCalculateMedian:
    """Tests pour calculate_median"""
    
    def test_median_odd_count(self):
        from src.utils.helpers.stats import calculate_median
        assert calculate_median([1, 2, 3, 4, 5]) == 3.0
    
    def test_median_even_count(self):
        from src.utils.helpers.stats import calculate_median
        assert calculate_median([1, 2, 3, 4]) == 2.5
    
    def test_median_empty(self):
        from src.utils.helpers.stats import calculate_median
        assert calculate_median([]) == 0.0
    
    def test_median_unsorted(self):
        from src.utils.helpers.stats import calculate_median
        assert calculate_median([5, 1, 3, 2, 4]) == 3.0


class TestCalculateVariance:
    """Tests pour calculate_variance"""
    
    def test_variance_normal(self):
        from src.utils.helpers.stats import calculate_variance
        result = calculate_variance([1, 2, 3, 4, 5])
        assert result == 2.5  # sample variance
    
    def test_variance_empty(self):
        from src.utils.helpers.stats import calculate_variance
        assert calculate_variance([]) == 0.0
    
    def test_variance_single(self):
        from src.utils.helpers.stats import calculate_variance
        assert calculate_variance([5]) == 0.0


class TestCalculateStdDev:
    """Tests pour calculate_std_dev"""
    
    def test_std_dev_normal(self):
        from src.utils.helpers.stats import calculate_std_dev
        result = calculate_std_dev([1, 2, 3, 4, 5])
        assert 1.5 < result < 1.6  # ~1.5811
    
    def test_std_dev_empty(self):
        from src.utils.helpers.stats import calculate_std_dev
        assert calculate_std_dev([]) == 0.0
    
    def test_std_dev_single(self):
        from src.utils.helpers.stats import calculate_std_dev
        assert calculate_std_dev([5]) == 0.0


class TestCalculatePercentile:
    """Tests pour calculate_percentile"""
    
    def test_percentile_50(self):
        from src.utils.helpers.stats import calculate_percentile
        result = calculate_percentile([1, 2, 3, 4, 5], 50)
        assert result == 3.0
    
    def test_percentile_empty(self):
        from src.utils.helpers.stats import calculate_percentile
        result = calculate_percentile([], 50)
        # Peut retourner 0 ou lever une exception selon l'implémentation
        assert result == 0.0 or result is None


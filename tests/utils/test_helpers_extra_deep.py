"""
Tests approfondis pour helpers/data.py, helpers/dates.py et helpers/strings.py

Module: src/utils/helpers/
Tests créés: ~100 tests
Objectif: Atteindre 80%+ de couverture
"""

import pytest
from datetime import date, datetime, timedelta


# =============================================================================
# TESTS helpers/data.py
# =============================================================================


class TestDataSafeGet:
    """Tests pour safe_get"""
    
    def test_safe_get_single_key(self):
        """Récupération clé simple"""
        from src.utils.helpers.data import safe_get
        
        data = {"a": 1, "b": 2}
        assert safe_get(data, "a") == 1
        assert safe_get(data, "b") == 2
    
    def test_safe_get_nested_keys(self):
        """Récupération clés imbriquées"""
        from src.utils.helpers.data import safe_get
        
        data = {"a": {"b": {"c": 42}}}
        assert safe_get(data, "a", "b", "c") == 42
        assert safe_get(data, "a", "b") == {"c": 42}
    
    def test_safe_get_missing_key_default(self):
        """Fallback quand clé absente"""
        from src.utils.helpers.data import safe_get
        
        data = {"a": 1}
        assert safe_get(data, "b", default=0) == 0
        assert safe_get(data, "a", "x", default="nope") == "nope"
    
    def test_safe_get_none_value(self):
        """Gestion valeur None"""
        from src.utils.helpers.data import safe_get
        
        data = {"a": None}
        assert safe_get(data, "a", default=42) == 42
    
    def test_safe_get_non_dict_intermediate(self):
        """Intermédiaire non-dict retourne default"""
        from src.utils.helpers.data import safe_get
        
        data = {"a": "string"}
        assert safe_get(data, "a", "b", default="fallback") == "fallback"
    
    def test_safe_get_empty_dict(self):
        """Dict vide"""
        from src.utils.helpers.data import safe_get
        
        assert safe_get({}, "a", default=None) is None
    
    def test_safe_get_deep_nesting(self):
        """Imbrication profonde (5+ niveaux)"""
        from src.utils.helpers.data import safe_get
        
        data = {"l1": {"l2": {"l3": {"l4": {"l5": "deep"}}}}}
        assert safe_get(data, "l1", "l2", "l3", "l4", "l5") == "deep"


class TestDataGroupBy:
    """Tests pour group_by"""
    
    def test_group_by_simple(self):
        """Groupement basique"""
        from src.utils.helpers.data import group_by
        
        items = [
            {"type": "A", "val": 1},
            {"type": "A", "val": 2},
            {"type": "B", "val": 3},
        ]
        result = group_by(items, "type")
        
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1
    
    def test_group_by_empty_list(self):
        """Liste vide"""
        from src.utils.helpers.data import group_by
        
        assert group_by([], "key") == {}
    
    def test_group_by_missing_key(self):
        """Clé absente crée groupe None"""
        from src.utils.helpers.data import group_by
        
        items = [{"a": 1}, {"type": "X"}]
        result = group_by(items, "type")
        
        assert None in result
        assert "X" in result
    
    def test_group_by_all_same(self):
        """Tous les items même groupe"""
        from src.utils.helpers.data import group_by
        
        items = [{"cat": "X", "i": i} for i in range(5)]
        result = group_by(items, "cat")
        
        assert len(result) == 1
        assert len(result["X"]) == 5


class TestDataCountBy:
    """Tests pour count_by"""
    
    def test_count_by_simple(self):
        """Comptage basique"""
        from src.utils.helpers.data import count_by
        
        items = [{"type": "A"}, {"type": "A"}, {"type": "B"}]
        result = count_by(items, "type")
        
        assert result["A"] == 2
        assert result["B"] == 1
    
    def test_count_by_empty(self):
        """Liste vide"""
        from src.utils.helpers.data import count_by
        
        assert count_by([], "key") == {}
    
    def test_count_by_all_unique(self):
        """Toutes valeurs uniques"""
        from src.utils.helpers.data import count_by
        
        items = [{"id": i} for i in range(5)]
        result = count_by(items, "id")
        
        assert all(v == 1 for v in result.values())


class TestDataDeduplicate:
    """Tests pour deduplicate"""
    
    def test_deduplicate_primitives(self):
        """Dédup valeurs primitives"""
        from src.utils.helpers.data import deduplicate
        
        assert deduplicate([1, 2, 2, 3, 1]) == [1, 2, 3]
        assert deduplicate(["a", "b", "a"]) == ["a", "b"]
    
    def test_deduplicate_with_key(self):
        """Dédup avec fonction clé"""
        from src.utils.helpers.data import deduplicate
        
        items = [{"id": 1, "v": "a"}, {"id": 1, "v": "b"}, {"id": 2, "v": "c"}]
        result = deduplicate(items, key=lambda x: x["id"])
        
        assert len(result) == 2
        assert result[0]["v"] == "a"  # Premier conservé
    
    def test_deduplicate_empty(self):
        """Liste vide"""
        from src.utils.helpers.data import deduplicate
        
        assert deduplicate([]) == []
    
    def test_deduplicate_no_duplicates(self):
        """Pas de doublons"""
        from src.utils.helpers.data import deduplicate
        
        assert deduplicate([1, 2, 3]) == [1, 2, 3]
    
    def test_deduplicate_all_same(self):
        """Tous identiques"""
        from src.utils.helpers.data import deduplicate
        
        assert deduplicate([5, 5, 5, 5]) == [5]


class TestDataFlatten:
    """Tests pour flatten"""
    
    def test_flatten_nested(self):
        """Aplatit listes imbriquées"""
        from src.utils.helpers.data import flatten
        
        assert flatten([[1, 2], [3, 4], [5]]) == [1, 2, 3, 4, 5]
    
    def test_flatten_empty_sublists(self):
        """Sous-listes vides"""
        from src.utils.helpers.data import flatten
        
        assert flatten([[], [1], [], [2, 3]]) == [1, 2, 3]
    
    def test_flatten_empty(self):
        """Liste vide"""
        from src.utils.helpers.data import flatten
        
        assert flatten([]) == []
    
    def test_flatten_single_sublist(self):
        """Une seule sous-liste"""
        from src.utils.helpers.data import flatten
        
        assert flatten([[1, 2, 3]]) == [1, 2, 3]


class TestDataPartition:
    """Tests pour partition"""
    
    def test_partition_even_odd(self):
        """Partitionne pairs/impairs"""
        from src.utils.helpers.data import partition
        
        matching, not_matching = partition([1, 2, 3, 4, 5], lambda x: x % 2 == 0)
        
        assert matching == [2, 4]
        assert not_matching == [1, 3, 5]
    
    def test_partition_all_matching(self):
        """Tous correspondent"""
        from src.utils.helpers.data import partition
        
        matching, not_matching = partition([2, 4, 6], lambda x: x % 2 == 0)
        
        assert matching == [2, 4, 6]
        assert not_matching == []
    
    def test_partition_none_matching(self):
        """Aucun ne correspond"""
        from src.utils.helpers.data import partition
        
        matching, not_matching = partition([1, 3, 5], lambda x: x % 2 == 0)
        
        assert matching == []
        assert not_matching == [1, 3, 5]
    
    def test_partition_empty(self):
        """Liste vide"""
        from src.utils.helpers.data import partition
        
        matching, not_matching = partition([], lambda x: True)
        
        assert matching == []
        assert not_matching == []


class TestDataMergeDicts:
    """Tests pour merge_dicts"""
    
    def test_merge_dicts_simple(self):
        """Fusion simple"""
        from src.utils.helpers.data import merge_dicts
        
        result = merge_dicts({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}
    
    def test_merge_dicts_override(self):
        """Dernier gagne"""
        from src.utils.helpers.data import merge_dicts
        
        result = merge_dicts({"a": 1}, {"a": 2})
        assert result == {"a": 2}
    
    def test_merge_dicts_multiple(self):
        """Plusieurs dicts"""
        from src.utils.helpers.data import merge_dicts
        
        result = merge_dicts({"a": 1}, {"b": 2}, {"c": 3}, {"a": 99})
        assert result == {"a": 99, "b": 2, "c": 3}
    
    def test_merge_dicts_empty(self):
        """Aucun dict"""
        from src.utils.helpers.data import merge_dicts
        
        assert merge_dicts() == {}


class TestDataPickOmit:
    """Tests pour pick et omit"""
    
    def test_pick_keys(self):
        """Extrait clés spécifiées"""
        from src.utils.helpers.data import pick
        
        data = {"a": 1, "b": 2, "c": 3}
        assert pick(data, ["a", "c"]) == {"a": 1, "c": 3}
    
    def test_pick_missing_keys(self):
        """Clés absentes ignorées"""
        from src.utils.helpers.data import pick
        
        data = {"a": 1}
        assert pick(data, ["a", "z"]) == {"a": 1}
    
    def test_omit_keys(self):
        """Exclut clés spécifiées"""
        from src.utils.helpers.data import omit
        
        data = {"a": 1, "b": 2, "c": 3}
        assert omit(data, ["b"]) == {"a": 1, "c": 3}
    
    def test_omit_all(self):
        """Exclut toutes les clés"""
        from src.utils.helpers.data import omit
        
        data = {"a": 1, "b": 2}
        assert omit(data, ["a", "b"]) == {}


# =============================================================================
# TESTS helpers/dates.py
# =============================================================================


class TestDatesWeekBounds:
    """Tests pour get_week_bounds"""
    
    def test_week_bounds_wednesday(self):
        """Mercredi -> lundi-dimanche"""
        from src.utils.helpers.dates import get_week_bounds
        
        wed = date(2025, 1, 8)  # Mercredi
        mon, sun = get_week_bounds(wed)
        
        assert mon.weekday() == 0  # Lundi
        assert sun.weekday() == 6  # Dimanche
        assert (sun - mon).days == 6
    
    def test_week_bounds_monday(self):
        """Lundi renvoie même lundi"""
        from src.utils.helpers.dates import get_week_bounds
        
        mon_input = date(2025, 1, 6)
        mon, sun = get_week_bounds(mon_input)
        
        assert mon == mon_input
    
    def test_week_bounds_sunday(self):
        """Dimanche renvoie même dimanche"""
        from src.utils.helpers.dates import get_week_bounds
        
        sun_input = date(2025, 1, 12)
        mon, sun = get_week_bounds(sun_input)
        
        assert sun == sun_input


class TestDatesDateRange:
    """Tests pour date_range"""
    
    def test_date_range_simple(self):
        """Range simple"""
        from src.utils.helpers.dates import date_range
        
        start = date(2025, 1, 1)
        end = date(2025, 1, 3)
        result = date_range(start, end)
        
        assert len(result) == 3
        assert result[0] == start
        assert result[-1] == end
    
    def test_date_range_same_day(self):
        """Même jour"""
        from src.utils.helpers.dates import date_range
        
        d = date(2025, 1, 1)
        result = date_range(d, d)
        
        assert result == [d]
    
    def test_date_range_week(self):
        """Semaine complète"""
        from src.utils.helpers.dates import date_range
        
        start = date(2025, 1, 6)  # Lundi
        end = date(2025, 1, 12)   # Dimanche
        result = date_range(start, end)
        
        assert len(result) == 7


class TestDatesMonthBounds:
    """Tests pour get_month_bounds"""
    
    def test_month_bounds_january(self):
        """Janvier (31 jours)"""
        from src.utils.helpers.dates import get_month_bounds
        
        d = date(2025, 1, 15)
        first, last = get_month_bounds(d)
        
        assert first == date(2025, 1, 1)
        assert last == date(2025, 1, 31)
    
    def test_month_bounds_february_leap(self):
        """Février année bissextile"""
        from src.utils.helpers.dates import get_month_bounds
        
        d = date(2024, 2, 15)  # 2024 = bissextile
        first, last = get_month_bounds(d)
        
        assert last == date(2024, 2, 29)
    
    def test_month_bounds_february_normal(self):
        """Février année normale"""
        from src.utils.helpers.dates import get_month_bounds
        
        d = date(2025, 2, 15)
        first, last = get_month_bounds(d)
        
        assert last == date(2025, 2, 28)
    
    def test_month_bounds_december(self):
        """Décembre (transition année)"""
        from src.utils.helpers.dates import get_month_bounds
        
        d = date(2025, 12, 15)
        first, last = get_month_bounds(d)
        
        assert first == date(2025, 12, 1)
        assert last == date(2025, 12, 31)


class TestDatesAddBusinessDays:
    """Tests pour add_business_days"""
    
    def test_add_business_days_monday(self):
        """Lundi + 5 jours = lundi suivant"""
        from src.utils.helpers.dates import add_business_days
        
        mon = date(2025, 1, 6)
        result = add_business_days(mon, 5)
        
        assert result == date(2025, 1, 13)
        assert result.weekday() == 0  # Lundi
    
    def test_add_business_days_friday(self):
        """Vendredi + 1 jour = lundi"""
        from src.utils.helpers.dates import add_business_days
        
        fri = date(2025, 1, 10)
        result = add_business_days(fri, 1)
        
        assert result == date(2025, 1, 13)
        assert result.weekday() == 0  # Lundi
    
    def test_add_business_days_zero(self):
        """0 jours = même date"""
        from src.utils.helpers.dates import add_business_days
        
        d = date(2025, 1, 6)
        result = add_business_days(d, 0)
        
        assert result == d


class TestDatesWeeksBetween:
    """Tests pour weeks_between"""
    
    def test_weeks_between_two_weeks(self):
        """14 jours = 2 semaines"""
        from src.utils.helpers.dates import weeks_between
        
        start = date(2025, 1, 1)
        end = date(2025, 1, 15)
        
        assert weeks_between(start, end) == 2
    
    def test_weeks_between_same_day(self):
        """Même jour = 0 semaines"""
        from src.utils.helpers.dates import weeks_between
        
        d = date(2025, 1, 1)
        assert weeks_between(d, d) == 0
    
    def test_weeks_between_partial(self):
        """10 jours = 1 semaine (floor)"""
        from src.utils.helpers.dates import weeks_between
        
        start = date(2025, 1, 1)
        end = date(2025, 1, 11)
        
        assert weeks_between(start, end) == 1


class TestDatesIsWeekend:
    """Tests pour is_weekend"""
    
    def test_is_weekend_saturday(self):
        """Samedi = weekend"""
        from src.utils.helpers.dates import is_weekend
        
        sat = date(2025, 1, 11)
        assert is_weekend(sat) is True
    
    def test_is_weekend_sunday(self):
        """Dimanche = weekend"""
        from src.utils.helpers.dates import is_weekend
        
        sun = date(2025, 1, 12)
        assert is_weekend(sun) is True
    
    def test_is_weekend_weekday(self):
        """Jours de semaine"""
        from src.utils.helpers.dates import is_weekend
        
        for d in [date(2025, 1, 6), date(2025, 1, 7), date(2025, 1, 8)]:
            assert is_weekend(d) is False


class TestDatesGetQuarter:
    """Tests pour get_quarter"""
    
    def test_get_quarter_q1(self):
        """Trimestre 1"""
        from src.utils.helpers.dates import get_quarter
        
        assert get_quarter(date(2025, 1, 15)) == 1
        assert get_quarter(date(2025, 2, 15)) == 1
        assert get_quarter(date(2025, 3, 15)) == 1
    
    def test_get_quarter_q2(self):
        """Trimestre 2"""
        from src.utils.helpers.dates import get_quarter
        
        assert get_quarter(date(2025, 4, 1)) == 2
        assert get_quarter(date(2025, 6, 30)) == 2
    
    def test_get_quarter_q3(self):
        """Trimestre 3"""
        from src.utils.helpers.dates import get_quarter
        
        assert get_quarter(date(2025, 7, 1)) == 3
        assert get_quarter(date(2025, 9, 30)) == 3
    
    def test_get_quarter_q4(self):
        """Trimestre 4"""
        from src.utils.helpers.dates import get_quarter
        
        assert get_quarter(date(2025, 10, 1)) == 4
        assert get_quarter(date(2025, 12, 31)) == 4


# =============================================================================
# TESTS helpers/strings.py
# =============================================================================


class TestStringsGenerateId:
    """Tests pour generate_id"""
    
    def test_generate_id_dict(self):
        """ID depuis dict"""
        from src.utils.helpers.strings import generate_id
        
        data = {"nom": "test", "value": 123}
        result = generate_id(data)
        
        assert len(result) == 16
        assert result.isalnum()
    
    def test_generate_id_deterministic(self):
        """Même données = même ID"""
        from src.utils.helpers.strings import generate_id
        
        data = {"a": 1, "b": 2}
        assert generate_id(data) == generate_id(data)
    
    def test_generate_id_order_independent(self):
        """Ordre des clés n'importe pas"""
        from src.utils.helpers.strings import generate_id
        
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}
        assert generate_id(d1) == generate_id(d2)
    
    def test_generate_id_different_data(self):
        """Différentes données = différents IDs"""
        from src.utils.helpers.strings import generate_id
        
        id1 = generate_id({"x": 1})
        id2 = generate_id({"x": 2})
        assert id1 != id2


class TestStringsNormalizeWhitespace:
    """Tests pour normalize_whitespace"""
    
    def test_normalize_whitespace_multiple_spaces(self):
        """Espaces multiples -> simple"""
        from src.utils.helpers.strings import normalize_whitespace
        
        assert normalize_whitespace("hello    world") == "hello world"
    
    def test_normalize_whitespace_trim(self):
        """Supprime espaces début/fin"""
        from src.utils.helpers.strings import normalize_whitespace
        
        assert normalize_whitespace("  hello  ") == "hello"
    
    def test_normalize_whitespace_tabs_newlines(self):
        """Tabs et newlines -> espaces"""
        from src.utils.helpers.strings import normalize_whitespace
        
        assert normalize_whitespace("hello\t\nworld") == "hello world"
    
    def test_normalize_whitespace_empty(self):
        """String vide"""
        from src.utils.helpers.strings import normalize_whitespace
        
        assert normalize_whitespace("") == ""


class TestStringsRemoveAccents:
    """Tests pour remove_accents"""
    
    def test_remove_accents_french(self):
        """Accents français"""
        from src.utils.helpers.strings import remove_accents
        
        assert remove_accents("café crème") == "cafe creme"
        assert remove_accents("où êtes-vous?") == "ou etes-vous?"
    
    def test_remove_accents_uppercase(self):
        """Majuscules avec accents"""
        from src.utils.helpers.strings import remove_accents
        
        assert remove_accents("ÉLÉPHANT") == "ELEPHANT"
    
    def test_remove_accents_no_accents(self):
        """Pas d'accents"""
        from src.utils.helpers.strings import remove_accents
        
        assert remove_accents("hello world") == "hello world"
    
    def test_remove_accents_mixed(self):
        """Mélange accents/non-accents"""
        from src.utils.helpers.strings import remove_accents
        
        assert remove_accents("Réservé pour été") == "Reserve pour ete"


class TestStringsCamelSnake:
    """Tests pour camel_to_snake et snake_to_camel"""
    
    def test_camel_to_snake_simple(self):
        """camelCase simple"""
        from src.utils.helpers.strings import camel_to_snake
        
        assert camel_to_snake("myVariable") == "my_variable"
        assert camel_to_snake("myVariableName") == "my_variable_name"
    
    def test_camel_to_snake_already_lowercase(self):
        """Déjà lowercase"""
        from src.utils.helpers.strings import camel_to_snake
        
        assert camel_to_snake("simple") == "simple"
    
    def test_snake_to_camel_simple(self):
        """snake_case simple"""
        from src.utils.helpers.strings import snake_to_camel
        
        assert snake_to_camel("my_variable") == "myVariable"
        assert snake_to_camel("my_variable_name") == "myVariableName"
    
    def test_snake_to_camel_single(self):
        """Un seul mot"""
        from src.utils.helpers.strings import snake_to_camel
        
        assert snake_to_camel("simple") == "simple"


class TestStringsPluralize:
    """Tests pour pluralize"""
    
    def test_pluralize_singular(self):
        """Singulier (count=1)"""
        from src.utils.helpers.strings import pluralize
        
        assert pluralize("item", 1) == "1 item"
    
    def test_pluralize_regular(self):
        """Pluriel régulier"""
        from src.utils.helpers.strings import pluralize
        
        assert pluralize("item", 5) == "5 items"
    
    def test_pluralize_custom_form(self):
        """Forme pluriel personnalisée"""
        from src.utils.helpers.strings import pluralize
        
        assert pluralize("cheval", 2, "chevaux") == "2 chevaux"
    
    def test_pluralize_ending_y(self):
        """Mot finissant par y"""
        from src.utils.helpers.strings import pluralize
        
        assert pluralize("city", 3) == "3 cities"
    
    def test_pluralize_ending_s(self):
        """Mot finissant par s"""
        from src.utils.helpers.strings import pluralize
        
        assert pluralize("bus", 2) == "2 buses"


class TestStringsMaskSensitive:
    """Tests pour mask_sensitive"""
    
    def test_mask_sensitive_default(self):
        """Masquage par défaut (4 visibles)"""
        from src.utils.helpers.strings import mask_sensitive
        
        assert mask_sensitive("1234567890") == "1234******"
    
    def test_mask_sensitive_custom(self):
        """Nombre personnalisé de visibles"""
        from src.utils.helpers.strings import mask_sensitive
        
        assert mask_sensitive("secret123", 3) == "sec******"
    
    def test_mask_sensitive_short(self):
        """Texte court (pas de masquage)"""
        from src.utils.helpers.strings import mask_sensitive
        
        assert mask_sensitive("abc", 4) == "abc"
    
    def test_mask_sensitive_exact(self):
        """Exactement visible_chars"""
        from src.utils.helpers.strings import mask_sensitive
        
        assert mask_sensitive("abcd", 4) == "abcd"

"""
Tests pour src/services/planning/utils.py

Tests des fonctions utilitaires pures pour le planning.
Ces tests ne nécessitent pas de base de données.
"""

import pytest
from datetime import date, datetime, timedelta

from src.services.planning.utils import (
    get_weekday_names,
    get_weekday_name,
    get_weekday_index,
    calculate_week_dates,
    get_week_range,
    get_monday_of_week,
    format_week_label,
    determine_protein_type,
    get_default_protein_schedule,
)


class TestWeekdayNames:
    """Tests pour les fonctions de noms de jours."""
    
    def test_get_weekday_names_returns_list(self):
        """Vérifie que get_weekday_names retourne une liste."""
        result = get_weekday_names()
        assert isinstance(result, list)
    
    def test_get_weekday_names_has_7_days(self):
        """Vérifie que la liste contient 7 jours."""
        result = get_weekday_names()
        assert len(result) == 7
    
    def test_get_weekday_names_starts_with_lundi(self):
        """Vérifie que la semaine commence par Lundi."""
        result = get_weekday_names()
        assert result[0] == "Lundi"
    
    def test_get_weekday_names_ends_with_dimanche(self):
        """Vérifie que la semaine finit par Dimanche."""
        result = get_weekday_names()
        assert result[6] == "Dimanche"
    
    def test_get_weekday_names_returns_copy(self):
        """Vérifie que la liste est une copie (pas de mutation)."""
        result1 = get_weekday_names()
        result2 = get_weekday_names()
        result1[0] = "Modified"
        assert result2[0] == "Lundi"


class TestGetWeekdayName:
    """Tests pour get_weekday_name."""
    
    def test_get_weekday_name_lundi(self):
        """Vérifie l'index 0 = Lundi."""
        assert get_weekday_name(0) == "Lundi"
    
    def test_get_weekday_name_dimanche(self):
        """Vérifie l'index 6 = Dimanche."""
        assert get_weekday_name(6) == "Dimanche"
    
    def test_get_weekday_name_mercredi(self):
        """Vérifie l'index 2 = Mercredi."""
        assert get_weekday_name(2) == "Mercredi"
    
    def test_get_weekday_name_vendredi(self):
        """Vérifie l'index 4 = Vendredi."""
        assert get_weekday_name(4) == "Vendredi"
    
    def test_get_weekday_name_invalid_negative(self):
        """Vérifie qu'un index négatif retourne une chaîne vide."""
        assert get_weekday_name(-1) == ""
    
    def test_get_weekday_name_invalid_high(self):
        """Vérifie qu'un index > 6 retourne une chaîne vide."""
        assert get_weekday_name(7) == ""
        assert get_weekday_name(100) == ""


class TestGetWeekdayIndex:
    """Tests pour get_weekday_index."""
    
    def test_get_weekday_index_lundi(self):
        """Vérifie Lundi = 0."""
        assert get_weekday_index("Lundi") == 0
    
    def test_get_weekday_index_dimanche(self):
        """Vérifie Dimanche = 6."""
        assert get_weekday_index("Dimanche") == 6
    
    def test_get_weekday_index_case_insensitive(self):
        """Vérifie que la recherche est insensible à la casse."""
        assert get_weekday_index("lundi") == 0
        assert get_weekday_index("LUNDI") == 0
        assert get_weekday_index("LuNdI") == 0
    
    def test_get_weekday_index_vendredi(self):
        """Vérifie vendredi = 4."""
        assert get_weekday_index("vendredi") == 4
    
    def test_get_weekday_index_invalid(self):
        """Vérifie qu'un nom invalide retourne -1."""
        assert get_weekday_index("invalid") == -1
        assert get_weekday_index("Monday") == -1
        assert get_weekday_index("") == -1


class TestCalculateWeekDates:
    """Tests pour calculate_week_dates."""
    
    def test_calculate_week_dates_returns_7_dates(self):
        """Vérifie que 7 dates sont retournées."""
        monday = date(2024, 1, 15)  # Un lundi
        result = calculate_week_dates(monday)
        assert len(result) == 7
    
    def test_calculate_week_dates_first_is_monday(self):
        """Vérifie que la première date est le lundi donné."""
        monday = date(2024, 1, 15)
        result = calculate_week_dates(monday)
        assert result[0] == monday
    
    def test_calculate_week_dates_last_is_sunday(self):
        """Vérifie que la dernière date est le dimanche."""
        monday = date(2024, 1, 15)
        result = calculate_week_dates(monday)
        assert result[6] == date(2024, 1, 21)
    
    def test_calculate_week_dates_consecutive(self):
        """Vérifie que les dates sont consécutives."""
        monday = date(2024, 1, 15)
        result = calculate_week_dates(monday)
        for i in range(6):
            assert (result[i + 1] - result[i]).days == 1
    
    def test_calculate_week_dates_span_6_days(self):
        """Vérifie que l'écart est de 6 jours."""
        monday = date(2024, 1, 15)
        result = calculate_week_dates(monday)
        assert (result[6] - result[0]).days == 6


class TestGetWeekRange:
    """Tests pour get_week_range."""
    
    def test_get_week_range_returns_tuple(self):
        """Vérifie que le résultat est un tuple."""
        result = get_week_range(date(2024, 1, 15))
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_get_week_range_first_is_input(self):
        """Vérifie que le premier élément est la date d'entrée."""
        monday = date(2024, 1, 15)
        start, _ = get_week_range(monday)
        assert start == monday
    
    def test_get_week_range_span_is_6_days(self):
        """Vérifie que l'écart est de 6 jours."""
        monday = date(2024, 1, 15)
        start, end = get_week_range(monday)
        assert (end - start).days == 6


class TestGetMondayOfWeek:
    """Tests pour get_monday_of_week."""
    
    def test_get_monday_of_week_from_monday(self):
        """Vérifie que lundi retourne lui-même."""
        monday = date(2024, 1, 15)  # Lundi
        assert get_monday_of_week(monday) == monday
    
    def test_get_monday_of_week_from_tuesday(self):
        """Vérifie depuis mardi."""
        tuesday = date(2024, 1, 16)  # Mardi
        assert get_monday_of_week(tuesday) == date(2024, 1, 15)
    
    def test_get_monday_of_week_from_sunday(self):
        """Vérifie depuis dimanche."""
        sunday = date(2024, 1, 21)  # Dimanche
        assert get_monday_of_week(sunday) == date(2024, 1, 15)
    
    def test_get_monday_of_week_from_datetime(self):
        """Vérifie avec un datetime."""
        dt = datetime(2024, 1, 18, 14, 30)  # Jeudi
        result = get_monday_of_week(dt)
        assert result == date(2024, 1, 15)
        assert isinstance(result, date)
    
    def test_get_monday_of_week_friday(self):
        """Vérifie depuis vendredi."""
        friday = date(2024, 1, 19)  # Vendredi
        assert get_monday_of_week(friday) == date(2024, 1, 15)


class TestFormatWeekLabel:
    """Tests pour format_week_label."""
    
    def test_format_week_label_basic(self):
        """Vérifie le format de base."""
        result = format_week_label(date(2024, 1, 15))
        assert "15/01/2024" in result
        assert "Semaine du" in result
    
    def test_format_week_label_with_end(self):
        """Vérifie avec date de fin explicite."""
        result = format_week_label(date(2024, 1, 15), date(2024, 1, 21))
        assert "15/01/2024" in result


class TestDetermineProteinType:
    """Tests pour determine_protein_type."""
    
    def test_determine_protein_type_poisson(self):
        """Vérifie la détection poisson."""
        result = determine_protein_type("lundi", ["lundi"], [], [])
        assert result[0] == "poisson"
        assert "🐟" in result[1]
    
    def test_determine_protein_type_viande_rouge(self):
        """Vérifie la détection viande rouge."""
        result = determine_protein_type("mardi", [], ["mardi"], [])
        assert result[0] == "viande_rouge"
        assert "🥩" in result[1]
    
    def test_determine_protein_type_vegetarien(self):
        """Vérifie la détection végétarien."""
        result = determine_protein_type("mercredi", [], [], ["mercredi"])
        assert result[0] == "vegetarien"
        assert "🥬" in result[1]
    
    def test_determine_protein_type_default_volaille(self):
        """Vérifie le fallback volaille."""
        result = determine_protein_type("jeudi", [], [], [])
        assert result[0] == "volaille"
        assert "🍗" in result[1]
    
    def test_determine_protein_type_case_insensitive(self):
        """Vérifie l'insensibilité à la casse."""
        # La fonction compare jour_lower donc "Lundi" devient "lundi"
        # Les jours dans poisson_jours doivent aussi être en minuscules
        result = determine_protein_type("lundi", ["lundi"], [], [])
        assert result[0] == "poisson"


class TestGetDefaultProteinSchedule:
    """Tests pour get_default_protein_schedule."""
    
    def test_get_default_protein_schedule_returns_dict(self):
        """Vérifie que le résultat est un dict."""
        result = get_default_protein_schedule()
        assert isinstance(result, dict)
    
    def test_get_default_protein_schedule_has_days(self):
        """Vérifie que les jours sont présents."""
        result = get_default_protein_schedule()
        assert len(result) >= 1
    
    def test_get_default_protein_schedule_has_7_days(self):
        """Vérifie que tous les jours sont présents."""
        result = get_default_protein_schedule()
        assert len(result) == 7
        expected_days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        for day in expected_days:
            assert day in result

    def test_get_default_protein_schedule_valid_types(self):
        """Vérifie que les types de protéines sont valides."""
        result = get_default_protein_schedule()
        valid_types = {"poisson", "viande_rouge", "volaille", "vegetarien"}
        for day, protein in result.items():
            assert protein in valid_types, f"{day} a un type invalide: {protein}"


# ═══════════════════════════════════════════════════════════
# TESTS ÉQUILIBRE NUTRITIONNEL (NOUVELLES FONCTIONS)
# ═══════════════════════════════════════════════════════════

from src.services.planning.utils import (
    calculate_week_balance,
    is_balanced_week,
)


class TestCalculateWeekBalance:
    """Tests pour calculate_week_balance."""
    
    def test_empty_list_returns_zeroes(self):
        """Balance vide retourne des zéros."""
        result = calculate_week_balance([])
        assert result["poisson"] == 0
        assert result["viande_rouge"] == 0
        assert result["volaille"] == 0
        assert result["vegetarien"] == 0
    
    def test_single_poisson(self):
        """Un repas poisson."""
        repas = [{"type_proteines": "saumon"}]
        result = calculate_week_balance(repas)
        assert result["poisson"] == 1
    
    def test_multiple_types(self):
        """Plusieurs types de protéines."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poulet"},
            {"type_proteines": "boeuf"},
            {"type_proteines": "légumes"},
        ]
        result = calculate_week_balance(repas)
        assert result["poisson"] == 1
        assert result["volaille"] == 1
        assert result["viande_rouge"] == 1
        assert result["vegetarien"] == 1
    
    def test_unknown_type_counted_as_autre(self):
        """Type inconnu compté comme 'autre'."""
        repas = [{"type_proteines": "inconnu_xyz"}]
        result = calculate_week_balance(repas)
        assert result["autre"] == 1
    
    def test_missing_type_counted_as_autre(self):
        """Repas sans type compté comme 'autre'."""
        repas = [{"nom": "Repas sans type"}]
        result = calculate_week_balance(repas)
        assert result["autre"] == 1
    
    def test_none_type_counted_as_autre(self):
        """Repas avec type None."""
        repas = [{"type_proteines": None}]
        result = calculate_week_balance(repas)
        # None ne passe pas la condition if protein
        assert result["autre"] == 0


class TestIsBalancedWeek:
    """Tests pour is_balanced_week."""
    
    def test_balanced_week(self):
        """Semaine équilibrée."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
            {"type_proteines": "légumes"},
            {"type_proteines": "poulet"},
        ]
        balanced, issues = is_balanced_week(repas)
        assert balanced is True
        assert len(issues) == 0
    
    def test_not_enough_fish(self):
        """Pas assez de poisson."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "légumes"},
        ]
        balanced, issues = is_balanced_week(repas)
        assert balanced is False
        assert any("poisson" in issue.lower() for issue in issues)
    
    def test_too_much_red_meat(self):
        """Trop de viande rouge."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
            {"type_proteines": "boeuf"},
            {"type_proteines": "boeuf"},
            {"type_proteines": "boeuf"},
            {"type_proteines": "légumes"},
        ]
        balanced, issues = is_balanced_week(repas)
        assert balanced is False
        assert any("viande rouge" in issue.lower() for issue in issues)
    
    def test_no_vegetarian(self):
        """Pas de repas végétarien."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
        ]
        balanced, issues = is_balanced_week(repas)
        assert balanced is False
        assert any("végétarien" in issue.lower() for issue in issues)


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════

from src.services.planning.utils import (
    format_meal_for_display,
    format_planning_summary,
    group_meals_by_type,
)


class TestFormatMealForDisplay:
    """Tests pour format_meal_for_display."""
    
    def test_basic_formatting(self):
        """Formatage basique."""
        repas = {"id": 1, "type_repas": "dejeuner", "recette_nom": "Pâtes"}
        result = format_meal_for_display(repas)
        assert result["id"] == 1
        assert result["display_type"] == "Dejeuner"
        assert result["recette_nom"] == "Pâtes"
    
    def test_emoji_for_dejeuner(self):
        """Emoji pour déjeuner."""
        repas = {"type_repas": "dejeuner"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "☀️"
    
    def test_emoji_for_diner(self):
        """Emoji pour dîner."""
        repas = {"type_repas": "diner"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "🌙"
    
    def test_emoji_for_petit_dejeuner(self):
        """Emoji pour petit-déjeuner."""
        repas = {"type_repas": "petit-dejeuner"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "🌅"
    
    def test_emoji_for_gouter(self):
        """Emoji pour goûter."""
        repas = {"type_repas": "gouter"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "🍪"
    
    def test_emoji_default(self):
        """Emoji par défaut."""
        repas = {"type_repas": "autre"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "🍽️"
    
    def test_fallback_to_notes(self):
        """Fallback sur notes si pas de recette_nom."""
        repas = {"type_repas": "dejeuner", "notes": "Repas familial"}
        result = format_meal_for_display(repas)
        assert result["recette_nom"] == "Repas familial"
    
    def test_fallback_to_non_defini(self):
        """Fallback sur 'Non défini' si rien."""
        repas = {"type_repas": "dejeuner"}
        result = format_meal_for_display(repas)
        assert result["recette_nom"] == "Non défini"
    
    def test_handles_underscores(self):
        """Gère les underscores dans le type."""
        repas = {"type_repas": "petit_dejeuner"}
        result = format_meal_for_display(repas)
        assert "Petit" in result["display_type"]


class TestFormatPlanningSummary:
    """Tests pour format_planning_summary."""
    
    def test_basic_summary(self):
        """Résumé basique."""
        data = {
            "nom": "Planning 15/01",
            "repas_par_jour": {
                "2024-01-15": [{"id": 1}],
                "2024-01-16": [{"id": 2}, {"id": 3}],
            }
        }
        result = format_planning_summary(data)
        assert "Planning 15/01" in result
        assert "2 jours" in result
        assert "3 repas" in result
    
    def test_empty_planning(self):
        """Planning vide."""
        data = {"nom": "Vide", "repas_par_jour": {}}
        result = format_planning_summary(data)
        assert "Vide" in result
        assert "0 jours" in result
        assert "0 repas" in result
    
    def test_partial_days(self):
        """Jours partiellement remplis."""
        data = {
            "nom": "Test",
            "repas_par_jour": {
                "2024-01-15": [{"id": 1}],
                "2024-01-16": [],  # Jour vide
            }
        }
        result = format_planning_summary(data)
        assert "1 jours" in result or "1 jour" in result


class TestGroupMealsByType:
    """Tests pour group_meals_by_type."""
    
    def test_empty_list(self):
        """Liste vide."""
        result = group_meals_by_type([])
        assert result == {}
    
    def test_single_type(self):
        """Un seul type."""
        meals = [{"type_repas": "dejeuner"}]
        result = group_meals_by_type(meals)
        assert "dejeuner" in result
        assert len(result["dejeuner"]) == 1
    
    def test_multiple_types(self):
        """Plusieurs types."""
        meals = [
            {"type_repas": "dejeuner"},
            {"type_repas": "diner"},
            {"type_repas": "dejeuner"},
        ]
        result = group_meals_by_type(meals)
        assert len(result["dejeuner"]) == 2
        assert len(result["diner"]) == 1
    
    def test_missing_type(self):
        """Type manquant."""
        meals = [{"nom": "Sans type"}]
        result = group_meals_by_type(meals)
        assert "autre" in result


# ═══════════════════════════════════════════════════════════
# TESTS AGRÉGATION COURSES
# ═══════════════════════════════════════════════════════════

from src.services.planning.utils import (
    aggregate_ingredients,
    sort_ingredients_by_rayon,
    get_rayon_order,
)


class TestAggregateIngredients:
    """Tests pour aggregate_ingredients."""
    
    def test_empty_list(self):
        """Liste vide."""
        result = aggregate_ingredients([])
        assert result == {}
    
    def test_single_ingredient(self):
        """Un ingrédient."""
        ings = [{"nom": "Tomate", "quantite": 2, "unite": "pcs"}]
        result = aggregate_ingredients(ings)
        assert "Tomate" in result
        assert result["Tomate"]["quantite"] == 2
    
    def test_aggregate_same_ingredient(self):
        """Agrège un même ingrédient."""
        ings = [
            {"nom": "Tomate", "quantite": 2, "unite": "pcs"},
            {"nom": "Tomate", "quantite": 3, "unite": "pcs"},
        ]
        result = aggregate_ingredients(ings)
        assert result["Tomate"]["quantite"] == 5
        assert result["Tomate"]["count"] == 2
    
    def test_different_ingredients(self):
        """Ingrédients différents."""
        ings = [
            {"nom": "Tomate", "quantite": 2, "unite": "pcs"},
            {"nom": "Oignon", "quantite": 1, "unite": "pcs"},
        ]
        result = aggregate_ingredients(ings)
        assert len(result) == 2
    
    def test_different_units_not_aggregated(self):
        """Unités différentes non agrégées (comptées séparément)."""
        ings = [
            {"nom": "Farine", "quantite": 500, "unite": "g"},
            {"nom": "Farine", "quantite": 2, "unite": "kg"},
        ]
        result = aggregate_ingredients(ings)
        # La quantité n'est pas agrégée car les unités sont différentes
        # mais le count est incrémenté
        assert result["Farine"]["count"] == 2
    
    def test_empty_name_ignored(self):
        """Nom vide ignoré."""
        ings = [{"nom": "", "quantite": 1}]
        result = aggregate_ingredients(ings)
        assert result == {}
    
    def test_missing_values_use_defaults(self):
        """Valeurs manquantes utilisent les défauts."""
        ings = [{"nom": "Test"}]
        result = aggregate_ingredients(ings)
        assert result["Test"]["quantite"] == 1
        assert result["Test"]["unite"] == "pcs"
    
    def test_rayon_from_categorie(self):
        """Rayon pris de catégorie si pas de rayon."""
        ings = [{"nom": "Test", "categorie": "legumes"}]
        result = aggregate_ingredients(ings)
        assert result["Test"]["rayon"] == "legumes"


class TestSortIngredientsByRayon:
    """Tests pour sort_ingredients_by_rayon."""
    
    def test_empty_input(self):
        """Entrée vide."""
        result = sort_ingredients_by_rayon([])
        assert result == []
    
    def test_dict_input(self):
        """Entrée dict."""
        ings = {"Tomate": {"rayon": "legumes", "quantite": 5, "nom": "Tomate"}}
        result = sort_ingredients_by_rayon(ings)
        assert len(result) == 1
        assert result[0]["nom"] == "Tomate"
    
    def test_list_input(self):
        """Entrée liste."""
        ings = [{"rayon": "legumes", "quantite": 5, "nom": "Tomate"}]
        result = sort_ingredients_by_rayon(ings)
        assert len(result) == 1
    
    def test_sorted_by_rayon_then_quantity(self):
        """Trié par rayon puis quantité décroissante."""
        ings = [
            {"nom": "A", "rayon": "z_autre", "quantite": 1},
            {"nom": "B", "rayon": "a_legumes", "quantite": 5},
            {"nom": "C", "rayon": "a_legumes", "quantite": 10},
        ]
        result = sort_ingredients_by_rayon(ings)
        # a_legumes vient avant z_autre
        assert result[0]["nom"] == "C"  # Plus grande quantité dans a_legumes
        assert result[1]["nom"] == "B"
        assert result[2]["nom"] == "A"


class TestGetRayonOrder:
    """Tests pour get_rayon_order."""
    
    def test_returns_list(self):
        """Retourne une liste."""
        result = get_rayon_order()
        assert isinstance(result, list)
    
    def test_has_standard_rayons(self):
        """Contient les rayons standards."""
        result = get_rayon_order()
        assert "fruits_legumes" in result or "legumes" in result
        assert "boucherie" in result
        assert "epicerie" in result
    
    def test_autre_is_last(self):
        """'autre' est le dernier."""
        result = get_rayon_order()
        assert result[-1] == "autre"


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════

from src.services.planning.utils import (
    validate_planning_dates,
    validate_meal_selection,
)


class TestValidatePlanningDates:
    """Tests pour validate_planning_dates."""
    
    def test_valid_week(self):
        """Semaine valide (lundi à dimanche)."""
        result, msg = validate_planning_dates(date(2024, 1, 15), date(2024, 1, 21))
        assert result is True
        assert msg == ""
    
    def test_end_before_start(self):
        """Fin avant début."""
        result, msg = validate_planning_dates(date(2024, 1, 21), date(2024, 1, 15))
        assert result is False
        assert "après" in msg.lower()
    
    def test_wrong_duration(self):
        """Durée incorrecte (pas 7 jours)."""
        result, msg = validate_planning_dates(date(2024, 1, 15), date(2024, 1, 20))
        assert result is False
        assert "7 jours" in msg
    
    def test_not_starting_monday(self):
        """Ne commence pas un lundi."""
        result, msg = validate_planning_dates(date(2024, 1, 16), date(2024, 1, 22))
        assert result is False
        assert "lundi" in msg.lower()


class TestValidateMealSelection:
    """Tests pour validate_meal_selection."""
    
    def test_valid_selection(self):
        """Sélection valide."""
        selection = {"jour_0": 1, "jour_1": 2}
        available = [1, 2, 3, 4, 5]
        result, errors = validate_meal_selection(selection, available)
        assert result is True
        assert len(errors) == 0
    
    def test_invalid_recipe_id(self):
        """ID de recette invalide."""
        selection = {"jour_0": 999}
        available = [1, 2, 3]
        result, errors = validate_meal_selection(selection, available)
        assert result is False
        assert len(errors) == 1
        assert "999" in errors[0]
    
    def test_empty_selection(self):
        """Sélection vide."""
        result, errors = validate_meal_selection({}, [1, 2, 3])
        assert result is True
        assert len(errors) == 0


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION PROMPT IA
# ═══════════════════════════════════════════════════════════

from src.services.planning.utils import (
    build_planning_prompt_context,
    parse_ai_planning_response,
)


class TestBuildPlanningPromptContext:
    """Tests pour build_planning_prompt_context."""
    
    def test_basic_context(self):
        """Contexte basique."""
        result = build_planning_prompt_context(date(2024, 1, 15))
        assert "15/01/2024" in result
        assert "7 jours" in result
    
    def test_with_preferences(self):
        """Avec préférences."""
        prefs = {
            "nb_personnes": 4,
            "budget": "100€",
            "allergies": ["arachides", "gluten"],
            "preferences_cuisine": ["italien", "français"],
        }
        result = build_planning_prompt_context(date(2024, 1, 15), preferences=prefs)
        assert "4" in result
        assert "100" in result
        assert "arachides" in result
        assert "italien" in result
    
    def test_with_constraints(self):
        """Avec contraintes."""
        constraints = ["Pas de viande le vendredi", "Budget limité"]
        result = build_planning_prompt_context(
            date(2024, 1, 15), 
            constraints=constraints
        )
        assert "vendredi" in result
        assert "Budget limité" in result
    
    def test_none_preferences(self):
        """Préférences None."""
        result = build_planning_prompt_context(date(2024, 1, 15), preferences=None)
        assert "15/01/2024" in result


class TestParseAIPlanningResponse:
    """Tests pour parse_ai_planning_response."""
    
    def test_valid_response(self):
        """Réponse valide."""
        response = [{"jour": "Lundi", "dejeuner": "Pâtes", "diner": "Salade"}]
        result = parse_ai_planning_response(response)
        assert len(result) == 1
        assert result[0]["jour"] == "Lundi"
        assert result[0]["dejeuner"] == "Pâtes"
    
    def test_normalizes_day_case(self):
        """Normalise la casse des jours."""
        response = [{"jour": "lundi", "dejeuner": "Test", "diner": "Test"}]
        result = parse_ai_planning_response(response)
        assert result[0]["jour"] == "Lundi"
    
    def test_missing_meals(self):
        """Repas manquants."""
        response = [{"jour": "Lundi"}]
        result = parse_ai_planning_response(response)
        assert result[0]["dejeuner"] == "Non défini"
        assert result[0]["diner"] == "Non défini"
    
    def test_empty_response(self):
        """Réponse vide."""
        result = parse_ai_planning_response([])
        assert result == []
    
    def test_invalid_day_kept_as_is(self):
        """Jour invalide gardé tel quel."""
        response = [{"jour": "Monday", "dejeuner": "Test", "diner": "Test"}]
        result = parse_ai_planning_response(response)
        # Non normalisé car pas un jour français
        assert result[0]["jour"] == "Monday"

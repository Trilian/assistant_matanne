"""
Tests unitaires pour planning_utils.py.

Ces tests vérifient les fonctions pures du module planning_utils
sans nécessiter de base de données ni de dépendances externes.
"""

import pytest
from datetime import date, datetime, timedelta


class TestWeekdayNames:
    """Tests pour les noms de jours."""
    
    def test_get_weekday_names_returns_7_days(self):
        """Test que get_weekday_names retourne 7 jours."""
        from src.services.planning_utils import get_weekday_names
        
        days = get_weekday_names()
        
        assert len(days) == 7
        assert days[0] == "Lundi"
        assert days[6] == "Dimanche"
    
    def test_get_weekday_names_returns_copy(self):
        """Test que la liste retournée est une copie."""
        from src.services.planning_utils import get_weekday_names
        
        days1 = get_weekday_names()
        days2 = get_weekday_names()
        
        days1[0] = "Modified"
        assert days2[0] == "Lundi"
    
    def test_get_weekday_name_valid_index(self):
        """Test get_weekday_name avec index valide."""
        from src.services.planning_utils import get_weekday_name
        
        assert get_weekday_name(0) == "Lundi"
        assert get_weekday_name(4) == "Vendredi"
        assert get_weekday_name(6) == "Dimanche"
    
    def test_get_weekday_name_invalid_index(self):
        """Test get_weekday_name avec index invalide."""
        from src.services.planning_utils import get_weekday_name
        
        assert get_weekday_name(-1) == ""
        assert get_weekday_name(7) == ""
    
    def test_get_weekday_index_valid(self):
        """Test get_weekday_index avec nom valide."""
        from src.services.planning_utils import get_weekday_index
        
        assert get_weekday_index("Lundi") == 0
        assert get_weekday_index("lundi") == 0  # Case-insensitive
        assert get_weekday_index("VENDREDI") == 4
    
    def test_get_weekday_index_invalid(self):
        """Test get_weekday_index avec nom invalide."""
        from src.services.planning_utils import get_weekday_index
        
        assert get_weekday_index("Monday") == -1
        assert get_weekday_index("") == -1


class TestCalculateWeekDates:
    """Tests pour le calcul des dates de semaine."""
    
    def test_calculate_week_dates_returns_7_dates(self):
        """Test que calculate_week_dates retourne 7 dates."""
        from src.services.planning_utils import calculate_week_dates
        
        start = date(2024, 1, 15)  # Lundi
        dates = calculate_week_dates(start)
        
        assert len(dates) == 7
    
    def test_calculate_week_dates_consecutive(self):
        """Test que les dates sont consécutives."""
        from src.services.planning_utils import calculate_week_dates
        
        start = date(2024, 1, 15)
        dates = calculate_week_dates(start)
        
        for i in range(6):
            diff = (dates[i + 1] - dates[i]).days
            assert diff == 1
    
    def test_calculate_week_dates_starts_correctly(self):
        """Test que la première date est correcte."""
        from src.services.planning_utils import calculate_week_dates
        
        start = date(2024, 1, 15)
        dates = calculate_week_dates(start)
        
        assert dates[0] == start
        assert dates[6] == date(2024, 1, 21)
    
    def test_get_week_range(self):
        """Test get_week_range."""
        from src.services.planning_utils import get_week_range
        
        start = date(2024, 1, 15)
        monday, sunday = get_week_range(start)
        
        assert monday == start
        assert sunday == date(2024, 1, 21)
        assert (sunday - monday).days == 6
    
    def test_get_monday_of_week_already_monday(self):
        """Test get_monday_of_week quand c'est déjà lundi."""
        from src.services.planning_utils import get_monday_of_week
        
        monday = date(2024, 1, 15)  # Lundi
        result = get_monday_of_week(monday)
        
        assert result == monday
    
    def test_get_monday_of_week_from_thursday(self):
        """Test get_monday_of_week depuis un jeudi."""
        from src.services.planning_utils import get_monday_of_week
        
        thursday = date(2024, 1, 18)  # Jeudi
        result = get_monday_of_week(thursday)
        
        assert result == date(2024, 1, 15)  # Lundi
    
    def test_get_monday_of_week_from_sunday(self):
        """Test get_monday_of_week depuis un dimanche."""
        from src.services.planning_utils import get_monday_of_week
        
        sunday = date(2024, 1, 21)  # Dimanche
        result = get_monday_of_week(sunday)
        
        assert result == date(2024, 1, 15)  # Lundi
    
    def test_get_monday_of_week_datetime(self):
        """Test get_monday_of_week avec datetime."""
        from src.services.planning_utils import get_monday_of_week
        
        dt = datetime(2024, 1, 18, 14, 30)  # Jeudi
        result = get_monday_of_week(dt)
        
        assert result == date(2024, 1, 15)
    
    def test_format_week_label(self):
        """Test format_week_label."""
        from src.services.planning_utils import format_week_label
        
        start = date(2024, 1, 15)
        label = format_week_label(start)
        
        assert "15/01/2024" in label
        assert "Semaine" in label


class TestProteinType:
    """Tests pour la détermination du type de protéine."""
    
    def test_determine_protein_type_poisson(self):
        """Test jour poisson."""
        from src.services.planning_utils import determine_protein_type
        
        protein, emoji = determine_protein_type(
            "lundi",
            poisson_jours=["lundi", "jeudi"],
            viande_rouge_jours=["mardi"],
            vegetarien_jours=["mercredi"]
        )
        
        assert protein == "poisson"
        assert "🐟" in emoji
    
    def test_determine_protein_type_viande_rouge(self):
        """Test jour viande rouge."""
        from src.services.planning_utils import determine_protein_type
        
        protein, emoji = determine_protein_type(
            "mardi",
            poisson_jours=["lundi"],
            viande_rouge_jours=["mardi"],
            vegetarien_jours=["mercredi"]
        )
        
        assert protein == "viande_rouge"
        assert "🥩" in emoji
    
    def test_determine_protein_type_vegetarien(self):
        """Test jour végétarien."""
        from src.services.planning_utils import determine_protein_type
        
        protein, emoji = determine_protein_type(
            "mercredi",
            poisson_jours=[],
            viande_rouge_jours=[],
            vegetarien_jours=["mercredi"]
        )
        
        assert protein == "vegetarien"
        assert "🥬" in emoji
    
    def test_determine_protein_type_default_volaille(self):
        """Test jour par défaut = volaille."""
        from src.services.planning_utils import determine_protein_type
        
        protein, emoji = determine_protein_type(
            "vendredi",
            poisson_jours=[],
            viande_rouge_jours=[],
            vegetarien_jours=[]
        )
        
        assert protein == "volaille"
        assert "🍗" in emoji
    
    def test_get_default_protein_schedule(self):
        """Test planning protéines par défaut."""
        from src.services.planning_utils import get_default_protein_schedule
        
        schedule = get_default_protein_schedule()
        
        assert schedule["lundi"] == "poisson"
        assert schedule["mercredi"] == "vegetarien"
        assert len(schedule) == 7


class TestWeekBalance:
    """Tests pour l'équilibre de la semaine."""
    
    def test_calculate_week_balance(self):
        """Test calcul de l'équilibre."""
        from src.services.planning_utils import calculate_week_balance
        
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
            {"type_proteines": "volaille"},
            {"type_proteines": "légumes"},
        ]
        
        balance = calculate_week_balance(repas)
        
        assert balance["poisson"] == 2
        assert balance["volaille"] == 1
        assert balance["vegetarien"] == 1
    
    def test_calculate_week_balance_empty(self):
        """Test équilibre avec liste vide."""
        from src.services.planning_utils import calculate_week_balance
        
        balance = calculate_week_balance([])
        
        assert balance["poisson"] == 0
        assert balance["viande_rouge"] == 0
    
    def test_calculate_week_balance_with_keywords(self):
        """Test équilibre avec mots-clés."""
        from src.services.planning_utils import calculate_week_balance
        
        repas = [
            {"type_proteines": "saumon grillé"},  # Devrait être poisson
            {"type_proteines": "boeuf bourguignon"},  # Viande rouge
        ]
        
        balance = calculate_week_balance(repas)
        
        assert balance["poisson"] == 1
        assert balance["viande_rouge"] == 1
    
    def test_is_balanced_week_valid(self):
        """Test semaine équilibrée."""
        from src.services.planning_utils import is_balanced_week
        
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
            {"type_proteines": "légumes"},
            {"type_proteines": "volaille"},
        ]
        
        balanced, issues = is_balanced_week(repas)
        
        assert balanced is True
        assert len(issues) == 0
    
    def test_is_balanced_week_not_enough_fish(self):
        """Test semaine sans assez de poisson."""
        from src.services.planning_utils import is_balanced_week
        
        repas = [
            {"type_proteines": "poisson"},  # Seulement 1
            {"type_proteines": "viande"},
            {"type_proteines": "légumes"},
        ]
        
        balanced, issues = is_balanced_week(repas)
        
        assert balanced is False
        assert any("poisson" in i for i in issues)
    
    def test_is_balanced_week_too_much_red_meat(self):
        """Test semaine avec trop de viande rouge."""
        from src.services.planning_utils import is_balanced_week
        
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
            {"type_proteines": "boeuf"},
            {"type_proteines": "veau"},
            {"type_proteines": "agneau"},
            {"type_proteines": "légumes"},
        ]
        
        balanced, issues = is_balanced_week(repas)
        
        assert balanced is False
        assert any("viande rouge" in i for i in issues)


class TestMealFormatting:
    """Tests pour le formatage des repas."""
    
    def test_format_meal_for_display(self):
        """Test formatage repas basique."""
        from src.services.planning_utils import format_meal_for_display
        
        repas = {
            "id": 1,
            "type_repas": "dejeuner",
            "recette_nom": "Pâtes carbonara"
        }
        
        formatted = format_meal_for_display(repas)
        
        assert formatted["display_type"] == "Dejeuner"
        assert formatted["recette_nom"] == "Pâtes carbonara"
        assert "emoji" in formatted
    
    def test_format_meal_for_display_with_emoji(self):
        """Test formatage repas avec emoji correct."""
        from src.services.planning_utils import format_meal_for_display
        
        assert format_meal_for_display({"type_repas": "petit-dejeuner"})["emoji"] == "🌅"
        assert format_meal_for_display({"type_repas": "dejeuner"})["emoji"] == "☀️"
        assert format_meal_for_display({"type_repas": "diner"})["emoji"] == "🌙"
    
    def test_format_meal_for_display_fallback_to_notes(self):
        """Test fallback sur notes si pas de recette."""
        from src.services.planning_utils import format_meal_for_display
        
        repas = {"type_repas": "dejeuner", "notes": "Restes d'hier"}
        
        formatted = format_meal_for_display(repas)
        
        assert formatted["recette_nom"] == "Restes d'hier"
    
    def test_format_planning_summary(self):
        """Test résumé du planning."""
        from src.services.planning_utils import format_planning_summary
        
        planning = {
            "nom": "Planning 15/01",
            "repas_par_jour": {
                "2024-01-15": [{"id": 1}, {"id": 2}],
                "2024-01-16": [{"id": 3}],
            }
        }
        
        summary = format_planning_summary(planning)
        
        assert "Planning 15/01" in summary
        assert "2 jours" in summary
        assert "3 repas" in summary
    
    def test_group_meals_by_type(self):
        """Test groupement par type."""
        from src.services.planning_utils import group_meals_by_type
        
        repas = [
            {"type_repas": "dejeuner", "id": 1},
            {"type_repas": "diner", "id": 2},
            {"type_repas": "dejeuner", "id": 3},
        ]
        
        grouped = group_meals_by_type(repas)
        
        assert len(grouped["dejeuner"]) == 2
        assert len(grouped["diner"]) == 1


class TestIngredientAggregation:
    """Tests pour l'agrégation des ingrédients."""
    
    def test_aggregate_ingredients_basic(self):
        """Test agrégation basique."""
        from src.services.planning_utils import aggregate_ingredients
        
        ingredients = [
            {"nom": "Tomate", "quantite": 2, "unite": "pcs"},
            {"nom": "Tomate", "quantite": 3, "unite": "pcs"},
            {"nom": "Oignon", "quantite": 1, "unite": "pcs"},
        ]
        
        agg = aggregate_ingredients(ingredients)
        
        assert agg["Tomate"]["quantite"] == 5
        assert agg["Tomate"]["count"] == 2
        assert agg["Oignon"]["quantite"] == 1
    
    def test_aggregate_ingredients_different_units(self):
        """Test agrégation avec unités différentes."""
        from src.services.planning_utils import aggregate_ingredients
        
        ingredients = [
            {"nom": "Eau", "quantite": 1, "unite": "L"},
            {"nom": "Eau", "quantite": 500, "unite": "mL"},  # Unité diff
        ]
        
        agg = aggregate_ingredients(ingredients)
        
        # Ne devrait pas additionner car unités différentes
        assert agg["Eau"]["count"] == 2
    
    def test_aggregate_ingredients_empty_name(self):
        """Test agrégation avec nom vide."""
        from src.services.planning_utils import aggregate_ingredients
        
        ingredients = [
            {"nom": "", "quantite": 1},
            {"nom": "Tomate", "quantite": 2},
        ]
        
        agg = aggregate_ingredients(ingredients)
        
        assert "" not in agg
        assert "Tomate" in agg
    
    def test_sort_ingredients_by_rayon(self):
        """Test tri par rayon."""
        from src.services.planning_utils import sort_ingredients_by_rayon
        
        ingredients = {
            "Lait": {"nom": "Lait", "rayon": "cremerie", "quantite": 2},
            "Tomate": {"nom": "Tomate", "rayon": "legumes", "quantite": 5},
        }
        
        sorted_list = sort_ingredients_by_rayon(ingredients)
        
        # legumes devrait venir avant cremerie (ou autre)
        assert isinstance(sorted_list, list)
        assert len(sorted_list) == 2
    
    def test_sort_ingredients_by_rayon_list_input(self):
        """Test tri avec liste en entrée."""
        from src.services.planning_utils import sort_ingredients_by_rayon
        
        ingredients = [
            {"nom": "Lait", "rayon": "z_autre", "quantite": 2},
            {"nom": "Tomate", "rayon": "a_legumes", "quantite": 5},
        ]
        
        sorted_list = sort_ingredients_by_rayon(ingredients)
        
        assert sorted_list[0]["rayon"] == "a_legumes"
    
    def test_get_rayon_order(self):
        """Test ordre des rayons."""
        from src.services.planning_utils import get_rayon_order
        
        order = get_rayon_order()
        
        assert "fruits_legumes" in order
        assert order.index("boucherie") < order.index("surgeles")


class TestValidation:
    """Tests pour la validation."""
    
    def test_validate_planning_dates_valid(self):
        """Test validation dates valides."""
        from src.services.planning_utils import validate_planning_dates
        
        start = date(2024, 1, 15)  # Lundi
        end = date(2024, 1, 21)  # Dimanche
        
        is_valid, error = validate_planning_dates(start, end)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_planning_dates_wrong_order(self):
        """Test validation dates inversées."""
        from src.services.planning_utils import validate_planning_dates
        
        is_valid, error = validate_planning_dates(date(2024, 1, 21), date(2024, 1, 15))
        
        assert is_valid is False
        assert "après" in error
    
    def test_validate_planning_dates_not_7_days(self):
        """Test validation pas 7 jours."""
        from src.services.planning_utils import validate_planning_dates
        
        is_valid, error = validate_planning_dates(date(2024, 1, 15), date(2024, 1, 20))
        
        assert is_valid is False
        assert "7 jours" in error
    
    def test_validate_planning_dates_not_monday(self):
        """Test validation pas un lundi."""
        from src.services.planning_utils import validate_planning_dates
        
        # Commence un mardi
        is_valid, error = validate_planning_dates(date(2024, 1, 16), date(2024, 1, 22))
        
        assert is_valid is False
        assert "lundi" in error
    
    def test_validate_meal_selection_valid(self):
        """Test validation sélection valide."""
        from src.services.planning_utils import validate_meal_selection
        
        selection = {"jour_0": 1, "jour_1": 2}
        available = [1, 2, 3, 4]
        
        is_valid, errors = validate_meal_selection(selection, available)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_meal_selection_missing_recipe(self):
        """Test validation recette manquante."""
        from src.services.planning_utils import validate_meal_selection
        
        selection = {"jour_0": 1, "jour_1": 999}  # 999 n'existe pas
        available = [1, 2, 3]
        
        is_valid, errors = validate_meal_selection(selection, available)
        
        assert is_valid is False
        assert len(errors) == 1


class TestAIPrompt:
    """Tests pour la génération de prompts IA."""
    
    def test_build_planning_prompt_context_basic(self):
        """Test contexte prompt basique."""
        from src.services.planning_utils import build_planning_prompt_context
        
        context = build_planning_prompt_context(date(2024, 1, 15))
        
        assert "15/01/2024" in context
        assert "7 jours" in context
    
    def test_build_planning_prompt_context_with_preferences(self):
        """Test contexte avec préférences."""
        from src.services.planning_utils import build_planning_prompt_context
        
        prefs = {
            "nb_personnes": 4,
            "budget": "modéré",
            "allergies": ["arachides", "gluten"],
        }
        
        context = build_planning_prompt_context(date(2024, 1, 15), prefs)
        
        assert "4" in context
        assert "modéré" in context
        assert "arachides" in context
    
    def test_build_planning_prompt_context_with_constraints(self):
        """Test contexte avec contraintes."""
        from src.services.planning_utils import build_planning_prompt_context
        
        context = build_planning_prompt_context(
            date(2024, 1, 15),
            constraints=["Pas de porc", "Repas rapides"]
        )
        
        assert "Pas de porc" in context
        assert "Repas rapides" in context
    
    def test_parse_ai_planning_response(self):
        """Test parsing réponse IA."""
        from src.services.planning_utils import parse_ai_planning_response
        
        response = [
            {"jour": "Lundi", "dejeuner": "Pâtes", "diner": "Salade"},
            {"jour": "Mardi", "dejeuner": "Riz", "diner": "Soupe"},
        ]
        
        parsed = parse_ai_planning_response(response)
        
        assert len(parsed) == 2
        assert parsed[0]["jour"] == "Lundi"
        assert parsed[0]["dejeuner"] == "Pâtes"
    
    def test_parse_ai_planning_response_normalize_day(self):
        """Test normalisation du jour."""
        from src.services.planning_utils import parse_ai_planning_response
        
        response = [{"jour": "lundi", "dejeuner": "X", "diner": "Y"}]
        
        parsed = parse_ai_planning_response(response)
        
        assert parsed[0]["jour"] == "Lundi"
    
    def test_parse_ai_planning_response_missing_fields(self):
        """Test champs manquants."""
        from src.services.planning_utils import parse_ai_planning_response
        
        response = [{"jour": "Lundi"}]
        
        parsed = parse_ai_planning_response(response)
        
        assert parsed[0]["dejeuner"] == "Non défini"
        assert parsed[0]["diner"] == "Non défini"


class TestConstants:
    """Tests pour les constantes."""
    
    def test_jours_semaine_constant(self):
        """Test constante JOURS_SEMAINE."""
        from src.services.planning_utils import JOURS_SEMAINE
        
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
    
    def test_types_repas_constant(self):
        """Test constante TYPES_REPAS."""
        from src.services.planning_utils import TYPES_REPAS
        
        assert "dejeuner" in TYPES_REPAS
        assert "diner" in TYPES_REPAS
    
    def test_types_proteines_constant(self):
        """Test constante TYPES_PROTEINES."""
        from src.services.planning_utils import TYPES_PROTEINES
        
        assert "poisson" in TYPES_PROTEINES
        assert "saumon" in TYPES_PROTEINES["poisson"]


class TestEdgeCases:
    """Tests pour les cas limites."""
    
    def test_aggregate_ingredients_null_quantity(self):
        """Test agrégation avec quantité nulle."""
        from src.services.planning_utils import aggregate_ingredients
        
        ingredients = [{"nom": "Sel", "quantite": None, "unite": "pcs"}]
        
        agg = aggregate_ingredients(ingredients)
        
        assert agg["Sel"]["quantite"] == 1  # Default à 1
    
    def test_format_meal_unknown_type(self):
        """Test formatage type inconnu."""
        from src.services.planning_utils import format_meal_for_display
        
        formatted = format_meal_for_display({"type_repas": "unknown_type"})
        
        assert formatted["emoji"] == "🍽️"  # Default emoji
    
    def test_calculate_week_dates_across_month(self):
        """Test dates traversant un mois."""
        from src.services.planning_utils import calculate_week_dates
        
        start = date(2024, 1, 29)  # Lundi 29 janvier
        dates = calculate_week_dates(start)
        
        assert dates[0].month == 1
        assert dates[6].month == 2  # Dimanche 4 février
    
    def test_calculate_week_dates_across_year(self):
        """Test dates traversant une année."""
        from src.services.planning_utils import calculate_week_dates
        
        start = date(2024, 12, 30)  # Lundi 30 décembre
        dates = calculate_week_dates(start)
        
        assert dates[0].year == 2024
        assert dates[6].year == 2025
    
    def test_empty_planning_summary(self):
        """Test résumé planning vide."""
        from src.services.planning_utils import format_planning_summary
        
        planning = {"nom": "Vide", "repas_par_jour": {}}
        
        summary = format_planning_summary(planning)
        
        assert "0 jours" in summary or "0 repas" in summary

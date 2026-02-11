"""Tests pour src/services/planning/utils.py - Fonctions utilitaires.

Couverture des fonctionnalités:
- Dates et calendrier
- Équilibre nutritionnel
- Formatage et affichage
- Agrégation des courses
- Validation
- Génération de prompt IA
"""

import pytest
from datetime import date, datetime, timedelta

from src.services.planning.utils import (
    # Dates et calendrier
    get_weekday_names,
    get_weekday_name,
    get_weekday_index,
    calculate_week_dates,
    get_week_range,
    get_monday_of_week,
    format_week_label,
    # Équilibre nutritionnel
    determine_protein_type,
    get_default_protein_schedule,
    calculate_week_balance,
    is_balanced_week,
    # Formatage
    format_meal_for_display,
    format_planning_summary,
    group_meals_by_type,
    # Courses
    aggregate_ingredients,
    sort_ingredients_by_rayon,
    get_rayon_order,
    # Validation
    validate_planning_dates,
    validate_meal_selection,
    # IA
    build_planning_prompt_context,
    parse_ai_planning_response,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def lundi_test():
    """Un lundi de test."""
    return date(2024, 1, 15)


@pytest.fixture
def sample_repas_list():
    """Liste de repas de test."""
    return [
        {"type_proteines": "poisson", "type_repas": "dejeuner"},
        {"type_proteines": "poisson", "type_repas": "diner"},
        {"type_proteines": "volaille", "type_repas": "dejeuner"},
        {"type_proteines": "viande rouge", "type_repas": "diner"},
        {"type_proteines": "légumes", "type_repas": "dejeuner"},
    ]


@pytest.fixture
def sample_ingredients():
    """Liste d'ingrédients de test."""
    return [
        {"nom": "Tomates", "quantite": 2, "unite": "pcs", "rayon": "legumes"},
        {"nom": "Tomates", "quantite": 3, "unite": "pcs", "rayon": "legumes"},
        {"nom": "Lait", "quantite": 1, "unite": "L", "rayon": "cremerie"},
        {"nom": "Pâtes", "quantite": 500, "unite": "g", "rayon": "epicerie"},
    ]


# ═══════════════════════════════════════════════════════════
# TESTS DATES ET CALENDRIER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetWeekdayNames:
    """Tests pour get_weekday_names."""

    def test_retourne_7_jours(self):
        """Retourne exactement 7 jours."""
        jours = get_weekday_names()
        assert len(jours) == 7

    def test_commence_par_lundi(self):
        """Commence par Lundi."""
        jours = get_weekday_names()
        assert jours[0] == "Lundi"

    def test_termine_par_dimanche(self):
        """Termine par Dimanche."""
        jours = get_weekday_names()
        assert jours[6] == "Dimanche"

    def test_retourne_copie(self):
        """Retourne une copie (non modifiable)."""
        jours1 = get_weekday_names()
        jours2 = get_weekday_names()
        jours1[0] = "Modifié"
        assert jours2[0] == "Lundi"

    def test_contient_tous_jours(self):
        """Contient tous les jours de la semaine."""
        jours = get_weekday_names()
        attendus = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        assert jours == attendus


@pytest.mark.unit
class TestGetWeekdayName:
    """Tests pour get_weekday_name."""

    def test_lundi(self):
        """Index 0 = Lundi."""
        assert get_weekday_name(0) == "Lundi"

    def test_mardi(self):
        """Index 1 = Mardi."""
        assert get_weekday_name(1) == "Mardi"

    def test_mercredi(self):
        """Index 2 = Mercredi."""
        assert get_weekday_name(2) == "Mercredi"

    def test_jeudi(self):
        """Index 3 = Jeudi."""
        assert get_weekday_name(3) == "Jeudi"

    def test_vendredi(self):
        """Index 4 = Vendredi."""
        assert get_weekday_name(4) == "Vendredi"

    def test_samedi(self):
        """Index 5 = Samedi."""
        assert get_weekday_name(5) == "Samedi"

    def test_dimanche(self):
        """Index 6 = Dimanche."""
        assert get_weekday_name(6) == "Dimanche"

    def test_index_invalide_negatif(self):
        """Index négatif retourne vide."""
        assert get_weekday_name(-1) == ""

    def test_index_invalide_trop_grand(self):
        """Index > 6 retourne vide."""
        assert get_weekday_name(7) == ""
        assert get_weekday_name(100) == ""


@pytest.mark.unit
class TestGetWeekdayIndex:
    """Tests pour get_weekday_index."""

    def test_lundi_minuscule(self):
        """'lundi' => 0."""
        assert get_weekday_index("lundi") == 0

    def test_lundi_majuscule(self):
        """'Lundi' => 0."""
        assert get_weekday_index("Lundi") == 0

    def test_lundi_majuscules(self):
        """'LUNDI' => 0."""
        assert get_weekday_index("LUNDI") == 0

    def test_mardi(self):
        """'mardi' => 1."""
        assert get_weekday_index("mardi") == 1

    def test_mercredi(self):
        """'mercredi' => 2."""
        assert get_weekday_index("mercredi") == 2

    def test_jeudi(self):
        """'jeudi' => 3."""
        assert get_weekday_index("jeudi") == 3

    def test_vendredi(self):
        """'vendredi' => 4."""
        assert get_weekday_index("vendredi") == 4

    def test_samedi(self):
        """'Samedi' => 5."""
        assert get_weekday_index("Samedi") == 5

    def test_dimanche(self):
        """'Dimanche' => 6."""
        assert get_weekday_index("Dimanche") == 6

    def test_jour_inconnu(self):
        """Jour inconnu => -1."""
        assert get_weekday_index("Lundredi") == -1
        assert get_weekday_index("Invalid") == -1
        assert get_weekday_index("") == -1


@pytest.mark.unit
class TestCalculateWeekDates:
    """Tests pour calculate_week_dates."""

    def test_retourne_7_dates(self, lundi_test):
        """Retourne 7 dates."""
        dates = calculate_week_dates(lundi_test)
        assert len(dates) == 7

    def test_premiere_date_est_debut(self, lundi_test):
        """Première date = semaine_debut."""
        dates = calculate_week_dates(lundi_test)
        assert dates[0] == lundi_test

    def test_derniere_date_6_jours_apres(self, lundi_test):
        """Dernière date = début + 6 jours."""
        dates = calculate_week_dates(lundi_test)
        assert dates[6] == lundi_test + timedelta(days=6)

    def test_dates_consecutives(self, lundi_test):
        """Dates sont consécutives."""
        dates = calculate_week_dates(lundi_test)
        for i in range(6):
            assert dates[i + 1] - dates[i] == timedelta(days=1)

    def test_retourne_liste(self, lundi_test):
        """Retourne une liste."""
        dates = calculate_week_dates(lundi_test)
        assert isinstance(dates, list)


@pytest.mark.unit
class TestGetWeekRange:
    """Tests pour get_week_range."""

    def test_retourne_tuple(self, lundi_test):
        """Retourne un tuple."""
        result = get_week_range(lundi_test)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_debut_fin_corrects(self, lundi_test):
        """Début et fin corrects."""
        debut, fin = get_week_range(lundi_test)
        assert debut == lundi_test
        assert fin == lundi_test + timedelta(days=6)

    def test_difference_6_jours(self, lundi_test):
        """Différence de 6 jours."""
        debut, fin = get_week_range(lundi_test)
        assert (fin - debut).days == 6


@pytest.mark.unit
class TestGetMondayOfWeek:
    """Tests pour get_monday_of_week."""

    def test_lundi_retourne_meme_date(self, lundi_test):
        """Lundi retourne la même date."""
        result = get_monday_of_week(lundi_test)
        assert result == lundi_test

    def test_mardi_retourne_lundi(self, lundi_test):
        """Mardi retourne le lundi précédent."""
        mardi = lundi_test + timedelta(days=1)
        result = get_monday_of_week(mardi)
        assert result == lundi_test

    def test_mercredi_retourne_lundi(self, lundi_test):
        """Mercredi retourne le lundi précédent."""
        mercredi = lundi_test + timedelta(days=2)
        result = get_monday_of_week(mercredi)
        assert result == lundi_test

    def test_jeudi_retourne_lundi(self, lundi_test):
        """Jeudi retourne le lundi précédent."""
        jeudi = lundi_test + timedelta(days=3)
        result = get_monday_of_week(jeudi)
        assert result == lundi_test

    def test_vendredi_retourne_lundi(self, lundi_test):
        """Vendredi retourne le lundi."""
        vendredi = lundi_test + timedelta(days=4)
        result = get_monday_of_week(vendredi)
        assert result == lundi_test

    def test_samedi_retourne_lundi(self, lundi_test):
        """Samedi retourne le lundi."""
        samedi = lundi_test + timedelta(days=5)
        result = get_monday_of_week(samedi)
        assert result == lundi_test

    def test_dimanche_retourne_lundi(self, lundi_test):
        """Dimanche retourne le lundi précédent."""
        dimanche = lundi_test + timedelta(days=6)
        result = get_monday_of_week(dimanche)
        assert result == lundi_test

    def test_accepte_datetime(self, lundi_test):
        """Accepte un datetime."""
        dt = datetime.combine(lundi_test + timedelta(days=2), datetime.min.time())
        result = get_monday_of_week(dt)
        assert result == lundi_test


@pytest.mark.unit
class TestFormatWeekLabel:
    """Tests pour format_week_label."""

    def test_format_label(self, lundi_test):
        """Formate correctement le label."""
        label = format_week_label(lundi_test)
        assert "Semaine du" in label
        assert "15/01/2024" in label

    def test_format_sans_fin(self, lundi_test):
        """Formate sans date de fin explicite."""
        label = format_week_label(lundi_test)
        assert "Semaine du" in label

    def test_format_avec_fin(self, lundi_test):
        """Formate avec date de fin."""
        fin = lundi_test + timedelta(days=6)
        label = format_week_label(lundi_test, fin)
        assert "Semaine du" in label


# ═══════════════════════════════════════════════════════════
# TESTS ÉQUILIBRE NUTRITIONNEL
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDetermineProteinType:
    """Tests pour determine_protein_type."""

    def test_jour_poisson(self):
        """Jour poisson retourne poisson."""
        type_prot, raison = determine_protein_type(
            "lundi",
            poisson_jours=["lundi", "jeudi"],
            viande_rouge_jours=[],
            vegetarien_jours=[]
        )
        assert type_prot == "poisson"
        assert "🐟" in raison

    def test_jour_viande_rouge(self):
        """Jour viande rouge."""
        type_prot, raison = determine_protein_type(
            "mardi",
            poisson_jours=[],
            viande_rouge_jours=["mardi"],
            vegetarien_jours=[]
        )
        assert type_prot == "viande_rouge"
        assert "🥩" in raison

    def test_jour_vegetarien(self):
        """Jour végétarien."""
        type_prot, raison = determine_protein_type(
            "mercredi",
            poisson_jours=[],
            viande_rouge_jours=[],
            vegetarien_jours=["mercredi"]
        )
        assert type_prot == "vegetarien"
        assert "🥬" in raison

    def test_jour_defaut_volaille(self):
        """Jour par défaut = volaille."""
        type_prot, raison = determine_protein_type(
            "samedi",
            poisson_jours=["lundi"],
            viande_rouge_jours=["mardi"],
            vegetarien_jours=["mercredi"]
        )
        assert type_prot == "volaille"
        assert "🍗" in raison

    def test_priorite_poisson(self):
        """Poisson a priorité sur les autres."""
        type_prot, raison = determine_protein_type(
            "lundi",
            poisson_jours=["lundi"],
            viande_rouge_jours=["lundi"],
            vegetarien_jours=["lundi"]
        )
        assert type_prot == "poisson"

    def test_liste_avec_majuscules(self):
        """Gère les jours avec majuscules dans les listes."""
        type_prot, raison = determine_protein_type(
            "lundi",  # jour_lower doit être en minuscules
            poisson_jours=["Lundi"],  # Mais la liste peut avoir des majuscules
            viande_rouge_jours=[],
            vegetarien_jours=[]
        )
        assert type_prot == "poisson"


@pytest.mark.unit
class TestGetDefaultProteinSchedule:
    """Tests pour get_default_protein_schedule."""

    def test_retourne_7_jours(self):
        """Retourne un planning pour 7 jours."""
        schedule = get_default_protein_schedule()
        assert len(schedule) == 7

    def test_lundi_est_poisson(self):
        """Lundi = poisson par défaut."""
        schedule = get_default_protein_schedule()
        assert schedule["lundi"] == "poisson"

    def test_mardi_est_viande_rouge(self):
        """Mardi = viande rouge par défaut."""
        schedule = get_default_protein_schedule()
        assert schedule["mardi"] == "viande_rouge"

    def test_mercredi_est_vegetarien(self):
        """Mercredi = végétarien par défaut."""
        schedule = get_default_protein_schedule()
        assert schedule["mercredi"] == "vegetarien"

    def test_jeudi_est_poisson(self):
        """Jeudi = poisson par défaut."""
        schedule = get_default_protein_schedule()
        assert schedule["jeudi"] == "poisson"

    def test_vendredi_est_volaille(self):
        """Vendredi = volaille par défaut."""
        schedule = get_default_protein_schedule()
        assert schedule["vendredi"] == "volaille"


@pytest.mark.unit
class TestCalculateWeekBalance:
    """Tests pour calculate_week_balance."""

    def test_comptage_correct(self, sample_repas_list):
        """Comptage correct des protéines."""
        balance = calculate_week_balance(sample_repas_list)
        assert balance["poisson"] == 2
        assert balance["volaille"] == 1
        assert balance["viande_rouge"] == 1
        assert balance["vegetarien"] == 1

    def test_liste_vide(self):
        """Liste vide = tout à zéro."""
        balance = calculate_week_balance([])
        assert balance["poisson"] == 0
        assert balance["volaille"] == 0
        assert balance["viande_rouge"] == 0
        assert balance["vegetarien"] == 0

    def test_type_inconnu_autre(self):
        """Type inconnu classé comme autre."""
        repas = [{"type_proteines": "martien"}]
        balance = calculate_week_balance(repas)
        assert balance["autre"] == 1


@pytest.mark.unit
class TestIsBalancedWeek:
    """Tests pour is_balanced_week."""

    def test_semaine_equilibree(self):
        """Semaine équilibrée."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
            {"type_proteines": "volaille"},
            {"type_proteines": "viande rouge"},
            {"type_proteines": "légumes"},
        ]
        balanced, issues = is_balanced_week(repas)
        assert balanced is True
        assert len(issues) == 0

    def test_pas_assez_poisson(self):
        """Pas assez de poisson signalé."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "volaille"},
            {"type_proteines": "viande rouge"},
            {"type_proteines": "légumes"},
        ]
        balanced, issues = is_balanced_week(repas)
        assert balanced is False
        assert any("poisson" in issue for issue in issues)

    def test_trop_viande_rouge(self):
        """Trop de viande rouge signalé."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
            {"type_proteines": "viande rouge"},
            {"type_proteines": "viande rouge"},
            {"type_proteines": "viande rouge"},
            {"type_proteines": "légumes"},
        ]
        balanced, issues = is_balanced_week(repas)
        assert balanced is False
        assert any("viande rouge" in issue for issue in issues)

    def test_pas_vegetarien(self):
        """Pas de végétarien signalé."""
        repas = [
            {"type_proteines": "poisson"},
            {"type_proteines": "poisson"},
            {"type_proteines": "volaille"},
        ]
        balanced, issues = is_balanced_week(repas)
        assert balanced is False
        assert any("végétarien" in issue for issue in issues)


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFormatMealForDisplay:
    """Tests pour format_meal_for_display."""

    def test_format_basique(self):
        """Formatage basique."""
        repas = {"id": 1, "type_repas": "dejeuner", "recette_nom": "Pâtes"}
        result = format_meal_for_display(repas)
        assert result["id"] == 1
        assert result["recette_nom"] == "Pâtes"
        assert "emoji" in result
        assert "display_type" in result

    def test_emoji_petit_dejeuner(self):
        """Emoji correct pour petit-déjeuner."""
        repas = {"type_repas": "petit-dejeuner"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "🌅"

    def test_emoji_dejeuner(self):
        """Emoji correct pour déjeuner."""
        repas = {"type_repas": "dejeuner"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "☀️"

    def test_emoji_gouter(self):
        """Emoji correct pour goûter."""
        repas = {"type_repas": "gouter"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "🍪"

    def test_emoji_diner(self):
        """Emoji correct pour dîner."""
        repas = {"type_repas": "diner"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "🌙"

    def test_emoji_defaut(self):
        """Emoji par défaut."""
        repas = {"type_repas": "collation"}
        result = format_meal_for_display(repas)
        assert result["emoji"] == "🍽️"

    def test_display_type_capitalise(self):
        """Display type est capitalisé."""
        repas = {"type_repas": "dejeuner"}
        result = format_meal_for_display(repas)
        assert result["display_type"] == "Dejeuner"


@pytest.mark.unit
class TestFormatPlanningSummary:
    """Tests pour format_planning_summary."""

    def test_format_summary(self):
        """Formate un résumé."""
        planning = {
            "nom": "Planning 15/01",
            "repas_par_jour": {
                "2024-01-15": [{"id": 1}, {"id": 2}],
                "2024-01-16": [],
            }
        }
        summary = format_planning_summary(planning)
        assert "Planning 15/01" in summary
        assert "1 jour" in summary
        assert "2 repas" in summary

    def test_format_sans_repas(self):
        """Formate sans repas."""
        planning = {
            "nom": "Planning vide",
            "repas_par_jour": {}
        }
        summary = format_planning_summary(planning)
        assert "Planning vide" in summary
        assert "0" in summary


@pytest.mark.unit
class TestGroupMealsByType:
    """Tests pour group_meals_by_type."""

    def test_groupe_par_type(self, sample_repas_list):
        """Groupe les repas par type."""
        grouped = group_meals_by_type(sample_repas_list)
        assert "dejeuner" in grouped
        assert "diner" in grouped
        assert len(grouped["dejeuner"]) == 3
        assert len(grouped["diner"]) == 2

    def test_liste_vide(self):
        """Gère une liste vide."""
        grouped = group_meals_by_type([])
        assert grouped == {}

    def test_type_unique(self):
        """Gère un seul type."""
        repas = [{"type_repas": "dejeuner"}, {"type_repas": "dejeuner"}]
        grouped = group_meals_by_type(repas)
        assert len(grouped) == 1
        assert grouped["dejeuner"] == repas


# ═══════════════════════════════════════════════════════════
# TESTS AGRÉGATION COURSES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAggregateIngredients:
    """Tests pour aggregate_ingredients."""

    def test_agregation_meme_ingredient(self, sample_ingredients):
        """Agrège les quantités du même ingrédient."""
        result = aggregate_ingredients(sample_ingredients)
        assert "Tomates" in result
        assert result["Tomates"]["quantite"] == 5

    def test_conserve_autres_champs(self, sample_ingredients):
        """Conserve rayon et unité."""
        result = aggregate_ingredients(sample_ingredients)
        assert result["Tomates"]["unite"] == "pcs"
        assert result["Tomates"]["rayon"] == "legumes"

    def test_compte_occurrences(self, sample_ingredients):
        """Compte les occurrences."""
        result = aggregate_ingredients(sample_ingredients)
        assert result["Tomates"]["count"] == 2
        assert result["Lait"]["count"] == 1

    def test_liste_vide(self):
        """Gère une liste vide."""
        result = aggregate_ingredients([])
        assert result == {}

    def test_ingredient_sans_nom(self):
        """Ignore les ingrédients sans nom."""
        ingredients = [{"nom": "", "quantite": 1}]
        result = aggregate_ingredients(ingredients)
        assert result == {}

    def test_quantite_defaut(self):
        """Quantité par défaut = 1."""
        ingredients = [{"nom": "Sel"}]
        result = aggregate_ingredients(ingredients)
        assert result["Sel"]["quantite"] == 1


@pytest.mark.unit
class TestSortIngredientsByRayon:
    """Tests pour sort_ingredients_by_rayon."""

    def test_tri_par_rayon(self):
        """Tri par rayon."""
        ingredients = {
            "Pâtes": {"nom": "Pâtes", "rayon": "epicerie", "quantite": 1},
            "Tomates": {"nom": "Tomates", "rayon": "legumes", "quantite": 2},
        }
        sorted_list = sort_ingredients_by_rayon(ingredients)
        # epicerie < legumes alphabétiquement
        assert sorted_list[0]["rayon"] == "epicerie"

    def test_accepte_liste(self):
        """Accepte une liste en entrée."""
        ingredients = [
            {"nom": "Pâtes", "rayon": "epicerie", "quantite": 1},
            {"nom": "Tomates", "rayon": "legumes", "quantite": 2},
        ]
        sorted_list = sort_ingredients_by_rayon(ingredients)
        assert len(sorted_list) == 2

    def test_tri_secondaire_quantite(self):
        """Tri secondaire par quantité décroissante."""
        ingredients = [
            {"nom": "A", "rayon": "epicerie", "quantite": 1},
            {"nom": "B", "rayon": "epicerie", "quantite": 5},
        ]
        sorted_list = sort_ingredients_by_rayon(ingredients)
        assert sorted_list[0]["nom"] == "B"


@pytest.mark.unit
class TestGetRayonOrder:
    """Tests pour get_rayon_order."""

    def test_retourne_liste(self):
        """Retourne une liste non vide."""
        order = get_rayon_order()
        assert isinstance(order, list)
        assert len(order) > 0

    def test_fruits_legumes_en_premier(self):
        """Fruits & légumes en premier."""
        order = get_rayon_order()
        assert "fruits_legumes" in order or "legumes" in order[:3]

    def test_contient_rayons_principaux(self):
        """Contient les rayons principaux."""
        order = get_rayon_order()
        assert "epicerie" in order
        assert "cremerie" in order
        assert "boucherie" in order


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestValidatePlanningDates:
    """Tests pour validate_planning_dates."""

    def test_dates_valides(self, lundi_test):
        """Dates valides."""
        fin = lundi_test + timedelta(days=6)
        is_valid, error = validate_planning_dates(lundi_test, fin)
        assert is_valid is True
        assert error == ""

    def test_fin_avant_debut(self, lundi_test):
        """Fin avant début invalide."""
        fin = lundi_test - timedelta(days=1)
        is_valid, error = validate_planning_dates(lundi_test, fin)
        assert is_valid is False
        assert "après" in error

    def test_pas_7_jours(self, lundi_test):
        """Pas exactement 7 jours invalide."""
        fin = lundi_test + timedelta(days=10)
        is_valid, error = validate_planning_dates(lundi_test, fin)
        assert is_valid is False
        assert "7 jours" in error

    def test_pas_un_lundi(self):
        """Début pas un lundi invalide."""
        mardi = date(2024, 1, 16)
        fin = mardi + timedelta(days=6)
        is_valid, error = validate_planning_dates(mardi, fin)
        assert is_valid is False
        assert "lundi" in error


@pytest.mark.unit
class TestValidateMealSelection:
    """Tests pour validate_meal_selection."""

    def test_selection_valide(self):
        """Sélection valide."""
        selection = {"jour_0": 1, "jour_1": 2}
        available = [1, 2, 3]
        is_valid, errors = validate_meal_selection(selection, available)
        assert is_valid is True
        assert len(errors) == 0

    def test_recette_non_disponible(self):
        """Recette non disponible signalée."""
        selection = {"jour_0": 99}
        available = [1, 2, 3]
        is_valid, errors = validate_meal_selection(selection, available)
        assert is_valid is False
        assert len(errors) >= 1
        assert "99" in errors[0]

    def test_selection_vide(self):
        """Sélection vide valide."""
        selection = {}
        available = [1, 2, 3]
        is_valid, errors = validate_meal_selection(selection, available)
        assert is_valid is True
        assert len(errors) == 0


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION PROMPT IA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBuildPlanningPromptContext:
    """Tests pour build_planning_prompt_context."""

    def test_contexte_basique(self, lundi_test):
        """Contexte basique."""
        context = build_planning_prompt_context(lundi_test)
        assert "15/01/2024" in context
        assert "7 jours" in context

    def test_avec_nb_personnes(self, lundi_test):
        """Avec nombre de personnes."""
        prefs = {"nb_personnes": 4}
        context = build_planning_prompt_context(lundi_test, preferences=prefs)
        assert "4" in context

    def test_avec_budget(self, lundi_test):
        """Avec budget."""
        prefs = {"budget": 100}
        context = build_planning_prompt_context(lundi_test, preferences=prefs)
        assert "100" in context

    def test_avec_allergies(self, lundi_test):
        """Avec allergies."""
        prefs = {"allergies": ["gluten", "lactose"]}
        context = build_planning_prompt_context(lundi_test, preferences=prefs)
        assert "gluten" in context
        assert "lactose" in context

    def test_avec_preferences_cuisine(self, lundi_test):
        """Avec préférences cuisine."""
        prefs = {"preferences_cuisine": ["italien", "asiatique"]}
        context = build_planning_prompt_context(lundi_test, preferences=prefs)
        assert "italien" in context or "asiatique" in context

    def test_avec_contraintes(self, lundi_test):
        """Avec contraintes."""
        constraints = ["Pas de poisson le vendredi"]
        context = build_planning_prompt_context(lundi_test, constraints=constraints)
        assert "poisson" in context


@pytest.mark.unit
class TestParseAiPlanningResponse:
    """Tests pour parse_ai_planning_response."""

    def test_parse_valide(self):
        """Parse réponse valide."""
        response = [
            {"jour": "Lundi", "dejeuner": "Pâtes", "diner": "Salade"},
            {"jour": "Mardi", "dejeuner": "Riz", "diner": "Soupe"},
        ]
        parsed = parse_ai_planning_response(response)
        assert len(parsed) == 2
        assert parsed[0]["jour"] == "Lundi"
        assert parsed[0]["dejeuner"] == "Pâtes"

    def test_normalise_jour_minuscule(self):
        """Normalise les jours en minuscules."""
        response = [{"jour": "lundi", "dejeuner": "Test", "diner": "Test"}]
        parsed = parse_ai_planning_response(response)
        assert parsed[0]["jour"] == "Lundi"

    def test_valeur_defaut_non_defini(self):
        """Valeur par défaut pour repas manquants."""
        response = [{"jour": "Lundi"}]
        parsed = parse_ai_planning_response(response)
        assert parsed[0]["dejeuner"] == "Non défini"
        assert parsed[0]["diner"] == "Non défini"

    def test_reponse_vide(self):
        """Gère une réponse vide."""
        parsed = parse_ai_planning_response([])
        assert parsed == []

    def test_jour_invalide(self):
        """Gère un jour invalide."""
        response = [{"jour": "Invalid", "dejeuner": "Test", "diner": "Test"}]
        parsed = parse_ai_planning_response(response)
        # Le jour devrait être conservé tel quel ou normalisé
        assert len(parsed) == 1

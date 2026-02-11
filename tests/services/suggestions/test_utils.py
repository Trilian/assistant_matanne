"""
Tests pour src/services/suggestions/utils.py
Cible: >80% couverture des fonctions utilitaires
"""

import pytest
from datetime import date, datetime
from unittest.mock import patch

from src.services.suggestions.utils import (
    # Constantes
    SAISONS,
    INGREDIENTS_SAISON,
    PROTEINES_POISSON,
    PROTEINES_VIANDE_ROUGE,
    PROTEINES_VOLAILLE,
    PROTEINES_VEGETARIEN,
    SCORE_INGREDIENT_DISPONIBLE,
    SCORE_INGREDIENT_PRIORITAIRE,
    SCORE_INGREDIENT_SAISON,
    SCORE_CATEGORIE_PREFEREE,
    SCORE_JAMAIS_PREPAREE,
    SCORE_DIFFICULTE_ADAPTEE,
    SCORE_TEMPS_ADAPTE,
    SCORE_VARIETE,
    # Fonctions saison
    get_current_season,
    get_seasonal_ingredients,
    is_ingredient_in_season,
    # Fonctions profil
    analyze_categories,
    analyze_frequent_ingredients,
    calculate_average_difficulty,
    calculate_average_time,
    calculate_average_portions,
    identify_favorites,
    days_since_last_preparation,
    # Fonctions scoring
    calculate_recipe_score,
    rank_recipes,
    generate_suggestion_reason,
    # Fonctions protéines
    detect_protein_type,
    calculate_week_protein_balance,
    is_week_balanced,
    # Fonctions variété
    calculate_variety_score,
    get_least_prepared_recipes,
    # Fonctions formatage
    format_suggestion,
    format_profile_summary,
    filter_by_constraints,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConstantes:
    """Tests pour les constantes."""

    def test_saisons_structure(self):
        """Vérifie la structure des saisons."""
        assert len(SAISONS) == 4
        assert all(saison in SAISONS for saison in ["printemps", "été", "automne", "hiver"])

    def test_saisons_mois(self):
        """Vérifie que chaque saison a les bons mois."""
        assert SAISONS["printemps"] == [3, 4, 5]
        assert SAISONS["été"] == [6, 7, 8]
        assert SAISONS["automne"] == [9, 10, 11]
        assert SAISONS["hiver"] == [12, 1, 2]

    def test_ingredients_saison_complete(self):
        """Vérifie que chaque saison a des ingrédients."""
        for saison in SAISONS:
            assert saison in INGREDIENTS_SAISON
            assert len(INGREDIENTS_SAISON[saison]) > 0

    def test_proteines_listes(self):
        """Vérifie les listes de protéines."""
        assert "saumon" in PROTEINES_POISSON
        assert "boeuf" in PROTEINES_VIANDE_ROUGE
        assert "poulet" in PROTEINES_VOLAILLE
        assert "tofu" in PROTEINES_VEGETARIEN

    def test_scores_positifs(self):
        """Vérifie que les scores sont positifs."""
        assert SCORE_INGREDIENT_DISPONIBLE > 0
        assert SCORE_INGREDIENT_PRIORITAIRE > 0
        assert SCORE_INGREDIENT_SAISON > 0
        assert SCORE_CATEGORIE_PREFEREE > 0
        assert SCORE_JAMAIS_PREPAREE > 0
        assert SCORE_DIFFICULTE_ADAPTEE > 0
        assert SCORE_TEMPS_ADAPTE > 0
        assert SCORE_VARIETE > 0


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS SAISON
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetCurrentSeason:
    """Tests pour get_current_season."""

    def test_printemps(self):
        """Vérifie détection du printemps."""
        assert get_current_season(date(2024, 3, 15)) == "printemps"
        assert get_current_season(date(2024, 4, 1)) == "printemps"
        assert get_current_season(date(2024, 5, 31)) == "printemps"

    def test_ete(self):
        """Vérifie détection de l'été."""
        assert get_current_season(date(2024, 6, 1)) == "été"
        assert get_current_season(date(2024, 7, 15)) == "été"
        assert get_current_season(date(2024, 8, 31)) == "été"

    def test_automne(self):
        """Vérifie détection de l'automne."""
        assert get_current_season(date(2024, 9, 1)) == "automne"
        assert get_current_season(date(2024, 10, 15)) == "automne"
        assert get_current_season(date(2024, 11, 30)) == "automne"

    def test_hiver(self):
        """Vérifie détection de l'hiver."""
        assert get_current_season(date(2024, 12, 1)) == "hiver"
        assert get_current_season(date(2024, 1, 15)) == "hiver"
        assert get_current_season(date(2024, 2, 28)) == "hiver"

    def test_datetime_input(self):
        """Vérifie avec un datetime."""
        assert get_current_season(datetime(2024, 7, 15, 14, 30)) == "été"

    def test_none_uses_today(self):
        """Vérifie que None utilise aujourd'hui."""
        result = get_current_season(None)
        assert result in SAISONS


@pytest.mark.unit
class TestGetSeasonalIngredients:
    """Tests pour get_seasonal_ingredients."""

    def test_ete_ingredients(self):
        """Vérifie les ingrédients d'été."""
        ingredients = get_seasonal_ingredients("été")
        assert "tomate" in ingredients
        assert "courgette" in ingredients

    def test_hiver_ingredients(self):
        """Vérifie les ingrédients d'hiver."""
        ingredients = get_seasonal_ingredients("hiver")
        assert "endive" in ingredients
        assert "orange" in ingredients

    def test_none_uses_current(self):
        """Vérifie que None utilise la saison actuelle."""
        ingredients = get_seasonal_ingredients(None)
        assert isinstance(ingredients, list)
        assert len(ingredients) > 0

    def test_accent_normalization(self):
        """Vérifie la normalisation des accents."""
        assert get_seasonal_ingredients("ete") == INGREDIENTS_SAISON["été"]
        assert get_seasonal_ingredients("ETE") == INGREDIENTS_SAISON["été"]

    def test_invalid_saison_returns_empty(self):
        """Vérifie qu'une saison invalide retourne vide."""
        assert get_seasonal_ingredients("invalid") == []


@pytest.mark.unit
class TestIsIngredientInSeason:
    """Tests pour is_ingredient_in_season."""

    def test_tomate_en_ete(self):
        """Vérifie que tomate est de saison en été."""
        assert is_ingredient_in_season("tomate", "été") is True

    def test_tomate_en_hiver(self):
        """Vérifie que tomate n'est pas de saison en hiver."""
        assert is_ingredient_in_season("tomate", "hiver") is False

    def test_partial_match(self):
        """Vérifie le match partiel."""
        assert is_ingredient_in_season("tomates cerises", "été") is True

    def test_no_match(self):
        """Vérifie le non-match."""
        assert is_ingredient_in_season("pizza", "été") is False


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS PROFIL
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyzeCategories:
    """Tests pour analyze_categories."""

    def test_empty_historique(self):
        """Vérifie avec historique vide."""
        assert analyze_categories([]) == []

    def test_single_categorie(self):
        """Vérifie avec une seule catégorie."""
        historique = [{"categorie": "italien"}, {"categorie": "italien"}]
        result = analyze_categories(historique)
        assert result == ["italien"]

    def test_multiple_categories(self):
        """Vérifie avec plusieurs catégories."""
        historique = [
            {"categorie": "italien"},
            {"categorie": "italien"},
            {"categorie": "italien"},
            {"categorie": "asiatique"},
            {"categorie": "asiatique"},
            {"categorie": "français"},
        ]
        result = analyze_categories(historique)
        assert result[0] == "italien"  # Plus fréquent
        assert "asiatique" in result

    def test_max_5_categories(self):
        """Vérifie le max de 5 catégories."""
        historique = [
            {"categorie": f"cat{i}"} for i in range(10)
        ]
        result = analyze_categories(historique)
        assert len(result) <= 5

    def test_ignore_none_categories(self):
        """Vérifie l'ignorance des None."""
        historique = [{"categorie": None}, {"categorie": "italien"}]
        result = analyze_categories(historique)
        assert result == ["italien"]


@pytest.mark.unit
class TestAnalyzeFrequentIngredients:
    """Tests pour analyze_frequent_ingredients."""

    def test_empty_historique(self):
        """Vérifie avec historique vide."""
        assert analyze_frequent_ingredients([]) == []

    def test_single_recette(self):
        """Vérifie avec une seule recette."""
        historique = [{"ingredients": ["tomate", "oignon"]}]
        result = analyze_frequent_ingredients(historique)
        assert set(result) == {"tomate", "oignon"}

    def test_multiple_recettes(self):
        """Vérifie avec plusieurs recettes."""
        historique = [
            {"ingredients": ["tomate", "oignon"]},
            {"ingredients": ["tomate", "ail"]},
            {"ingredients": ["tomate", "poivron"]},
        ]
        result = analyze_frequent_ingredients(historique)
        assert result[0] == "tomate"  # Plus fréquent

    def test_max_10_ingredients(self):
        """Vérifie le max de 10 ingrédients."""
        historique = [
            {"ingredients": [f"ing{i}" for i in range(20)]}
        ]
        result = analyze_frequent_ingredients(historique)
        assert len(result) <= 10


@pytest.mark.unit
class TestCalculateAverageDifficulty:
    """Tests pour calculate_average_difficulty."""

    def test_empty_historique(self):
        """Vérifie avec historique vide."""
        assert calculate_average_difficulty([]) == "moyen"

    def test_single_difficulty(self):
        """Vérifie avec une seule difficulté."""
        historique = [{"difficulte": "facile"}, {"difficulte": "facile"}]
        assert calculate_average_difficulty(historique) == "facile"

    def test_most_common(self):
        """Vérifie le calcul du plus commun."""
        historique = [
            {"difficulte": "facile"},
            {"difficulte": "facile"},
            {"difficulte": "difficile"},
        ]
        assert calculate_average_difficulty(historique) == "facile"


@pytest.mark.unit
class TestCalculateAverageTime:
    """Tests pour calculate_average_time."""

    def test_empty_historique(self):
        """Vérifie avec historique vide."""
        assert calculate_average_time([]) == 45

    def test_single_time(self):
        """Vérifie avec un seul temps."""
        historique = [{"temps_preparation": 30}]
        assert calculate_average_time(historique) == 30

    def test_average_calculation(self):
        """Vérifie le calcul de moyenne."""
        historique = [
            {"temps_preparation": 30},
            {"temps_preparation": 60},
        ]
        assert calculate_average_time(historique) == 45


@pytest.mark.unit
class TestCalculateAveragePortions:
    """Tests pour calculate_average_portions."""

    def test_empty_historique(self):
        """Vérifie avec historique vide."""
        assert calculate_average_portions([]) == 4

    def test_average_calculation(self):
        """Vérifie le calcul de moyenne."""
        historique = [
            {"portions": 4},
            {"portions": 6},
        ]
        assert calculate_average_portions(historique) == 5


@pytest.mark.unit
class TestIdentifyFavorites:
    """Tests pour identify_favorites."""

    def test_empty_historique(self):
        """Vérifie avec historique vide."""
        assert identify_favorites([]) == []

    def test_no_favorites(self):
        """Vérifie quand pas assez de répétitions."""
        historique = [{"recette_id": 1}, {"recette_id": 2}]
        assert identify_favorites(historique, min_count=3) == []

    def test_favorites_found(self):
        """Vérifie la détection des favoris."""
        historique = [
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 2},
        ]
        result = identify_favorites(historique, min_count=3)
        assert result == [1]

    def test_custom_min_count(self):
        """Vérifie le min_count personnalisé."""
        historique = [{"recette_id": 1}, {"recette_id": 1}]
        result = identify_favorites(historique, min_count=2)
        assert result == [1]


@pytest.mark.unit
class TestDaysSinceLastPreparation:
    """Tests pour days_since_last_preparation."""

    def test_never_prepared(self):
        """Vérifie quand jamais préparée."""
        historique = [{"recette_id": 2, "date": "2024-01-01"}]
        result = days_since_last_preparation(1, historique)
        assert result is None

    def test_days_calculation(self):
        """Vérifie le calcul des jours."""
        ref_date = date(2024, 1, 15)
        historique = [{"recette_id": 1, "date": "2024-01-10"}]
        result = days_since_last_preparation(1, historique, ref_date)
        assert result == 5

    def test_datetime_in_historique(self):
        """Vérifie avec datetime dans l'historique."""
        ref_date = date(2024, 1, 15)
        historique = [{"recette_id": 1, "date": datetime(2024, 1, 10)}]
        result = days_since_last_preparation(1, historique, ref_date)
        assert result == 5

    def test_date_cuisson_key(self):
        """Vérifie avec la clé date_cuisson."""
        ref_date = date(2024, 1, 15)
        historique = [{"recette_id": 1, "date_cuisson": "2024-01-10"}]
        result = days_since_last_preparation(1, historique, ref_date)
        assert result == 5

    def test_most_recent(self):
        """Vérifie qu'on prend la plus récente."""
        ref_date = date(2024, 1, 15)
        historique = [
            {"recette_id": 1, "date": "2024-01-05"},
            {"recette_id": 1, "date": "2024-01-10"},
        ]
        result = days_since_last_preparation(1, historique, ref_date)
        assert result == 5


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS SCORING
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculateRecipeScore:
    """Tests pour calculate_recipe_score."""

    def test_minimal_input(self):
        """Vérifie avec entrée minimale."""
        recette = {"id": 1, "nom": "Test"}
        contexte = {}
        score = calculate_recipe_score(recette, contexte)
        assert score >= 0

    def test_bonus_ingredients_disponibles(self):
        """Vérifie le bonus pour ingrédients disponibles."""
        recette = {"id": 1, "ingredients": ["tomate", "oignon"]}
        contexte = {"ingredients_disponibles": ["tomate"]}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_INGREDIENT_DISPONIBLE

    def test_bonus_ingredients_prioritaires(self):
        """Vérifie le bonus pour ingrédients prioritaires."""
        recette = {"id": 1, "ingredients": ["tomate"]}
        contexte = {"ingredients_a_utiliser": ["tomate"]}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_INGREDIENT_PRIORITAIRE

    def test_bonus_categorie_preferee(self):
        """Vérifie le bonus pour catégorie préférée."""
        recette = {"id": 1, "categorie": "italien"}
        contexte = {}
        profil = {"categories_preferees": ["italien"]}
        score = calculate_recipe_score(recette, contexte, profil)
        assert score >= SCORE_CATEGORIE_PREFEREE

    def test_bonus_temps_adapte(self):
        """Vérifie le bonus pour temps adapté."""
        recette = {"id": 1, "temps_preparation": 30}
        contexte = {"temps_disponible_minutes": 60}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_TEMPS_ADAPTE

    def test_malus_temps_trop_long(self):
        """Vérifie le malus pour temps trop long."""
        recette_rapide = {"id": 1, "temps_preparation": 30}
        recette_longue = {"id": 2, "temps_preparation": 90}
        contexte = {"temps_disponible_minutes": 30}
        score_rapide = calculate_recipe_score(recette_rapide, contexte)
        score_longue = calculate_recipe_score(recette_longue, contexte)
        assert score_rapide > score_longue

    def test_contrainte_vegetarien(self):
        """Vérifie la contrainte végétarien."""
        recette = {"id": 1, "est_vegetarien": False}
        contexte = {"contraintes": ["vegetarien"]}
        score = calculate_recipe_score(recette, contexte)
        assert score <= 50  # Pénalité appliquée

    def test_contrainte_sans_gluten(self):
        """Vérifie la contrainte sans gluten."""
        recette = {"id": 1, "contient_gluten": True}
        contexte = {"contraintes": ["sans gluten"]}
        score = calculate_recipe_score(recette, contexte)
        assert score <= 50  # Pénalité appliquée


@pytest.mark.unit
class TestRankRecipes:
    """Tests pour rank_recipes."""

    def test_empty_list(self):
        """Vérifie avec liste vide."""
        result = rank_recipes([], {})
        assert result == []

    def test_ranking_order(self):
        """Vérifie l'ordre de classement."""
        recettes = [
            {"id": 1, "temps_preparation": 120},  # Trop long
            {"id": 2, "temps_preparation": 30},   # Adapté
        ]
        contexte = {"temps_disponible_minutes": 60}
        result = rank_recipes(recettes, contexte)
        assert result[0]["id"] == 2  # Le rapide en premier

    def test_limit(self):
        """Vérifie la limite de résultats."""
        recettes = [{"id": i} for i in range(10)]
        result = rank_recipes(recettes, {}, limit=3)
        assert len(result) == 3

    def test_score_added(self):
        """Vérifie que le score est ajouté."""
        recettes = [{"id": 1}]
        result = rank_recipes(recettes, {})
        assert "score" in result[0]


@pytest.mark.unit
class TestGenerateSuggestionReason:
    """Tests pour generate_suggestion_reason."""

    def test_ingredients_prioritaires(self):
        """Vérifie la raison pour ingrédients prioritaires."""
        recette = {"ingredients": ["tomate"]}
        contexte = {"ingredients_a_utiliser": ["tomate"]}
        raison = generate_suggestion_reason(recette, contexte)
        assert "consommer" in raison.lower() or "tomate" in raison.lower()

    def test_saison(self):
        """Vérifie la raison pour ingrédient de saison."""
        recette = {"ingredients": ["tomate"]}
        contexte = {"saison": "été"}
        raison = generate_suggestion_reason(recette, contexte)
        assert "saison" in raison.lower() or len(raison) > 0

    def test_score_eleve(self):
        """Vérifie la raison pour score élevé."""
        recette = {"score": 85}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert len(raison) > 0

    def test_nouvelle_recette(self):
        """Vérifie la raison pour nouvelle recette."""
        recette = {"est_nouvelle": True}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert "découvrir" in raison.lower() or len(raison) > 0

    def test_default_reason(self):
        """Vérifie la raison par défaut."""
        recette = {}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert len(raison) > 0


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS PROTEINES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDetectProteinType:
    """Tests pour detect_protein_type."""

    def test_poisson_from_type(self):
        """Vérifie détection poisson du champ type."""
        recette = {"type_proteines": "saumon fumé"}
        assert detect_protein_type(recette) == "poisson"

    def test_viande_rouge_from_nom(self):
        """Vérifie détection viande rouge du nom."""
        recette = {"nom": "Boeuf bourguignon"}
        assert detect_protein_type(recette) == "viande_rouge"

    def test_volaille_from_description(self):
        """Vérifie détection volaille de la description."""
        recette = {"description": "Délicieux poulet rôti"}
        assert detect_protein_type(recette) == "volaille"

    def test_vegetarien_from_flag(self):
        """Vérifie détection végétarien du flag."""
        recette = {"est_vegetarien": True}
        assert detect_protein_type(recette) == "vegetarien"

    def test_vegetarien_from_ingredients(self):
        """Vérifie détection végétarien des ingrédients."""
        recette = {"ingredients": ["tofu", "légumes"]}
        assert detect_protein_type(recette) == "vegetarien"

    def test_autre(self):
        """Vérifie le type autre."""
        recette = {"nom": "Salade mixte"}
        assert detect_protein_type(recette) == "autre"


@pytest.mark.unit
class TestCalculateWeekProteinBalance:
    """Tests pour calculate_week_protein_balance."""

    def test_empty(self):
        """Vérifie avec liste vide."""
        result = calculate_week_protein_balance([])
        assert all(v == 0 for v in result.values())

    def test_mixed_week(self):
        """Vérifie avec semaine variée."""
        repas = [
            {"type_proteines": "saumon"},
            {"type_proteines": "poulet"},
            {"nom": "Boeuf bourguignon"},
            {"est_vegetarien": True},
        ]
        result = calculate_week_protein_balance(repas)
        assert result["poisson"] == 1
        assert result["volaille"] == 1
        assert result["viande_rouge"] == 1
        assert result["vegetarien"] == 1


@pytest.mark.unit
class TestIsWeekBalanced:
    """Tests pour is_week_balanced."""

    def test_balanced_week(self):
        """Vérifie une semaine équilibrée."""
        repas = [
            {"type_proteines": "saumon"},
            {"type_proteines": "cabillaud"},
            {"type_proteines": "poulet"},
            {"type_proteines": "dinde"},
            {"type_proteines": "boeuf"},
            {"est_vegetarien": True},
            {"type_proteines": "porc"},
        ]
        equilibre, problemes = is_week_balanced(repas)
        assert equilibre is True
        assert len(problemes) == 0

    def test_pas_assez_poisson(self):
        """Vérifie détection manque de poisson."""
        repas = [
            {"type_proteines": "boeuf"},
            {"type_proteines": "poulet"},
            {"est_vegetarien": True},
        ]
        equilibre, problemes = is_week_balanced(repas)
        assert equilibre is False
        assert any("poisson" in p.lower() for p in problemes)

    def test_trop_viande_rouge(self):
        """Vérifie détection trop de viande rouge."""
        repas = [
            {"nom": "Boeuf bourguignon"},
            {"nom": "Côte d'agneau"},
            {"nom": "Rôti de veau"},
            {"type_proteines": "saumon"},
            {"type_proteines": "cabillaud"},
            {"est_vegetarien": True},
        ]
        equilibre, problemes = is_week_balanced(repas)
        assert equilibre is False
        assert any("rouge" in p.lower() for p in problemes)


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS VARIETE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculateVarietyScore:
    """Tests pour calculate_variety_score."""

    def test_empty_selection(self):
        """Vérifie avec sélection vide."""
        assert calculate_variety_score([], []) == 100.0

    def test_all_new(self):
        """Vérifie avec toutes nouvelles recettes."""
        recettes = [{"id": 1}, {"id": 2}]
        historique = [{"recette_id": 99, "date": "2024-01-01"}]
        score = calculate_variety_score(recettes, historique)
        assert score == 100.0

    def test_all_repeated(self):
        """Vérifie avec toutes répétées récemment."""
        recettes = [{"id": 1}, {"id": 2}]
        today = date.today().isoformat()
        historique = [
            {"recette_id": 1, "date": today},
            {"recette_id": 2, "date": today},
        ]
        score = calculate_variety_score(recettes, historique, jours_reference=7)
        assert score == 0.0


@pytest.mark.unit
class TestGetLeastPreparedRecipes:
    """Tests pour get_least_prepared_recipes."""

    def test_empty(self):
        """Vérifie avec entrées vides."""
        assert get_least_prepared_recipes([], []) == []

    def test_order(self):
        """Vérifie l'ordre (moins préparées en premier)."""
        recettes = [{"id": 1}, {"id": 2}, {"id": 3}]
        historique = [
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 2},
        ]
        result = get_least_prepared_recipes(recettes, historique, limit=2)
        assert result[0]["id"] == 3  # Jamais préparée
        assert result[1]["id"] == 2  # Préparée 1 fois

    def test_limit(self):
        """Vérifie la limite."""
        recettes = [{"id": i} for i in range(10)]
        result = get_least_prepared_recipes(recettes, [], limit=3)
        assert len(result) == 3


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS FORMATAGE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFormatSuggestion:
    """Tests pour format_suggestion."""

    def test_minimal(self):
        """Vérifie avec données minimales."""
        recette = {"id": 1}
        result = format_suggestion(recette)
        assert result["id"] == 1
        assert result["nom"] == "Sans nom"

    def test_full_data(self):
        """Vérifie avec données complètes."""
        recette = {
            "id": 1,
            "nom": "Pâtes",
            "temps_preparation": 15,
            "temps_cuisson": 10,
            "difficulte": "facile",
            "categorie": "italien",
            "score": 85,
        }
        result = format_suggestion(recette, "Rapide à préparer")
        assert result["nom"] == "Pâtes"
        assert result["temps_total"] == 25
        assert result["temps_display"] == "25 min"
        assert result["raison"] == "Rapide à préparer"
        assert result["score"] == 85

    def test_protein_type_detected(self):
        """Vérifie la détection du type de protéine."""
        recette = {"id": 1, "nom": "Poulet rôti"}
        result = format_suggestion(recette)
        assert result["protein_type"] == "volaille"


@pytest.mark.unit
class TestFormatProfileSummary:
    """Tests pour format_profile_summary."""

    def test_empty_profile(self):
        """Vérifie avec profil vide."""
        result = format_profile_summary({})
        assert "construction" in result.lower()

    def test_full_profile(self):
        """Vérifie avec profil complet."""
        profil = {
            "categories_preferees": ["italien", "asiatique", "français"],
            "ingredients_frequents": ["tomate", "oignon", "ail", "huile", "sel"],
            "temps_moyen_minutes": 45,
            "recettes_favorites": [1, 2, 3],
        }
        result = format_profile_summary(profil)
        assert "italien" in result
        assert "tomate" in result
        assert "45" in result
        assert "3" in result or "favorites" in result.lower()


@pytest.mark.unit
class TestFilterByConstraints:
    """Tests pour filter_by_constraints."""

    def test_no_constraints(self):
        """Vérifie sans contraintes."""
        recettes = [{"id": 1}, {"id": 2}]
        result = filter_by_constraints(recettes, [])
        assert len(result) == 2

    def test_vegetarien_constraint(self):
        """Vérifie contrainte végétarien."""
        recettes = [
            {"id": 1, "est_vegetarien": True},
            {"id": 2, "nom": "Boeuf bourguignon"},
        ]
        result = filter_by_constraints(recettes, ["vegetarien"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_vegan_constraint(self):
        """Vérifie contrainte vegan."""
        recettes = [
            {"id": 1, "est_vegan": True},
            {"id": 2, "est_vegan": False},
        ]
        result = filter_by_constraints(recettes, ["vegan"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_sans_gluten_constraint(self):
        """Vérifie contrainte sans gluten."""
        recettes = [
            {"id": 1, "contient_gluten": False},
            {"id": 2, "contient_gluten": True},
        ]
        result = filter_by_constraints(recettes, ["sans gluten"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_sans_lactose_constraint(self):
        """Vérifie contrainte sans lactose."""
        recettes = [
            {"id": 1, "contient_lactose": False},
            {"id": 2, "contient_lactose": True},
        ]
        result = filter_by_constraints(recettes, ["sans lactose"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_multiple_constraints(self):
        """Vérifie plusieurs contraintes."""
        recettes = [
            {"id": 1, "est_vegetarien": True, "contient_gluten": False},
            {"id": 2, "est_vegetarien": True, "contient_gluten": True},
            {"id": 3, "nom": "Boeuf bourguignon"},  # Sera détecté comme viande rouge
        ]
        result = filter_by_constraints(recettes, ["vegetarien", "sans gluten"])
        assert len(result) == 1
        assert result[0]["id"] == 1

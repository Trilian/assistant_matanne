"""
Tests complets pour suggestions_ia_utils.py

Couvre toutes les fonctions pures du module:
- Détection de saison
- Analyse de profil culinaire
- Scoring de recettes
- Détection de protéines
- Équilibre nutritionnel
- Formatage et filtrage
"""

import pytest
from datetime import date, datetime, timedelta

from src.services.suggestions import (
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
    SCORE_TEMPS_ADAPTE,
    SCORE_DIFFICULTE_ADAPTEE,
    SCORE_VARIETE,
    # Fonctions saison
    get_current_season,
    get_seasonal_ingredients,
    is_ingredient_in_season,
    # Fonctions analyse profil
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


class TestConstantes:
    """Tests pour vérifier que les constantes sont bien définies."""

    def test_saisons_complete(self):
        """Vérifie que toutes les saisons sont définies."""
        assert len(SAISONS) == 4
        assert "printemps" in SAISONS
        assert "été" in SAISONS
        assert "automne" in SAISONS
        assert "hiver" in SAISONS

    def test_saisons_mois_valides(self):
        """Vérifie que tous les mois sont couverts."""
        all_months = []
        for mois in SAISONS.values():
            all_months.extend(mois)
        assert sorted(all_months) == list(range(1, 13))

    def test_ingredients_saison_non_vides(self):
        """Vérifie que chaque saison a des ingrédients."""
        for saison, ingredients in INGREDIENTS_SAISON.items():
            assert len(ingredients) > 0, f"{saison} n'a pas d'ingrédients"

    def test_proteines_listes_non_vides(self):
        """Vérifie que les listes de protéines sont définies."""
        assert len(PROTEINES_POISSON) > 0
        assert len(PROTEINES_VIANDE_ROUGE) > 0
        assert len(PROTEINES_VOLAILLE) > 0
        assert len(PROTEINES_VEGETARIEN) > 0


# ═══════════════════════════════════════════════════════════
# TESTS DÉTECTION SAISON
# ═══════════════════════════════════════════════════════════


class TestGetCurrentSeason:
    """Tests pour get_current_season()."""

    def test_printemps_mars(self):
        assert get_current_season(date(2024, 3, 15)) == "printemps"

    def test_printemps_avril(self):
        assert get_current_season(date(2024, 4, 1)) == "printemps"

    def test_printemps_mai(self):
        assert get_current_season(date(2024, 5, 31)) == "printemps"

    def test_ete_juin(self):
        assert get_current_season(date(2024, 6, 21)) == "été"

    def test_ete_juillet(self):
        assert get_current_season(date(2024, 7, 15)) == "été"

    def test_ete_aout(self):
        assert get_current_season(date(2024, 8, 31)) == "été"

    def test_automne_septembre(self):
        assert get_current_season(date(2024, 9, 22)) == "automne"

    def test_automne_octobre(self):
        assert get_current_season(date(2024, 10, 15)) == "automne"

    def test_automne_novembre(self):
        assert get_current_season(date(2024, 11, 30)) == "automne"

    def test_hiver_decembre(self):
        assert get_current_season(date(2024, 12, 25)) == "hiver"

    def test_hiver_janvier(self):
        assert get_current_season(date(2024, 1, 1)) == "hiver"

    def test_hiver_fevrier(self):
        assert get_current_season(date(2024, 2, 14)) == "hiver"

    def test_datetime_input(self):
        """Accepte datetime en plus de date."""
        dt = datetime(2024, 7, 15, 12, 30, 0)
        assert get_current_season(dt) == "été"

    def test_none_returns_current(self):
        """None retourne la saison actuelle."""
        result = get_current_season(None)
        assert result in SAISONS.keys()


class TestGetSeasonalIngredients:
    """Tests pour get_seasonal_ingredients()."""

    def test_ete_ingredients(self):
        ingredients = get_seasonal_ingredients("été")
        assert "tomate" in ingredients
        assert "courgette" in ingredients
        assert "aubergine" in ingredients

    def test_hiver_ingredients(self):
        ingredients = get_seasonal_ingredients("hiver")
        assert "endive" in ingredients
        assert "orange" in ingredients

    def test_printemps_ingredients(self):
        ingredients = get_seasonal_ingredients("printemps")
        assert "asperge" in ingredients
        assert "radis" in ingredients

    def test_automne_ingredients(self):
        ingredients = get_seasonal_ingredients("automne")
        assert "champignon" in ingredients
        assert "potiron" in ingredients

    def test_normalisation_accents(self):
        """Gère les accents correctement."""
        ing1 = get_seasonal_ingredients("ete")
        ing2 = get_seasonal_ingredients("été")
        assert ing1 == ing2

    def test_none_returns_current_season(self):
        """None retourne les ingrédients de la saison actuelle."""
        result = get_seasonal_ingredients(None)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_saison_inconnue_retourne_liste_vide(self):
        """Saison inconnue retourne liste vide."""
        result = get_seasonal_ingredients("invalide")
        assert result == []


class TestIsIngredientInSeason:
    """Tests pour is_ingredient_in_season()."""

    def test_tomate_ete(self):
        assert is_ingredient_in_season("tomate", "été") is True

    def test_tomate_hiver(self):
        assert is_ingredient_in_season("tomate", "hiver") is False

    def test_endive_hiver(self):
        assert is_ingredient_in_season("endive", "hiver") is True

    def test_asperge_printemps(self):
        assert is_ingredient_in_season("asperge", "printemps") is True

    def test_case_insensitive(self):
        """Insensible à la casse."""
        assert is_ingredient_in_season("TOMATE", "été") is True
        assert is_ingredient_in_season("Tomate", "été") is True

    def test_partial_match(self):
        """Match partiel fonctionne."""
        assert is_ingredient_in_season("tomates cerises", "été") is True

    def test_none_saison_uses_current(self):
        """None utilise la saison actuelle."""
        result = is_ingredient_in_season("tomate", None)
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE PROFIL CULINAIRE
# ═══════════════════════════════════════════════════════════


class TestAnalyzeCategories:
    """Tests pour analyze_categories()."""

    def test_categories_comptees(self):
        historique = [
            {"categorie": "italien"},
            {"categorie": "italien"},
            {"categorie": "asiatique"},
            {"categorie": "français"},
            {"categorie": "italien"},
        ]
        result = analyze_categories(historique)
        assert result[0] == "italien"  # Le plus fréquent

    def test_max_5_categories(self):
        historique = [{"categorie": f"cat{i}"} for i in range(10)]
        result = analyze_categories(historique)
        assert len(result) <= 5

    def test_historique_vide(self):
        result = analyze_categories([])
        assert result == []

    def test_ignore_none_categories(self):
        historique = [
            {"categorie": "italien"},
            {"categorie": None},
            {"autre": "valeur"},
            {"categorie": "italien"},
        ]
        result = analyze_categories(historique)
        assert result == ["italien"]


class TestAnalyzeFrequentIngredients:
    """Tests pour analyze_frequent_ingredients()."""

    def test_ingredients_comptees(self):
        historique = [
            {"ingredients": ["tomate", "oignon"]},
            {"ingredients": ["tomate", "ail"]},
            {"ingredients": ["tomate", "basilic"]},
        ]
        result = analyze_frequent_ingredients(historique)
        assert result[0] == "tomate"  # Le plus fréquent

    def test_max_10_ingredients(self):
        historique = [{"ingredients": [f"ing{i}" for i in range(20)]}]
        result = analyze_frequent_ingredients(historique)
        assert len(result) <= 10

    def test_historique_vide(self):
        result = analyze_frequent_ingredients([])
        assert result == []

    def test_ingredients_non_liste(self):
        """Ignore les ingredients qui ne sont pas des listes."""
        historique = [
            {"ingredients": ["tomate"]},
            {"ingredients": "pas une liste"},
        ]
        result = analyze_frequent_ingredients(historique)
        assert result == ["tomate"]


class TestCalculateAverageDifficulty:
    """Tests pour calculate_average_difficulty()."""

    def test_difficulte_la_plus_frequente(self):
        historique = [
            {"difficulte": "facile"},
            {"difficulte": "facile"},
            {"difficulte": "moyen"},
        ]
        result = calculate_average_difficulty(historique)
        assert result == "facile"

    def test_historique_vide_retourne_moyen(self):
        result = calculate_average_difficulty([])
        assert result == "moyen"

    def test_ignore_none(self):
        historique = [
            {"difficulte": "difficile"},
            {"difficulte": None},
        ]
        result = calculate_average_difficulty(historique)
        assert result == "difficile"


class TestCalculateAverageTime:
    """Tests pour calculate_average_time()."""

    def test_moyenne_calculee(self):
        historique = [
            {"temps_preparation": 30},
            {"temps_preparation": 60},
            {"temps_preparation": 30},
        ]
        result = calculate_average_time(historique)
        assert result == 40

    def test_historique_vide_retourne_45(self):
        result = calculate_average_time([])
        assert result == 45

    def test_ignore_zero(self):
        historique = [
            {"temps_preparation": 60},
            {"temps_preparation": 0},
        ]
        result = calculate_average_time(historique)
        assert result == 60


class TestCalculateAveragePortions:
    """Tests pour calculate_average_portions()."""

    def test_moyenne_calculee(self):
        historique = [
            {"portions": 4},
            {"portions": 6},
            {"portions": 2},
        ]
        result = calculate_average_portions(historique)
        assert result == 4

    def test_historique_vide_retourne_4(self):
        result = calculate_average_portions([])
        assert result == 4


class TestIdentifyFavorites:
    """Tests pour identify_favorites()."""

    def test_favoris_identifies(self):
        historique = [
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 2},
            {"recette_id": 2},
        ]
        result = identify_favorites(historique, min_count=3)
        assert 1 in result
        assert 2 not in result

    def test_min_count_custom(self):
        historique = [
            {"recette_id": 1},
            {"recette_id": 1},
        ]
        result = identify_favorites(historique, min_count=2)
        assert 1 in result

    def test_historique_vide(self):
        result = identify_favorites([])
        assert result == []


class TestDaysSinceLastPreparation:
    """Tests pour days_since_last_preparation()."""

    def test_calcul_jours(self):
        today = date.today()
        historique = [
            {"recette_id": 1, "date": today - timedelta(days=5)},
        ]
        result = days_since_last_preparation(1, historique, today)
        assert result == 5

    def test_recette_jamais_preparee(self):
        result = days_since_last_preparation(999, [])
        assert result is None

    def test_date_string_format(self):
        today = date.today()
        historique = [
            {"recette_id": 1, "date": (today - timedelta(days=3)).isoformat()},
        ]
        result = days_since_last_preparation(1, historique, today)
        assert result == 3

    def test_datetime_input(self):
        today = date.today()
        historique = [
            {"recette_id": 1, "date": datetime.combine(today - timedelta(days=2), datetime.min.time())},
        ]
        result = days_since_last_preparation(1, historique, today)
        assert result == 2

    def test_date_cuisson_fallback(self):
        today = date.today()
        historique = [
            {"recette_id": 1, "date_cuisson": today - timedelta(days=7)},
        ]
        result = days_since_last_preparation(1, historique, today)
        assert result == 7

    def test_plusieurs_dates_prend_la_plus_recente(self):
        today = date.today()
        historique = [
            {"recette_id": 1, "date": today - timedelta(days=10)},
            {"recette_id": 1, "date": today - timedelta(days=2)},
        ]
        result = days_since_last_preparation(1, historique, today)
        assert result == 2


# ═══════════════════════════════════════════════════════════
# TESTS SCORING RECETTES
# ═══════════════════════════════════════════════════════════


class TestCalculateRecipeScore:
    """Tests pour calculate_recipe_score()."""

    def test_score_ingredient_disponible(self):
        recette = {"ingredients": ["tomate", "oignon"]}
        contexte = {"ingredients_disponibles": ["tomate"]}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_INGREDIENT_DISPONIBLE

    def test_score_ingredient_prioritaire(self):
        recette = {"ingredients": ["tomate"]}
        contexte = {"ingredients_a_utiliser": ["tomate"]}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_INGREDIENT_PRIORITAIRE

    def test_score_categorie_preferee(self):
        recette = {"categorie": "italien"}
        contexte = {}
        profil = {"categories_preferees": ["italien"]}
        score = calculate_recipe_score(recette, contexte, profil)
        assert score >= SCORE_CATEGORIE_PREFEREE

    def test_score_temps_adapte(self):
        recette = {"temps_preparation": 20, "temps_cuisson": 10}
        contexte = {"temps_disponible_minutes": 60}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_TEMPS_ADAPTE

    def test_penalite_temps_trop_long(self):
        recette = {"temps_preparation": 60, "temps_cuisson": 60}
        contexte = {"temps_disponible_minutes": 30}
        score = calculate_recipe_score(recette, contexte)
        # Le score devrait être réduit
        assert score < 50

    def test_score_jamais_preparee(self):
        recette = {"id": 1}
        contexte = {}
        historique = [{"recette_id": 2}]  # Autre recette
        score = calculate_recipe_score(recette, contexte, None, historique)
        assert score >= SCORE_JAMAIS_PREPAREE

    def test_penalite_contrainte_vegetarien(self):
        recette = {"est_vegetarien": False}
        contexte = {"contraintes": ["vegetarien"]}
        score = calculate_recipe_score(recette, contexte)
        assert score < 0 or score == 0  # Pénalité de -50

    def test_score_normalise_0_100(self):
        recette = {"ingredients": ["a"] * 20}
        contexte = {"ingredients_a_utiliser": ["a"] * 20}
        score = calculate_recipe_score(recette, contexte)
        assert 0 <= score <= 100


class TestRankRecipes:
    """Tests pour rank_recipes()."""

    def test_tri_par_score(self):
        recettes = [
            {"id": 1, "ingredients": []},
            {"id": 2, "ingredients": ["tomate"]},
        ]
        contexte = {"ingredients_a_utiliser": ["tomate"]}
        result = rank_recipes(recettes, contexte)
        assert result[0]["id"] == 2  # Meilleur score

    def test_limit_resultat(self):
        recettes = [{"id": i} for i in range(10)]
        result = rank_recipes(recettes, {}, limit=3)
        assert len(result) == 3

    def test_score_ajoute(self):
        recettes = [{"id": 1}]
        result = rank_recipes(recettes, {})
        assert "score" in result[0]


class TestGenerateSuggestionReason:
    """Tests pour generate_suggestion_reason()."""

    def test_raison_ingredient_prioritaire(self):
        recette = {"ingredients": ["tomate"]}
        contexte = {"ingredients_a_utiliser": ["tomate"]}
        raison = generate_suggestion_reason(recette, contexte)
        assert "tomate" in raison.lower()

    def test_raison_ingredient_saison(self):
        recette = {"ingredients": ["tomate"]}
        contexte = {"saison": "été"}
        raison = generate_suggestion_reason(recette, contexte)
        assert "saison" in raison.lower() or "tomate" in raison.lower()

    def test_raison_score_eleve(self):
        recette = {"score": 85}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert "préférences" in raison.lower() or "profil" in raison.lower()

    def test_raison_recette_nouvelle(self):
        recette = {"est_nouvelle": True}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert "découvrir" in raison.lower()


# ═══════════════════════════════════════════════════════════
# TESTS DÉTECTION PROTÉINES
# ═══════════════════════════════════════════════════════════


class TestDetectProteinType:
    """Tests pour detect_protein_type()."""

    def test_poisson_explicite(self):
        recette = {"type_proteines": "saumon"}
        assert detect_protein_type(recette) == "poisson"

    def test_viande_rouge_nom(self):
        recette = {"nom": "Boeuf bourguignon"}
        assert detect_protein_type(recette) == "viande_rouge"

    def test_volaille_description(self):
        recette = {"description": "Délicieux poulet rôti"}
        assert detect_protein_type(recette) == "volaille"

    def test_vegetarien_flag(self):
        recette = {"est_vegetarien": True}
        assert detect_protein_type(recette) == "vegetarien"

    def test_vegetarien_ingredients(self):
        recette = {"ingredients": ["tofu", "légumes"]}
        assert detect_protein_type(recette) == "vegetarien"

    def test_autre_par_defaut(self):
        recette = {"nom": "Salade verte"}
        assert detect_protein_type(recette) == "autre"


class TestCalculateWeekProteinBalance:
    """Tests pour calculate_week_protein_balance()."""

    def test_comptage_correct(self):
        repas = [
            {"nom": "Saumon grillé"},
            {"nom": "Boeuf bourguignon"},
            {"nom": "Poulet rôti"},
            {"est_vegetarien": True},
        ]
        balance = calculate_week_protein_balance(repas)
        assert balance["poisson"] == 1
        assert balance["viande_rouge"] == 1
        assert balance["volaille"] == 1
        assert balance["vegetarien"] == 1


class TestIsWeekBalanced:
    """Tests pour is_week_balanced()."""

    def test_semaine_equilibree(self):
        repas = [
            {"nom": "Saumon"},
            {"nom": "Thon"},
            {"est_vegetarien": True},
            {"nom": "Poulet"},
            {"nom": "Boeuf"},
        ]
        balanced, problemes = is_week_balanced(repas)
        assert balanced is True
        assert len(problemes) == 0

    def test_pas_assez_poisson(self):
        repas = [
            {"nom": "Boeuf"},
            {"nom": "Poulet"},
            {"nom": "Agneau"},
        ]
        balanced, problemes = is_week_balanced(repas)
        assert balanced is False
        assert any("poisson" in p.lower() for p in problemes)

    def test_trop_viande_rouge(self):
        repas = [
            {"nom": "Saumon"},
            {"nom": "Saumon"},
            {"est_vegetarien": True},
            {"nom": "Boeuf"},
            {"nom": "Agneau"},
            {"nom": "Veau"},
        ]
        balanced, problemes = is_week_balanced(repas)
        assert balanced is False
        assert any("viande rouge" in p.lower() for p in problemes)


# ═══════════════════════════════════════════════════════════
# TESTS VARIÉTÉ
# ═══════════════════════════════════════════════════════════


class TestCalculateVarietyScore:
    """Tests pour calculate_variety_score()."""

    def test_nouvelles_recettes_score_100(self):
        recettes = [{"id": 1}, {"id": 2}]
        historique = [{"recette_id": 99, "date": date.today()}]
        score = calculate_variety_score(recettes, historique)
        assert score == 100.0

    def test_repetitions_score_reduit(self):
        today = date.today()
        recettes = [{"id": 1}, {"id": 2}]
        historique = [
            {"recette_id": 1, "date": today - timedelta(days=3)},
        ]
        score = calculate_variety_score(recettes, historique)
        assert score == 50.0

    def test_liste_vide_score_100(self):
        score = calculate_variety_score([], [])
        assert score == 100.0


class TestGetLeastPreparedRecipes:
    """Tests pour get_least_prepared_recipes()."""

    def test_tri_par_preparation(self):
        recettes = [{"id": 1}, {"id": 2}, {"id": 3}]
        historique = [
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 2},
        ]
        result = get_least_prepared_recipes(recettes, historique)
        assert result[0]["id"] == 3  # Jamais préparée

    def test_limit_respecte(self):
        recettes = [{"id": i} for i in range(10)]
        result = get_least_prepared_recipes(recettes, [], limit=3)
        assert len(result) == 3


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════


class TestFormatSuggestion:
    """Tests pour format_suggestion()."""

    def test_format_complet(self):
        recette = {
            "id": 1,
            "nom": "Pâtes carbonara",
            "temps_preparation": 15,
            "temps_cuisson": 10,
            "difficulte": "facile",
            "categorie": "italien",
            "score": 85,
        }
        result = format_suggestion(recette, "Délicieux!")
        assert result["id"] == 1
        assert result["nom"] == "Pâtes carbonara"
        assert result["temps_total"] == 25
        assert result["raison"] == "Délicieux!"

    def test_format_minimal(self):
        recette = {"id": 1}
        result = format_suggestion(recette)
        assert result["nom"] == "Sans nom"
        assert result["temps_display"] == "Non spécifié"


class TestFormatProfileSummary:
    """Tests pour format_profile_summary()."""

    def test_format_complet(self):
        profil = {
            "categories_preferees": ["italien", "français"],
            "ingredients_frequents": ["tomate", "oignon"],
            "temps_moyen_minutes": 45,
            "recettes_favorites": [1, 2, 3],
        }
        result = format_profile_summary(profil)
        assert "italien" in result
        assert "tomate" in result
        assert "45 min" in result

    def test_profil_vide(self):
        result = format_profile_summary({})
        assert "construction" in result.lower()


class TestFilterByConstraints:
    """Tests pour filter_by_constraints()."""

    def test_filtre_vegetarien(self):
        recettes = [
            {"id": 1, "est_vegetarien": True},
            {"id": 2, "nom": "Poulet rôti"},
        ]
        result = filter_by_constraints(recettes, ["vegetarien"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_filtre_vegan(self):
        recettes = [
            {"id": 1, "est_vegan": True},
            {"id": 2, "est_vegetarien": True},
        ]
        result = filter_by_constraints(recettes, ["vegan"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_filtre_sans_gluten(self):
        recettes = [
            {"id": 1, "contient_gluten": False},
            {"id": 2, "contient_gluten": True},
        ]
        result = filter_by_constraints(recettes, ["sans gluten"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_filtre_sans_lactose(self):
        recettes = [
            {"id": 1, "contient_lactose": False},
            {"id": 2, "contient_lactose": True},
        ]
        result = filter_by_constraints(recettes, ["sans lactose"])
        assert len(result) == 1

    def test_pas_de_contraintes(self):
        recettes = [{"id": 1}, {"id": 2}]
        result = filter_by_constraints(recettes, [])
        assert len(result) == 2

    def test_contraintes_multiples(self):
        recettes = [
            {"id": 1, "est_vegetarien": True, "contient_gluten": False},
            {"id": 2, "est_vegetarien": True, "contient_gluten": True},
            {"id": 3, "nom": "Boeuf", "contient_gluten": False},
        ]
        result = filter_by_constraints(recettes, ["vegetarien", "sans gluten"])
        assert len(result) == 1
        assert result[0]["id"] == 1

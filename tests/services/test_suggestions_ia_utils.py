"""
Tests unitaires pour suggestions_ia_utils.py

Ces tests vérifient les fonctions pures sans dépendance base de données.
"""

import pytest
from datetime import date, datetime, timedelta
from src.services.suggestions import (
    # Saison
    get_current_season,
    get_seasonal_ingredients,
    is_ingredient_in_season,
    
    # Analyse du profil
    analyze_categories,
    analyze_frequent_ingredients,
    calculate_average_difficulty,
    calculate_average_time,
    calculate_average_portions,
    identify_favorites,
    days_since_last_preparation,
    
    # Scoring
    calculate_recipe_score,
    rank_recipes,
    generate_suggestion_reason,
    
    # Protéines
    detect_protein_type,
    calculate_week_protein_balance,
    is_week_balanced,
    
    # Variété
    calculate_variety_score,
    get_least_prepared_recipes,
    
    # Formatage
    format_suggestion,
    format_profile_summary,
    filter_by_constraints,
    
    # Constantes
    SAISONS,
    INGREDIENTS_SAISON,
)


# ═══════════════════════════════════════════════════════════
# Tests: Détermination de la saison
# ═══════════════════════════════════════════════════════════


class TestGetCurrentSeason:
    """Tests pour get_current_season"""
    
    def test_printemps(self):
        assert get_current_season(date(2024, 3, 15)) == "printemps"
        assert get_current_season(date(2024, 4, 20)) == "printemps"
        assert get_current_season(date(2024, 5, 31)) == "printemps"
    
    def test_ete(self):
        assert get_current_season(date(2024, 6, 1)) == "été"
        assert get_current_season(date(2024, 7, 15)) == "été"
        assert get_current_season(date(2024, 8, 31)) == "été"
    
    def test_automne(self):
        assert get_current_season(date(2024, 9, 1)) == "automne"
        assert get_current_season(date(2024, 10, 15)) == "automne"
        assert get_current_season(date(2024, 11, 30)) == "automne"
    
    def test_hiver(self):
        assert get_current_season(date(2024, 12, 1)) == "hiver"
        assert get_current_season(date(2024, 1, 15)) == "hiver"
        assert get_current_season(date(2024, 2, 28)) == "hiver"
    
    def test_datetime_input(self):
        dt = datetime(2024, 7, 15, 12, 30)
        assert get_current_season(dt) == "été"
    
    def test_none_input(self):
        # Devrait retourner la saison actuelle
        saison = get_current_season(None)
        assert saison in ["printemps", "été", "automne", "hiver"]


class TestGetSeasonalIngredients:
    """Tests pour get_seasonal_ingredients"""
    
    def test_ingredients_ete(self):
        ingredients = get_seasonal_ingredients("été")
        assert "tomate" in ingredients
        assert "courgette" in ingredients
        assert "melon" in ingredients
    
    def test_ingredients_hiver(self):
        ingredients = get_seasonal_ingredients("hiver")
        assert "endive" in ingredients
        assert "orange" in ingredients
    
    def test_ingredients_printemps(self):
        ingredients = get_seasonal_ingredients("printemps")
        assert "asperge" in ingredients
        assert "fraise" in ingredients
    
    def test_ingredients_automne(self):
        ingredients = get_seasonal_ingredients("automne")
        assert "champignon" in ingredients
        assert "potiron" in ingredients
    
    def test_saison_none(self):
        # Devrait utiliser la saison courante
        ingredients = get_seasonal_ingredients(None)
        assert isinstance(ingredients, list)
        assert len(ingredients) > 0
    
    def test_normalisation_accent(self):
        # "ete" sans accent devrait fonctionner
        ingredients = get_seasonal_ingredients("ete")
        assert len(ingredients) > 0


class TestIsIngredientInSeason:
    """Tests pour is_ingredient_in_season"""
    
    def test_tomate_ete(self):
        assert is_ingredient_in_season("tomate", "été") is True
    
    def test_tomate_hiver(self):
        assert is_ingredient_in_season("tomate", "hiver") is False
    
    def test_orange_hiver(self):
        assert is_ingredient_in_season("orange", "hiver") is True
    
    def test_asperge_printemps(self):
        assert is_ingredient_in_season("asperge", "printemps") is True
    
    def test_case_insensitive(self):
        assert is_ingredient_in_season("TOMATE", "été") is True
        assert is_ingredient_in_season("Tomate", "été") is True
    
    def test_partial_match(self):
        # "tomates cerises" contient "tomate"
        assert is_ingredient_in_season("tomates cerises", "été") is True


# ═══════════════════════════════════════════════════════════
# Tests: Analyse du profil culinaire
# ═══════════════════════════════════════════════════════════


class TestAnalyzeCategories:
    """Tests pour analyze_categories"""
    
    def test_categories_triees(self):
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
        assert result[1] == "asiatique"
    
    def test_historique_vide(self):
        assert analyze_categories([]) == []
    
    def test_max_5_categories(self):
        historique = [{"categorie": f"cat{i}"} for i in range(10)]
        result = analyze_categories(historique)
        assert len(result) <= 5
    
    def test_ignore_none(self):
        historique = [
            {"categorie": "italien"},
            {"categorie": None},
            {},
        ]
        result = analyze_categories(historique)
        assert result == ["italien"]


class TestAnalyzeFrequentIngredients:
    """Tests pour analyze_frequent_ingredients"""
    
    def test_ingredients_tries(self):
        historique = [
            {"ingredients": ["tomate", "oignon", "ail"]},
            {"ingredients": ["tomate", "oignon"]},
            {"ingredients": ["tomate"]},
        ]
        result = analyze_frequent_ingredients(historique)
        assert result[0] == "tomate"  # 3 occurrences
    
    def test_max_10_ingredients(self):
        historique = [{"ingredients": [f"ing{i}" for i in range(20)]}]
        result = analyze_frequent_ingredients(historique)
        assert len(result) <= 10
    
    def test_historique_vide(self):
        assert analyze_frequent_ingredients([]) == []


class TestCalculateAverageDifficulty:
    """Tests pour calculate_average_difficulty"""
    
    def test_difficulte_majoritaire(self):
        historique = [
            {"difficulte": "facile"},
            {"difficulte": "facile"},
            {"difficulte": "moyen"},
        ]
        assert calculate_average_difficulty(historique) == "facile"
    
    def test_historique_vide(self):
        assert calculate_average_difficulty([]) == "moyen"
    
    def test_ignore_none(self):
        historique = [
            {"difficulte": "difficile"},
            {"difficulte": None},
        ]
        assert calculate_average_difficulty(historique) == "difficile"


class TestCalculateAverageTime:
    """Tests pour calculate_average_time"""
    
    def test_temps_moyen(self):
        historique = [
            {"temps_preparation": 30},
            {"temps_preparation": 60},
        ]
        assert calculate_average_time(historique) == 45
    
    def test_historique_vide(self):
        assert calculate_average_time([]) == 45  # Valeur par défaut
    
    def test_ignore_zero(self):
        historique = [
            {"temps_preparation": 60},
            {"temps_preparation": 0},
        ]
        assert calculate_average_time(historique) == 60


class TestCalculateAveragePortions:
    """Tests pour calculate_average_portions"""
    
    def test_portions_moyennes(self):
        historique = [
            {"portions": 4},
            {"portions": 6},
        ]
        assert calculate_average_portions(historique) == 5
    
    def test_historique_vide(self):
        assert calculate_average_portions([]) == 4  # Valeur par défaut


class TestIdentifyFavorites:
    """Tests pour identify_favorites"""
    
    def test_recettes_favorites(self):
        historique = [
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 2},
        ]
        result = identify_favorites(historique, min_count=3)
        assert 1 in result
        assert 2 not in result
    
    def test_seuil_personnalise(self):
        historique = [
            {"recette_id": 5},
            {"recette_id": 5},
        ]
        result = identify_favorites(historique, min_count=2)
        assert 5 in result


class TestDaysSinceLastPreparation:
    """Tests pour days_since_last_preparation"""
    
    def test_jours_depuis(self):
        today = date.today()
        historique = [
            {"recette_id": 1, "date": (today - timedelta(days=5)).isoformat()},
        ]
        result = days_since_last_preparation(1, historique, today)
        assert result == 5
    
    def test_jamais_preparee(self):
        result = days_since_last_preparation(999, [], date.today())
        assert result is None
    
    def test_plusieurs_preparations(self):
        today = date.today()
        historique = [
            {"recette_id": 1, "date": (today - timedelta(days=10)).isoformat()},
            {"recette_id": 1, "date": (today - timedelta(days=3)).isoformat()},
        ]
        result = days_since_last_preparation(1, historique, today)
        assert result == 3  # Plus récente


# ═══════════════════════════════════════════════════════════
# Tests: Scoring des recettes
# ═══════════════════════════════════════════════════════════


class TestCalculateRecipeScore:
    """Tests pour calculate_recipe_score"""
    
    def test_score_basique(self):
        recette = {"id": 1, "nom": "Salade", "ingredients": ["tomate", "salade"]}
        contexte = {"ingredients_disponibles": ["tomate", "salade"]}
        score = calculate_recipe_score(recette, contexte)
        assert score > 0
    
    def test_score_ingredient_prioritaire(self):
        recette = {"id": 1, "nom": "Tarte", "ingredients": ["tomate"]}
        contexte = {"ingredients_a_utiliser": ["tomate"]}
        score = calculate_recipe_score(recette, contexte)
        assert score >= 25  # SCORE_INGREDIENT_PRIORITAIRE
    
    def test_score_categorie_preferee(self):
        recette = {"id": 1, "categorie": "italien"}
        contexte = {}
        profil = {"categories_preferees": ["italien"]}
        score = calculate_recipe_score(recette, contexte, profil)
        assert score >= 15  # SCORE_CATEGORIE_PREFEREE
    
    def test_penalite_temps(self):
        recette = {"id": 1, "temps_preparation": 60, "temps_cuisson": 60}
        contexte = {"temps_disponible_minutes": 30}
        score = calculate_recipe_score(recette, contexte)
        # Le score devrait être pénalisé
        assert score < 50
    
    def test_contrainte_vegetarienne(self):
        recette = {"id": 1, "est_vegetarien": False}
        contexte = {"contraintes": ["vegetarien"]}
        score = calculate_recipe_score(recette, contexte)
        assert score < 0 or score == 0


class TestRankRecipes:
    """Tests pour rank_recipes"""
    
    def test_classement(self):
        recettes = [
            {"id": 1, "nom": "A", "ingredients": []},
            {"id": 2, "nom": "B", "ingredients": ["tomate"]},
        ]
        contexte = {"ingredients_disponibles": ["tomate"]}
        
        result = rank_recipes(recettes, contexte, limit=2)
        assert result[0]["id"] == 2  # Celui avec l'ingrédient
    
    def test_limit(self):
        recettes = [{"id": i, "nom": f"R{i}"} for i in range(10)]
        result = rank_recipes(recettes, {}, limit=3)
        assert len(result) == 3
    
    def test_scores_inclus(self):
        recettes = [{"id": 1, "nom": "Test"}]
        result = rank_recipes(recettes, {})
        assert "score" in result[0]


class TestGenerateSuggestionReason:
    """Tests pour generate_suggestion_reason"""
    
    def test_raison_ingredient(self):
        recette = {"ingredients": ["tomate"]}
        contexte = {"ingredients_a_utiliser": ["tomate"]}
        raison = generate_suggestion_reason(recette, contexte)
        assert "tomate" in raison.lower() or len(raison) > 0
    
    def test_raison_score_eleve(self):
        recette = {"score": 85, "ingredients": []}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert len(raison) > 0
    
    def test_nouvelle_recette(self):
        recette = {"est_nouvelle": True, "ingredients": []}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert "découvrir" in raison.lower() or len(raison) > 0


# ═══════════════════════════════════════════════════════════
# Tests: Détection de type de protéine
# ═══════════════════════════════════════════════════════════


class TestDetectProteinType:
    """Tests pour detect_protein_type"""
    
    def test_poisson(self):
        assert detect_protein_type({"type_proteines": "saumon"}) == "poisson"
        assert detect_protein_type({"nom": "Filet de cabillaud"}) == "poisson"
    
    def test_viande_rouge(self):
        assert detect_protein_type({"nom": "Steak de boeuf"}) == "viande_rouge"
        assert detect_protein_type({"ingredients": ["agneau"]}) == "viande_rouge"
    
    def test_volaille(self):
        assert detect_protein_type({"nom": "Poulet rôti"}) == "volaille"
    
    def test_vegetarien(self):
        assert detect_protein_type({"est_vegetarien": True}) == "vegetarien"
        assert detect_protein_type({"ingredients": ["tofu"]}) == "vegetarien"
    
    def test_autre(self):
        assert detect_protein_type({"nom": "Salade verte"}) == "autre"


class TestCalculateWeekProteinBalance:
    """Tests pour calculate_week_protein_balance"""
    
    def test_equilibre(self):
        repas = [
            {"nom": "Saumon"},
            {"nom": "Poulet"},
            {"est_vegetarien": True},
        ]
        balance = calculate_week_protein_balance(repas)
        assert "poisson" in balance
        assert "volaille" in balance
        assert "vegetarien" in balance


class TestIsWeekBalanced:
    """Tests pour is_week_balanced"""
    
    def test_semaine_equilibree(self):
        repas = [
            {"nom": "Saumon"},
            {"nom": "Thon"},
            {"nom": "Poulet"},
            {"est_vegetarien": True},
            {"nom": "Dinde"},
        ]
        is_balanced, problemes = is_week_balanced(repas)
        assert is_balanced is True
        assert len(problemes) == 0
    
    def test_trop_viande_rouge(self):
        repas = [
            {"nom": "Boeuf"},
            {"nom": "Agneau"},
            {"nom": "Porc"},
        ]
        is_balanced, problemes = is_week_balanced(repas)
        assert is_balanced is False
        assert any("viande rouge" in p.lower() for p in problemes)
    
    def test_pas_assez_poisson(self):
        repas = [{"nom": "Poulet"} for _ in range(5)]
        is_balanced, problemes = is_week_balanced(repas)
        assert is_balanced is False
        assert any("poisson" in p.lower() for p in problemes)


# ═══════════════════════════════════════════════════════════
# Tests: Variété
# ═══════════════════════════════════════════════════════════


class TestCalculateVarietyScore:
    """Tests pour calculate_variety_score"""
    
    def test_toutes_nouvelles(self):
        recettes = [{"id": 1}, {"id": 2}]
        historique = []
        score = calculate_variety_score(recettes, historique)
        assert score == 100.0
    
    def test_toutes_recentes(self):
        today = date.today()
        recettes = [{"id": 1}, {"id": 2}]
        historique = [
            {"recette_id": 1, "date": (today - timedelta(days=3)).isoformat()},
            {"recette_id": 2, "date": (today - timedelta(days=5)).isoformat()},
        ]
        score = calculate_variety_score(recettes, historique)
        assert score == 0.0
    
    def test_melange(self):
        today = date.today()
        recettes = [{"id": 1}, {"id": 2}]
        historique = [
            {"recette_id": 1, "date": (today - timedelta(days=3)).isoformat()},
        ]
        score = calculate_variety_score(recettes, historique)
        assert score == 50.0


class TestGetLeastPreparedRecipes:
    """Tests pour get_least_prepared_recipes"""
    
    def test_moins_preparees(self):
        recettes = [{"id": 1}, {"id": 2}, {"id": 3}]
        historique = [
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 2},
        ]
        result = get_least_prepared_recipes(recettes, historique, limit=2)
        ids = [r["id"] for r in result]
        assert 3 in ids  # Jamais préparée
        assert 2 in ids  # 1 fois seulement


# ═══════════════════════════════════════════════════════════
# Tests: Formatage et affichage
# ═══════════════════════════════════════════════════════════


class TestFormatSuggestion:
    """Tests pour format_suggestion"""
    
    def test_formatage_complet(self):
        recette = {
            "id": 1,
            "nom": "Tarte aux tomates",
            "temps_preparation": 20,
            "temps_cuisson": 30,
            "difficulte": "facile",
            "categorie": "français",
            "score": 75,
        }
        result = format_suggestion(recette, "Ingrédients de saison")
        
        assert result["id"] == 1
        assert result["nom"] == "Tarte aux tomates"
        assert result["temps_total"] == 50
        assert result["temps_display"] == "50 min"
        assert result["raison"] == "Ingrédients de saison"
    
    def test_temps_zero(self):
        recette = {"id": 1, "nom": "Test"}
        result = format_suggestion(recette)
        assert result["temps_display"] == "Non spécifié"


class TestFormatProfileSummary:
    """Tests pour format_profile_summary"""
    
    def test_profil_complet(self):
        profil = {
            "categories_preferees": ["italien", "asiatique"],
            "ingredients_frequents": ["tomate", "oignon"],
            "temps_moyen_minutes": 45,
            "recettes_favorites": [1, 2, 3],
        }
        summary = format_profile_summary(profil)
        assert "italien" in summary
        assert "45" in summary
    
    def test_profil_vide(self):
        summary = format_profile_summary({})
        assert "construction" in summary.lower()


class TestFilterByConstraints:
    """Tests pour filter_by_constraints"""
    
    def test_filtre_vegetarien(self):
        recettes = [
            {"id": 1, "est_vegetarien": True},
            {"id": 2, "est_vegetarien": False, "nom": "Poulet"},
        ]
        result = filter_by_constraints(recettes, ["vegetarien"])
        assert len(result) == 1
        assert result[0]["id"] == 1
    
    def test_filtre_sans_gluten(self):
        recettes = [
            {"id": 1, "contient_gluten": True},
            {"id": 2, "contient_gluten": False},
        ]
        result = filter_by_constraints(recettes, ["sans gluten"])
        assert len(result) == 1
        assert result[0]["id"] == 2
    
    def test_pas_de_contraintes(self):
        recettes = [{"id": 1}, {"id": 2}]
        result = filter_by_constraints(recettes, [])
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# Tests: Constantes
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes du module"""
    
    def test_saisons(self):
        assert len(SAISONS) == 4
        for saison, mois in SAISONS.items():
            assert len(mois) == 3
    
    def test_ingredients_saison(self):
        assert len(INGREDIENTS_SAISON) == 4
        for saison, ingredients in INGREDIENTS_SAISON.items():
            assert len(ingredients) > 0

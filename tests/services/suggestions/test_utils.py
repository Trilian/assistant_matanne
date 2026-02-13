"""
Tests for src/services/suggestions/utils.py

Pure utility functions - no mocking needed.
"""

from datetime import date, datetime

from src.services.suggestions.utils import (
    SCORE_CATEGORIE_PREFEREE,
    SCORE_DIFFICULTE_ADAPTEE,
    SCORE_INGREDIENT_DISPONIBLE,
    SCORE_INGREDIENT_PRIORITAIRE,
    SCORE_INGREDIENT_SAISON,
    SCORE_JAMAIS_PREPAREE,
    SCORE_TEMPS_ADAPTE,
    SCORE_VARIETE,
    # Profil
    analyze_categories,
    analyze_frequent_ingredients,
    calculate_average_difficulty,
    calculate_average_portions,
    calculate_average_time,
    # Scoring
    calculate_recipe_score,
    calculate_variety_score,
    calculate_week_protein_balance,
    days_since_last_preparation,
    # Protéines
    detect_protein_type,
    filter_by_constraints,
    format_profile_summary,
    # Formatage
    format_suggestion,
    generate_suggestion_reason,
    # Saisons
    get_current_season,
    get_least_prepared_recipes,
    get_seasonal_ingredients,
    identify_favorites,
    is_ingredient_in_season,
    is_week_balanced,
    rank_recipes,
)


class TestSaisons:
    """Tests pour les fonctions de saison."""

    def test_get_current_season_printemps(self):
        """Test saison printemps."""
        assert get_current_season(date(2024, 4, 15)) == "printemps"
        assert get_current_season(date(2024, 3, 1)) == "printemps"
        assert get_current_season(date(2024, 5, 31)) == "printemps"

    def test_get_current_season_ete(self):
        """Test saison été."""
        assert get_current_season(date(2024, 7, 15)) == "été"
        assert get_current_season(date(2024, 6, 1)) == "été"
        assert get_current_season(date(2024, 8, 31)) == "été"

    def test_get_current_season_automne(self):
        """Test saison automne."""
        assert get_current_season(date(2024, 10, 15)) == "automne"
        assert get_current_season(date(2024, 9, 1)) == "automne"
        assert get_current_season(date(2024, 11, 30)) == "automne"

    def test_get_current_season_hiver(self):
        """Test saison hiver."""
        assert get_current_season(date(2024, 12, 15)) == "hiver"
        assert get_current_season(date(2024, 1, 15)) == "hiver"
        assert get_current_season(date(2024, 2, 28)) == "hiver"

    def test_get_current_season_default(self):
        """Test avec None utilise date d'aujourd'hui."""
        result = get_current_season(None)
        assert result in ["printemps", "été", "automne", "hiver"]

    def test_get_current_season_datetime_input(self):
        """Test avec datetime au lieu de date."""
        result = get_current_season(datetime(2024, 7, 15, 12, 30))
        assert result == "été"

    def test_get_seasonal_ingredients_ete(self):
        """Test ingrédients d'été."""
        ingredients = get_seasonal_ingredients("été")
        assert "tomate" in ingredients
        assert "courgette" in ingredients
        assert "melon" in ingredients

    def test_get_seasonal_ingredients_hiver(self):
        """Test ingrédients d'hiver."""
        ingredients = get_seasonal_ingredients("hiver")
        assert "endive" in ingredients
        assert "orange" in ingredients

    def test_get_seasonal_ingredients_automne(self):
        """Test ingrédients d'automne."""
        ingredients = get_seasonal_ingredients("automne")
        assert "champignon" in ingredients
        assert "potiron" in ingredients

    def test_get_seasonal_ingredients_printemps(self):
        """Test ingrédients de printemps."""
        ingredients = get_seasonal_ingredients("printemps")
        assert "asperge" in ingredients
        assert "radis" in ingredients

    def test_get_seasonal_ingredients_none(self):
        """Test sans saison spécifiée."""
        result = get_seasonal_ingredients(None)
        assert isinstance(result, list)

    def test_get_seasonal_ingredients_normalized(self):
        """Test normalisation des accents."""
        result = get_seasonal_ingredients("ete")
        assert "tomate" in result

    def test_get_seasonal_ingredients_unknown(self):
        """Test saison inconnue retourne liste vide."""
        result = get_seasonal_ingredients("inconnu")
        assert result == []

    def test_is_ingredient_in_season_true(self):
        """Test ingrédient de saison."""
        assert is_ingredient_in_season("tomate", "été") is True
        assert is_ingredient_in_season("Tomate fraîche", "été") is True

    def test_is_ingredient_in_season_false(self):
        """Test ingrédient hors saison."""
        assert is_ingredient_in_season("tomate", "hiver") is False

    def test_is_ingredient_in_season_partial_match(self):
        """Test correspondance partielle."""
        assert is_ingredient_in_season("aubergine grillée", "été") is True


class TestProfilAnalysis:
    """Tests pour l'analyse du profil culinaire."""

    def test_analyze_categories(self):
        """Test analyse des catégories."""
        historique = [
            {"categorie": "italien"},
            {"categorie": "italien"},
            {"categorie": "français"},
            {"categorie": "italien"},
            {"categorie": "asiatique"},
        ]
        result = analyze_categories(historique)
        assert result[0] == "italien"
        assert len(result) <= 5

    def test_analyze_categories_empty(self):
        """Test avec historique vide."""
        assert analyze_categories([]) == []

    def test_analyze_categories_no_category(self):
        """Test avec entrées sans catégorie."""
        historique = [{"autre": "valeur"}, {}]
        assert analyze_categories(historique) == []

    def test_analyze_frequent_ingredients(self):
        """Test analyse des ingrédients fréquents."""
        historique = [
            {"ingredients": ["tomate", "oignon", "ail"]},
            {"ingredients": ["tomate", "basilic"]},
            {"ingredients": ["tomate"]},
        ]
        result = analyze_frequent_ingredients(historique)
        assert result[0] == "tomate"
        assert len(result) <= 10

    def test_analyze_frequent_ingredients_empty(self):
        """Test avec historique vide."""
        assert analyze_frequent_ingredients([]) == []

    def test_analyze_frequent_ingredients_no_ingredients(self):
        """Test entrées sans ingrédients."""
        historique = [{"autre": "valeur"}, {"ingredients": None}]
        assert analyze_frequent_ingredients(historique) == []

    def test_calculate_average_difficulty(self):
        """Test calcul difficulté moyenne."""
        historique = [
            {"difficulte": "facile"},
            {"difficulte": "facile"},
            {"difficulte": "moyen"},
        ]
        assert calculate_average_difficulty(historique) == "facile"

    def test_calculate_average_difficulty_empty(self):
        """Test avec historique vide."""
        assert calculate_average_difficulty([]) == "moyen"

    def test_calculate_average_time(self):
        """Test calcul temps moyen."""
        historique = [
            {"temps_preparation": 30},
            {"temps_preparation": 60},
            {"temps_preparation": 45},
        ]
        assert calculate_average_time(historique) == 45

    def test_calculate_average_time_empty(self):
        """Test temps par défaut."""
        assert calculate_average_time([]) == 45

    def test_calculate_average_time_missing(self):
        """Test avec temps manquants."""
        historique = [{"temps_preparation": 0}, {"autre": 1}]
        assert calculate_average_time(historique) == 45

    def test_calculate_average_portions(self):
        """Test calcul portions moyennes."""
        historique = [
            {"portions": 4},
            {"portions": 6},
            {"portions": 2},
        ]
        assert calculate_average_portions(historique) == 4

    def test_calculate_average_portions_empty(self):
        """Test portions par défaut."""
        assert calculate_average_portions([]) == 4

    def test_identify_favorites(self):
        """Test identification des favoris."""
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

    def test_identify_favorites_empty(self):
        """Test avec historique vide."""
        assert identify_favorites([]) == []

    def test_days_since_last_preparation(self):
        """Test calcul jours depuis dernière préparation."""
        today = date(2024, 7, 15)
        historique = [
            {"recette_id": 1, "date": date(2024, 7, 10)},
            {"recette_id": 1, "date": date(2024, 7, 5)},
            {"recette_id": 2, "date": date(2024, 7, 1)},
        ]
        assert days_since_last_preparation(1, historique, today) == 5
        assert days_since_last_preparation(2, historique, today) == 14

    def test_days_since_last_preparation_never(self):
        """Test recette jamais préparée."""
        historique = [{"recette_id": 1, "date": date(2024, 7, 10)}]
        assert days_since_last_preparation(99, historique) is None

    def test_days_since_last_preparation_datetime_input(self):
        """Test avec datetime."""
        today = date(2024, 7, 15)
        historique = [
            {"recette_id": 1, "date": datetime(2024, 7, 10, 12, 0)},
        ]
        assert days_since_last_preparation(1, historique, today) == 5

    def test_days_since_last_preparation_string_date(self):
        """Test avec date en string."""
        today = date(2024, 7, 15)
        historique = [
            {"recette_id": 1, "date": "2024-07-10"},
        ]
        assert days_since_last_preparation(1, historique, today) == 5

    def test_days_since_last_preparation_date_cuisson(self):
        """Test avec clé date_cuisson."""
        today = date(2024, 7, 15)
        historique = [
            {"recette_id": 1, "date_cuisson": date(2024, 7, 13)},
        ]
        assert days_since_last_preparation(1, historique, today) == 2

    def test_days_since_last_preparation_invalid_string(self):
        """Test avec string invalide."""
        historique = [
            {"recette_id": 1, "date": "invalid-date"},
        ]
        assert days_since_last_preparation(1, historique) is None


class TestScoring:
    """Tests pour le scoring des recettes."""

    def test_calculate_recipe_score_basic(self):
        """Test score basique."""
        recette = {"id": 1, "nom": "Test", "ingredients": ["tomate"]}
        contexte = {"ingredients_disponibles": ["tomate"]}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_INGREDIENT_DISPONIBLE

    def test_calculate_recipe_score_prioritaire(self):
        """Test score avec ingrédient prioritaire."""
        recette = {"id": 1, "ingredients": ["tomate"]}
        contexte = {
            "ingredients_disponibles": ["tomate"],
            "ingredients_a_utiliser": ["tomate"],
        }
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_INGREDIENT_PRIORITAIRE

    def test_calculate_recipe_score_saison(self):
        """Test score saison."""
        recette = {"id": 1, "ingredients": ["tomate"]}
        contexte = {"saison": "été"}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_INGREDIENT_SAISON

    def test_calculate_recipe_score_categorie_preferee(self):
        """Test score catégorie préférée."""
        recette = {"id": 1, "categorie": "italien", "ingredients": []}
        contexte = {}
        profil = {"categories_preferees": ["italien"]}
        score = calculate_recipe_score(recette, contexte, profil)
        assert score >= SCORE_CATEGORIE_PREFEREE

    def test_calculate_recipe_score_temps_adapte(self):
        """Test score temps adapté."""
        recette = {"id": 1, "temps_preparation": 30, "temps_cuisson": 15, "ingredients": []}
        contexte = {"temps_disponible_minutes": 60}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_TEMPS_ADAPTE

    def test_calculate_recipe_score_temps_trop_long(self):
        """Test pénalité temps trop long."""
        recette = {"id": 1, "temps_preparation": 90, "temps_cuisson": 60, "ingredients": []}
        contexte = {"temps_disponible_minutes": 30}
        score = calculate_recipe_score(recette, contexte)
        assert score <= 0  # Pénalité (score est cappé à 0 minimum)

    def test_calculate_recipe_score_difficulte_adaptee(self):
        """Test score difficulté adaptée."""
        recette = {"id": 1, "difficulte": "facile", "ingredients": []}
        contexte = {}
        profil = {"difficulte_moyenne": "facile"}
        score = calculate_recipe_score(recette, contexte, profil)
        assert score >= SCORE_DIFFICULTE_ADAPTEE

    def test_calculate_recipe_score_jamais_preparee(self):
        """Test score recette jamais préparée."""
        recette = {"id": 99, "ingredients": []}
        contexte = {}
        historique = [{"recette_id": 1, "date": date(2024, 7, 10)}]
        score = calculate_recipe_score(recette, contexte, None, historique)
        assert score >= SCORE_JAMAIS_PREPAREE

    def test_calculate_recipe_score_variete(self):
        """Test score variété (pas préparée récemment)."""
        recette = {"id": 1, "ingredients": []}
        contexte = {}
        historique = [{"recette_id": 1, "date": date(2024, 1, 1)}]  # Très ancien
        score = calculate_recipe_score(recette, contexte, None, historique)
        assert score >= SCORE_VARIETE

    def test_calculate_recipe_score_contrainte_vegetarien(self):
        """Test pénalité contrainte végétarien non respectée."""
        recette = {"id": 1, "ingredients": ["poulet"], "est_vegetarien": False}
        contexte = {"contraintes": ["vegetarien"]}
        score = calculate_recipe_score(recette, contexte)
        assert score <= 0

    def test_calculate_recipe_score_contrainte_sans_gluten(self):
        """Test pénalité contrainte sans gluten non respectée."""
        recette = {"id": 1, "ingredients": [], "contient_gluten": True}
        contexte = {"contraintes": ["sans gluten"]}
        score = calculate_recipe_score(recette, contexte)
        assert score <= 0

    def test_calculate_recipe_score_ingredients_string(self):
        """Test avec ingrédients en string."""
        recette = {"id": 1, "ingredients": "tomate"}
        contexte = {"ingredients_disponibles": ["tomate"]}
        score = calculate_recipe_score(recette, contexte)
        assert score >= SCORE_INGREDIENT_DISPONIBLE

    def test_rank_recipes(self):
        """Test classement des recettes."""
        recettes = [
            {"id": 1, "ingredients": []},
            {"id": 2, "ingredients": ["tomate"]},
            {"id": 3, "ingredients": ["tomate", "oignon"]},
        ]
        contexte = {"ingredients_disponibles": ["tomate", "oignon"]}
        ranked = rank_recipes(recettes, contexte, limit=2)
        assert len(ranked) == 2
        assert ranked[0]["score"] >= ranked[1]["score"]

    def test_rank_recipes_with_profil(self):
        """Test classement avec profil."""
        recettes = [
            {"id": 1, "categorie": "autre", "ingredients": []},
            {"id": 2, "categorie": "italien", "ingredients": []},
        ]
        contexte = {}
        profil = {"categories_preferees": ["italien"]}
        ranked = rank_recipes(recettes, contexte, profil, limit=5)
        assert ranked[0]["categorie"] == "italien"

    def test_generate_suggestion_reason_priority(self):
        """Test génération raison priorité."""
        recette = {"ingredients": ["tomate"], "score": 90}
        contexte = {"ingredients_a_utiliser": ["tomate"]}
        raison = generate_suggestion_reason(recette, contexte)
        assert "tomate" in raison.lower() or "préférences" in raison.lower()

    def test_generate_suggestion_reason_saison(self):
        """Test génération raison saison."""
        recette = {"ingredients": ["tomate"], "score": 60}
        contexte = {"saison": "été"}
        raison = generate_suggestion_reason(recette, contexte)
        assert "saison" in raison.lower() or "correspond" in raison.lower()

    def test_generate_suggestion_reason_high_score(self):
        """Test raison score élevé."""
        recette = {"ingredients": [], "score": 85}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert "préférences" in raison.lower()

    def test_generate_suggestion_reason_nouvelle(self):
        """Test raison recette nouvelle."""
        recette = {"ingredients": [], "est_nouvelle": True, "score": 50}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert "découvrir" in raison.lower()

    def test_generate_suggestion_reason_default(self):
        """Test raison par défaut."""
        recette = {"ingredients": [], "score": 30}
        contexte = {}
        raison = generate_suggestion_reason(recette, contexte)
        assert "profil" in raison.lower()


class TestProteinDetection:
    """Tests pour la détection de type de protéine."""

    def test_detect_protein_type_poisson(self):
        """Test détection poisson."""
        recette = {"type_proteines": "saumon"}
        assert detect_protein_type(recette) == "poisson"

    def test_detect_protein_type_viande_rouge(self):
        """Test détection viande rouge."""
        recette = {"nom": "Steak de boeuf"}
        assert detect_protein_type(recette) == "viande_rouge"

    def test_detect_protein_type_volaille(self):
        """Test détection volaille."""
        recette = {"description": "Un délicieux poulet rôti"}
        assert detect_protein_type(recette) == "volaille"

    def test_detect_protein_type_vegetarien_explicit(self):
        """Test végétarien explicite."""
        recette = {"est_vegetarien": True}
        assert detect_protein_type(recette) == "vegetarien"

    def test_detect_protein_type_vegetarien_ingredients(self):
        """Test végétarien par ingrédients."""
        recette = {"ingredients": ["tofu", "légumes"]}
        assert detect_protein_type(recette) == "vegetarien"

    def test_detect_protein_type_autre(self):
        """Test autre (non identifié)."""
        recette = {"nom": "Salade verte"}
        assert detect_protein_type(recette) == "autre"

    def test_detect_protein_type_type_proteines_field(self):
        """Test avec champ type_proteines."""
        assert detect_protein_type({"type_proteines": "thon"}) == "poisson"
        assert detect_protein_type({"type_proteines": "agneau"}) == "viande_rouge"
        assert detect_protein_type({"type_proteines": "dinde"}) == "volaille"
        assert detect_protein_type({"type_proteines": "lentille"}) == "vegetarien"

    def test_calculate_week_protein_balance(self):
        """Test calcul équilibre protéique."""
        repas = [
            {"nom": "Saumon"},
            {"nom": "Poulet"},
            {"nom": "Boeuf"},
            {"est_vegetarien": True},
        ]
        balance = calculate_week_protein_balance(repas)
        assert balance["poisson"] == 1
        assert balance["volaille"] == 1
        assert balance["viande_rouge"] == 1
        assert balance["vegetarien"] == 1

    def test_is_week_balanced_true(self):
        """Test semaine équilibrée."""
        repas = [
            {"nom": "Saumon"},
            {"nom": "Thon"},  # 2 poissons
            {"nom": "Poulet"},
            {"nom": "Dinde"},  # 2 volailles
            {"nom": "Boeuf"},  # 1 viande rouge
            {"est_vegetarien": True},  # 1 végétarien
            {"nom": "Salade"},  # autre
        ]
        balanced, problemes = is_week_balanced(repas)
        assert balanced is True
        assert len(problemes) == 0

    def test_is_week_balanced_false_no_fish(self):
        """Test semaine non équilibrée - pas de poisson."""
        repas = [
            {"nom": "Poulet"},
            {"est_vegetarien": True},
        ]
        balanced, problemes = is_week_balanced(repas)
        assert balanced is False
        assert any("poisson" in p.lower() for p in problemes)

    def test_is_week_balanced_false_too_much_red_meat(self):
        """Test semaine non équilibrée - trop de viande rouge."""
        repas = [
            {"nom": "Saumon"},
            {"nom": "Thon"},
            {"nom": "Boeuf"},
            {"nom": "Agneau"},
            {"nom": "Veau"},
            {"est_vegetarien": True},
        ]
        balanced, problemes = is_week_balanced(repas)
        assert balanced is False
        assert any("viande rouge" in p.lower() for p in problemes)

    def test_is_week_balanced_false_no_vegetarian(self):
        """Test semaine non équilibrée - pas de végétarien."""
        repas = [
            {"nom": "Saumon"},
            {"nom": "Thon"},
            {"nom": "Poulet"},
            {"nom": "Dinde"},
        ]
        balanced, problemes = is_week_balanced(repas)
        assert balanced is False
        assert any("végétarien" in p.lower() for p in problemes)


class TestVariete:
    """Tests pour le calcul de variété."""

    def test_calculate_variety_score_all_new(self):
        """Test score variété - toutes nouvelles."""
        recettes = [{"id": 1}, {"id": 2}, {"id": 3}]
        historique = []
        score = calculate_variety_score(recettes, historique)
        assert score == 100.0

    def test_calculate_variety_score_all_recent(self):
        """Test score variété - toutes récentes."""
        recettes = [{"id": 1}, {"id": 2}]
        historique = [
            {"recette_id": 1, "date": date.today()},
            {"recette_id": 2, "date": date.today()},
        ]
        score = calculate_variety_score(recettes, historique)
        assert score == 0.0

    def test_calculate_variety_score_mixed(self):
        """Test score variété - mixte."""
        recettes = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
        historique = [
            {"recette_id": 1, "date": date.today()},
            {"recette_id": 2, "date": date.today()},
        ]
        score = calculate_variety_score(recettes, historique)
        assert score == 50.0

    def test_calculate_variety_score_empty(self):
        """Test score variété - liste vide."""
        score = calculate_variety_score([], [])
        assert score == 100.0

    def test_calculate_variety_score_old_history(self):
        """Test score variété - historique ancien."""
        recettes = [{"id": 1}]
        historique = [
            {"recette_id": 1, "date": date(2020, 1, 1)},  # Très ancien
        ]
        score = calculate_variety_score(recettes, historique, jours_reference=14)
        assert score == 100.0

    def test_get_least_prepared_recipes(self):
        """Test recettes les moins préparées."""
        recettes = [{"id": 1}, {"id": 2}, {"id": 3}]
        historique = [
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 1},
            {"recette_id": 2},
        ]
        result = get_least_prepared_recipes(recettes, historique, limit=2)
        assert result[0]["id"] == 3  # Jamais préparée
        assert len(result) == 2


class TestFormatage:
    """Tests pour les fonctions de formatage."""

    def test_format_suggestion(self):
        """Test formatage suggestion."""
        recette = {
            "id": 1,
            "nom": "Pâtes carbonara",
            "temps_preparation": 15,
            "temps_cuisson": 20,
            "difficulte": "facile",
            "categorie": "italien",
            "score": 85,
        }
        result = format_suggestion(recette, "Recette rapide")
        assert result["nom"] == "Pâtes carbonara"
        assert result["raison"] == "Recette rapide"
        assert result["temps_total"] == 35
        assert result["temps_display"] == "35 min"
        assert result["difficulte"] == "facile"
        assert result["protein_type"] == "autre"

    def test_format_suggestion_no_time(self):
        """Test formatage sans temps."""
        recette = {"id": 1, "nom": "Test"}
        result = format_suggestion(recette)
        assert result["temps_display"] == "Non spécifié"

    def test_format_profile_summary(self):
        """Test résumé du profil."""
        profil = {
            "categories_preferees": ["italien", "français", "asiatique"],
            "ingredients_frequents": ["tomate", "oignon", "ail"],
            "temps_moyen_minutes": 45,
            "recettes_favorites": [1, 2, 3],
        }
        summary = format_profile_summary(profil)
        assert "italien" in summary
        assert "tomate" in summary
        assert "45 min" in summary
        assert "3 recettes" in summary

    def test_format_profile_summary_empty(self):
        """Test résumé profil vide."""
        summary = format_profile_summary({})
        assert "en cours de construction" in summary

    def test_filter_by_constraints_none(self):
        """Test filtrage sans contraintes."""
        recettes = [{"id": 1}, {"id": 2}]
        result = filter_by_constraints(recettes, [])
        assert len(result) == 2

    def test_filter_by_constraints_vegetarien(self):
        """Test filtrage végétarien."""
        recettes = [
            {"id": 1, "est_vegetarien": True},
            {"id": 2, "nom": "Boeuf"},  # Contient viande rouge
            {"id": 3, "nom": "Salade"},  # Autre
        ]
        result = filter_by_constraints(recettes, ["vegetarien"])
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 3

    def test_filter_by_constraints_vegan(self):
        """Test filtrage vegan."""
        recettes = [
            {"id": 1, "est_vegan": True},
            {"id": 2, "est_vegan": False},
        ]
        result = filter_by_constraints(recettes, ["vegan"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_filter_by_constraints_sans_gluten(self):
        """Test filtrage sans gluten."""
        recettes = [
            {"id": 1, "contient_gluten": False},
            {"id": 2, "contient_gluten": True},
        ]
        result = filter_by_constraints(recettes, ["sans gluten"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_filter_by_constraints_sans_lactose(self):
        """Test filtrage sans lactose."""
        recettes = [
            {"id": 1, "contient_lactose": False},
            {"id": 2, "contient_lactose": True},
        ]
        result = filter_by_constraints(recettes, ["sans lactose"])
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_filter_by_constraints_multiple(self):
        """Test filtrage contraintes multiples."""
        recettes = [
            {"id": 1, "est_vegetarien": True, "contient_gluten": False},
            {"id": 2, "est_vegetarien": True, "contient_gluten": True},
            {
                "id": 3,
                "nom": "Boeuf grillé",
                "est_vegetarien": False,
                "contient_gluten": False,
            },  # Contient viande
        ]
        result = filter_by_constraints(recettes, ["végétarien", "sans gluten"])
        assert len(result) == 1
        assert result[0]["id"] == 1

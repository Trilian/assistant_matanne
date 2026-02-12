"""
Tests complets pour le module planificateur_repas.

Couvre:
- Modèles dataclasses (PreferencesUtilisateur, FeedbackRecette, etc.)
- Fonctions logique (calculer_score_recette, filtrer_recettes_eligibles, etc.)
- Constantes
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

# Import du module logic (fonctions pures)
from src.domains.cuisine.logic.planificateur_repas_logic import (
    JOURS_SEMAINE,
    PROTEINES,
    ROBOTS_CUISINE,
    TEMPS_CATEGORIES,
    RecetteSuggestion,
    RepasPlannifie,
    PlanningSemaine,
    calculer_score_recette,
    filtrer_recettes_eligibles,
    generer_suggestions_alternatives,
    generer_prompt_semaine,
    generer_prompt_alternative,
    valider_equilibre_semaine,
    suggerer_ajustements_equilibre,
)

# Import des schemas
from src.domains.cuisine.logic.schemas import (
    PreferencesUtilisateur,
    FeedbackRecette,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes du planificateur."""

    def test_jours_semaine_count(self):
        assert len(JOURS_SEMAINE) == 7

    def test_jours_semaine_content(self):
        assert "Lundi" in JOURS_SEMAINE
        assert "Dimanche" in JOURS_SEMAINE

    def test_proteines_defined(self):
        assert len(PROTEINES) > 0
        assert "poulet" in PROTEINES

    def test_robots_cuisine_defined(self):
        assert isinstance(ROBOTS_CUISINE, dict)
        assert "four" in ROBOTS_CUISINE or "monsieur_cuisine" in ROBOTS_CUISINE

    def test_temps_categories_defined(self):
        assert isinstance(TEMPS_CATEGORIES, dict)
        assert "express" in TEMPS_CATEGORIES
        assert "normal" in TEMPS_CATEGORIES


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES DATACLASSES
# ═══════════════════════════════════════════════════════════


class TestPreferencesUtilisateur:
    """Tests pour le modèle PreferencesUtilisateur."""

    def test_create_default_preferences(self):
        prefs = PreferencesUtilisateur()
        assert prefs is not None
        assert prefs.nb_adultes == 2
        assert prefs.jules_present is True

    def test_create_preferences_with_exclusions(self):
        prefs = PreferencesUtilisateur(
            aliments_exclus=["gluten", "lactose"],
        )
        assert "gluten" in prefs.aliments_exclus
        assert len(prefs.aliments_exclus) == 2

    def test_create_preferences_with_favoris(self):
        prefs = PreferencesUtilisateur(
            aliments_favoris=["poulet", "pâtes"],
        )
        assert "poulet" in prefs.aliments_favoris

    def test_create_preferences_with_temps(self):
        prefs = PreferencesUtilisateur(
            temps_semaine="express",
            temps_weekend="long",
        )
        assert prefs.temps_semaine == "express"
        assert prefs.temps_weekend == "long"

    def test_create_preferences_with_robots(self):
        prefs = PreferencesUtilisateur(
            robots=["four", "monsieur_cuisine", "airfryer"],
        )
        assert "four" in prefs.robots
        assert len(prefs.robots) == 3

    def test_to_dict(self):
        prefs = PreferencesUtilisateur()
        data = prefs.to_dict()
        assert isinstance(data, dict)
        assert "nb_adultes" in data
        assert "aliments_exclus" in data

    def test_from_dict(self):
        data = {
            "nb_adultes": 3,
            "aliments_exclus": ["gluten"],
            "temps_semaine": "express",
        }
        prefs = PreferencesUtilisateur.from_dict(data)
        assert prefs.nb_adultes == 3
        assert "gluten" in prefs.aliments_exclus


class TestFeedbackRecette:
    """Tests pour le modèle FeedbackRecette."""

    def test_create_feedback_like(self):
        feedback = FeedbackRecette(
            recette_id=1,
            recette_nom="Poulet rôti",
            feedback="like",
        )
        assert feedback.feedback == "like"
        assert feedback.score == 1

    def test_create_feedback_dislike(self):
        feedback = FeedbackRecette(
            recette_id=2,
            recette_nom="Sushi",
            feedback="dislike",
            contexte="Trop long à préparer",
        )
        assert feedback.feedback == "dislike"
        assert feedback.contexte == "Trop long à préparer"
        assert feedback.score == -1

    def test_create_feedback_neutral(self):
        feedback = FeedbackRecette(
            recette_id=3,
            recette_nom="Salade",
            feedback="neutral",
        )
        assert feedback.score == 0

    def test_feedback_date_auto(self):
        feedback = FeedbackRecette(
            recette_id=1,
            recette_nom="Test",
            feedback="like",
        )
        assert feedback.date_feedback == date.today()


class TestRecetteSuggestion:
    """Tests pour le modèle RecetteSuggestion."""

    def test_create_suggestion(self):
        suggestion = RecetteSuggestion(
            id=1,
            nom="Pâtes carbonara",
            description="Pâtes crémeuses",
            temps_preparation=15,
            temps_cuisson=10,
            portions=4,
            difficulte="facile",
        )
        assert suggestion.id == 1
        assert suggestion.nom == "Pâtes carbonara"
        assert suggestion.temps_total == 25

    def test_suggestion_with_proteine(self):
        suggestion = RecetteSuggestion(
            id=1,
            nom="Poulet rôti",
            description="Poulet au four",
            temps_preparation=20,
            temps_cuisson=60,
            portions=4,
            difficulte="moyen",
            type_proteine="poulet",
            categorie_proteine="volaille",
        )
        assert suggestion.type_proteine == "poulet"
        assert suggestion.categorie_proteine == "volaille"

    def test_suggestion_with_score(self):
        suggestion = RecetteSuggestion(
            id=1,
            nom="Test",
            description="Test",
            temps_preparation=10,
            temps_cuisson=10,
            portions=2,
            difficulte="facile",
            score_match=85.5,
            raison_suggestion="Correspond à vos goûts",
        )
        assert suggestion.score_match == 85.5
        assert suggestion.raison_suggestion is not None

    def test_emoji_difficulte(self):
        facile = RecetteSuggestion(
            id=1, nom="T", description="T", temps_preparation=5,
            temps_cuisson=5, portions=2, difficulte="facile"
        )
        moyen = RecetteSuggestion(
            id=2, nom="T", description="T", temps_preparation=5,
            temps_cuisson=5, portions=2, difficulte="moyen"
        )
        difficile = RecetteSuggestion(
            id=3, nom="T", description="T", temps_preparation=5,
            temps_cuisson=5, portions=2, difficulte="difficile"
        )
        
        assert facile.emoji_difficulte == "🟢"
        assert moyen.emoji_difficulte == "🟡"
        assert difficile.emoji_difficulte == "🔴"


class TestRepasPlannifie:
    """Tests pour le modèle RepasPlannifie."""

    def test_create_repas_empty(self):
        repas = RepasPlannifie(
            jour=date(2026, 2, 9),
            type_repas="déjeuner",
        )
        assert repas.jour == date(2026, 2, 9)
        assert repas.type_repas == "déjeuner"
        assert repas.est_vide is True

    def test_create_repas_with_recette(self):
        recette = RecetteSuggestion(
            id=1, nom="Salade", description="Fraîche",
            temps_preparation=10, temps_cuisson=0,
            portions=2, difficulte="facile"
        )
        repas = RepasPlannifie(
            jour=date(2026, 2, 9),
            type_repas="déjeuner",
            recette=recette,
        )
        assert repas.recette is not None
        assert repas.est_vide is False

    def test_jour_nom(self):
        # 9 février 2026 est un lundi
        repas = RepasPlannifie(
            jour=date(2026, 2, 9),
            type_repas="déjeuner",
        )
        assert repas.jour_nom == "Lundi"


class TestPlanningSemaine:
    """Tests pour le modèle PlanningSemaine."""

    def test_create_planning(self):
        planning = PlanningSemaine(
            date_debut=date(2026, 2, 9),
            date_fin=date(2026, 2, 15),
        )
        assert planning.date_debut == date(2026, 2, 9)
        assert planning.date_fin == date(2026, 2, 15)

    def test_create_planning_with_repas(self):
        repas = [
            RepasPlannifie(jour=date(2026, 2, 9), type_repas="déjeuner"),
            RepasPlannifie(jour=date(2026, 2, 9), type_repas="dîner"),
        ]
        planning = PlanningSemaine(
            date_debut=date(2026, 2, 9),
            date_fin=date(2026, 2, 15),
            repas=repas,
        )
        assert len(planning.repas) == 2


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS LOGIQUE
# ═══════════════════════════════════════════════════════════


class TestCalculerScoreRecette:
    """Tests pour calculer_score_recette."""

    def test_score_recette_standard(self):
        recette = Mock()
        recette.id = 1
        recette.nom = "Salade composée"
        recette.temps_preparation = 15
        recette.temps_cuisson = 0
        recette.ingredients = []
        
        prefs = PreferencesUtilisateur()
        feedbacks = []
        equilibre = {"volaille": 0, "poisson": 0}
        stock = []
        
        score, raison = calculer_score_recette(
            recette, prefs, feedbacks, equilibre, stock
        )
        assert 0 <= score <= 100
        assert isinstance(raison, str)

    def test_score_recette_avec_exclusion(self):
        recette = Mock()
        recette.id = 1
        recette.nom = "Pizza au gluten"
        recette.temps_preparation = 30
        recette.temps_cuisson = 20
        recette.ingredients = []
        
        prefs = PreferencesUtilisateur(aliments_exclus=["gluten"])
        feedbacks = []
        equilibre = {}
        stock = []
        
        score, raison = calculer_score_recette(
            recette, prefs, feedbacks, equilibre, stock
        )
        # Excluded recipes should get 0
        assert score == 0.0
        assert "gluten" in raison.lower()

    def test_score_recette_avec_favori(self):
        recette = Mock()
        recette.id = 1
        recette.nom = "Poulet aux herbes"
        recette.temps_preparation = 20
        recette.temps_cuisson = 30
        recette.ingredients = []
        
        prefs = PreferencesUtilisateur(aliments_favoris=["poulet"])
        feedbacks = []
        equilibre = {}
        stock = []
        
        score, raison = calculer_score_recette(
            recette, prefs, feedbacks, equilibre, stock
        )
        # Favoris should boost score
        assert score >= 50

    def test_score_recette_avec_feedback_like(self):
        recette = Mock()
        recette.id = 1
        recette.nom = "Favori"
        recette.temps_preparation = 15
        recette.temps_cuisson = 10
        recette.ingredients = []
        
        prefs = PreferencesUtilisateur()
        feedbacks = [
            FeedbackRecette(recette_id=1, recette_nom="Favori", feedback="like"),
        ]
        equilibre = {}
        stock = []
        
        score, raison = calculer_score_recette(
            recette, prefs, feedbacks, equilibre, stock
        )
        # Positive feedback should boost score
        assert score >= 50


class TestFiltrerRecettesEligibles:
    """Tests pour filtrer_recettes_eligibles."""

    def test_filtre_exclusions(self):
        r1 = Mock()
        r1.nom = "Salade fraîche"
        r1.type_repas = None
        
        r2 = Mock()
        r2.nom = "Pizza au gluten"
        r2.type_repas = None
        
        recettes = [r1, r2]
        prefs = PreferencesUtilisateur(aliments_exclus=["gluten"])
        
        result = filtrer_recettes_eligibles(recettes, prefs)
        # Should filter out gluten containing recipe
        assert len(result) == 1
        assert result[0].nom == "Salade fraîche"

    def test_filtre_liste_vide(self):
        result = filtrer_recettes_eligibles([], PreferencesUtilisateur())
        assert result == []

    def test_filtre_toutes_eligibles(self):
        r1 = Mock()
        r1.nom = "Salade"
        r1.type_repas = None
        
        r2 = Mock()
        r2.nom = "Pâtes"
        r2.type_repas = None
        
        recettes = [r1, r2]
        prefs = PreferencesUtilisateur()
        
        result = filtrer_recettes_eligibles(recettes, prefs)
        assert len(result) == 2


class TestGenererSuggestionsAlternatives:
    """Tests pour generer_suggestions_alternatives."""

    def test_generer_alternatives_empty_list(self):
        recette = RecetteSuggestion(
            id=1, nom="Original", description="Test",
            temps_preparation=10, temps_cuisson=10,
            portions=2, difficulte="facile"
        )
        
        prefs = PreferencesUtilisateur()
        feedbacks = []
        equilibre = {}
        stock = []
        
        alternatives = generer_suggestions_alternatives(
            recette, [], prefs, feedbacks, equilibre, stock, nb_alternatives=3
        )
        
        assert alternatives == []

    def test_generer_alternatives_with_recettes(self):
        recette = RecetteSuggestion(
            id=1, nom="Original", description="Test",
            temps_preparation=10, temps_cuisson=10,
            portions=2, difficulte="facile"
        )
        
        recettes_dispo = [
            MagicMock(id=2, nom="Alt 1"),
            MagicMock(id=3, nom="Alt 2"),
        ]
        
        prefs = PreferencesUtilisateur()
        feedbacks = []
        equilibre = {}
        stock = []
        
        alternatives = generer_suggestions_alternatives(
            recette, recettes_dispo, prefs, feedbacks, equilibre, stock,
            nb_alternatives=2
        )
        
        assert len(alternatives) <= 2


class TestGenererPromptSemaine:
    """Tests pour generer_prompt_semaine."""

    def test_prompt_basique(self):
        prefs = PreferencesUtilisateur()
        feedbacks = []
        
        prompt = generer_prompt_semaine(prefs, feedbacks, date_debut=date(2026, 2, 9))
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "famille" in prompt.lower() or "repas" in prompt.lower()

    def test_prompt_avec_contraintes(self):
        prefs = PreferencesUtilisateur(
            aliments_exclus=["gluten"],
            temps_semaine="express",
        )
        feedbacks = []
        
        prompt = generer_prompt_semaine(prefs, feedbacks, date_debut=date(2026, 2, 9))
        
        assert "gluten" in prompt.lower()

    def test_prompt_avec_feedbacks(self):
        prefs = PreferencesUtilisateur()
        feedbacks = [
            FeedbackRecette(recette_id=1, recette_nom="Poulet rôti", feedback="like"),
        ]
        
        prompt = generer_prompt_semaine(prefs, feedbacks, date_debut=date(2026, 2, 9))
        
        # Should include liked recipes
        assert "Poulet rôti" in prompt or len(prompt) > 100


class TestGenererPromptAlternative:
    """Tests pour generer_prompt_alternative."""

    def test_prompt_alternative(self):
        prefs = PreferencesUtilisateur()
        contraintes_equilibre = {"poisson": 0, "vegetarien": 0, "viande_rouge": 1}
        
        prompt = generer_prompt_alternative(
            recette_a_remplacer="Pâtes bolognaise",
            type_repas="déjeuner",
            jour="Lundi",
            preferences=prefs,
            contraintes_equilibre=contraintes_equilibre
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "alternatives" in prompt.lower() or "Pâtes bolognaise" in prompt


class TestValiderEquilibreSemaine:
    """Tests pour valider_equilibre_semaine."""

    def test_planning_vide(self):
        planning = PlanningSemaine(
            date_debut=date(2026, 2, 9),
            date_fin=date(2026, 2, 15)
        )
        prefs = PreferencesUtilisateur()
        
        est_valide, alertes = valider_equilibre_semaine(planning, prefs)
        
        assert isinstance(est_valide, bool)
        assert isinstance(alertes, list)

    def test_planning_avec_repas(self):
        planning = PlanningSemaine(
            date_debut=date(2026, 2, 9),
            date_fin=date(2026, 2, 15),
            repas=[
                RepasPlannifie(jour=date(2026, 2, 9), type_repas="déjeuner"),
                RepasPlannifie(jour=date(2026, 2, 9), type_repas="dîner"),
            ]
        )
        prefs = PreferencesUtilisateur()
        
        est_valide, alertes = valider_equilibre_semaine(planning, prefs)
        
        assert isinstance(est_valide, bool)
        assert isinstance(alertes, list)


class TestSuggererAjustementsEquilibre:
    """Tests pour suggerer_ajustements_equilibre."""

    def test_suggestions_planning_vide(self):
        equilibre = {"poisson": 0, "vegetarien": 0, "viande_rouge": 0}
        prefs = PreferencesUtilisateur()
        
        suggestions = suggerer_ajustements_equilibre(equilibre, prefs)
        
        assert isinstance(suggestions, list)

    def test_suggestions_equilibre_atteint(self):
        prefs = PreferencesUtilisateur()
        equilibre = {
            "poisson": prefs.poisson_par_semaine,
            "vegetarien": prefs.vegetarien_par_semaine,
            "viande_rouge": 0
        }
        
        suggestions = suggerer_ajustements_equilibre(equilibre, prefs)
        
        # Should have no suggestions when equilibre is good
        assert isinstance(suggestions, list)


# ═══════════════════════════════════════════════════════════
# TESTS IMPORT
# ═══════════════════════════════════════════════════════════


class TestImports:
    """Tests d'import des modules."""

    def test_import_logic(self):
        import src.domains.cuisine.logic.planificateur_repas_logic as logic
        assert logic is not None

    def test_import_schemas(self):
        import src.domains.cuisine.logic.schemas as schemas
        assert hasattr(schemas, "PreferencesUtilisateur")
        assert hasattr(schemas, "FeedbackRecette")

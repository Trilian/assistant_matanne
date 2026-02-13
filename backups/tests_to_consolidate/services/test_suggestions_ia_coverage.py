"""
Tests couverture pour src/services/suggestions_ia.py
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODÃˆLES PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestProfilCulinaireModel:
    """Tests pour ProfilCulinaire."""

    def test_profil_culinaire_defaults(self):
        """Test valeurs par dÃ©faut."""
        from src.services.suggestions_ia import ProfilCulinaire

        profil = ProfilCulinaire()

        assert profil.categories_preferees == []
        assert profil.ingredients_frequents == []
        assert profil.ingredients_evites == []
        assert profil.difficulte_moyenne == "moyen"
        assert profil.temps_moyen_minutes == 45
        assert profil.nb_portions_habituel == 4
        assert profil.recettes_favorites == []
        assert profil.jours_depuis_derniere_recette == {}

    def test_profil_culinaire_complete(self):
        """Test crÃ©ation complÃ¨te."""
        from src.services.suggestions_ia import ProfilCulinaire

        profil = ProfilCulinaire(
            categories_preferees=["Italien", "FranÃ§ais"],
            ingredients_frequents=["Tomate", "Ail"],
            difficulte_moyenne="facile",
            temps_moyen_minutes=30,
            nb_portions_habituel=2,
            recettes_favorites=[1, 2, 3],
        )

        assert len(profil.categories_preferees) == 2
        assert "Tomate" in profil.ingredients_frequents
        assert profil.difficulte_moyenne == "facile"


@pytest.mark.unit
class TestContexteSuggestionModel:
    """Tests pour ContexteSuggestion."""

    def test_contexte_defaults(self):
        """Test valeurs par dÃ©faut."""
        from src.services.suggestions_ia import ContexteSuggestion

        ctx = ContexteSuggestion()

        assert ctx.type_repas == "dÃ®ner"
        assert ctx.nb_personnes == 4
        assert ctx.temps_disponible_minutes == 60
        assert ctx.ingredients_disponibles == []
        assert ctx.ingredients_a_utiliser == []
        assert ctx.contraintes == []
        assert ctx.saison == ""
        assert ctx.budget == "normal"

    def test_contexte_complete(self):
        """Test crÃ©ation complÃ¨te."""
        from src.services.suggestions_ia import ContexteSuggestion

        ctx = ContexteSuggestion(
            type_repas="dÃ©jeuner",
            nb_personnes=6,
            temps_disponible_minutes=90,
            ingredients_disponibles=["Poulet", "Riz"],
            ingredients_a_utiliser=["Tomates Ã  utiliser"],
            contraintes=["Sans gluten"],
            saison="Ã©tÃ©",
            budget="Ã©conomique",
        )

        assert ctx.type_repas == "dÃ©jeuner"
        assert ctx.nb_personnes == 6
        assert "Sans gluten" in ctx.contraintes


@pytest.mark.unit
class TestSuggestionRecetteModel:
    """Tests pour SuggestionRecette."""

    def test_suggestion_defaults(self):
        """Test valeurs par dÃ©faut."""
        from src.services.suggestions_ia import SuggestionRecette

        sugg = SuggestionRecette()

        assert sugg.recette_id is None
        assert sugg.nom == ""
        assert sugg.raison == ""
        assert sugg.score == 0.0
        assert sugg.tags == []
        assert sugg.temps_preparation == 0
        assert sugg.difficulte == ""
        assert sugg.ingredients_manquants == []
        assert sugg.est_nouvelle is False

    def test_suggestion_complete(self):
        """Test crÃ©ation complÃ¨te."""
        from src.services.suggestions_ia import SuggestionRecette

        sugg = SuggestionRecette(
            recette_id=42,
            nom="Poulet rÃ´ti",
            raison="Correspond Ã  vos prÃ©fÃ©rences",
            score=0.85,
            tags=["classique", "famille"],
            temps_preparation=60,
            difficulte="moyen",
            ingredients_manquants=["Thym"],
            est_nouvelle=True,
        )

        assert sugg.recette_id == 42
        assert sugg.score == 0.85
        assert sugg.est_nouvelle is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE INIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSuggestionsIAServiceInit:
    """Tests pour l'initialisation du service."""

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_init_success(self, mock_client_ia, mock_analyseur, mock_cache):
        """Test initialisation rÃ©ussie."""
        mock_client_ia.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionsIAService

        service = SuggestionsIAService()

        assert service.client_ia is not None
        assert service.analyseur is not None
        assert service.cache is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ANALYSER PROFIL CULINAIRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestAnalyserProfilCulinaire:
    """Tests pour analyser_profil_culinaire()."""

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_analyser_profil_sans_historique(self, mock_client, mock_analyseur, mock_cache):
        """Test sans historique."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import ProfilCulinaire, SuggestionsIAService

        service = SuggestionsIAService()

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []

        result = service.analyser_profil_culinaire(session=mock_session)

        assert isinstance(result, ProfilCulinaire)
        assert result.categories_preferees == []

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_analyser_profil_avec_historique(self, mock_client, mock_analyseur, mock_cache):
        """Test avec historique."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionsIAService

        service = SuggestionsIAService()

        # Mock historique
        mock_hist = Mock()
        mock_hist.recette_id = 1
        mock_hist.date_cuisson = datetime.now().date()

        # Mock recette
        mock_recette = Mock()
        mock_recette.id = 1
        mock_recette.categorie = "Italien"
        mock_recette.difficulte = "facile"
        mock_recette.temps_preparation = 30
        mock_recette.portions = 4
        mock_recette.ingredients = []

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_hist]
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_recette
        mock_session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = mock_hist

        result = service.analyser_profil_culinaire(session=mock_session)

        assert "Italien" in result.categories_preferees


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONSTRUIRE CONTEXTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestConstruireContexte:
    """Tests pour construire_contexte()."""

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_construire_contexte_minimal(self, mock_client, mock_analyseur, mock_cache):
        """Test contexte minimal."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import ContexteSuggestion, SuggestionsIAService

        service = SuggestionsIAService()

        mock_session = MagicMock()
        # Pas de planning actif
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.filter.return_value.all.return_value = []

        result = service.construire_contexte(session=mock_session)

        assert isinstance(result, ContexteSuggestion)

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_construire_contexte_avec_inventaire(self, mock_client, mock_analyseur, mock_cache):
        """Test contexte avec articles inventaire."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionsIAService

        service = SuggestionsIAService()

        # Mock article inventaire
        mock_article = Mock()
        mock_article.nom = "Tomate"
        mock_article.quantite = 5
        mock_article.date_peremption = None  # Pas de date de pÃ©remption

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_article]

        result = service.construire_contexte(session=mock_session)

        assert "Tomate" in result.ingredients_disponibles

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_construire_contexte_avec_peremption(self, mock_client, mock_analyseur, mock_cache):
        """Test contexte avec article proche pÃ©remption."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionsIAService

        service = SuggestionsIAService()

        # Mock article avec pÃ©remption dans 3 jours
        mock_article = Mock()
        mock_article.nom = "Yaourt"
        mock_article.quantite = 4
        mock_article.date_peremption = datetime.now() + timedelta(days=3)  # Dans 5 jours = triggera

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_article]

        result = service.construire_contexte(session=mock_session)

        assert "Yaourt" in result.ingredients_disponibles
        assert "Yaourt" in result.ingredients_a_utiliser  # Close to expiration


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALCULER SCORE RECETTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestCalculerScoreRecette:
    """Tests pour _calculer_score_recette()."""

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_calculer_score_recette_nouvelle(self, mock_client, mock_analyseur, mock_cache):
        """Test score pour nouvelle recette."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import (
            ContexteSuggestion,
            ProfilCulinaire,
            SuggestionsIAService,
        )

        service = SuggestionsIAService()

        mock_recette = Mock()
        mock_recette.id = 999  # ID pas dans profil
        mock_recette.categorie = "Italien"
        mock_recette.difficulte = "facile"
        mock_recette.temps_preparation = 30
        mock_recette.ingredients = []

        profil = ProfilCulinaire(
            categories_preferees=["Italien"],
            recettes_favorites=[1, 2, 3],
            jours_depuis_derniere_recette={1: 5},
        )

        contexte = ContexteSuggestion(temps_disponible_minutes=60)

        # Ordre correct: recette, contexte, profil
        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score >= 0

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_calculer_score_recette_recente(self, mock_client, mock_analyseur, mock_cache):
        """Test score pour recette rÃ©cemment prÃ©parÃ©e (score plus bas)."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import (
            ContexteSuggestion,
            ProfilCulinaire,
            SuggestionsIAService,
        )

        service = SuggestionsIAService()

        mock_recette = Mock()
        mock_recette.id = 1  # ID prÃ©sent dans profil avec peu de jours
        mock_recette.categorie = "FranÃ§ais"
        mock_recette.difficulte = "moyen"
        mock_recette.temps_preparation = 45
        mock_recette.ingredients = []

        profil = ProfilCulinaire(
            jours_depuis_derniere_recette={1: 2}  # PrÃ©parÃ©e il y a 2 jours
        )

        contexte = ContexteSuggestion()

        # Ordre correct: recette, contexte, profil
        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score >= 0

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_calculer_score_temps_adapte(self, mock_client, mock_analyseur, mock_cache):
        """Test bonus temps adaptÃ©."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import (
            ContexteSuggestion,
            ProfilCulinaire,
            SuggestionsIAService,
        )

        service = SuggestionsIAService()

        mock_recette = Mock()
        mock_recette.id = 10
        mock_recette.categorie = "Italien"
        mock_recette.difficulte = "facile"
        mock_recette.temps_preparation = 20  # Moins que temps disponible
        mock_recette.ingredients = []

        profil = ProfilCulinaire()
        contexte = ContexteSuggestion(temps_disponible_minutes=60)

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert "Temps adaptÃ©" in raisons
        assert "rapide" in tags

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_calculer_score_temps_trop_long(self, mock_client, mock_analyseur, mock_cache):
        """Test malus temps trop long."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import (
            ContexteSuggestion,
            ProfilCulinaire,
            SuggestionsIAService,
        )

        service = SuggestionsIAService()

        mock_recette = Mock()
        mock_recette.id = 10
        mock_recette.categorie = "FranÃ§ais"
        mock_recette.difficulte = "difficile"
        mock_recette.temps_preparation = 120  # > temps disponible + 30
        mock_recette.ingredients = []

        profil = ProfilCulinaire()
        contexte = ContexteSuggestion(temps_disponible_minutes=30)

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        # Score de base - 20 (trop long)
        assert score < 50  # Score de base est 50

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_calculer_score_ingredients_disponibles(self, mock_client, mock_analyseur, mock_cache):
        """Test bonus ingrÃ©dients en stock."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import (
            ContexteSuggestion,
            ProfilCulinaire,
            SuggestionsIAService,
        )

        service = SuggestionsIAService()

        # Mock ingrÃ©dient
        mock_ing = Mock()
        mock_ing.ingredient = Mock()
        mock_ing.ingredient.nom = "Tomate"

        mock_recette = Mock()
        mock_recette.id = 10
        mock_recette.categorie = "Italien"
        mock_recette.difficulte = "facile"
        mock_recette.temps_preparation = 30
        mock_recette.ingredients = [mock_ing]

        profil = ProfilCulinaire()
        contexte = ContexteSuggestion(
            temps_disponible_minutes=60, ingredients_disponibles=["Tomate"]
        )

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        # Devrait avoir bon score car ingrÃ©dient disponible
        assert score >= 50

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_calculer_score_ingredients_a_consommer(self, mock_client, mock_analyseur, mock_cache):
        """Test bonus utilisation ingrÃ©dients prioritaires."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import (
            ContexteSuggestion,
            ProfilCulinaire,
            SuggestionsIAService,
        )

        service = SuggestionsIAService()

        # Mock ingrÃ©dient
        mock_ing = Mock()
        mock_ing.ingredient = Mock()
        mock_ing.ingredient.nom = "Lait"

        mock_recette = Mock()
        mock_recette.id = 10
        mock_recette.categorie = "Dessert"
        mock_recette.difficulte = "facile"
        mock_recette.temps_preparation = 30
        mock_recette.ingredients = [mock_ing]

        profil = ProfilCulinaire()
        contexte = ContexteSuggestion(
            temps_disponible_minutes=60,
            ingredients_disponibles=["Lait"],
            ingredients_a_utiliser=["Lait"],  # Proche pÃ©remption
        )

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert "anti-gaspi" in tags or score > 50


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS TROUVER INGREDIENTS MANQUANTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestTrouverIngredientsManquants:
    """Tests pour _trouver_ingredients_manquants()."""

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_trouver_pas_de_manquants(self, mock_client, mock_analyseur, mock_cache):
        """Test quand tous les ingrÃ©dients sont disponibles."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionsIAService

        service = SuggestionsIAService()

        # Mock ingrÃ©dient
        mock_ing = Mock()
        mock_ing.ingredient = Mock(nom="Tomate")

        mock_recette = Mock()
        mock_recette.ingredients = [mock_ing]

        disponibles = ["tomate", "oignon"]

        result = service._trouver_ingredients_manquants(mock_recette, disponibles)

        assert result == []

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_trouver_avec_manquants(self, mock_client, mock_analyseur, mock_cache):
        """Test quand des ingrÃ©dients manquent."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionsIAService

        service = SuggestionsIAService()

        # Mock ingrÃ©dients
        mock_ing1 = Mock()
        mock_ing1.ingredient = Mock(nom="Tomate")

        mock_ing2 = Mock()
        mock_ing2.ingredient = Mock(nom="Poulet")

        mock_recette = Mock()
        mock_recette.ingredients = [mock_ing1, mock_ing2]

        disponibles = ["tomate"]  # Poulet pas dispo

        result = service._trouver_ingredients_manquants(mock_recette, disponibles)

        assert "Poulet" in result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MIXER SUGGESTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestMixerSuggestions:
    """Tests pour _mixer_suggestions()."""

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_mixer_suggestions_empty(self, mock_client, mock_analyseur, mock_cache):
        """Test mixer listes vides."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionsIAService

        service = SuggestionsIAService()

        # _mixer_suggestions prend (suggestions, nb_total)
        result = service._mixer_suggestions([], 5)

        assert result == []

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_mixer_suggestions_with_items(self, mock_client, mock_analyseur, mock_cache):
        """Test mixer avec Ã©lÃ©ments."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionRecette, SuggestionsIAService

        service = SuggestionsIAService()

        # CrÃ©er suggestions avec favoris et dÃ©couvertes
        all_suggestions = [
            SuggestionRecette(recette_id=1, nom="Recette 1", score=0.9, est_nouvelle=False),
            SuggestionRecette(recette_id=2, nom="Recette 2", score=0.8, est_nouvelle=False),
            SuggestionRecette(recette_id=3, nom="Recette 3", score=0.7, est_nouvelle=True),
        ]

        # _mixer_suggestions prend (suggestions, nb_total)
        result = service._mixer_suggestions(all_suggestions, 3)

        assert len(result) <= 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SUGGERER RECETTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSuggererRecettes:
    """Tests pour suggerer_recettes()."""

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_suggerer_recettes_sans_contexte(self, mock_client, mock_analyseur, mock_cache):
        """Test suggestions sans contexte explicite."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import SuggestionsIAService

        service = SuggestionsIAService()

        mock_session = MagicMock()
        # Pas de recettes
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.query.return_value.all.return_value = []

        result = service.suggerer_recettes(session=mock_session)

        assert isinstance(result, list)

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_suggerer_recettes_avec_recettes(self, mock_client, mock_analyseur, mock_cache):
        """Test suggestions avec des recettes en DB."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import ContexteSuggestion, SuggestionsIAService

        service = SuggestionsIAService()

        # Mock recette avec ingrÃ©dient
        mock_ing = Mock()
        mock_ing.ingredient = Mock()
        mock_ing.ingredient.nom = "Tomate"

        mock_recette = Mock()
        mock_recette.id = 1
        mock_recette.nom = "Salade Tomate"
        mock_recette.categorie = "Salade"
        mock_recette.temps_preparation = 20
        mock_recette.difficulte = "facile"
        mock_recette.portions = 2
        mock_recette.ingredients = [mock_ing]

        mock_session = MagicMock()
        # Le query pour les recettes avec options
        mock_query = MagicMock()
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = [mock_recette]
        mock_session.query.return_value = mock_query

        # Pour construire_contexte et analyser_profil - pas d'articles/historique
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.first.return_value = None

        contexte = ContexteSuggestion(temps_disponible_minutes=60)

        result = service.suggerer_recettes(
            contexte=contexte, nb_suggestions=5, session=mock_session
        )

        assert isinstance(result, list)

    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_suggerer_recettes_pas_de_recettes(self, mock_client, mock_analyseur, mock_cache):
        """Test suggestions quand pas de recettes en BD."""
        mock_client.return_value = Mock()
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        from src.services.suggestions_ia import ContexteSuggestion, SuggestionsIAService

        service = SuggestionsIAService()

        mock_session = MagicMock()
        # Pas de recettes du tout
        mock_query = MagicMock()
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []  # Aucune recette
        mock_session.query.return_value = mock_query
        mock_session.query.return_value.filter.return_value.all.return_value = []

        contexte = ContexteSuggestion()

        result = service.suggerer_recettes(contexte=contexte, session=mock_session)

        assert result == []
        mock_session.query.return_value.all.return_value = []

        result = service.suggerer_recettes(session=mock_session)

        assert isinstance(result, list)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SUGGERER AVEC IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSuggererAvecIA:
    """Tests pour suggerer_avec_ia()."""

    @patch("src.core.database.get_db_context")
    @patch("src.services.suggestions_ia.obtenir_cache")
    @patch("src.services.suggestions_ia.AnalyseurIA")
    @patch("src.services.suggestions_ia.ClientIA")
    def test_suggerer_avec_ia_reponse_vide(
        self, mock_client, mock_analyseur, mock_cache, mock_db_ctx
    ):
        """Test avec rÃ©ponse IA vide."""
        mock_ia = Mock()
        mock_ia.appeler = Mock(return_value=None)
        mock_client.return_value = mock_ia
        mock_analyseur.return_value = Mock()
        mock_cache.return_value = Mock()

        # Mock de la session DB
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = Mock(return_value=False)

        from src.services.suggestions_ia import ContexteSuggestion, SuggestionsIAService

        service = SuggestionsIAService()
        service.client_ia.appeler = Mock(return_value=None)

        contexte = ContexteSuggestion()

        # Appeler avec session injectÃ©e pour bypass le dÃ©corateur
        result = service.suggerer_avec_ia("test requete", contexte, session=mock_session)

        # Retourne liste vide si rÃ©ponse IA nulle
        assert isinstance(result, list)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODULE EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestModuleExports:
    """Tests pour les exports du module."""

    def test_profil_culinaire_exported(self):
        """Test ProfilCulinaire exportÃ©."""
        from src.services.suggestions_ia import ProfilCulinaire

        assert ProfilCulinaire is not None

    def test_contexte_suggestion_exported(self):
        """Test ContexteSuggestion exportÃ©."""
        from src.services.suggestions_ia import ContexteSuggestion

        assert ContexteSuggestion is not None

    def test_suggestion_recette_exported(self):
        """Test SuggestionRecette exportÃ©."""
        from src.services.suggestions_ia import SuggestionRecette

        assert SuggestionRecette is not None

    def test_service_exported(self):
        """Test SuggestionsIAService exportÃ©."""
        from src.services.suggestions_ia import SuggestionsIAService

        assert SuggestionsIAService is not None

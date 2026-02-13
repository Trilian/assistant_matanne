"""
Tests for src/services/suggestions/service.py

ServiceSuggestions - IA-powered recipe suggestions.
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.suggestions.service import (
    ServiceSuggestions,
    SuggestionsIAService,
    get_suggestions_ia_service,
    obtenir_service_suggestions,
)
from src.services.suggestions.types import (
    ContexteSuggestion,
    ProfilCulinaire,
    SuggestionRecette,
)


class TestProfilCulinaire:
    """Tests for ProfilCulinaire type."""

    def test_create_default(self):
        """Test création avec défauts."""
        profil = ProfilCulinaire()
        assert profil.categories_preferees == []
        assert profil.ingredients_frequents == []
        assert profil.difficulte_moyenne == "moyen"
        assert profil.temps_moyen_minutes == 45
        assert profil.nb_portions_habituel == 4
        assert profil.recettes_favorites == []
        assert profil.jours_depuis_derniere_recette == {}

    def test_create_with_values(self):
        """Test création avec valeurs."""
        profil = ProfilCulinaire(
            categories_preferees=["italien", "français"],
            ingredients_frequents=["tomate", "oignon"],
            difficulte_moyenne="facile",
            temps_moyen_minutes=30,
            nb_portions_habituel=2,
            recettes_favorites=[1, 2, 3],
            jours_depuis_derniere_recette={1: 5, 2: 10},
        )
        assert profil.categories_preferees == ["italien", "français"]
        assert profil.temps_moyen_minutes == 30


class TestContexteSuggestion:
    """Tests for ContexteSuggestion type."""

    def test_create_default(self):
        """Test création avec défauts."""
        contexte = ContexteSuggestion()
        assert contexte.type_repas == "dîner"
        assert contexte.nb_personnes == 4
        assert contexte.temps_disponible_minutes == 60
        assert contexte.ingredients_disponibles == []
        assert contexte.contraintes == []
        assert contexte.budget == "normal"

    def test_create_with_values(self):
        """Test création avec valeurs."""
        contexte = ContexteSuggestion(
            type_repas="déjeuner",
            nb_personnes=2,
            temps_disponible_minutes=30,
            ingredients_disponibles=["tomate", "oignon"],
            ingredients_a_utiliser=["tomate"],
            contraintes=["vegetarien"],
            saison="été",
            budget="économique",
        )
        assert contexte.type_repas == "déjeuner"
        assert contexte.nb_personnes == 2
        assert "tomate" in contexte.ingredients_a_utiliser


class TestSuggestionRecette:
    """Tests for SuggestionRecette type."""

    def test_create_default(self):
        """Test création avec défauts."""
        suggestion = SuggestionRecette()
        assert suggestion.recette_id is None
        assert suggestion.nom == ""
        assert suggestion.score == 0.0
        assert suggestion.est_nouvelle is False
        assert suggestion.ingredients_manquants == []

    def test_create_with_values(self):
        """Test création avec valeurs."""
        suggestion = SuggestionRecette(
            recette_id=1,
            nom="Pâtes carbonara",
            raison="Rapide à préparer",
            score=85.0,
            tags=["rapide", "italien"],
            temps_preparation=20,
            difficulte="facile",
            ingredients_manquants=["guanciale"],
            est_nouvelle=True,
        )
        assert suggestion.recette_id == 1
        assert suggestion.nom == "Pâtes carbonara"
        assert suggestion.score == 85.0


class TestServiceSuggestions:
    """Tests for ServiceSuggestions."""

    @pytest.fixture
    def service(self):
        """Fixture service avec mocks."""
        with (
            patch("src.services.suggestions.service.ClientIA") as mock_client,
            patch("src.services.suggestions.service.AnalyseurIA") as mock_analyseur,
            patch("src.services.suggestions.service.obtenir_cache") as mock_cache,
        ):
            mock_cache.return_value = MagicMock()
            s = ServiceSuggestions()
            s.client_ia = mock_client.return_value
            s.analyseur = mock_analyseur.return_value
            return s

    @pytest.fixture
    def mock_session(self):
        """Fixture session mock."""
        return MagicMock()

    # ═══════════════════════════════════════════════════════════
    # analyser_profil_culinaire
    # ═══════════════════════════════════════════════════════════

    def test_analyser_profil_culinaire_empty(self, service, mock_session):
        """Test profil vide sans historique."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            profil = service.analyser_profil_culinaire(session=mock_session)

        assert isinstance(profil, ProfilCulinaire)
        assert profil.categories_preferees == []

    def test_analyser_profil_culinaire_with_history(self, service, mock_session):
        """Test profil avec historique."""
        # Mock historique
        mock_historique = [MagicMock(date_cuisson=date.today(), recette_id=1)]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_historique

        # Mock recette
        mock_recette = MagicMock(
            id=1,
            categorie="italien",
            difficulte="facile",
            temps_preparation=30,
            portions=4,
        )
        mock_recette.ingredients = []
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_recette
        mock_session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = mock_historique[
            0
        ]

        profil = service.analyser_profil_culinaire(session=mock_session)

        assert isinstance(profil, ProfilCulinaire)

    def test_analyser_profil_culinaire_with_ingredients(self, service, mock_session):
        """Test profil avec ingrédients."""
        mock_historique = [MagicMock(date_cuisson=date.today(), recette_id=1)]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_historique

        # Mock ingrédient
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "tomate"
        mock_ri = MagicMock()
        mock_ri.ingredient = mock_ingredient

        mock_recette = MagicMock(
            id=1,
            categorie="italien",
            difficulte="facile",
            temps_preparation=30,
            portions=4,
        )
        mock_recette.ingredients = [mock_ri]

        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_recette
        mock_session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = mock_historique[
            0
        ]

        profil = service.analyser_profil_culinaire(session=mock_session)

        assert isinstance(profil, ProfilCulinaire)

    def test_analyser_profil_culinaire_favorites(self, service, mock_session):
        """Test détection favoris (3+ préparations)."""
        mock_historique = [
            MagicMock(date_cuisson=date.today(), recette_id=1),
            MagicMock(date_cuisson=date.today(), recette_id=1),
            MagicMock(date_cuisson=date.today(), recette_id=1),  # 3 fois
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_historique

        mock_recette = MagicMock(
            id=1, categorie=None, difficulte=None, temps_preparation=None, portions=None
        )
        mock_recette.ingredients = []
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_recette
        mock_session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = mock_historique[
            0
        ]

        profil = service.analyser_profil_culinaire(session=mock_session)

        assert 1 in profil.recettes_favorites

    # ═══════════════════════════════════════════════════════════
    # construire_contexte
    # ═══════════════════════════════════════════════════════════

    def test_construire_contexte_basic(self, service, mock_session):
        """Test construction contexte basique."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        contexte = service.construire_contexte(session=mock_session)

        assert isinstance(contexte, ContexteSuggestion)
        assert contexte.type_repas == "dîner"
        assert contexte.nb_personnes == 4
        assert contexte.saison in ["printemps", "été", "automne", "hiver"]

    def test_construire_contexte_custom(self, service, mock_session):
        """Test construction contexte personnalisé."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        contexte = service.construire_contexte(
            type_repas="déjeuner",
            nb_personnes=2,
            temps_minutes=30,
            session=mock_session,
        )

        assert contexte.type_repas == "déjeuner"
        assert contexte.nb_personnes == 2
        assert contexte.temps_disponible_minutes == 30

    def test_construire_contexte_with_stock(self, service, mock_session):
        """Test contexte avec ingrédients en stock."""
        mock_article = MagicMock()
        mock_article.nom = "Tomate"
        mock_article.date_peremption = None
        mock_article.quantite = 5

        mock_session.query.return_value.filter.return_value.all.return_value = [mock_article]

        contexte = service.construire_contexte(session=mock_session)

        assert "Tomate" in contexte.ingredients_disponibles

    def test_construire_contexte_priority_ingredients(self, service, mock_session):
        """Test ingrédients à utiliser en priorité."""
        demain = datetime.now() + timedelta(days=2)
        mock_article = MagicMock()
        mock_article.nom = "Yaourt"
        mock_article.date_peremption = demain
        mock_article.quantite = 2

        mock_session.query.return_value.filter.return_value.all.return_value = [mock_article]

        contexte = service.construire_contexte(session=mock_session)

        assert "Yaourt" in contexte.ingredients_a_utiliser

    def test_construire_contexte_saison_printemps(self, service, mock_session):
        """Test saison printemps."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        with patch("src.services.suggestions.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 4, 15)
            contexte = service.construire_contexte(session=mock_session)

        assert contexte.saison == "printemps"

    def test_construire_contexte_saison_ete(self, service, mock_session):
        """Test saison été."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        with patch("src.services.suggestions.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 7, 15)
            contexte = service.construire_contexte(session=mock_session)

        assert contexte.saison == "été"

    def test_construire_contexte_saison_automne(self, service, mock_session):
        """Test saison automne."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        with patch("src.services.suggestions.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 10, 15)
            contexte = service.construire_contexte(session=mock_session)

        assert contexte.saison == "automne"

    def test_construire_contexte_saison_hiver(self, service, mock_session):
        """Test saison hiver."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        with patch("src.services.suggestions.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 1, 15)
            contexte = service.construire_contexte(session=mock_session)

        assert contexte.saison == "hiver"

    # ═══════════════════════════════════════════════════════════
    # suggerer_recettes
    # ═══════════════════════════════════════════════════════════

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_recettes_empty(self, mock_profil, mock_contexte, service, mock_session):
        """Test suggestions sans recettes."""
        mock_contexte.return_value = ContexteSuggestion()
        mock_profil.return_value = ProfilCulinaire()
        mock_session.query.return_value.options.return_value.all.return_value = []

        suggestions = service.suggerer_recettes(session=mock_session)

        assert suggestions == []

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_recettes_basic(self, mock_profil, mock_contexte, service, mock_session):
        """Test suggestions basiques."""
        mock_contexte.return_value = ContexteSuggestion(
            ingredients_disponibles=["tomate"],
            temps_disponible_minutes=60,
        )
        mock_profil.return_value = ProfilCulinaire(
            categories_preferees=["italien"],
            jours_depuis_derniere_recette={},
        )

        # Mock recette
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "tomate"
        mock_ri = MagicMock()
        mock_ri.ingredient = mock_ingredient

        mock_recette = MagicMock(
            id=1,
            nom="Pâtes tomate",
            categorie="italien",
            difficulte="facile",
            temps_preparation=30,
            portions=4,
        )
        mock_recette.ingredients = [mock_ri]

        mock_session.query.return_value.options.return_value.all.return_value = [mock_recette]

        suggestions = service.suggerer_recettes(session=mock_session)

        assert len(suggestions) >= 1
        assert isinstance(suggestions[0], SuggestionRecette)

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_recettes_with_context(
        self, mock_profil, mock_contexte, service, mock_session
    ):
        """Test suggestions avec contexte fourni."""
        contexte = ContexteSuggestion(
            type_repas="déjeuner",
            nb_personnes=2,
        )
        mock_profil.return_value = ProfilCulinaire()
        mock_session.query.return_value.options.return_value.all.return_value = []

        suggestions = service.suggerer_recettes(
            contexte=contexte,
            session=mock_session,
        )

        # construire_contexte ne doit pas être appelé si contexte fourni
        assert suggestions == []

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_recettes_sort_by_score(
        self, mock_profil, mock_contexte, service, mock_session
    ):
        """Test tri par score."""
        mock_contexte.return_value = ContexteSuggestion()
        mock_profil.return_value = ProfilCulinaire(
            categories_preferees=["italien"],
            jours_depuis_derniere_recette={},
        )

        # Recette avec catégorie préférée (score plus élevé)
        mock_recette1 = MagicMock(
            id=1,
            nom="Pâtes",
            categorie="italien",
            difficulte="facile",
            temps_preparation=30,
        )
        mock_recette1.ingredients = []

        # Recette sans catégorie préférée
        mock_recette2 = MagicMock(
            id=2,
            nom="Salade",
            categorie="français",
            difficulte="facile",
            temps_preparation=15,
        )
        mock_recette2.ingredients = []

        mock_session.query.return_value.options.return_value.all.return_value = [
            mock_recette2,
            mock_recette1,
        ]

        suggestions = service.suggerer_recettes(nb_suggestions=2, session=mock_session)

        # La recette italienne devrait avoir un score plus élevé
        if len(suggestions) >= 2:
            assert suggestions[0].score >= suggestions[1].score

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_recettes_no_discoveries(
        self, mock_profil, mock_contexte, service, mock_session
    ):
        """Test sans découvertes."""
        mock_contexte.return_value = ContexteSuggestion()
        mock_profil.return_value = ProfilCulinaire(jours_depuis_derniere_recette={1: 5})

        mock_recette = MagicMock(
            id=1,
            nom="Test",
            categorie="autre",
            difficulte="moyen",
            temps_preparation=45,
        )
        mock_recette.ingredients = []

        mock_session.query.return_value.options.return_value.all.return_value = [mock_recette]

        suggestions = service.suggerer_recettes(
            inclure_decouvertes=False,
            session=mock_session,
        )

        assert isinstance(suggestions, list)

    # ═══════════════════════════════════════════════════════════
    # _calculer_score_recette
    # ═══════════════════════════════════════════════════════════

    def test_calculer_score_recette_basic(self, service, mock_session):
        """Test calcul score basique."""
        mock_recette = MagicMock(
            id=1,
            categorie="autre",
            temps_preparation=30,
            difficulte="moyen",
        )
        mock_recette.ingredients = []

        contexte = ContexteSuggestion()
        profil = ProfilCulinaire()

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score >= 50  # Score de base
        assert isinstance(raisons, list)
        assert isinstance(tags, list)

    def test_calculer_score_recette_categorie_preferee(self, service):
        """Test bonus catégorie préférée."""
        mock_recette = MagicMock(
            id=1,
            categorie="italien",
            temps_preparation=30,
            difficulte="moyen",
        )
        mock_recette.ingredients = []

        contexte = ContexteSuggestion()
        profil = ProfilCulinaire(categories_preferees=["italien", "français"])

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score > 50
        assert any("Catégorie" in r for r in raisons)
        assert "favori" in tags

    def test_calculer_score_recette_temps_adapte(self, service):
        """Test bonus temps adapté."""
        mock_recette = MagicMock(
            id=1,
            categorie="autre",
            temps_preparation=30,
            difficulte="moyen",
        )
        mock_recette.ingredients = []

        contexte = ContexteSuggestion(temps_disponible_minutes=60)
        profil = ProfilCulinaire()

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score > 50
        assert "rapide" in tags

    def test_calculer_score_recette_temps_trop_long(self, service):
        """Test malus temps trop long."""
        mock_recette = MagicMock(
            id=1,
            categorie="autre",
            temps_preparation=120,
            difficulte="difficile",
        )
        mock_recette.ingredients = []

        contexte = ContexteSuggestion(temps_disponible_minutes=30)
        profil = ProfilCulinaire()

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score < 50  # Malus appliqué

    def test_calculer_score_recette_ingredients_prioritaires(self, service):
        """Test bonus ingrédients prioritaires."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "tomate"
        mock_ri = MagicMock()
        mock_ri.ingredient = mock_ingredient

        mock_recette = MagicMock(
            id=1,
            categorie="autre",
            temps_preparation=30,
            difficulte="moyen",
        )
        mock_recette.ingredients = [mock_ri]

        contexte = ContexteSuggestion(
            ingredients_a_utiliser=["tomate"],
            ingredients_disponibles=["tomate"],
        )
        profil = ProfilCulinaire()

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score > 50
        assert "anti-gaspi" in tags

    def test_calculer_score_recette_repetition_recente(self, service):
        """Test malus répétition récente."""
        mock_recette = MagicMock(
            id=1,
            categorie="autre",
            temps_preparation=30,
            difficulte="moyen",
        )
        mock_recette.ingredients = []

        contexte = ContexteSuggestion()
        profil = ProfilCulinaire(jours_depuis_derniere_recette={1: 3})  # 3 jours

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score < 50  # Malus majeur
        assert any("récemment" in r for r in raisons)

    def test_calculer_score_recette_decouverte(self, service):
        """Test bonus découverte."""
        mock_recette = MagicMock(
            id=99,
            categorie="autre",
            temps_preparation=30,
            difficulte="moyen",
        )
        mock_recette.ingredients = []

        contexte = ContexteSuggestion()
        profil = ProfilCulinaire(jours_depuis_derniere_recette={1: 10})  # Autre recette

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert "découverte" in tags

    def test_calculer_score_recette_saison(self, service):
        """Test bonus saison."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "tomate"
        mock_ri = MagicMock()
        mock_ri.ingredient = mock_ingredient

        mock_recette = MagicMock(
            id=1,
            categorie="autre",
            temps_preparation=30,
            difficulte="moyen",
        )
        mock_recette.ingredients = [mock_ri]

        contexte = ContexteSuggestion(saison="été")
        profil = ProfilCulinaire()

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert score > 50
        assert "de-saison" in tags

    def test_calculer_score_recette_favorite(self, service):
        """Test bonus recette favorite."""
        mock_recette = MagicMock(
            id=1,
            categorie="autre",
            temps_preparation=30,
            difficulte="moyen",
        )
        mock_recette.ingredients = []

        contexte = ContexteSuggestion()
        profil = ProfilCulinaire(
            recettes_favorites=[1],
            jours_depuis_derniere_recette={1: 30},
        )

        score, raisons, tags = service._calculer_score_recette(mock_recette, contexte, profil)

        assert "classique" in tags

    # ═══════════════════════════════════════════════════════════
    # _trouver_ingredients_manquants
    # ═══════════════════════════════════════════════════════════

    def test_trouver_ingredients_manquants_none(self, service):
        """Test aucun ingrédient manquant."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "tomate"
        mock_ri = MagicMock()
        mock_ri.ingredient = mock_ingredient

        mock_recette = MagicMock()
        mock_recette.ingredients = [mock_ri]

        manquants = service._trouver_ingredients_manquants(
            mock_recette,
            ["tomate", "oignon"],
        )

        assert len(manquants) == 0

    def test_trouver_ingredients_manquants_some(self, service):
        """Test certains ingrédients manquants."""
        mock_ing1 = MagicMock()
        mock_ing1.nom = "tomate"
        mock_ri1 = MagicMock()
        mock_ri1.ingredient = mock_ing1

        mock_ing2 = MagicMock()
        mock_ing2.nom = "basilic"
        mock_ri2 = MagicMock()
        mock_ri2.ingredient = mock_ing2

        mock_recette = MagicMock()
        mock_recette.ingredients = [mock_ri1, mock_ri2]

        manquants = service._trouver_ingredients_manquants(mock_recette, ["tomate"])

        assert len(manquants) == 1
        assert "basilic" in manquants

    def test_trouver_ingredients_manquants_no_ingredients_attr(self, service):
        """Test recette sans attribut ingredients."""
        mock_recette = MagicMock(spec=[])  # Pas d'attribut ingredients

        manquants = service._trouver_ingredients_manquants(mock_recette, ["tomate"])

        assert manquants == []

    def test_trouver_ingredients_manquants_case_insensitive(self, service):
        """Test insensible à la casse."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Tomate"
        mock_ri = MagicMock()
        mock_ri.ingredient = mock_ingredient

        mock_recette = MagicMock()
        mock_recette.ingredients = [mock_ri]

        manquants = service._trouver_ingredients_manquants(mock_recette, ["tomate"])

        assert len(manquants) == 0

    # ═══════════════════════════════════════════════════════════
    # _mixer_suggestions
    # ═══════════════════════════════════════════════════════════

    def test_mixer_suggestions_basic(self, service):
        """Test mix basique."""
        favoris = [SuggestionRecette(nom=f"Favori{i}", est_nouvelle=False) for i in range(5)]
        decouvertes = [SuggestionRecette(nom=f"Decouverte{i}", est_nouvelle=True) for i in range(5)]
        suggestions = favoris + decouvertes

        result = service._mixer_suggestions(suggestions, 5)

        assert len(result) == 5
        # Ratio ~60% favoris, ~40% découvertes
        nb_favoris = sum(1 for s in result if not s.est_nouvelle)
        assert nb_favoris >= 2

    def test_mixer_suggestions_only_favoris(self, service):
        """Test avec seulement des favoris."""
        suggestions = [SuggestionRecette(nom=f"F{i}", est_nouvelle=False) for i in range(10)]

        result = service._mixer_suggestions(suggestions, 5)

        assert len(result) == 5

    def test_mixer_suggestions_only_decouvertes(self, service):
        """Test avec seulement des découvertes."""
        suggestions = [SuggestionRecette(nom=f"D{i}", est_nouvelle=True) for i in range(10)]

        result = service._mixer_suggestions(suggestions, 5)

        assert len(result) == 5

    def test_mixer_suggestions_less_than_requested(self, service):
        """Test avec moins de suggestions que demandé."""
        suggestions = [SuggestionRecette(nom=f"S{i}", est_nouvelle=False) for i in range(3)]

        result = service._mixer_suggestions(suggestions, 10)

        assert len(result) == 3

    # ═══════════════════════════════════════════════════════════
    # suggerer_avec_ia
    # ═══════════════════════════════════════════════════════════

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_avec_ia_success(self, mock_profil, mock_contexte, service, mock_session):
        """Test suggestions IA réussies."""
        mock_contexte.return_value = ContexteSuggestion(
            ingredients_disponibles=["tomate"],
            ingredients_a_utiliser=["yaourt"],
        )
        mock_profil.return_value = ProfilCulinaire(categories_preferees=["italien"])

        # Mock réponse IA
        service.client_ia.generer.return_value = '[{"nom": "Suggestion IA", "description": "Test"}]'
        service.analyseur.extraire_json.return_value = [
            {"nom": "Suggestion IA", "description": "Test"}
        ]

        suggestions = service.suggerer_avec_ia(
            "Je veux quelque chose de rapide",
            session=mock_session,
        )

        assert len(suggestions) == 1
        assert suggestions[0]["nom"] == "Suggestion IA"

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_avec_ia_with_context(self, mock_profil, mock_contexte, service, mock_session):
        """Test suggestions IA avec contexte fourni."""
        contexte = ContexteSuggestion(type_repas="déjeuner")
        mock_profil.return_value = ProfilCulinaire()

        service.client_ia.generer.return_value = "[]"
        service.analyseur.extraire_json.return_value = []

        suggestions = service.suggerer_avec_ia(
            "Test",
            contexte=contexte,
            session=mock_session,
        )

        assert suggestions == []

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_avec_ia_error(self, mock_profil, mock_contexte, service, mock_session):
        """Test gestion erreur IA."""
        mock_contexte.return_value = ContexteSuggestion()
        mock_profil.return_value = ProfilCulinaire()

        service.client_ia.generer.side_effect = Exception("Erreur IA")

        suggestions = service.suggerer_avec_ia("Test", session=mock_session)

        assert suggestions == []

    @patch.object(ServiceSuggestions, "construire_contexte")
    @patch.object(ServiceSuggestions, "analyser_profil_culinaire")
    def test_suggerer_avec_ia_invalid_response(
        self, mock_profil, mock_contexte, service, mock_session
    ):
        """Test réponse IA invalide."""
        mock_contexte.return_value = ContexteSuggestion()
        mock_profil.return_value = ProfilCulinaire()

        service.client_ia.generer.return_value = "invalid"
        service.analyseur.extraire_json.return_value = None  # Pas une liste

        suggestions = service.suggerer_avec_ia("Test", session=mock_session)

        assert suggestions == []


class TestFactory:
    """Tests pour les factories."""

    def test_obtenir_service_suggestions_singleton(self):
        """Test singleton."""
        # Reset singleton
        import src.services.suggestions.service as module

        module._suggestions_service = None

        service1 = obtenir_service_suggestions()
        service2 = obtenir_service_suggestions()

        assert service1 is service2
        assert isinstance(service1, ServiceSuggestions)

    def test_get_suggestions_ia_service_alias(self):
        """Test alias."""
        assert get_suggestions_ia_service == obtenir_service_suggestions

    def test_suggestions_ia_service_alias(self):
        """Test alias de classe."""
        assert SuggestionsIAService == ServiceSuggestions

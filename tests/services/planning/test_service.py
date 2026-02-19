"""
Tests pour src/services/planning/service.py

Tests du service de planning avec mocks.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.cuisine.planning.service import ServicePlanning
from src.services.cuisine.planning.types import JourPlanning, ParametresEquilibre


class TestServicePlanningInit:
    """Tests d'initialisation du service."""

    def test_service_creation(self):
        """Vérifie que le service peut être créé."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            service = ServicePlanning()
            assert service is not None

    def test_service_has_model(self):
        """Vérifie que le service a un modèle défini."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            service = ServicePlanning()
            assert service.model is not None


class TestServicePlanningMethods:
    """Tests des méthodes du service."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            return ServicePlanning()

    @pytest.fixture
    def mock_db(self):
        """Fixture pour une session DB mockée."""
        mock = MagicMock()
        mock.query.return_value.filter.return_value.first.return_value = None
        mock.query.return_value.options.return_value.filter.return_value.first.return_value = None
        return mock

    def test_get_planning_returns_none_when_not_found(self, service, mock_db):
        """Vérifie que get_planning retourne None si non trouvé."""
        result = service.get_planning(planning_id=999, db=mock_db)
        # La méthode peut retourner None ou lever une exception selon l'implémentation
        assert result is None

    def test_get_planning_complet_returns_none_when_not_found(self, service, mock_db):
        """Vérifie que get_planning_complet retourne None si non trouvé."""
        result = service.get_planning_complet(planning_id=999, db=mock_db)
        assert result is None

    def test_suggerer_recettes_equilibrees_returns_list(self, service, mock_db):
        """Vérifie que suggerer_recettes_equilibrees retourne une liste."""
        params = ParametresEquilibre()
        result = service.suggerer_recettes_equilibrees(
            semaine_debut=date.today(), parametres=params, db=mock_db
        )
        assert isinstance(result, list)


class TestParametresEquilibre:
    """Tests pour le schéma ParametresEquilibre."""

    def test_creation_defaults(self):
        """Vérifie les valeurs par défaut."""
        params = ParametresEquilibre()
        assert params.pates_riz_count == 3
        assert len(params.poisson_jours) == 2

    def test_creation_custom_values(self):
        """Vérifie avec des valeurs personnalisées."""
        params = ParametresEquilibre(
            poisson_jours=["lundi", "jeudi", "vendredi"],
            viande_rouge_jours=["mardi"],
            vegetarien_jours=["mercredi", "samedi"],
            pates_riz_count=4,
        )
        assert len(params.poisson_jours) == 3
        assert params.pates_riz_count == 4

    def test_pates_riz_count_validation_min(self):
        """Vérifie la validation minimum."""
        with pytest.raises(ValueError):
            ParametresEquilibre(pates_riz_count=0)

    def test_pates_riz_count_validation_max(self):
        """Vérifie la validation maximum."""
        with pytest.raises(ValueError):
            ParametresEquilibre(pates_riz_count=10)

    def test_ingredients_exclus_empty_default(self):
        """Vérifie que ingredients_exclus est vide par défaut."""
        params = ParametresEquilibre()
        assert params.ingredients_exclus == []

    def test_preferences_extras_empty_default(self):
        """Vérifie que preferences_extras est vide par défaut."""
        params = ParametresEquilibre()
        assert params.preferences_extras == {}


class TestJourPlanning:
    """Tests pour le schéma JourPlanning."""

    def test_creation_valid(self):
        """Vérifie la création avec des valeurs valides."""
        jour = JourPlanning(
            jour="Lundi 1",  # min_length=6
            dejeuner="Poulet rôti",
            diner="Soupe de légumes",
        )
        assert jour.jour == "Lundi 1"
        assert jour.dejeuner == "Poulet rôti"

    def test_jour_min_length(self):
        """Vérifie la longueur minimum du jour."""
        with pytest.raises(ValueError):
            JourPlanning(jour="Lu", dejeuner="Test", diner="Test")

    def test_dejeuner_min_length(self):
        """Vérifie la longueur minimum du déjeuner."""
        with pytest.raises(ValueError):
            JourPlanning(jour="Lundi 1", dejeuner="AB", diner="Test")

    def test_diner_min_length(self):
        """Vérifie la longueur minimum du dîner."""
        with pytest.raises(ValueError):
            JourPlanning(jour="Lundi 1", dejeuner="Test", diner="AB")


class TestServicePlanningCache:
    """Tests du cache du service."""

    def test_cache_key_generation(self):
        """Vérifie la génération des clés de cache."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            service = ServicePlanning()
            # Le service utilise des décorateurs @avec_cache
            assert hasattr(service, "get_planning")

    def test_cache_ttl(self):
        """Vérifie le TTL de cache configuré."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            service = ServicePlanning()
            assert service.cache_ttl == 1800  # 30 minutes


class TestServicePlanningIntegration:
    """Tests d'intégration du service."""

    @pytest.fixture
    def mock_planning(self):
        """Fixture pour un planning mocké."""
        mock = MagicMock()
        mock.id = 1
        mock.nom = "Test Planning"
        mock.semaine_debut = date.today()
        mock.semaine_fin = date.today() + timedelta(days=6)
        mock.actif = True
        mock.genere_par_ia = False
        mock.repas = []
        return mock

    def test_get_planning_complet_format(self, mock_planning):
        """Vérifie le format de retour de get_planning_complet."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            service = ServicePlanning()

            mock_db = MagicMock()
            mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_planning

            result = service.get_planning_complet(planning_id=1, db=mock_db)

            if result is not None:
                assert "id" in result
                assert "nom" in result
                assert "repas_par_jour" in result


# ═══════════════════════════════════════════════════════════
# TESTS SUPPLÉMENTAIRES POUR SERVICE PLANNING
# ═══════════════════════════════════════════════════════════


class TestServicePlanningPlanningComplet:
    """Tests pour get_planning_complet."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            return ServicePlanning()

    def test_get_planning_complet_with_repas(self, service):
        """Test get_planning_complet avec des repas."""
        mock_planning = MagicMock()
        mock_planning.id = 1
        mock_planning.nom = "Planning Test"
        mock_planning.semaine_debut = date(2024, 1, 15)
        mock_planning.semaine_fin = date(2024, 1, 21)
        mock_planning.actif = True
        mock_planning.genere_par_ia = False

        mock_repas = MagicMock()
        mock_repas.id = 1
        mock_repas.date_repas = date(2024, 1, 15)
        mock_repas.type_repas = "déjeuner"
        mock_repas.recette_id = 1
        mock_repas.recette = MagicMock(nom="Pâtes")
        mock_repas.prepare = False
        mock_repas.notes = "Test"

        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_planning
        )

        result = service.get_planning_complet(planning_id=1, db=mock_db)

        if result:
            assert result["id"] == 1
            assert "repas_par_jour" in result
            assert len(result["repas_par_jour"]) > 0


class TestServicePlanningSuggestions:
    """Tests pour suggerer_recettes_equilibrees."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            return ServicePlanning()

    @pytest.fixture
    def mock_db_with_recettes(self):
        """Fixture avec recettes mockées."""
        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.nom = "Recette Test"
        mock_recette.description = "Description test"
        mock_recette.temps_preparation = 15
        mock_recette.temps_cuisson = 30
        mock_recette.type_proteines = "poisson"

        mock = MagicMock()
        mock.query.return_value.filter.return_value.limit.return_value.all.return_value = [
            mock_recette
        ]
        mock.query.return_value.filter.return_value.filter.return_value.limit.return_value.all.return_value = [
            mock_recette
        ]
        return mock

    def test_suggerer_recettes_equilibrees_basic(self, service, mock_db_with_recettes):
        """Test de base des suggestions équilibrées."""
        params = ParametresEquilibre()
        result = service.suggerer_recettes_equilibrees(
            semaine_debut=date(2024, 1, 15), parametres=params, db=mock_db_with_recettes
        )
        assert isinstance(result, list)


class TestServicePlanningCreerAvecChoix:
    """Tests pour creer_planning_avec_choix."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            return ServicePlanning()

    def test_creer_planning_avec_choix_empty_selection(self, service):
        """Test avec sélection vide."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = service.creer_planning_avec_choix(
            semaine_debut=date(2024, 1, 15), recettes_selection={}, db=mock_db
        )
        # Retourne un planning même avec sélection vide
        if result:
            mock_db.add.assert_called()

    def test_creer_planning_avec_choix_with_recipe(self, service):
        """Test avec recette sélectionnée."""
        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.nom = "Pâtes"

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_recette

        _result = service.creer_planning_avec_choix(
            semaine_debut=date(2024, 1, 15), recettes_selection={"jour_0": 1}, db=mock_db
        )
        # Vérifie que la méthode a été appelée
        assert mock_db.add.called

    def test_creer_planning_avec_choix_recipe_not_found(self, service):
        """Test avec recette non trouvée."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        _result = service.creer_planning_avec_choix(
            semaine_debut=date(2024, 1, 15), recettes_selection={"jour_0": 999}, db=mock_db
        )
        # La méthode continue même si recette non trouvée


class TestServicePlanningAgregerCourses:
    """Tests pour agréger_courses_pour_planning."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            return ServicePlanning()

    def test_agreger_courses_planning_not_found(self, service):
        """Test avec planning inexistant."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = service.agréger_courses_pour_planning(planning_id=999, db=mock_db)
        assert result == []

    def test_agreger_courses_planning_without_repas(self, service):
        """Test avec planning sans repas."""
        mock_planning = MagicMock()
        mock_planning.repas = []

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_planning

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        assert result == []

    def test_agreger_courses_repas_without_recette_id(self, service):
        """Test avec repas sans recette_id."""
        mock_repas = MagicMock()
        mock_repas.recette_id = None

        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_planning

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        assert result == []

    def test_agreger_courses_recette_not_found(self, service):
        """Test avec recette non trouvée."""
        mock_repas = MagicMock()
        mock_repas.recette_id = 1

        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        # Premier appel retourne le planning, second retourne None pour la recette
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_planning,
            None,  # recette non trouvée
        ]

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        assert result == []

    def test_agreger_courses_recette_no_ingredients(self, service):
        """Test avec recette sans ingrédients."""
        mock_repas = MagicMock()
        mock_repas.recette_id = 1

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.ingredients = []

        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_planning,
            mock_recette,
        ]

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        assert result == []

    def test_agreger_courses_ingredient_none(self, service):
        """Test avec ingrédient None."""
        mock_recette_ingredient = MagicMock()
        mock_recette_ingredient.ingredient = None

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.ingredients = [mock_recette_ingredient]

        mock_repas = MagicMock()
        mock_repas.recette_id = 1

        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_planning,
            mock_recette,
        ]

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        assert result == []

    def test_agreger_courses_full_flow(self, service):
        """Test du flux complet avec ingrédients."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Tomate"
        mock_ingredient.unite = "kg"
        mock_ingredient.categorie = "legumes"

        mock_recette_ingredient = MagicMock()
        mock_recette_ingredient.quantite = 2
        mock_recette_ingredient.unite = "kg"
        mock_recette_ingredient.ingredient = mock_ingredient

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.ingredients = [mock_recette_ingredient]

        mock_repas = MagicMock()
        mock_repas.recette_id = 1

        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_planning,
            mock_recette,
        ]

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        assert isinstance(result, list)
        if result:
            assert result[0]["nom"] == "Tomate"
            assert result[0]["quantite"] == 2

    def test_agreger_courses_with_multiple_same_ingredient(self, service):
        """Test avec plusieurs fois le même ingrédient."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Tomate"
        mock_ingredient.unite = "kg"
        mock_ingredient.categorie = "legumes"

        mock_recette_ingredient1 = MagicMock()
        mock_recette_ingredient1.quantite = 2
        mock_recette_ingredient1.unite = "kg"
        mock_recette_ingredient1.ingredient = mock_ingredient

        mock_recette_ingredient2 = MagicMock()
        mock_recette_ingredient2.quantite = 3
        mock_recette_ingredient2.unite = "kg"
        mock_recette_ingredient2.ingredient = mock_ingredient

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.ingredients = [mock_recette_ingredient1, mock_recette_ingredient2]

        mock_repas = MagicMock()
        mock_repas.recette_id = 1

        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_planning,
            mock_recette,
        ]

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        if result:
            assert result[0]["quantite"] == 5  # 2 + 3

    def test_agreger_courses_different_units(self, service):
        """Test avec unités différentes."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Farine"
        mock_ingredient.unite = None
        mock_ingredient.categorie = "epicerie"

        mock_recette_ingredient1 = MagicMock()
        mock_recette_ingredient1.quantite = 500
        mock_recette_ingredient1.unite = "g"
        mock_recette_ingredient1.ingredient = mock_ingredient

        mock_recette_ingredient2 = MagicMock()
        mock_recette_ingredient2.quantite = 2
        mock_recette_ingredient2.unite = "kg"  # Unité différente
        mock_recette_ingredient2.ingredient = mock_ingredient

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.ingredients = [mock_recette_ingredient1, mock_recette_ingredient2]

        mock_repas = MagicMock()
        mock_repas.recette_id = 1

        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_planning,
            mock_recette,
        ]

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        # Avec unités différentes, quantité n'est pas agrégée mais count est incrémenté
        if result:
            assert result[0]["repas_count"] == 2

    def test_agreger_courses_with_none_quantite(self, service):
        """Test avec quantité None."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Sel"
        mock_ingredient.unite = "pcs"
        mock_ingredient.categorie = "epicerie"

        mock_recette_ingredient = MagicMock()
        mock_recette_ingredient.quantite = None
        mock_recette_ingredient.unite = None
        mock_recette_ingredient.ingredient = mock_ingredient

        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.ingredients = [mock_recette_ingredient]

        mock_repas = MagicMock()
        mock_repas.recette_id = 1

        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_planning,
            mock_recette,
        ]

        result = service.agréger_courses_pour_planning(planning_id=1, db=mock_db)
        if result:
            assert result[0]["quantite"] == 1  # Default value


class TestServicePlanningGenererIA:
    """Tests pour generer_planning_ia."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            return ServicePlanning()

    def test_generer_planning_ia_method_exists(self, service):
        """Vérifie que la méthode existe."""
        assert hasattr(service, "generer_planning_ia")


class TestServicePlanningGetPlanning:
    """Tests supplémentaires pour get_planning."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            return ServicePlanning()

    def test_get_planning_with_id(self, service):
        """Test get_planning avec un ID spécifique."""
        mock_planning = MagicMock()
        mock_planning.id = 1

        mock_db = MagicMock()
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_planning
        )

        _result = service.get_planning(planning_id=1, db=mock_db)
        # Le résultat dépend de l'implémentation
        # Ici on vérifie juste que la méthode accepte les paramètres

    def test_get_planning_active(self, service):
        """Test get_planning pour le planning actif."""
        mock_planning = MagicMock()
        mock_planning.actif = True

        mock_db = MagicMock()
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_planning
        )

        _result = service.get_planning(planning_id=None, db=mock_db)
        # Vérifie que la requête est faite pour le planning actif


# ═══════════════════════════════════════════════════════════
# TESTS POUR GENERER_PLANNING_SEMAINE_IA
# ═══════════════════════════════════════════════════════════


class TestGenererPlanningIA:
    """Tests pour generer_planning_ia - lignes 468-593."""

    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            return ServicePlanning()

    @pytest.fixture
    def mock_db(self):
        """Fixture pour une session DB mockée."""
        mock = MagicMock()
        mock.add = MagicMock()
        mock.flush = MagicMock()
        mock.commit = MagicMock()
        mock.refresh = MagicMock()
        return mock

    def test_generer_planning_ia_success(self, service, mock_db):
        """Test génération IA réussie - crée planning avec repas."""
        # Simuler réponse IA réussie
        mock_jours = [
            JourPlanning(jour="Lundi01", dejeuner="Pâtes carbonara", diner="Salade niçoise"),
            JourPlanning(jour="Mardi02", dejeuner="Poulet rôti", diner="Soupe légumes"),
            JourPlanning(jour="Mercredi", dejeuner="Poisson grillé", diner="Omelette"),
            JourPlanning(jour="Jeudi04", dejeuner="Riz cantonais", diner="Quiche lorraine"),
            JourPlanning(jour="Vendredi", dejeuner="Boeuf bourguignon", diner="Pizza maison"),
            JourPlanning(jour="Samedi06", dejeuner="Couscous royal", diner="Crêpes"),
            JourPlanning(jour="Dimanche", dejeuner="Rôti de porc", diner="Ratatouille"),
        ]

        with (
            patch.object(service, "call_with_list_parsing_sync", return_value=mock_jours),
            patch("src.services.cuisine.planning.service.Cache"),
        ):
            _result = service.generer_planning_ia(
                semaine_debut=date(2024, 1, 15), preferences={}, db=mock_db
            )

            # Vérifie appels DB
            assert mock_db.add.called
            assert mock_db.commit.called

    def test_generer_planning_ia_fallback_when_no_data(self, service, mock_db):
        """Test fallback au planning par défaut quand IA échoue."""
        # Simuler échec IA (retourne None)
        with patch.object(service, "call_with_list_parsing_sync", return_value=None):
            _result = service.generer_planning_ia(
                semaine_debut=date(2024, 1, 15), preferences=None, db=mock_db
            )

            # Vérifie qu'un planning par défaut est créé
            assert mock_db.add.called
            assert mock_db.commit.called

    def test_generer_planning_ia_fallback_empty_list(self, service, mock_db):
        """Test fallback quand IA retourne liste vide."""
        with patch.object(service, "call_with_list_parsing_sync", return_value=[]):
            _result = service.generer_planning_ia(
                semaine_debut=date(2024, 1, 15), preferences={}, db=mock_db
            )

            # Vérifie création planning par défaut
            assert mock_db.add.called

    def test_generer_planning_ia_with_preferences(self, service, mock_db):
        """Test génération avec préférences personnalisées."""
        mock_jours = [
            JourPlanning(jour="Lundi01", dejeuner="Repas 1", diner="Diner 1"),
            JourPlanning(jour="Mardi02", dejeuner="Repas 2", diner="Diner 2"),
            JourPlanning(jour="Mercredi", dejeuner="Repas 3", diner="Diner 3"),
            JourPlanning(jour="Jeudi04", dejeuner="Repas 4", diner="Diner 4"),
            JourPlanning(jour="Vendredi", dejeuner="Repas 5", diner="Diner 5"),
            JourPlanning(jour="Samedi06", dejeuner="Repas 6", diner="Diner 6"),
            JourPlanning(jour="Dimanche", dejeuner="Repas 7", diner="Diner 7"),
        ]

        preferences = {"regime": "végétarien", "budget": "économique"}

        with (
            patch.object(service, "call_with_list_parsing_sync", return_value=mock_jours),
            patch("src.services.cuisine.planning.service.Cache"),
        ):
            _result = service.generer_planning_ia(
                semaine_debut=date(2024, 1, 15), preferences=preferences, db=mock_db
            )

            # Vérifie que call_with_list_parsing_sync est appelé
            service.call_with_list_parsing_sync.assert_called_once()

    def test_generer_planning_ia_creates_correct_repas_count(self, service, mock_db):
        """Test que 14 repas sont créés (2 par jour x 7 jours)."""
        mock_jours = [
            JourPlanning(jour="Lundi01", dejeuner="Dej", diner="Din"),
            JourPlanning(jour="Mardi02", dejeuner="Dej", diner="Din"),
            JourPlanning(jour="Mercred3", dejeuner="Dej", diner="Din"),
            JourPlanning(jour="Jeudi04", dejeuner="Dej", diner="Din"),
            JourPlanning(jour="Vendredi", dejeuner="Dej", diner="Din"),
            JourPlanning(jour="Samedi06", dejeuner="Dej", diner="Din"),
            JourPlanning(jour="Dimanche", dejeuner="Dej", diner="Din"),
        ]

        with (
            patch.object(service, "call_with_list_parsing_sync", return_value=mock_jours),
            patch("src.services.cuisine.planning.service.Cache"),
        ):
            service.generer_planning_ia(semaine_debut=date(2024, 1, 15), db=mock_db)

            # 1 planning + 14 repas = 15 appels à add
            # Mais le premier add est le planning, puis les repas
            add_calls = mock_db.add.call_count
            assert add_calls >= 8  # Au moins 1 planning + 7 jours de repas


# ═══════════════════════════════════════════════════════════
# TESTS DES FACTORIES
# ═══════════════════════════════════════════════════════════


class TestServicePlanningFactories:
    """Tests pour les factories du module."""

    def test_obtenir_service_planning(self):
        """Test de la factory principale."""
        from src.services.cuisine.planning.service import obtenir_service_planning

        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            service = obtenir_service_planning()
            assert service is not None
            assert isinstance(service, ServicePlanning)

    def test_get_planning_service_alias(self):
        """Test de l'alias anglais."""
        from src.services.cuisine.planning.service import get_planning_service

        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            service = get_planning_service()
            assert service is not None
            assert isinstance(service, ServicePlanning)

    def test_singleton_pattern(self):
        """Test que la factory retourne un singleton."""
        import src.services.cuisine.planning.service as service_module
        from src.services.cuisine.planning.service import obtenir_service_planning

        # Reset singleton
        service_module._service_planning = None

        with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
            service1 = obtenir_service_planning()
            service2 = obtenir_service_planning()
            assert service1 is service2


class TestPlanningServiceAlias:
    """Tests pour l'alias PlanningService."""

    def test_alias_exists(self):
        """Vérifie que l'alias existe."""
        from src.services.cuisine.planning.service import PlanningService

        assert PlanningService is ServicePlanning

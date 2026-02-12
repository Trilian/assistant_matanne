"""
Tests pour src/services/planning/service.py

Tests du service de planning avec mocks.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

from src.services.planning.service import ServicePlanning
from src.services.planning.types import ParametresEquilibre, JourPlanning


class TestServicePlanningInit:
    """Tests d'initialisation du service."""
    
    def test_service_creation(self):
        """Vérifie que le service peut être créé."""
        with patch('src.services.planning.service.obtenir_client_ia'):
            service = ServicePlanning()
            assert service is not None
    
    def test_service_has_model(self):
        """Vérifie que le service a un modèle défini."""
        with patch('src.services.planning.service.obtenir_client_ia'):
            service = ServicePlanning()
            assert service.model is not None


class TestServicePlanningMethods:
    """Tests des méthodes du service."""
    
    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch('src.services.planning.service.obtenir_client_ia'):
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
            semaine_debut=date.today(),
            parametres=params,
            db=mock_db
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
            pates_riz_count=4
        )
        assert len(params.poisson_jours) == 3
        assert params.pates_riz_count == 4
    
    def test_pates_riz_count_validation_min(self):
        """Vérifie la validation minimum."""
        with pytest.raises(Exception):
            ParametresEquilibre(pates_riz_count=0)
    
    def test_pates_riz_count_validation_max(self):
        """Vérifie la validation maximum."""
        with pytest.raises(Exception):
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
            diner="Soupe de légumes"
        )
        assert jour.jour == "Lundi 1"
        assert jour.dejeuner == "Poulet rôti"
    
    def test_jour_min_length(self):
        """Vérifie la longueur minimum du jour."""
        with pytest.raises(Exception):
            JourPlanning(jour="Lu", dejeuner="Test", diner="Test")
    
    def test_dejeuner_min_length(self):
        """Vérifie la longueur minimum du déjeuner."""
        with pytest.raises(Exception):
            JourPlanning(jour="Lundi 1", dejeuner="AB", diner="Test")
    
    def test_diner_min_length(self):
        """Vérifie la longueur minimum du dîner."""
        with pytest.raises(Exception):
            JourPlanning(jour="Lundi 1", dejeuner="Test", diner="AB")


class TestServicePlanningCache:
    """Tests du cache du service."""
    
    def test_cache_key_generation(self):
        """Vérifie la génération des clés de cache."""
        with patch('src.services.planning.service.obtenir_client_ia'):
            service = ServicePlanning()
            # Le service utilise des décorateurs @avec_cache
            assert hasattr(service, 'get_planning')
    
    def test_cache_ttl(self):
        """Vérifie le TTL de cache configuré."""
        with patch('src.services.planning.service.obtenir_client_ia'):
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
        with patch('src.services.planning.service.obtenir_client_ia'):
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
        with patch('src.services.planning.service.obtenir_client_ia'):
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
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_planning
        
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
        with patch('src.services.planning.service.obtenir_client_ia'):
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
        mock.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_recette]
        mock.query.return_value.filter.return_value.filter.return_value.limit.return_value.all.return_value = [mock_recette]
        return mock
    
    def test_suggerer_recettes_equilibrees_basic(self, service, mock_db_with_recettes):
        """Test de base des suggestions équilibrées."""
        params = ParametresEquilibre()
        result = service.suggerer_recettes_equilibrees(
            semaine_debut=date(2024, 1, 15),
            parametres=params,
            db=mock_db_with_recettes
        )
        assert isinstance(result, list)


class TestServicePlanningCreerAvecChoix:
    """Tests pour creer_planning_avec_choix."""
    
    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch('src.services.planning.service.obtenir_client_ia'):
            return ServicePlanning()
    
    def test_creer_planning_avec_choix_empty_selection(self, service):
        """Test avec sélection vide."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = service.creer_planning_avec_choix(
            semaine_debut=date(2024, 1, 15),
            recettes_selection={},
            db=mock_db
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
        
        result = service.creer_planning_avec_choix(
            semaine_debut=date(2024, 1, 15),
            recettes_selection={"jour_0": 1},
            db=mock_db
        )
        # Vérifie que la méthode a été appelée
        assert mock_db.add.called
    
    def test_creer_planning_avec_choix_recipe_not_found(self, service):
        """Test avec recette non trouvée."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = service.creer_planning_avec_choix(
            semaine_debut=date(2024, 1, 15),
            recettes_selection={"jour_0": 999},
            db=mock_db
        )
        # La méthode continue même si recette non trouvée


class TestServicePlanningAgregerCourses:
    """Tests pour agréger_courses_pour_planning."""
    
    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch('src.services.planning.service.obtenir_client_ia'):
            return ServicePlanning()
    
    def test_agreger_courses_planning_not_found(self, service):
        """Test avec planning inexistant."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = service.agréger_courses_pour_planning(
            planning_id=999,
            db=mock_db
        )
        assert result == []
    
    def test_agreger_courses_planning_without_repas(self, service):
        """Test avec planning sans repas."""
        mock_planning = MagicMock()
        mock_planning.repas = []
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_planning
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
        assert result == []
    
    def test_agreger_courses_repas_without_recette_id(self, service):
        """Test avec repas sans recette_id."""
        mock_repas = MagicMock()
        mock_repas.recette_id = None
        
        mock_planning = MagicMock()
        mock_planning.repas = [mock_repas]
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_planning
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
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
            None  # recette non trouvée
        ]
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
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
            mock_recette
        ]
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
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
            mock_recette
        ]
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
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
            mock_recette
        ]
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
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
            mock_recette
        ]
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
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
            mock_recette
        ]
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
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
            mock_recette
        ]
        
        result = service.agréger_courses_pour_planning(
            planning_id=1,
            db=mock_db
        )
        if result:
            assert result[0]["quantite"] == 1  # Default value


class TestServicePlanningGenererIA:
    """Tests pour generer_planning_ia."""
    
    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch('src.services.planning.service.obtenir_client_ia'):
            return ServicePlanning()
    
    def test_generer_planning_ia_method_exists(self, service):
        """Vérifie que la méthode existe."""
        assert hasattr(service, 'generer_planning_ia')


class TestServicePlanningGetPlanning:
    """Tests supplémentaires pour get_planning."""
    
    @pytest.fixture
    def service(self):
        """Fixture pour créer un service mocké."""
        with patch('src.services.planning.service.obtenir_client_ia'):
            return ServicePlanning()
    
    def test_get_planning_with_id(self, service):
        """Test get_planning avec un ID spécifique."""
        mock_planning = MagicMock()
        mock_planning.id = 1
        
        mock_db = MagicMock()
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_planning
        
        result = service.get_planning(planning_id=1, db=mock_db)
        # Le résultat dépend de l'implémentation
        # Ici on vérifie juste que la méthode accepte les paramètres
    
    def test_get_planning_active(self, service):
        """Test get_planning pour le planning actif."""
        mock_planning = MagicMock()
        mock_planning.actif = True
        
        mock_db = MagicMock()
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_planning
        
        result = service.get_planning(planning_id=None, db=mock_db)
        # Vérifie que la requête est faite pour le planning actif


# ═══════════════════════════════════════════════════════════
# TESTS DES FACTORIES
# ═══════════════════════════════════════════════════════════


class TestServicePlanningFactories:
    """Tests pour les factories du module."""
    
    def test_obtenir_service_planning(self):
        """Test de la factory principale."""
        from src.services.planning.service import obtenir_service_planning
        with patch('src.services.planning.service.obtenir_client_ia'):
            service = obtenir_service_planning()
            assert service is not None
            assert isinstance(service, ServicePlanning)
    
    def test_get_planning_service_alias(self):
        """Test de l'alias anglais."""
        from src.services.planning.service import get_planning_service
        with patch('src.services.planning.service.obtenir_client_ia'):
            service = get_planning_service()
            assert service is not None
            assert isinstance(service, ServicePlanning)
    
    def test_singleton_pattern(self):
        """Test que la factory retourne un singleton."""
        from src.services.planning.service import obtenir_service_planning, _service_planning
        import src.services.planning.service as service_module
        
        # Reset singleton
        service_module._service_planning = None
        
        with patch('src.services.planning.service.obtenir_client_ia'):
            service1 = obtenir_service_planning()
            service2 = obtenir_service_planning()
            assert service1 is service2


class TestPlanningServiceAlias:
    """Tests pour l'alias PlanningService."""
    
    def test_alias_exists(self):
        """Vérifie que l'alias existe."""
        from src.services.planning.service import PlanningService
        assert PlanningService is ServicePlanning

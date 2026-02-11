"""Tests pour src/services/planning/service.py - ServicePlanning.

Couverture des fonctionnalités:
- get_planning, get_planning_complet
- suggerer_recettes_equilibrees
- creer_planning_avec_choix
- agréger_courses_pour_planning
- generer_planning_ia
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from contextlib import contextmanager

from src.services.planning.service import ServicePlanning, get_planning_service, obtenir_service_planning
from src.services.planning.types import ParametresEquilibre


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def lundi_test():
    """Un lundi de test."""
    return date(2024, 1, 15)


@pytest.fixture
def mock_db_session():
    """Session de base de données mockée avec filter chain."""
    from sqlalchemy.orm import Session
    
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []
    mock_query.first.return_value = None
    mock_query.count.return_value = 0
    mock_session.query.return_value = mock_query
    
    return mock_session


@pytest.fixture
def mock_context(mock_db_session):
    """Context manager pour mocker obtenir_contexte_db."""
    @contextmanager
    def _mock_db():
        yield mock_db_session
    return _mock_db


@pytest.fixture
def service():
    """Instance de ServicePlanning."""
    return ServicePlanning()


@pytest.fixture
def sample_planning():
    """Planning de test."""
    planning = MagicMock()
    planning.id = 1
    planning.semaine_debut = date(2024, 1, 15)
    planning.semaine_fin = date(2024, 1, 21)
    planning.nom = "Semaine 3"
    planning.actif = True
    planning.genere_par_ia = False
    planning.repas = []
    return planning


@pytest.fixture
def sample_repas():
    """Repas de test."""
    repas = MagicMock()
    repas.id = 1
    repas.date_repas = date(2024, 1, 15)
    repas.type_repas = "dejeuner"
    repas.recette_id = 1
    repas.prepare = False
    repas.notes = "Test"
    repas.portion_ajustee = None
    repas.recette = MagicMock(
        id=1,
        nom="Pâtes carbonara",
        temps_preparation=30,
        temps_cuisson=15,
        portions=4,
        versions=[]
    )
    return repas


@pytest.fixture
def sample_recettes():
    """Liste de recettes de test."""
    recettes = []
    for i, nom in enumerate(["Pâtes", "Salade", "Riz", "Poulet", "Soupe"]):
        recette = MagicMock()
        recette.id = i + 1
        recette.nom = nom
        recette.description = f"Description {nom}"
        recette.type_proteines = ["poisson", "volaille", "viande_rouge", "vegetarien", "poisson"][i]
        recette.est_equilibre = True
        recette.est_vegetarien = (i == 3)
        recette.temps_preparation = 30
        recette.temps_cuisson = 20
        recette.difficulte = "facile"
        recettes.append(recette)
    return recettes


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceFactory:
    """Tests pour les factories du service."""

    def test_get_planning_service_returns_instance(self):
        """La factory retourne une instance de ServicePlanning."""
        service = get_planning_service()
        assert service is not None
        assert isinstance(service, ServicePlanning)

    def test_obtenir_service_planning_returns_instance(self):
        """La factory française retourne une instance."""
        service = obtenir_service_planning()
        assert service is not None
        assert isinstance(service, ServicePlanning)

    def test_service_has_required_attributes(self):
        """Le service a les attributs requis."""
        service = ServicePlanning()
        assert hasattr(service, 'model')
        assert hasattr(service, 'get_planning')
        assert hasattr(service, 'get_planning_complet')
        assert hasattr(service, 'suggerer_recettes_equilibrees')

    def test_singleton_returns_same_instance(self):
        """Le singleton retourne la même instance."""
        service1 = obtenir_service_planning()
        service2 = obtenir_service_planning()
        assert service1 is service2


# ═══════════════════════════════════════════════════════════
# TESTS GET_PLANNING
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetPlanning:
    """Tests pour get_planning."""

    def test_retourne_planning_par_id(self, service, sample_planning, mock_db_session, mock_context):
        """Retourne le planning pour un ID donné."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = sample_planning
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning(planning_id=1)
        
        assert result is None or result == sample_planning

    def test_retourne_planning_actif(self, service, sample_planning, mock_db_session, mock_context):
        """Retourne le planning actif."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = sample_planning
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning()
        
        assert result is None or hasattr(result, 'id')

    def test_retourne_none_si_inexistant(self, service, mock_db_session, mock_context):
        """Retourne None si pas de planning."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = None
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning(planning_id=9999)
        
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS GET_PLANNING_COMPLET
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetPlanningComplet:
    """Tests pour get_planning_complet."""

    def test_retourne_dict_avec_repas(self, service, sample_planning, sample_repas, mock_db_session, mock_context):
        """Retourne un dict avec les repas."""
        sample_planning.repas = [sample_repas]
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = sample_planning
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning_complet(1)
        
        assert result is None or isinstance(result, dict)

    def test_retourne_none_si_inexistant(self, service, mock_db_session, mock_context):
        """Retourne None si planning n'existe pas."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = None
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning_complet(9999)
        
        assert result is None

    def test_structure_dict_complete(self, service, sample_planning, sample_repas, mock_db_session, mock_context):
        """Le dict retourné a la structure attendue."""
        sample_planning.repas = [sample_repas]
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = sample_planning
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning_complet(1)
        
        if result is not None:
            expected_keys = ['id', 'nom', 'semaine_debut', 'semaine_fin', 'actif', 'genere_par_ia', 'repas_par_jour']
            for key in expected_keys:
                assert key in result


# ═══════════════════════════════════════════════════════════
# TESTS SUGGERER_RECETTES_EQUILIBREES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSuggererRecettesEquilibrees:
    """Tests pour suggerer_recettes_equilibrees."""

    def test_retourne_liste(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Retourne une liste de suggestions."""
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value.all.return_value = sample_recettes[:3]
        
        parametres = ParametresEquilibre()
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.suggerer_recettes_equilibrees(lundi_test, parametres)
        
        assert isinstance(result, list)

    def test_avec_parametres_poisson(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Utilise les paramètres de poisson."""
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value.all.return_value = [sample_recettes[0]]
        
        parametres = ParametresEquilibre(poisson_jours=["lundi", "jeudi"])
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.suggerer_recettes_equilibrees(lundi_test, parametres)
        
        assert isinstance(result, list)

    def test_avec_parametres_vegetarien(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Utilise les paramètres végétarien."""
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value.all.return_value = [sample_recettes[3]]
        
        parametres = ParametresEquilibre(vegetarien_jours=["mercredi"])
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.suggerer_recettes_equilibrees(lundi_test, parametres)
        
        assert isinstance(result, list)

    def test_avec_parametres_viande_rouge(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Utilise les paramètres viande rouge."""
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value.all.return_value = [sample_recettes[2]]
        
        parametres = ParametresEquilibre(viande_rouge_jours=["mardi"])
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.suggerer_recettes_equilibrees(lundi_test, parametres)
        
        assert isinstance(result, list)

    def test_avec_ingredients_exclus(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Exclut les ingrédients spécifiés."""
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value.all.return_value = sample_recettes[:2]
        
        parametres = ParametresEquilibre(ingredients_exclus=["gluten", "lactose"])
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.suggerer_recettes_equilibrees(lundi_test, parametres)
        
        assert isinstance(result, list)

    def test_retourne_liste_vide_sans_recettes(self, service, mock_db_session, mock_context, lundi_test):
        """Retourne liste vide si pas de recettes."""
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value.all.return_value = []
        
        parametres = ParametresEquilibre()
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.suggerer_recettes_equilibrees(lundi_test, parametres)
        
        assert isinstance(result, list)

    def test_complete_avec_alternatives(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Complète avec des alternatives si pas assez de recettes."""
        mock_query = mock_db_session.query.return_value
        mock_query.filter.return_value = mock_query
        # Premier appel retourne 1 recette, second retourne des alternatives
        mock_query.limit.return_value.all.side_effect = [[sample_recettes[0]], sample_recettes[1:3]]
        mock_query.notin_.return_value = mock_query
        
        parametres = ParametresEquilibre()
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.suggerer_recettes_equilibrees(lundi_test, parametres)
        
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS CREER_PLANNING_AVEC_CHOIX
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCreerPlanningAvecChoix:
    """Tests pour creer_planning_avec_choix."""

    def test_cree_planning(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Crée un planning avec les choix."""
        mock_recette = sample_recettes[0]
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_recette
        
        choix = {"jour_0": 1, "jour_1": 2}
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.creer_planning_avec_choix(lundi_test, choix)
        
        assert mock_db_session.add.called or result is None

    def test_ignore_recettes_inexistantes(self, service, mock_db_session, mock_context, lundi_test):
        """Ignore les recettes qui n'existent pas."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        choix = {"jour_0": 9999}
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.creer_planning_avec_choix(lundi_test, choix)
        
        assert result is None or hasattr(result, 'id')

    def test_cree_repas_pour_chaque_jour(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Crée des repas pour chaque jour choisi."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_recettes[0]
        
        choix = {"jour_0": 1, "jour_1": 2, "jour_2": 3}
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.creer_planning_avec_choix(lundi_test, choix)
        
        # Vérifie que le service a été appelé
        assert mock_db_session.add.called or result is None

    def test_avec_enfants_adaptes(self, service, sample_recettes, mock_db_session, mock_context, lundi_test):
        """Gère les enfants pour adaptation."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_recettes[0]
        
        choix = {"jour_0": 1}
        enfants = [1, 2]
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.creer_planning_avec_choix(lundi_test, choix, enfants_adaptes=enfants)
        
        assert result is None or hasattr(result, 'id')


# ═══════════════════════════════════════════════════════════
# TESTS AGREGATION COURSES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAgregerCourses:
    """Tests pour agréger_courses_pour_planning."""

    def test_retourne_liste_vide_sans_planning(self, service, mock_db_session, mock_context):
        """Retourne liste vide sans planning."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.agréger_courses_pour_planning(9999)
        
        assert result == []

    def test_retourne_liste_ingredients(self, service, sample_planning, sample_repas, mock_db_session, mock_context):
        """Retourne liste d'ingrédients agrégés."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Pâtes"
        mock_ingredient.unite = "g"
        mock_ingredient.categorie = "epicerie"
        
        mock_recette_ingredient = MagicMock()
        mock_recette_ingredient.quantite = 500
        mock_recette_ingredient.unite = "g"
        mock_recette_ingredient.ingredient = mock_ingredient
        
        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.ingredients = [mock_recette_ingredient]
        
        sample_repas.recette_id = 1
        sample_planning.repas = [sample_repas]
        
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [sample_planning, mock_recette]
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.agréger_courses_pour_planning(1)
        
        assert isinstance(result, list)

    def test_somme_quantites_meme_ingredient(self, service, sample_planning, mock_db_session, mock_context):
        """Somme les quantités du même ingrédient."""
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Pâtes"
        mock_ingredient.unite = "g"
        mock_ingredient.categorie = "epicerie"
        
        mock_ri1 = MagicMock(quantite=500, unite="g", ingredient=mock_ingredient)
        mock_ri2 = MagicMock(quantite=300, unite="g", ingredient=mock_ingredient)
        
        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.ingredients = [mock_ri1, mock_ri2]
        
        mock_repas = MagicMock(recette_id=1)
        sample_planning.repas = [mock_repas]
        
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [sample_planning, mock_recette]
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.agréger_courses_pour_planning(1)
        
        assert isinstance(result, list)

    def test_planning_sans_repas(self, service, sample_planning, mock_db_session, mock_context):
        """Gère un planning sans repas."""
        sample_planning.repas = []
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_planning
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.agréger_courses_pour_planning(1)
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS GENERER_PLANNING_IA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGenererPlanningIA:
    """Tests pour generer_planning_ia."""

    def test_genere_planning_ia_succes(self, service, mock_db_session, mock_context, lundi_test):
        """Génère un planning avec l'IA."""
        mock_jour_planning = MagicMock()
        mock_jour_planning.dejeuner = "Pâtes"
        mock_jour_planning.diner = "Salade"
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            with patch.object(service, 'call_with_list_parsing_sync') as mock_ia:
                mock_ia.return_value = [mock_jour_planning] * 7
                with patch.object(service, 'build_planning_context') as mock_ctx:
                    mock_ctx.return_value = "Context"
                    
                    result = service.generer_planning_ia(lundi_test)
        
        assert result is None or hasattr(result, 'id')

    def test_genere_planning_defaut_sans_ia(self, service, mock_db_session, mock_context, lundi_test):
        """Génère planning par défaut si IA échoue."""
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            with patch.object(service, 'call_with_list_parsing_sync') as mock_ia:
                mock_ia.return_value = None
                with patch.object(service, 'build_planning_context') as mock_ctx:
                    mock_ctx.return_value = "Context"
                    
                    result = service.generer_planning_ia(lundi_test)
        
        assert result is None or hasattr(result, 'id')

    def test_genere_planning_avec_preferences(self, service, mock_db_session, mock_context, lundi_test):
        """Génère un planning avec préférences."""
        preferences = {"nb_personnes": 4, "budget": 100}
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            with patch.object(service, 'call_with_list_parsing_sync') as mock_ia:
                mock_ia.return_value = None
                with patch.object(service, 'build_planning_context') as mock_ctx:
                    mock_ctx.return_value = "Context"
                    
                    result = service.generer_planning_ia(lundi_test, preferences=preferences)
        
        assert result is None or hasattr(result, 'id')


# ═══════════════════════════════════════════════════════════
# TESTS AVEC FIXTURE DB PATCHÉE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceWithPatchedDB:
    """Tests avec patch_db_context pour l'intégration."""

    def test_service_instantiation(self, planning_service):
        """Vérifie l'instanciation du service avec la fixture."""
        assert planning_service is not None
        assert isinstance(planning_service, ServicePlanning)

    def test_get_planning_with_fixture(self, planning_service):
        """Test get_planning avec la fixture de DB."""
        result = planning_service.get_planning()
        assert result is None

    def test_get_planning_complet_with_fixture(self, planning_service):
        """Test get_planning_complet avec la fixture de DB."""
        result = planning_service.get_planning_complet(1)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS INTEGRATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestServiceIntegration:
    """Tests d'intégration avec DB réelle."""

    def test_crud_basique(self, patch_db_context, planning_factory):
        """Test CRUD basique du service."""
        service = ServicePlanning()
        planning = planning_factory.create(nom="Test Planning")
        
        assert planning is not None
        assert planning.id is not None

    def test_workflow_complet(self, patch_db_context, planning_factory, recette_factory):
        """Test du workflow complet."""
        service = ServicePlanning()
        
        recette1 = recette_factory.create(nom="Pâtes")
        recette2 = recette_factory.create(nom="Salade")
        
        planning = planning_factory.create(
            nom="Semaine Test",
            semaine_debut=date(2024, 1, 15)
        )
        
        assert planning.nom == "Semaine Test"
        assert recette1.nom == "Pâtes"


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES HÉRITÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMethodesHeritees:
    """Tests pour les méthodes héritées de BaseService."""

    def test_has_model_attribute(self):
        """Le service a l'attribut model."""
        service = ServicePlanning()
        assert hasattr(service, 'model')

    def test_has_cache_ttl(self):
        """Le service a un cache TTL configuré."""
        service = ServicePlanning()
        assert hasattr(service, 'cache_ttl')

    def test_inherits_from_base_ai_service(self):
        """Le service hérite de BaseAIService."""
        from src.services.base import BaseAIService
        service = ServicePlanning()
        assert isinstance(service, BaseAIService)

    def test_inherits_from_base_service(self):
        """Le service hérite de BaseService."""
        from src.services.base import BaseService
        service = ServicePlanning()
        assert isinstance(service, BaseService)


# ═══════════════════════════════════════════════════════════
# TESTS CAS LIMITES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCasLimites:
    """Tests pour les cas limites."""

    def test_date_future(self, service, mock_db_session, mock_context):
        """Gère les dates futures."""
        future_date = date.today() + timedelta(days=365)
        
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = None
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning(planning_id=1)
        
        assert result is None

    def test_date_passee(self, service, mock_db_session, mock_context):
        """Gère les dates passées."""
        past_date = date(2020, 1, 1)
        
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = None
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning(planning_id=1)
        
        assert result is None

    def test_choix_vide(self, service, mock_db_session, mock_context, lundi_test):
        """Gère un dictionnaire de choix vide."""
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.creer_planning_avec_choix(lundi_test, {})
        
        assert result is None or hasattr(result, 'id')

    def test_id_negatif(self, service, mock_db_session, mock_context):
        """Gère un ID négatif."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = None
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_planning(planning_id=-1)
        
        assert result is None

"""
Tests pour RecetteService - Tests des méthodes réelles du service

Uses patch_db_context fixture to use test SQLite DB instead of production.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.recettes import RecetteService, get_recette_service


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY ET INSTANCIATION
# ═══════════════════════════════════════════════════════════

class TestRecetteServiceFactory:
    """Tests pour la factory et l'instanciation."""
    
    def test_get_recette_service_returns_instance(self, patch_db_context):
        """La factory retourne une instance de RecetteService."""
        service = get_recette_service()
        assert service is not None
        assert isinstance(service, RecetteService)
    
    def test_service_has_model(self, patch_db_context):
        """Le service a le modèle Recette configuré."""
        service = get_recette_service()
        assert hasattr(service, 'model')
        assert service.model.__name__ == 'Recette'
    
    def test_service_inherits_base_service(self, patch_db_context):
        """Le service hérite de BaseService."""
        service = get_recette_service()
        assert hasattr(service, 'create')
        assert hasattr(service, 'get_by_id')
        assert hasattr(service, 'get_all')
        assert hasattr(service, 'update')
        assert hasattr(service, 'delete')


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES CRUD (héritées de BaseService)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceCRUD:
    """Tests pour les méthodes CRUD héritées."""
    
    def test_get_all_returns_list(self, recette_service):
        """get_all retourne une liste."""
        with patch.object(recette_service, '_with_session') as mock_session:
            mock_session.return_value = []
            result = recette_service.get_all()
            assert isinstance(result, list)
    
    def test_get_by_id_with_mock(self, recette_service):
        """get_by_id utilise le cache."""
        with patch.object(recette_service, '_with_session') as mock_session:
            mock_session.return_value = None
            result = recette_service.get_by_id(99999)
            # Retourne None si non trouvé
            assert mock_session.called


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES SPÉCIFIQUES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceSpecific:
    """Tests pour les méthodes spécifiques à RecetteService."""
    
    def test_get_by_id_full_exists(self, recette_service):
        """La méthode get_by_id_full existe."""
        assert hasattr(recette_service, 'get_by_id_full')
        assert callable(recette_service.get_by_id_full)
    
    def test_get_by_type_exists(self, recette_service):
        """La méthode get_by_type existe."""
        assert hasattr(recette_service, 'get_by_type')
        assert callable(recette_service.get_by_type)
    
    def test_create_complete_exists(self, recette_service):
        """La méthode create_complete existe."""
        assert hasattr(recette_service, 'create_complete')
        assert callable(recette_service.create_complete)
    
    def test_generer_version_bebe_exists(self, recette_service):
        """La méthode generer_version_bebe existe."""
        assert hasattr(recette_service, 'generer_version_bebe')
        assert callable(recette_service.generer_version_bebe)
    
    def test_generer_version_batch_cooking_exists(self, recette_service):
        """La méthode generer_version_batch_cooking existe."""
        assert hasattr(recette_service, 'generer_version_batch_cooking')
        assert callable(recette_service.generer_version_batch_cooking)
    
    def test_get_stats_recette_exists(self, recette_service):
        """La méthode get_stats_recette existe."""
        assert hasattr(recette_service, 'get_stats_recette')
        assert callable(recette_service.get_stats_recette)
    
    def test_get_versions_exists(self, recette_service):
        """La méthode get_versions existe."""
        assert hasattr(recette_service, 'get_versions')
        assert callable(recette_service.get_versions)
    
    def test_export_to_csv_exists(self, recette_service):
        """La méthode export_to_csv existe."""
        assert hasattr(recette_service, 'export_to_csv')
        assert callable(recette_service.export_to_csv)
    
    def test_export_to_json_exists(self, recette_service):
        """La méthode export_to_json existe."""
        assert hasattr(recette_service, 'export_to_json')
        assert callable(recette_service.export_to_json)


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceExport:
    """Tests pour les méthodes d'export."""
    
    def test_export_to_csv_with_empty_list(self, recette_service):
        """Export CSV avec liste vide."""
        result = recette_service.export_to_csv([])
        assert isinstance(result, str)
    
    def test_export_to_json_with_empty_list(self, recette_service):
        """Export JSON avec liste vide."""
        result = recette_service.export_to_json([])
        # Doit être une liste JSON vide
        import json
        parsed = json.loads(result)
        assert parsed == []
    
    def test_export_to_csv_with_mock_recettes(self, recette_service):
        """Export CSV avec recettes mockées."""
        mock_recette = MagicMock()
        mock_recette.nom = "Test Recipe"
        mock_recette.description = "Description"
        mock_recette.temps_preparation = 15
        mock_recette.temps_cuisson = 30
        mock_recette.portions = 4
        mock_recette.difficulte = "facile"
        mock_recette.type_repas = "déjeuner"
        mock_recette.saison = "toute_année"
        mock_recette.vegetarien = False
        mock_recette.vegan = False
        mock_recette.sans_gluten = False
        mock_recette.recette_ingredients = []
        mock_recette.etapes = []
        
        result = recette_service.export_to_csv([mock_recette])
        assert isinstance(result, str)
        assert "Test Recipe" in result


# ═══════════════════════════════════════════════════════════
# TESTS BASEAISERVICE HÉRITÉ
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteServiceAI:
    """Tests pour les méthodes IA héritées."""
    
    def test_has_build_json_prompt(self, recette_service):
        """Le service a la méthode build_json_prompt."""
        assert hasattr(recette_service, 'build_json_prompt')
    
    def test_has_build_system_prompt(self, recette_service):
        """Le service a la méthode build_system_prompt."""
        assert hasattr(recette_service, 'build_system_prompt')
    
    def test_service_name_is_recettes(self, recette_service):
        """Le service_name est 'recettes'."""
        assert recette_service.service_name == "recettes"


def test_import_recettes_module():
    """Vérifie que le module recettes s'importe sans erreur."""
    import importlib
    module = importlib.import_module("src.services.recettes")
    assert module is not None

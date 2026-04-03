"""
Tests simplifiÃ©s pour les 6 nouveaux services IA du Sprint 13.
"""

import pytest
from unittest.mock import Mock, patch

# Imports services
from src.services.inventaire.ia_service import (
    get_inventaire_ai_service,
    InventaireAIService,
)
from src.services.planning.ia_service import (
    get_planning_ai_service,
    PlanningAIService,
)
from src.services.integrations.meteo_impact_ai import (
    get_meteo_impact_ai_service,
    MeteoImpactAIService,
)
from src.services.integrations.habitudes_ia import (
    get_habitudes_ai_service,
    HabitudesAIService,
)
from src.services.maison.projets_ia_service import (
    get_projets_maison_ai_service,
    ProjetsMaisonAIService,
)
from src.services.cuisine.nutrition_famille_ia import (
    get_nutrition_famille_ai_service,
    NutritionFamilleAIService,
)


class TestInventoryAIServices:
    """Tests simples pour les 6 services IA"""

    def test_inventaire_ai_service_creation(self):
        """Test crÃ©ation du service inventaire"""
        service = InventaireAIService()
        assert service is not None
        assert service.service_name == "inventaire_ia"

    def test_planning_ai_service_creation(self):
        """Test crÃ©ation du service planning"""
        service = PlanningAIService()
        assert service is not None
        assert service.service_name == "planning_ia"

    def test_meteo_impact_ai_service_creation(self):
        """Test crÃ©ation du service mÃ©tÃ©o"""
        service = MeteoImpactAIService()
        assert service is not None
        assert service.service_name == "meteo_impact"

    def test_habitudes_ai_service_creation(self):
        """Test crÃ©ation du service habitudes"""
        service = HabitudesAIService()
        assert service is not None
        assert service.service_name == "habitudes_ia"

    def test_projets_maison_ai_service_creation(self):
        """Test crÃ©ation du service projets"""
        service = ProjetsMaisonAIService()
        assert service is not None
        assert service.service_name == "projets_maison_ia"

    def test_nutrition_famille_ai_service_creation(self):
        """Test crÃ©ation du service nutrition"""
        service = NutritionFamilleAIService()
        assert service is not None
        assert service.service_name == "nutrition_famille_ia"


class TestFactoryFunctions:
    """Tests des fonctions factory"""

    def test_inventaire_factory(self):
        """Test factory inventaire"""
        service = get_inventaire_ai_service()
        assert isinstance(service, InventaireAIService)

    def test_planning_factory(self):
        """Test factory planning"""
        service = get_planning_ai_service()
        assert isinstance(service, PlanningAIService)

    def test_meteo_factory(self):
        """Test factory mÃ©tÃ©o"""
        service = get_meteo_impact_ai_service()
        assert isinstance(service, MeteoImpactAIService)

    def test_habitudes_factory(self):
        """Test factory habitudes"""
        service = get_habitudes_ai_service()
        assert isinstance(service, HabitudesAIService)

    def test_projets_factory(self):
        """Test factory projets"""
        service = get_projets_maison_ai_service()
        assert isinstance(service, ProjetsMaisonAIService)

    def test_nutrition_factory(self):
        """Test factory nutrition"""
        service = get_nutrition_famille_ai_service()
        assert isinstance(service, NutritionFamilleAIService)


class TestServiceInheritance:
    """Tests d'hÃ©ritage de BaseAIService"""

    def test_inventaire_inherits_base_ai_service(self):
        """VÃ©rifier hÃ©ritage"""
        service = InventaireAIService()
        assert hasattr(service, "call_with_cache")
        assert hasattr(service, "call_with_dict_parsing_sync")
        assert hasattr(service, "call_with_list_parsing_sync")

    def test_planning_inherits_base_ai_service(self):
        """VÃ©rifier hÃ©ritage"""
        service = PlanningAIService()
        assert hasattr(service, "call_with_cache")
        assert hasattr(service, "call_with_dict_parsing_sync")

    def test_all_services_have_cache_prefix(self):
        """VÃ©rifier tous les services ont un cache_prefix"""
        services = [
            InventaireAIService(),
            PlanningAIService(),
            MeteoImpactAIService(),
            HabitudesAIService(),
            ProjetsMaisonAIService(),
            NutritionFamilleAIService(),
        ]

        for service in services:
            assert service.cache_prefix is not None
            assert isinstance(service.cache_prefix, str)
            assert len(service.cache_prefix) > 0

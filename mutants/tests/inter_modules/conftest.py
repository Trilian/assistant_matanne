"""Fixtures et configuration pour les tests inter-modules."""

import pytest


@pytest.fixture(scope="session", autouse=True)
def register_inter_module_services():
    """Enregistre tous les services inter-modules via @service_factory.
    
    Cette fixture s'exécute automatiquement au début de la session de test
    pour s'assurer que les services NIM1-NIM4 sont disponibles dans le registre.
    """
    # Importer les modules qui contiennent les factories @service_factory
    from src.services.cuisine.inter_module_inventaire_budget import get_inventaire_budget_service
    from src.services.cuisine.inter_module_planning_jardin import get_planning_jardin_service
    from src.services.cuisine.inter_module_garmin_nutrition_adultes import get_garmin_nutrition_adultes_service
    from src.services.utilitaires.inter_module_dashboard_actions import get_dashboard_actions_rapides_service
    
    # L'import des modules a exécuté les décorateurs @service_factory
    # Les services sont maintenant enregistrés dans le registre
    yield

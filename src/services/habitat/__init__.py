"""Services du module Habitat."""

from src.services.core.registry import service_factory

from .scenarios_service import ScenariosHabitatService


@service_factory("habitat_scenarios", tags={"habitat", "ia", "decision"})
def obtenir_service_scenarios_habitat() -> ScenariosHabitatService:
    """Factory singleton du service de scénarios Habitat."""
    return ScenariosHabitatService()


get_habitat_scenarios_service = obtenir_service_scenarios_habitat

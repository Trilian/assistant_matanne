"""Façade cuisine pour les fonctionnalités IA transverses."""

from __future__ import annotations

from typing import Any

from src.services.core.registry import service_factory
from src.services.ia_avancee import get_innovations_service


class ServiceInnovationsCuisine:
    """Expose les innovations cuisine/courses depuis un namespace de domaine stable."""

    @staticmethod
    def _service() -> Any:
        return get_innovations_service()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._service(), name)

    def suggerer_repas_ce_soir(self, *, temps_disponible_min: int, humeur: str) -> Any:
        return self._service().suggerer_repas_ce_soir(
            temps_disponible_min=temps_disponible_min,
            humeur=humeur,
        )

    def analyser_patterns_alimentaires(self, *, periode_jours: int) -> Any:
        return self._service().analyser_patterns_alimentaires(periode_jours=periode_jours)

    def appliquer_saisonnalite_intelligente(self) -> Any:
        return self._service().appliquer_saisonnalite_intelligente()

    def proposer_repas_adapte_garmin(self, *, user_id: int | None = None) -> Any:
        return self._service().proposer_repas_adapte_garmin(user_id=user_id)

    def generer_planification_hebdo_complete(self, *, user_id: str = "") -> Any:
        return self._service().generer_planification_hebdo_complete(user_id=user_id)

    def proposer_batch_cooking_intelligent(self, *, user_id: str = "") -> Any:
        return self._service().proposer_batch_cooking_intelligent(user_id=user_id)



@service_factory("cuisine_innovations", tags={"cuisine", "ia"})
def obtenir_service_innovations_cuisine() -> ServiceInnovationsCuisine:
    """Retourne la façade IA cuisine consolidée."""
    return ServiceInnovationsCuisine()

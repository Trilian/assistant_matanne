"""Façade famille pour les fonctionnalités IA consolidées hors `experimental/`."""

from __future__ import annotations

from typing import Any

from src.services.core.registry import service_factory
from src.services.ia_avancee import get_innovations_service


class ServiceInnovationsFamille:
    """Expose les fonctions famille/routines/vacances depuis le package métier."""

    @staticmethod
    def _service() -> Any:
        return get_innovations_service()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._service(), name)

    def coach_routines_ia(self) -> Any:
        return self._service().coach_routines_ia()

    def generer_planning_jules_adaptatif(self) -> Any:
        return self._service().generer_planning_jules_adaptatif()

    def calculer_score_famille_hebdo(self) -> Any:
        return self._service().calculer_score_famille_hebdo()

    def obtenir_mode_vacances(self, *, user_id: str = "") -> Any:
        return self._service().obtenir_mode_vacances(user_id=user_id)

    def configurer_mode_vacances(
        self,
        *,
        user_id: str = "",
        actif: bool,
        checklist_voyage_auto: bool,
    ) -> Any:
        return self._service().configurer_mode_vacances(
            user_id=user_id,
            actif=actif,
            checklist_voyage_auto=checklist_voyage_auto,
        )

    def calculer_score_bien_etre(self) -> Any:
        return self._service().calculer_score_bien_etre()

    def enrichir_contacts(self) -> Any:
        return self._service().enrichir_contacts()


@service_factory("famille_innovations", tags={"famille", "ia"})
def obtenir_service_innovations_famille() -> ServiceInnovationsFamille:
    """Retourne la façade IA famille consolidée."""
    return ServiceInnovationsFamille()

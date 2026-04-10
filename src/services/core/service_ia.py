"""Façade core pour le pilotage IA et les insights contextuels."""

from __future__ import annotations

from typing import Any

from src.services.core.registry import service_factory
from src.services.ia_avancee import get_innovations_service


class ServiceInnovationsCore:
    """Expose les fonctions de pilotage IA via un namespace core stable."""

    @staticmethod
    def _service() -> Any:
        return get_innovations_service()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._service(), name)

    def apprendre_habitudes_utilisateur(self) -> Any:
        return self._service().apprendre_habitudes_utilisateur()

    def generer_alertes_contextuelles(self) -> Any:
        return self._service().generer_alertes_contextuelles()

    def obtenir_mode_pilote_automatique(self, *, user_id: int | None = None) -> Any:
        return self._service().obtenir_mode_pilote_automatique(user_id=user_id)

    def configurer_mode_pilote_automatique(
        self, *, user_id: int | None = None, actif: bool, niveau_autonomie: str
    ) -> Any:
        return self._service().configurer_mode_pilote_automatique(
            user_id=user_id,
            actif=actif,
            niveau_autonomie=niveau_autonomie,
        )

    def generer_insights_quotidiens(self, *, limite: int = 2) -> Any:
        return self._service().generer_insights_quotidiens(limite=limite)

    def analyser_meteo_contextuelle(self) -> Any:
        return self._service().analyser_meteo_contextuelle()

    def analyser_preferences_apprises(self, *, user_id: str = "") -> Any:
        return self._service().analyser_preferences_apprises(user_id=user_id)

    def obtenir_capacites_telegram_conversationnelles(self) -> Any:
        return self._service().obtenir_capacites_telegram_conversationnelles()


@service_factory("core_innovations", tags={"core", "ia"})
def obtenir_service_innovations_core() -> ServiceInnovationsCore:
    """Retourne la façade core des innovations consolidées."""
    return ServiceInnovationsCore()

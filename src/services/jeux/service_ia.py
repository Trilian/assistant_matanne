"""Façade jeux pour les analyses Loto/Euromillions consolidées."""

from __future__ import annotations

from typing import Any

from src.services.core.registry import service_factory
from src.services.ia_avancee import get_innovations_service


class ServiceInnovationsJeux:
    """Expose les innovations liées aux jeux depuis un namespace métier stable."""

    @staticmethod
    def _service() -> Any:
        return get_innovations_service()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._service(), name)

    def analyser_tendances_loto(self, *, type_jeu: str = "loto") -> Any:
        return self._service().analyser_tendances_loto(type_jeu=type_jeu)


@service_factory("jeux_innovations", tags={"jeux", "ia"})
def obtenir_service_innovations_jeux() -> ServiceInnovationsJeux:
    """Retourne la façade IA jeux consolidée."""
    return ServiceInnovationsJeux()

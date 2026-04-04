"""Façade maison/habitat pour les analyses énergie et consommation."""

from __future__ import annotations

from typing import Any

from src.services.core.registry import service_factory
from src.services.ia_avancee import get_innovations_service


class ServiceInnovationsMaison:
    """Expose les analyses énergie consolidées dans le domaine maison."""

    @staticmethod
    def _service() -> Any:
        return get_innovations_service()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._service(), name)

    def detecter_anomalies_energie(self) -> Any:
        return self._service().detecter_anomalies_energie()

    def comparer_fournisseurs_energie(
        self,
        *,
        prix_kwh_actuel_eur: float,
        abonnement_mensuel_eur: float,
    ) -> Any:
        return self._service().comparer_fournisseurs_energie(
            prix_kwh_actuel_eur=prix_kwh_actuel_eur,
            abonnement_mensuel_eur=abonnement_mensuel_eur,
        )

    def obtenir_tableau_bord_energie_temps_reel(self) -> Any:
        return self._service().obtenir_tableau_bord_energie_temps_reel()


@service_factory("maison_innovations", tags={"maison", "energie", "ia"})
def obtenir_service_innovations_maison() -> ServiceInnovationsMaison:
    """Retourne la façade IA maison consolidée."""
    return ServiceInnovationsMaison()

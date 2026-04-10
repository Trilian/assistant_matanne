"""Façade rapports pour les synthèses IA migrées depuis `experimental/`."""

from __future__ import annotations

from typing import Any

from src.services.core.registry import service_factory
from src.services.ia_avancee import get_innovations_service


class ServiceInnovationsRapports:
    """Expose les rapports et résumés IA depuis le package rapports."""

    @staticmethod
    def _service() -> Any:
        return get_innovations_service()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._service(), name)

    def generer_resume_mensuel_ia(self) -> Any:
        return self._service().generer_resume_mensuel_ia()

    def generer_bilan_annuel(self, *, annee: int | None = None) -> Any:
        return self._service().generer_bilan_annuel(annee=annee)

    def generer_journal_familial_auto(self) -> Any:
        return self._service().generer_journal_familial_auto()

    def generer_journal_familial_pdf(self) -> Any:
        return self._service().generer_journal_familial_pdf()

    def generer_rapport_mensuel_pdf(self, *, mois: str | None = None) -> Any:
        return self._service().generer_rapport_mensuel_pdf(mois=mois)

    def calculer_score_bien_etre(self) -> Any:
        return self._service().calculer_score_bien_etre()

    def calculer_score_eco_responsable(self) -> Any:
        return self._service().calculer_score_eco_responsable()

    def generer_carte_visuelle_partageable(
        self, *, type_carte: str, titre: str | None = None
    ) -> Any:
        return self._service().generer_carte_visuelle_partageable(
            type_carte=type_carte,
            titre=titre,
        )

    def obtenir_mode_tablette_magazine(self) -> Any:
        return self._service().obtenir_mode_tablette_magazine()


@service_factory("rapports_innovations", tags={"rapports", "ia"})
def obtenir_service_innovations_rapports() -> ServiceInnovationsRapports:
    """Retourne la façade IA rapports consolidée."""
    return ServiceInnovationsRapports()

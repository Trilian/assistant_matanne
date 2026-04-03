"""
Service inter-modules : Meteo -> Activites famille.

Bridge inter-modules :
- P5-04: pluie -> activites interieur, beau temps -> exterieur
"""

from __future__ import annotations

import logging
from datetime import date as date_type, timedelta
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class MeteoActivitesInteractionService:
    """Bridge meteo -> activites famille."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def suggerer_activites_selon_meteo(self, *, jours_horizon: int = 3, db=None) -> dict[str, Any]:
        from src.services.utilitaires.meteo_service import obtenir_meteo_service

        service_meteo = obtenir_meteo_service()
        meteo = service_meteo.obtenir_meteo()
        suggestions: list[dict[str, str]] = []

        for prev in meteo.previsions[:jours_horizon]:
            date_iso = getattr(prev, "date", None)
            pluie = (getattr(prev, "precip_mm", 0) or 0) > 1 or (getattr(prev, "precip_proba", 0) or 0) >= 60
            if pluie:
                suggestions.append(
                    {
                        "date": str(date_iso),
                        "type": "interieur",
                        "idee": "Atelier cuisine, jeux de societe, bibliotheque ou piscine couverte.",
                    }
                )
            else:
                suggestions.append(
                    {
                        "date": str(date_iso),
                        "type": "exterieur",
                        "idee": "Parc, balade, velo, pique-nique ou sortie nature.",
                    }
                )

        return {
            "ville": meteo.ville,
            "suggestions": suggestions,
            "message": f"{len(suggestions)} suggestion(s) activites basees meteo.",
        }


@service_factory("meteo_activites_interaction", tags={"famille", "meteo", "activites"})
def obtenir_service_meteo_activites_interaction() -> MeteoActivitesInteractionService:
    """Factory pour le bridge meteo -> activites."""
    return MeteoActivitesInteractionService()

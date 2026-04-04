"""
Service inter-modules : Météo → Planning repas.

Phase 4.4 : prioriser les idées de repas selon les conditions météo
(ex. BBQ / plancha s'il fait beau, soupe si le temps est froid ou pluvieux).
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from src.core.decorators import avec_gestion_erreurs
from src.services.core.registry import service_factory
from src.services.cuisine.planning.meteo import MeteoJour

logger = logging.getLogger(__name__)


class MeteoPlanningInteractionService:
    """Bridge météo → suggestions repas du planning."""

    @staticmethod
    def _construire_meteo_jour(temperature: float, description: str) -> MeteoJour:
        """Crée un objet météo minimal à partir d'entrées simples."""
        return MeteoJour(
            date=date.today(),
            temperature=float(temperature),
            temperature_ressentie=float(temperature),
            description=description,
            icone="01d",
            humidite=50,
            vent_kmh=10.0,
        )

    @staticmethod
    def _etendre_types_recommandes(meteo: MeteoJour) -> list[str]:
        """Ajoute des synonymes culinaires plus proches de l'usage produit."""
        types = list(meteo.suggestion_type_repas)

        if meteo.ambiance in {"chaud", "doux"}:
            types.extend(["bbq", "barbecue", "plancha", "salade"])
        if meteo.ambiance in {"frais", "froid"}:
            types.extend(["soupe", "potage", "velouté", "plat mijoté"])
        if any(mot in meteo.description.lower() for mot in ("pluie", "averse", "bruine", "orage")):
            types.extend(["soupe", "gratin", "mijoté"])

        return list(dict.fromkeys(types))

    @avec_gestion_erreurs(default_return={"types_recommandes": [], "suggestions_priorisees": []})
    def prioriser_suggestions_selon_meteo(
        self,
        suggestions: list[str],
        *,
        temperature: float,
        description: str,
    ) -> dict[str, Any]:
        """Réordonne les suggestions repas selon la météo du jour."""
        meteo = self._construire_meteo_jour(temperature=temperature, description=description)
        types_recommandes = self._etendre_types_recommandes(meteo)
        mots_cles = tuple(type_repas.lower() for type_repas in types_recommandes)

        def _score(suggestion: str) -> tuple[int, str]:
            texte = suggestion.lower()
            score = 0

            if any(mot in texte for mot in mots_cles):
                score += 10

            if meteo.ambiance in {"chaud", "doux"} and any(
                mot in texte for mot in ("bbq", "barbecue", "grill", "plancha", "salade")
            ):
                score += 5

            if meteo.ambiance in {"frais", "froid"} and any(
                mot in texte for mot in ("soupe", "potage", "velout", "gratin", "mijot")
            ):
                score += 5

            if "pluie" in meteo.description.lower() and any(
                mot in texte for mot in ("soupe", "gratin", "mijot")
            ):
                score += 3

            return score, suggestion.lower()

        suggestions_priorisees = sorted(suggestions, key=_score, reverse=True)

        message = (
            "Beau temps : on privilégie BBQ, plancha et salades."
            if meteo.ambiance in {"chaud", "doux"}
            else "Temps frais/froid : on privilégie soupes, gratins et plats mijotés."
        )

        resultat = {
            "ambiance": meteo.ambiance,
            "temperature": meteo.temperature,
            "description": meteo.description,
            "types_recommandes": types_recommandes,
            "suggestions_priorisees": suggestions_priorisees,
            "message": message,
        }
        logger.debug(
            "Météo→Planning ambiance=%s temperature=%.1f suggestions=%d",
            meteo.ambiance,
            meteo.temperature,
            len(suggestions_priorisees),
        )
        return resultat

    @avec_gestion_erreurs(default_return={"types_recommandes": []})
    def suggerer_types_repas_du_jour(
        self,
        *,
        temperature: float,
        description: str,
    ) -> dict[str, Any]:
        """Retourne uniquement les types de repas adaptés à la météo."""
        resultat = self.prioriser_suggestions_selon_meteo(
            [],
            temperature=temperature,
            description=description,
        )
        return {
            "ambiance": resultat.get("ambiance"),
            "types_recommandes": resultat.get("types_recommandes", []),
            "message": resultat.get("message"),
        }


@service_factory(
    "meteo_planning_interaction",
    tags={"cuisine", "planning", "meteo", "phase4"},
)
def obtenir_service_meteo_planning_interaction() -> MeteoPlanningInteractionService:
    """Factory pour le bridge Météo → Planning repas."""
    return MeteoPlanningInteractionService()

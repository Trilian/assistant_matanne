"""
Service inter-modules : Produits de saison -> Planning IA.

Bridge inter-modules :
- P5-03: favoriser les produits de saison dans le planning IA
"""

from __future__ import annotations

import logging
from datetime import date as date_type
from typing import Any

from src.core.decorators import avec_gestion_erreurs
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class SaisonMenuInteractionService:
    """Bridge saison -> suggestions de planning."""

    def _saison_courante(self) -> str:
        mois = date_type.today().month
        if mois in (12, 1, 2):
            return "hiver"
        if mois in (3, 4, 5):
            return "printemps"
        if mois in (6, 7, 8):
            return "ete"
        return "automne"

    @avec_gestion_erreurs(default_return={})
    def obtenir_contexte_saisonnier_planning(self, limite: int = 20) -> dict[str, Any]:
        """Retourne le contexte saisonnier a injecter dans les prompts de planning IA."""
        from src.services.cuisine.suggestions.saisons_enrichi import (
            INGREDIENTS_SAISON_ENRICHI,
            obtenir_saison,
        )

        saison = obtenir_saison()
        mois_actuel = date_type.today().month
        produits = [
            ing.nom
            for ing in INGREDIENTS_SAISON_ENRICHI.get(saison, [])
            if mois_actuel in ing.pic_mois
        ][:limite]

        prompt_boost = (
            "Favoriser les ingredients suivants (saison locale): " + ", ".join(produits)
            if produits
            else "Aucun ingredient saisonnier disponible, utiliser des recettes de saison generiques."
        )

        return {
            "saison": saison,
            "produits_recommandes": produits,
            "prompt_boost": prompt_boost,
            "message": f"Contexte saisonnier prepare pour {saison}.",
        }


@service_factory("saison_menu_interaction", tags={"cuisine", "planning", "saisonnalite"})
def obtenir_service_saison_menu_interaction() -> SaisonMenuInteractionService:
    """Factory pour le bridge saison -> planning."""
    return SaisonMenuInteractionService()

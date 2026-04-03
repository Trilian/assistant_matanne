"""
Service inter-modules : Produits de saison -> Planning IA.

Bridge inter-modules :
- P5-03: favoriser les produits de saison dans le planning IA
"""

from __future__ import annotations

import json
import logging
from datetime import date as date_type
from pathlib import Path
from typing import Any

from src.core.decorators import avec_gestion_erreurs
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)
DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "reference" / "produits_de_saison.json"


class SaisonMenuInteractionService:
    """Bridge saison -> suggestions de planning."""

    def _charger_produits_saison(self) -> dict[str, list[str]]:
        if not DATA_FILE.exists():
            return {}
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return {}

        if isinstance(data, dict):
            if "saisons" in data and isinstance(data["saisons"], dict):
                return {k.lower(): v for k, v in data["saisons"].items() if isinstance(v, list)}
            return {k.lower(): v for k, v in data.items() if isinstance(v, list)}
        return {}

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
        saisons = self._charger_produits_saison()
        saison = self._saison_courante()
        produits = saisons.get(saison, [])[:limite]

        prompt_boost = (
            "Favoriser les ingredients suivants (saison locale): " + ", ".join(produits)
            if produits
            else "Aucun jeu de donnees saisonnier disponible, utiliser des recettes de saison generiques."
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

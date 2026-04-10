"""
Service IA — Diagnostic maison par photo (Pixtral).

Utilise la vision IA pour diagnostiquer des pannes ou problèmes
maison à partir de photos (B4.5 / IA3).
"""

import logging

from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class DiagnosticMaisonService(BaseAIService):
    """Service de diagnostic maison par analyse d'image IA."""

    def __init__(self):
        super().__init__(
            cache_prefix="diagnostic_maison",
            default_ttl=3600,
            service_name="diagnostic_maison",
        )

    def diagnostiquer_photo(self, image_base64: str, description: str = "") -> dict:
        """Analyse une photo pour diagnostiquer un problème maison.

        Args:
            image_base64: Image encodée en base64
            description: Description optionnelle du problème

        Returns:
            Dict avec diagnostic, gravite, actions_recommandees, cout_estime
        """
        prompt = f"""Analyse cette photo d'un problème maison.
{f"Description utilisateur: {description}" if description else ""}

Diagnostique le problème et réponds en JSON:
{{
  "diagnostic": "Description claire du problème identifié",
  "gravite": "faible|moyenne|haute|urgente",
  "actions_recommandees": [
    {{"action": "Description action", "priorite": "immediate|court_terme|long_terme", "diy": true}},
  ],
  "cout_estime": {{"min": 0, "max": 100, "unite": "EUR"}},
  "professionnel_requis": false,
  "type_professionnel": "plombier|électricien|maçon|peintre|autre|null",
  "urgence_intervention": false
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt=(
                    "Tu es un expert en diagnostic de pannes et problèmes maison. "
                    "Analyse les photos avec précision. Réponds en JSON valide."
                ),
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA diagnostic maison: {e}")

        return {
            "diagnostic": "Analyse non disponible",
            "gravite": "inconnue",
            "actions_recommandees": [],
            "cout_estime": None,
            "professionnel_requis": False,
            "erreur": "Service IA temporairement indisponible",
        }

    def diagnostiquer_texte(self, description: str) -> dict:
        """Diagnostic basé sur une description textuelle.

        Args:
            description: Description du problème

        Returns:
            Dict avec diagnostic, causes_probables, solutions
        """
        prompt = f"""Un utilisateur décrit un problème maison:
"{description}"

Diagnostique le problème et réponds en JSON:
{{
  "diagnostic": "Diagnostic probable",
  "causes_probables": ["cause 1", "cause 2"],
  "solutions": [
    {{"solution": "Description", "difficulte": "facile|moyen|difficile", "diy": true, "cout_estime": "0-50€"}}
  ],
  "professionnel_recommande": false,
  "type_professionnel": "plombier|électricien|autre|null"
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es un expert bricolage/maison. Réponds en JSON valide.",
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA diagnostic texte: {e}")

        return {
            "diagnostic": "Veuillez décrire le problème plus en détail",
            "causes_probables": [],
            "solutions": [],
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("diagnostic_maison", tags={"maison", "ia"})
def obtenir_service_diagnostic_maison() -> DiagnosticMaisonService:
    """Factory singleton."""
    return DiagnosticMaisonService()

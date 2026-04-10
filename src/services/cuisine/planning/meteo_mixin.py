"""
Mixin météo pour les services planning.

Fournit une interface de classe mixin pour intégrer la météo
dans les services de planning (PlanningService, WeekendAIService…).

Les fonctions sous-jacentes restent dans meteo.py ;
ce mixin les expose comme méthodes de classe.

Usage:
    class MonServicePlanning(BaseAIService, MeteoMixin):
        def generer_planning(self, semaine):
            meteo = self.obtenir_meteo_semaine(semaine)
            contexte = self.construire_contexte_meteo(meteo)
            ...
"""

import asyncio
import logging
from datetime import date, timedelta

from .meteo import MeteoJour, construire_contexte_meteo_prompt, obtenir_meteo_jour

logger = logging.getLogger(__name__)


class MeteoMixin:
    """Mixin ajoutant les capacités météo à un service planning."""

    async def obtenir_meteo(self, jour: date | None = None) -> MeteoJour | None:
        """Récupère la météo pour un jour donné."""
        return await obtenir_meteo_jour(jour)

    async def obtenir_meteo_semaine(self, date_debut: date | None = None) -> list[MeteoJour]:
        """Récupère la météo pour 7 jours à partir de date_debut.

        Returns:
            Liste de MeteoJour (peut être vide si l'API n'est pas configurée).
        """
        date_debut = date_debut or date.today()
        jours = [date_debut + timedelta(days=i) for i in range(7)]

        resultats: list[MeteoJour] = []
        for jour in jours:
            meteo = await obtenir_meteo_jour(jour)
            if meteo:
                resultats.append(meteo)

        return resultats

    def construire_contexte_meteo(self, meteo_jours: list[MeteoJour]) -> str:
        """Construit un contexte météo complet pour un prompt IA.

        Args:
            meteo_jours: Liste de MeteoJour pour la période.

        Returns:
            Fragment de prompt combinant toutes les journées.
        """
        if not meteo_jours:
            return ""

        fragments = [construire_contexte_meteo_prompt(m) for m in meteo_jours]
        return "\n".join(fragments)

    def enrichir_prompt_avec_meteo(self, prompt: str, meteo_jours: list[MeteoJour]) -> str:
        """Enrichit un prompt IA avec le contexte météo.

        Si aucune donnée météo, retourne le prompt inchangé.
        """
        contexte = self.construire_contexte_meteo(meteo_jours)
        if not contexte:
            return prompt

        return f"{prompt}\n\n--- Contexte météo ---\n{contexte}"

    def filtrer_suggestions_par_meteo(self, suggestions: list[str], meteo: MeteoJour) -> list[str]:
        """Filtre/réordonne des suggestions de repas selon la météo.

        Place les suggestions cohérentes avec l'ambiance météo en premier.
        """
        types_adaptes = set(meteo.suggestion_type_repas)

        adaptees = []
        autres = []
        for s in suggestions:
            s_lower = s.lower()
            if any(t in s_lower for t in types_adaptes):
                adaptees.append(s)
            else:
                autres.append(s)

        return adaptees + autres


__all__ = ["MeteoMixin"]

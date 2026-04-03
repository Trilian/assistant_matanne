"""
Mixin jardin pour le service météo.

Contient les méthodes de conseils de jardinage et de planification d'arrosage,
extraites de ServiceMeteo pour une meilleure séparation des responsabilités.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .service import ConseilJardin, MeteoJour, PlanArrosage

logger = logging.getLogger(__name__)

__all__ = ["MeteoJardinMixin"]


class MeteoJardinMixin:
    """
    Mixin fournissant les fonctionnalités jardin du service météo.

    Méthodes:
    - generer_conseils: Conseils de jardinage contextuels basés sur la météo
    - generer_plan_arrosage: Plan d'arrosage intelligent sur plusieurs jours

    NOTE: Ce mixin s'attend à être utilisé avec ServiceMeteo qui fournit
    self.get_previsions() et les modèles Pydantic associés.
    """

    # ═══════════════════════════════════════════════════════════
    # CONSEILS DE JARDINAGE
    # ═══════════════════════════════════════════════════════════

    def generer_conseils(self, previsions: list[MeteoJour] | None = None) -> list[ConseilJardin]:
        """
        Génère des conseils de jardinage basés sur la météo.

        Args:
            previsions: Prévisions météo

        Returns:
            Liste des conseils
        """
        from .service import ConseilJardin

        if previsions is None:
            previsions = self.get_previsions(3)

        if not previsions:
            return []

        conseils = []
        aujourd_hui = previsions[0] if previsions else None

        if not aujourd_hui:  # pragma: no cover - defensive code
            return []

        # Conseils basés sur la température
        if aujourd_hui.temperature_max >= 25:
            conseils.append(
                ConseilJardin(
                    priorite=1,
                    icone="💧",
                    titre="Arrosage recommandé",
                    description="Températures élevées, pensez à arroser le soir ou tôt le matin.",
                    action_recommandee="Arroser ce soir après 19h",
                )
            )

        if aujourd_hui.temperature_min < 10:
            conseils.append(
                ConseilJardin(
                    priorite=2,
                    icone="🌡️",
                    titre="Nuits fraîches",
                    description="Les nuits sont fraîches, attention aux plantes sensibles.",
                    plantes_concernees=["Tomates", "Basilic", "Courges"],
                    action_recommandee="Vérifier les protections",
                )
            )

        # Conseils basés sur la pluie
        if aujourd_hui.probabilite_pluie < 20 and aujourd_hui.precipitation_mm < 2:
            conseils.append(
                ConseilJardin(
                    priorite=2,
                    icone="🌱",
                    titre="Journée sèche",
                    description="Pas de pluie prévue, idéal pour les travaux au jardin.",
                    action_recommandee="Désherber, tailler, ou planter",
                )
            )
        elif aujourd_hui.probabilite_pluie > 60:
            conseils.append(
                ConseilJardin(
                    priorite=2,
                    icone="🌧️",
                    titre="Pluie prévue",
                    description="Inutile d'arroser, la pluie s'en chargera.",
                    action_recommandee="Reporter l'arrosage",
                )
            )

        # Conseils basés sur le vent
        if aujourd_hui.vent_km_h < 15:
            conseils.append(
                ConseilJardin(
                    priorite=3,
                    icone="🌱",
                    titre="Conditions idéales pour traiter",
                    description="Peu de vent, conditions parfaites pour les traitements foliaires.",
                    action_recommandee="Traiter si nécessaire (purin, savon noir...)",
                )
            )

        # Conseils UV
        if aujourd_hui.uv_index >= 8:
            conseils.append(
                ConseilJardin(
                    priorite=1,
                    icone="☀️",
                    titre="UV très forts",
                    description="Évitez de jardiner entre 12h et 16h. Pensez à vous protéger.",
                    action_recommandee="Jardiner le matin ou en fin de journée",
                )
            )

        # Conseil lune (simplifié - basé sur le jour du mois)
        jour_mois = date.today().day
        if 1 <= jour_mois <= 7 or 15 <= jour_mois <= 22:
            conseils.append(
                ConseilJardin(
                    priorite=3,
                    icone="🌙",
                    titre="Période favorable aux semis",
                    description="Lune montante, favorable aux semis et greffes.",
                    action_recommandee="Semer les graines",
                )
            )

        return sorted(conseils, key=lambda c: c.priorite)

    # ═══════════════════════════════════════════════════════════
    # PLAN D'ARROSAGE
    # ═══════════════════════════════════════════════════════════

    def generer_plan_arrosage(
        self,
        nb_jours: int = 7,
        surface_m2: float = 50.0,
    ) -> list[PlanArrosage]:
        """
        Génère un plan d'arrosage intelligent.

        Args:
            nb_jours: Nombre de jours à planifier
            surface_m2: Surface du jardin en m²

        Returns:
            Plan d'arrosage journalier
        """
        from .service import PlanArrosage

        previsions = self.get_previsions(nb_jours)

        if not previsions:
            return []

        plan = []
        pluie_cumul = 0.0  # Pluie cumulée sur les derniers jours

        for i, prev in enumerate(previsions):
            # Calculer le besoin en eau
            # Base: 3-5L/m² par semaine = ~0.5-0.7L/m²/jour
            besoin_base = surface_m2 * 0.6  # Litres/jour

            # Ajuster selon température
            if prev.temperature_max > 30:
                besoin_base *= 1.5
            elif prev.temperature_max > 25:
                besoin_base *= 1.2
            elif prev.temperature_max < 15:
                besoin_base *= 0.7

            # Soustraire la pluie prévue (1mm = 1L/m²)
            apport_pluie = prev.precipitation_mm * surface_m2 / 1000 * surface_m2

            # Tenir compte de la pluie récente
            pluie_cumul = pluie_cumul * 0.7 + prev.precipitation_mm  # Décroissance

            # Calculer le besoin net
            besoin_net = max(0, besoin_base - apport_pluie - (pluie_cumul * 0.3))

            # Décision d'arrosage
            besoin_arrosage = (
                besoin_net > besoin_base * 0.5
                and prev.probabilite_pluie < 60
                and prev.precipitation_mm < 5
            )

            # Raison
            if prev.precipitation_mm >= 5:
                raison = f"Pluie prévue ({prev.precipitation_mm}mm)"
            elif prev.probabilite_pluie >= 60:
                raison = f"Forte probabilité de pluie ({prev.probabilite_pluie}%)"
            elif pluie_cumul > 10:
                raison = "Sol encore humide des dernières pluies"
            elif besoin_arrosage:
                raison = f"Températures {prev.temperature_max}°C, évaporation importante"
            else:
                raison = "Conditions favorables, arrosage léger possible"

            # Plantes prioritaires si canicule
            plantes_prio = []
            if prev.temperature_max > 30:
                plantes_prio = ["Tomates", "Courgettes", "Salades", "Semis récents"]

            plan.append(
                PlanArrosage(
                    date=prev.date,
                    besoin_arrosage=besoin_arrosage,
                    quantite_recommandee_litres=round(besoin_net, 1) if besoin_arrosage else 0,
                    raison=raison,
                    plantes_prioritaires=plantes_prio,
                )
            )

        return plan

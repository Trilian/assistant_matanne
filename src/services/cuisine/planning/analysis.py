"""
Analyse et détection d'alertes pour le planning unifié.

Extrait du service principal pour réduire sa taille.
Contient:
- Calcul de charge familiale
- Détection d'alertes journalières/hebdomadaires
- Calcul de budget et statistiques
"""

import logging
from datetime import date

from .types import JourCompletSchema

logger = logging.getLogger(__name__)


class PlanningAnalysisMixin:
    """
    Mixin fournissant l'analyse et la détection d'alertes.

    Calcule la charge, les alertes et les stats.
    """

    def _calculer_charge(
        self,
        repas: list[dict],
        activites: list[dict],
        projets: list[dict],
        routines: list[dict],
    ) -> int:
        """Calcule score de charge (0-100) pour un jour"""
        score = 0

        # Repas complexes
        if repas:
            temps_total = sum(r.get("temps_total", 0) for r in repas)
            score += min(30, (temps_total // 30))  # Max 30 pts pour repas

        # Activités
        score += min(20, len(activites) * 10)  # Max 20 pts

        # Projets urgents
        score += min(25, len([p for p in projets if p.get("priorite") == "haute"]) * 15)

        # Routines nombreuses
        score += min(25, len(routines) * 5)

        return min(100, score)

    def _score_to_charge(self, score: int) -> str:
        """Convertit score numérique en label"""
        if score < 35:
            return "faible"
        elif score < 70:
            return "normal"
        else:
            return "intense"

    def _detecter_alertes(
        self,
        jour: date,
        repas: list[dict],
        activites: list[dict],
        projets: list[dict],
        charge_score: int,
    ) -> list[str]:
        """Détecte alertes intelligentes pour un jour"""
        alertes = []

        # Surcharge
        if charge_score >= 80:
            alertes.append("⚠️ Jour très chargé - Penser à prendre du temps")

        # Pas d'activité pour Jules
        if not any(a.get("pour_jules") for a in activites):
            alertes.append("👶 Pas d'activité prévue pour Jules")

        # Projets urgents sans tâches
        projets_urgents = [p for p in projets if p.get("priorite") == "haute"]
        if projets_urgents:
            alertes.append(f"🔴 {len(projets_urgents)} projet(s) urgent(s)")

        # Repas trop nombreux/complexes
        if len(repas) > 3:
            alertes.append(f"🍽️ {len(repas)} repas ce jour - Vérifier préparation")

        return alertes

    def _detecter_alertes_semaine(self, jours: dict[str, JourCompletSchema]) -> list[str]:
        """Détecte alertes pour la semaine globale"""
        alertes = []

        jours_list = list(jours.values())

        # Couverture activités Jules
        activites_jules = sum(
            sum(1 for a in j.activites if a.get("pour_jules")) for j in jours_list
        )
        if activites_jules == 0:
            alertes.append("👶 Aucune activité Jules cette semaine")
        elif activites_jules < 3:
            alertes.append("👶 Peu d'activités pour Jules (recommandé: 3+)")

        # Charge globale
        charges_intenses = sum(1 for j in jours_list if j.charge_score >= 80)
        if charges_intenses >= 3:
            alertes.append("⚠️ Plus de 3 jours très chargés - Risque burnout familial")

        # Budget
        budget_total = sum(j.budget_jour for j in jours_list)
        if budget_total > 500:  # Adapter à votre budget famille
            alertes.append(f"💰 Budget semaine: {budget_total:.2f}€ - Veiller au budget")

        return alertes

    def _calculer_budget_jour(self, activites: list[dict], projets: list[dict]) -> float:
        """Calcule budget estimé du jour"""
        return sum(a.get("budget") or 0 for a in activites)

    def _calculer_stats_semaine(self, jours: dict[str, JourCompletSchema]) -> dict:
        """Calcule stats globales semaine"""
        jours_list = list(jours.values())

        return {
            "total_repas": sum(len(j.repas) for j in jours_list),
            "total_activites": sum(len(j.activites) for j in jours_list),
            "activites_jules": sum(
                sum(1 for a in j.activites if a.get("pour_jules")) for j in jours_list
            ),
            "total_projets": sum(len(j.projets) for j in jours_list),
            "total_events": sum(len(j.events) for j in jours_list),
            "budget_total": sum(j.budget_jour for j in jours_list),
            "charge_moyenne": int(sum(j.charge_score for j in jours_list) / len(jours_list))
            if jours_list
            else 0,
        }


__all__ = ["PlanningAnalysisMixin"]

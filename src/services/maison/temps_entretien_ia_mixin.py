"""
Mixin IA pour le service Temps d'Entretien.

Contient toutes les méthodes d'analyse IA, suggestions et recommandations
matériel, extraites de TempsEntretienService pour séparation des responsabilités.

Usage:
    class TempsEntretienService(TempsEntretienIAMixin, BaseAIService):
        ...
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from .schemas import (
    AnalyseTempsIA,
    AnalyseTempsRequest,
    NiveauUrgence,
    PrioriteRemplacement,
    RecommandationMateriel,
    SuggestionOptimisation,
    TypeActiviteEntretien,
)

if TYPE_CHECKING:
    from .schemas import (
        ResumeTempsHebdo,
        StatistiqueTempsActivite,
    )

logger = logging.getLogger(__name__)


class TempsEntretienIAMixin:
    """Mixin fournissant les capacités d'analyse IA au service temps d'entretien.

    Accède via `self` aux attributs/méthodes de TempsEntretienService et BaseAIService:
    - self.obtenir_statistiques_activite()
    - self.obtenir_resume_semaine()
    - self.call_with_list_parsing()
    - self.client
    - self._historique
    """

    # ═══════════════════════════════════════════════════════
    # ANALYSE IA
    # ═══════════════════════════════════════════════════════

    async def analyser_temps_ia(
        self,
        request: AnalyseTempsRequest,
    ) -> AnalyseTempsIA:
        """Analyse le temps passé avec suggestions IA.

        Args:
            request: Paramètres d'analyse

        Returns:
            Analyse complète avec suggestions et recommandations
        """
        # Déterminer la période
        periodes_jours = {
            "semaine": 7,
            "mois": 30,
            "trimestre": 90,
            "annee": 365,
        }
        jours = periodes_jours.get(request.periode, 30)

        # Collecter les données
        stats_activites = self.obtenir_statistiques_activite(jours)
        resume_semaine = self.obtenir_resume_semaine()

        # Préparer les données pour l'IA
        temps_total = sum(s.temps_total_minutes for s in stats_activites)
        repartition = {s.type_activite.value: s.temps_total_minutes for s in stats_activites}

        # Préparer le contexte pour l'IA
        contexte = self._preparer_contexte_analyse(
            stats_activites,
            resume_semaine,
            request,
        )

        # Appeler l'IA pour les suggestions
        suggestions = []
        recommandations = []

        if request.inclure_suggestions:
            suggestions = await self._generer_suggestions_ia(contexte)

        if request.inclure_materiel:
            recommandations = await self._generer_recommandations_materiel_ia(
                contexte,
                budget_max=request.budget_materiel_max,
            )

        # Générer le résumé textuel
        resume = await self._generer_resume_ia(contexte)

        # Calculer le score d'efficacité
        score = self._calculer_score_efficacite(stats_activites, resume_semaine)

        return AnalyseTempsIA(
            periode_analysee=request.periode,
            resume_textuel=resume,
            temps_total_minutes=temps_total,
            repartition_par_categorie=repartition,
            suggestions_optimisation=suggestions,
            recommandations_materiel=recommandations,
            objectif_temps_suggere_min=self._suggerer_objectif(temps_total, jours),
            score_efficacite=score,
        )

    def _preparer_contexte_analyse(
        self,
        stats: list[StatistiqueTempsActivite],
        resume: ResumeTempsHebdo,
        request: AnalyseTempsRequest,
    ) -> str:
        """Prépare le contexte textuel pour l'IA."""
        lignes = [
            f"## Analyse temps entretien maison - Période: {request.periode}",
            "",
            "### Statistiques par activité:",
        ]

        for stat in stats[:10]:
            icone = stat.icone
            lignes.append(
                f"- {icone} {stat.type_activite.value}: "
                f"{stat.temps_total_minutes} min ({stat.nb_sessions} sessions), "
                f"tendance {stat.tendance}"
            )

        lignes.extend(
            [
                "",
                "### Résumé semaine actuelle:",
                f"- Temps total: {resume.temps_total_minutes} min",
                f"- Jardin: {resume.temps_jardin_minutes} min",
                f"- Ménage: {resume.temps_menage_minutes} min",
                f"- Bricolage: {resume.temps_bricolage_minutes} min",
                f"- Jour le plus actif: {resume.jour_plus_actif or 'N/A'}",
                f"- Évolution vs semaine précédente: {resume.comparaison_semaine_precedente:+.1f}%",
            ]
        )

        if request.objectif_temps_hebdo_min:
            lignes.append(f"- Objectif utilisateur: {request.objectif_temps_hebdo_min} min/semaine")

        return "\n".join(lignes)

    async def _generer_suggestions_ia(
        self,
        contexte: str,
    ) -> list[SuggestionOptimisation]:
        """Génère des suggestions d'optimisation via IA."""
        prompt = f"""
{contexte}

En tant qu'expert en organisation domestique, analyse ces données et propose
3-5 suggestions pour optimiser le temps d'entretien:

Types de suggestions possibles:
- regroupement: Combiner des tâches similaires
- planification: Meilleure répartition dans la semaine
- materiel: Équipement qui pourrait aider (traiter dans recommandations_materiel)
- delegation: Tâches à déléguer ou externaliser

Pour chaque suggestion, indique:
- titre: Titre court et accrocheur
- description: Explication détaillée
- type_suggestion: parmi [regroupement, planification, delegation]
- temps_economise_estime_min: Estimation du temps gagné par semaine
- activites_concernees: Liste des activités impactées
- priorite: haute, moyenne ou basse

Réponds uniquement en JSON avec une liste de suggestions.
"""

        try:
            result = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=SuggestionOptimisation,
                system_prompt="Tu es un expert en organisation et optimisation du temps domestique.",
            )
            return result
        except Exception as e:
            logger.warning(f"Erreur génération suggestions IA: {e}")
            return self._suggestions_par_defaut()

    async def _generer_recommandations_materiel_ia(
        self,
        contexte: str,
        budget_max: Decimal | None = None,
    ) -> list[RecommandationMateriel]:
        """Génère des recommandations de matériel via IA."""
        budget_str = f"Budget maximum: {budget_max}€" if budget_max else "Pas de limite de budget"

        prompt = f"""
{contexte}

{budget_str}

En tant qu'expert en équipement domestique et jardin, propose 2-4 équipements
qui permettraient de gagner du temps sur l'entretien:

Pour chaque recommandation:
- nom_materiel: Nom du produit/équipement
- description: Pourquoi cet équipement est utile
- categorie: jardin, menage, ou bricolage
- prix_estime_min: Prix minimum estimé en euros
- prix_estime_max: Prix maximum estimé en euros
- temps_economise_par_session_min: Minutes gagnées par utilisation
- retour_investissement_semaines: Nombre de semaines avant rentabilisation
- activites_ameliorees: Liste des activités optimisées
- priorite_achat: urgente, haute, normale, basse, future

Privilégie les équipements avec le meilleur rapport temps gagné / prix.
Réponds uniquement en JSON avec une liste de recommandations.
"""

        try:
            result = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=RecommandationMateriel,
                system_prompt="Tu es un expert en équipement domestique et jardinage.",
            )
            return result
        except Exception as e:
            logger.warning(f"Erreur génération recommandations matériel: {e}")
            return self._recommandations_par_defaut()

    async def _generer_resume_ia(self, contexte: str) -> str:
        """Génère un résumé textuel de l'analyse."""
        prompt = f"""
{contexte}

Rédige un résumé concis (3-4 phrases) de cette analyse du temps d'entretien.
Mentionne les points clés: temps total, activités principales, tendances.
Sois encourageant mais objectif.
"""

        try:
            result = await self.client.chat(
                prompt=prompt,
                system_prompt="Tu es un assistant familial bienveillant.",
            )
            return result.strip()
        except Exception as e:
            logger.warning(f"Erreur génération résumé: {e}")
            return "Analyse du temps d'entretien disponible. Consultez les statistiques pour plus de détails."

    def _calculer_score_efficacite(
        self,
        stats: list[StatistiqueTempsActivite],
        resume: ResumeTempsHebdo,
    ) -> int:
        """Calcule un score d'efficacité global (0-100)."""
        score = 50  # Base

        # Bonus régularité (sessions régulières)
        if resume.nb_sessions >= 5:
            score += 10
        elif resume.nb_sessions >= 3:
            score += 5

        # Bonus répartition équilibrée
        categories = [
            resume.temps_jardin_minutes,
            resume.temps_menage_minutes,
            resume.temps_bricolage_minutes,
        ]
        categories_actives = sum(1 for c in categories if c > 0)
        if categories_actives >= 2:
            score += 10

        # Bonus tendance positive
        tendances_hausse = sum(1 for s in stats if s.tendance == "hausse")
        tendances_baisse = sum(1 for s in stats if s.tendance == "baisse")
        if tendances_baisse > tendances_hausse:
            score += 15  # Temps qui diminue = plus efficace

        # Bonus satisfaction moyenne
        sessions_avec_note = [s for s in self._historique if s.satisfaction is not None]
        if sessions_avec_note:
            satisfaction_moyenne = sum(s.satisfaction for s in sessions_avec_note) / len(
                sessions_avec_note
            )
            score += int((satisfaction_moyenne - 3) * 5)

        return max(0, min(100, score))

    def _suggerer_objectif(self, temps_actuel: int, jours: int) -> int:
        """Suggère un objectif hebdomadaire basé sur l'historique."""
        temps_hebdo_actuel = (temps_actuel / jours) * 7
        # Suggérer une légère réduction (-10%)
        return int(temps_hebdo_actuel * 0.9)

    def _suggestions_par_defaut(self) -> list[SuggestionOptimisation]:
        """Suggestions par défaut si l'IA échoue."""
        return [
            SuggestionOptimisation(
                titre="Regrouper les tâches jardin",
                description="Faites tonte + désherbage + arrosage dans la même session",
                type_suggestion="regroupement",
                temps_economise_estime_min=30,
                activites_concernees=[
                    TypeActiviteEntretien.TONTE,
                    TypeActiviteEntretien.DESHERBAGE,
                    TypeActiviteEntretien.ARROSAGE,
                ],
                priorite=NiveauUrgence.MOYENNE,
            ),
            SuggestionOptimisation(
                titre="Planifier le ménage sur 2 jours",
                description="Répartissez aspirateur/sols sur 2 jours plutôt qu'un seul",
                type_suggestion="planification",
                temps_economise_estime_min=15,
                activites_concernees=[
                    TypeActiviteEntretien.ASPIRATEUR,
                    TypeActiviteEntretien.LAVAGE_SOL,
                ],
                priorite=NiveauUrgence.BASSE,
            ),
        ]

    def _recommandations_par_defaut(self) -> list[RecommandationMateriel]:
        """Recommandations par défaut si l'IA échoue."""
        return [
            RecommandationMateriel(
                nom_materiel="Robot tondeuse",
                description="Tond automatiquement pendant que vous faites autre chose",
                categorie="jardin",
                prix_estime_min=Decimal("300"),
                prix_estime_max=Decimal("1200"),
                temps_economise_par_session_min=45,
                retour_investissement_semaines=26,
                activites_ameliorees=[TypeActiviteEntretien.TONTE],
                priorite_achat=PrioriteRemplacement.NORMALE,
            ),
            RecommandationMateriel(
                nom_materiel="Aspirateur robot",
                description="Aspire automatiquement chaque jour",
                categorie="menage",
                prix_estime_min=Decimal("150"),
                prix_estime_max=Decimal("800"),
                temps_economise_par_session_min=30,
                retour_investissement_semaines=12,
                activites_ameliorees=[TypeActiviteEntretien.ASPIRATEUR],
                priorite_achat=PrioriteRemplacement.HAUTE,
            ),
        ]

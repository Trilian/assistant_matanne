"""
Service IA dédié à l'optimisation du planning des repas.

Spécialisé dans l'optimisation nutritionnelle, variété et simplification.
"""

from pydantic import BaseModel, Field
from typing import Optional

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


# ── Modèles Pydantic ──


class AnalyseVariete(BaseModel):
    """Analyse de la variété d'un planning"""

    score_variete: int = Field(..., ge=0, le=100, description="Score de variété (0-100)")
    proteins_bien_repartis: bool = Field(..., description="Protéines réparties sur la semaine")
    types_cuisines: list[str] = Field(..., description="Types de cuisines représentées")
    repetitions_problematiques: list[str] = Field(
        default_factory=list, description="Éléments trop répétés"
    )
    recommandations: list[str] = Field(..., description="Suggestions de variété")


class OptimisationNutrition(BaseModel):
    """Optimisation nutritionnelle du planning"""

    calories_jour: dict = Field(..., description="Calories par jour de la semaine")
    proteines_equilibree: bool = Field(..., description="Protéines bien réparties")
    fruits_legumes_quota: float = Field(
        ..., ge=0, le=1, description="% d'atteinte du quota fruits/légumes"
    )
    equilibre_fibre: bool = Field(..., description="Consommation fibre adéquate")
    aliments_a_privilegier: list[str] = Field(..., description="Aliments à ajouter")
    aliments_a_limiter: list[str] = Field(..., description="Aliments à réduire")


class SimplifcationSemaine(BaseModel):
    """Suggestions de simplification pour une semaine chargée"""

    nb_recettes_complexes: int = Field(..., description="Nombre de recettes complexes")
    suggestions_simplification: list[str] = Field(
        ..., description="Recettes à remplacer par des versions simples"
    )
    gain_temps_minutes: int = Field(..., ge=0, description="Temps gagné en minutes")
    recettes_simples_substitution: list[str] = Field(..., description="Alternatives simples")
    charge_globale: str = Field(..., description="Évaluation: léger/normal/chargé")


class PlanningAIService(BaseAIService):
    """
    Service IA pour l'optimisation du planning des repas.

    Spécialisations:
    - Optimisation nutritionnelle (calories, protéines, fruits/légumes)
    - Scoring de variété (types de cuisines, pas de répétition)
    - Suggestions de simplification en semaine chargée
    - Détection des déséquilibres
    - Adaptations intelligentes
    """

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="planning_ia",
            default_ttl=7200,  # 2h cache
            service_name="planning_ia",
        )

    def analyser_variete_semaine(
        self, planning_repas: list[dict]
    ) -> AnalyseVariete:
        """
        Analyse la variété du planning de la semaine.

        Args:
            planning_repas: Liste des repas [{"jour": "lundi", "petit_dej": "...", "midi": "...", "soir": "..."}, ...]

        Returns:
            AnalyseVariete avec score et recommandations
        """
        repas_desc = "\n".join(
            f"{r['jour']}: {r.get('petit_dej', '-')}, {r.get('midi', '-')}, {r.get('soir', '-')}"
            for r in planning_repas
        )

        prompt = f"""Analyse la variété de ce planning hebdomadaire:
{repas_desc}

Évalue:
1. Score variété (0=très monotone, 100=très varié)
2. Diversité des protéines (poisson/poulet/viande/oeuf/légumes)
3. Types de cuisines (française/asiatique/méditerranéenne/etc)
4. Éléments trop répétés (si max 2x semaine = ok)
5. Recommandations de variété

Format JSON."""

        result = self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt="Tu es nutritionniste expert. Évalue la variété de manière objective.",
        )

        return AnalyseVariete(
            score_variete=int(result.get("score_variete", 50)),
            proteins_bien_repartis=result.get("proteins_bien_repartis", False),
            types_cuisines=result.get("types_cuisines", []),
            repetitions_problematiques=result.get("repetitions_problematiques", []),
            recommandations=result.get("recommandations", []),
        )

    def optimiser_nutrition_semaine(
        self,
        planning_repas: list[dict],
        restrictions: Optional[list[str]] = None,
    ) -> OptimisationNutrition:
        """
        Optimise la nutrition du planning.

        Args:
            planning_repas: Repas planifiés
            restrictions: Restrictions diététiques (végétarien, sans gluten, etc)

        Returns:
            OptimisationNutrition avec équilibre et suggestions
        """
        repas_desc = "\n".join(
            f"{r['jour']}: {r.get('petit_dej', '-')}, {r.get('midi', '-')}, {r.get('soir', '-')}"
            for r in planning_repas
        )

        restrictions_str = f"Restrictions: {', '.join(restrictions)}" if restrictions else ""

        prompt = f"""Optimise la nutrition de ce planning:
{repas_desc}
{restrictions_str}

Analyse:
1. Calories/jour (cible 2000-2500 adulte)
2. Protéines réparties (idéalement 25-30g/repas principal)
3. % fruits/légumes/féculents (5 portions fruits/légumes/jour)
4. Fibre (25g+/jour pour adulte)
5. Aliments à privilégier
6. Aliments à limiter

Format JSON."""

        result = self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt="Tu es diététicienne experte. Fournis une analyse nutritionnelle précise.",
        )

        return OptimisationNutrition(
            calories_jour=result.get("calories_jour", {}),
            proteines_equilibree=result.get("proteines_equilibree", False),
            fruits_legumes_quota=float(result.get("fruits_legumes_quota", 0.5)),
            equilibre_fibre=result.get("equilibre_fibre", False),
            aliments_a_privilegier=result.get("aliments_a_privilegier", []),
            aliments_a_limiter=result.get("aliments_a_limiter", []),
        )

    def suggerer_simplification(
        self,
        planning_repas: list[dict],
        nb_heures_cuisine_max: int = 4,
    ) -> SimplifcationSemaine:
        """
        Suggère une simplification si la semaine est trop chargée.

        Args:
            planning_repas: Repas planifiés
            nb_heures_cuisine_max: Heures max disponibles pour la cuisine

        Returns:
            SimplifcationSemaine avec alternatives et gains de temps
        """
        repas_desc = "\n".join(
            f"{r['jour']}: {r.get('petit_dej', '-')}, {r.get('midi', '-')}, {r.get('soir', '-')}"
            for r in planning_repas
        )

        prompt = f"""Évalue la charge de cuisine pour ce planning:
{repas_desc}

Contexte: max {nb_heures_cuisine_max}h disponibles cette semaine

Identifie:
1. Recettes complexes (durée/technique)
2. Combien peuvent être remplacées par des versions simples
3. Temps total actuel vs après simplification
4. Alternatives rapides (≤20 min) pour remplacer
5. Charge globale (léger/normal/chargé)

Format JSON."""


        result = self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt="Tu es expert culinaire pragmatique. Propose des simplifications réalistes.",
        )

        return SimplificationSemaine(
            nb_recettes_complexes=int(result.get("nb_recettes_complexes", 0)),
            suggestions_simplification=result.get("suggestions_simplification", []),
            gain_temps_minutes=int(result.get("gain_temps_minutes", 0)),
            recettes_simples_substitution=result.get("recettes_simples_substitution", []),
            charge_globale=result.get("charge_globale", "normal"),
        )

    def suggerer_recettes_adaptees(
        self,
        contexte: str,
        nb_recettes: int = 3,
    ) -> list[str]:
        """
        Suggère des recettes adaptées au contexte.

        Args:
            contexte: Description du contexte (ex: "semaine chargée, peu d'ingrédients")
            nb_recettes: Nombre de suggestions

        Returns:
            Liste de recettes suggérées
        """
        prompt = f"""Suggère {nb_recettes} recettes adaptées au contexte:
{contexte}

Critères:
- Rapides (≤30 min)
- Variées
- Adaptables
- Ingrédients simples

Liste format: "1. Recette A\n2. Recette B..."."""

        result = self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es chef culinaire pragmatique. Suggère des recettes réalistes et savoureuses.",
            max_tokens=300,
        )

        return [line.strip("0123456789. ") for line in result.split("\n") if line.strip()]

    def stream_analyse_variete(self, planning_repas: list[dict]):
        """Stream d'analyse de variété."""
        repas_desc = "\n".join(
            f"{r['jour']}: {r.get('petit_dej', '-')}, {r.get('midi', '-')}, {r.get('soir', '-')}"
            for r in planning_repas
        )

        prompt = f"""Analyse la variété:
{repas_desc}

Score variété, diversité protéines, types de cuisines, éléments répétés, recommandations."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es nutritionniste expert.",
            max_tokens=500,
        )


@service_factory("planning_ia", tags={"planning", "ia", "cuisine"})
def get_planning_ai_service() -> PlanningAIService:
    """Factory pour le service IA planning."""
    return PlanningAIService()

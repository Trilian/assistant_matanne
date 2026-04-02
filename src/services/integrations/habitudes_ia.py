"""
Service IA pour l'analyse intelligente des habitudes familiales.

Analyse patterns de routines, détecte anomalies, suggère personnalisations.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


# ── Modèles Pydantic ──


class AnalyseHabitude(BaseModel):
    """Analyse d'une habitude/routine"""

    habitude: str = Field(..., description="Nom de l'habitude (ex: petit-déj, dodo, sport)")
    frequence_hebdo: int = Field(..., ge=0, le=7, description="Fois par semaine")
    consistency: float = Field(..., ge=0, le=1, description="Consistance (0=chaotique, 1=régulière)")
    jours_preferres: list[str] = Field(..., description="Jours où c'est régulier")
    heures_preferees: list[str] = Field(..., description="Horaires généraux (matin/midi/soir)")
    status: Literal["etablie", "fragile", "negligee"] = Field(..., description="Statut de la routine")
    impact_positif: list[str] = Field(..., description="Impacts positifs détectés")
    facteurs_decouplage: list[str] = Field(..., description="Ce qui la déstabilise")


class TendanceFamiliale(BaseModel):
    """Tendance globale de la famille"""

    periode: str = Field(..., description="Période analysée (dernière semaine, mois, etc)")
    engagement_activites: float = Field(
        ..., ge=0, le=100, description="% d'engagement dans activités"
    )
    variete_activites: int = Field(..., ge=0, le=100, description="Score variété")
    coherence_routines: int = Field(
        ..., ge=0, le=100, description="Score cohérence des routines"
    )
    equilibre_work_life: str = Field(..., description="Évaluation (excellent/bon/moyen/difficile)")
    moments_stress_detectes: list[str] = Field(..., description="Moments critiques")
    points_forts: list[str] = Field(..., description="Aspects positifs à maintenir")
    axes_amelioration: list[str] = Field(..., description="Domaines à travailler")


class HabitudesAIService(BaseAIService):
    """
    Service IA pour analyse des habitudes familiales.

    Fonctionnalités:
    - Analyse des routines (petit-déj, sommeil, sport, etc)
    - Détection de patterns (régularité, anomalies)
    - Scoring de consistance
    - Suggestions de personnalisation
    - Tendances globales de la famille
    - Alertes sur dégradation de routines
    """

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="habitudes",
            default_ttl=7200,
            service_name="habitudes_ia",
        )

    async def analyser_habitude(
        self,
        habitude_nom: str,
        historique_7j: list[dict],  # [{"date": "2026-04-05", "realise": true, "heure": "07:30"}, ...]
        description_contexte: str = "",
    ) -> AnalyseHabitude:
        """
        Analyse une habitude/routine.

        Args:
            habitude_nom: Nom de l'habitude (petit-déj, dodo, sport, etc)
            historique_7j: [{"date": "2026-04-05", "realise": true, "heure": "07:30"}, ...]
            description_contexte: Contexte additionnel

        Returns:
            AnalyseHabitude avec scoring et facteurs
        """
        nb_realisations = sum(1 for h in historique_7j if h.get("realise", False))
        heures = [h["heure"] for h in historique_7j if h.get("heure")]

        prompt = f"""Analyse la routine: {habitude_nom}
Contexte: {description_contexte}

Historique 7 jours:
- Réalisations: {nb_realisations}/7
- Horaires: {', '.join(heures) if heures else 'variables'}
- Jours: {[h['date'] for h in historique_7j]}

Évalue:
1. Fréquence hebdo (0-7)
2. Consistency (0-100%)
3. Jours préférés
4. Horaires généraux
5. Statut (établie/fragile/négligée)
6. Impacts positifs détectés
7. Facteurs la déstabilisent

Format JSON."""

        result = await self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt="Tu es coach en habitudes. Analyse de manière bienveillante et constructive.",
        )

        return AnalyseHabitude(
            habitude=habitude_nom,
            frequence_hebdo=int(result.get("frequence_hebdo", nb_realisations)),
            consistency=float(result.get("consistency", nb_realisations / 7)),
            jours_preferres=result.get("jours_preferres", []),
            heures_preferees=result.get("heures_preferees", []),
            status=result.get("status", "etablie" if nb_realisations >= 4 else "fragile"),
            impact_positif=result.get("impact_positif", []),
            facteurs_decouplage=result.get("facteurs_decouplage", []),
        )

    async def analyser_tendances_famille(
        self,
        habitudes_analysees: list[dict],  # [{"nom": "petit-déj", "realisations": 5, "status": "établie"}, ...]
        periode_jours: int = 7,
        notes_contexte: str = "",
    ) -> TendanceFamiliale:
        """
        Analyse les tendances globales de la famille.

        Args:
            habitudes_analysees: Habitudes avec scoring
            periode_jours: Période d'analyse (7, 30, etc)
            notes_contexte: Événements spéciaux (vacances, déménagement, etc)

        Returns:
            Tendances avec insights
        """
        habitudes_str = "\n".join(
            f"- {h['nom']}: {h['realisations']}/10, {h['status']}"
            for h in habitudes_analysees
        )

        prompt = f"""Analyse les tendances familiales (période: {periode_jours}j):
{habitudes_str}

Contexte: {notes_contexte if notes_contexte else 'Normal'}

Évalue:
1. Engagement activités (%)
2. Variété activités (score)
3. Cohérence routines (score)
4. Équilibre travail/vie (excellent/bon/moyen/difficile)
5. Moments stress
6. Points forts à maintenir
7. Axes d'amélioration

Format JSON."""

        result = await self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt="Tu es expert family wellness. Fournis insights bienveillants et constructifs.",
        )

        return TendanceFamiliale(
            periode=f"{periode_jours} derniers jours",
            engagement_activites=float(result.get("engagement_activites", 60)),
            variete_activites=int(result.get("variete_activites", 60)),
            coherence_routines=int(result.get("coherence_routines", 60)),
            equilibre_work_life=result.get("equilibre_work_life", "moyen"),
            moments_stress_detectes=result.get("moments_stress_detectes", []),
            points_forts=result.get("points_forts", []),
            axes_amelioration=result.get("axes_amelioration", []),
        )

    async def suggerer_routine_personnalisee(
        self,
        habitude_nom: str,
        profil: str,  # "enfant", "adulte_travail", "adulte_home", "mixte"
        contraintes: list[str] = None,
        objectif: str = "",
    ) -> str:
        """
        Suggère une routine adaptée au profil.

        Args:
            habitude_nom: Habitude à mettre en place
            profil: Type de profil/contexte
            contraintes: [ex: "peu de temps", "petit budget", "impatience enfant"]
            objectif: Objectif spécifique

        Returns:
            Routine détaillée avec guide de mise en place
        """
        contraintes_str = f", Contraintes: {', '.join(contraintes)}" if contraintes else ""

        prompt = f"""Conçois une routine personnalisée:
Habitude: {habitude_nom}
Profil: {profil}
Objectif: {objectif}{contraintes_str}

Propose:
1. Structure détaillée (étapes, timing)
2. Triggers pour rester consistant
3. Adaptations selon jours
4. Freins probables et solutions
5. Métriques de suivi

Ton bienveillant, pratique. Sois réaliste."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es coach expérimenté en habitudes. Crée des routines réalistes et motivantes.",
            max_tokens=800,
        )

    async def detecter_anomalies_routine(
        self,
        habitude_nom: str,
        historique_30j: list[dict],
        baseline_normal: int = 20,  # Jours sur 30
    ) -> dict:
        """
        Détecte anomalies/dégradation de routine.

        Args:
            habitude_nom: Habitude à analyser
            historique_30j: Historique 30 jours
            baseline_normal: Nombre de jours "normaux" attendus

        Returns:
            Anomalies détectées et alertes
        """
        nb_realisations = sum(1 for h in historique_30j if h.get("realise", False))
        dégradation = baseline_normal - nb_realisations

        prompt = f"""Analyse anomalies routine: {habitude_nom}
Historique 30j:
- Réalisations: {nb_realisations}/30
- Baseline attendu: {baseline_normal}/30
- Dégradation: {dégradation} jours

Cause probables:
1. Changement de circonstances?
2. Fatigue/stress?
3. Manque de motivation?
4. Obstacles pratiques?

Fournis: analyse problème, alertes, recommandations.
Format JSON."""

        result = await self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt="Tu es analyste d'habitudes. Sois factuel et supportant.",
        )

        return result

    def stream_tendances_famille(
        self,
        habitudes_analysees: list[dict],
        periode_jours: int = 7,
    ):
        """Stream d'analyse des tendances."""
        habitudes_str = "\n".join(
            f"- {h['nom']}: {h['realisations']}/{h['max']}"
            for h in habitudes_analysees
        )

        prompt = f"""Analyser tendances familiales (période: {periode_jours}j):
{habitudes_str}

Engagement, variété, cohérence, équilibre, stress, points forts, améliorations."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert family wellness.",
            max_tokens=600,
        )


@service_factory("habitudes_ia", tags={"famille", "ia", "core", "wellness"})
def get_habitudes_ai_service() -> HabitudesAIService:
    """Factory pour le service habitudes."""
    return HabitudesAIService()

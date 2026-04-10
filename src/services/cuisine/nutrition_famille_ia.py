"""
Service IA pour nutritionExtension Jules → toute la famille.

Basé sur données Garmin + recettes planifiées + profils individuels.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

# ── Modèles Pydantic ──


class DonneesNutritionnelles(BaseModel):
    """Données nutritionnelles pour une personne"""

    personne: str = Field(..., description="Nom personne")
    periode: str = Field(..., description="Période analysée (jour/semaine/mois)")
    calories_moyenne: float = Field(..., ge=0, description="Calories/jour moyenne")
    proteines_g: float = Field(..., ge=0, description="Protéines/jour en g")
    glucides_g: float = Field(..., ge=0, description="Glucides/jour en g")
    lipides_g: float = Field(..., ge=0, description="Lipides/jour en g")
    fibres_g: float = Field(..., ge=0, description="Fibres/jour en g")
    fruits_legumes_portions: float = Field(..., ge=0, description="Portions fruits/légumes/jour")
    eau_litres: float = Field(..., ge=0, description="Litres d'eau/jour")
    equilibre_score: int = Field(..., ge=0, le=100, description="Score équilibre nutritionnel")


class BilanNutritionFamille(BaseModel):
    """Bilan nutritionnel familial"""

    periode: str = Field(..., description="Période du bilan")
    membres_analyses: list[str] = Field(..., description="Membres de la famille analysés")
    moyennes_familles: DonneesNutritionnelles = Field(..., description="Moyennes familiales")
    disparites: list[str] = Field(..., description="Disparités détectées")
    anomalies: list[str] = Field(..., description="Anomalies santé possibles")
    points_forts: list[str] = Field(..., description="Points forts du groupe")
    recommendations_globales: list[str] = Field(..., description="Recommendations pour la famille")
    recommendations_individualisees: dict = Field(..., description="Recommendations par personne")


class NutritionFamilleAIService(BaseAIService):
    """
    Service IA pour nutrition familiale.

    Extension de la nutrition Jules (enfant) à toute la famille.

    Intégrations:
    - Données Garmin (adultes): calories brûlées, activité
    - Recettes planifiées: apports nutritionnels
    - Profils individuels: âge, sexe, objectifs
    - Données de suivi (poids, bien-être)

    Fonctionnalités:
    - Bilan nutritionnel par personne
    - Bilan nutritionnel familial
    - Détection déséquilibres
    - Recommendations adaptées par âge/objectif
    - Harmonie meal-prep pour toute la famille
    """

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="nutrition_famille",
            default_ttl=7200,
            service_name="nutrition_famille_ia",
        )

    async def analyser_nutrition_personne(
        self,
        personne_nom: str,
        age_ans: int,
        sexe: Literal["M", "F"],
        activite_niveau: Literal["sedentaire", "leger", "modere", "actif", "tres_actif"],
        donnees_garmin_semaine: dict | None = None,
        recettes_semaine: list[str] = None,
        objectif_sante: str = "maintien",
    ) -> DonneesNutritionnelles:
        """
        Analyse nutrition pour une personne.

        Args:
            personne_nom: Nom de la personne
            age_ans: Âge en années
            sexe: M ou F
            activite_niveau: Niveau d'activité
            donnees_garmin_semaine: Données Garmin {"calories_brulees": X, "pas": Y, ...}
            recettes_semaine: Recettes mangées dans la semaine
            objectif_sante: "maintien", "perte_poids", "prise_muscle", "athletic"

        Returns:
            DonneesNutritionnelles avec bilan
        """
        garmin_str = (
            f"Garmin: {donnees_garmin_semaine}"
            if donnees_garmin_semaine
            else "Aucune donnée Garmin"
        )
        recettes_str = f"Recettes: {', '.join(recettes_semaine[:5])}" if recettes_semaine else ""

        prompt = f"""Analyse nutrition pour {personne_nom}:
Profil: {age_ans}ans, {sexe}
Activité: {activite_niveau}
Objectif: {objectif_sante}
{garmin_str}
{recettes_str}

Estime:
1. Besoins caloriques/jour
2. Apports pour la semaine (calories, protéines, glucides, lipides, fibres)
3. % fruits/légumes/jour
4. Hydratation
5. Score équilibre (0-100)
6. Anomalies détectées
7. Recommendations personnalisées

Format JSON."""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es diététicienne experte. Analyse precise basée sur profil et données.",
        )

        return DonneesNutritionnelles(
            personne=personne_nom,
            periode="semaine dernière",
            calories_moyenne=float(result.get("calories_moyenne", 2000)),
            proteines_g=float(result.get("proteines_g", 50)),
            glucides_g=float(result.get("glucides_g", 200)),
            lipides_g=float(result.get("lipides_g", 60)),
            fibres_g=float(result.get("fibres_g", 25)),
            fruits_legumes_portions=float(result.get("fruits_legumes_portions", 4.5)),
            eau_litres=float(result.get("eau_litres", 1.8)),
            equilibre_score=int(result.get("equilibre_score", 70)),
        )

    async def bilan_nutrition_famille(
        self,
        membres_donnees: list[
            dict
        ],  # [{"nom": "Pierre", "age": 12, "activite": "modere", ...}, ...]
        recettes_planifiees: list[str],
        periode_jours: int = 7,
    ) -> BilanNutritionFamille:
        """
        Fait un bilan nutritionnel familial.

        Args:
            membres_donnees: Profils des membres
            recettes_planifiees: Recettes prévues pour la période
            periode_jours: Période du bilan

        Returns:
            BilanNutritionFamille complet
        """
        membres_str = "\n".join(
            f"- {m['nom']}: {m['age']}ans, {m['activite']}, {m.get('objectif', 'maintien')}"
            for m in membres_donnees
        )
        recettes_str = ", ".join(recettes_planifiees[:10])

        prompt = f"""Bilan nutrition familiale ({periode_jours}j):
Membres:
{membres_str}

Recettes prévues: {recettes_str}

Analyse:
1. Profils nutritionnels individuels (estimés)
2. Moyennes familiales
3. Disparités entre membres (ex: enfant vs adultes)
4. Anomalies possibles (carences, excès)
5. Points forts du groupe
6. Recommendations globales (repas partagés mais adaptations)
7. Recommendations individualisées par membre

Format JSON avec structure claire."""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es nutritionniste familial. Comprends les complexités multi-âges.",
        )

        # Parser les données individuelles
        moyennes = DonneesNutritionnelles(
            personne="FAMILLE",
            periode=f"{periode_jours} jours",
            calories_moyenne=float(result.get("calories_moyenne_famille", 2000)),
            proteines_g=float(result.get("proteines_moyenne", 50)),
            glucides_g=float(result.get("glucides_moyenne", 200)),
            lipides_g=float(result.get("lipides_moyenne", 60)),
            fibres_g=float(result.get("fibres_moyenne", 25)),
            fruits_legumes_portions=float(result.get("fruits_legumes_portions_famille", 4.5)),
            eau_litres=float(result.get("eau_litres_famille", 1.8)),
            equilibre_score=int(result.get("equilibre_score_famille", 70)),
        )

        return BilanNutritionFamille(
            periode=f"{periode_jours} derniers jours",
            membres_analyses=[m["nom"] for m in membres_donnees],
            moyennes_familles=moyennes,
            disparites=result.get("disparites", []),
            anomalies=result.get("anomalies", []),
            points_forts=result.get("points_forts", []),
            recommendations_globales=result.get("recommendations_globales", []),
            recommendations_individualisees=result.get("recommendations_individualisees", {}),
        )

    async def adapter_recette_pour_famille(
        self,
        recette_nom: str,
        recette_apports: dict,  # {"calories": 600, "proteines_g": 25, ...}
        membres_famille: list[dict],  # [{"nom": "Jules", "age_mois": 24}, ...]
    ) -> dict:
        """
        Adapte une recette pour tous les membres de la famille.

        Args:
            recette_nom: Nom de la recette
            recette_apports: Apports nutritionnels
            membres_famille: Membres avec âges (Jules en mois, autres en ans)

        Returns:
            Adaptations par personne (portions, simplifications, etc)
        """
        membres_str = "\n".join(
            f"- {m['nom']}: {m.get('age_mois', m.get('age_ans', 30) * 12)} mois equiv"
            for m in membres_famille
        )

        prompt = f"""Adapte cette recette pour toute la famille:
Recette: {recette_nom}
Apports: {recette_apports}

Membres:
{membres_str}

Pour chaque membre, propose:
1. Portion adaptée
2. Simplifications (moins épicé, morceaux adaptés, etc)
3. Substitutions si allergie/restriction connue
4. Temps de préparation/cuisson adapté
5. Format consommable (purée, morceaux, intact, etc)

Format JSON par personne."""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es expert nutrition familiale multi-âges. Crée adaptations réalistes.",
        )

        return result

    async def recommandations_equilibrage(
        self,
        semaine_planifiee: list[str],  # Recettes pour 7j
        profils_famille: list[dict],
    ) -> str:
        """
        Recommande des ajustements pour équilibrer nutrition.

        Args:
            semaine_planifiee: Recettes prévues pour la semaine
            profils_famille: Profils membres

        Returns:
            Recommendations d'équilibrage
        """
        recettes_str = "\n".join(f"- {r}" for r in semaine_planifiee)
        profils_str = "\n".join(
            f"- {p['nom']}: {p['age']}ans, {p.get('objectif', 'maintien')}" for p in profils_famille
        )

        prompt = f"""Recommande équilibrage nutritionnel:
Semaine planifiée:
{recettes_str}

Famille:
{profils_str}

Suggestions:
1. Points forts de cette semaine
2. Carences possibles
3. Ajustements recommandés (ajouter fruits, réduire graisses, etc)
4. Distribution macro-nutrients optimale par jour
5. Boissons et collations recommandées
6. Adaptations Jules si nécessaire

Sois concis et actionnable."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es nutritionniste familial pragmatique.",
            max_tokens=600,
        )

    def stream_bilan_nutrition_familia(
        self,
        membres_donnees: list[dict],
        periode_jours: int = 7,
    ):
        """Stream du bilan familial."""
        membres_str = "\n".join(f"- {m['nom']}: {m['age']}ans" for m in membres_donnees)

        prompt = f"""Bilan nutrition familiale ({periode_jours}j):
{membres_str}

Profils individuels, moyennes, disparités, anomalies, points forts, recommendations."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es nutritionniste familial.",
            max_tokens=700,
        )


@service_factory("nutrition_famille_ia", tags={"cuisine", "famille", "ia", "nutrition"})
def get_nutrition_famille_ai_service() -> NutritionFamilleAIService:
    """Factory pour le service nutrition famille."""
    return NutritionFamilleAIService()

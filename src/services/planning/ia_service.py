"""
Service IA dédié à l'optimisation du planning des repas.

Spécialisé dans l'optimisation nutritionnelle, variété et simplification.
"""

from typing import Optional

from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.base.async_utils import sync_wrapper
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


class SimplificationSemaine(BaseModel):
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

    async def analyser_variete_semaine(self, planning_repas: list[dict]) -> AnalyseVariete:
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

Réponds en JSON avec ces clés exactes:
{{
  "score_variete": <int 0-100>,
  "proteins_bien_repartis": <bool>,
  "types_cuisines": ["française", "asiatique"],  // liste plate de strings
  "repetitions_problematiques": ["..."],
  "recommandations": ["..."]
}}"""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es nutritionniste expert. Évalue la variété de manière objective.",
        )

        types_cuisines_raw = result.get("types_cuisines") or []
        if isinstance(types_cuisines_raw, dict):
            types_cuisines_raw = list(types_cuisines_raw.keys())

        return AnalyseVariete(
            score_variete=int(result.get("score_variete") or 50),
            proteins_bien_repartis=result.get("proteins_bien_repartis") or False,
            types_cuisines=types_cuisines_raw,
            repetitions_problematiques=result.get("repetitions_problematiques") or [],
            recommandations=result.get("recommandations") or [],
        )

    def analyser_variete_semaine_sync(self, planning_repas: list[dict]) -> AnalyseVariete:
        """Version synchrone pour rétrocompatibilité."""
        _sync = sync_wrapper(self.analyser_variete_semaine)
        return _sync(planning_repas)

    async def optimiser_nutrition_semaine(
        self,
        planning_repas: list[dict],
        restrictions: list[str] | None = None,
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

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es diététicienne experte. Fournis une analyse nutritionnelle précise.",
        )

        return OptimisationNutrition(
            calories_jour=result.get("calories_jour") or {},
            proteines_equilibree=result.get("proteines_equilibree") or False,
            fruits_legumes_quota=float(result.get("fruits_legumes_quota") or 0.5),
            equilibre_fibre=result.get("equilibre_fibre") or False,
            aliments_a_privilegier=result.get("aliments_a_privilegier") or [],
            aliments_a_limiter=result.get("aliments_a_limiter") or [],
        )

    async def suggerer_simplification(
        self,
        planning_repas: list[dict],
        nb_heures_cuisine_max: int = 4,
    ) -> SimplificationSemaine:
        """
        Suggère une simplification si la semaine est trop chargée.

        Args:
            planning_repas: Repas planifiés
            nb_heures_cuisine_max: Heures max disponibles pour la cuisine

        Returns:
            SimplificationSemaine avec alternatives et gains de temps
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

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es expert culinaire pragmatique. Propose des simplifications réalistes.",
        )

        return SimplificationSemaine(
            nb_recettes_complexes=int(result.get("nb_recettes_complexes") or 0),
            suggestions_simplification=result.get("suggestions_simplification") or [],
            gain_temps_minutes=int(result.get("gain_temps_minutes") or 0),
            recettes_simples_substitution=result.get("recettes_simples_substitution") or [],
            charge_globale=result.get("charge_globale") or "normal",
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

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es chef culinaire pragmatique. Suggère des recettes réalistes et savoureuses.",
            max_tokens=300,
        )

        return [line.strip("0123456789. ") for line in result.split("\n") if line.strip()]

    async def suggerer_accompagnements(
        self,
        recette_nom: str,
        categorie: str | None,
        saison: str = "printemps",
    ) -> dict:
        """
        Suggère les accompagnements manquants pour équilibrer un repas.

        Logique bidirectionnelle :
        - Plat protéiné    → 2 légumes + 1 féculent
        - Plat féculent    → 1 protéine + 1-2 légumes
        - Plat légume      → 1 protéine + 1 féculent
        - Mixte / inconnu  → 1 légume + suggestions selon contexte

        Args:
            recette_nom: Nom du plat principal
            categorie:   categorie_nutritionnelle (ex: "proteines_poisson", "feculents")
            saison:      Saison courante pour suggestions saisonnières

        Returns:
            dict avec clés legumes, feculents, proteines (chacune list[str])
        """
        from src.services.planning.nutrition import (
            CATEGORIES_FECULENTS,
            CATEGORIES_LEGUMES,
            CATEGORIES_PROTEINES,
        )

        if categorie in CATEGORIES_PROTEINES:
            consigne = (
                f"Le plat principal est une source de protéines : {recette_nom}. "
                "Propose 2 légumes et 1 féculent adaptés à ce plat, de saison "
                f"({saison}), simples à cuisiner, variés et savoureux."
            )
            champs_attendus = "legumes (liste 2), feculents (liste 1)"
        elif categorie in CATEGORIES_FECULENTS:
            consigne = (
                f"Le plat principal est essentiellement un féculent : {recette_nom}. "
                "Propose 1 source de protéines et 1 légume pour compléter l'assiette, "
                f"de saison ({saison}), adaptés au plat."
            )
            champs_attendus = "proteines (liste 1-2 options), legumes (liste 1)"
        elif categorie in CATEGORIES_LEGUMES:
            consigne = (
                f"Le plat principal est essentiellement un légume : {recette_nom}. "
                "Propose 1 source de protéines et 1 féculent pour compléter l'assiette, "
                f"de saison ({saison}), adaptés au plat."
            )
            champs_attendus = "proteines (liste 1-2 options), feculents (liste 1)"
        else:
            consigne = (
                f"Pour le plat {recette_nom}, propose des accompagnements équilibrés "
                f"(légumes et/ou féculents), de saison ({saison})."
            )
            champs_attendus = "legumes (liste 1-2), feculents (liste 0-1)"

        prompt = f"""{consigne}

Réponds UNIQUEMENT en JSON valide avec ces clés :
{{
  "legumes": ["exemple 1", "exemple 2"],
  "feculents": ["exemple 1"],
  "proteines": ["exemple 1", "exemple 2"]
}}

Règles :
- {champs_attendus}
- Noms courts et concrets (ex: "Haricots verts vapeur", "Riz basmati", "Filet de saumon")
- Pas de sauces ni préparations complexes pour les accompagnements
- Si une liste n'est pas pertinente, retourne []"""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt=(
                "Tu es nutritionniste et chef cuisinier. "
                "Tu proposes des accompagnements équilibrés selon les recommandations PNNS4. "
                "Réponds TOUJOURS en JSON valide."
            ),
        )

        return {
            "legumes": result.get("legumes", []),
            "feculents": result.get("feculents", []),
            "proteines": result.get("proteines", []),
        }

    def suggerer_accompagnements_sync(
        self, recette_nom: str, categorie: str | None, saison: str = "printemps"
    ) -> dict:
        """Version synchrone de suggerer_accompagnements."""
        _sync = sync_wrapper(self.suggerer_accompagnements)
        return _sync(recette_nom, categorie, saison)

    async def detecter_categorie_recette(self, recette_nom: str, ingredients: str = "") -> str:
        """
        Détecte la catégorie nutritionnelle d'un plat via Mistral.

        Utilisé uniquement si type_proteines ET categorie_nutritionnelle sont absents.

        Args:
            recette_nom:  Nom de la recette
            ingredients:  Ingrédients principaux (optionnel, améliore la précision)

        Returns:
            categorie_nutritionnelle parmi :
            proteines_poisson | proteines_viande_rouge | proteines_volaille |
            proteines_oeuf | proteines_legumineuses | feculents | legumes_principaux | mixte
        """
        prompt = f"""Classifie ce plat en UNE SEULE catégorie nutritionnelle.

Plat : {recette_nom}
{f"Ingrédients principaux : {ingredients}" if ingredients else ""}

Catégories disponibles :
- proteines_poisson     : poisson, fruits de mer (ex: saumon, cabillaud, crevettes)
- proteines_viande_rouge: bœuf, porc, agneau, veau (ex: steak, côtelettes)
- proteines_volaille    : poulet, dinde, canard, lapin
- proteines_oeuf        : œufs comme protéine principale (ex: omelette, quiche)
- proteines_legumineuses: lentilles, pois chiches, haricots comme protéine principale
- feculents             : riz, pâtes, pommes de terre, semoule dominent (ex: gratin dauphinois)
- legumes_principaux    : légumes dominent sans protéine forte (ex: ratatouille, gratin courgettes)
- mixte                 : mélange équilibré (ex: pot-au-feu, hachis parmentier)

Réponds UNIQUEMENT avec le nom de la catégorie, rien d'autre."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es nutritionniste expert. Réponds avec UN seul mot-clé de catégorie.",
            max_tokens=30,
        )

        # Nettoyer la réponse : garder uniquement le token de catégorie
        categories_valides = {
            "proteines_poisson", "proteines_viande_rouge", "proteines_volaille",
            "proteines_oeuf", "proteines_legumineuses", "feculents",
            "legumes_principaux", "mixte",
        }
        token = result.strip().lower().replace("-", "_").split()[0] if result else "mixte"
        return token if token in categories_valides else "mixte"

    def detecter_categorie_recette_sync(
        self, recette_nom: str, ingredients: str = ""
    ) -> str:
        """Version synchrone de detecter_categorie_recette."""
        _sync = sync_wrapper(self.detecter_categorie_recette)
        return _sync(recette_nom, ingredients)

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

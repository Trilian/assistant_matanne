"""
Service IA Recettes - Génération & Adaptation

Service IA pour :
- Génération automatique de recettes
- Adaptation pour bébé
- Adaptation batch cooking
- Suggestions intelligentes
"""
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError

from src.core import (
    BaseAIService,
    RecipeAIMixin,
    obtenir_client_ia,
    handle_errors,
    valider_modele,
    RecetteInput,
    IngredientInput,
    EtapeInput,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════

class RecetteSuggestion(BaseModel):
    """Recette suggérée par l'IA."""
    nom: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(4, gt=0, le=20)
    difficulte: str = Field("moyen", pattern="^(facile|moyen|difficile)$")
    type_repas: str = Field(..., pattern="^(petit_déjeuner|déjeuner|dîner|goûter)$")
    saison: str = Field("toute_année", pattern="^(printemps|été|automne|hiver|toute_année)$")
    ingredients: List[Dict] = Field(..., min_length=1)
    etapes: List[Dict] = Field(..., min_length=1)


class VersionBebeGeneree(BaseModel):
    """Version bébé générée."""
    instructions_modifiees: str = Field(..., min_length=10)
    notes_bebe: str = Field(..., min_length=10)
    ingredients_modifies: Optional[Dict] = None
    age_minimum_mois: int = Field(6, ge=6, le=36)


class VersionBatchGeneree(BaseModel):
    """Version batch cooking générée."""
    etapes_paralleles: List[str] = Field(..., min_length=1)
    temps_optimise: int = Field(..., gt=0)
    conseils_batch: str = Field(..., min_length=10)
    portions_recommandees: int = Field(8, ge=4, le=20)


# ═══════════════════════════════════════════════════════════
# SERVICE IA RECETTES
# ═══════════════════════════════════════════════════════════

class RecetteAIService(BaseAIService, RecipeAIMixin):
    """
    Service IA pour recettes.

    Hérite de BaseAIService + RecipeAIMixin pour accès
    aux helpers spécifiques recettes.
    """

    def __init__(self, client=None):
        """
        Initialise le service IA recettes.

        Args:
            client: Client IA (optionnel, créé automatiquement sinon)
        """
        super().__init__(
            client=client or obtenir_client_ia(),
            cache_prefix="recettes_ai",
            default_ttl=3600,  # 1h pour recettes
            default_temperature=0.8  # Plus créatif
        )

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION RECETTES
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=[])
    async def generer_recettes(
            self,
            filters: Dict,
            ingredients_dispo: Optional[List[str]] = None,
            nb_recettes: int = 3
    ) -> List[RecetteSuggestion]:
        """
        Génère des suggestions de recettes.

        Args:
            filters: Filtres (saison, type_repas, difficulte, etc.)
            ingredients_dispo: Ingrédients disponibles (optionnel)
            nb_recettes: Nombre de recettes à générer

        Returns:
            Liste de recettes validées

        Example:
            >>> recettes = await ai_service.generer_recettes(
            ...     {"saison": "été", "type_repas": "dîner"},
            ...     ingredients_dispo=["tomates", "basilic"],
            ...     nb_recettes=3
            ... )
        """
        logger.info(f"Génération de {nb_recettes} recettes avec filtres: {filters}")

        # Construire contexte avec mixin
        context = self.build_recipe_context(
            filters=filters,
            ingredients_dispo=ingredients_dispo,
            nb_recettes=nb_recettes
        )

        # Construire prompt structuré
        prompt = self.build_json_prompt(
            context=context,
            task=f"Génère {nb_recettes} recettes originales et réalisables",
            json_schema=self._get_schema_recettes(),
            constraints=[
                "Ingrédients facilement trouvables",
                "Instructions claires et détaillées",
                "Temps réalistes",
                "Portions adaptées à une famille (4-6 personnes)",
                "Variété des plats (pas 2 fois la même base)"
            ]
        )

        # Appel IA avec parsing
        try:
            recettes = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=RecetteSuggestion,
                list_key="recettes",
                temperature=0.8,
                max_tokens=3000,
                use_cache=True,
                max_items=nb_recettes
            )

            # Validation métier supplémentaire
            recettes_valides = []
            for recette in recettes:
                # Valider avec le modèle complet RecetteInput
                is_valid, error_msg, validated = valider_modele(
                    RecetteInput,
                    {
                        **recette.dict(),
                        "type_repas": recette.type_repas,
                        "saison": recette.saison,
                        "difficulte": recette.difficulte,
                    }
                )

                if is_valid:
                    recettes_valides.append(recette)
                else:
                    logger.warning(f"Recette '{recette.nom}' invalide: {error_msg}")

            logger.info(f"✅ {len(recettes_valides)}/{nb_recettes} recettes générées et validées")
            return recettes_valides

        except Exception as e:
            logger.error(f"Erreur génération recettes: {e}")
            return self._get_fallback_recettes(nb_recettes, filters)

    # ═══════════════════════════════════════════════════════════
    # ADAPTATION BÉBÉ
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    async def adapter_recette_bebe(
            self,
            recette_id: int
    ) -> Optional[VersionBebeGeneree]:
        """
        Adapte une recette pour bébé.

        Args:
            recette_id: ID de la recette à adapter

        Returns:
            Version bébé générée et validée, ou None si erreur
        """
        logger.info(f"Adaptation bébé: recette {recette_id}")

        # Charger recette complète
        from .recette_service import recette_service
        recette = recette_service.get_by_id_full(recette_id)

        if not recette:
            logger.error(f"Recette {recette_id} introuvable")
            return None

        # Construire contexte avec mixin
        context = self.build_recipe_adaptation_context(
            recette=recette,
            adaptation_type="bébé"
        )

        # Prompt spécifique bébé
        prompt = f"""{context}

RÈGLES STRICTES BÉBÉ:
- PAS de sel ajouté
- PAS de sucre raffiné
- PAS de miel (risque botulisme avant 1 an)
- Texture adaptée (purée/morceaux selon âge)
- Portions réduites (60-120g selon âge)
- Cuisson complète obligatoire
- Allergènes identifiés clairement

FORMAT JSON:
{{
  "instructions_modifiees": "Instructions complètes adaptées bébé avec textures et portions",
  "notes_bebe": "Précautions allergènes, âge minimum, texture recommandée",
  "ingredients_modifies": {{
    "supprimer": ["sel", "sucre"],
    "remplacer": {{"lait de vache": "lait maternel ou infantile"}},
    "adapter": {{"tomates": "tomates pelées et épépinées"}}
  }},
  "age_minimum_mois": 8
}}

UNIQUEMENT JSON !"""

        try:
            version = await self.call_with_parsing(
                prompt=prompt,
                response_model=VersionBebeGeneree,
                temperature=0.7,
                max_tokens=1500,
                use_cache=True
            )

            logger.info(f"✅ Version bébé générée (âge min: {version.age_minimum_mois} mois)")
            return version

        except Exception as e:
            logger.error(f"Erreur adaptation bébé: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # ADAPTATION BATCH COOKING
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    async def adapter_recette_batch(
            self,
            recette_id: int
    ) -> Optional[VersionBatchGeneree]:
        """
        Adapte une recette en batch cooking.

        Args:
            recette_id: ID de la recette

        Returns:
            Version batch générée, ou None
        """
        logger.info(f"Adaptation batch: recette {recette_id}")

        from .recette_service import recette_service
        recette = recette_service.get_by_id_full(recette_id)

        if not recette:
            return None

        context = self.build_recipe_adaptation_context(
            recette=recette,
            adaptation_type="batch_cooking"
        )

        temps_total = recette.temps_preparation + recette.temps_cuisson

        prompt = f"""{context}

OBJECTIF BATCH COOKING:
- Multiplier par 2-3 les portions
- Paralléliser au maximum les tâches
- Optimiser le temps total (gain 20-30%)
- Prévoir congélation si possible

FORMAT JSON:
{{
  "etapes_paralleles": [
    "Pendant cuisson X, préparer Y",
    "Utiliser 2 plaques de cuisson simultanément"
  ],
  "temps_optimise": {int(temps_total * 0.7)},
  "conseils_batch": "Congeler en portions individuelles, utiliser contenants hermétiques, étiqueter avec date",
  "portions_recommandees": {recette.portions * 2}
}}

UNIQUEMENT JSON !"""

        try:
            version = await self.call_with_parsing(
                prompt=prompt,
                response_model=VersionBatchGeneree,
                temperature=0.7,
                max_tokens=1500,
                use_cache=True
            )

            gain_temps = temps_total - version.temps_optimise
            logger.info(f"✅ Version batch générée (gain: {gain_temps}min)")
            return version

        except Exception as e:
            logger.error(f"Erreur adaptation batch: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    def _get_schema_recettes(self) -> str:
        """Schéma JSON pour génération recettes."""
        return """
{
  "recettes": [
    {
      "nom": "Nom de la recette",
      "description": "Description appétissante en 1-2 phrases",
      "temps_preparation": 20,
      "temps_cuisson": 30,
      "portions": 4,
      "difficulte": "facile|moyen|difficile",
      "type_repas": "petit_déjeuner|déjeuner|dîner|goûter",
      "saison": "printemps|été|automne|hiver|toute_année",
      "ingredients": [
        {"nom": "Tomates", "quantite": 3, "unite": "pcs", "optionnel": false}
      ],
      "etapes": [
        {"ordre": 1, "description": "Étape détaillée", "duree": 10}
      ]
    }
  ]
}
"""

    def _get_fallback_recettes(
            self,
            nb: int,
            filters: Dict
    ) -> List[RecetteSuggestion]:
        """Recettes de secours en cas d'erreur."""
        type_repas = filters.get("type_repas", "dîner")
        saison = filters.get("saison", "toute_année")

        fallback = []

        # Recette simple universelle
        for i in range(min(nb, 2)):
            fallback.append(RecetteSuggestion(
                nom=f"Recette Simple {i+1}",
                description="Une recette simple et rapide pour tous les jours",
                temps_preparation=15,
                temps_cuisson=20,
                portions=4,
                difficulte="facile",
                type_repas=type_repas,
                saison=saison,
                ingredients=[
                    {"nom": "Ingrédient principal", "quantite": 500, "unite": "g", "optionnel": False}
                ],
                etapes=[
                    {"ordre": 1, "description": "Préparer les ingrédients", "duree": 10},
                    {"ordre": 2, "description": "Cuire et servir", "duree": 20}
                ]
            ))

        logger.warning(f"Utilisation de {len(fallback)} recettes fallback")
        return fallback


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

recette_ai_service = RecetteAIService()
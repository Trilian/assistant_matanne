# src/services/recette_version_service.py
"""
Service Génération Versions Recettes
Génération automatique des versions Bébé et Batch Cooking
"""
import asyncio
import json
import logging
from typing import Dict, Optional
from pydantic import BaseModel, Field

from src.core.ai_agent import AgentIA
from src.core.ai_cache import AICache, RateLimiter
from src.core.database import get_db_context
from src.core.models import Recette, VersionRecette, TypeVersionRecetteEnum

logger = logging.getLogger(__name__)


# ===================================
# SCHÉMAS PYDANTIC
# ===================================

class VersionBebeGeneree(BaseModel):
    """Version bébé générée par IA"""
    instructions_modifiees: str = Field(..., min_length=10)
    notes_bebe: str = Field(..., min_length=10)
    ingredients_modifies: Optional[Dict] = None
    age_minimum_mois: int = Field(6, ge=6, le=36)


class VersionBatchGeneree(BaseModel):
    """Version batch cooking générée"""
    etapes_paralleles: list[str] = Field(..., min_length=1)
    temps_optimise: int = Field(..., gt=0)
    conseils_batch: str = Field(..., min_length=10)
    portions_recommandees: int = Field(8, ge=4, le=20)


# ===================================
# SERVICE
# ===================================

class RecetteVersionService:
    """Service de génération de versions alternatives"""

    def __init__(self, agent: AgentIA):
        self.agent = agent

    # ===================================
    # VERSION BÉBÉ
    # ===================================

    async def generer_version_bebe(
            self,
            recette_id: int
    ) -> Optional[VersionBebeGeneree]:
        """
        Génère automatiquement une version bébé

        Returns:
            VersionBebeGeneree validée ou None
        """
        logger.info(f"Génération version bébé: recette {recette_id}")

        # Vérifier rate limit
        can_call, error = RateLimiter.can_call()
        if not can_call:
            raise ValueError(error)

        # Charger recette
        with get_db_context() as db:
            recette = db.query(Recette).get(recette_id)

            if not recette:
                return None

            # Construire prompt
            prompt = self._build_prompt_version_bebe(recette)

            # Appel IA
            response = await self._call_with_retry(
                prompt,
                "Nutritionniste pédiatrique expert. Réponds UNIQUEMENT en JSON.",
                1000
            )

            # Parser
            try:
                data = self._parse_json(response)
                version = VersionBebeGeneree(**data)

                logger.info(f"✅ Version bébé générée (âge: {version.age_minimum_mois}m)")
                return version

            except Exception as e:
                logger.error(f"Erreur parsing version bébé: {e}")
                return None

    def _build_prompt_version_bebe(self, recette: Recette) -> str:
        """Construit le prompt pour version bébé"""

        ingredients_str = "\n".join([
            f"- {ing.quantite} {ing.unite} {ing.ingredient.nom}"
            for ing in recette.ingredients
        ])

        etapes_str = "\n".join([
            f"{etape.ordre}. {etape.description}"
            for etape in sorted(recette.etapes, key=lambda x: x.ordre)
        ])

        return f"""Adapte cette recette pour un BÉBÉ de 6-18 mois.

RECETTE ORIGINALE: {recette.nom}

INGRÉDIENTS:
{ingredients_str}

ÉTAPES:
{etapes_str}

RÈGLES STRICTES BÉBÉ:
- PAS de sel ajouté
- PAS de sucre raffiné
- PAS de miel (risque botulisme)
- Texture adaptée (purée/morceaux selon âge)
- Portions réduites
- Cuisson complète
- Ingrédients allergènes identifiés

FORMAT JSON:
{{
  "instructions_modifiees": "Instructions complètes adaptées bébé avec textures et portions",
  "notes_bebe": "Précautions allergènes, âge minimum, texture recommandée",
  "ingredients_modifies": {{
    "supprimer": ["sel", "sucre"],
    "remplacer": {{"X": "Y"}},
    "adapter": {{"tomates": "tomates pelées"}}
  }},
  "age_minimum_mois": 8
}}

UNIQUEMENT JSON !"""

    # ===================================
    # VERSION BATCH COOKING
    # ===================================

    async def generer_version_batch(
            self,
            recette_id: int
    ) -> Optional[VersionBatchGeneree]:
        """
        Génère automatiquement une version batch cooking

        Returns:
            VersionBatchGeneree validée ou None
        """
        logger.info(f"Génération version batch: recette {recette_id}")

        can_call, error = RateLimiter.can_call()
        if not can_call:
            raise ValueError(error)

        with get_db_context() as db:
            recette = db.query(Recette).get(recette_id)

            if not recette:
                return None

            prompt = self._build_prompt_version_batch(recette)

            response = await self._call_with_retry(
                prompt,
                "Expert batch cooking. JSON uniquement.",
                1000
            )

            try:
                data = self._parse_json(response)
                version = VersionBatchGeneree(**data)

                logger.info(f"✅ Version batch générée (gain: {recette.temps_preparation + recette.temps_cuisson - version.temps_optimise}min)")
                return version

            except Exception as e:
                logger.error(f"Erreur parsing version batch: {e}")
                return None

    def _build_prompt_version_batch(self, recette: Recette) -> str:
        """Construit le prompt pour version batch"""

        ingredients_str = "\n".join([
            f"- {ing.quantite} {ing.unite} {ing.ingredient.nom}"
            for ing in recette.ingredients
        ])

        etapes_str = "\n".join([
            f"{etape.ordre}. {etape.description} ({etape.duree}min)" if etape.duree else f"{etape.ordre}. {etape.description}"
            for etape in sorted(recette.etapes, key=lambda x: x.ordre)
        ])

        temps_total = recette.temps_preparation + recette.temps_cuisson

        return f"""Optimise cette recette en mode BATCH COOKING (plusieurs portions).

RECETTE: {recette.nom}
TEMPS ACTUEL: {temps_total}min

INGRÉDIENTS (x{recette.portions}p):
{ingredients_str}

ÉTAPES:
{etapes_str}

OBJECTIF:
- Multiplier par 2-3 les portions
- Paralléliser au maximum
- Optimiser le temps total
- Congélation si possible

FORMAT JSON:
{{
  "etapes_paralleles": [
    "Pendant cuisson X, préparer Y",
    "Utiliser 2 plaques de cuisson simultanément"
  ],
  "temps_optimise": {int(temps_total * 0.7)},
  "conseils_batch": "Congeler en portions individuelles, utiliser contenants hermétiques",
  "portions_recommandees": {recette.portions * 2}
}}

JSON uniquement !"""

    # ===================================
    # SAUVEGARDE EN DB
    # ===================================

    def sauvegarder_version(
            self,
            recette_id: int,
            version_data: VersionBebeGeneree | VersionBatchGeneree,
            type_version: str
    ) -> bool:
        """
        Sauvegarde une version générée en base

        Returns:
            True si succès
        """
        with get_db_context() as db:
            # Supprimer ancienne version si existe
            db.query(VersionRecette).filter(
                VersionRecette.recette_base_id == recette_id,
                VersionRecette.type_version == type_version
            ).delete()

            # Créer nouvelle version
            if isinstance(version_data, VersionBebeGeneree):
                version = VersionRecette(
                    recette_base_id=recette_id,
                    type_version=TypeVersionRecetteEnum.BEBE.value,
                    instructions_modifiees=version_data.instructions_modifiees,
                    notes_bebe=version_data.notes_bebe,
                    ingredients_modifies=version_data.ingredients_modifies
                )
            else:  # VersionBatchGeneree
                version = VersionRecette(
                    recette_base_id=recette_id,
                    type_version=TypeVersionRecetteEnum.BATCH_COOKING.value,
                    etapes_paralleles_batch=version_data.etapes_paralleles,
                    temps_optimise_batch=version_data.temps_optimise
                )

            db.add(version)
            db.commit()

            logger.info(f"✅ Version {type_version} sauvegardée pour recette {recette_id}")
            return True

    # ===================================
    # HELPERS
    # ===================================

    async def _call_with_retry(
            self,
            prompt: str,
            system_prompt: str,
            max_tokens: int,
            max_retries: int = 3
    ) -> str:
        """Appel IA avec retry"""
        for attempt in range(max_retries):
            try:
                response = await self.agent._call_mistral(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=max_tokens
                )
                RateLimiter.record_call()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    def _parse_json(self, response: str) -> Dict:
        """Parse JSON depuis réponse IA"""
        cleaned = response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return json.loads(cleaned.strip())


# ===================================
# FACTORY
# ===================================

def create_recette_version_service(agent: AgentIA) -> RecetteVersionService:
    """Factory"""
    return RecetteVersionService(agent)
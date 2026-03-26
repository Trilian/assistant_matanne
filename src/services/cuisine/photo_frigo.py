"""
Service Photo Frigo — Analyse photo du frigo → suggestions de recettes.

Utilise Pixtral (vision multimodale) pour détecter les ingrédients
visibles dans une photo du frigo et suggérer des recettes.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.registry import service_factory
from src.services.integrations.multimodal import MultiModalAIService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class IngredientDetecte(BaseModel):
    """Ingrédient détecté dans la photo du frigo."""

    nom: str = Field(description="Nom de l'ingrédient")
    quantite_estimee: str | None = Field(None, description="Quantité estimée")
    confiance: float = Field(default=0.8, ge=0, le=1, description="Score de confiance")


class RecetteSuggestion(BaseModel):
    """Recette suggérée à partir des ingrédients détectés."""

    nom: str = Field(description="Nom de la recette")
    description: str = Field(description="Description courte")
    temps_preparation: int | None = Field(None, description="Temps en minutes")
    ingredients_utilises: list[str] = Field(default_factory=list)
    ingredients_manquants: list[str] = Field(default_factory=list)


class RecetteBD(BaseModel):
    """Recette depuis la base de données (match ingrédients)."""

    id: int
    nom: str
    description: str | None = None
    nb_ingredients_matches: int = 0
    pourcentage_match: float = 0.0
    ingredients_utilises: list[str] = Field(default_factory=list)


class ResultatPhotoFrigo(BaseModel):
    """Résultat complet de l'analyse photo frigo."""

    ingredients_detectes: list[IngredientDetecte] = Field(default_factory=list)
    recettes_suggerees: list[RecetteSuggestion] = Field(default_factory=list)
    recettes_db: list[RecetteBD] = Field(default_factory=list)
    sync_possible: bool = False


class ResultatPhotoFrigoMultiZone(BaseModel):
    """Résultat agrégé d'une analyse sur plusieurs zones."""

    zones_analysees: list[str] = Field(default_factory=list)
    ingredients_detectes: list[IngredientDetecte] = Field(default_factory=list)
    recettes_suggerees: list[RecetteSuggestion] = Field(default_factory=list)
    recettes_db: list[RecetteBD] = Field(default_factory=list)
    par_zone: dict[str, ResultatPhotoFrigo] = Field(default_factory=dict)
    sync_possible: bool = False


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


SYSTEM_PROMPT_DETECTION = """Tu es un expert en alimentation. Analyse cette photo de frigo ou d'aliments.

Identifie TOUS les ingrédients visibles (fruits, légumes, viandes, produits laitiers, condiments, etc.).
Pour chaque ingrédient, estime la quantité visible.

Réponds en JSON avec ce format exact:
{
    "ingredients": [
        {"nom": "tomates", "quantite_estimee": "4-5 pièces", "confiance": 0.95},
        {"nom": "fromage râpé", "quantite_estimee": "200g environ", "confiance": 0.8}
    ]
}

Sois exhaustif et précis. Langue: français."""

SYSTEM_PROMPT_RECETTES = """Tu es un chef cuisinier expert. À partir des ingrédients disponibles, suggère des recettes réalisables.

Privilégie:
- Les recettes utilisant un maximum d'ingrédients disponibles
- Les recettes simples et rapides
- La cuisine française et familiale

Pour chaque recette, indique les ingrédients utilisés parmi ceux disponibles
ET les ingrédients manquants (condiments basiques comme sel/poivre/huile sont considérés disponibles).

Réponds en JSON:
{
    "recettes": [
        {
            "nom": "Nom de la recette",
            "description": "Description courte et appétissante",
            "temps_preparation": 30,
            "ingredients_utilises": ["tomates", "fromage"],
            "ingredients_manquants": ["basilic frais"]
        }
    ]
}

Suggère 3 à 5 recettes maximum. Langue: français."""


class PhotoFrigoService:
    """Service d'analyse photo frigo via IA multimodale."""

    def __init__(self) -> None:
        self._multimodal: MultiModalAIService | None = None

    @property
    def multimodal(self) -> MultiModalAIService:
        if self._multimodal is None:
            from src.services.integrations.multimodal import get_multimodal_service
            self._multimodal = get_multimodal_service()
        return self._multimodal

    async def analyser_photo_frigo(
        self, image_bytes: bytes, zone: str = "frigo"
    ) -> ResultatPhotoFrigo:
        """Analyse une photo du frigo et suggère des recettes.

        1. Détecte les ingrédients dans l'image
        2. Cherche des recettes DB correspondantes
        3. Suggère des recettes supplémentaires via IA
        """
        # Étape 1 : Détection des ingrédients
        ingredients = await self._detecter_ingredients(image_bytes, zone)

        if not ingredients:
            return ResultatPhotoFrigo()

        noms_ingredients = [i.nom for i in ingredients]

        # Étape 2 : Recettes DB (synchrone)
        recettes_db = self.trouver_recettes_db(noms_ingredients)

        # Étape 3 : Suggestion de recettes IA
        recettes_ia = await self._suggerer_recettes(ingredients)

        return ResultatPhotoFrigo(
            ingredients_detectes=ingredients,
            recettes_suggerees=recettes_ia,
            recettes_db=recettes_db,
            sync_possible=len(ingredients) > 0,
        )

    async def analyser_photo_frigo_multi_zone(
        self,
        image_bytes: bytes,
        zones: list[str],
    ) -> ResultatPhotoFrigoMultiZone:
        """Analyse une même photo sur plusieurs contextes de zones.

        Permet d'améliorer la détection en appliquant des prompts adaptés à
        chaque zone (frigo, placard, congélateur), puis fusionne les résultats.
        """
        zones_uniques = [z for z in dict.fromkeys(zones) if z in {"frigo", "placard", "congelateur"}]
        if not zones_uniques:
            zones_uniques = ["frigo"]

        resultats_par_zone: dict[str, ResultatPhotoFrigo] = {}
        for zone in zones_uniques:
            resultats_par_zone[zone] = await self.analyser_photo_frigo(image_bytes, zone=zone)

        ingredients_map: dict[str, IngredientDetecte] = {}
        recettes_ia_map: dict[str, RecetteSuggestion] = {}
        recettes_db_map: dict[int, RecetteBD] = {}

        for resultat in resultats_par_zone.values():
            for ingredient in resultat.ingredients_detectes:
                cle = ingredient.nom.strip().lower()
                existant = ingredients_map.get(cle)
                if existant is None or ingredient.confiance > existant.confiance:
                    ingredients_map[cle] = ingredient

            for recette in resultat.recettes_suggerees:
                cle = recette.nom.strip().lower()
                if cle not in recettes_ia_map:
                    recettes_ia_map[cle] = recette

            for recette_db in resultat.recettes_db:
                existante = recettes_db_map.get(recette_db.id)
                if existante is None or recette_db.pourcentage_match > existante.pourcentage_match:
                    recettes_db_map[recette_db.id] = recette_db

        return ResultatPhotoFrigoMultiZone(
            zones_analysees=zones_uniques,
            ingredients_detectes=list(ingredients_map.values()),
            recettes_suggerees=list(recettes_ia_map.values()),
            recettes_db=list(recettes_db_map.values()),
            par_zone=resultats_par_zone,
            sync_possible=bool(ingredients_map),
        )

    def trouver_recettes_db(self, noms_ingredients: list[str]) -> list[RecetteBD]:
        """Cherche les recettes DB qui matchent les ingrédients détectés."""
        if not noms_ingredients:
            return []

        try:
            from sqlalchemy import func

            from src.api.utils import executer_avec_session
            from src.core.models import Ingredient, Recette, RecetteIngredient

            def _query():
                with executer_avec_session() as session:
                    # Trouver les IDs d'ingrédients matchant les noms détectés
                    ingredient_ids = [
                        row.id
                        for nom in noms_ingredients
                        for row in session.query(Ingredient.id).filter(
                            func.lower(Ingredient.nom).contains(nom.lower()[:8])
                        ).all()
                    ]

                    if not ingredient_ids:
                        return []

                    # Trouver les recettes avec le plus de matches
                    rows = (
                        session.query(
                            Recette.id,
                            Recette.nom,
                            Recette.description,
                            func.count(RecetteIngredient.ingredient_id.distinct()).label("nb_match"),
                            func.array_agg(Ingredient.nom.distinct()).label("ing_noms"),
                        )
                        .join(RecetteIngredient, RecetteIngredient.recette_id == Recette.id)
                        .join(Ingredient, Ingredient.id == RecetteIngredient.ingredient_id)
                        .filter(RecetteIngredient.ingredient_id.in_(ingredient_ids))
                        .group_by(Recette.id, Recette.nom, Recette.description)
                        .order_by(func.count(RecetteIngredient.ingredient_id.distinct()).desc())
                        .limit(5)
                        .all()
                    )

                    result = []
                    for row in rows:
                        # Compter total ingrédients de la recette pour le %
                        total = session.query(func.count(RecetteIngredient.id)).filter(
                            RecetteIngredient.recette_id == row.id
                        ).scalar() or 1
                        result.append(RecetteBD(
                            id=row.id,
                            nom=row.nom,
                            description=row.description,
                            nb_ingredients_matches=row.nb_match,
                            pourcentage_match=round(row.nb_match / total * 100),
                            ingredients_utilises=list(row.ing_noms or []),
                        ))
                    return result

            return _query()
        except Exception as e:
            logger.warning("trouver_recettes_db échoué: %s", e)
            return []

    async def _detecter_ingredients(
        self, image_bytes: bytes, zone: str = "frigo"
    ) -> list[IngredientDetecte]:
        """Détecte les ingrédients dans une photo via IA vision."""
        zone_labels = {
            "frigo": "frigo (produits frais, laitiers, légumes)",
            "placard": "placard (épicerie sèche, conserves, pâtes, riz)",
            "congelateur": "congélateur (surgelés, plats congelés)",
        }
        zone_label = zone_labels.get(zone, "réfrigérateur")
        prompt = f"Identifie tous les ingrédients visibles dans cette photo de {zone_label}."
        image_b64 = self.multimodal._encode_image(image_bytes)

        result = await self.multimodal._call_vision_model(
            image_b64=image_b64,
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_DETECTION,
        )

        if not result or not isinstance(result, dict):
            return []

        raw_ingredients = result.get("ingredients", [])
        return [
            IngredientDetecte(
                nom=ing.get("nom", ""),
                quantite_estimee=ing.get("quantite_estimee"),
                confiance=ing.get("confiance", 0.8),
            )
            for ing in raw_ingredients
            if ing.get("nom")
        ]

    async def _suggerer_recettes(
        self, ingredients: list[IngredientDetecte]
    ) -> list[RecetteSuggestion]:
        """Suggère des recettes à partir des ingrédients détectés."""
        noms = [i.nom for i in ingredients]
        prompt = f"Ingrédients disponibles : {', '.join(noms)}. Suggère des recettes."

        result = self.multimodal.call_with_json_parsing_sync(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_RECETTES,
        )

        if not result or not isinstance(result, dict):
            return []

        raw_recettes = result.get("recettes", [])
        return [
            RecetteSuggestion(
                nom=r.get("nom", ""),
                description=r.get("description", ""),
                temps_preparation=r.get("temps_preparation"),
                ingredients_utilises=r.get("ingredients_utilises", []),
                ingredients_manquants=r.get("ingredients_manquants", []),
            )
            for r in raw_recettes
            if r.get("nom")
        ]


@service_factory("photo_frigo")
def get_photo_frigo_service() -> PhotoFrigoService:
    """Factory pour le service photo frigo."""
    return PhotoFrigoService()

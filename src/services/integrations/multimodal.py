"""
Multi-Modal AI Service — Innovation v11: Images + Texte.

Service IA pour le traitement multi-modal:
- Reconnaissance de recettes depuis photos
- Extraction de données depuis factures/tickets
- Analyse nutritionnelle d'images de plats
- Description de photos pour accessibilité

Usage:
    from src.services.multimodal import (
        MultiModalAIService,
        get_multimodal_service,
        analyser_image_recette,
        extraire_facture,
        analyser_plat,
    )

    # Service complet
    service = get_multimodal_service()
    recette = service.extraire_recette_image_sync(image_bytes)

    # Helpers rapides
    ingredients = analyser_image_recette(uploaded_file)
    facture_data = extraire_facture(image_bytes)
"""

from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

__all__ = [
    "MultiModalAIService",
    "get_multimodal_service",
    "analyser_image_recette",
    "extraire_facture",
    "analyser_plat",
    "decrire_image",
]


# ═══════════════════════════════════════════════════════════
# SCHEMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class IngredientExtrait(BaseModel):
    """Ingrédient extrait d'une image."""

    nom: str = Field(description="Nom de l'ingrédient")
    quantite: str | None = Field(default=None, description="Quantité si visible")
    unite: str | None = Field(default=None, description="Unité si visible")
    confiance: float = Field(default=0.8, ge=0, le=1, description="Score de confiance")


class RecetteExtraite(BaseModel):
    """Recette extraite d'une image."""

    nom: str = Field(default="Recette sans nom", description="Nom probable du plat")
    ingredients: list[IngredientExtrait] = Field(default_factory=list)
    etapes: list[str] = Field(default_factory=list, description="Étapes si visibles")
    temps_preparation: str | None = Field(default=None, description="Temps préparation")
    temps_cuisson: str | None = Field(default=None, description="Temps cuisson")
    difficulte: str | None = Field(default=None, description="Niveau de difficulté")
    categorie: str | None = Field(default=None, description="Catégorie (entrée, plat, dessert)")


class LigneFacture(BaseModel):
    """Ligne d'une facture/ticket."""

    description: str = Field(description="Description du produit")
    quantite: float = Field(default=1, description="Quantité")
    prix_unitaire: float | None = Field(default=None, description="Prix unitaire")
    prix_total: float = Field(description="Prix total de la ligne")


class FactureExtraite(BaseModel):
    """Données extraites d'une facture/ticket."""

    magasin: str | None = Field(default=None, description="Nom du magasin")
    date: str | None = Field(default=None, description="Date d'achat")
    lignes: list[LigneFacture] = Field(default_factory=list)
    sous_total: float | None = Field(default=None)
    tva: float | None = Field(default=None)
    total: float | None = Field(default=None, description="Total TTC")
    mode_paiement: str | None = Field(default=None)


class AnalyseNutritionnelle(BaseModel):
    """Analyse nutritionnelle d'un plat photographié."""

    description: str = Field(description="Description du plat")
    calories_estimees: int = Field(default=0, description="Calories estimées (kcal)")
    proteines_g: float | None = Field(default=None)
    glucides_g: float | None = Field(default=None)
    lipides_g: float | None = Field(default=None)
    fibres_g: float | None = Field(default=None)
    portion_estimee: str | None = Field(default=None, description="Taille de portion")
    ingredients_detectes: list[str] = Field(default_factory=list)
    equilibre: str | None = Field(default=None, description="Verdict équilibre")
    conseils: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SERVICE MULTI-MODAL
# ═══════════════════════════════════════════════════════════


class MultiModalAIService(BaseAIService):
    """Service IA multi-modal pour analyse d'images.

    Utilise les APIs vision:
    - Mistral vision (pixtral)
    - OpenAI GPT-4V
    - Claude 3 vision

    Fonctionnalités:
    - Extraction de recettes depuis photos
    - OCR de factures et tickets
    - Analyse nutritionnelle de plats
    - Description d'images
    """

    def __init__(self, **kwargs):
        super().__init__(
            service_name="multimodal",
            cache_prefix="multimodal",
            **kwargs,
        )
        self._vision_model = "pixtral-12b-2024-09-18"  # Mistral vision model

    def _encode_image(self, image: bytes | str | Path) -> str:
        """Encode une image en base64.

        Args:
            image: Bytes, chemin, ou base64 existant

        Returns:
            String base64
        """
        if isinstance(image, str):
            if image.startswith("data:image"):
                # Déjà en base64 data URL
                return image
            if len(image) > 1000:
                # Probablement déjà en base64
                return f"data:image/jpeg;base64,{image}"
            # Chemin fichier
            image = Path(image)

        if isinstance(image, Path):
            image = image.read_bytes()

        # Bytes → base64
        b64 = base64.b64encode(image).decode("utf-8")

        # Détecter le type MIME
        mime = "image/jpeg"
        if image[:8] == b"\x89PNG\r\n\x1a\n":
            mime = "image/png"
        elif image[:4] == b"GIF8":
            mime = "image/gif"
        elif image[:4] == b"RIFF" and image[8:12] == b"WEBP":
            mime = "image/webp"

        return f"data:{mime};base64,{b64}"

    async def extraire_recette_image(
        self,
        image: bytes | str | Path,
        *,
        langue: str = "fr",
    ) -> RecetteExtraite | None:
        """Extrait une recette depuis une image.

        Analyse des photos de:
        - Recettes écrites/imprimées
        - Plats cuisinés (identifie les ingrédients)
        - Captures d'écran de sites de recettes

        Args:
            image: Image source
            langue: Langue de sortie

        Returns:
            RecetteExtraite ou None si échec
        """
        image_b64 = self._encode_image(image)

        system_prompt = f"""Tu es un expert culinaire. Analyse cette image et extrait la recette.

Si c'est une photo de plat cuisiné, identifie les ingrédients visibles et devine la recette.
Si c'est une photo de recette écrite, extrait le texte et structure-le.

Réponds en JSON avec ce format exact:
{{
    "nom": "Nom du plat",
    "ingredients": [
        {{"nom": "ingrédient", "quantite": "200", "unite": "g", "confiance": 0.9}}
    ],
    "etapes": ["Étape 1...", "Étape 2..."],
    "temps_preparation": "15 min",
    "temps_cuisson": "30 min",
    "difficulte": "Facile|Moyen|Difficile",
    "categorie": "Entrée|Plat|Dessert|Autre"
}}

Langue de réponse: {langue}
Sois précis sur les quantités si elles sont visibles."""

        try:
            result = await self._call_vision_model(
                image_b64=image_b64,
                prompt="Analyse cette image et extrait la recette.",
                system_prompt=system_prompt,
            )

            if result:
                return RecetteExtraite.model_validate(result)
            return None

        except Exception as e:
            logger.error(f"Erreur extraction recette: {e}")
            return None

    async def extraire_facture(
        self,
        image: bytes | str | Path,
    ) -> FactureExtraite | None:
        """Extrait les données d'une facture ou ticket de caisse.

        Args:
            image: Photo de facture/ticket

        Returns:
            FactureExtraite ou None
        """
        image_b64 = self._encode_image(image)

        system_prompt = """Tu es un expert OCR. Extrait les données de cette facture/ticket.

Réponds en JSON avec ce format:
{
    "magasin": "Nom du magasin",
    "date": "JJ/MM/AAAA",
    "lignes": [
        {"description": "Produit", "quantite": 1, "prix_unitaire": 2.50, "prix_total": 2.50}
    ],
    "sous_total": 10.00,
    "tva": 2.00,
    "total": 12.00,
    "mode_paiement": "CB|Espèces|Chèque"
}

Extrais TOUTES les lignes visibles. Si un champ n'est pas visible, mets null."""

        try:
            result = await self._call_vision_model(
                image_b64=image_b64,
                prompt="Extrait les données de cette facture ou ticket de caisse.",
                system_prompt=system_prompt,
            )

            if result:
                return FactureExtraite.model_validate(result)
            return None

        except Exception as e:
            logger.error(f"Erreur extraction facture: {e}")
            return None

    async def analyser_plat(
        self,
        image: bytes | str | Path,
    ) -> AnalyseNutritionnelle | None:
        """Analyse nutritionnelle d'une photo de plat.

        Args:
            image: Photo du plat

        Returns:
            AnalyseNutritionnelle ou None
        """
        image_b64 = self._encode_image(image)

        system_prompt = """Tu es un nutritionniste expert. Analyse cette photo de plat.

Réponds en JSON:
{
    "description": "Description du plat",
    "calories_estimees": 500,
    "proteines_g": 25,
    "glucides_g": 50,
    "lipides_g": 20,
    "fibres_g": 5,
    "portion_estimee": "Assiette moyenne (300g)",
    "ingredients_detectes": ["poulet", "riz", "légumes"],
    "equilibre": "Équilibré|Trop calorique|Manque de légumes|...",
    "conseils": ["Ajouter des légumes verts", "..."]
}

Base tes estimations sur les portions visibles. Sois réaliste."""

        try:
            result = await self._call_vision_model(
                image_b64=image_b64,
                prompt="Analyse nutritionnelle de ce plat.",
                system_prompt=system_prompt,
            )

            if result:
                return AnalyseNutritionnelle.model_validate(result)
            return None

        except Exception as e:
            logger.error(f"Erreur analyse nutritionnelle: {e}")
            return None

    async def decrire_image(
        self,
        image: bytes | str | Path,
        *,
        contexte: str = "général",
    ) -> str | None:
        """Génère une description textuelle d'une image.

        Utile pour:
        - Accessibilité (alt text)
        - Recherche sémantique
        - Documentation

        Args:
            image: Image source
            contexte: Contexte (cuisine, produit, général)

        Returns:
            Description textuelle
        """
        image_b64 = self._encode_image(image)

        context_instructions = {
            "cuisine": "Décris ce plat ou cette recette de manière appétissante.",
            "produit": "Décris ce produit alimentaire (marque, type, caractéristiques).",
            "général": "Décris cette image de manière détaillée.",
        }

        prompt = context_instructions.get(contexte, context_instructions["général"])

        try:
            result = await self._call_vision_model(
                image_b64=image_b64,
                prompt=prompt,
                system_prompt="Réponds en français avec une description concise mais complète.",
                return_json=False,
            )

            return result if isinstance(result, str) else str(result)

        except Exception as e:
            logger.error(f"Erreur description image: {e}")
            return None

    async def _call_vision_model(
        self,
        image_b64: str,
        prompt: str,
        system_prompt: str,
        *,
        return_json: bool = True,
    ) -> dict | str | None:
        """Appelle le modèle vision.

        Args:
            image_b64: Image encodée en base64 data URL
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            return_json: Parser la réponse en JSON

        Returns:
            Réponse dict/str ou None
        """
        # Lazy import du client
        if self.client is None:
            from src.core.ai import obtenir_client_ia

            self.client = obtenir_client_ia()

        try:
            # Appel API avec modèle vision (chat_with_vision)
            response = await self.client.chat_with_vision(
                prompt=f"{system_prompt}\n\n{prompt}",
                image_base64=image_b64.replace("data:image/jpeg;base64,", "").replace(
                    "data:image/png;base64,", ""
                ),
                temperature=0.3,
                max_tokens=2000,
            )

            if not response:
                return None

            # Parser JSON si demandé
            if return_json:
                from src.core.ai import AnalyseurIA

                analyseur = AnalyseurIA()
                return analyseur.extraire_json(response)

            return response

        except Exception as e:
            logger.error(f"Vision model error: {e}")
            # Fallback: essayer sans vision (description textuelle)
            if not return_json:
                return f"[Image non analysable: {e}]"
            return None


# ═══════════════════════════════════════════════════════════
# FACTORY & HELPERS
# ═══════════════════════════════════════════════════════════


@service_factory("multimodal", tags={"ia", "vision"})
def get_multimodal_service() -> MultiModalAIService:
    """Obtient le service multi-modal (singleton).

    Returns:
        Instance MultiModalAIService
    """
    return MultiModalAIService()


# Helpers synchrones pour usage direct


def analyser_image_recette(
    image: bytes | str | Path,
    *,
    langue: str = "fr",
) -> RecetteExtraite | None:
    """Helper: extrait une recette depuis une image.

    Args:
        image: Image de recette ou plat
        langue: Langue de sortie

    Returns:
        RecetteExtraite ou None
    """
    service = get_multimodal_service()
    return service.extraire_recette_image_sync(image, langue=langue)


def extraire_facture(image: bytes | str | Path) -> FactureExtraite | None:
    """Helper: extrait les données d'une facture.

    Args:
        image: Photo de facture/ticket

    Returns:
        FactureExtraite ou None
    """
    service = get_multimodal_service()
    return service.extraire_facture_sync(image)


def analyser_plat(image: bytes | str | Path) -> AnalyseNutritionnelle | None:
    """Helper: analyse nutritionnelle d'un plat.

    Args:
        image: Photo du plat

    Returns:
        AnalyseNutritionnelle ou None
    """
    service = get_multimodal_service()
    return service.analyser_plat_sync(image)


def decrire_image(
    image: bytes | str | Path,
    *,
    contexte: str = "général",
) -> str | None:
    """Helper: décrit une image.

    Args:
        image: Image source
        contexte: Contexte (cuisine, produit, général)

    Returns:
        Description textuelle
    """
    service = get_multimodal_service()
    return service.decrire_image_sync(image, contexte=contexte)

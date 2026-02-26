"""
Client IA — Module Vision/OCR (Pixtral)

Méthodes d'appel API avec images pour la reconnaissance visuelle.
Extrait du client monolithique pour une meilleure maintenabilité.
"""

__all__ = ["VisionMixin"]

import logging
from typing import TYPE_CHECKING

import httpx

from ..exceptions import ErreurServiceIA

logger = logging.getLogger(__name__)


class VisionMixin:
    """Mixin ajoutant les capacités vision/OCR au ClientIA.

    Nécessite que la classe hôte fournisse:
    - ``_ensure_config_loaded()``
    - ``cle_api``, ``url_base``
    """

    if TYPE_CHECKING:
        cle_api: str | None
        url_base: str | None

        def _ensure_config_loaded(self) -> None: ...

    async def chat_with_vision(
        self,
        prompt: str,
        image_base64: str,
        max_tokens: int = 1000,
        temperature: float = 0.3,
    ) -> str:
        """
        Appel API avec image (Vision) pour OCR.

        Args:
            prompt: Instructions pour l'analyse
            image_base64: Image encodée en base64
            max_tokens: Tokens max pour la réponse
            temperature: Température (recommandé: 0.3 pour OCR)

        Returns:
            Texte extrait de l'image
        """
        # Charger la config
        self._ensure_config_loaded()

        if not self.cle_api:
            raise ErreurServiceIA(
                "Clé API Mistral non configurée",
                message_utilisateur="La clé API Mistral n'est pas configurée.",
            )

        # Modèle vision (pixtral)
        vision_model = "pixtral-12b-2409"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.url_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.cle_api}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": vision_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            response.raise_for_status()
            result = response.json()

            if not result.get("choices"):
                raise ErreurServiceIA(
                    "Réponse vision vide", message_utilisateur="L'analyse de l'image a échoué"
                )

            content = result["choices"][0]["message"]["content"]
            logger.info(f"[OK] Vision: {len(content)} caractères extraits")

            return content

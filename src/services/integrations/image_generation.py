"""Service de generation d'images via Hugging Face Inference API."""

from __future__ import annotations

import base64
import logging
import os
from typing import Any

import httpx

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Genere des images d'inspiration depuis un prompt texte."""

    def __init__(self) -> None:
        self._token = os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_API_TOKEN")
        self._model = os.getenv(
            "HUGGINGFACE_IMAGE_MODEL",
            "stabilityai/stable-diffusion-xl-base-1.0",
        )
        self._base_url = os.getenv(
            "HUGGINGFACE_INFERENCE_URL",
            f"https://api-inference.huggingface.co/models/{self._model}",
        )

    def generer_image(
        self,
        *,
        prompt: str,
        negative_prompt: str | None = None,
        largeur: int = 1024,
        hauteur: int = 768,
    ) -> dict[str, Any]:
        """Genere une image et retourne un data URL base64 quand l'API est configuree."""
        if not self._token:
            return {
                "statut": "non_configure",
                "modele": self._model,
                "prompt": prompt,
                "image_base64": None,
                "message": "HUGGINGFACE_API_TOKEN manquant",
            }

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "image/png",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt or "",
                "width": largeur,
                "height": hauteur,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
            },
        }

        try:
            with httpx.Client(timeout=90.0, follow_redirects=True) as client:
                response = client.post(self._base_url, headers=headers, json=payload)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "image/png")
            if "application/json" in content_type:
                data = response.json()
                return {
                    "statut": "indisponible",
                    "modele": self._model,
                    "prompt": prompt,
                    "image_base64": None,
                    "message": data.get("error")
                    or data.get("estimated_time")
                    or "Generation impossible",
                }

            encoded = base64.b64encode(response.content).decode("utf-8")
            return {
                "statut": "ok",
                "modele": self._model,
                "prompt": prompt,
                "image_base64": f"data:{content_type};base64,{encoded}",
                "message": None,
            }
        except Exception as exc:
            logger.warning("Generation image HF impossible: %s", exc)
            return {
                "statut": "erreur",
                "modele": self._model,
                "prompt": prompt,
                "image_base64": None,
                "message": str(exc),
            }


@service_factory("image_generation", tags={"ia", "image", "habitat"})
def obtenir_service_generation_image() -> ImageGenerationService:
    """Factory singleton pour la generation d'images."""
    return ImageGenerationService()

"""
Client IA — Module Streaming SSE

Appel API avec réponse progressive (Server-Sent Events).
Extrait du client monolithique pour une meilleure maintenabilité.
"""

__all__ = ["StreamingMixin"]

import logging
from typing import TYPE_CHECKING

import httpx

from ..exceptions import ErreurLimiteDebit, ErreurServiceIA
from .rate_limit import RateLimitIA

logger = logging.getLogger(__name__)


class StreamingMixin:
    """Mixin ajoutant les capacités de streaming au ClientIA.

    Nécessite que la classe hôte fournisse:
    - ``_ensure_config_loaded()``
    - ``cle_api``, ``url_base``, ``modele``, ``timeout``
    """

    if TYPE_CHECKING:
        cle_api: str | None
        url_base: str | None
        modele: str | None
        timeout: float | None

        def _ensure_config_loaded(self) -> None: ...

    async def appeler_streaming(
        self,
        prompt: str,
        prompt_systeme: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """
        Appel API avec streaming — retourne un async generator.

        Permet d'afficher la réponse progressivement dans Streamlit.
        Le rate limiting est vérifié au début, le cache est IGNORÉ
        (streaming = pas de cache pour UX en temps réel).

        Args:
            prompt: Prompt utilisateur
            prompt_systeme: Instructions système
            temperature: Température (0-2)
            max_tokens: Tokens max

        Yields:
            str: Chunks de texte au fur et à mesure qu'ils arrivent

        Usage:
            async for chunk in client.appeler_streaming("Génère une recette"):
                print(chunk, end="", flush=True)

        Raises:
            ErreurServiceIA: Si erreur API
            ErreurLimiteDebit: Si rate limit dépassé
        """
        # Charger la config
        self._ensure_config_loaded()

        # Vérifier rate limit
        peut_appeler, message_erreur = RateLimitIA.peut_appeler()
        if not peut_appeler:
            raise ErreurLimiteDebit(message_erreur, message_utilisateur=message_erreur)

        if not self.cle_api:
            raise ErreurServiceIA(
                "Clé API Mistral non configurée",
                message_utilisateur="La clé API Mistral n'est pas configurée.",
            )

        messages: list[dict[str, str]] = []
        if prompt_systeme:
            messages.append({"role": "system", "content": prompt_systeme})
        messages.append({"role": "user", "content": prompt})

        full_response: list[str] = []

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.url_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.cle_api}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.modele,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    data = line[6:]  # Remove "data: " prefix

                    if data == "[DONE]":
                        break

                    try:
                        import json

                        chunk_json = json.loads(data)
                        choices = chunk_json.get("choices", [])

                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                full_response.append(content)
                                yield content

                    except Exception as e:
                        logger.debug(f"Erreur parsing chunk streaming: {e}")
                        continue

        # Enregistrer l'appel
        total_content = "".join(full_response)
        RateLimitIA.enregistrer_appel(service="mistral_streaming")
        logger.info(f"[OK] Streaming terminé ({len(total_content)} caractères)")

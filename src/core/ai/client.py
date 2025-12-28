"""
Client IA Unifié - Mistral AI
Remplace ai_agent.py avec meilleure architecture
"""
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..config import get_settings
from ..errors import AIServiceError, RateLimitError
from .cache import AICache

logger = logging.getLogger(__name__)


class AIClient:
    """
    Client IA unifié pour Mistral

    Fonctionnalités:
    - Appels API avec retry automatique
    - Cache intelligent
    - Rate limiting
    - Gestion d'erreurs robuste
    """

    def __init__(self):
        """Initialise le client avec la config"""
        settings = get_settings()

        try:
            self.api_key = settings.MISTRAL_API_KEY
            self.model = settings.MISTRAL_MODEL
            self.base_url = settings.MISTRAL_BASE_URL
            self.timeout = settings.MISTRAL_TIMEOUT

            logger.info(f"✅ AIClient initialisé (modèle: {self.model})")

        except ValueError as e:
            logger.error(f"❌ Configuration IA manquante: {e}")
            raise AIServiceError(
                str(e),
                user_message="Configuration IA manquante"
            )

    # ═══════════════════════════════════════════════════════════
    # APPEL API PRINCIPAL
    # ═══════════════════════════════════════════════════════════

    async def call(
            self,
            prompt: str,
            system_prompt: str = "",
            temperature: float = 0.7,
            max_tokens: int = 1000,
            use_cache: bool = True,
            max_retries: int = 3
    ) -> str:
        """
        Appel API avec cache et retry

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            temperature: Température (0-2)
            max_tokens: Tokens max
            use_cache: Utiliser le cache
            max_retries: Nombre de retries

        Returns:
            Réponse de l'IA

        Raises:
            AIServiceError: Si erreur API
            RateLimitError: Si rate limit dépassé
        """
        # Vérifier rate limit
        from .cache import RateLimit
        can_call, error_msg = RateLimit.can_call()
        if not can_call:
            raise RateLimitError(error_msg, user_message=error_msg)

        # Vérifier cache
        if use_cache:
            cache_key = AICache.generate_key(
                prompt=prompt,
                system=system_prompt,
                temperature=temperature
            )

            cached = AICache.get(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {cache_key[:50]}")
                return cached

        # Appel API avec retry
        for attempt in range(max_retries):
            try:
                response = await self._do_call(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # Enregistrer appel
                RateLimit.record_call()

                # Cacher résultat
                if use_cache:
                    AICache.set(cache_key, response)

                return response

            except httpx.HTTPError as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ API error after {max_retries} retries: {e}")
                    raise AIServiceError(
                        f"Erreur API Mistral: {str(e)}",
                        user_message="L'IA est temporairement indisponible"
                    )

                # Attente exponentielle
                wait_time = 2 ** attempt
                logger.warning(f"Retry {attempt + 1}/{max_retries} après {wait_time}s")
                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                raise AIServiceError(
                    f"Erreur inattendue: {str(e)}",
                    user_message="Erreur lors de l'appel IA"
                )

        # Ne devrait jamais arriver ici
        raise AIServiceError("Échec après tous les retries")

    async def _do_call(
            self,
            prompt: str,
            system_prompt: str,
            temperature: float,
            max_tokens: int
    ) -> str:
        """Effectue l'appel API réel"""
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            )

            response.raise_for_status()
            result = response.json()

            content = result["choices"][0]["message"]["content"]
            logger.info(f"✅ Réponse reçue ({len(content)} chars)")

            return content

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES MÉTIER (LEGACY)
    # ═══════════════════════════════════════════════════════════

    async def chat(
            self,
            message: str,
            historique: List[Dict] = None,
            contexte: Optional[Dict] = None
    ) -> str:
        """
        Interface conversationnelle (legacy)

        Maintenu pour compatibilité avec l'ancien code
        """
        hist_text = ""
        if historique:
            hist_text = "\n".join([
                f"{h['role']}: {h['content']}"
                for h in historique[-5:]
            ])

        ctx_text = ""
        if contexte:
            import json
            ctx_text = f"\n\nContexte:\n{json.dumps(contexte, indent=2)}"

        system_prompt = (
            "Tu es l'assistant familial MaTanne. "
            "Tu aides avec: Cuisine, Famille, Maison, Planning."
            f"{ctx_text}"
        )

        prompt = f"Historique:\n{hist_text}\n\nUtilisateur: {message}"

        return await self.call(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def get_model_info(self) -> Dict[str, Any]:
        """Retourne info sur le modèle"""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout
        }


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (LAZY)
# ═══════════════════════════════════════════════════════════

_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """
    Récupère l'instance AIClient (singleton lazy)

    Returns:
        Instance AIClient
    """
    global _client
    if _client is None:
        _client = AIClient()
    return _client
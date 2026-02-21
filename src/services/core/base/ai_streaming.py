"""Mixin: streaming IA — réponse progressive pour UX temps réel."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AIStreamingMixin:
    """Fournit call_with_streaming et call_with_streaming_sync.

    Attend sur ``self``: client, default_temperature, service_name, circuit_breaker.
    """

    async def call_with_streaming(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
    ):
        """
        Appel IA avec streaming — retourne un async generator.

        Utile pour afficher progressivement les réponses longues (suggestions,
        analyses, etc.) dans Streamlit via st.write_stream() ou un container
        personnalisé.

        Le cache est IGNORÉ en streaming (UX temps réel prioritaire).
        Le circuit breaker et rate limiting sont toujours appliqués.

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            temperature: Température (None = default)
            max_tokens: Tokens max

        Yields:
            str: Chunks de texte au fur et à mesure qu'ils arrivent

        Usage dans Streamlit:
            # Option 1: st.write_stream() (Streamlit >= 1.31)
            st.write_stream(service.call_with_streaming_sync(prompt))

            # Option 2: Container manuel
            container = st.empty()
            full_text = ""
            for chunk in service.call_with_streaming_sync(prompt):
                full_text += chunk
                container.markdown(full_text)

        Raises:
            ErreurLimiteDebit: Si quota dépassé
        """
        if self.client is None:
            logger.warning(f"⚠️ Client IA indispo ({self.service_name})")
            return

        temp = temperature if temperature is not None else self.default_temperature

        # Vérifier circuit breaker AVANT l'appel
        from src.core.ai.circuit_breaker import EtatCircuit

        etat = self.circuit_breaker.etat
        if etat == EtatCircuit.OUVERT:
            logger.warning(f"⚡ Circuit '{self.circuit_breaker.nom}' OUVERT — streaming bloqué")
            return

        try:
            async for chunk in self.client.appeler_streaming(
                prompt=prompt,
                prompt_systeme=system_prompt,
                temperature=temp,
                max_tokens=max_tokens,
            ):
                yield chunk

            self.circuit_breaker._enregistrer_succes()

        except Exception as e:
            self.circuit_breaker._enregistrer_echec()
            logger.warning(f"Streaming échoué ({self.service_name}): {e}")
            raise

    def call_with_streaming_sync(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
    ):
        """
        Version synchrone du streaming pour Streamlit.

        Retourne un générateur synchrone qui peut être passé directement
        à st.write_stream() ou itéré dans une boucle.

        Usage:
            # Avec st.write_stream()
            st.write_stream(service.call_with_streaming_sync("Génère une recette"))

            # Avec boucle manuelle
            for chunk in service.call_with_streaming_sync("Génère une recette"):
                st.write(chunk)
        """
        import asyncio
        import concurrent.futures

        async def collect_chunks():
            chunks = []
            async for chunk in self.call_with_streaming(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                chunks.append(chunk)
            return chunks

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # Event loop active — use thread
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, collect_chunks())
                chunks = future.result()
        else:
            chunks = asyncio.run(collect_chunks())

        # Yield les chunks un par un (pour st.write_stream)
        yield from chunks

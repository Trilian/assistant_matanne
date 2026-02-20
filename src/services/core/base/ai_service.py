"""
Base AI Service - Service IA Générique avec Rate Limiting Auto
Version améliorée avec gestion automatique des quotas et retry

[!] Ce module N'IMPORTE PAS streamlit — découplé de l'UI.
    Les erreurs sont loguées et propagées, l'affichage est géré
    par la couche UI via l'Event Bus.
"""

import logging
from datetime import datetime

from pydantic import BaseModel, ValidationError

from src.core.ai import AnalyseurIA, CircuitBreaker, ClientIA, RateLimitIA, obtenir_circuit
from src.core.ai.cache import CacheIA
from src.core.errors_base import ErreurLimiteDebit
from src.services.core.base.async_utils import sync_wrapper

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# BASE AI SERVICE (AVEC RATE LIMITING AUTO)
# ═══════════════════════════════════════════════════════════


class BaseAIService:
    """
    Service IA de base avec fonctionnalités communes

    Fonctionnalités AUTO :
    - ✅ Rate limiting avec retry intelligent
    - ✅ Cache sémantique automatique
    - ✅ Circuit breaker (protection service externe)
    - ✅ Parsing JSON robuste
    - ✅ Gestion d'erreurs unifiée
    - ✅ Logging avec métriques
    """

    def __init__(
        self,
        client: ClientIA,
        cache_prefix: str = "ai",
        default_ttl: int = 3600,
        default_temperature: float = 0.7,
        service_name: str = "unknown",
        circuit_breaker: CircuitBreaker | None = None,
    ):
        """
        Initialise le service IA

        Args:
            client: Client IA (ClientIA)
            cache_prefix: Préfixe pour clés cache
            default_ttl: TTL cache par défaut (secondes)
            default_temperature: Température par défaut
            service_name: Nom du service (pour analytics)
            circuit_breaker: Circuit breaker (auto-créé si None)
        """
        self.client = client
        self.cache_prefix = cache_prefix
        self.default_ttl = default_ttl
        self.default_temperature = default_temperature
        self.service_name = service_name
        self.circuit_breaker = circuit_breaker or obtenir_circuit(
            nom=f"ai_{service_name}",
            seuil_echecs=5,
            delai_reset=60.0,
        )

    # ═══════════════════════════════════════════════════════════
    # APPELS IA AVEC RATE LIMITING AUTO + CACHE
    # ═══════════════════════════════════════════════════════════

    async def call_with_cache(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
        use_cache: bool = True,
        category: str | None = None,
    ) -> str | None:
        """
        Appel IA avec rate limiting + cache automatiques

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            temperature: Température (None = default)
            max_tokens: Tokens max
            use_cache: Utiliser le cache
            category: Catégorie pour cache

        Returns:
            Réponse IA ou None si erreur

        Raises:
            ErreurLimiteDebit: Si quota atteint
        """
        # ✅ Vérifier que le client IA est disponible
        if self.client is None:
            logger.warning(f"⚠️ Client IA indispo ({self.service_name})")
            return None

        temp = temperature if temperature is not None else self.default_temperature
        cache_category = category or self.cache_prefix

        # ✅ Vérifier cache AVANT rate limit (économise les quotas)
        if use_cache:
            cached = CacheIA.obtenir(
                prompt=prompt,
                systeme=system_prompt,
                temperature=temp,
            )

            if cached:
                logger.info(f"✅ Cache HIT ({cache_category}) - Quota économisé !")
                return cached

        # ✅ Vérifier rate limit AUTO
        autorise, msg = RateLimitIA.peut_appeler()
        if not autorise:
            logger.warning(f"⏳ Rate limit: {msg}")
            raise ErreurLimiteDebit(msg, message_utilisateur=msg)

        # ✅ Vérifier circuit breaker AVANT l'appel
        from src.core.ai.circuit_breaker import EtatCircuit

        etat = self.circuit_breaker.etat
        if etat == EtatCircuit.OUVERT:
            logger.warning(f"⚡ Circuit '{self.circuit_breaker.nom}' OUVERT — appel bloqué")
            return None

        # Appel IA protégé par CircuitBreaker
        start_time = datetime.now()

        try:
            response = await self.client.appeler(
                prompt=prompt,
                prompt_systeme=system_prompt,
                temperature=temp,
                max_tokens=max_tokens,
                utiliser_cache=False,  # On gère le cache nous-mêmes
            )
            self.circuit_breaker._enregistrer_succes()
        except Exception as e:
            self.circuit_breaker._enregistrer_echec()
            logger.warning("Appel IA échoué (%s): %s", self.service_name, e)
            raise

        duration = (datetime.now() - start_time).total_seconds()

        # ✅ Enregistrer appel AUTO (avec métriques)
        RateLimitIA.enregistrer_appel(
            service=self.service_name,
            tokens_utilises=len(response) if response else 0,  # Approximation
        )

        logger.info(
            f"✅ Appel IA réussi ({self.service_name}) - "
            f"{duration:.2f}s - {len(response) if response else 0} chars"
        )

        # Sauvegarder dans cache
        if use_cache and response:
            CacheIA.definir(
                prompt=prompt,
                reponse=response,
                systeme=system_prompt,
                temperature=temp,
            )

        return response

    # ═══════════════════════════════════════════════════════════
    # PARSING AVEC VALIDATION
    # ═══════════════════════════════════════════════════════════

    async def call_with_parsing(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
        use_cache: bool = True,
        fallback: dict | None = None,
    ) -> BaseModel | None:
        """
        Appel IA avec parsing automatique vers modèle Pydantic

        Rate limiting + cache AUTO intégrés !
        """
        # Appel IA (rate limiting déjà géré)
        response = await self.call_with_cache(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache,
        )

        if not response:
            return None

        # Parser avec AnalyseurIA
        try:
            parsed = AnalyseurIA.analyser(
                reponse=response, modele=response_model, valeur_secours=fallback, strict=False
            )

            logger.info(f"✅ Parsing réussi: {response_model.__name__}")
            return parsed

        except ValidationError as e:
            logger.error(f"❌ Erreur parsing {response_model.__name__}: {e}")

            if fallback:
                logger.warning("Utilisation fallback")
                return response_model(**fallback)

            return None

    # Version synchrone auto-générée via sync_wrapper
    call_with_parsing_sync = sync_wrapper(call_with_parsing)

    async def call_with_list_parsing(
        self,
        prompt: str,
        item_model: type[BaseModel],
        list_key: str = "items",
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 2000,
        use_cache: bool = True,
        max_items: int | None = None,
    ) -> list[BaseModel]:
        """
        Appel IA avec parsing d'une liste

        Rate limiting + cache AUTO intégrés !
        """
        # Appel IA (rate limiting déjà géré)
        response = await self.call_with_cache(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache,
        )

        if not response:
            return []

        # Parser liste
        try:
            from src.core.ai.parser import analyser_liste_reponse

            items = analyser_liste_reponse(
                reponse=response, modele_item=item_model, cle_liste=list_key, items_secours=[]
            )

            # Limiter nombre d'items
            if max_items and len(items) > max_items:
                items = items[:max_items]
                logger.info(f"Liste limitée à {max_items} items")

            logger.info(f"✅ {len(items)} items parsés ({item_model.__name__})")
            return items

        except Exception as e:
            logger.error(f"❌ Erreur parsing liste: {e}")
            return []

    # Version synchrone auto-générée via sync_wrapper
    call_with_list_parsing_sync = sync_wrapper(call_with_list_parsing)

    async def call_with_json_parsing(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 2000,
        use_cache: bool = True,
    ) -> BaseModel | None:
        """
        Appel IA avec parsing direct vers un modèle Pydantic unique.

        Args:
            prompt: Prompt utilisateur
            response_model: Modèle Pydantic attendu en réponse
            system_prompt: Instructions système
            temperature: Température (None = default)
            max_tokens: Tokens max
            use_cache: Utiliser le cache

        Returns:
            Instance du modèle Pydantic ou None si erreur
        """
        response = await self.call_with_cache(
            prompt=prompt,
            system_prompt=system_prompt
            or "Retourne uniquement du JSON valide, pas de markdown ni de texte.",
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache,
        )

        if not response:
            return None

        # Déléguer le parsing JSON à AnalyseurIA (nettoyage markdown inclus)
        try:
            parsed = AnalyseurIA.analyser(
                reponse=response,
                modele=response_model,
                valeur_secours=None,
                strict=False,
            )
            logger.info(f"✅ JSON parsé vers {response_model.__name__}")
            return parsed

        except ValidationError as e:
            logger.error(f"❌ Erreur validation Pydantic: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur parsing inattendue: {e}")
            return None

    # Version synchrone auto-générée via sync_wrapper
    call_with_json_parsing_sync = sync_wrapper(call_with_json_parsing)

    # ═══════════════════════════════════════════════════════════
    # HELPERS PROMPTS STRUCTURÉS
    # ═══════════════════════════════════════════════════════════

    def build_json_prompt(
        self, context: str, task: str, json_schema: str, constraints: list[str] | None = None
    ) -> str:
        """Construit un prompt structuré pour réponse JSON"""
        prompt = f"{context}\n\n"
        prompt += f"TÂCHE: {task}\n\n"

        if constraints:
            prompt += "CONTRAINTES:\n"
            for constraint in constraints:
                prompt += f"- {constraint}\n"
            prompt += "\n"

        prompt += "FORMAT JSON ATTENDU:\n"
        prompt += f"{json_schema}\n\n"
        prompt += "IMPORTANT: Réponds UNIQUEMENT en JSON valide, sans texte avant ou après."

        return prompt

    def build_system_prompt(
        self, role: str, expertise: list[str], rules: list[str] | None = None
    ) -> str:
        """Construit un system prompt structuré"""
        prompt = f"Tu es {role}.\n\n"

        prompt += "EXPERTISE:\n"
        for exp in expertise:
            prompt += f"- {exp}\n"
        prompt += "\n"

        if rules:
            prompt += "RÈGLES:\n"
            for rule in rules:
                prompt += f"- {rule}\n"
            prompt += "\n"

        prompt += "Réponds toujours en français, de manière claire et structurée."

        return prompt

    # ═══════════════════════════════════════════════════════════
    # MÉTRIQUES & DEBUG
    # ═══════════════════════════════════════════════════════════

    def get_cache_stats(self) -> dict:
        """Retourne statistiques cache"""
        return CacheIA.obtenir_statistiques()

    def get_rate_limit_stats(self) -> dict:
        """Retourne statistiques rate limiting"""
        return RateLimitIA.obtenir_statistiques()

    def clear_cache(self):
        """Vide le cache"""
        CacheIA.invalider_tout()
        logger.info(f"🗑️ Cache {self.cache_prefix} vidé")

    def get_circuit_breaker_stats(self) -> dict:
        """Retourne statistiques du circuit breaker."""
        return self.circuit_breaker.obtenir_statistiques()

    def reset_circuit_breaker(self):
        """Reset manuel du circuit breaker."""
        self.circuit_breaker.reset()

    # ═══════════════════════════════════════════════════════════
    # API SAFE — Retourne Result[T, ErrorInfo] au lieu de None
    # ═══════════════════════════════════════════════════════════

    async def safe_call_with_cache(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
        use_cache: bool = True,
        category: str | None = None,
    ):
        """Appel IA retournant Result au lieu de str|None.

        Returns:
            Success[str] si réponse, Failure[ErrorInfo] si erreur/rate limit
        """
        from src.services.core.base.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache,
                category=category,
            )
            if response is None:
                return failure(
                    ErrorCode.AI_UNAVAILABLE,
                    "Client IA indisponible",
                    message_utilisateur="Le service IA est temporairement indisponible",
                    source=self.service_name,
                )
            return success(response)
        except ErreurLimiteDebit as e:
            return failure(
                ErrorCode.RATE_LIMITED,
                str(e),
                message_utilisateur=str(e),
                source=self.service_name,
            )
        except Exception as e:
            return from_exception(e, source=self.service_name)

    async def safe_call_with_parsing(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
        use_cache: bool = True,
        fallback: dict | None = None,
    ):
        """Appel IA avec parsing Pydantic, retourne Result.

        Returns:
            Success[BaseModel] si parsé, Failure[ErrorInfo] si échec
        """
        from src.services.core.base.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            parsed = await self.call_with_parsing(
                prompt=prompt,
                response_model=response_model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache,
                fallback=fallback,
            )
            if parsed is None:
                return failure(
                    ErrorCode.PARSING_ERROR,
                    f"Impossible de parser la réponse vers {response_model.__name__}",
                    source=self.service_name,
                )
            return success(parsed)
        except Exception as e:
            return from_exception(e, source=self.service_name)

    async def safe_call_with_list_parsing(
        self,
        prompt: str,
        item_model: type[BaseModel],
        list_key: str = "items",
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 2000,
        use_cache: bool = True,
        max_items: int | None = None,
    ):
        """Appel IA avec parsing liste, retourne Result.

        Returns:
            Success[list[BaseModel]], Failure[ErrorInfo] si erreur
        """
        from src.services.core.base.result import from_exception, success

        try:
            items = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=item_model,
                list_key=list_key,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache,
                max_items=max_items,
            )
            return success(items)
        except Exception as e:
            return from_exception(e, source=self.service_name)

    async def safe_call_with_json_parsing(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 2000,
        use_cache: bool = True,
    ):
        """Appel IA avec parsing JSON, retourne Result.

        Returns:
            Success[BaseModel] si parsé, Failure[ErrorInfo] si échec
        """
        from src.services.core.base.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            parsed = await self.call_with_json_parsing(
                prompt=prompt,
                response_model=response_model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache,
            )
            if parsed is None:
                return failure(
                    ErrorCode.PARSING_ERROR,
                    f"Impossible de parser JSON vers {response_model.__name__}",
                    source=self.service_name,
                )
            return success(parsed)
        except Exception as e:
            return from_exception(e, source=self.service_name)

    # Versions synchrones des méthodes safe
    safe_call_with_cache_sync = sync_wrapper(safe_call_with_cache)
    safe_call_with_parsing_sync = sync_wrapper(safe_call_with_parsing)
    safe_call_with_list_parsing_sync = sync_wrapper(safe_call_with_list_parsing)
    safe_call_with_json_parsing_sync = sync_wrapper(safe_call_with_json_parsing)

    # ═══════════════════════════════════════════════════════════
    # HEALTH CHECK — Satisfait HealthCheckProtocol
    # ═══════════════════════════════════════════════════════════

    def health_check(self):
        """Vérifie la santé du service IA (client, rate limit).

        Returns:
            ServiceHealth avec statut, latence et détails quotas
        """
        import time

        from src.services.core.base.protocols import ServiceHealth, ServiceStatus

        start = time.perf_counter()
        details: dict = {"service_name": self.service_name}

        try:
            # Vérifier client
            client_ok = self.client is not None
            details["client_available"] = client_ok

            # Vérifier rate limit
            autorise, msg = RateLimitIA.peut_appeler()
            details["rate_limit_ok"] = autorise
            if not autorise:
                details["rate_limit_message"] = msg

            # Vérifier circuit breaker
            cb_stats = self.circuit_breaker.obtenir_statistiques()
            details["circuit_breaker"] = cb_stats

            # Récupérer stats
            details["rate_limit_stats"] = self.get_rate_limit_stats()
            details["cache_stats"] = self.get_cache_stats()

            latency = (time.perf_counter() - start) * 1000

            if not client_ok:
                return ServiceHealth(
                    status=ServiceStatus.UNHEALTHY,
                    service_name=f"AI:{self.service_name}",
                    message="Client IA indisponible",
                    latency_ms=latency,
                    details=details,
                )

            if not autorise:
                return ServiceHealth(
                    status=ServiceStatus.DEGRADED,
                    service_name=f"AI:{self.service_name}",
                    message=f"Rate limité: {msg}",
                    latency_ms=latency,
                    details=details,
                )

            # Vérifier état du circuit breaker
            from src.core.ai.circuit_breaker import EtatCircuit

            if cb_stats["etat"] != EtatCircuit.FERME.value:
                return ServiceHealth(
                    status=ServiceStatus.DEGRADED,
                    service_name=f"AI:{self.service_name}",
                    message=f"Circuit breaker {cb_stats['etat']} "
                    f"({cb_stats['echecs_consecutifs']} échecs)",
                    latency_ms=latency,
                    details=details,
                )

            return ServiceHealth(
                status=ServiceStatus.HEALTHY,
                service_name=f"AI:{self.service_name}",
                message="Service IA opérationnel",
                latency_ms=latency,
                details=details,
            )
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                service_name=f"AI:{self.service_name}",
                message=f"Erreur health check: {e}",
                latency_ms=latency,
                details={"error": str(e)},
            )


# ═══════════════════════════════════════════════════════════
# MIXINS SPÉCIALISÉS — voir ai_mixins.py (source unique)
# ═══════════════════════════════════════════════════════════
from .ai_mixins import InventoryAIMixin, PlanningAIMixin, RecipeAIMixin  # noqa: E402, F401

# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def create_base_ai_service(
    cache_prefix: str = "ai",
    default_ttl: int = 3600,
    default_temperature: float = 0.7,
    service_name: str = "unknown",
    seuil_echecs: int = 5,
    delai_reset: float = 60.0,
) -> BaseAIService:
    """Factory pour créer un BaseAIService avec CircuitBreaker.

    Args:
        cache_prefix: Préfixe pour clés cache
        default_ttl: TTL cache par défaut (secondes)
        default_temperature: Température par défaut
        service_name: Nom du service (pour analytics)
        seuil_echecs: Échecs consécutifs avant ouverture du circuit
        delai_reset: Délai en secondes avant test de reprise
    """
    from src.core.ai import obtenir_client_ia

    client = obtenir_client_ia()
    cb = obtenir_circuit(
        nom=f"ai_{service_name}",
        seuil_echecs=seuil_echecs,
        delai_reset=delai_reset,
    )

    return BaseAIService(
        client=client,
        cache_prefix=cache_prefix,
        default_ttl=default_ttl,
        default_temperature=default_temperature,
        service_name=service_name,
        circuit_breaker=cb,
    )

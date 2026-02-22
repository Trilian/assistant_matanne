"""
Base AI Service - Service IA Générique avec Rate Limiting Auto.

Compose 4 mixins (streaming, safe, diagnostics, prompts) pour garder
chaque fichier à taille raisonnable tout en conservant la même API publique.

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
from src.services.core.base.ai_diagnostics import AIDiagnosticsMixin
from src.services.core.base.ai_prompts import AIPromptsMixin
from src.services.core.base.ai_streaming import AIStreamingMixin
from src.services.core.base.async_utils import ServiceMeta, sync_wrapper

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# BASE AI SERVICE (AVEC RATE LIMITING AUTO)
# ═══════════════════════════════════════════════════════════


class BaseAIService(
    AIStreamingMixin,
    AIDiagnosticsMixin,
    AIPromptsMixin,
    metaclass=ServiceMeta,
):
    """
    Service IA de base avec fonctionnalités communes

    Fonctionnalités AUTO :
    - ✅ Rate limiting avec retry intelligent
    - ✅ Cache sémantique automatique
    - ✅ Circuit breaker (protection service externe)
    - ✅ Parsing JSON robuste
    - ✅ Gestion d'erreurs unifiée
    - ✅ Logging avec métriques
    - ✅ API duale async/sync (auto-générée via ServiceMeta)

    Toutes les méthodes async ont une version _sync auto-générée:
        - call_with_cache() → call_with_cache_sync()
        - call_with_parsing() → call_with_parsing_sync()
        - call_with_list_parsing() → call_with_list_parsing_sync()
        - safe_call_with_cache() → safe_call_with_cache_sync()
        etc.
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

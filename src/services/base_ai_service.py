"""
Service IA de Base Centralisé
Élimine 60% de duplication entre services IA

Architecture:
- Hérite de AIClient pour les appels API
- Intègre AIParser pour parsing automatique
- Cache et Rate Limiting intégrés
- Prompts templates réutilisables
"""
import logging
from typing import Dict, List, Optional, TypeVar, Type, Any
from pydantic import BaseModel
from datetime import datetime

from src.core.ai import AIClient, AIParser, parse_list_response
from src.core.cache import Cache, RateLimit
from src.core.errors import handle_errors, AIServiceError, RateLimitError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class BaseAIService:
    """
    Service IA de base avec fonctionnalités communes

    Usage:
        class RecetteAIService(BaseAIService):
            def __init__(self, client: AIClient):
                super().__init__(client, cache_prefix="recettes_ai")
    """

    def __init__(
            self,
            client: AIClient,
            cache_prefix: str = "ai",
            default_ttl: int = 1800,
            default_temperature: float = 0.7
    ):
        """
        Args:
            client: Client IA
            cache_prefix: Préfixe pour les clés de cache
            default_ttl: TTL par défaut (30min)
            default_temperature: Température par défaut
        """
        self.client = client
        self.cache_prefix = cache_prefix
        self.default_ttl = default_ttl
        self.default_temperature = default_temperature

    # ═══════════════════════════════════════════════════════════
    # APPELS IA GÉNÉRIQUES
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    async def call_with_parsing(
            self,
            prompt: str,
            response_model: Type[T],
            system_prompt: str = "",
            temperature: Optional[float] = None,
            max_tokens: int = 1000,
            use_cache: bool = True,
            cache_ttl: Optional[int] = None,
            fallback: Optional[Dict] = None,
            strict: bool = False
    ) -> T:
        """
        Appel IA avec parsing automatique

        Args:
            prompt: Prompt utilisateur
            response_model: Modèle Pydantic de retour
            system_prompt: Instructions système
            temperature: Température (défaut: self.default_temperature)
            max_tokens: Tokens max
            use_cache: Utiliser cache
            cache_ttl: TTL cache (défaut: self.default_ttl)
            fallback: Données fallback si échec
            strict: Mode strict (raise si échec)

        Returns:
            Instance validée du modèle
        """
        # Vérifier rate limit
        can_call, error_msg = RateLimit.can_call()
        if not can_call:
            raise RateLimitError(error_msg, user_message=error_msg)

        # Température
        temp = temperature if temperature is not None else self.default_temperature

        # Clé cache
        cache_key = None
        if use_cache:
            cache_key = self._generate_cache_key(prompt, system_prompt, temp)
            cached = Cache.get(cache_key, ttl=cache_ttl or self.default_ttl)
            if cached:
                logger.debug(f"Cache HIT: {cache_key[:50]}")
                return response_model(**cached)

        # Appel IA
        logger.info(f"🤖 Appel IA: {response_model.__name__}")

        response = await self.client.call(
            prompt=prompt,
            system_prompt=system_prompt or self._default_system_prompt(),
            temperature=temp,
            max_tokens=max_tokens,
            use_cache=False  # On gère le cache nous-mêmes
        )

        # Parser
        result = AIParser.parse(
            response,
            response_model,
            fallback=fallback,
            strict=strict
        )

        # Cacher
        if use_cache and cache_key:
            Cache.set(cache_key, result.dict(), ttl=cache_ttl or self.default_ttl)

        logger.info(f"✅ Résultat parsé: {response_model.__name__}")
        return result

    @handle_errors(show_in_ui=True)
    async def call_with_list_parsing(
            self,
            prompt: str,
            item_model: Type[BaseModel],
            list_key: str = "items",
            system_prompt: str = "",
            temperature: Optional[float] = None,
            max_tokens: int = 2000,
            use_cache: bool = True,
            cache_ttl: Optional[int] = None,
            fallback_items: Optional[List[Dict]] = None,
            max_items: Optional[int] = None
    ) -> List[BaseModel]:
        """
        Appel IA retournant une liste

        Args:
            prompt: Prompt
            item_model: Modèle d'un item
            list_key: Clé JSON contenant la liste
            system_prompt: Instructions
            temperature: Température
            max_tokens: Tokens max
            use_cache: Cache
            cache_ttl: TTL cache
            fallback_items: Items fallback
            max_items: Nombre max d'items à retourner

        Returns:
            Liste d'items validés
        """
        # Vérifier rate limit
        can_call, error_msg = RateLimit.can_call()
        if not can_call:
            raise RateLimitError(error_msg, user_message=error_msg)

        # Température
        temp = temperature if temperature is not None else self.default_temperature

        # Clé cache
        cache_key = None
        if use_cache:
            cache_key = self._generate_cache_key(prompt, system_prompt, temp)
            cached = Cache.get(cache_key, ttl=cache_ttl or self.default_ttl)
            if cached:
                logger.debug(f"Cache HIT: {cache_key[:50]}")
                return [item_model(**item) for item in cached]

        # Appel IA
        logger.info(f"🤖 Appel IA liste: {item_model.__name__}")

        response = await self.client.call(
            prompt=prompt,
            system_prompt=system_prompt or self._default_system_prompt(),
            temperature=temp,
            max_tokens=max_tokens,
            use_cache=False
        )

        # Parser liste
        items = parse_list_response(
            response,
            item_model,
            list_key=list_key,
            fallback_items=fallback_items or []
        )

        # Limiter si demandé
        if max_items:
            items = items[:max_items]

        # Cacher
        if use_cache and cache_key:
            Cache.set(
                cache_key,
                [item.dict() for item in items],
                ttl=cache_ttl or self.default_ttl
            )

        logger.info(f"✅ {len(items)} items parsés")
        return items

    # ═══════════════════════════════════════════════════════════
    # HELPERS PROMPTS
    # ═══════════════════════════════════════════════════════════

    def build_json_prompt(
            self,
            context: str,
            task: str,
            json_schema: str,
            examples: Optional[str] = None,
            constraints: Optional[List[str]] = None
    ) -> str:
        """
        Construit un prompt structuré pour JSON

        Args:
            context: Contexte métier
            task: Tâche à accomplir
            json_schema: Schéma JSON attendu
            examples: Exemples (optionnel)
            constraints: Contraintes (optionnel)

        Returns:
            Prompt structuré
        """
        prompt = f"{context}\n\n"
        prompt += f"TÂCHE: {task}\n\n"

        if constraints:
            prompt += "CONTRAINTES:\n"
            for idx, constraint in enumerate(constraints, 1):
                prompt += f"{idx}. {constraint}\n"
            prompt += "\n"

        if examples:
            prompt += f"EXEMPLES:\n{examples}\n\n"

        prompt += f"FORMAT JSON:\n{json_schema}\n\n"
        prompt += "⚠️ UNIQUEMENT LE JSON, RIEN D'AUTRE !"

        return prompt

    def _default_system_prompt(self) -> str:
        """Prompt système par défaut"""
        return (
            "Tu es un assistant JSON expert. "
            "Tu génères UNIQUEMENT du JSON valide. "
            "RÈGLES: "
            "1. Commence directement par { "
            "2. Termine directement par } "
            "3. Utilise UNIQUEMENT des doubles guillemets "
            "4. Pas de markdown (```json) "
            "5. Pas de texte avant/après le JSON"
        )

    def _generate_cache_key(
            self,
            prompt: str,
            system_prompt: str,
            temperature: float
    ) -> str:
        """Génère clé de cache unique"""
        import hashlib
        import json

        data = {
            "prefix": self.cache_prefix,
            "prompt": prompt[:500],  # Limiter pour performance
            "system": system_prompt[:200],
            "temp": temperature
        }

        cache_str = json.dumps(data, sort_keys=True)
        cache_hash = hashlib.md5(cache_str.encode()).hexdigest()

        return f"{self.cache_prefix}_{cache_hash}"

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES À OVERRIDE (TEMPLATES)
    # ═══════════════════════════════════════════════════════════

    def get_fallback_data(self, request_type: str) -> Dict:
        """
        Retourne données de fallback

        À override dans les classes filles
        """
        return {}

    def validate_response(self, data: Dict) -> bool:
        """
        Validation métier custom

        À override dans les classes filles
        """
        return True

    # ═══════════════════════════════════════════════════════════
    # MÉTRIQUES & DEBUG
    # ═══════════════════════════════════════════════════════════

    def get_usage_stats(self) -> Dict:
        """Stats d'utilisation du service"""
        usage = RateLimit.get_usage()
        cache_stats = Cache.get_stats()

        return {
            "service": self.__class__.__name__,
            "cache_prefix": self.cache_prefix,
            "rate_limit": {
                "calls_today": usage["calls_today"],
                "remaining": usage["remaining_today"]
            },
            "cache": {
                "hit_rate": cache_stats["hit_rate"],
                "total_keys": cache_stats["total_keys"]
            }
        }

    def clear_cache(self):
        """Vide le cache du service"""
        Cache.invalidate(self.cache_prefix)
        logger.info(f"Cache vidé: {self.cache_prefix}")


# ═══════════════════════════════════════════════════════════
# MIXINS SPÉCIALISÉS
# ═══════════════════════════════════════════════════════════

class RecipeAIMixin:
    """Mixin pour services IA recettes"""

    def build_recipe_context(
            self,
            filters: Dict,
            ingredients: Optional[List[str]] = None,
            nb_recipes: int = 1
    ) -> str:
        """Construit contexte pour génération recettes"""
        context = f"Génère {nb_recipes} recette(s)"

        if filters.get("saison"):
            context += f" de saison {filters['saison']}"
        if filters.get("type_repas"):
            context += f" pour le {filters['type_repas']}"
        if filters.get("is_quick"):
            context += " rapides (<30min)"
        if ingredients:
            context += f" avec: {', '.join(ingredients[:5])}"

        return context


class PlanningAIMixin:
    """Mixin pour services IA planning"""

    def build_planning_context(
            self,
            config: Dict,
            semaine_debut: str
    ) -> str:
        """Construit contexte pour génération planning"""
        context = f"Planning semaine du {semaine_debut}\n"
        context += f"Foyer: {config.get('nb_adultes', 2)} adultes, "
        context += f"{config.get('nb_enfants', 0)} enfants\n"

        if config.get('a_bebe'):
            context += "👶 Mode bébé activé\n"

        if config.get('batch_cooking_actif'):
            context += "🍳 Batch cooking activé\n"

        return context


class InventoryAIMixin:
    """Mixin pour services IA inventaire"""

    def build_inventory_summary(self, inventaire: List[Dict]) -> str:
        """Construit résumé inventaire"""
        total = len(inventaire)

        # Compter par statut
        from collections import Counter
        statuts = Counter(i.get("statut", "ok") for i in inventaire)

        summary = f"Inventaire: {total} articles\n"
        summary += f"Stock bas: {statuts.get('sous_seuil', 0)}\n"
        summary += f"Péremption proche: {statuts.get('peremption_proche', 0)}\n"
        summary += f"Critiques: {statuts.get('critique', 0)}"

        return summary
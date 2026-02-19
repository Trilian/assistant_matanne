"""
Base AI Service - Service IA Générique avec Rate Limiting Auto
Version améliorée avec gestion automatique des quotas et retry
"""

import asyncio
import logging
from datetime import datetime

from pydantic import BaseModel, ValidationError

from src.core.ai import AnalyseurIA, ClientIA, RateLimitIA
from src.core.ai.cache import CacheIA
from src.core.errors import ErreurLimiteDebit, gerer_erreurs
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
    ):
        """
        Initialise le service IA

        Args:
            client: Client IA (ClientIA)
            cache_prefix: Préfixe pour clés cache
            default_ttl: TTL cache par défaut (secondes)
            default_temperature: Température par défaut
            service_name: Nom du service (pour analytics)
        """
        self.client = client
        self.cache_prefix = cache_prefix
        self.default_ttl = default_ttl
        self.default_temperature = default_temperature
        self.service_name = service_name

    # ═══════════════════════════════════════════════════════════
    # APPELS IA AVEC RATE LIMITING AUTO + CACHE
    # ═══════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=None)
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

        # Appel IA
        start_time = datetime.now()

        response = await self.client.appeler(
            prompt=prompt,
            prompt_systeme=system_prompt,
            temperature=temp,
            max_tokens=max_tokens,
            utiliser_cache=False,  # On gère le cache nous-mêmes
        )

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

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=None)
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

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
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

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=None)
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

        # Parser JSON vers modèle Pydantic
        try:
            import json

            # Nettoyer la réponse des markdown code blocks
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            # Parser JSON
            data = json.loads(cleaned)

            # Valider avec Pydantic
            result = response_model(**data)
            logger.info(f"✅ JSON parsé vers {response_model.__name__}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
            logger.debug(f"Réponse brute: {response[:500]}")
            return None
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


# ═══════════════════════════════════════════════════════════
# MIXINS SPÉCIALISÉS (INCHANGÉS mais maintenant UTILISÉS !)
# ═══════════════════════════════════════════════════════════


class RecipeAIMixin:
    """Mixin pour fonctionnalités IA recettes"""

    def build_recipe_context(
        self, filters: dict, ingredients_dispo: list[str] | None = None, nb_recettes: int = 3
    ) -> str:
        """Construit contexte pour génération recettes"""
        context = f"Génère {nb_recettes} recettes avec les critères suivants:\n\n"

        if filters.get("saison"):
            context += f"- Saison: {filters['saison']}\n"
        if filters.get("type_repas"):
            context += f"- Type de repas: {filters['type_repas']}\n"
        if filters.get("difficulte"):
            context += f"- Difficulté max: {filters['difficulte']}\n"
        if filters.get("is_quick"):
            context += "- Temps max: 30 minutes\n"

        if ingredients_dispo:
            context += "\nINGRÉDIENTS DISPONIBLES:\n"
            for ing in ingredients_dispo[:10]:
                context += f"- {ing}\n"
            context += "\nPrivilégier ces ingrédients si possible.\n"

        return context


class PlanningAIMixin:
    """Mixin pour fonctionnalités IA planning"""

    def build_planning_context(self, config: dict, semaine_debut: str) -> str:
        """Construit contexte pour génération planning"""
        context = f"Génère un planning hebdomadaire pour la semaine du {semaine_debut}.\n\n"

        context += "CONFIGURATION FOYER:\n"
        context += f"- {config.get('nb_adultes', 2)} adultes\n"
        context += f"- {config.get('nb_enfants', 0)} enfants\n"

        if config.get("a_bebe"):
            context += "- Présence d'un jeune enfant (adapter certaines recettes pour texture/allergènes)\n"

        if config.get("batch_cooking_actif"):
            context += "- Batch cooking activé (optimiser temps)\n"

        return context


class InventoryAIMixin:
    """Mixin pour fonctionnalités IA inventaire"""

    def build_inventory_summary(self, inventaire: list[dict]) -> str:
        """Construit résumé inventaire pour IA"""
        from collections import defaultdict

        summary = f"INVENTAIRE ({len(inventaire)} articles):\n\n"

        # Grouper par catégorie
        categories = defaultdict(list)
        for article in inventaire:
            cat = article.get("categorie", "Autre")
            categories[cat].append(article)

        # Résumer par catégorie
        for cat, articles in categories.items():
            summary += f"{cat}:\n"
            for art in articles[:5]:  # Max 5 par catégorie
                statut = art.get("statut", "ok")
                icon = "🔴" if statut == "critique" else "⚠️" if statut == "sous_seuil" else "✅"
                summary += f"  {icon} {art['nom']}: {art['quantite']} {art['unite']}\n"

            if len(articles) > 5:
                summary += f"  ... et {len(articles) - 5} autres\n"
            summary += "\n"

        # Résumé statuts
        critiques = len([a for a in inventaire if a.get("statut") == "critique"])
        sous_seuil = len([a for a in inventaire if a.get("statut") == "sous_seuil"])

        summary += "STATUTS:\n"
        summary += f"- {critiques} articles critiques\n"
        summary += f"- {sous_seuil} articles sous le seuil\n"

        return summary


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def create_base_ai_service(
    cache_prefix: str = "ai",
    default_ttl: int = 3600,
    default_temperature: float = 0.7,
    service_name: str = "unknown",
) -> BaseAIService:
    """Factory pour créer un BaseAIService"""
    from src.core.ai import obtenir_client_ia

    client = obtenir_client_ia()

    return BaseAIService(
        client=client,
        cache_prefix=cache_prefix,
        default_ttl=default_ttl,
        default_temperature=default_temperature,
        service_name=service_name,
    )

"""
Base AI Service - Service IA Générique avec Mixins
Fournit fonctionnalités communes pour tous les services IA
"""
import logging
from typing import Optional, Dict, List, Any, Type
from datetime import datetime
from pydantic import BaseModel, ValidationError

from src.core.ai import ClientIA, AnalyseurIA
from src.core.ai.cache import CacheIA
from src.core.errors import ErreurServiceIA, gerer_erreurs

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# BASE AI SERVICE
# ═══════════════════════════════════════════════════════════

class BaseAIService:
    """
    Service IA de base avec fonctionnalités communes

    Fonctionnalités:
    - Appels IA avec cache sémantique automatique
    - Parsing JSON robuste
    - Retry automatique
    - Rate limiting
    - Gestion d'erreurs
    - Helpers pour prompts structurés
    """

    def __init__(
            self,
            client: ClientIA,
            cache_prefix: str = "ai",
            default_ttl: int = 3600,
            default_temperature: float = 0.7
    ):
        """
        Initialise le service IA

        Args:
            client: Client IA (ClientIA)
            cache_prefix: Préfixe pour clés cache
            default_ttl: TTL cache par défaut (secondes)
            default_temperature: Température par défaut
        """
        self.client = client
        self.cache_prefix = cache_prefix
        self.default_ttl = default_ttl
        self.default_temperature = default_temperature

    # ═══════════════════════════════════════════════════════════
    # APPELS IA AVEC CACHE
    # ═══════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=None)
    async def call_with_cache(
            self,
            prompt: str,
            system_prompt: str = "",
            temperature: Optional[float] = None,
            max_tokens: int = 1000,
            use_cache: bool = True,
            category: Optional[str] = None
    ) -> Optional[str]:
        """
        Appel IA avec cache sémantique automatique

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            temperature: Température (None = default)
            max_tokens: Tokens max
            use_cache: Utiliser le cache
            category: Catégorie pour cache sémantique

        Returns:
            Réponse IA ou None si erreur
        """
        temp = temperature if temperature is not None else self.default_temperature
        cache_category = category or self.cache_prefix

        # Vérifier cache sémantique
        if use_cache:
            cached = CacheIA.obtenir(
                prompt=prompt,
                systeme=system_prompt,
                temperature=temp,
            )

            if cached:
                logger.info(f"✅ Cache HIT sémantique ({cache_category})")
                return cached

        # Appel IA
        response = await self.client.appeler(
            prompt=prompt,
            prompt_systeme=system_prompt,
            temperature=temp,
            max_tokens=max_tokens,
            utiliser_cache=False  # On gère le cache nous-mêmes
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
            response_model: Type[BaseModel],
            system_prompt: str = "",
            temperature: Optional[float] = None,
            max_tokens: int = 1000,
            use_cache: bool = True,
            fallback: Optional[Dict] = None
    ) -> Optional[BaseModel]:
        """
        Appel IA avec parsing automatique vers modèle Pydantic

        Args:
            prompt: Prompt
            response_model: Modèle Pydantic cible
            system_prompt: Instructions système
            temperature: Température
            max_tokens: Tokens max
            use_cache: Utiliser cache
            fallback: Dict fallback si parsing échoue

        Returns:
            Instance validée du modèle ou None
        """
        # Appel IA
        response = await self.call_with_cache(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache
        )

        if not response:
            return None

        # Parser avec AnalyseurIA
        try:
            parsed = AnalyseurIA.analyser(
                reponse=response,
                modele=response_model,
                valeur_secours=fallback,
                strict=False
            )

            logger.info(f"✅ Parsing réussi: {response_model.__name__}")
            return parsed

        except ValidationError as e:
            logger.error(f"❌ Erreur parsing {response_model.__name__}: {e}")

            if fallback:
                logger.warning("Utilisation fallback")
                return response_model(**fallback)

            return None

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
    async def call_with_list_parsing(
            self,
            prompt: str,
            item_model: Type[BaseModel],
            list_key: str = "items",
            system_prompt: str = "",
            temperature: Optional[float] = None,
            max_tokens: int = 2000,
            use_cache: bool = True,
            max_items: Optional[int] = None
    ) -> List[BaseModel]:
        """
        Appel IA avec parsing d'une liste

        Args:
            prompt: Prompt
            item_model: Modèle d'un item
            list_key: Clé JSON contenant la liste
            system_prompt: Instructions système
            temperature: Température
            max_tokens: Tokens max
            use_cache: Utiliser cache
            max_items: Nombre max d'items

        Returns:
            Liste d'items validés
        """
        # Appel IA
        response = await self.call_with_cache(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache
        )

        if not response:
            return []

        # Parser liste
        try:
            from src.core.ai.parser import analyser_liste_reponse

            items = analyser_liste_reponse(
                reponse=response,
                modele_item=item_model,
                cle_liste=list_key,
                items_secours=[]
            )

            # Limiter nombre d'items
            if max_items and len(items) > max_items:
                items = items[:max_items]
                logger.info(f"Liste limitée à {max_items} items")

            logger.info(f"✅ {len(items)} items parsés")
            return items

        except Exception as e:
            logger.error(f"❌ Erreur parsing liste: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # HELPERS PROMPTS STRUCTURÉS
    # ═══════════════════════════════════════════════════════════

    def build_json_prompt(
            self,
            context: str,
            task: str,
            json_schema: str,
            constraints: Optional[List[str]] = None
    ) -> str:
        """
        Construit un prompt structuré pour réponse JSON

        Args:
            context: Contexte métier
            task: Tâche à accomplir
            json_schema: Schéma JSON attendu
            constraints: Liste de contraintes

        Returns:
            Prompt formaté
        """
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
            self,
            role: str,
            expertise: List[str],
            rules: Optional[List[str]] = None
    ) -> str:
        """
        Construit un system prompt structuré

        Args:
            role: Rôle de l'IA (ex: "Nutritionniste expert")
            expertise: Domaines d'expertise
            rules: Règles à respecter

        Returns:
            System prompt formaté
        """
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

    def get_cache_stats(self) -> Dict:
        """Retourne statistiques cache"""
        return CacheIA.obtenir_statistiques()

    def clear_cache(self):
        """Vide le cache"""
        CacheIA.invalider_tout()
        logger.info(f"🗑️ Cache {self.cache_prefix} vidé")


# ═══════════════════════════════════════════════════════════
# MIXINS SPÉCIALISÉS
# ═══════════════════════════════════════════════════════════

class RecipeAIMixin:
    """Mixin pour fonctionnalités IA recettes"""

    def build_recipe_context(
            self,
            filters: Dict,
            ingredients_dispo: Optional[List[str]] = None,
            nb_recettes: int = 3
    ) -> str:
        """
        Construit contexte pour génération recettes

        Args:
            filters: Filtres (saison, type_repas, etc.)
            ingredients_dispo: Ingrédients disponibles
            nb_recettes: Nombre de recettes

        Returns:
            Contexte formaté
        """
        context = f"Génère {nb_recettes} recettes avec les critères suivants:\n\n"

        if filters.get("saison"):
            context += f"- Saison: {filters['saison']}\n"
        if filters.get("type_repas"):
            context += f"- Type de repas: {filters['type_repas']}\n"
        if filters.get("difficulte"):
            context += f"- Difficulté max: {filters['difficulte']}\n"
        if filters.get("is_quick"):
            context += f"- Temps max: 30 minutes\n"

        if ingredients_dispo:
            context += f"\nINGRÉDIENTS DISPONIBLES:\n"
            for ing in ingredients_dispo[:10]:
                context += f"- {ing}\n"
            context += "\nPrivilégier ces ingrédients si possible.\n"

        return context

    def build_recipe_adaptation_context(
            self,
            recette: Any,
            adaptation_type: str
    ) -> str:
        """
        Construit contexte pour adaptation recette

        Args:
            recette: Recette à adapter
            adaptation_type: Type d'adaptation (bébé, batch, etc.)

        Returns:
            Contexte formaté
        """
        context = f"RECETTE ORIGINALE: {recette.nom}\n\n"
        context += f"TYPE D'ADAPTATION: {adaptation_type}\n\n"

        context += "INGRÉDIENTS:\n"
        for ing in recette.ingredients:
            context += f"- {ing.quantite} {ing.unite} {ing.ingredient.nom}\n"

        context += "\nÉTAPES:\n"
        for etape in sorted(recette.etapes, key=lambda x: x.ordre):
            context += f"{etape.ordre}. {etape.description}\n"

        return context


class PlanningAIMixin:
    """Mixin pour fonctionnalités IA planning"""

    def build_planning_context(
            self,
            config: Dict,
            semaine_debut: str
    ) -> str:
        """
        Construit contexte pour génération planning

        Args:
            config: Configuration foyer
            semaine_debut: Date début semaine

        Returns:
            Contexte formaté
        """
        context = f"Génère un planning hebdomadaire pour la semaine du {semaine_debut}.\n\n"

        context += "CONFIGURATION FOYER:\n"
        context += f"- {config.get('nb_adultes', 2)} adultes\n"
        context += f"- {config.get('nb_enfants', 0)} enfants\n"

        if config.get('a_bebe'):
            context += "- Présence d'un bébé (adapter certaines recettes)\n"

        if config.get('batch_cooking_actif'):
            context += "- Batch cooking activé (optimiser temps)\n"

        return context


class InventoryAIMixin:
    """Mixin pour fonctionnalités IA inventaire"""

    def build_inventory_summary(
            self,
            inventaire: List[Dict]
    ) -> str:
        """
        Construit résumé inventaire pour IA

        Args:
            inventaire: Liste articles inventaire

        Returns:
            Résumé formaté
        """
        summary = f"INVENTAIRE ({len(inventaire)} articles):\n\n"

        # Grouper par catégorie
        from collections import defaultdict
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

        summary += f"STATUTS:\n"
        summary += f"- {critiques} articles critiques\n"
        summary += f"- {sous_seuil} articles sous le seuil\n"

        return summary


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

def create_base_ai_service(
        cache_prefix: str = "ai",
        default_ttl: int = 3600,
        default_temperature: float = 0.7
) -> BaseAIService:
    """
    Factory pour créer un BaseAIService

    Args:
        cache_prefix: Préfixe cache
        default_ttl: TTL par défaut
        default_temperature: Température par défaut

    Returns:
        Instance BaseAIService
    """
    from src.core.ai import obtenir_client_ia

    client = obtenir_client_ia()

    return BaseAIService(
        client=client,
        cache_prefix=cache_prefix,
        default_ttl=default_ttl,
        default_temperature=default_temperature
    )
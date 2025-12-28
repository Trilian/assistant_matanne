"""
Cache IA Spécifique
Cache optimisé pour les réponses IA
"""
import hashlib
import json
from typing import Optional
from ..cache import Cache


class AICache:
    """
    Cache spécialisé pour réponses IA

    Wrapper autour du Cache principal avec
    génération de clés optimisée pour l'IA
    """

    @staticmethod
    def generate_key(
            prompt: str,
            system: str = "",
            temperature: float = 0.7,
            model: str = ""
    ) -> str:
        """
        Génère une clé de cache unique pour un appel IA

        Args:
            prompt: Prompt utilisateur
            system: Prompt système
            temperature: Température
            model: Modèle utilisé

        Returns:
            Clé de cache unique
        """
        # Combiner tous les paramètres
        cache_data = {
            "prompt": prompt.strip(),
            "system": system.strip(),
            "temperature": temperature,
            "model": model
        }

        # Hash MD5 du JSON trié
        cache_str = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_str.encode()).hexdigest()

        return f"ai_call_{cache_hash}"

    @staticmethod
    def get(key: str, ttl: int = 1800) -> Optional[str]:
        """
        Récupère une réponse IA du cache

        Args:
            key: Clé cache
            ttl: Time to live (défaut: 30 min)

        Returns:
            Réponse IA ou None
        """
        return Cache.get(key, ttl)

    @staticmethod
    def set(key: str, value: str, ttl: int = 1800):
        """
        Sauvegarde une réponse IA en cache

        Args:
            key: Clé cache
            value: Réponse IA
            ttl: Time to live (défaut: 30 min)
        """
        Cache.set(key, value, ttl)

    @staticmethod
    def clear_ai_cache():
        """Vide uniquement le cache IA"""
        Cache.invalidate("ai_call_")
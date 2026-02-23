"""
Stockage Redis pour la limitation de débit.

Remplace le stockage en mémoire pour la production.
Utilise des clés Redis avec TTL pour le nettoyage automatique.

Configuration:
    Variable d'environnement REDIS_URL (ex: redis://localhost:6379/0)
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)


class StockageRedis:
    """Stockage Redis pour la limitation de débit.

    Compatible avec l'interface de ``StockageLimitationDebit`` (in-memory).
    Utilise des sorted sets Redis pour un sliding window précis.
    """

    def __init__(self, redis_url: str | None = None):
        self._redis_url = redis_url or os.getenv("REDIS_URL", "")
        self._client: Any | None = None
        self._prefix = "ratelimit:"

    @property
    def client(self) -> Any:
        """Connexion Redis lazy (créée au premier accès)."""
        if self._client is None:
            try:
                import redis

                self._client = redis.from_url(
                    self._redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=1,
                    retry_on_timeout=True,
                )
                # Test de connexion
                self._client.ping()
                logger.info("Connexion Redis établie pour rate limiting")
            except Exception as e:
                logger.error(f"Connexion Redis échouée: {e}")
                raise
        return self._client

    def _cle(self, cle: str) -> str:
        """Préfixe la clé avec le namespace rate limiting."""
        return f"{self._prefix}{cle}"

    def incrementer(self, cle: str, fenetre_secondes: int) -> int:
        """
        Incrémente le compteur via sorted set Redis (sliding window).

        Chaque requête est un membre du sorted set avec timestamp comme score.
        Les membres expirés sont supprimés automatiquement.

        Args:
            cle: Clé unique (IP, user_id, etc.)
            fenetre_secondes: Taille de la fenêtre en secondes

        Returns:
            Nombre de requêtes dans la fenêtre
        """
        redis_cle = self._cle(cle)
        maintenant = time.time()
        seuil = maintenant - fenetre_secondes

        pipe = self.client.pipeline()
        # Supprimer les entrées expirées
        pipe.zremrangebyscore(redis_cle, "-inf", seuil)
        # Ajouter la nouvelle requête (membre unique = timestamp précis)
        pipe.zadd(redis_cle, {f"{maintenant}:{id(pipe)}": maintenant})
        # Compter les entrées dans la fenêtre
        pipe.zcard(redis_cle)
        # TTL auto-cleanup
        pipe.expire(redis_cle, fenetre_secondes + 60)
        resultats = pipe.execute()

        return resultats[2]  # zcard result

    def obtenir_compte(self, cle: str, fenetre_secondes: int) -> int:
        """Retourne le nombre de requêtes dans la fenêtre."""
        redis_cle = self._cle(cle)
        maintenant = time.time()
        seuil = maintenant - fenetre_secondes

        # Nettoyer et compter en pipeline
        pipe = self.client.pipeline()
        pipe.zremrangebyscore(redis_cle, "-inf", seuil)
        pipe.zcard(redis_cle)
        resultats = pipe.execute()

        return resultats[1]

    def obtenir_restant(self, cle: str, fenetre_secondes: int, limite: int) -> int:
        """Retourne le nombre de requêtes restantes."""
        compte = self.obtenir_compte(cle, fenetre_secondes)
        return max(0, limite - compte)

    def obtenir_temps_reset(self, cle: str, fenetre_secondes: int) -> int:
        """Retourne le temps avant reset de la fenêtre (en secondes)."""
        redis_cle = self._cle(cle)

        # Obtenir le score le plus ancien
        plus_anciens = self.client.zrange(redis_cle, 0, 0, withscores=True)
        if not plus_anciens:
            return 0

        plus_ancien_ts = plus_anciens[0][1]
        reset_a = plus_ancien_ts + fenetre_secondes
        restant = int(reset_a - time.time())
        return max(0, restant)

    def est_bloque(self, cle: str) -> bool:
        """Vérifie si une clé est temporairement bloquée."""
        cle_blocage = self._cle(f"blocked:{cle}")
        return self.client.exists(cle_blocage) > 0

    def bloquer(self, cle: str, duree_secondes: int):
        """Bloque temporairement une clé via TTL Redis."""
        cle_blocage = self._cle(f"blocked:{cle}")
        self.client.setex(cle_blocage, duree_secondes, "1")


def obtenir_stockage_optimal():
    """
    Factory qui retourne le meilleur stockage disponible.

    Retourne ``StockageRedis`` si REDIS_URL est configuré,
    sinon fallback sur ``StockageLimitationDebit`` (in-memory).

    Returns:
        Instance de stockage (Redis ou in-memory)
    """
    redis_url = os.getenv("REDIS_URL", "")

    if redis_url:
        try:
            stockage = StockageRedis(redis_url)
            _ = (
                stockage.client
            )  # Test connexion (trigger la connexion) - évite l'expression inutile
            logger.info("Rate limiting: stockage Redis activé")
            return stockage
        except Exception as e:
            logger.warning(f"Rate limiting: fallback in-memory (Redis indisponible: {e})")

    from .storage import StockageLimitationDebit

    logger.info("Rate limiting: stockage in-memory (REDIS_URL non configuré)")
    return StockageLimitationDebit()

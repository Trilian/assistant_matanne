"""
Stockage des compteurs de limitation de débit.

Implémentation en mémoire (pour développement).
Pour la production, utiliser Redis.
"""

import time
from collections import defaultdict


class StockageLimitationDebit:
    """Stockage des compteurs de limitation de débit."""

    def __init__(self):
        self._store: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._lock_store: dict[str, float] = {}

    def _nettoyer_anciennes_entrees(self, cle: str, fenetre_secondes: int):
        """Nettoie les entrées expirées."""
        maintenant = time.time()
        seuil = maintenant - fenetre_secondes
        self._store[cle] = [(ts, compte) for ts, compte in self._store[cle] if ts > seuil]

    def incrementer(self, cle: str, fenetre_secondes: int) -> int:
        """
        Incrémente le compteur et retourne le total dans la fenêtre.

        Args:
            cle: Clé unique (IP, user_id, etc.)
            fenetre_secondes: Taille de la fenêtre en secondes

        Returns:
            Nombre de requêtes dans la fenêtre
        """
        maintenant = time.time()
        self._nettoyer_anciennes_entrees(cle, fenetre_secondes)
        self._store[cle].append((maintenant, 1))
        return sum(compte for _, compte in self._store[cle])

    def obtenir_compte(self, cle: str, fenetre_secondes: int) -> int:
        """Retourne le nombre de requêtes dans la fenêtre."""
        self._nettoyer_anciennes_entrees(cle, fenetre_secondes)
        return sum(compte for _, compte in self._store[cle])

    def obtenir_restant(self, cle: str, fenetre_secondes: int, limite: int) -> int:
        """Retourne le nombre de requêtes restantes."""
        compte = self.obtenir_compte(cle, fenetre_secondes)
        return max(0, limite - compte)

    def obtenir_temps_reset(self, cle: str, fenetre_secondes: int) -> int:
        """Retourne le temps avant reset de la fenêtre (en secondes)."""
        if not self._store[cle]:
            return 0
        plus_ancien = min(ts for ts, _ in self._store[cle])
        reset_a = plus_ancien + fenetre_secondes
        restant = int(reset_a - time.time())
        return max(0, restant)

    def est_bloque(self, cle: str) -> bool:
        """Vérifie si une clé est temporairement bloquée."""
        if cle not in self._lock_store:
            return False
        bloque_jusqua = self._lock_store[cle]
        if time.time() > bloque_jusqua:
            del self._lock_store[cle]
            return False
        return True

    def bloquer(self, cle: str, duree_secondes: int):
        """Bloque temporairement une clé."""
        self._lock_store[cle] = time.time() + duree_secondes

    # Alias anglais
    def increment(self, key: str, window_seconds: int) -> int:
        return self.incrementer(key, window_seconds)

    def get_count(self, key: str, window_seconds: int) -> int:
        return self.obtenir_compte(key, window_seconds)

    def get_remaining(self, key: str, window_seconds: int, limit: int) -> int:
        return self.obtenir_restant(key, window_seconds, limit)

    def get_reset_time(self, key: str, window_seconds: int) -> int:
        return self.obtenir_temps_reset(key, window_seconds)

    def is_blocked(self, key: str) -> bool:
        return self.est_bloque(key)

    def block(self, key: str, duration_seconds: int):
        return self.bloquer(key, duration_seconds)


# Alias rétrocompatibilité
RateLimitStore = StockageLimitationDebit

# Instance globale
_stockage = StockageLimitationDebit()
_store = _stockage

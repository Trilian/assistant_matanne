"""
Stockage des compteurs de limitation de débit.

Implémentation en mémoire (pour développement).
Pour la production, utiliser Redis.

ATTENTION (A11): Ce stockage in-memory fonctionne correctement uniquement en mode
single-worker. Avec Uvicorn multi-workers (--workers N), chaque worker possède son
propre compteur en mémoire, ce qui rend les limites N fois plus permissives.
Pour une limitation de débit fiable en multi-workers, configurer REDIS_URL dans
l'environnement afin d'utiliser StockageRedis (redis_storage.py).

Thread-safety: les opérations sont protégées par un ``threading.Lock``
pour gérer les accès concurrents au sein d'un même worker (threads).
"""

import threading
import time
from collections import defaultdict


class StockageLimitationDebit:
    """Stockage thread-safe des compteurs de limitation de débit.

    Chaque opération de lecture/écriture est protégée par un verrou
    global (``threading.Lock``) afin d'éviter les race conditions
    lorsque plusieurs threads/workers accèdent au même processus.

    Phase A5: Éviction LRU pour borner la consommation mémoire.
    Quand le nombre de clés dépasse ``max_cles``, les clés les plus
    anciennes (sans entrées récentes) sont supprimées.
    """

    # Seuil maximal de clés en mémoire (Phase A5)
    MAX_CLES_DEFAUT = 50_000

    def __init__(self, max_cles: int = MAX_CLES_DEFAUT):
        self._store: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._lock_store: dict[str, float] = {}
        self._lock = threading.Lock()
        self._max_cles = max_cles

    def _nettoyer_anciennes_entrees(self, cle: str, fenetre_secondes: int):
        """Nettoie les entrées expirées. Doit être appelé sous ``_lock``."""
        maintenant = time.time()
        seuil = maintenant - fenetre_secondes
        self._store[cle] = [(ts, compte) for ts, compte in self._store[cle] if ts > seuil]
        # Phase A5: Supprimer les clés vides pour éviter les fuites mémoire
        if not self._store[cle]:
            del self._store[cle]

    def _evicter_si_necessaire(self):
        """Évicte les clés les plus anciennes si le seuil est dépassé (Phase A5).

        Doit être appelé sous ``_lock``.
        """
        if len(self._store) <= self._max_cles:
            return

        # Trier les clés par timestamp le plus récent (les plus anciennes d'abord)
        cles_triees = sorted(
            self._store.keys(),
            key=lambda k: max((ts for ts, _ in self._store[k]), default=0),
        )

        # Supprimer les 20% les plus anciennes
        nb_a_supprimer = max(1, len(cles_triees) // 5)
        for cle in cles_triees[:nb_a_supprimer]:
            del self._store[cle]

    def incrementer(self, cle: str, fenetre_secondes: int) -> int:
        """
        Incrémente le compteur et retourne le total dans la fenêtre.

        Thread-safe: opération atomique protégée par verrou.

        Args:
            cle: Clé unique (IP, user_id, etc.)
            fenetre_secondes: Taille de la fenêtre en secondes

        Returns:
            Nombre de requêtes dans la fenêtre
        """
        with self._lock:
            maintenant = time.time()
            self._nettoyer_anciennes_entrees(cle, fenetre_secondes)
            self._store[cle].append((maintenant, 1))
            self._evicter_si_necessaire()
            return sum(compte for _, compte in self._store[cle])

    def obtenir_compte(self, cle: str, fenetre_secondes: int) -> int:
        """Retourne le nombre de requêtes dans la fenêtre."""
        with self._lock:
            self._nettoyer_anciennes_entrees(cle, fenetre_secondes)
            return sum(compte for _, compte in self._store[cle])

    def obtenir_restant(self, cle: str, fenetre_secondes: int, limite: int) -> int:
        """Retourne le nombre de requêtes restantes."""
        compte = self.obtenir_compte(cle, fenetre_secondes)
        return max(0, limite - compte)

    def obtenir_temps_reset(self, cle: str, fenetre_secondes: int) -> int:
        """Retourne le temps avant reset de la fenêtre (en secondes)."""
        with self._lock:
            if not self._store[cle]:
                return 0
            plus_ancien = min(ts for ts, _ in self._store[cle])
            reset_a = plus_ancien + fenetre_secondes
            restant = int(reset_a - time.time())
            return max(0, restant)

    def est_bloque(self, cle: str) -> bool:
        """Vérifie si une clé est temporairement bloquée."""
        with self._lock:
            if cle not in self._lock_store:
                return False
            bloque_jusqua = self._lock_store[cle]
            if time.time() > bloque_jusqua:
                del self._lock_store[cle]
                return False
            return True

    def bloquer(self, cle: str, duree_secondes: int):
        """Bloque temporairement une clé."""
        with self._lock:
            self._lock_store[cle] = time.time() + duree_secondes


# Instance globale
_stockage = StockageLimitationDebit()

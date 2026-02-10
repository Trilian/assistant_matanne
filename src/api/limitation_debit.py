"""
Module de Limitation de Débit pour l'API REST.

Implémente la limitation de débit avec:
- Limites par IP
- Limites par utilisateur authentifié
- Limites par endpoint
- Stockage en mémoire ou Redis

Noms français avec alias anglais pour compatibilité.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════


class StrategieLimitationDebit(str, Enum):
    """Stratégies de limitation de débit."""
    FENETRE_FIXE = "fixed_window"  # Fenêtre fixe (ex: 100 req/min)
    FENETRE_GLISSANTE = "sliding_window"  # Fenêtre glissante
    SEAU_A_JETONS = "token_bucket"  # Seau à jetons
    
    # Alias anglais
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


# Alias rétrocompatibilité
RateLimitStrategy = StrategieLimitationDebit


@dataclass
class ConfigLimitationDebit:
    """Configuration de la limitation de débit."""
    
    # Limites globales par défaut
    requetes_par_minute: int = 60
    requetes_par_heure: int = 1000
    requetes_par_jour: int = 10000
    
    # Limites par type d'utilisateur
    requetes_anonyme_par_minute: int = 20
    requetes_authentifie_par_minute: int = 60
    requetes_premium_par_minute: int = 200
    
    # Limites spécifiques aux endpoints IA
    requetes_ia_par_minute: int = 10
    requetes_ia_par_heure: int = 100
    requetes_ia_par_jour: int = 500
    
    # Configuration
    strategie: StrategieLimitationDebit = StrategieLimitationDebit.FENETRE_GLISSANTE
    activer_headers: bool = True
    
    # Endpoints exemptés
    chemins_exemptes: list[str] = field(default_factory=lambda: [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ])
    
    # Alias anglais (propriétés)
    @property
    def requests_per_minute(self) -> int:
        return self.requetes_par_minute
    
    @property
    def requests_per_hour(self) -> int:
        return self.requetes_par_heure
    
    @property
    def requests_per_day(self) -> int:
        return self.requetes_par_jour
    
    @property
    def anonymous_requests_per_minute(self) -> int:
        return self.requetes_anonyme_par_minute
    
    @property
    def authenticated_requests_per_minute(self) -> int:
        return self.requetes_authentifie_par_minute
    
    @property
    def premium_requests_per_minute(self) -> int:
        return self.requetes_premium_par_minute
    
    @property
    def ai_requests_per_minute(self) -> int:
        return self.requetes_ia_par_minute
    
    @property
    def ai_requests_per_hour(self) -> int:
        return self.requetes_ia_par_heure
    
    @property
    def ai_requests_per_day(self) -> int:
        return self.requetes_ia_par_jour
    
    @property
    def strategy(self) -> StrategieLimitationDebit:
        return self.strategie
    
    @property
    def enable_headers(self) -> bool:
        return self.activer_headers
    
    @property
    def exempt_paths(self) -> list[str]:
        return self.chemins_exemptes


# Alias rétrocompatibilité
RateLimitConfig = ConfigLimitationDebit

# Configuration globale
config_limitation_debit = ConfigLimitationDebit()
rate_limit_config = config_limitation_debit  # Alias


# ═══════════════════════════════════════════════════════════
# STOCKAGE DES COMPTEURS
# ═══════════════════════════════════════════════════════════


class StockageLimitationDebit:
    """
    Stockage des compteurs de limitation de débit.
    
    Implémentation en mémoire (pour développement).
    Pour la production, utiliser Redis.
    """
    
    def __init__(self):
        self._store: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._lock_store: dict[str, float] = {}
    
    def _nettoyer_anciennes_entrees(self, cle: str, fenetre_secondes: int):
        """Nettoie les entrées expirées."""
        maintenant = time.time()
        seuil = maintenant - fenetre_secondes
        
        self._store[cle] = [
            (ts, compte) for ts, compte in self._store[cle]
            if ts > seuil
        ]
    
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
_store = _stockage  # Alias


# ═══════════════════════════════════════════════════════════
# LIMITEUR DE DÉBIT
# ═══════════════════════════════════════════════════════════


class LimiteurDebit:
    """
    Limiteur de débit principal.
    
    Supporte plusieurs fenêtres de temps simultanées.
    """
    
    def __init__(
        self,
        stockage: StockageLimitationDebit | None = None,
        config: ConfigLimitationDebit | None = None,
    ):
        self.stockage = stockage or _stockage
        self.config = config or config_limitation_debit
        # Alias
        self.store = self.stockage
    
    def _generer_cle(
        self,
        request: Request,
        identifiant: str | None = None,
        endpoint: str | None = None,
    ) -> str:
        """Génère une clé unique pour la limitation de débit."""
        parties = []
        
        if identifiant:
            parties.append(f"user:{identifiant}")
        else:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0].strip()
            else:
                ip = request.client.host if request.client else "unknown"
            parties.append(f"ip:{ip}")
        
        if endpoint:
            parties.append(f"endpoint:{endpoint}")
        
        return ":".join(parties)
    
    def verifier_limite(
        self,
        request: Request,
        id_utilisateur: str | None = None,
        est_premium: bool = False,
        est_endpoint_ia: bool = False,
    ) -> dict[str, Any]:
        """
        Vérifie la limite de débit et retourne les informations.
        
        Args:
            request: Requête FastAPI
            id_utilisateur: ID utilisateur (si authentifié)
            est_premium: Utilisateur premium
            est_endpoint_ia: Endpoint utilisant l'IA
            
        Returns:
            Dict avec: allowed, limit, remaining, reset, retry_after
            
        Raises:
            HTTPException: Si limite dépassée
        """
        if request.url.path in self.config.chemins_exemptes:
            return {"allowed": True, "limit": -1, "remaining": -1}
        
        cle = self._generer_cle(request, id_utilisateur)
        
        if self.stockage.est_bloque(cle):
            raise HTTPException(
                status_code=429,
                detail="Trop de requêtes. Réessayez plus tard.",
                headers={"Retry-After": "60"}
            )
        
        # Déterminer les limites
        if est_endpoint_ia:
            limite_minute = self.config.requetes_ia_par_minute
            limite_heure = self.config.requetes_ia_par_heure
            limite_jour = self.config.requetes_ia_par_jour
        elif est_premium:
            limite_minute = self.config.requetes_premium_par_minute
            limite_heure = self.config.requetes_par_heure * 2
            limite_jour = self.config.requetes_par_jour * 2
        elif id_utilisateur:
            limite_minute = self.config.requetes_authentifie_par_minute
            limite_heure = self.config.requetes_par_heure
            limite_jour = self.config.requetes_par_jour
        else:
            limite_minute = self.config.requetes_anonyme_par_minute
            limite_heure = self.config.requetes_par_heure // 2
            limite_jour = self.config.requetes_par_jour // 2
        
        fenetres = [
            ("minute", 60, limite_minute),
            ("hour", 3600, limite_heure),
            ("day", 86400, limite_jour),
        ]
        
        plus_restrictif = None
        
        for nom_fenetre, fenetre_secondes, limite in fenetres:
            cle_fenetre = f"{cle}:{nom_fenetre}"
            compte = self.stockage.incrementer(cle_fenetre, fenetre_secondes)
            
            if compte > limite:
                restant = 0
                reset = self.stockage.obtenir_temps_reset(cle_fenetre, fenetre_secondes)
                
                if compte > limite * 2:
                    self.stockage.bloquer(cle, 300)
                    logger.warning(f"Abus détecté: {cle}")
                
                raise HTTPException(
                    status_code=429,
                    detail=f"Limite de requêtes dépassée ({nom_fenetre}). Réessayez dans {reset}s.",
                    headers={
                        "X-RateLimit-Limit": str(limite),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset),
                        "Retry-After": str(reset),
                    }
                )
            
            restant = limite - compte
            reset = self.stockage.obtenir_temps_reset(cle_fenetre, fenetre_secondes)
            
            if plus_restrictif is None or restant < plus_restrictif["remaining"]:
                plus_restrictif = {
                    "allowed": True,
                    "limit": limite,
                    "remaining": restant,
                    "reset": reset,
                    "window": nom_fenetre,
                }
        
        return plus_restrictif or {"allowed": True}
    
    def ajouter_headers(self, response: Response, info_limite: dict[str, Any]):
        """Ajoute les headers de limitation de débit à la réponse."""
        if not self.config.activer_headers:
            return
        
        if info_limite.get("limit", -1) >= 0:
            response.headers["X-RateLimit-Limit"] = str(info_limite.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(info_limite.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(info_limite.get("reset", 0))
    
    # Alias anglais
    def check_rate_limit(
        self,
        request: Request,
        user_id: str | None = None,
        is_premium: bool = False,
        is_ai_endpoint: bool = False,
    ) -> dict[str, Any]:
        return self.verifier_limite(request, user_id, is_premium, is_ai_endpoint)
    
    def add_headers(self, response: Response, rate_info: dict[str, Any]):
        return self.ajouter_headers(response, rate_info)
    
    def _get_key(self, request: Request, identifier: str | None = None, endpoint: str | None = None) -> str:
        return self._generer_cle(request, identifier, endpoint)


# Alias rétrocompatibilité
RateLimiter = LimiteurDebit

# Instance globale
limiteur_debit = LimiteurDebit()
rate_limiter = limiteur_debit  # Alias


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE FASTAPI
# ═══════════════════════════════════════════════════════════


class MiddlewareLimitationDebit(BaseHTTPMiddleware):
    """
    Middleware FastAPI pour la limitation de débit automatique.
    
    Usage:
        app.add_middleware(MiddlewareLimitationDebit)
    
    Note:
        Désactiver avec RATE_LIMITING_DISABLED=true (pour tests)
    """
    
    def __init__(self, app, limiteur: LimiteurDebit | None = None):
        super().__init__(app)
        self.limiteur = limiteur or limiteur_debit
        self.limiter = self.limiteur  # Alias
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Intercepte les requêtes et applique la limitation de débit."""
        import os
        
        # Bypass si désactivé (pour les tests)
        if os.environ.get("RATE_LIMITING_DISABLED", "").lower() == "true":
            return await call_next(request)
        
        id_utilisateur = None
        auth_header = request.headers.get("Authorization", "")
        
        if auth_header.startswith("Bearer "):
            try:
                import jwt
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                id_utilisateur = payload.get("sub")
            except Exception:
                pass
        
        est_ia = "/ai/" in request.url.path or "/suggest" in request.url.path
        
        info_limite = self.limiteur.verifier_limite(
            request,
            id_utilisateur=id_utilisateur,
            est_endpoint_ia=est_ia,
        )
        
        response = await call_next(request)
        self.limiteur.ajouter_headers(response, info_limite)
        
        return response


# Alias rétrocompatibilité
RateLimitMiddleware = MiddlewareLimitationDebit


# ═══════════════════════════════════════════════════════════
# DÉCORATEURS
# ═══════════════════════════════════════════════════════════


def limite_debit(
    requetes_par_minute: int | None = None,
    requetes_par_heure: int | None = None,
    fonction_cle: Callable[[Request], str] | None = None,
):
    """
    Décorateur pour appliquer une limite de débit spécifique à un endpoint.
    
    Usage:
        @app.get("/operation-couteuse")
        @limite_debit(requetes_par_minute=5)
        async def operation_couteuse(request: Request):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request is None:
                request = kwargs.get("request")
            
            if request is None:
                return await func(*args, **kwargs)
            
            if fonction_cle:
                cle = fonction_cle(request)
            else:
                forwarded = request.headers.get("X-Forwarded-For")
                if forwarded:
                    ip = forwarded.split(",")[0].strip()
                else:
                    ip = request.client.host if request.client else "unknown"
                cle = f"ip:{ip}:endpoint:{request.url.path}"
            
            if requetes_par_minute:
                compte = _stockage.incrementer(f"{cle}:minute", 60)
                if compte > requetes_par_minute:
                    reset = _stockage.obtenir_temps_reset(f"{cle}:minute", 60)
                    raise HTTPException(
                        status_code=429,
                        detail=f"Limite dépassée. Réessayez dans {reset}s.",
                        headers={"Retry-After": str(reset)}
                    )
            
            if requetes_par_heure:
                compte = _stockage.incrementer(f"{cle}:hour", 3600)
                if compte > requetes_par_heure:
                    reset = _stockage.obtenir_temps_reset(f"{cle}:hour", 3600)
                    raise HTTPException(
                        status_code=429,
                        detail=f"Limite horaire dépassée. Réessayez dans {reset}s.",
                        headers={"Retry-After": str(reset)}
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Alias anglais avec mêmes paramètres
def rate_limit(
    requests_per_minute: int | None = None,
    requests_per_hour: int | None = None,
    key_func: Callable[[Request], str] | None = None,
):
    """Alias anglais de limite_debit."""
    return limite_debit(
        requetes_par_minute=requests_per_minute,
        requetes_par_heure=requests_per_hour,
        fonction_cle=key_func,
    )


# ═══════════════════════════════════════════════════════════
# DÉPENDANCES FASTAPI
# ═══════════════════════════════════════════════════════════


async def verifier_limite_debit(
    request: Request,
    est_ia: bool = False,
) -> dict[str, Any]:
    """
    Dépendance FastAPI pour vérifier la limite de débit.
    """
    return limiteur_debit.verifier_limite(request, est_endpoint_ia=est_ia)


async def verifier_limite_debit_ia(request: Request) -> dict[str, Any]:
    """Dépendance pour les endpoints IA."""
    return await verifier_limite_debit(request, est_ia=True)


# Alias anglais
async def check_rate_limit(request: Request, is_ai: bool = False) -> dict[str, Any]:
    return await verifier_limite_debit(request, est_ia=is_ai)


async def check_ai_rate_limit(request: Request) -> dict[str, Any]:
    return await verifier_limite_debit_ia(request)


# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════


def obtenir_stats_limitation() -> dict[str, Any]:
    """Retourne les statistiques de limitation de débit."""
    return {
        "cles_actives": len(_stockage._store),
        "cles_bloquees": len(_stockage._lock_store),
        "configuration": {
            "requetes_par_minute": config_limitation_debit.requetes_par_minute,
            "requetes_par_heure": config_limitation_debit.requetes_par_heure,
            "requetes_ia_par_minute": config_limitation_debit.requetes_ia_par_minute,
        }
    }


def reinitialiser_limites():
    """Réinitialise tous les compteurs (pour les tests)."""
    global _stockage, _store
    _stockage = StockageLimitationDebit()
    _store = _stockage


def configurer_limites(config: ConfigLimitationDebit):
    """Configure les limites globales."""
    global config_limitation_debit, rate_limit_config, limiteur_debit, rate_limiter
    config_limitation_debit = config
    rate_limit_config = config
    limiteur_debit = LimiteurDebit(config=config)
    rate_limiter = limiteur_debit


# Alias anglais
def get_rate_limit_stats() -> dict[str, Any]:
    return obtenir_stats_limitation()


def reset_rate_limits():
    return reinitialiser_limites()


def configure_rate_limits(config: ConfigLimitationDebit):
    return configurer_limites(config)

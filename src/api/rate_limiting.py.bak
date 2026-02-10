"""
Module de Rate Limiting pour l'API REST.

Implémente la limitation de débit avec:
- Limites par IP
- Limites par utilisateur authentifié
- Limites par endpoint
- Stockage en mémoire ou Redis
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


class RateLimitStrategy(str, Enum):
    """Stratégies de rate limiting."""
    FIXED_WINDOW = "fixed_window"  # Fenêtre fixe (ex: 100 req/min)
    SLIDING_WINDOW = "sliding_window"  # Fenêtre glissante
    TOKEN_BUCKET = "token_bucket"  # Seau à jetons


@dataclass
class RateLimitConfig:
    """Configuration de rate limiting."""
    
    # Limites globales par défaut
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    
    # Limites par type d'utilisateur
    anonymous_requests_per_minute: int = 20
    authenticated_requests_per_minute: int = 60
    premium_requests_per_minute: int = 200
    
    # Limites spécifiques aux endpoints IA
    ai_requests_per_minute: int = 10
    ai_requests_per_hour: int = 100
    ai_requests_per_day: int = 500
    
    # Configuration
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    enable_headers: bool = True  # Ajouter X-RateLimit-* headers
    
    # Endpoints exemptés
    exempt_paths: list[str] = field(default_factory=lambda: [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ])


# Configuration globale
rate_limit_config = RateLimitConfig()


# ═══════════════════════════════════════════════════════════
# STOCKAGE DES COMPTEURS
# ═══════════════════════════════════════════════════════════


class RateLimitStore:
    """
    Stockage des compteurs de rate limiting.
    
    Implémentation en mémoire (pour développement).
    Pour la production, utiliser Redis.
    """
    
    def __init__(self):
        # Structure: {key: [(timestamp, count), ...]}
        self._store: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._lock_store: dict[str, float] = {}
    
    def _clean_old_entries(self, key: str, window_seconds: int):
        """Nettoie les entrées expirées."""
        now = time.time()
        cutoff = now - window_seconds
        
        self._store[key] = [
            (ts, count) for ts, count in self._store[key]
            if ts > cutoff
        ]
    
    def increment(self, key: str, window_seconds: int) -> int:
        """
        Incrémente le compteur et retourne le total dans la fenêtre.
        
        Args:
            key: Clé unique (IP, user_id, etc.)
            window_seconds: Taille de la fenêtre en secondes
            
        Returns:
            Nombre de requêtes dans la fenêtre
        """
        now = time.time()
        
        # Nettoyer les anciennes entrées
        self._clean_old_entries(key, window_seconds)
        
        # Ajouter la nouvelle requête
        self._store[key].append((now, 1))
        
        # Calculer le total
        return sum(count for _, count in self._store[key])
    
    def get_count(self, key: str, window_seconds: int) -> int:
        """Retourne le nombre de requêtes dans la fenêtre."""
        self._clean_old_entries(key, window_seconds)
        return sum(count for _, count in self._store[key])
    
    def get_remaining(self, key: str, window_seconds: int, limit: int) -> int:
        """Retourne le nombre de requêtes restantes."""
        count = self.get_count(key, window_seconds)
        return max(0, limit - count)
    
    def get_reset_time(self, key: str, window_seconds: int) -> int:
        """Retourne le temps avant reset de la fenêtre (en secondes)."""
        if not self._store[key]:
            return 0
        
        oldest = min(ts for ts, _ in self._store[key])
        reset_at = oldest + window_seconds
        remaining = int(reset_at - time.time())
        
        return max(0, remaining)
    
    def is_blocked(self, key: str) -> bool:
        """Vérifie si une clé est temporairement bloquée."""
        if key not in self._lock_store:
            return False
        
        blocked_until = self._lock_store[key]
        if time.time() > blocked_until:
            del self._lock_store[key]
            return False
        
        return True
    
    def block(self, key: str, duration_seconds: int):
        """Bloque temporairement une clé."""
        self._lock_store[key] = time.time() + duration_seconds


# Instance globale
_store = RateLimitStore()


# ═══════════════════════════════════════════════════════════
# RATE LIMITER
# ═══════════════════════════════════════════════════════════


class RateLimiter:
    """
    Rate limiter principal.
    
    Supporte plusieurs fenêtres de temps simultanées.
    """
    
    def __init__(
        self,
        store: RateLimitStore | None = None,
        config: RateLimitConfig | None = None,
    ):
        self.store = store or _store
        self.config = config or rate_limit_config
    
    def _get_key(
        self,
        request: Request,
        identifier: str | None = None,
        endpoint: str | None = None,
    ) -> str:
        """Génère une clé unique pour le rate limiting."""
        parts = []
        
        # Identifiant (IP ou user_id)
        if identifier:
            parts.append(f"user:{identifier}")
        else:
            # Obtenir l'IP client
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0].strip()
            else:
                ip = request.client.host if request.client else "unknown"
            parts.append(f"ip:{ip}")
        
        # Endpoint optionnel
        if endpoint:
            parts.append(f"endpoint:{endpoint}")
        
        return ":".join(parts)
    
    def check_rate_limit(
        self,
        request: Request,
        user_id: str | None = None,
        is_premium: bool = False,
        is_ai_endpoint: bool = False,
    ) -> dict[str, Any]:
        """
        Vérifie le rate limit et retourne les informations.
        
        Args:
            request: Requête FastAPI
            user_id: ID utilisateur (si authentifié)
            is_premium: Utilisateur premium
            is_ai_endpoint: Endpoint utilisant l'IA
            
        Returns:
            Dict avec: allowed, limit, remaining, reset, retry_after
            
        Raises:
            HTTPException: Si limite dépassée
        """
        # Vérifier les chemins exemptés
        if request.url.path in self.config.exempt_paths:
            return {"allowed": True, "limit": -1, "remaining": -1}
        
        key = self._get_key(request, user_id)
        
        # Vérifier si bloqué
        if self.store.is_blocked(key):
            raise HTTPException(
                status_code=429,
                detail="Trop de requêtes. Réessayez plus tard.",
                headers={"Retry-After": "60"}
            )
        
        # Déterminer les limites selon le type d'utilisateur et d'endpoint
        if is_ai_endpoint:
            limit_minute = self.config.ai_requests_per_minute
            limit_hour = self.config.ai_requests_per_hour
            limit_day = self.config.ai_requests_per_day
        elif is_premium:
            limit_minute = self.config.premium_requests_per_minute
            limit_hour = self.config.requests_per_hour * 2
            limit_day = self.config.requests_per_day * 2
        elif user_id:
            limit_minute = self.config.authenticated_requests_per_minute
            limit_hour = self.config.requests_per_hour
            limit_day = self.config.requests_per_day
        else:
            limit_minute = self.config.anonymous_requests_per_minute
            limit_hour = self.config.requests_per_hour // 2
            limit_day = self.config.requests_per_day // 2
        
        # Vérifier chaque fenêtre
        windows = [
            ("minute", 60, limit_minute),
            ("hour", 3600, limit_hour),
            ("day", 86400, limit_day),
        ]
        
        most_restrictive = None
        
        for window_name, window_seconds, limit in windows:
            window_key = f"{key}:{window_name}"
            count = self.store.increment(window_key, window_seconds)
            
            if count > limit:
                # Limite dépassée
                remaining = 0
                reset = self.store.get_reset_time(window_key, window_seconds)
                
                # Bloquer temporairement si abus répété
                if count > limit * 2:
                    self.store.block(key, 300)  # 5 minutes
                    logger.warning(f"Rate limit abuse detected: {key}")
                
                raise HTTPException(
                    status_code=429,
                    detail=f"Limite de requêtes dépassée ({window_name}). Réessayez dans {reset}s.",
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset),
                        "Retry-After": str(reset),
                    }
                )
            
            # Garder la fenêtre la plus restrictive
            remaining = limit - count
            reset = self.store.get_reset_time(window_key, window_seconds)
            
            if most_restrictive is None or remaining < most_restrictive["remaining"]:
                most_restrictive = {
                    "allowed": True,
                    "limit": limit,
                    "remaining": remaining,
                    "reset": reset,
                    "window": window_name,
                }
        
        return most_restrictive or {"allowed": True}
    
    def add_headers(self, response: Response, rate_info: dict[str, Any]):
        """Ajoute les headers de rate limiting à la réponse."""
        if not self.config.enable_headers:
            return
        
        if rate_info.get("limit", -1) >= 0:
            response.headers["X-RateLimit-Limit"] = str(rate_info.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(rate_info.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(rate_info.get("reset", 0))


# Instance globale
rate_limiter = RateLimiter()


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE FASTAPI
# ═══════════════════════════════════════════════════════════


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware FastAPI pour le rate limiting automatique.
    
    Usage:
        app.add_middleware(RateLimitMiddleware)
    """
    
    def __init__(self, app, limiter: RateLimiter | None = None):
        super().__init__(app)
        self.limiter = limiter or rate_limiter
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Intercepte les requêtes et applique le rate limiting."""
        # Extraire l'utilisateur du header Authorization
        user_id = None
        auth_header = request.headers.get("Authorization", "")
        
        if auth_header.startswith("Bearer "):
            try:
                import jwt
                token = auth_header.split(" ")[1]
                # Décoder sans vérifier (la vérification est faite ailleurs)
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("sub")
            except Exception:
                pass
        
        # Vérifier si c'est un endpoint IA
        is_ai = "/ai/" in request.url.path or "/suggest" in request.url.path
        
        # Vérifier le rate limit
        rate_info = self.limiter.check_rate_limit(
            request,
            user_id=user_id,
            is_ai_endpoint=is_ai,
        )
        
        # Exécuter la requête
        response = await call_next(request)
        
        # Ajouter les headers
        self.limiter.add_headers(response, rate_info)
        
        return response


# ═══════════════════════════════════════════════════════════
# DÉCORATEURS
# ═══════════════════════════════════════════════════════════


def rate_limit(
    requests_per_minute: int | None = None,
    requests_per_hour: int | None = None,
    key_func: Callable[[Request], str] | None = None,
):
    """
    Décorateur pour appliquer un rate limit spécifique à un endpoint.
    
    Usage:
        @app.get("/expensive-operation")
        @rate_limit(requests_per_minute=5)
        async def expensive_operation(request: Request):
            ...
    
    Args:
        requests_per_minute: Limite par minute
        requests_per_hour: Limite par heure
        key_func: Fonction pour générer la clé (par défaut: IP)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Trouver la request dans les arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request is None:
                request = kwargs.get("request")
            
            if request is None:
                # Pas de request, exécuter normalement
                return await func(*args, **kwargs)
            
            # Générer la clé
            if key_func:
                key = key_func(request)
            else:
                forwarded = request.headers.get("X-Forwarded-For")
                if forwarded:
                    ip = forwarded.split(",")[0].strip()
                else:
                    ip = request.client.host if request.client else "unknown"
                key = f"ip:{ip}:endpoint:{request.url.path}"
            
            # Vérifier les limites
            if requests_per_minute:
                count = _store.increment(f"{key}:minute", 60)
                if count > requests_per_minute:
                    reset = _store.get_reset_time(f"{key}:minute", 60)
                    raise HTTPException(
                        status_code=429,
                        detail=f"Limite dépassée. Réessayez dans {reset}s.",
                        headers={"Retry-After": str(reset)}
                    )
            
            if requests_per_hour:
                count = _store.increment(f"{key}:hour", 3600)
                if count > requests_per_hour:
                    reset = _store.get_reset_time(f"{key}:hour", 3600)
                    raise HTTPException(
                        status_code=429,
                        detail=f"Limite horaire dépassée. Réessayez dans {reset}s.",
                        headers={"Retry-After": str(reset)}
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# DÉPENDANCE FASTAPI
# ═══════════════════════════════════════════════════════════


async def check_rate_limit(
    request: Request,
    is_ai: bool = False,
) -> dict[str, Any]:
    """
    Dépendance FastAPI pour vérifier le rate limit.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(rate_info: dict = Depends(check_rate_limit)):
            ...
    
    Args:
        request: Requête FastAPI (injectée automatiquement)
        is_ai: True si endpoint utilisant l'IA
        
    Returns:
        Informations de rate limit
    """
    return rate_limiter.check_rate_limit(request, is_ai_endpoint=is_ai)


async def check_ai_rate_limit(request: Request) -> dict[str, Any]:
    """Dépendance pour les endpoints IA."""
    return await check_rate_limit(request, is_ai=True)


# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════


def get_rate_limit_stats() -> dict[str, Any]:
    """Retourne les statistiques de rate limiting."""
    return {
        "active_keys": len(_store._store),
        "blocked_keys": len(_store._lock_store),
        "config": {
            "requests_per_minute": rate_limit_config.requests_per_minute,
            "requests_per_hour": rate_limit_config.requests_per_hour,
            "ai_requests_per_minute": rate_limit_config.ai_requests_per_minute,
        }
    }


def reset_rate_limits():
    """Réinitialise tous les compteurs (pour les tests)."""
    global _store
    _store = RateLimitStore()


def configure_rate_limits(config: RateLimitConfig):
    """Configure les limites globales."""
    global rate_limit_config, rate_limiter
    rate_limit_config = config
    rate_limiter = RateLimiter(config=config)

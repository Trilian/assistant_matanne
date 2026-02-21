"""
Middleware Pipeline - Pipeline composable pour les appels de service.

Remplace l'empilement de @avec_cache + @avec_gestion_erreurs + @avec_session_db
par un pipeline middleware unique et composable avec ordre garanti correct.

Architecture:
    Service Method → Logging → RateLimit → Cache → ErrorHandler → Session → Execute

Usage:
    from src.services.core.middleware import service_method, with_pipeline

    # Option 1: Décorateur configurable
    @service_method(cache=True, rate_limit=True, session=True)
    def ma_methode(self, data: dict, db: Session = None) -> Recette:
        ...

    # Option 2: Preset pipeline
    @with_pipeline("ia")  # ou "db", "full", "minimal"
    def autre_methode(self, prompt: str) -> str:
        ...

Presets disponibles:
    - "minimal" : Logging + ErrorHandler
    - "db"      : Logging + ErrorHandler + Session
    - "ia"      : Logging + RateLimit + Cache + ErrorHandler
    - "full"    : Logging + RateLimit + Cache + ErrorHandler + Session

STATUS: Infrastructure optionnelle — disponible mais non câblée en production.
Les services utilisent actuellement BaseService._with_session() et BaseAIService.call_with_cache()
directement. Ce pipeline est une alternative plus composable pour des cas d'usage avancés.

Tests: tests/services/core/test_middleware.py (fonctionnels, couverture complète)
"""

from __future__ import annotations

import functools
import hashlib
import inspect
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ═══════════════════════════════════════════════════════════
# TYPES — Presets de pipelines
# ═══════════════════════════════════════════════════════════

PipelinePreset = Literal["minimal", "db", "ia", "full"]


# ═══════════════════════════════════════════════════════════
# CONTEXTE — Données transportées dans le pipeline
# ═══════════════════════════════════════════════════════════


@dataclass
class MiddlewareContext:
    """
    Contexte partagé entre les middlewares d'un pipeline.

    Transporte les métadonnées de l'appel et permet aux middlewares
    de communiquer entre eux sans couplage direct.
    """

    # Identité de l'appel
    service_name: str = ""
    method_name: str = ""
    call_id: str = ""

    # Paramètres de l'appel
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)

    # Configuration des middlewares
    use_cache: bool = False
    cache_ttl: int = 300
    cache_key: str = ""
    use_rate_limit: bool = False
    use_session: bool = False
    use_logging: bool = True

    # Valeur de fallback en cas d'erreur
    fallback_value: Any = None

    # Métriques collectées pendant l'exécution
    start_time: float = 0.0
    end_time: float = 0.0
    cache_hit: bool = False
    from_cache: bool = False
    error: Exception | None = None

    # Métadonnées additionnelles
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Durée d'exécution en millisecondes."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def set_timing(self) -> None:
        """Marque le début du timing."""
        self.start_time = time.perf_counter()

    def end_timing(self) -> None:
        """Marque la fin du timing."""
        self.end_time = time.perf_counter()


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE — Interface de base
# ═══════════════════════════════════════════════════════════

# Type du handler "next" dans la chaîne
NextHandler = Callable[[MiddlewareContext], Any]


class Middleware:
    """
    Middleware de base (à sous-classer).

    Chaque middleware reçoit le contexte et un callable `next_handler`
    pour passer au middleware suivant dans la chaîne.

    Usage:
        class MonMiddleware(Middleware):
            def process(self, ctx: MiddlewareContext, next_handler: NextHandler) -> Any:
                # Pré-traitement
                result = next_handler(ctx)  # Appel suivant
                # Post-traitement
                return result
    """

    def process(self, ctx: MiddlewareContext, next_handler: NextHandler) -> Any:
        """Traite la requête. À surcharger dans les sous-classes."""
        return next_handler(ctx)


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE: LOGGING
# ═══════════════════════════════════════════════════════════


class LoggingMiddleware(Middleware):
    """Middleware de logging avec métriques de performance."""

    def process(self, ctx: MiddlewareContext, next_handler: NextHandler) -> Any:
        ctx.set_timing()
        method_id = f"{ctx.service_name}.{ctx.method_name}"

        logger.debug(f"→ {method_id} appelé")

        try:
            result = next_handler(ctx)
            ctx.end_timing()

            # Log succès avec métriques
            cache_info = " (cache)" if ctx.from_cache else ""
            logger.info(f"✅ {method_id}{cache_info} — " f"{ctx.duration_ms:.1f}ms")
            return result

        except Exception as e:
            ctx.end_timing()
            ctx.error = e
            logger.error(f"❌ {method_id} — " f"{ctx.duration_ms:.1f}ms — {type(e).__name__}: {e}")
            raise


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE: CACHE
# ═══════════════════════════════════════════════════════════


class CacheMiddleware(Middleware):
    """Middleware de cache avec TTL."""

    def process(self, ctx: MiddlewareContext, next_handler: NextHandler) -> Any:
        if not ctx.use_cache:
            return next_handler(ctx)

        from src.core.caching import Cache

        # Générer la clé de cache si pas fournie
        cache_key = ctx.cache_key or self._generate_key(ctx)

        # Sentinelle pour distinguer None en cache de "pas en cache"
        _MISS = object()
        cached = Cache.obtenir(cache_key, sentinelle=_MISS, ttl=ctx.cache_ttl)

        if cached is not _MISS:
            ctx.cache_hit = True
            ctx.from_cache = True
            logger.debug(f"Cache HIT: {cache_key}")
            return cached

        # Cache miss → exécuter
        result = next_handler(ctx)

        # Sauvegarder en cache
        if result is not None:
            Cache.definir(cache_key, result, ttl=ctx.cache_ttl)
            logger.debug(f"Cache SET: {cache_key}")

        return result

    @staticmethod
    def _generate_key(ctx: MiddlewareContext) -> str:
        """Génère une clé de cache à partir du contexte."""
        # Exclure les params non-cachables (db, session)
        filtered_kwargs = {
            k: v for k, v in ctx.kwargs.items() if k not in ("db", "session", "self")
        }

        key_parts = [
            ctx.service_name,
            ctx.method_name,
            str(ctx.args[1:]) if len(ctx.args) > 1 else "",  # Skip self
            str(sorted(filtered_kwargs.items())),
        ]
        raw_key = "|".join(key_parts)
        return hashlib.md5(raw_key.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE: ERROR HANDLER (SANS couplage UI)
# ═══════════════════════════════════════════════════════════


class ErrorHandlerMiddleware(Middleware):
    """
    Middleware de gestion d'erreurs SANS couplage Streamlit.

    Les erreurs sont capturées, loguées et transformées en valeur de fallback.
    L'affichage UI est délégué à la couche UI via l'Event Bus.
    """

    def process(self, ctx: MiddlewareContext, next_handler: NextHandler) -> Any:
        try:
            return next_handler(ctx)
        except Exception as e:
            from src.core.errors_base import ExceptionApp

            ctx.error = e
            method_id = f"{ctx.service_name}.{ctx.method_name}"

            if isinstance(e, ExceptionApp):
                # Erreur métier — log adapté au type
                logger.warning(f"{type(e).__name__} dans {method_id}: {e.message}")
            else:
                # Erreur inattendue — log critique
                logger.error(f"Erreur inattendue dans {method_id}: {e}", exc_info=True)

            # Émettre un événement d'erreur (si event bus disponible)
            try:
                from src.services.core.events import obtenir_bus

                bus = obtenir_bus()
                bus.emettre(
                    "service.error",
                    {
                        "service": ctx.service_name,
                        "method": ctx.method_name,
                        "error_type": type(e).__name__,
                        "message": str(e),
                        "duration_ms": ctx.duration_ms,
                    },
                )
            except Exception as e:
                logger.debug("Event bus non disponible: %s", e)

            return ctx.fallback_value


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE: RATE LIMIT (IA)
# ═══════════════════════════════════════════════════════════


class RateLimitMiddleware(Middleware):
    """Middleware de rate limiting pour les appels IA."""

    def process(self, ctx: MiddlewareContext, next_handler: NextHandler) -> Any:
        if not ctx.use_rate_limit:
            return next_handler(ctx)

        from src.core.ai import RateLimitIA
        from src.core.errors_base import ErreurLimiteDebit

        autorise, msg = RateLimitIA.peut_appeler()
        if not autorise:
            logger.warning(f"⏳ Rate limit: {msg}")
            raise ErreurLimiteDebit(msg, message_utilisateur=msg)

        result = next_handler(ctx)

        # Enregistrer l'appel
        RateLimitIA.enregistrer_appel(
            service=ctx.service_name,
            tokens_utilises=ctx.metadata.get("tokens", 0),
        )

        return result


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE: SESSION DB
# ═══════════════════════════════════════════════════════════


class SessionMiddleware(Middleware):
    """Middleware d'injection de session DB."""

    def process(self, ctx: MiddlewareContext, next_handler: NextHandler) -> Any:
        if not ctx.use_session:
            return next_handler(ctx)

        # Vérifier si une session est déjà fournie
        db = ctx.kwargs.get("db") or ctx.kwargs.get("session")
        if db is not None:
            return next_handler(ctx)

        # Créer une nouvelle session
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            # Détecter le nom du paramètre dans la fonction cible
            ctx.kwargs["db"] = session
            return next_handler(ctx)


# ═══════════════════════════════════════════════════════════
# PIPELINE — Composition de middlewares
# ═══════════════════════════════════════════════════════════


class ServicePipeline:
    """
    Pipeline composable de middlewares.

    Compose les middlewares en une chaîne d'exécution.
    L'ordre est important : le premier middleware ajouté est
    le plus externe (exécuté en premier).

    Usage:
        pipeline = ServicePipeline()
        pipeline.add(LoggingMiddleware())
        pipeline.add(CacheMiddleware())
        pipeline.add(ErrorHandlerMiddleware())

        # Ou via factory:
        pipeline = ServicePipeline.default()
    """

    def __init__(self):
        self._middlewares: list[Middleware] = []

    def add(self, middleware: Middleware) -> ServicePipeline:
        """Ajoute un middleware au pipeline. Retourne self pour chaînage."""
        self._middlewares.append(middleware)
        return self

    def execute(
        self,
        func: Callable[..., T],
        ctx: MiddlewareContext,
    ) -> T:
        """
        Exécute la fonction à travers le pipeline de middlewares.

        Construit la chaîne de handlers (du dernier au premier middleware)
        puis exécute le tout.
        """

        # Handler final : exécuter la vraie fonction
        def final_handler(context: MiddlewareContext) -> T:
            return func(*context.args, **context.kwargs)

        # Construire la chaîne (en partant du dernier middleware)
        handler = final_handler
        for middleware in reversed(self._middlewares):
            # Capturer le middleware et le handler courant dans la closure
            handler = self._make_handler(middleware, handler)

        return handler(ctx)

    @staticmethod
    def _make_handler(middleware: Middleware, next_handler: NextHandler) -> NextHandler:
        """Crée un handler qui appelle le middleware avec le next_handler."""

        def handler(ctx: MiddlewareContext) -> Any:
            return middleware.process(ctx, next_handler)

        return handler

    @classmethod
    def default(cls) -> ServicePipeline:
        """
        Crée un pipeline avec la configuration standard.

        Ordre: Logging → ErrorHandler → Cache → RateLimit → Session
        """
        pipeline = cls()
        pipeline.add(LoggingMiddleware())
        pipeline.add(ErrorHandlerMiddleware())
        pipeline.add(CacheMiddleware())
        pipeline.add(RateLimitMiddleware())
        pipeline.add(SessionMiddleware())
        return pipeline

    @classmethod
    def minimal(cls) -> ServicePipeline:
        """Pipeline minimal : logging + error handling."""
        pipeline = cls()
        pipeline.add(LoggingMiddleware())
        pipeline.add(ErrorHandlerMiddleware())
        return pipeline

    @classmethod
    def ai_pipeline(cls) -> ServicePipeline:
        """Pipeline pour les services IA : avec rate limiting."""
        pipeline = cls()
        pipeline.add(LoggingMiddleware())
        pipeline.add(ErrorHandlerMiddleware())
        pipeline.add(CacheMiddleware())
        pipeline.add(RateLimitMiddleware())
        return pipeline


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: @service_method — Raccourci pour le pipeline
# ═══════════════════════════════════════════════════════════

# Pipeline singleton partagé
_default_pipeline: ServicePipeline | None = None


def _get_default_pipeline() -> ServicePipeline:
    """Obtient le pipeline par défaut (lazy singleton)."""
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = ServicePipeline.default()
    return _default_pipeline


def service_method(
    cache: bool = False,
    cache_ttl: int = 300,
    cache_key_func: Callable[..., str] | None = None,
    rate_limit: bool = False,
    session: bool = False,
    fallback: Any = None,
    log: bool = True,
    pipeline: ServicePipeline | None = None,
) -> Callable:
    """
    Décorateur pour appliquer le pipeline middleware à une méthode de service.

    Remplace l'empilement de @avec_cache + @avec_gestion_erreurs + @avec_session_db
    par un seul décorateur configurable.

    Usage:
        class MonService(BaseService[Recette]):
            @service_method(cache=True, cache_ttl=600, session=True)
            def charger_recettes(self, categorie: str, db: Session = None) -> list[Recette]:
                return db.query(Recette).filter_by(categorie=categorie).all()

            @service_method(rate_limit=True, cache=True)
            def suggerer_ia(self, prompt: str) -> str:
                return self.client.appeler(prompt)

    Args:
        cache: Activer le cache
        cache_ttl: Durée de vie du cache (secondes)
        cache_key_func: Fonction custom pour générer la clé de cache
        rate_limit: Activer le rate limiting (pour appels IA)
        session: Activer l'injection de session DB
        fallback: Valeur de retour en cas d'erreur
        log: Activer le logging
        pipeline: Pipeline custom (sinon utilise le default)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        active_pipeline = pipeline or _get_default_pipeline()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Extraire le service_name de self si disponible
            service_name = ""
            if args and hasattr(args[0], "service_name"):
                service_name = args[0].service_name
            elif args and hasattr(args[0], "__class__"):
                service_name = args[0].__class__.__name__

            # Construire le contexte
            ctx = MiddlewareContext(
                service_name=service_name,
                method_name=func.__name__,
                args=args,
                kwargs=kwargs,
                use_cache=cache,
                cache_ttl=cache_ttl,
                use_rate_limit=rate_limit,
                use_session=session,
                use_logging=log,
                fallback_value=fallback,
            )

            # Clé de cache custom
            if cache and cache_key_func:
                try:
                    ctx.cache_key = cache_key_func(*args, **kwargs)
                except Exception as e:
                    logger.debug("Cache key generation échouée: %s", e)

            return active_pipeline.execute(func, ctx)

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: @with_pipeline — Utilise un preset nommé
# ═══════════════════════════════════════════════════════════

# Cache des pipelines par preset (lazy init)
_preset_pipelines: dict[PipelinePreset, ServicePipeline] = {}


def _get_preset_pipeline(preset: PipelinePreset) -> ServicePipeline:
    """Obtient ou crée un pipeline pour un preset donné."""
    if preset not in _preset_pipelines:
        if preset == "minimal":
            _preset_pipelines[preset] = ServicePipeline.minimal()
        elif preset == "db":
            pipeline = ServicePipeline()
            pipeline.add(LoggingMiddleware())
            pipeline.add(ErrorHandlerMiddleware())
            pipeline.add(SessionMiddleware())
            _preset_pipelines[preset] = pipeline
        elif preset == "ia":
            _preset_pipelines[preset] = ServicePipeline.ai_pipeline()
        elif preset == "full":
            _preset_pipelines[preset] = ServicePipeline.default()
        else:
            raise ValueError(f"Preset inconnu: {preset}")
    return _preset_pipelines[preset]


def with_pipeline(
    preset: PipelinePreset = "full",
    cache_ttl: int = 300,
    cache_key_func: Callable[..., str] | None = None,
    fallback: Any = None,
) -> Callable:
    """
    Décorateur simplifié utilisant un preset de pipeline nommé.

    Plus simple que @service_method quand on veut juste un preset standard.

    Usage:
        @with_pipeline("ia")
        def suggerer(self, prompt: str) -> str:
            ...

        @with_pipeline("db")
        def charger(self, id: int, db: Session = None) -> Recette:
            ...

        @with_pipeline("full", cache_ttl=600, fallback=[])
        def lister(self, db: Session = None) -> list[Recette]:
            ...

    Presets:
        - "minimal" : Logging + ErrorHandler (pas de cache, DB, rate limit)
        - "db"      : Logging + ErrorHandler + Session DB
        - "ia"      : Logging + RateLimit + Cache + ErrorHandler
        - "full"    : Tous les middlewares (Logging + RateLimit + Cache + Error + Session)

    Args:
        preset: Nom du preset ("minimal", "db", "ia", "full")
        cache_ttl: TTL cache (si le preset inclut le cache)
        cache_key_func: Fonction custom pour clé de cache
        fallback: Valeur de retour en cas d'erreur
    """
    pipeline = _get_preset_pipeline(preset)

    # Déterminer les flags selon le preset
    use_cache = preset in ("ia", "full")
    use_rate_limit = preset in ("ia", "full")
    use_session = preset in ("db", "full")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Extraire le service_name
            service_name = ""
            if args and hasattr(args[0], "service_name"):
                service_name = args[0].service_name
            elif args and hasattr(args[0], "__class__"):
                service_name = args[0].__class__.__name__

            ctx = MiddlewareContext(
                service_name=service_name,
                method_name=func.__name__,
                args=args,
                kwargs=kwargs,
                use_cache=use_cache,
                cache_ttl=cache_ttl,
                use_rate_limit=use_rate_limit,
                use_session=use_session,
                use_logging=True,
                fallback_value=fallback,
            )

            if use_cache and cache_key_func:
                try:
                    ctx.cache_key = cache_key_func(*args, **kwargs)
                except Exception as e:
                    logger.debug("Cache key generation échouée: %s", e)

            return pipeline.execute(func, ctx)

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════
# PRESETS — Constantes pour configuration programmatique
# ═══════════════════════════════════════════════════════════

# Ces constantes permettent de référencer les presets sans chaînes
PIPELINE_MINIMAL: PipelinePreset = "minimal"
PIPELINE_DB: PipelinePreset = "db"
PIPELINE_IA: PipelinePreset = "ia"
PIPELINE_FULL: PipelinePreset = "full"


__all__ = [
    # Core
    "Middleware",
    "MiddlewareContext",
    "ServicePipeline",
    "PipelinePreset",
    # Middlewares
    "CacheMiddleware",
    "ErrorHandlerMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
    "SessionMiddleware",
    # Décorateurs
    "service_method",
    "with_pipeline",
    # Presets
    "PIPELINE_MINIMAL",
    "PIPELINE_DB",
    "PIPELINE_IA",
    "PIPELINE_FULL",
]

"""
Builtin — Middlewares pré-construits pour la pipeline.

Chaque middleware est autonome et configurable:
- ``LogMiddleware``: Logging structuré des opérations
- ``TimingMiddleware``: Chronométrage avec seuil d'alerte
- ``RetryMiddleware``: Retry automatique avec backoff exponentiel
- ``ValidationMiddleware``: Validation Pydantic des paramètres
- ``CacheMiddleware``: Cache transparent via CacheMultiNiveau
- ``CircuitBreakerMiddleware``: Protection circuit-breaker
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

from .base import Contexte, Middleware, NextFn

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════


class LogMiddleware(Middleware):
    """
    Middleware de logging structuré.

    Enregistre le début, la fin et les erreurs de chaque opération
    avec les métadonnées du contexte.

    Args:
        niveau: Niveau de log (default: "DEBUG")
        inclure_params: Inclure les paramètres dans le log
        logger_name: Nom du logger (default: module logger)
    """

    def __init__(
        self,
        niveau: str = "DEBUG",
        inclure_params: bool = False,
        logger_name: str | None = None,
    ):
        self._niveau = getattr(logging, niveau.upper(), logging.DEBUG)
        self._inclure_params = inclure_params
        self._logger = logging.getLogger(logger_name) if logger_name else logger

    def traiter(self, ctx: Contexte, suivant: NextFn) -> Any:
        params_str = f" params={ctx.params}" if self._inclure_params else ""
        self._logger.log(
            self._niveau,
            f"[DÉBUT] {ctx.operation}{params_str}",
        )

        try:
            result = suivant(ctx)
            self._logger.log(
                self._niveau,
                f"[FIN] {ctx.operation} ({ctx.duree_ms:.1f}ms)",
            )
            return result

        except Exception as e:
            self._logger.error(
                f"[ERREUR] {ctx.operation}: {type(e).__name__}: {e} " f"({ctx.duree_ms:.1f}ms)"
            )
            raise


# ═══════════════════════════════════════════════════════════
# TIMING
# ═══════════════════════════════════════════════════════════


class TimingMiddleware(Middleware):
    """
    Middleware de chronométrage avec alerte sur seuil.

    Mesure la durée d'exécution et émet un warning si le seuil
    est dépassé. Enregistre aussi dans les métriques si disponible.

    Args:
        seuil_ms: Seuil d'alerte en millisecondes (default: 500)
        enregistrer_metrique: Enregistrer dans le collecteur de métriques
    """

    def __init__(
        self,
        seuil_ms: float = 500,
        enregistrer_metrique: bool = True,
    ):
        self._seuil_ms = seuil_ms
        self._enregistrer = enregistrer_metrique

    def traiter(self, ctx: Contexte, suivant: NextFn) -> Any:
        debut = time.perf_counter()

        try:
            result = suivant(ctx)
            return result
        finally:
            duree_ms = (time.perf_counter() - debut) * 1000
            ctx.metadata["duree_ms"] = duree_ms

            if duree_ms > self._seuil_ms:
                logger.warning(
                    f"[LENT] {ctx.operation}: {duree_ms:.1f}ms " f"(seuil: {self._seuil_ms}ms)"
                )

            if self._enregistrer:
                try:
                    from src.core.monitoring import MetriqueType, enregistrer_metrique

                    enregistrer_metrique(
                        f"middleware.{ctx.operation}.duree_ms",
                        duree_ms,
                        MetriqueType.HISTOGRAMME,
                    )
                except ImportError:
                    pass


# ═══════════════════════════════════════════════════════════
# RETRY
# ═══════════════════════════════════════════════════════════


class RetryMiddleware(Middleware):
    """
    Middleware de retry avec backoff exponentiel.

    Relance automatiquement l'opération en cas d'échec sur des
    exceptions récupérables, avec un délai croissant entre les tentatives.

    Args:
        max_tentatives: Nombre maximum de tentatives (default: 3)
        delai_base: Délai initial en secondes (default: 0.5)
        facteur: Multiplicateur du délai (default: 2.0)
        exceptions: Tuple d'exceptions à retrier (default: Exception)
        sur_retry: Callback optionnel appelé avant chaque retry
    """

    def __init__(
        self,
        max_tentatives: int = 3,
        delai_base: float = 0.5,
        facteur: float = 2.0,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        sur_retry: Callable[[int, Exception], None] | None = None,
    ):
        self._max = max_tentatives
        self._delai_base = delai_base
        self._facteur = facteur
        self._exceptions = exceptions
        self._sur_retry = sur_retry

    def traiter(self, ctx: Contexte, suivant: NextFn) -> Any:
        derniere_erreur: Exception | None = None

        for tentative in range(1, self._max + 1):
            try:
                ctx.metadata["tentative"] = tentative
                result = suivant(ctx)
                if tentative > 1:
                    logger.info(f"[RETRY] {ctx.operation} réussi à la tentative {tentative}")
                return result

            except self._exceptions as e:
                derniere_erreur = e
                ctx.error = e

                if tentative < self._max:
                    delai = self._delai_base * (self._facteur ** (tentative - 1))
                    logger.warning(
                        f"[RETRY] {ctx.operation} tentative {tentative}/{self._max} "
                        f"échouée: {e}. Retry dans {delai:.1f}s"
                    )

                    if self._sur_retry:
                        self._sur_retry(tentative, e)

                    time.sleep(delai)
                else:
                    logger.error(
                        f"[RETRY] {ctx.operation} échec définitif après "
                        f"{self._max} tentatives: {e}"
                    )

        ctx.metadata["retries_epuises"] = True
        raise derniere_erreur  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


class ValidationMiddleware(Middleware):
    """
    Middleware de validation Pydantic des paramètres.

    Valide les paramètres du contexte via un modèle Pydantic
    avant de passer au middleware suivant.

    Args:
        schema: Classe Pydantic BaseModel pour validation
        champ: Clé dans ``ctx.params`` contenant les données (default: toutes)
        strict: Si True, lève une exception. Si False, log un warning.
    """

    def __init__(
        self,
        schema: type,
        champ: str | None = None,
        strict: bool = True,
    ):
        self._schema = schema
        self._champ = champ
        self._strict = strict

    def traiter(self, ctx: Contexte, suivant: NextFn) -> Any:
        from pydantic import ValidationError

        try:
            if self._champ:
                data = ctx.params.get(self._champ, {})
                validated = self._schema(**data)
                ctx.params[self._champ] = validated.model_dump()
            else:
                validated = self._schema(**ctx.params)
                ctx.params = validated.model_dump()

            ctx.metadata["validated"] = True

        except ValidationError as e:
            ctx.metadata["validation_errors"] = e.errors()

            if self._strict:
                from src.core.errors_base import ErreurValidation

                raise ErreurValidation(
                    f"Validation échouée pour {ctx.operation}: {e}",
                    details={"errors": e.errors()},
                    message_utilisateur="Les données fournies sont invalides.",
                ) from e
            else:
                logger.warning(
                    f"[VALIDATION] {ctx.operation}: {len(e.errors())} erreur(s) "
                    f"ignorées (mode non-strict)"
                )

        return suivant(ctx)


# ═══════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════


class CacheMiddleware(Middleware):
    """
    Middleware de cache transparent via CacheMultiNiveau.

    Vérifie le cache avant d'exécuter l'opération. Si le résultat
    est en cache, le retourne sans appeler ``suivant``.

    Args:
        ttl: Durée de vie en secondes (default: 300)
        key_fn: Fonction pour générer la clé de cache depuis le contexte.
            Défaut: ``f"{ctx.operation}:{sorted(ctx.params.items())}"``
        cache_none: Si True, cache aussi les résultats None (default: False)
    """

    def __init__(
        self,
        ttl: int = 300,
        key_fn: Callable[[Contexte], str] | None = None,
        cache_none: bool = False,
    ):
        self._ttl = ttl
        self._key_fn = key_fn
        self._cache_none = cache_none

    def traiter(self, ctx: Contexte, suivant: NextFn) -> Any:
        from src.core.caching import CacheMultiNiveau

        cache = CacheMultiNiveau()
        _MISS = object()

        # Générer la clé
        cache_key = (
            self._key_fn(ctx) if self._key_fn else f"{ctx.operation}:{sorted(ctx.params.items())}"
        )

        # Check cache
        cached = cache.get(cache_key, default=_MISS)
        if cached is not _MISS:
            ctx.metadata["cache_hit"] = True
            return cached

        # Exécuter et cacher
        ctx.metadata["cache_hit"] = False
        result = suivant(ctx)

        if result is not None or self._cache_none:
            cache.set(cache_key, result, ttl=self._ttl)

        return result


# ═══════════════════════════════════════════════════════════
# CIRCUIT BREAKER
# ═══════════════════════════════════════════════════════════


class CircuitBreakerMiddleware(Middleware):
    """
    Middleware circuit-breaker (protection contre les cascades d'erreurs).

    Trois états:
    - FERME: Opérations normales, comptage des erreurs
    - OUVERT: Rejette immédiatement (après ``seuil_erreurs`` erreurs)
    - SEMI-OUVERT: Laisse passer 1 requête de test après ``delai_reset``

    Args:
        seuil_erreurs: Nombre d'erreurs avant ouverture (default: 5)
        delai_reset: Secondes avant passage en semi-ouvert (default: 60)
        exceptions: Types d'exceptions déclenchant le breaker
    """

    def __init__(
        self,
        seuil_erreurs: int = 5,
        delai_reset: float = 60.0,
        exceptions: tuple[type[Exception], ...] = (Exception,),
    ):
        self._seuil = seuil_erreurs
        self._delai_reset = delai_reset
        self._exceptions = exceptions
        self._erreurs = 0
        self._dernier_echec: float = 0
        self._etat: str = "FERME"

    def traiter(self, ctx: Contexte, suivant: NextFn) -> Any:
        ctx.metadata["circuit_breaker_etat"] = self._etat

        # Circuit ouvert — rejeter immédiatement
        if self._etat == "OUVERT":
            if time.time() - self._dernier_echec > self._delai_reset:
                self._etat = "SEMI_OUVERT"
                logger.info(f"[CB] {ctx.operation}: passage en SEMI_OUVERT " f"(test de reprise)")
            else:
                raise RuntimeError(
                    f"Circuit ouvert pour '{ctx.operation}'. "
                    f"Retry dans {self._delai_reset - (time.time() - self._dernier_echec):.0f}s"
                )

        try:
            result = suivant(ctx)

            # Reset en cas de succès
            if self._etat == "SEMI_OUVERT":
                logger.info(f"[CB] {ctx.operation}: circuit refermé (succès)")
            self._etat = "FERME"
            self._erreurs = 0
            return result

        except self._exceptions as e:
            self._erreurs += 1
            self._dernier_echec = time.time()

            if self._erreurs >= self._seuil:
                self._etat = "OUVERT"
                logger.error(
                    f"[CB] {ctx.operation}: circuit OUVERT après "
                    f"{self._erreurs} erreurs consécutives"
                )
            elif self._etat == "SEMI_OUVERT":
                self._etat = "OUVERT"
                logger.warning(
                    f"[CB] {ctx.operation}: test de reprise échoué, " f"retour en OUVERT"
                )

            ctx.error = e
            raise

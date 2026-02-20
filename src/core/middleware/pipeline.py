"""
Pipeline — Constructeur et exécuteur de chaînes middleware.

Usage fluent::

    pipeline = (
        Pipeline("mon_service")
        .utiliser(LogMiddleware())
        .utiliser(TimingMiddleware(seuil_ms=100))
        .construire()
    )

    # Exécution directe
    result = pipeline.executer(
        Contexte(operation="charger"),
        handler=lambda ctx: db.query(Model).all()
    )

    # Ou via décorateur
    @pipeline.decorer
    def ma_fonction(x: int) -> int:
        return x * 2
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from .base import Contexte, Middleware, NextFn

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class Pipeline:
    """
    Constructeur de pipeline middleware (builder pattern).

    Compose N middlewares en une chaîne d'exécution
    imbriquée (onion model) :

        LogMiddleware → TimingMiddleware → RetryMiddleware → handler

    Chaque middleware peut :
    - Modifier le contexte avant/après
    - Court-circuiter la chaîne (ne pas appeler ``suivant``)
    - Intercepter les exceptions
    """

    def __init__(self, nom: str = "default"):
        """
        Args:
            nom: Nom de la pipeline (pour logging/debug)
        """
        self._nom = nom
        self._middlewares: list[Middleware] = []
        self._construit = False

    # ── Builder (Fluent API) ─────────────────────────────────

    def utiliser(self, middleware: Middleware) -> Pipeline:
        """
        Ajoute un middleware à la chaîne.

        Args:
            middleware: Instance de Middleware à ajouter

        Returns:
            Self (fluent API)

        Raises:
            RuntimeError: Si la pipeline est déjà construite
        """
        if self._construit:
            raise RuntimeError(
                f"Pipeline '{self._nom}' déjà construite. "
                "Créez une nouvelle instance pour modifier la chaîne."
            )
        self._middlewares.append(middleware)
        return self

    def construire(self) -> Pipeline:
        """
        Finalise la pipeline (empêche les modifications ultérieures).

        Returns:
            Self (fluent API)
        """
        self._construit = True
        logger.info(
            f"Pipeline '{self._nom}' construite avec "
            f"{len(self._middlewares)} middleware(s): "
            f"{[m.nom for m in self._middlewares]}"
        )
        return self

    # ── Exécution ────────────────────────────────────────────

    def executer(
        self,
        ctx: Contexte,
        handler: NextFn,
    ) -> Any:
        """
        Exécute la pipeline complète.

        Construit la chaîne d'appels imbriquée (onion model)
        puis l'exécute avec le contexte donné.

        Args:
            ctx: Contexte initial
            handler: Fonction finale (la logique métier)

        Returns:
            Résultat de l'exécution
        """
        # Construire la chaîne de fonctions imbriquées
        # handler → wrappedByLastMiddleware → ... → wrappedByFirstMiddleware
        chain: NextFn = handler

        for middleware in reversed(self._middlewares):
            chain = self._wrap(middleware, chain)

        # Exécuter la chaîne complète
        result = chain(ctx)
        ctx.result = result
        return result

    def decorer(self, func: F) -> F:
        """
        Décorateur qui wrappe une fonction avec la pipeline.

        Le Contexte est créé automatiquement à partir des arguments
        de la fonction.

        Usage::

            @pipeline.decorer
            def charger_recettes(page: int = 1) -> list:
                return db.query(Recette).all()

        Args:
            func: Fonction à décorer

        Returns:
            Fonction décorée avec la pipeline
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = Contexte(
                operation=func.__qualname__,
                params=kwargs,
                args=args,
            )

            def handler(c: Contexte) -> Any:
                return func(*c.args, **c.params)

            return self.executer(ctx, handler)

        return wrapper  # type: ignore

    # ── Introspection ────────────────────────────────────────

    @property
    def nom(self) -> str:
        """Nom de la pipeline."""
        return self._nom

    @property
    def middlewares(self) -> list[Middleware]:
        """Liste des middlewares (lecture seule)."""
        return list(self._middlewares)

    def __len__(self) -> int:
        return len(self._middlewares)

    def __repr__(self) -> str:
        noms = [m.nom for m in self._middlewares]
        return f"Pipeline('{self._nom}', middlewares={noms})"

    # ── Privé ────────────────────────────────────────────────

    @staticmethod
    def _wrap(middleware: Middleware, suivant: NextFn) -> NextFn:
        """Enrobe un handler avec un middleware."""

        def wrapped(ctx: Contexte) -> Any:
            return middleware.traiter(ctx, suivant)

        return wrapped

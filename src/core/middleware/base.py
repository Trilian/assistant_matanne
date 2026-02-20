"""
Base — Types et classes abstraites du middleware.

Définit:
- ``Contexte``: Objet de contexte traversant la pipeline
- ``Middleware``: Classe abstraite pour chaque maillon
- ``NextFn``: Type de la fonction "next" de la chaîne
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# Type de la fonction "suivant" dans la chaîne
NextFn = Callable[["Contexte"], Any]


@dataclass
class Contexte:
    """
    Objet de contexte traversant la pipeline middleware.

    Transporte les données de requête, les métadonnées et le résultat
    à travers chaque middleware de la chaîne.

    Attributes:
        operation: Nom de l'opération en cours
        params: Paramètres de l'opération (kwargs)
        args: Arguments positionnels
        metadata: Métadonnées libres (timing, retry count, etc.)
        result: Résultat de l'opération (rempli par le handler final)
        error: Exception levée (remplie si erreur)
        timestamp: Moment de création du contexte
    """

    operation: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    args: tuple = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Exception | None = None
    timestamp: float = field(default_factory=time.time)

    @property
    def duree_ms(self) -> float:
        """Durée depuis la création du contexte en millisecondes."""
        return (time.time() - self.timestamp) * 1000

    @property
    def a_echoue(self) -> bool:
        """Indique si l'opération a échoué."""
        return self.error is not None

    def avec_metadata(self, **kwargs: Any) -> Contexte:
        """Retourne le contexte avec des métadonnées supplémentaires (fluent)."""
        self.metadata.update(kwargs)
        return self


class Middleware(ABC):
    """
    Classe abstraite pour un middleware de la pipeline.

    Chaque middleware reçoit un ``Contexte`` et une fonction ``next``
    qu'il doit appeler pour continuer la chaîne (ou pas, pour court-circuiter).

    Implémentez :meth:`traiter` pour ajouter votre logique::

        class MonMiddleware(Middleware):
            def traiter(self, ctx: Contexte, suivant: NextFn) -> Any:
                # Avant
                logger.info(f"Début {ctx.operation}")
                # Appeler le suivant
                result = suivant(ctx)
                # Après
                logger.info(f"Fin {ctx.operation}")
                return result
    """

    @abstractmethod
    def traiter(self, ctx: Contexte, suivant: NextFn) -> Any:
        """
        Traite le contexte et appelle le middleware suivant.

        Args:
            ctx: Contexte de l'opération
            suivant: Fonction pour appeler le prochain middleware

        Returns:
            Résultat de l'opération (passé à travers la chaîne)
        """
        ...

    @property
    def nom(self) -> str:
        """Nom du middleware (pour logging/debug)."""
        return self.__class__.__name__

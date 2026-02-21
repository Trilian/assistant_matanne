"""Décorateur: gestion unifiée des sessions de base de données."""

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def avec_session_db(func: F) -> F:
    """
    Décorateur unifié pour gestion de session DB.

    Injecte automatiquement une session DB si :
    - Aucune session n'est fournie en paramètre
    - Utilise obtenir_contexte_db() pour créer une nouvelle session

    Usage:
        @avec_session_db
        def creer_recette(data: dict, db: Session) -> Recette:
            recette = Recette(**data)
            db.add(recette)
            db.commit()
            return recette

        # Appel sans DB (session créée automatiquement)
        recette = creer_recette({"nom": "Tarte"})

        # Appel avec DB existante
        with obtenir_contexte_db() as session:
            recette = creer_recette({"nom": "Tarte"}, db=session)

    Raises:
        ErreurBaseDeDonnees: Si création de session échoue
    """

    # Pré-calculer la signature à la décoration (pas à chaque appel)
    _sig = inspect.signature(func)
    _param_name = "session" if "session" in _sig.parameters else "db"

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Si 'db' ou 'session' est déjà fourni(e), utiliser directement
        if ("db" in kwargs and kwargs["db"] is not None) or (
            "session" in kwargs and kwargs["session"] is not None
        ):
            return func(*args, **kwargs)

        # Sinon, créer une nouvelle session
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            kwargs[_param_name] = session
            return func(*args, **kwargs)

    return wrapper  # type: ignore

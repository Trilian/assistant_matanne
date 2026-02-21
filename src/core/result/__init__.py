"""
Result Package — Gestion explicite des succès/échecs style Rust.

Ce package fournit un type Result monadique pour remplacer les exceptions
implicites par une gestion explicite et typée des erreurs.

Organisation:
- codes.py: ErrorCode (enum), ErrorInfo (dataclass)
- base.py: Result (ABC), Ok, Err
- helpers.py: success(), failure(), capturer(), depuis_option()
- combinators.py: combiner(), collect(), premier_ok()
- decorators.py: @avec_result, @safe, @result_api

Usage basique::

    from src.core.result import Ok, Err, Result

    def diviser(a: int, b: int) -> Result[float, str]:
        if b == 0:
            return Err("Division par zéro")
        return Ok(a / b)

    # Pattern matching (Python 3.10+)
    match diviser(10, 2):
        case Ok(v): print(f"Résultat: {v}")
        case Err(e): print(f"Erreur: {e}")

    # Chaînage fonctionnel
    result = (
        diviser(10, 2)
        .map(lambda x: x * 2)
        .map_err(lambda e: f"Erreur calcul: {e}")
        .unwrap_or(0.0)
    )

Usage production (erreurs structurées)::

    from src.core.result import Ok, failure, ErrorCode, result_api

    def charger_recette(id: int) -> Result[Recette, ErrorInfo]:
        recette = db.get(id)
        if not recette:
            return failure(ErrorCode.NOT_FOUND, f"Recette #{id} introuvable")
        return Ok(recette)

    @result_api(message_utilisateur="Impossible de charger les recettes")
    def charger_recettes(categorie: str) -> list[Recette]:
        return db.query(Recette).filter_by(categorie=categorie).all()
"""

from __future__ import annotations

# Types principaux
from .base import Err, Failure, Ok, Result, Success

# Codes d'erreur
from .codes import ErrorCode, ErrorInfo

# Combinateurs
from .combinators import collect, collect_all, combiner, premier_ok

# Décorateurs
from .decorators import avec_result, register_error_mapping, result_api, safe

# Helpers
from .helpers import (
    capturer,
    capturer_async,
    depuis_bool,
    depuis_option,
    failure,
    from_exception,
    success,
)

__all__ = [
    # Types principaux
    "Result",
    "Ok",
    "Err",
    "ErrorInfo",
    "ErrorCode",
    # Aliases backward compat
    "Success",
    "Failure",
    # Factories
    "success",
    "failure",
    "from_exception",
    # Helpers conversion
    "capturer",
    "capturer_async",
    "depuis_option",
    "depuis_bool",
    # Combinateurs
    "combiner",
    "premier_ok",
    "collect",
    "collect_all",
    # Décorateurs
    "avec_result",
    "safe",
    "result_api",
    # Extension
    "register_error_mapping",
]

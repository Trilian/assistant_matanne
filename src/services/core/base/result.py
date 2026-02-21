"""
Result[T, E] - Shim de rétro-compatibilité.

Ce module re-exporte TOUT depuis ``src.core.result`` (source de vérité unique).
Les imports existants ``from src.services.core.base.result import ...`` continuent
de fonctionner sans modification.

Pour tout nouveau code, préférer::

    from src.core.result import Ok, Err, Result, ErrorCode, ErrorInfo
"""

# Re-export intégral depuis la source de vérité unique
from src.core.result import (
    Err,
    ErrorCode,
    ErrorInfo,
    Ok,
    Result,
    avec_result,
    capturer,
    capturer_async,
    collect,
    collect_all,
    combiner,
    depuis_bool,
    depuis_option,
    failure,
    from_exception,
    premier_ok,
    register_error_mapping,
    result_api,
    safe,
    success,
)
from src.core.result import (
    Err as Failure,
)
from src.core.result import (
    Ok as Success,
)

__all__ = [
    # Types principaux (noms compat)
    "Result",
    "Success",
    "Failure",
    # Types principaux (noms canoniques)
    "Ok",
    "Err",
    "ErrorInfo",
    "ErrorCode",
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

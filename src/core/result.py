"""Result shim — ré-exports depuis le package ``src.core.result``.

DEPRECATED: Ce module fournit un import rétro-compatible.

Préférez importer directement depuis ``src.core.result`` (package).
"""

from __future__ import annotations

# Ré-export public depuis le package implémenté dans
# ``src/core/result/`` (package). Ce fichier reste uniquement
# pour la rétro-compatibilité des imports existants.
from src.core.result import (
    Err,
    ErrorCode,
    ErrorInfo,
    Failure,
    Ok,
    Result,
    Success,
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

__all__ = [
    "Result",
    "Ok",
    "Err",
    "ErrorInfo",
    "ErrorCode",
    "Success",
    "Failure",
    "success",
    "failure",
    "from_exception",
    "capturer",
    "capturer_async",
    "depuis_option",
    "depuis_bool",
    "combiner",
    "premier_ok",
    "collect",
    "collect_all",
    "avec_result",
    "safe",
    "result_api",
    "register_error_mapping",
]

"""
Dépendances FastAPI pour la limitation de débit.
"""

from typing import Any

from fastapi import Request

from .limiter import limiteur_debit


async def verifier_limite_debit(
    request: Request,
    est_ia: bool = False,
) -> dict[str, Any]:
    """
    Dépendance FastAPI pour vérifier la limite de débit.

    Usage:
        @app.get("/endpoint")
        async def endpoint(
            request: Request,
            rate_info: dict = Depends(verifier_limite_debit)
        ):
            ...
    """
    return limiteur_debit.verifier_limite(request, est_endpoint_ia=est_ia)


async def verifier_limite_debit_ia(request: Request) -> dict[str, Any]:
    """Dépendance pour les endpoints IA."""
    return await verifier_limite_debit(request, est_ia=True)

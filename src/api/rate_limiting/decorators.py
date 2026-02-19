"""
Décorateurs pour la limitation de débit.
"""

from collections.abc import Callable
from functools import wraps

from fastapi import HTTPException, Request

from .storage import _stockage


def limite_debit(
    requetes_par_minute: int | None = None,
    requetes_par_heure: int | None = None,
    fonction_cle: Callable[[Request], str] | None = None,
):
    """
    Décorateur pour appliquer une limite de débit spécifique à un endpoint.

    Usage:
        @app.get("/operation-couteuse")
        @limite_debit(requetes_par_minute=5)
        async def operation_couteuse(request: Request):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request is None:
                request = kwargs.get("request")

            if request is None:
                return await func(*args, **kwargs)

            if fonction_cle:
                cle = fonction_cle(request)
            else:
                forwarded = request.headers.get("X-Forwarded-For")
                if forwarded:
                    ip = forwarded.split(",")[0].strip()
                else:
                    ip = request.client.host if request.client else "unknown"
                cle = f"ip:{ip}:endpoint:{request.url.path}"

            if requetes_par_minute:
                compte = _stockage.incrementer(f"{cle}:minute", 60)
                if compte > requetes_par_minute:
                    reset = _stockage.obtenir_temps_reset(f"{cle}:minute", 60)
                    raise HTTPException(
                        status_code=429,
                        detail=f"Limite dépassée. Réessayez dans {reset}s.",
                        headers={"Retry-After": str(reset)},
                    )

            if requetes_par_heure:
                compte = _stockage.incrementer(f"{cle}:hour", 3600)
                if compte > requetes_par_heure:
                    reset = _stockage.obtenir_temps_reset(f"{cle}:hour", 3600)
                    raise HTTPException(
                        status_code=429,
                        detail=f"Limite horaire dépassée. Réessayez dans {reset}s.",
                        headers={"Retry-After": str(reset)},
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator

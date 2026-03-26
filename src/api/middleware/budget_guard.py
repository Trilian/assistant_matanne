"""
Middleware Budget Guard — Bloque les paris si limite mensuelle atteinte.

Ce middleware s'applique aux routes de création de paris et contrôle:
- Limite mensuelle dépassée
- Auto-exclusion active
- Mode cooldown actif
"""

import logging
from typing import Awaitable, Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class BudgetGuardMiddleware(BaseHTTPMiddleware):
    """
    Middleware de protection budget qui bloque les paris si
    la limite mensuelle est atteinte ou si l'auto-exclusion est active.

    Routes concernées:
    - POST /api/v1/jeux/paris
    - POST /api/v1/jeux/loto/grilles
    - POST /api/v1/jeux/euromillions/grilles
    """

    PROTECTED_ROUTES = [
        "/api/v1/jeux/paris",
        "/api/v1/jeux/loto/grilles",
        "/api/v1/jeux/euromillions/grilles",
    ]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Dispatch middleware: vérifie le budget avant tout pari.
        """
        # Check si route protégée + méthode POST
        if request.method == "POST" and any(
            request.url.path.startswith(route) for route in self.PROTECTED_ROUTES
        ):
            # Vérifier le statut du jeu responsable
            try:
                from src.services.jeux import get_responsable_gaming_service

                svc = get_responsable_gaming_service()
                suivi = svc.obtenir_suivi_mensuel()

                # Blocage 1: Auto-exclusion active
                if suivi.get("auto_exclusion") and suivi["auto_exclusion"] is not None:
                    logger.warning(
                        f"Tentative pari bloquée: auto-exclusion active jusqu'au {suivi['auto_exclusion']}"
                    )
                    raise HTTPException(
                        status_code=403,
                        detail=f"🚫 Auto-exclusion active jusqu'au {suivi['auto_exclusion']}. Veuillez respecter votre pause.",
                    )

                # Blocage 2: Budget mensuel atteint
                if suivi.get("est_bloque", False):
                    logger.warning(
                        f"Tentative pari bloquée: budget mensuel atteint ({suivi.get('limite_mensuelle', 0)}€)"
                    )
                    raise HTTPException(
                        status_code=402,
                        detail=f"💳 Budget mensuel atteint ({suivi.get('limite_mensuelle', 0)}€). Attendez le mois prochain ou augmentez votre limite.",
                    )

                # Blocage 3: Mode cooldown actif
                if suivi.get("cooldown_actif", False):
                    cooldown_fin = suivi.get("cooldown_fin", "")
                    logger.warning(
                        f"Tentative pari bloquée: cooldown actif jusqu'au {cooldown_fin}"
                    )
                    raise HTTPException(
                        status_code=429,
                        detail=f"⏸️ Mode cooldown actif jusqu'au {cooldown_fin}. Prenez une pause avant de jouer à nouveau.",
                    )

            except HTTPException:
                raise  # Re-raise pour bloquer la requête
            except Exception as e:
                # Si erreur dans le service, logger mais ne PAS bloquer
                # (principe fail-open pour éviter blocage total)
                logger.error(f"Erreur middleware budget guard: {e}", exc_info=True)

        # Passer au handler suivant si tout est OK
        return await call_next(request)

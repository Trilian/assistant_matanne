"""
Endpoint de reporting CSP (Content-Security-Policy).

Reçoit les rapports de violations CSP envoyés par les navigateurs
et les journalise pour analyse. Utilisé en tandem avec le header
Content-Security-Policy: report-uri /api/v1/security/csp-report

Phase I — I8: CSP strict + rotation JWT
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import Response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/security", tags=["Sécurité"])


def _journaliser_violation(rapport: dict, ip: str) -> None:
    """Journalise une violation CSP (exécuté en tâche de fond)."""
    uri = rapport.get("document-uri", "?")
    directive = rapport.get("violated-directive", "?")
    bloque = rapport.get("blocked-uri", "?")
    sample = rapport.get("script-sample", "")

    logger.warning(
        "🛡️ CSP violation — directive='%s' blocked='%s' document='%s' ip='%s'%s",
        directive,
        bloque,
        uri,
        ip,
        f" sample='{sample[:80]}'" if sample else "",
    )


@router.post(
    "/csp-report",
    status_code=204,
    summary="Rapport de violation CSP",
    description=(
        "Endpoint public recevant les rapports de violations CSP "
        "envoyés automatiquement par les navigateurs. "
        "Toujours répond 204 No Content pour ne pas perturber les navigateurs."
    ),
    include_in_schema=False,  # Pas dans la doc Swagger publique
)
async def recevoir_rapport_csp(
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    """
    Reçoit et journalise les violations CSP du navigateur.

    Les navigateurs envoient des rapports JSON au format:
    { "csp-report": { "document-uri": ..., "violated-directive": ..., ... } }

    On répond toujours 204 pour éviter les erreurs côté navigateur.
    """
    try:
        body = await request.json()
        # Le rapport peut être encapsulé dans "csp-report" ou directement à la racine
        rapport = body.get("csp-report", body)
        ip = request.client.host if request.client else "unknown"
        background_tasks.add_task(_journaliser_violation, rapport, ip)
    except Exception:
        # Ne jamais renvoyer d'erreur au navigateur pour les rapports CSP
        pass

    return Response(status_code=204)

"""
"""Routes API Export Backup — Export de données personnelles.

Endpoints pour l'export de données (backup personnel) et la suppression de compte.
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from src.api.dependencies import require_auth
from src.api.schemas.rgpd import (
    ExportRGPDResponse,
    ResumeDonneesResponse,
    SuppressionCompteRequest,
    SuppressionCompteResponse,
)
from src.api.utils import executer_async, gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rgpd", tags=["Export Backup"])


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENDPOINTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/export", responses={200: {"content": {"application/zip": {}}}})
@gerer_exception_api
async def exporter_donnees(
    user: dict = Depends(require_auth),
):
    """
    Exporte toutes les donnÃ©es personnelles de l'utilisateur (droit d'accÃ¨s RGPD).

    Retourne un fichier ZIP contenant :
    - `donnees.json` : toutes les donnÃ©es en JSON
    - Un fichier CSV par catÃ©gorie de donnÃ©es
    - `metadata.json` : mÃ©tadonnÃ©es de l'export

    Returns:
        Fichier ZIP tÃ©lÃ©chargeable
    """
    from src.services.core.utilisateur.rgpd import obtenir_rgpd_service

    service = obtenir_rgpd_service()
    user_id = user.get("sub") or user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Identifiant utilisateur manquant")

    def _export():
        return service.exporter_donnees_utilisateur(user_id=user_id)

    zip_path = await executer_async(_export)

    if not zip_path or not zip_path.exists():
        raise HTTPException(status_code=500, detail="Erreur lors de la gÃ©nÃ©ration de l'export")

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=zip_path.name,
        headers={"Content-Disposition": f'attachment; filename="{zip_path.name}"'},
    )


@router.get("/data-summary", response_model=ResumeDonneesResponse)
@gerer_exception_api
async def resume_donnees(
    user: dict = Depends(require_auth),
):
    """
    RÃ©sumÃ© des donnÃ©es personnelles stockÃ©es (nombre d'Ã©lÃ©ments par catÃ©gorie).

    Permet Ã  l'utilisateur de voir quelles donnÃ©es sont stockÃ©es sans les tÃ©lÃ©charger.
    """
    from src.services.core.utilisateur.rgpd import obtenir_rgpd_service

    service = obtenir_rgpd_service()
    user_id = user.get("sub") or user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Identifiant utilisateur manquant")

    def _summary():
        return service.obtenir_resume_donnees(user_id=user_id)

    return await executer_async(_summary)


@router.post("/delete-account", response_model=SuppressionCompteResponse)
@gerer_exception_api
async def supprimer_compte(
    request: SuppressionCompteRequest,
    user: dict = Depends(require_auth),
):
    """
    Supprime dÃ©finitivement le compte et toutes les donnÃ©es associÃ©es (droit Ã  l'effacement).

    **ATTENTION** : Cette action est irrÃ©versible. Toutes les donnÃ©es seront supprimÃ©es.

    Le champ `confirmation` doit contenir exactement "SUPPRIMER MON COMPTE".
    """
    if request.confirmation != "SUPPRIMER MON COMPTE":
        raise HTTPException(
            status_code=400,
            detail="Confirmation invalide. Envoyez exactement 'SUPPRIMER MON COMPTE'.",
        )

    from src.services.core.utilisateur.rgpd import obtenir_rgpd_service

    service = obtenir_rgpd_service()
    user_id = user.get("sub") or user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Identifiant utilisateur manquant")

    logger.warning(
        f"Demande de suppression de compte RGPD pour user {user_id[:8]}, "
        f"motif: {request.motif or 'non spÃ©cifiÃ©'}"
    )

    def _delete():
        return service.supprimer_compte(user_id=user_id)

    elements_supprimes = await executer_async(_delete)

    return SuppressionCompteResponse(
        message="Votre compte et toutes vos donnÃ©es ont Ã©tÃ© supprimÃ©s dÃ©finitivement.",
        deleted_at=datetime.now(UTC),
        elements_supprimes=elements_supprimes,
    )


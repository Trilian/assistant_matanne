"""
Routes API RGPD — Export et suppression des données personnelles.

Endpoints pour le droit d'accès, de portabilité et d'effacement (RGPD).
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

router = APIRouter(prefix="/api/v1/rgpd", tags=["RGPD"])


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.get("/export", responses={200: {"content": {"application/zip": {}}}})
@gerer_exception_api
async def exporter_donnees(
    user: dict = Depends(require_auth),
):
    """
    Exporte toutes les données personnelles de l'utilisateur (droit d'accès RGPD).

    Retourne un fichier ZIP contenant :
    - `donnees.json` : toutes les données en JSON
    - Un fichier CSV par catégorie de données
    - `metadata.json` : métadonnées de l'export

    Returns:
        Fichier ZIP téléchargeable
    """
    from src.services.core.utilisateur.rgpd import get_rgpd_service

    service = get_rgpd_service()
    user_id = user.get("sub", user.get("id", ""))

    def _export():
        return service.exporter_donnees_utilisateur(user_id=user_id)

    zip_path = await executer_async(_export)

    if not zip_path or not zip_path.exists():
        raise HTTPException(status_code=500, detail="Erreur lors de la génération de l'export")

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
    Résumé des données personnelles stockées (nombre d'éléments par catégorie).

    Permet à l'utilisateur de voir quelles données sont stockées sans les télécharger.
    """
    from src.services.core.utilisateur.rgpd import get_rgpd_service

    service = get_rgpd_service()
    user_id = user.get("sub", user.get("id", ""))

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
    Supprime définitivement le compte et toutes les données associées (droit à l'effacement).

    **ATTENTION** : Cette action est irréversible. Toutes les données seront supprimées.

    Le champ `confirmation` doit contenir exactement "SUPPRIMER MON COMPTE".
    """
    if request.confirmation != "SUPPRIMER MON COMPTE":
        raise HTTPException(
            status_code=400,
            detail="Confirmation invalide. Envoyez exactement 'SUPPRIMER MON COMPTE'.",
        )

    from src.services.core.utilisateur.rgpd import get_rgpd_service

    service = get_rgpd_service()
    user_id = user.get("sub", user.get("id", ""))

    logger.warning(
        f"Demande de suppression de compte RGPD pour user {user_id[:8]}, "
        f"motif: {request.motif or 'non spécifié'}"
    )

    def _delete():
        return service.supprimer_compte(user_id=user_id)

    elements_supprimes = await executer_async(_delete)

    return SuppressionCompteResponse(
        message="Votre compte et toutes vos données ont été supprimés définitivement.",
        deleted_at=datetime.now(UTC),
        elements_supprimes=elements_supprimes,
    )

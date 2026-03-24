"""
Routes API pour l'export PDF.

Génération de documents PDF via le service ServiceExportPDF.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_LECTURE
from src.api.utils import executer_async, gerer_exception_api
from src.services.rapports.export import obtenir_service_export_pdf

router = APIRouter(prefix="/api/v1/export", tags=["Export"])

TYPES_EXPORT = {"courses", "planning", "recette", "budget"}


@router.post("/pdf", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def exporter_pdf(
    type_export: str = Query(
        ...,
        description="Type d'export: courses, planning, recette, budget",
    ),
    id_ressource: int | None = Query(None, description="ID optionnel de la ressource"),
    user: dict[str, Any] = Depends(require_auth),
):
    """
    Génère un export PDF.

    Types supportés:
    - courses: Liste de courses active
    - planning: Planning de la semaine (id_ressource requis)
    - recette: Fiche recette détaillée (id_ressource requis)
    - budget: Résumé budget mensuel (id_ressource = période en jours, défaut: 30)
    """
    if type_export not in TYPES_EXPORT:
        raise HTTPException(
            status_code=422,
            detail=f"Type d'export non supporté: {type_export}",
        )

    if type_export in ("recette", "planning") and not id_ressource:
        raise HTTPException(
            status_code=422,
            detail=f"id_ressource requis pour {type_export}",
        )

    def _generate():
        service = obtenir_service_export_pdf()

        if type_export == "courses":
            return service.exporter_liste_courses(), "liste_courses"

        elif type_export == "planning":
            return service.exporter_planning_semaine(id_ressource), "planning_semaine"

        elif type_export == "recette":
            return service.exporter_recette(id_ressource), "recette"

        elif type_export == "budget":
            periode = id_ressource if id_ressource else 30  # Période en jours (défaut: 30)
            return service.exporter_budget(periode), "budget_familial"

    buffer, nom_fichier = await executer_async(_generate)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nom_fichier}.pdf"',
        },
    )

"""
Routes API pour l'export PDF.

Génération de documents PDF via le service backend.
"""

import io
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_LECTURE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/export", tags=["Export"])


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
    - planning: Planning de la semaine
    - recette: Fiche recette détaillée
    - budget: Résumé budget mensuel
    """
    from src.api.utils import executer_avec_session

    def _generate():
        with executer_avec_session() as session:
            # Pour chaque type, on génère un contenu texte simple
            # Le vrai PDF sera implémenté quand le ServiceRapportsPDF sera connecté
            if type_export == "courses":
                from src.core.models import ListeCourses

                if not id_ressource:
                    raise HTTPException(status_code=422, detail="id_ressource requis pour courses")
                liste = session.query(ListeCourses).filter(ListeCourses.id == id_ressource).first()
                if not liste:
                    raise HTTPException(status_code=404, detail="Liste non trouvée")
                titre = f"Liste de courses: {liste.nom}"
                contenu = titre

            elif type_export == "planning":
                titre = "Planning de la semaine"
                contenu = titre

            elif type_export == "recette":
                from src.core.models import Recette

                if not id_ressource:
                    raise HTTPException(status_code=422, detail="id_ressource requis pour recette")
                recette = session.query(Recette).filter(Recette.id == id_ressource).first()
                if not recette:
                    raise HTTPException(status_code=404, detail="Recette non trouvée")
                titre = f"Recette: {recette.nom}"
                contenu = titre

            elif type_export == "budget":
                titre = "Budget mensuel"
                contenu = titre

            else:
                raise HTTPException(
                    status_code=422,
                    detail=f"Type d'export non supporté: {type_export}",
                )

            return contenu, titre

    contenu, titre = await executer_async(_generate)

    # Retourner comme texte pour l'instant (ServiceRapportsPDF sera branché plus tard)
    buffer = io.BytesIO(contenu.encode("utf-8"))
    return StreamingResponse(
        buffer,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{titre}.txt"',
        },
    )

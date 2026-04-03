"""
Routes API pour le tableau de bord — section widgets.

Endpoints : documents expirants, actions rapides widgets et historique.
"""

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/dashboard", tags=["Tableau de bord — Widgets"])


@router.get(
    "/documents-expirants",
    responses=REPONSES_LISTE,
    summary="Documents famille expirants ou expirés",
)
@gerer_exception_api
async def obtenir_documents_expirants(
    jours_horizon: int = 60,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les documents famille expirants (widget dashboard B8).

    Inclut les documents déjà expirés et ceux qui expirent dans les N prochains jours.
    """

    def _query():
        with executer_avec_session() as session:
            from src.core.models import DocumentFamille

            aujourd_hui = date.today()
            limite = aujourd_hui + timedelta(days=jours_horizon)

            documents = (
                session.query(DocumentFamille)
                .filter(
                    DocumentFamille.date_expiration.isnot(None),
                    DocumentFamille.actif.is_(True),
                    DocumentFamille.date_expiration <= limite,
                )
                .order_by(DocumentFamille.date_expiration.asc())
                .all()
            )

            items = []
            nb_expires = 0
            nb_bientot = 0

            for doc in documents:
                jours_restants = (doc.date_expiration - aujourd_hui).days
                est_expire = jours_restants < 0

                if est_expire:
                    nb_expires += 1
                    severite = "danger"
                elif jours_restants <= 7:
                    nb_bientot += 1
                    severite = "danger"
                elif jours_restants <= 30:
                    nb_bientot += 1
                    severite = "warning"
                else:
                    severite = "info"

                items.append({
                    "id": doc.id,
                    "titre": doc.titre,
                    "categorie": doc.categorie,
                    "membre_famille": doc.membre_famille,
                    "date_expiration": doc.date_expiration.isoformat(),
                    "jours_restants": jours_restants,
                    "est_expire": est_expire,
                    "severite": severite,
                })

            return {
                "items": items,
                "total": len(items),
                "nb_expires": nb_expires,
                "nb_bientot": nb_bientot,
                "message": (
                    f"{nb_expires} document(s) expiré(s), "
                    f"{nb_bientot} expirent bientôt."
                ),
            }

    return await executer_async(_query)


class WidgetActionRequest(BaseModel):
    widget_id: str = Field(..., description="Identifiant du widget (ex: 'courses', 'planning')")
    action: str = Field(..., description="Type d'action (ex: 'marquer_vu', 'snooze', 'refresh')")
    donnees: dict[str, Any] = Field(default_factory=dict, description="Données optionnelles de l'action")


@router.post(
    "/widgets/action",
    responses=REPONSES_LISTE,
    summary="Enregistrer une action rapide d'un widget",
)
@gerer_exception_api
async def enregistrer_action_widget(
    payload: WidgetActionRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Publie un événement dashboard.widget.action_rapide depuis le frontend.

    Permet au dashboard de signaler qu'un utilisateur a interagi avec un widget
    (marquer comme vu, snoozer une alerte, déclencher un refresh, etc.).
    """
    try:
        from src.services.core.events import obtenir_bus

        obtenir_bus().emettre(
            "dashboard.widget.action_rapide",
            {
                "action": payload.action,
                "widget_id": payload.widget_id,
                "donnees": payload.donnees,
            },
            source="dashboard",
        )
    except Exception:
        pass

    return {
        "widget_id": payload.widget_id,
        "action": payload.action,
        "statut": "ok",
    }


@router.get(
    "/widgets/actions",
    responses=REPONSES_LISTE,
    summary="Historique des actions rapides widgets",
)
@gerer_exception_api
async def obtenir_historique_actions_widgets(
    limite: int = Query(10, ge=1, le=50),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les dernières actions widgets émises sur l'Event Bus dashboard."""

    def _query() -> dict[str, Any]:
        from src.services.core.events import obtenir_bus

        events = obtenir_bus().obtenir_historique(
            type_evenement="dashboard.widget.action_rapide",
            limite=limite,
        )
        items = [
            {
                "event_id": event.event_id,
                "type": event.type,
                "source": event.source,
                "timestamp": event.timestamp.isoformat(),
                "widget_id": (event.data or {}).get("widget_id"),
                "action": (event.data or {}).get("action"),
                "donnees": (event.data or {}).get("donnees", {}),
            }
            for event in reversed(events)
        ]
        return {"items": items, "total": len(items)}

    return await executer_async(_query)

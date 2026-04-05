"""
Routes pour les webhooks sortants.

Endpoints:
- POST   /api/v1/webhooks           : CrÃ©er un abonnement webhook
- GET    /api/v1/webhooks           : Lister les webhooks de l'utilisateur
- GET    /api/v1/webhooks/{id}      : DÃ©tail d'un webhook
- PUT    /api/v1/webhooks/{id}      : Modifier un webhook
- DELETE /api/v1/webhooks/{id}      : Supprimer un webhook
- POST   /api/v1/webhooks/{id}/test : Tester la connectivitÃ© d'un webhook
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import require_auth
from src.api.schemas.errors import (
    REPONSES_AUTH,
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
)
from src.api.schemas.webhooks import (
    WebhookCreate,
    WebhookListResponse,
    WebhookResponse,
    WebhookTestResponse,
    WebhookUpdate,
)
from src.api.utils import gerer_exception_api
from src.services.integrations.webhooks import obtenir_webhook_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["Webhooks"],
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENDPOINTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=201,
    responses=REPONSES_CRUD_CREATION,
    summary="CrÃ©er un webhook",
    description="CrÃ©e un nouvel abonnement webhook. Un secret HMAC-SHA256 est gÃ©nÃ©rÃ© automatiquement.",
)
@gerer_exception_api
async def creer_webhook(
    donnees: WebhookCreate,
    current_user: dict = Depends(require_auth),
):
    """Crée un webhook et retourne les données incluant le secret."""
    service = obtenir_webhook_service()
    result = service.creer_webhook(
        url=str(donnees.url),
        evenements=donnees.evenements,
        user_id=current_user.get("id"),
        description=donnees.description,
    )

    return result


@router.get(
    "",
    response_model=WebhookListResponse,
    responses=REPONSES_AUTH,
    summary="Lister mes webhooks",
    description="Retourne tous les webhooks de l'utilisateur authentifiÃ©.",
)
@gerer_exception_api
async def lister_webhooks(
    current_user: dict = Depends(require_auth),
):
    """Liste les webhooks de l'utilisateur courant."""
    service = obtenir_webhook_service()
    items = service.lister_webhooks(user_id=current_user.get("id"))

    return WebhookListResponse(items=items, total=len(items))


@router.get(
    "/{webhook_id}",
    response_model=WebhookResponse,
    responses=REPONSES_CRUD_LECTURE,
    summary="DÃ©tail d'un webhook",
    description="Retourne les informations d'un webhook spÃ©cifique.",
)
@gerer_exception_api
async def obtenir_webhook(
    webhook_id: int,
    current_user: dict = Depends(require_auth),
):
    """RÃ©cupÃ¨re un webhook par son ID."""
    service = obtenir_webhook_service()
    webhook = service.obtenir_webhook(webhook_id)

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook non trouvÃ©")

    return webhook


@router.put(
    "/{webhook_id}",
    response_model=WebhookResponse,
    responses=REPONSES_CRUD_ECRITURE,
    summary="Modifier un webhook",
    description="Met Ã  jour les propriÃ©tÃ©s d'un webhook existant.",
)
@gerer_exception_api
async def modifier_webhook(
    webhook_id: int,
    maj: WebhookUpdate,
    current_user: dict = Depends(require_auth),
):
    """Modifie un webhook existant."""
    update_data = maj.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="Aucun champ Ã  mettre Ã  jour fourni")

    # Convertir HttpUrl en str si prÃ©sent
    if "url" in update_data and update_data["url"] is not None:
        update_data["url"] = str(update_data["url"])

    service = obtenir_webhook_service()
    result = service.modifier_webhook(webhook_id, **update_data)

    if not result:
        raise HTTPException(status_code=404, detail="Webhook non trouvÃ©")

    return result


@router.delete(
    "/{webhook_id}",
    status_code=204,
    responses=REPONSES_CRUD_SUPPRESSION,
    summary="Supprimer un webhook",
    description="Supprime dÃ©finitivement un abonnement webhook.",
)
@gerer_exception_api
async def supprimer_webhook(
    webhook_id: int,
    current_user: dict = Depends(require_auth),
):
    """Supprime un webhook."""
    service = obtenir_webhook_service()
    deleted = service.supprimer_webhook(webhook_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Webhook non trouvÃ©")

    return None


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookTestResponse,
    responses=REPONSES_CRUD_LECTURE,
    summary="Tester un webhook",
    description="Envoie un ping de test au webhook pour vÃ©rifier sa connectivitÃ©.",
)
@gerer_exception_api
async def tester_webhook(
    webhook_id: int,
    current_user: dict = Depends(require_auth),
):
    """Envoie un payload de test au webhook."""
    service = obtenir_webhook_service()
    result = service.tester_webhook(webhook_id)

    if result.get("error") == "Webhook non trouvÃ©":
        raise HTTPException(status_code=404, detail="Webhook non trouvÃ©")

    return result


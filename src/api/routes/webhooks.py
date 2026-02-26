"""
Routes pour les webhooks sortants.

Endpoints:
- POST   /api/v1/webhooks           : Créer un abonnement webhook
- GET    /api/v1/webhooks           : Lister les webhooks de l'utilisateur
- GET    /api/v1/webhooks/{id}      : Détail d'un webhook
- PUT    /api/v1/webhooks/{id}      : Modifier un webhook
- DELETE /api/v1/webhooks/{id}      : Supprimer un webhook
- POST   /api/v1/webhooks/{id}/test : Tester la connectivité d'un webhook
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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["Webhooks"],
)


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=201,
    responses=REPONSES_CRUD_CREATION,
    summary="Créer un webhook",
    description="Crée un nouvel abonnement webhook. Un secret HMAC-SHA256 est généré automatiquement.",
)
@gerer_exception_api
async def creer_webhook(
    data: WebhookCreate,
    current_user: dict = Depends(require_auth),
):
    """Crée un webhook et retourne les données incluant le secret."""
    from src.services.webhooks import get_webhook_service

    service = get_webhook_service()
    result = service.creer_webhook(
        url=str(data.url),
        evenements=data.evenements,
        user_id=current_user.get("id"),
        description=data.description,
    )

    return result


@router.get(
    "",
    response_model=WebhookListResponse,
    responses=REPONSES_AUTH,
    summary="Lister mes webhooks",
    description="Retourne tous les webhooks de l'utilisateur authentifié.",
)
@gerer_exception_api
async def lister_webhooks(
    current_user: dict = Depends(require_auth),
):
    """Liste les webhooks de l'utilisateur courant."""
    from src.services.webhooks import get_webhook_service

    service = get_webhook_service()
    items = service.lister_webhooks(user_id=current_user.get("id"))

    return WebhookListResponse(items=items, total=len(items))


@router.get(
    "/{webhook_id}",
    response_model=WebhookResponse,
    responses=REPONSES_CRUD_LECTURE,
    summary="Détail d'un webhook",
    description="Retourne les informations d'un webhook spécifique.",
)
@gerer_exception_api
async def obtenir_webhook(
    webhook_id: int,
    current_user: dict = Depends(require_auth),
):
    """Récupère un webhook par son ID."""
    from src.services.webhooks import get_webhook_service

    service = get_webhook_service()
    webhook = service.obtenir_webhook(webhook_id)

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook non trouvé")

    return webhook


@router.put(
    "/{webhook_id}",
    response_model=WebhookResponse,
    responses=REPONSES_CRUD_ECRITURE,
    summary="Modifier un webhook",
    description="Met à jour les propriétés d'un webhook existant.",
)
@gerer_exception_api
async def modifier_webhook(
    webhook_id: int,
    data: WebhookUpdate,
    current_user: dict = Depends(require_auth),
):
    """Modifie un webhook existant."""
    from src.services.webhooks import get_webhook_service

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour fourni")

    # Convertir HttpUrl en str si présent
    if "url" in update_data and update_data["url"] is not None:
        update_data["url"] = str(update_data["url"])

    service = get_webhook_service()
    result = service.modifier_webhook(webhook_id, **update_data)

    if not result:
        raise HTTPException(status_code=404, detail="Webhook non trouvé")

    return result


@router.delete(
    "/{webhook_id}",
    status_code=204,
    responses=REPONSES_CRUD_SUPPRESSION,
    summary="Supprimer un webhook",
    description="Supprime définitivement un abonnement webhook.",
)
@gerer_exception_api
async def supprimer_webhook(
    webhook_id: int,
    current_user: dict = Depends(require_auth),
):
    """Supprime un webhook."""
    from src.services.webhooks import get_webhook_service

    service = get_webhook_service()
    deleted = service.supprimer_webhook(webhook_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Webhook non trouvé")

    return None


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookTestResponse,
    responses=REPONSES_CRUD_LECTURE,
    summary="Tester un webhook",
    description="Envoie un ping de test au webhook pour vérifier sa connectivité.",
)
@gerer_exception_api
async def tester_webhook(
    webhook_id: int,
    current_user: dict = Depends(require_auth),
):
    """Envoie un payload de test au webhook."""
    from src.services.webhooks import get_webhook_service

    service = get_webhook_service()
    result = service.tester_webhook(webhook_id)

    if result.get("error") == "Webhook non trouvé":
        raise HTTPException(status_code=404, detail="Webhook non trouvé")

    return result

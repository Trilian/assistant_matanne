"""Routes d'innovations orientées pilotage, apprentissage et proactivité."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, Query

from src.api.dependencies import require_auth
from src.api.routes.innovations_common import (
    RESPONSES_IA_TYPED,
    creer_router_innovations,
    get_innovations_service,
)
from src.api.schemas.fonctionnalites_avancees import (
    AlertesContextuellesResponse,
    ApprentissageHabitudesResponse,
    ApprentissagePreferencesResponse,
    InsightsQuotidiensResponse,
    MeteoContextuelleResponse,
    ModePiloteAutomatiqueResponse,
    ModePiloteConfigurationRequest,
    TelegramConversationnelResponse,
)
from src.api.utils import gerer_exception_api

router = creer_router_innovations()


@router.get(
    "/apprentissage-habitudes",
    response_model=ApprentissageHabitudesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Apprentissage continu habitudes",
)
@gerer_exception_api
async def apprentissage_habitudes(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.apprendre_habitudes_utilisateur()
    return result or ApprentissageHabitudesResponse()


@router.get(
    "/alertes-contextuelles",
    response_model=AlertesContextuellesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Alertes intelligentes contextuelles",
)
@gerer_exception_api
async def alertes_contextuelles(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.generer_alertes_contextuelles()
    return result or AlertesContextuellesResponse()


@router.get(
    "/mode-pilote",
    response_model=ModePiloteAutomatiqueResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Mode pilote automatique",
)
@gerer_exception_api
async def mode_pilote(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id_raw = user.get("id")
    user_id = int(user_id_raw) if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit() else None
    result = service.obtenir_mode_pilote_automatique(user_id=user_id)
    return result or ModePiloteAutomatiqueResponse()


@router.post(
    "/mode-pilote/config",
    response_model=ModePiloteAutomatiqueResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Config mode pilote automatique",
)
@gerer_exception_api
async def configurer_mode_pilote(
    body: ModePiloteConfigurationRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id_raw = user.get("id")
    user_id = int(user_id_raw) if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit() else None
    result = service.configurer_mode_pilote_automatique(
        user_id=user_id,
        actif=body.actif,
        niveau_autonomie=body.niveau_autonomie,
    )
    return result or ModePiloteAutomatiqueResponse(actif=body.actif)


@router.get(
    "/insights-quotidiens",
    response_model=InsightsQuotidiensResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Insights IA proactifs quotidiens",
)
@gerer_exception_api
async def insights_quotidiens(
    limite: int = Query(2, ge=1, le=2, description="1 ou 2 insights maximum par jour"),
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.generer_insights_quotidiens(limite=limite)
    return result or InsightsQuotidiensResponse(limite_journaliere=limite)


@router.get(
    "/meteo-contextuelle",
    response_model=MeteoContextuelleResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Meteo contextuelle cross-module",
)
@gerer_exception_api
async def meteo_contextuelle(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.analyser_meteo_contextuelle()
    return result or MeteoContextuelleResponse()


@router.get(
    "/preferences-apprises",
    response_model=ApprentissagePreferencesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Apprentissage des preferences",
)
@gerer_exception_api
async def preferences_apprises(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id = str(user.get("id") or "")
    result = service.analyser_preferences_apprises(user_id=user_id)
    return result or ApprentissagePreferencesResponse()


@router.get(
    "/telegram-conversationnel",
    response_model=TelegramConversationnelResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Telegram conversationnel",
)
@gerer_exception_api
async def telegram_conversationnel(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.obtenir_capacites_telegram_conversationnelles()
    return result or TelegramConversationnelResponse()

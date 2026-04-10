"""Routes admin — IA (métriques, console)."""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from typing import Any

from fastapi import Depends, HTTPException

from src.api.dependencies import require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    AdminAIConsoleRequest,
    _journaliser_action_admin,
    router,
)

logger = logging.getLogger(__name__)


@router.get(
    "/ia/metrics",
    responses=REPONSES_AUTH_ADMIN,
    summary="Métriques IA avancées",
    description="Retourne les métriques IA consolidées (appels, tokens, cache, coût estimé).",
)
@gerer_exception_api
async def lire_metriques_ia_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import get_metrics
    from src.core.ai import RateLimitIA
    from src.core.ai.cache import CacheIA
    from src.core.monitoring.collector import collecteur

    metrics = get_metrics()
    ai_metrics = (metrics.get("ai") or {}) if isinstance(metrics, dict) else {}
    tokens_utilises = int(ai_metrics.get("tokens_used", 0) or 0)
    cout_1k_tokens = float(os.getenv("IA_COST_EUR_1K_TOKENS", "0.002"))
    cout_estime = round((tokens_utilises / 1000.0) * cout_1k_tokens, 4)

    collecteur_ia = collecteur.filtrer_par_prefixe("ia.")
    return {
        "generated_at": datetime.now().isoformat(),
        "api": ai_metrics,
        "rate_limit": RateLimitIA.obtenir_statistiques(),
        "cache": CacheIA.obtenir_statistiques(),
        "monitoring": collecteur_ia,
        "cout_estime_eur": cout_estime,
        "cout_eur_1k_tokens": cout_1k_tokens,
    }


@router.post(
    "/ai/console",
    responses=REPONSES_AUTH_ADMIN,
    summary="Console IA admin",
    description="Exécute un prompt IA admin et retourne la réponse brute.",
)
@gerer_exception_api
async def console_ia_admin(
    body: AdminAIConsoleRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Endpoint de test prompt/réponse brute pour l'admin."""
    from src.core.ai import obtenir_client_ia

    prompt = body.prompt.strip()
    if len(prompt) < 3:
        raise HTTPException(
            status_code=422, detail="Le prompt doit contenir au moins 3 caractères."
        )

    start = time.perf_counter()
    client = obtenir_client_ia()
    reponse = await client.appeler(
        prompt=prompt,
        prompt_systeme=body.prompt_systeme,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        utiliser_cache=body.utiliser_cache,
    )
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    _journaliser_action_admin(
        action="admin.ai.console",
        entite_type="ai",
        utilisateur_id=str(user.get("id", "admin")),
        details={"duration_ms": duration_ms},
    )
    return {
        "status": "ok",
        "duration_ms": duration_ms,
        "model": getattr(client, "modele", "unknown"),
        "response": reponse,
    }

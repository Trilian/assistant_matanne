"""Routes admin — Audit et Events."""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text

from src.api.dependencies import require_role
from src.api.schemas.admin import (
    AdminAuditLogsResponse,
    AdminAuditStatsResponse,
    AdminEventsListResponse,
)
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    EventBusReplayRequest,
    EventBusTriggerRequest,
    _construire_pdf_audit,
    _journaliser_action_admin,
    _verifier_limite_admin,
    router,
)

logger = logging.getLogger(__name__)

@router.get(
    "/audit-logs",
    response_model=AdminAuditLogsResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les logs d'audit",
    description="Retourne les logs d'audit paginés avec filtres optionnels. Nécessite le rôle admin.",
)
@gerer_exception_api
async def lister_audit_logs(
    page: int = Query(1, ge=1),
    par_page: int = Query(50, ge=1, le=200),
    action: str | None = Query(None, description="Filtrer par type d'action"),
    entite_type: str | None = Query(None, description="Filtrer par type d'entité"),
    depuis: datetime | None = Query(None, description="Date de début (ISO 8601)"),
    jusqu_a: datetime | None = Query(None, description="Date de fin (ISO 8601)"),
    user: dict[str, Any] = Depends(require_role("admin")),
):
    """Retourne les logs d'audit paginés avec filtres."""
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()
    resultat = service.consulter(
        action=action,
        entite_type=entite_type,
        depuis=depuis,
        jusqu_a=jusqu_a,
        limite=par_page,
        page=page,
    )

    return {
        "items": [e.model_dump() for e in resultat.entrees],
        "total": resultat.total,
        "page": resultat.page,
        "par_page": resultat.par_page,
        "pages_totales": max(1, (resultat.total + par_page - 1) // par_page),
    }


@router.get(
    "/security-logs",
    response_model=AdminAuditLogsResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les événements de sécurité",
    description="Retourne les logs de sécurité (auth, rate limiting, admin) avec filtres.",
)
@gerer_exception_api
async def lister_logs_securite(
    page: int = Query(1, ge=1),
    par_page: int = Query(20, ge=1, le=200),
    event_type: str | None = Query(None, description="Filtrer par type d'événement"),
    depuis: datetime | None = Query(None, description="Date de début (ISO 8601)"),
    jusqu_a: datetime | None = Query(None, description="Date de fin (ISO 8601)"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Expose un flux dédié sécurité pour le dashboard admin."""
    from sqlalchemy import text

    from src.api.utils import executer_avec_session

    offset = (page - 1) * par_page
    conditions: list[str] = ["1=1"]
    params: dict[str, Any] = {"limit": par_page, "offset": offset}

    if event_type:
        conditions.append("event_type = :event_type")
        params["event_type"] = event_type
    else:
        conditions.append("(event_type LIKE 'auth.%' OR event_type LIKE 'rate_limit.%' OR event_type LIKE 'admin.%')")

    if depuis:
        conditions.append("created_at >= :depuis")
        params["depuis"] = depuis
    if jusqu_a:
        conditions.append("created_at <= :jusqu_a")
        params["jusqu_a"] = jusqu_a

    where_clause = " AND ".join(conditions)

    with executer_avec_session() as session:
        total = int(
            session.execute(
                text(f"SELECT COUNT(*) FROM logs_securite WHERE {where_clause}"),
                params,
            ).scalar()
            or 0
        )

        rows = session.execute(
            text(
                f"""
                SELECT id, created_at, event_type, user_id, ip, user_agent, details
                FROM logs_securite
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()

    items = [
        {
            "id": int(r["id"]),
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            "event_type": r["event_type"],
            "user_id": r["user_id"],
            "ip": r["ip"],
            "user_agent": r["user_agent"],
            "source": "security",
            "details": r["details"] or {},
        }
        for r in rows
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "par_page": par_page,
        "pages_totales": max(1, (total + par_page - 1) // par_page),
    }


@router.get(
    "/audit-stats",
    response_model=AdminAuditStatsResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Statistiques d'audit",
    description="Statistiques agrégées du journal d'audit.",
)
@gerer_exception_api
async def statistiques_audit(
    user: dict[str, Any] = Depends(require_role("admin")),
):
    """Retourne les statistiques d'audit (compteurs par action, entité, source)."""
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()
    return service.statistiques()


@router.get(
    "/audit-export",
    responses=REPONSES_AUTH_ADMIN,
    summary="Export CSV des logs",
    description="Exporte les logs d'audit au format CSV.",
)
@gerer_exception_api
async def exporter_audit_csv(
    action: str | None = Query(None),
    entite_type: str | None = Query(None),
    depuis: datetime | None = Query(None),
    jusqu_a: datetime | None = Query(None),
    user: dict[str, Any] = Depends(require_role("admin")),
):
    """Export CSV des logs d'audit."""
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()
    resultat = service.consulter(
        action=action,
        entite_type=entite_type,
        depuis=depuis,
        jusqu_a=jusqu_a,
        limite=10000,
        page=1,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Action", "Source", "Utilisateur", "Entité", "ID Entité", "Détails"])

    for e in resultat.entrees:
        writer.writerow([
            e.timestamp.isoformat(),
            e.action,
            e.source,
            e.utilisateur_id or "",
            e.entite_type,
            str(e.entite_id) if e.entite_id else "",
            str(e.details) if e.details else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-logs.csv"},
    )


@router.get(
    "/audit-export/pdf",
    responses=REPONSES_AUTH_ADMIN,
    summary="Export PDF des logs d'audit",
    description="Exporte les logs d'audit au format PDF.",
)
@gerer_exception_api
async def exporter_audit_pdf(
    action: str | None = Query(None),
    entite_type: str | None = Query(None),
    depuis: datetime | None = Query(None),
    jusqu_a: datetime | None = Query(None),
    user: dict[str, Any] = Depends(require_role("admin")),
):
    """Export PDF des logs d'audit."""
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()
    resultat = service.consulter(
        action=action,
        entite_type=entite_type,
        depuis=depuis,
        jusqu_a=jusqu_a,
        limite=2000,
        page=1,
    )

    pdf_bytes = _construire_pdf_audit(
        list(resultat.entrees),
        {
            "action": action,
            "entite_type": entite_type,
            "depuis": depuis.isoformat() if depuis else None,
            "jusqu_a": jusqu_a.isoformat() if jusqu_a else None,
        },
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=audit-logs.pdf"},
    )


@router.get(
    "/events",
    response_model=AdminEventsListResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Consulter le bus d'événements",
    description="Expose les métriques et l'historique récent du bus d'événements domaine.",
)
@gerer_exception_api
async def lire_evenements_admin(
    limite: int = Query(30, ge=1, le=200),
    type_evenement: str | None = Query(None, description="Filtrer sur un type exact"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    historique = bus.obtenir_historique(type_evenement=type_evenement, limite=limite)
    items = [
        {
            "event_id": event.event_id,
            "type": event.type,
            "source": event.source,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "data": event.data or {},
        }
        for event in historique
    ]
    return {
        "metriques": bus.obtenir_metriques(),
        "items": items,
        "total": len(items),
    }


@router.post(
    "/events/trigger",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Déclencher un événement domaine",
    description="Émet manuellement un événement sur le bus pour tester les subscribers.",
)
@gerer_exception_api
async def declencher_evenement_admin(
    body: EventBusTriggerRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    handlers_notifies = bus.emettre(
        type_evenement=body.type_evenement,
        data=body.payload,
        source=body.source,
    )
    _journaliser_action_admin(
        action="admin.events.trigger",
        entite_type="event_bus",
        utilisateur_id=str(user.get("id", "admin")),
        details={
            "type_evenement": body.type_evenement,
            "source": body.source,
            "handlers_notifies": handlers_notifies,
        },
    )
    return {
        "status": "ok",
        "type_evenement": body.type_evenement,
        "handlers_notifies": handlers_notifies,
    }


@router.post(
    "/events/replay",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Rejouer un événement passé",
    description="Recharge l'historique DB du bus puis ré-émet un ou plusieurs événements.",
)
@gerer_exception_api
async def rejouer_evenement_admin(
    body: EventBusReplayRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    limite = max(1, min(50, int(body.limite or 1)))
    events = bus.rejouer_historique_db(type_evenement=body.type_evenement, limite=200)

    if body.event_id:
        events = [e for e in events if e.event_id == body.event_id]

    if not events:
        raise HTTPException(status_code=404, detail="Aucun événement trouvé pour replay")

    a_rejouer = events[-limite:]
    total_handlers = 0
    replayes: list[dict[str, Any]] = []

    for event in a_rejouer:
        notified = bus.emettre(
            type_evenement=event.type,
            data=event.data,
            source=body.source,
        )
        total_handlers += notified
        replayes.append(
            {
                "event_id": event.event_id,
                "type": event.type,
                "handlers_notifies": notified,
            }
        )

    _journaliser_action_admin(
        action="admin.events.replay",
        entite_type="event_bus",
        utilisateur_id=str(user.get("id", "admin")),
        details={
            "event_id": body.event_id,
            "type_evenement": body.type_evenement,
            "limite": limite,
            "replayes": len(replayes),
            "handlers_notifies": total_handlers,
        },
    )

    return {
        "status": "ok",
        "replayes": replayes,
        "total": len(replayes),
        "handlers_notifies": total_handlers,
    }



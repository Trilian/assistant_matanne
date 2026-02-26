"""
Routes API pour les calendriers.

Endpoints pour:
- Calendriers externes synchronisés
- Événements de calendrier
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.pagination import appliquer_cursor_filter, construire_reponse_cursor, decoder_cursor
from src.api.schemas.errors import REPONSES_CRUD_LECTURE, REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/calendriers", tags=["Calendriers"])


# ═══════════════════════════════════════════════════════════
# CALENDRIERS EXTERNES
# ═══════════════════════════════════════════════════════════


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_calendriers(
    provider: str | None = Query(
        None, description="Filtrer par fournisseur (google, apple, outlook, ical_url)"
    ),
    enabled: bool | None = Query(None, description="Filtrer par statut activé"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les calendriers externes synchronisés."""
    from src.core.models import CalendrierExterne

    def _query():
        with executer_avec_session() as session:
            query = session.query(CalendrierExterne)

            if provider:
                query = query.filter(CalendrierExterne.provider == provider)
            if enabled is not None:
                query = query.filter(CalendrierExterne.enabled == enabled)

            calendriers = query.order_by(CalendrierExterne.nom).all()

            return {
                "items": [
                    {
                        "id": c.id,
                        "provider": c.provider,
                        "nom": c.nom,
                        "enabled": c.enabled,
                        "sync_interval_minutes": c.sync_interval_minutes,
                        "last_sync": c.last_sync.isoformat() if c.last_sync else None,
                        "sync_direction": c.sync_direction,
                        "evenements_count": len(c.evenements) if c.evenements else 0,
                    }
                    for c in calendriers
                ],
            }

    return await executer_async(_query)


@router.get("/{calendrier_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_calendrier(
    calendrier_id: int,
    user: dict[str, Any] = Depends(require_auth),
):
    """Récupère un calendrier externe par son ID."""
    from src.core.models import CalendrierExterne

    def _query():
        with executer_avec_session() as session:
            calendrier = (
                session.query(CalendrierExterne)
                .filter(CalendrierExterne.id == calendrier_id)
                .first()
            )
            if not calendrier:
                raise HTTPException(status_code=404, detail="Calendrier non trouvé")

            return {
                "id": calendrier.id,
                "provider": calendrier.provider,
                "nom": calendrier.nom,
                "url": calendrier.url,
                "enabled": calendrier.enabled,
                "sync_interval_minutes": calendrier.sync_interval_minutes,
                "last_sync": calendrier.last_sync.isoformat() if calendrier.last_sync else None,
                "sync_direction": calendrier.sync_direction,
                "created_at": calendrier.cree_le.isoformat() if calendrier.cree_le else None,
                "updated_at": calendrier.modifie_le.isoformat() if calendrier.modifie_le else None,
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


@router.get("/evenements", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_evenements(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    calendrier_id: int | None = Query(None, description="Filtrer par calendrier source"),
    date_debut: datetime | None = Query(None, description="Date minimum (ISO 8601)"),
    date_fin: datetime | None = Query(None, description="Date maximum (ISO 8601)"),
    all_day: bool | None = Query(None, description="Filtrer événements journée entière"),
    cursor: str | None = Query(None, description="Curseur pour pagination cursor-based"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les événements de calendrier.

    Supporte pagination offset ou cursor-based pour grandes collections.
    """
    from src.core.models import EvenementCalendrier

    def _query():
        with executer_avec_session() as session:
            query = session.query(EvenementCalendrier)

            if calendrier_id:
                query = query.filter(EvenementCalendrier.source_calendrier_id == calendrier_id)
            if date_debut:
                query = query.filter(EvenementCalendrier.date_debut >= date_debut)
            if date_fin:
                query = query.filter(EvenementCalendrier.date_debut <= date_fin)
            if all_day is not None:
                query = query.filter(EvenementCalendrier.all_day == all_day)

            query = query.order_by(EvenementCalendrier.date_debut.asc())

            # Pagination cursor-based
            if cursor:
                cursor_params = decoder_cursor(cursor)
                query = appliquer_cursor_filter(query, cursor_params, EvenementCalendrier)
                items = query.limit(page_size + 1).all()
                return construire_reponse_cursor(items, page_size, cursor_field="id")

            # Pagination offset
            total = query.count()
            items = query.offset((page - 1) * page_size).limit(page_size).all()

            return {
                "items": [
                    {
                        "id": e.id,
                        "uid": e.uid,
                        "titre": e.titre,
                        "description": e.description,
                        "date_debut": e.date_debut.isoformat(),
                        "date_fin": e.date_fin.isoformat() if e.date_fin else None,
                        "lieu": e.lieu,
                        "all_day": e.all_day,
                        "recurrence_rule": e.recurrence_rule,
                        "rappel_minutes": e.rappel_minutes,
                        "source_calendrier_id": e.source_calendrier_id,
                    }
                    for e in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/evenements/{evenement_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_evenement(
    evenement_id: int,
    user: dict[str, Any] = Depends(require_auth),
):
    """Récupère un événement par son ID."""
    from src.core.models import EvenementCalendrier

    def _query():
        with executer_avec_session() as session:
            evenement = (
                session.query(EvenementCalendrier)
                .filter(EvenementCalendrier.id == evenement_id)
                .first()
            )
            if not evenement:
                raise HTTPException(status_code=404, detail="Événement non trouvé")

            return {
                "id": evenement.id,
                "uid": evenement.uid,
                "titre": evenement.titre,
                "description": evenement.description,
                "date_debut": evenement.date_debut.isoformat(),
                "date_fin": evenement.date_fin.isoformat() if evenement.date_fin else None,
                "lieu": evenement.lieu,
                "all_day": evenement.all_day,
                "recurrence_rule": evenement.recurrence_rule,
                "rappel_minutes": evenement.rappel_minutes,
                "source_calendrier_id": evenement.source_calendrier_id,
                "created_at": evenement.cree_le.isoformat() if evenement.cree_le else None,
                "updated_at": evenement.modifie_le.isoformat() if evenement.modifie_le else None,
            }

    return await executer_async(_query)


@router.get("/evenements/aujourd-hui", responses=REPONSES_LISTE)
@gerer_exception_api
async def evenements_aujourdhui(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère les événements du jour."""
    from datetime import timedelta

    from src.core.models import EvenementCalendrier

    def _query():
        with executer_avec_session() as session:
            now = datetime.now()
            debut_jour = now.replace(hour=0, minute=0, second=0, microsecond=0)
            fin_jour = debut_jour + timedelta(days=1)

            evenements = (
                session.query(EvenementCalendrier)
                .filter(
                    EvenementCalendrier.date_debut >= debut_jour,
                    EvenementCalendrier.date_debut < fin_jour,
                )
                .order_by(EvenementCalendrier.date_debut.asc())
                .all()
            )

            return {
                "date": now.date().isoformat(),
                "items": [
                    {
                        "id": e.id,
                        "titre": e.titre,
                        "date_debut": e.date_debut.isoformat(),
                        "date_fin": e.date_fin.isoformat() if e.date_fin else None,
                        "lieu": e.lieu,
                        "all_day": e.all_day,
                    }
                    for e in evenements
                ],
            }

    return await executer_async(_query)


@router.get("/evenements/semaine", responses=REPONSES_LISTE)
@gerer_exception_api
async def evenements_semaine(
    date_debut: datetime | None = Query(None, description="Date de début (défaut: lundi courant)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère les événements de la semaine."""
    from datetime import timedelta

    from src.core.models import EvenementCalendrier

    def _query():
        with executer_avec_session() as session:
            if not date_debut:
                now = datetime.now()
                debut = now - timedelta(days=now.weekday())
                debut = debut.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                debut = date_debut.replace(hour=0, minute=0, second=0, microsecond=0)

            fin = debut + timedelta(days=7)

            evenements = (
                session.query(EvenementCalendrier)
                .filter(
                    EvenementCalendrier.date_debut >= debut,
                    EvenementCalendrier.date_debut < fin,
                )
                .order_by(EvenementCalendrier.date_debut.asc())
                .all()
            )

            # Grouper par jour
            par_jour: dict[str, list] = {}
            for e in evenements:
                jour = e.date_debut.date().isoformat()
                if jour not in par_jour:
                    par_jour[jour] = []
                par_jour[jour].append(
                    {
                        "id": e.id,
                        "titre": e.titre,
                        "date_debut": e.date_debut.isoformat(),
                        "date_fin": e.date_fin.isoformat() if e.date_fin else None,
                        "lieu": e.lieu,
                        "all_day": e.all_day,
                    }
                )

            return {
                "date_debut": debut.isoformat(),
                "date_fin": fin.isoformat(),
                "par_jour": par_jour,
                "total": len(evenements),
            }

    return await executer_async(_query)

"""
Routes API pour les calendriers.

Endpoints pour:
- Calendriers externes synchronisÃ©s
- Ã‰vÃ©nements de calendrier
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.pagination import appliquer_cursor_filter, construire_reponse_cursor, decoder_cursor
from src.api.schemas import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.core.models import CalendrierExterne, EvenementCalendrier

router = APIRouter(prefix="/api/v1/calendriers", tags=["Calendriers"])


@router.get("/scolaire/zones", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_zones_calendrier_scolaire(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les zones scolaires supportees pour l'import automatique."""
    from src.services.famille.calendrier_scolaire import lister_zones_scolaires

    return {"zones": lister_zones_scolaires()}


@router.post("/scolaire/activer", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def activer_calendrier_scolaire_auto(
    zone: str = Query(..., description="Zone scolaire A, B ou C"),
    ajuster_planning: bool = Query(True, description="Creer/mettre a jour les evenements planning vacances"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Active l'import auto du calendrier scolaire pour une zone."""
    from src.services.famille.calendrier_scolaire import importer_calendrier_scolaire

    def _query() -> dict[str, Any]:
        return importer_calendrier_scolaire(
            user_id=user.get("id"),
            zone=zone,
            ajuster_planning=ajuster_planning,
        )

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALENDRIERS EXTERNES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_calendriers(
    provider: str | None = Query(
        None, description="Filtrer par fournisseur (google, apple, outlook, ical_url)"
    ),
    enabled: bool | None = Query(None, description="Filtrer par statut activÃ©"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les calendriers externes synchronisÃ©s."""

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
    """RÃ©cupÃ¨re un calendrier externe par son ID."""

    def _query():
        with executer_avec_session() as session:
            calendrier = (
                session.query(CalendrierExterne)
                .filter(CalendrierExterne.id == calendrier_id)
                .first()
            )
            if not calendrier:
                raise HTTPException(status_code=404, detail="Calendrier non trouvÃ©")

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


@router.post("", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_calendrier(
    nom: str = Query(..., description="Nom du calendrier"),
    provider: str = Query(..., description="Provider (ical_url)"),
    url: str | None = Query(None, description="URL iCal si provider=ical_url"),
    sync_interval_minutes: int = Query(60, description="Intervalle de sync en minutes"),
    sync_direction: str = Query("import", description="Direction sync: import, export, bidirectional"),
    user: dict[str, Any] = Depends(require_auth),
):
    """CrÃ©e un nouveau calendrier externe (iCal par URL)."""

    if provider not in ("ical_url", "google", "apple", "outlook"):
        raise HTTPException(status_code=422, detail=f"Provider non supportÃ©: {provider}")

    if provider == "ical_url" and not url:
        raise HTTPException(status_code=422, detail="url requis pour provider=ical_url")

    def _create():
        with executer_avec_session() as session:
            calendrier = CalendrierExterne(
                user_id=user["id"],
                provider=provider,
                nom=nom,
                url=url,
                enabled=True,
                sync_interval_minutes=sync_interval_minutes,
                sync_direction=sync_direction,
            )
            session.add(calendrier)
            session.commit()
            return {
                "id": calendrier.id,
                "provider": calendrier.provider,
                "nom": calendrier.nom,
                "url": calendrier.url,
                "enabled": calendrier.enabled,
                "sync_interval_minutes": calendrier.sync_interval_minutes,
                "sync_direction": calendrier.sync_direction,
                "last_sync": calendrier.last_sync.isoformat() if calendrier.last_sync else None,
            }

    return await executer_async(_create)


@router.delete("/{calendrier_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_calendrier(
    calendrier_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime un calendrier externe."""

    def _delete():
        with executer_avec_session() as session:
            deleted = (
                session.query(CalendrierExterne)
                .filter(
                    CalendrierExterne.id == calendrier_id,
                    CalendrierExterne.user_id == user["id"],
                )
                .delete()
            )
            session.commit()
            if not deleted:
                raise HTTPException(status_code=404, detail="Calendrier non trouvÃ©")
            return MessageResponse(message="Calendrier supprimÃ©", id=calendrier_id)

    return await executer_async(_delete)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ã‰VÃ‰NEMENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/evenements", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_evenements(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    calendrier_id: int | None = Query(None, description="Filtrer par calendrier source"),
    date_debut: datetime | None = Query(None, description="Date minimum (ISO 8601)"),
    date_fin: datetime | None = Query(None, description="Date maximum (ISO 8601)"),
    all_day: bool | None = Query(None, description="Filtrer Ã©vÃ©nements journÃ©e entiÃ¨re"),
    cursor: str | None = Query(None, description="Curseur pour pagination cursor-based"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les Ã©vÃ©nements de calendrier.

    Supporte pagination offset ou cursor-based pour grandes collections.
    """

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
    """RÃ©cupÃ¨re un Ã©vÃ©nement par son ID."""

    def _query():
        with executer_avec_session() as session:
            evenement = (
                session.query(EvenementCalendrier)
                .filter(EvenementCalendrier.id == evenement_id)
                .first()
            )
            if not evenement:
                raise HTTPException(status_code=404, detail="Ã‰vÃ©nement non trouvÃ©")

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
    """RÃ©cupÃ¨re les Ã©vÃ©nements du jour."""
    def _query():
        with executer_avec_session() as session:
            from datetime import timedelta

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
    date_debut: datetime | None = Query(None, description="Date de dÃ©but (dÃ©faut: lundi courant)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """RÃ©cupÃ¨re les Ã©vÃ©nements de la semaine."""

    def _query():
        with executer_avec_session() as session:
            from datetime import timedelta

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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GOOGLE CALENDAR â€” OAuth & Sync
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/google/auth-url")
@gerer_exception_api
async def obtenir_url_auth_google(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, str]:
    """GÃ©nÃ¨re l'URL d'autorisation OAuth2 Google Calendar."""
    from src.core.config import obtenir_parametres
    from src.services.famille.calendrier import obtenir_calendar_sync_service

    def _gen():
        params = obtenir_parametres()
        redirect_uri = params.GOOGLE_REDIRECT_URI
        if not redirect_uri:
            raise HTTPException(status_code=500, detail="GOOGLE_REDIRECT_URI non configurÃ©")
        service = obtenir_calendar_sync_service()
        url = service.get_google_auth_url(str(user["id"]), redirect_uri)
        return {"auth_url": url}

    return await executer_async(_gen)


@router.get("/google/callback")
@gerer_exception_api
async def callback_google(
    code: str = Query(..., description="Code d'autorisation OAuth2"),
    state: str = Query(..., description="User ID passÃ© via state"),
) -> dict[str, Any]:
    """Callback OAuth2 Google â€” Ã©change le code contre des tokens."""
    from src.core.config import obtenir_parametres
    from src.services.famille.calendrier import obtenir_calendar_sync_service

    def _exchange():
        params = obtenir_parametres()
        redirect_uri = params.GOOGLE_REDIRECT_URI
        service = obtenir_calendar_sync_service()
        config = service.handle_google_callback(state, code, redirect_uri)
        if not config:
            raise HTTPException(status_code=400, detail="Ã‰chec de l'authentification Google")
        return {
            "status": "connected",
            "provider": "google",
            "name": config.name,
        }

    return await executer_async(_exchange)


@router.post("/google/sync")
@gerer_exception_api
async def synchroniser_google(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©clenche une synchronisation manuelle avec Google Calendar."""
    from src.services.famille.calendrier import obtenir_calendar_sync_service

    def _sync():
        service = obtenir_calendar_sync_service()
        result = service.sync_google_calendar(str(user["id"]))
        return {
            "status": "success",
            "events_imported": result.imported if result else 0,
            "events_exported": result.exported if result else 0,
            "errors": result.errors if result else [],
        }

    return await executer_async(_sync)


@router.get("/google/status")
@gerer_exception_api
async def statut_google(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """VÃ©rifie l'Ã©tat de la connexion Google Calendar."""
    from src.core.models import CalendrierExterne

    def _query():
        with executer_avec_session() as session:
            cal = (
                session.query(CalendrierExterne)
                .filter(
                    CalendrierExterne.user_id == user["id"],
                    CalendrierExterne.provider == "google",
                )
                .first()
            )
            if not cal:
                return {"connected": False}
            return {
                "connected": True,
                "nom": cal.nom,
                "last_sync": cal.last_sync.isoformat() if cal.last_sync else None,
                "enabled": cal.enabled,
                "sync_direction": cal.sync_direction,
            }

    return await executer_async(_query)


@router.delete("/google/disconnect")
@gerer_exception_api
async def deconnecter_google(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, str]:
    """DÃ©connecte Google Calendar et supprime les tokens."""
    from src.core.models import CalendrierExterne

    def _delete():
        with executer_avec_session() as session:
            deleted = (
                session.query(CalendrierExterne)
                .filter(
                    CalendrierExterne.user_id == user["id"],
                    CalendrierExterne.provider == "google",
                )
                .delete()
            )
            session.commit()
            if not deleted:
                raise HTTPException(status_code=404, detail="Aucune connexion Google trouvÃ©e")
            return {"status": "disconnected"}

    return await executer_async(_delete)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GOOGLE CALENDAR â€” SYNC PLANNING REPAS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/google/sync-planning", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def synchroniser_planning_vers_google(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Pousse le planning repas actif de la semaine vers Google Calendar.

    Pour chaque repas du planning actif, crÃ©e un Ã©vÃ©nement Google Calendar
    avec l'heure appropriÃ©e (dÃ©jeuner 12h, dÃ®ner 19h, etc.).
    """
    from src.services.integrations.google_calendar import synchroniser_planning_google

    from src.core.models.planning import Planning, Repas
    from datetime import date, timedelta

    def _collect():
        with executer_avec_session() as session:
            aujourd_hui = date.today()
            debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
            fin_semaine = debut_semaine + timedelta(days=6)

            repas = (
                session.query(Repas)
                .join(Planning)
                .filter(
                    Planning.statut == "actif",
                    Repas.date_repas >= debut_semaine,
                    Repas.date_repas <= fin_semaine,
                )
                .all()
            )

            return [
                {
                    "date": r.date_repas.isoformat(),
                    "type_repas": r.type_repas,
                    "recette_nom": r.recette.nom if r.recette else r.notes or "Repas",
                    "notes": r.notes or "",
                }
                for r in repas
            ]

    repas_list = await executer_async(_collect)

    if not repas_list:
        return {"created": 0, "errors": [], "message": "Aucun repas Ã  synchroniser"}

    result = await synchroniser_planning_google(repas_list)
    return result


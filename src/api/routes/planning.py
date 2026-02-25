"""
Routes API pour le planning.

Gestion du planning de repas hebdomadaire : consultation, création,
modification et suppression de repas planifiés.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas import (
    MessageResponse,
    PlanningSemaineResponse,
    RepasCreate,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/planning", tags=["Planning"])


@router.get("/semaine", response_model=PlanningSemaineResponse)
@gerer_exception_api
async def obtenir_planning_semaine(
    date_debut: datetime | None = Query(
        None, description="Date de début de semaine (ISO 8601). Défaut: lundi courant"
    ),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Récupère le planning de repas de la semaine.

    Retourne tous les repas planifiés pour une semaine donnée, organisés
    par jour et type de repas (petit-déjeuner, déjeuner, dîner).

    Args:
        date_debut: Date de début (défaut: lundi de la semaine courante)

    Returns:
        Planning structuré par jour avec date_debut, date_fin et repas

    Example:
        ```
        GET /api/v1/planning/semaine?date_debut=2026-02-16

        Response:
        {
            "date_debut": "2026-02-16T00:00:00",
            "date_fin": "2026-02-23T00:00:00",
            "planning": {
                "2026-02-16": {
                    "dejeuner": {"id": 1, "recette_id": 42, "notes": null},
                    "diner": {"id": 2, "recette_id": 15, "notes": "Rapide"}
                }
            }
        }
        ```
    """
    from src.core.models import Repas

    if not date_debut:
        today = datetime.now(UTC)
        date_debut = today - timedelta(days=today.weekday())

    date_fin = date_debut + timedelta(days=7)

    def _query():
        with executer_avec_session() as session:
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas >= date_debut, Repas.date_repas < date_fin)
                .order_by(Repas.date_repas)
                .all()
            )

            planning = {}
            for r in repas:
                jour = r.date_repas.strftime("%Y-%m-%d")
                if jour not in planning:
                    planning[jour] = {}
                planning[jour][r.type_repas] = {
                    "id": r.id,
                    "recette_id": r.recette_id,
                    "notes": getattr(r, "notes", None),
                }

            return {
                "date_debut": date_debut.isoformat(),
                "date_fin": date_fin.isoformat(),
                "planning": planning,
            }

    return await executer_async(_query)


@router.post("/repas", response_model=MessageResponse)
@gerer_exception_api
async def creer_repas(repas: RepasCreate, user: dict[str, Any] = Depends(require_auth)):
    """
    Planifie un repas pour une date et un type donnés.

    Crée automatiquement le planning hebdomadaire s'il n'existe pas.
    Si un repas existe déjà pour la même date et le même type,
    il est mis à jour au lieu d'être dupliqué.

    Args:
        repas: Données du repas (date, type_repas, recette_id, notes)

    Returns:
        Message de confirmation avec l'ID du repas créé/mis à jour

    Raises:
        401: Non authentifié
        422: Données invalides

    Example:
        ```
        POST /api/v1/planning/repas
        Authorization: Bearer <token>

        Body:
        {
            "date": "2026-02-19",
            "type_repas": "diner",
            "recette_id": 42,
            "notes": "Préparer la veille"
        }

        Response:
        {"message": "Repas planifié", "id": 7}
        ```
    """
    from src.core.models import Planning, Repas

    def _create():
        with executer_avec_session() as session:
            # Récupérer ou créer un planning par défaut
            date_repas = repas.date.date() if hasattr(repas.date, "date") else repas.date

            # Chercher un planning existant pour cette date
            planning = (
                session.query(Planning)
                .filter(Planning.semaine_debut <= date_repas, Planning.semaine_fin >= date_repas)
                .first()
            )

            if not planning:
                # Créer un planning par défaut
                debut = date_repas - timedelta(days=date_repas.weekday())
                fin = debut + timedelta(days=6)
                planning = Planning(
                    nom=f"Semaine du {debut.strftime('%d/%m')}",
                    semaine_debut=debut,
                    semaine_fin=fin,
                    actif=True,
                )
                session.add(planning)
                session.flush()

            # Vérifier s'il existe déjà un repas pour cette date/type
            existing = (
                session.query(Repas)
                .filter(
                    Repas.date_repas == date_repas,
                    Repas.type_repas == repas.type_repas,
                    Repas.planning_id == planning.id,
                )
                .first()
            )

            if existing:
                # Mettre à jour
                existing.recette_id = repas.recette_id
                if hasattr(existing, "notes"):
                    existing.notes = repas.notes
                session.commit()
                return MessageResponse(message="Repas mis à jour", id=existing.id)

            # Créer
            db_repas = Repas(
                planning_id=planning.id,
                date_repas=date_repas,
                type_repas=repas.type_repas,
                recette_id=repas.recette_id,
            )
            session.add(db_repas)
            session.commit()

            return MessageResponse(message="Repas planifié", id=db_repas.id)

    return await executer_async(_create)


@router.put("/repas/{repas_id}", response_model=MessageResponse)
@gerer_exception_api
async def modifier_repas(
    repas_id: int, repas: RepasCreate, user: dict[str, Any] = Depends(require_auth)
):
    """
    Met à jour un repas planifié.

    Permet de changer la recette, le type de repas ou les notes
    d'un repas déjà planifié.

    Args:
        repas_id: ID du repas à modifier
        repas: Nouvelles données du repas

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Repas non trouvé

    Example:
        ```
        PUT /api/v1/planning/repas/7
        Authorization: Bearer <token>

        Body:
        {
            "date": "2026-02-19",
            "type_repas": "diner",
            "recette_id": 15,
            "notes": "Changement de dernière minute"
        }

        Response:
        {"message": "Repas mis à jour", "id": 7}
        ```
    """
    from src.core.models import Repas

    def _update():
        with executer_avec_session() as session:
            db_repas = session.query(Repas).filter(Repas.id == repas_id).first()

            if not db_repas:
                raise HTTPException(status_code=404, detail="Repas non trouvé")

            db_repas.type_repas = repas.type_repas
            db_repas.recette_id = repas.recette_id
            if hasattr(db_repas, "notes") and repas.notes:
                db_repas.notes = repas.notes

            session.commit()
            session.refresh(db_repas)

            return MessageResponse(message="Repas mis à jour", id=db_repas.id)

    return await executer_async(_update)


@router.delete("/repas/{repas_id}", response_model=MessageResponse)
@gerer_exception_api
async def supprimer_repas(repas_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    Supprime un repas planifié.

    Args:
        repas_id: ID du repas à supprimer

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Repas non trouvé

    Example:
        ```
        DELETE /api/v1/planning/repas/7
        Authorization: Bearer <token>

        Response:
        {"message": "Repas supprimé", "id": 7}
        ```
    """
    from src.core.models import Repas

    def _delete():
        with executer_avec_session() as session:
            repas = session.query(Repas).filter(Repas.id == repas_id).first()

            if not repas:
                raise HTTPException(status_code=404, detail="Repas non trouvé")

            session.delete(repas)
            session.commit()

            return MessageResponse(message="Repas supprimé", id=repas_id)

    return await executer_async(_delete)

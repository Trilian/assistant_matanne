"""
Routes API pour le planning.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import require_auth
from src.api.schemas import (
    MessageResponse,
    PlanningSemaineResponse,
    RepasCreate,
)
from src.api.utils import executer_avec_session

router = APIRouter(prefix="/api/v1/planning", tags=["Planning"])


@router.get("/semaine", response_model=PlanningSemaineResponse)
async def get_planning_semaine(
    date_debut: datetime | None = None,
) -> dict[str, Any]:
    """Récupère le planning de la semaine."""
    from src.core.models import Repas

    if not date_debut:
        today = datetime.now()
        date_debut = today - timedelta(days=today.weekday())

    date_fin = date_debut + timedelta(days=7)

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


@router.post("/repas", response_model=MessageResponse)
async def create_repas(repas: RepasCreate, user: dict[str, Any] = Depends(require_auth)):
    """Planifie un repas."""
    from src.core.models import Planning, Repas

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


@router.put("/repas/{repas_id}", response_model=MessageResponse)
async def update_repas(
    repas_id: int, repas: RepasCreate, user: dict[str, Any] = Depends(require_auth)
):
    """Met à jour un repas planifié."""
    from src.core.models import Repas

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


@router.delete("/repas/{repas_id}", response_model=MessageResponse)
async def delete_repas(repas_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Supprime un repas planifié."""
    from src.core.models import Repas

    with executer_avec_session() as session:
        repas = session.query(Repas).filter(Repas.id == repas_id).first()

        if not repas:
            raise HTTPException(status_code=404, detail="Repas non trouvé")

        session.delete(repas)
        session.commit()

        return MessageResponse(message="Repas supprimé", id=repas_id)

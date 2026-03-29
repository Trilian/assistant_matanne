"""
Routes API Maison — Projets domestiques.

Sous-routeur inclus dans maison.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.core.backup.utils_serialization import model_to_dict

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Maison"])

# ═══════════════════════════════════════════════════════════
# PROJETS DOMESTIQUES
# ═══════════════════════════════════════════════════════════


@router.get("/projets", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_projets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    statut: str | None = Query(None, description="Filtrer par statut (en_cours, terminé, annulé)"),
    priorite: str | None = Query(None, description="Filtrer par priorité"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les projets domestiques."""
    from src.core.models import Projet

    def _query():
        with executer_avec_session() as session:
            query = session.query(Projet)

            if statut:
                query = query.filter(Projet.statut == statut)
            if priorite:
                query = query.filter(Projet.priorite == priorite)

            total = query.count()
            items = (
                query.order_by(Projet.cree_le.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": p.id,
                        "nom": p.nom,
                        "description": p.description,
                        "statut": p.statut,
                        "priorite": p.priorite,
                        "date_debut": p.date_debut.isoformat() if p.date_debut else None,
                        "date_fin_prevue": p.date_fin_prevue.isoformat()
                        if p.date_fin_prevue
                        else None,
                        "date_fin_reelle": p.date_fin_reelle.isoformat()
                        if p.date_fin_reelle
                        else None,
                        "taches_count": len(p.tasks) if p.tasks else 0,
                    }
                    for p in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/projets/{projet_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_projet(projet_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Récupère un projet avec ses tâches."""
    from src.core.models import Projet

    def _query():
        with executer_avec_session() as session:
            projet = session.query(Projet).filter(Projet.id == projet_id).first()
            if not projet:
                raise HTTPException(status_code=404, detail="Projet non trouvé")

            return {
                "id": projet.id,
                "nom": projet.nom,
                "description": projet.description,
                "statut": projet.statut,
                "priorite": projet.priorite,
                "date_debut": projet.date_debut.isoformat() if projet.date_debut else None,
                "date_fin_prevue": projet.date_fin_prevue.isoformat()
                if projet.date_fin_prevue
                else None,
                "date_fin_reelle": projet.date_fin_reelle.isoformat()
                if projet.date_fin_reelle
                else None,
                "taches": [
                    {
                        "id": t.id,
                        "nom": t.nom,
                        "statut": t.statut,
                        "priorite": t.priorite,
                        "date_echeance": t.date_echeance.isoformat() if t.date_echeance else None,
                        "assigne_a": t.assigne_a,
                    }
                    for t in (projet.tasks or [])
                ],
            }

    return await executer_async(_query)


@router.post("/projets", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_projet(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un nouveau projet domestique."""
    from src.core.models import Projet

    def _query():
        with executer_avec_session() as session:
            projet = Projet(
                nom=payload["nom"],
                description=payload.get("description"),
                statut=payload.get("statut", "en_cours"),
                priorite=payload.get("priorite", "moyenne"),
                date_debut=payload.get("date_debut"),
                date_fin_prevue=payload.get("date_fin_prevue"),
            )
            session.add(projet)
            session.commit()
            session.refresh(projet)
            return {
                "id": projet.id,
                "nom": projet.nom,
                "statut": projet.statut,
                "priorite": projet.priorite,
            }

    return await executer_async(_query)


@router.patch("/projets/{projet_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_projet(
    projet_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un projet domestique."""
    from src.core.models import Projet

    def _query():
        with executer_avec_session() as session:
            projet = session.query(Projet).filter(Projet.id == projet_id).first()
            if not projet:
                raise HTTPException(status_code=404, detail="Projet non trouvé")

            for champ in ("nom", "description", "statut", "priorite", "date_debut", "date_fin_prevue", "date_fin_reelle"):
                if champ in payload:
                    setattr(projet, champ, payload[champ])

            session.commit()
            session.refresh(projet)
            return {
                "id": projet.id,
                "nom": projet.nom,
                "statut": projet.statut,
                "priorite": projet.priorite,
            }

    return await executer_async(_query)


@router.delete("/projets/{projet_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_projet(
    projet_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un projet et ses tâches."""
    from src.core.models import Projet

    def _query():
        with executer_avec_session() as session:
            projet = session.query(Projet).filter(Projet.id == projet_id).first()
            if not projet:
                raise HTTPException(status_code=404, detail="Projet non trouvé")
            session.delete(projet)
            session.commit()
            return MessageResponse(message=f"Projet '{projet.nom}' supprimé")

    return await executer_async(_query)


@router.post("/projets/{projet_id}/estimer-ia", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def estimer_projet_ia(
    projet_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère une estimation IA complète pour un projet (budget, tâches, matériaux)."""
    from src.core.models import Projet
    from src.services.maison import get_projets_service

    def _get_projet():
        with executer_avec_session() as session:
            projet = session.query(Projet).filter(Projet.id == projet_id).first()
            if not projet:
                raise HTTPException(status_code=404, detail="Projet non trouvé")
            return {
                "nom": projet.nom,
                "description": projet.description or "",
                "categorie": projet.categorie or "travaux",
            }

    projet_data = await executer_async(_get_projet)

    service = get_projets_service()
    estimation = await service.estimer_projet(
        nom=projet_data["nom"],
        description=projet_data["description"],
        categorie=projet_data["categorie"],
    )
    return estimation.model_dump(mode="json")


# ═══════════════════════════════════════════════════════════
# PROJETS — PRIORISER IA
# ═══════════════════════════════════════════════════════════


@router.get("/projets/prioriser-ia", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def prioriser_projets_ia(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggère un ordre de priorité pour les projets en cours via l'IA."""
    from src.core.models.maison import ProjetMaison
    from src.services.maison.conseiller_service import get_conseiller_maison_service
    from src.api.utils import executer_avec_session

    def _query():
        with executer_avec_session() as session:
            projets = (
                session.query(ProjetMaison)
                .filter(ProjetMaison.statut.in_(["en_cours", "planifie", "en_attente"]))
                .order_by(ProjetMaison.priorite.desc())
                .limit(10)
                .all()
            )
            if not projets:
                return {"priorites": [], "conseil": "Aucun projet actif à prioriser."}

            service = get_conseiller_maison_service()
            noms = ", ".join(p.nom for p in projets)
            try:
                conseil = service.obtenir_conseil("travaux")
                message = conseil.get("conseils", ["Priorisez selon l'urgence et le budget disponible."])[0] if isinstance(conseil.get("conseils"), list) else "Priorisez selon l'urgence et le budget."
            except Exception:
                message = "Priorisez selon l'urgence et le budget disponible."
                logger.warning("[maison] Conseil IA priorisation projets non disponible")

            return {
                "priorites": [
                    {"id": p.id, "nom": p.nom, "statut": p.statut, "priorite": p.priorite}
                    for p in projets
                ],
                "conseil": message,
                "projets_analyses": noms,
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SYNC TÂCHES MAISON → PLANNING FAMILIAL
# ═══════════════════════════════════════════════════════════


@router.post("/planning/sync-famille", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api

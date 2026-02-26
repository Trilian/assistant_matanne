"""
Routes API pour la maison.

Endpoints pour la gestion de la maison:
- Projets domestiques
- Routines
- Tâches d'entretien
- Jardin
- Stocks maison
- Meubles wishlist
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import REPONSES_CRUD_LECTURE, REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/maison", tags=["Maison"])


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


# ═══════════════════════════════════════════════════════════
# ROUTINES
# ═══════════════════════════════════════════════════════════


@router.get("/routines", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_routines(
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    actif: bool = Query(True, description="Routines actives seulement"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les routines familiales."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            query = session.query(Routine)

            if categorie:
                query = query.filter(Routine.categorie == categorie)
            if actif is not None:
                query = query.filter(Routine.actif == actif)

            routines = query.order_by(Routine.nom).all()

            return {
                "items": [
                    {
                        "id": r.id,
                        "nom": r.nom,
                        "description": r.description,
                        "categorie": r.categorie,
                        "frequence": r.frequence,
                        "actif": r.actif,
                        "taches_count": len(r.tasks) if r.tasks else 0,
                    }
                    for r in routines
                ],
            }

    return await executer_async(_query)


@router.get("/routines/{routine_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_routine(routine_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Récupère une routine avec ses tâches."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvée")

            return {
                "id": routine.id,
                "nom": routine.nom,
                "description": routine.description,
                "categorie": routine.categorie,
                "frequence": routine.frequence,
                "actif": routine.actif,
                "taches": [
                    {
                        "id": t.id,
                        "nom": t.nom,
                        "ordre": t.ordre,
                        "heure_prevue": t.heure_prevue,
                        "fait_le": t.fait_le.isoformat() if t.fait_le else None,
                    }
                    for t in sorted((routine.tasks or []), key=lambda x: x.ordre)
                ],
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# TÂCHES D'ENTRETIEN
# ═══════════════════════════════════════════════════════════


@router.get("/entretien", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_taches_entretien(
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    piece: str | None = Query(None, description="Filtrer par pièce"),
    fait: bool | None = Query(None, description="Filtrer par statut fait/non fait"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les tâches d'entretien planifiées."""
    from src.core.models import TacheEntretien

    def _query():
        with executer_avec_session() as session:
            query = session.query(TacheEntretien)

            if categorie:
                query = query.filter(TacheEntretien.categorie == categorie)
            if piece:
                query = query.filter(TacheEntretien.piece == piece)
            if fait is not None:
                query = query.filter(TacheEntretien.fait == fait)

            taches = query.order_by(TacheEntretien.prochaine_fois.asc().nullsfirst()).all()

            return {
                "items": [
                    {
                        "id": t.id,
                        "nom": t.nom,
                        "description": t.description,
                        "categorie": t.categorie,
                        "piece": t.piece,
                        "frequence_jours": t.frequence_jours,
                        "derniere_fois": t.derniere_fois.isoformat() if t.derniere_fois else None,
                        "prochaine_fois": t.prochaine_fois.isoformat()
                        if t.prochaine_fois
                        else None,
                        "duree_minutes": t.duree_minutes,
                        "responsable": t.responsable,
                        "priorite": t.priorite,
                        "fait": t.fait,
                    }
                    for t in taches
                ],
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# JARDIN
# ═══════════════════════════════════════════════════════════


@router.get("/jardin", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_elements_jardin(
    type_element: str | None = Query(None, description="Filtrer par type (plante, légume, etc.)"),
    statut: str | None = Query(None, description="Filtrer par statut"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les éléments du jardin."""
    from src.core.models import ElementJardin

    def _query():
        with executer_avec_session() as session:
            query = session.query(ElementJardin)

            if type_element:
                query = query.filter(ElementJardin.type == type_element)
            if statut:
                query = query.filter(ElementJardin.statut == statut)

            elements = query.order_by(ElementJardin.nom).all()

            return {
                "items": [
                    {
                        "id": e.id,
                        "nom": e.nom,
                        "type": e.type,
                        "location": e.location,
                        "statut": e.statut,
                        "date_plantation": e.date_plantation.isoformat()
                        if e.date_plantation
                        else None,
                        "date_recolte_prevue": e.date_recolte_prevue.isoformat()
                        if e.date_recolte_prevue
                        else None,
                    }
                    for e in elements
                ],
            }

    return await executer_async(_query)


@router.get("/jardin/{element_id}/journal", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_journal_jardin(
    element_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère le journal d'entretien d'un élément du jardin."""
    from src.core.models import JournalJardin

    def _query():
        with executer_avec_session() as session:
            logs = (
                session.query(JournalJardin)
                .filter(JournalJardin.garden_item_id == element_id)
                .order_by(JournalJardin.date.desc())
                .all()
            )

            return {
                "element_id": element_id,
                "logs": [
                    {
                        "id": log.id,
                        "date": log.date.isoformat(),
                        "action": log.action,
                        "notes": log.notes,
                    }
                    for log in logs
                ],
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# STOCKS MAISON
# ═══════════════════════════════════════════════════════════


@router.get("/stocks", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_stocks_maison(
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    alerte_stock: bool = Query(False, description="Afficher seulement les stocks bas"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les stocks de consommables maison."""
    from src.core.models import StockMaison

    def _query():
        with executer_avec_session() as session:
            query = session.query(StockMaison)

            if categorie:
                query = query.filter(StockMaison.categorie == categorie)
            if alerte_stock:
                query = query.filter(StockMaison.quantite <= StockMaison.seuil_alerte)

            stocks = query.order_by(StockMaison.nom).all()

            return {
                "items": [
                    {
                        "id": s.id,
                        "nom": s.nom,
                        "categorie": s.categorie,
                        "quantite": s.quantite,
                        "unite": s.unite,
                        "seuil_alerte": s.seuil_alerte,
                        "emplacement": s.emplacement,
                        "prix_unitaire": float(s.prix_unitaire) if s.prix_unitaire else None,
                        "en_alerte": s.quantite <= s.seuil_alerte,
                    }
                    for s in stocks
                ],
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# MEUBLES WISHLIST
# ═══════════════════════════════════════════════════════════


@router.get("/meubles", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_meubles(
    piece: str | None = Query(None, description="Filtrer par pièce"),
    statut: str | None = Query(None, description="Filtrer par statut"),
    priorite: str | None = Query(None, description="Filtrer par priorité"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les meubles de la wishlist."""
    from src.core.models import Meuble

    def _query():
        with executer_avec_session() as session:
            query = session.query(Meuble)

            if piece:
                query = query.filter(Meuble.piece == piece)
            if statut:
                query = query.filter(Meuble.statut == statut)
            if priorite:
                query = query.filter(Meuble.priorite == priorite)

            meubles = query.order_by(Meuble.priorite, Meuble.nom).all()

            return {
                "items": [
                    {
                        "id": m.id,
                        "nom": m.nom,
                        "description": m.description,
                        "piece": m.piece,
                        "categorie": m.categorie,
                        "prix_estime": float(m.prix_estime) if m.prix_estime else None,
                        "prix_max": float(m.prix_max) if m.prix_max else None,
                        "prix_reel": float(m.prix_reel) if m.prix_reel else None,
                        "statut": m.statut,
                        "priorite": m.priorite,
                        "magasin": m.magasin,
                        "url": m.url,
                    }
                    for m in meubles
                ],
            }

    return await executer_async(_query)

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
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
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


@router.post("/entretien", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_tache_entretien(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une nouvelle tâche d'entretien."""
    from src.core.models import TacheEntretien

    def _query():
        with executer_avec_session() as session:
            tache = TacheEntretien(
                nom=payload["nom"],
                description=payload.get("description"),
                categorie=payload.get("categorie", "entretien"),
                piece=payload.get("piece"),
                frequence_jours=payload.get("frequence_jours"),
                prochaine_fois=payload.get("prochaine_fois"),
                duree_minutes=payload.get("duree_minutes", 30),
                responsable=payload.get("responsable"),
                priorite=payload.get("priorite", "normale"),
            )
            session.add(tache)
            session.commit()
            session.refresh(tache)
            return {
                "id": tache.id,
                "nom": tache.nom,
                "categorie": tache.categorie,
                "piece": tache.piece,
                "priorite": tache.priorite,
                "fait": tache.fait,
            }

    return await executer_async(_query)


@router.patch("/entretien/{tache_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_tache_entretien(
    tache_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour une tâche d'entretien (ou la marque comme faite)."""
    from src.core.models import TacheEntretien

    def _query():
        with executer_avec_session() as session:
            tache = session.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()
            if not tache:
                raise HTTPException(status_code=404, detail="Tâche non trouvée")

            for champ in ("nom", "description", "categorie", "piece", "frequence_jours",
                          "prochaine_fois", "duree_minutes", "responsable", "priorite", "fait"):
                if champ in payload:
                    setattr(tache, champ, payload[champ])

            # Si marqué comme fait, mettre à jour derniere_fois
            if payload.get("fait") is True:
                tache.derniere_fois = date.today()
                if tache.frequence_jours:
                    from datetime import timedelta
                    tache.prochaine_fois = date.today() + timedelta(days=tache.frequence_jours)
                    tache.fait = False  # Reset pour la prochaine occurrence

            session.commit()
            session.refresh(tache)
            return {
                "id": tache.id,
                "nom": tache.nom,
                "fait": tache.fait,
                "derniere_fois": tache.derniere_fois.isoformat() if tache.derniere_fois else None,
                "prochaine_fois": tache.prochaine_fois.isoformat() if tache.prochaine_fois else None,
            }

    return await executer_async(_query)


@router.delete("/entretien/{tache_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_tache_entretien(
    tache_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une tâche d'entretien."""
    from src.core.models import TacheEntretien

    def _query():
        with executer_avec_session() as session:
            tache = session.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()
            if not tache:
                raise HTTPException(status_code=404, detail="Tâche non trouvée")
            session.delete(tache)
            session.commit()
            return MessageResponse(message=f"Tâche '{tache.nom}' supprimée")

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


@router.post("/jardin", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_element_jardin(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un élément au jardin."""
    from src.core.models import ElementJardin

    def _query():
        with executer_avec_session() as session:
            element = ElementJardin(
                nom=payload["nom"],
                type=payload.get("type", "plante"),
                location=payload.get("location"),
                statut=payload.get("statut", "actif"),
                date_plantation=payload.get("date_plantation"),
                date_recolte_prevue=payload.get("date_recolte_prevue"),
                notes=payload.get("notes"),
            )
            session.add(element)
            session.commit()
            session.refresh(element)
            return {
                "id": element.id,
                "nom": element.nom,
                "type": element.type,
                "statut": element.statut,
            }

    return await executer_async(_query)


@router.patch("/jardin/{element_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_element_jardin(
    element_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un élément du jardin."""
    from src.core.models import ElementJardin

    def _query():
        with executer_avec_session() as session:
            element = session.query(ElementJardin).filter(ElementJardin.id == element_id).first()
            if not element:
                raise HTTPException(status_code=404, detail="Élément non trouvé")

            for champ in ("nom", "type", "location", "statut", "date_plantation",
                          "date_recolte_prevue", "notes"):
                if champ in payload:
                    setattr(element, champ, payload[champ])

            session.commit()
            session.refresh(element)
            return {
                "id": element.id,
                "nom": element.nom,
                "type": element.type,
                "statut": element.statut,
            }

    return await executer_async(_query)


@router.delete("/jardin/{element_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_element_jardin(
    element_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un élément du jardin."""
    from src.core.models import ElementJardin

    def _query():
        with executer_avec_session() as session:
            element = session.query(ElementJardin).filter(ElementJardin.id == element_id).first()
            if not element:
                raise HTTPException(status_code=404, detail="Élément non trouvé")
            session.delete(element)
            session.commit()
            return MessageResponse(message=f"Élément '{element.nom}' supprimé")

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


@router.post("/stocks", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_stock(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un stock de consommable maison."""
    from src.core.models import StockMaison

    def _query():
        with executer_avec_session() as session:
            stock = StockMaison(
                nom=payload["nom"],
                categorie=payload.get("categorie", "autre"),
                quantite=payload.get("quantite", 0),
                unite=payload.get("unite", "unité"),
                seuil_alerte=payload.get("seuil_alerte", 1),
                emplacement=payload.get("emplacement"),
                prix_unitaire=payload.get("prix_unitaire"),
            )
            session.add(stock)
            session.commit()
            session.refresh(stock)
            return {
                "id": stock.id,
                "nom": stock.nom,
                "categorie": stock.categorie,
                "quantite": stock.quantite,
            }

    return await executer_async(_query)


@router.patch("/stocks/{stock_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_stock(
    stock_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un stock (quantité, seuil, etc.)."""
    from src.core.models import StockMaison

    def _query():
        with executer_avec_session() as session:
            stock = session.query(StockMaison).filter(StockMaison.id == stock_id).first()
            if not stock:
                raise HTTPException(status_code=404, detail="Stock non trouvé")

            for champ in ("nom", "categorie", "quantite", "unite", "seuil_alerte",
                          "emplacement", "prix_unitaire"):
                if champ in payload:
                    setattr(stock, champ, payload[champ])

            session.commit()
            session.refresh(stock)
            return {
                "id": stock.id,
                "nom": stock.nom,
                "quantite": stock.quantite,
                "en_alerte": stock.quantite <= stock.seuil_alerte,
            }

    return await executer_async(_query)


@router.delete("/stocks/{stock_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_stock(
    stock_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un stock."""
    from src.core.models import StockMaison

    def _query():
        with executer_avec_session() as session:
            stock = session.query(StockMaison).filter(StockMaison.id == stock_id).first()
            if not stock:
                raise HTTPException(status_code=404, detail="Stock non trouvé")
            session.delete(stock)
            session.commit()
            return MessageResponse(message=f"Stock '{stock.nom}' supprimé")

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


# ═══════════════════════════════════════════════════════════
# CALENDRIER DES SEMIS (JARDIN INTELLIGENT)
# ═══════════════════════════════════════════════════════════


@router.get("/jardin/calendrier-semis", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_calendrier_semis(
    mois: int | None = Query(None, ge=1, le=12, description="Mois (1-12), défaut: mois courant"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Retourne le calendrier des semis pour le mois donné.

    Utilise le catalogue de plantes (data/plantes_catalogue.json) pour
    déterminer quoi semer, planter et récolter selon la saison.
    """
    import json
    from pathlib import Path

    mois_courant = mois or date.today().month

    NOMS_MOIS = [
        "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
    ]

    # Charger le catalogue de plantes
    catalogue_path = Path("data/plantes_catalogue.json")
    if not catalogue_path.exists():
        return {
            "mois": mois_courant,
            "mois_nom": NOMS_MOIS[mois_courant],
            "a_semer": [],
            "a_planter": [],
            "a_recolter": [],
            "conseils": [],
        }

    with open(catalogue_path, encoding="utf-8") as f:
        catalogue = json.load(f)

    plantes = catalogue if isinstance(catalogue, list) else catalogue.get("plantes", [])

    a_semer = []
    a_planter = []
    a_recolter = []

    for plante in plantes:
        nom = plante.get("nom", "")
        semis = plante.get("mois_semis", plante.get("semis", []))
        plantation = plante.get("mois_plantation", plante.get("plantation", []))
        recolte = plante.get("mois_recolte", plante.get("recolte", []))

        if mois_courant in semis:
            a_semer.append({"nom": nom, "type": plante.get("type", ""), "details": plante.get("notes_semis", "")})
        if mois_courant in plantation:
            a_planter.append({"nom": nom, "type": plante.get("type", ""), "details": plante.get("notes_plantation", "")})
        if mois_courant in recolte:
            a_recolter.append({"nom": nom, "type": plante.get("type", ""), "details": plante.get("notes_recolte", "")})

    return {
        "mois": mois_courant,
        "mois_nom": NOMS_MOIS[mois_courant],
        "a_semer": a_semer,
        "a_planter": a_planter,
        "a_recolter": a_recolter,
        "conseils": [],
    }


# ═══════════════════════════════════════════════════════════
# SANTÉ DES APPAREILS (ENTRETIEN INTELLIGENT)
# ═══════════════════════════════════════════════════════════


@router.get("/entretien/sante-appareils", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_sante_appareils(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Dashboard santé des appareils.

    Agrège les tâches d'entretien pour calculer un score de santé
    par appareil/zone, et identifie les actions urgentes.
    """
    from src.core.models import TacheEntretien

    def _query():
        with executer_avec_session() as session:
            aujourd_hui = date.today()

            taches = session.query(TacheEntretien).all()

            # Grouper par pièce/catégorie
            par_zone: dict[str, dict[str, Any]] = {}
            actions_urgentes = []

            for t in taches:
                zone = t.piece or t.categorie or "Général"

                if zone not in par_zone:
                    par_zone[zone] = {
                        "zone": zone,
                        "total_taches": 0,
                        "taches_a_jour": 0,
                        "taches_en_retard": 0,
                        "score_sante": 100,
                    }

                par_zone[zone]["total_taches"] += 1

                en_retard = (
                    t.prochaine_fois is not None
                    and t.prochaine_fois < aujourd_hui
                    and not t.fait
                )

                if en_retard:
                    par_zone[zone]["taches_en_retard"] += 1
                    jours_retard = (aujourd_hui - t.prochaine_fois).days
                    actions_urgentes.append(
                        {
                            "tache": t.nom,
                            "zone": zone,
                            "jours_retard": jours_retard,
                            "priorite": t.priorite,
                        }
                    )
                else:
                    par_zone[zone]["taches_a_jour"] += 1

            # Calculer score par zone
            for zone_data in par_zone.values():
                total = zone_data["total_taches"]
                if total > 0:
                    zone_data["score_sante"] = round(
                        (zone_data["taches_a_jour"] / total) * 100
                    )

            # Score global
            total_taches = sum(z["total_taches"] for z in par_zone.values())
            total_a_jour = sum(z["taches_a_jour"] for z in par_zone.values())
            score_global = round((total_a_jour / total_taches) * 100) if total_taches > 0 else 100

            # Trier les actions urgentes par jours de retard
            actions_urgentes.sort(key=lambda x: x["jours_retard"], reverse=True)

            return {
                "score_global": score_global,
                "total_taches": total_taches,
                "taches_a_jour": total_a_jour,
                "taches_en_retard": total_taches - total_a_jour,
                "zones": list(par_zone.values()),
                "actions_urgentes": actions_urgentes[:10],
            }

    return await executer_async(_query)

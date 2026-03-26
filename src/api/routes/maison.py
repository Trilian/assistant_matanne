"""
Routes API pour la maison.

Endpoints pour la gestion de la maison:
- Projets domestiques
- Routines
- Tâches d'entretien
- Jardin
- Stocks maison
- Meubles wishlist
- Cellier (cave & garde-manger)
- Artisans (carnet d'adresses)
- Contrats (assurances, énergie, etc.)
- Garanties (appareils & SAV)
- Diagnostics immobiliers & estimations
- Éco-tips (actions écologiques)
- Dépenses maison
- Nuisibles (traitements)
- Devis comparatifs
- Entretien saisonnier
- Relevés compteurs
- Visualisation plan maison
- Hub data (stats dashboard)
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
from src.services.maison.schemas import AlerteMaison, BriefingMaison, TacheJour

router = APIRouter(prefix="/api/v1/maison", tags=["Maison"])


# ═══════════════════════════════════════════════════════════
# CONTEXTE MAISON (Phase X)
# ═══════════════════════════════════════════════════════════


@router.get("/briefing", response_model=BriefingMaison, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_briefing_maison(
    date_cible: date | None = Query(None, description="Date du briefing (défaut: aujourd'hui)"),
    user: dict[str, Any] = Depends(require_auth),
) -> BriefingMaison:
    """
    Obtient le briefing quotidien maison.
    
    Agrège 6 sources de données:
    - Alertes (garanties, contrats, diagnostics, entretien)
    - Tâches du jour (ménage, entretien, projets, jardin)
    - Météo (impact jardin & ménage)
    - Projets actifs
    - Jardin contextuel
    - Cellier & énergie (anomalies)
    
    Returns:
        Briefing maison contextuel
    """
    from src.services.maison.contexte_maison_service import obtenir_service_contexte_maison

    def _query():
        service = obtenir_service_contexte_maison()
        return service.obtenir_briefing(date_cible=date_cible)

    return await executer_async(_query)


@router.get("/alertes", response_model=list[AlerteMaison], responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_alertes_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> list[AlerteMaison]:
    """
    Obtient toutes les alertes maison.
    
    Retourne toutes les alertes (pas juste le top 8 du briefing):
    - Garanties expirant
    - Contrats (assurance, énergie, internet)
    - Diagnostics immobiliers
    - Entretien saisonnier
    
    Returns:
        Liste complète des alertes triées par urgence
    """
    from src.services.maison.contexte_maison_service import obtenir_service_contexte_maison

    def _query():
        service = obtenir_service_contexte_maison()
        return service.obtenir_toutes_alertes()

    return await executer_async(_query)


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


@router.post(
    "/routines/{routine_id}/repetitions",
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def enregistrer_repetition(
    routine_id: int,
    tache_ids: list[int] | None = None,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une répétition (toutes ou certaines tâches faites aujourd'hui)."""
    from src.core.models import Routine, TacheRoutine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvée")

            query = session.query(TacheRoutine).filter(
                TacheRoutine.routine_id == routine_id
            )
            if tache_ids:
                query = query.filter(TacheRoutine.id.in_(tache_ids))

            today = date.today()
            updated = 0
            for tache in query.all():
                tache.fait_le = today
                updated += 1

            session.commit()

            return {
                "routine_id": routine_id,
                "date": today.isoformat(),
                "taches_completees": updated,
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


@router.get("/jardin/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_ia_jardin(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Tâches saisonnières du jardin générées par IA (conseils pratiques pour la saison en cours)."""
    from src.services.maison.jardin_service import get_jardin_service
    import asyncio

    service = get_jardin_service()
    conseils_bruts = await service.generer_conseils_saison()

    # Transformer la réponse texte en liste structurée de tâches
    lignes = [l.strip() for l in conseils_bruts.splitlines() if l.strip()]
    taches = []
    for ligne in lignes:
        # Nettoyer les puces/numéros en début de ligne
        for prefix in ("- ", "• ", "* "):
            if ligne.startswith(prefix):
                ligne = ligne[len(prefix):]
        if ligne and not ligne.endswith(":"):
            taches.append({"tache": ligne, "saison": service.obtenir_saison_actuelle()})

    return {"taches": taches, "total": len(taches)}


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
    catalogue_path = Path("data/reference/plantes_catalogue.json")
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


# ═══════════════════════════════════════════════════════════
# MEUBLES — CRUD complémentaire (GET existe déjà ci-dessus)
# ═══════════════════════════════════════════════════════════


@router.post("/meubles", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_meuble(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un meuble dans la wishlist."""
    from src.services.maison import get_meubles_crud_service

    def _query():
        service = get_meubles_crud_service()
        return model_to_dict(service.create_meuble(payload))

    return await executer_async(_query)


@router.patch("/meubles/{meuble_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_meuble(
    meuble_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un meuble."""
    from src.services.maison import get_meubles_crud_service

    def _query():
        service = get_meubles_crud_service()
        return model_to_dict(service.update_meuble(meuble_id, payload))

    return await executer_async(_query)


@router.delete("/meubles/{meuble_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_meuble(
    meuble_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un meuble de la wishlist."""
    from src.services.maison import get_meubles_crud_service

    def _query():
        service = get_meubles_crud_service()
        service.delete_meuble(meuble_id)
        return MessageResponse(message="Meuble supprimé")

    return await executer_async(_query)


@router.get("/meubles/budget", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_budget_meubles(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Résumé budget meubles (total estimé, max, par pièce)."""
    from src.services.maison import get_meubles_crud_service

    def _query():
        service = get_meubles_crud_service()
        return service.get_budget_resume()

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# CELLIER (cave & garde-manger)
# ═══════════════════════════════════════════════════════════


@router.get("/cellier", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_articles_cellier(
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    emplacement: str | None = Query(None, description="Filtrer par emplacement"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les articles du cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        articles = service.get_all_articles(
            filtre_categorie=categorie,
            filtre_emplacement=emplacement,
        )
        return {"items": articles}

    return await executer_async(_query)


@router.get("/cellier/alertes/peremption", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_peremption_cellier(
    jours: int = Query(14, ge=1, le=90, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Articles dont la date de péremption approche."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return {"items": service.get_alertes_peremption(jours_horizon=jours)}

    return await executer_async(_query)


@router.get("/cellier/alertes/stock", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_stock_cellier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Articles dont le stock est en dessous du seuil d'alerte."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return {"items": service.get_alertes_stock()}

    return await executer_async(_query)


@router.get("/cellier/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_cellier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques du cellier (total, par catégorie, valeur)."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return service.get_stats_cellier()

    return await executer_async(_query)


@router.get("/cellier/{article_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_article_cellier(
    article_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'un article du cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        result = service.get_article_by_id(article_id)
        if not result:
            raise HTTPException(status_code=404, detail="Article non trouvé")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/cellier", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_article_cellier(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un article au cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return model_to_dict(service.create_article(payload))

    return await executer_async(_query)


@router.patch("/cellier/{article_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_article_cellier(
    article_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un article du cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        return model_to_dict(service.update_article(article_id, payload))

    return await executer_async(_query)


@router.delete("/cellier/{article_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_article_cellier(
    article_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un article du cellier."""
    from src.services.maison import get_cellier_crud_service

    def _query():
        service = get_cellier_crud_service()
        service.delete_article(article_id)
        return MessageResponse(message="Article supprimé")

    return await executer_async(_query)


@router.patch("/cellier/{article_id}/quantite", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def ajuster_quantite_cellier(
    article_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajuste la quantité d'un article (+/- delta)."""
    from src.services.maison import get_cellier_crud_service

    delta = payload.get("delta", 0)

    def _query():
        service = get_cellier_crud_service()
        return service.ajuster_quantite(article_id, delta)

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ARTISANS (carnet d'adresses)
# ═══════════════════════════════════════════════════════════


@router.get("/artisans", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_artisans(
    metier: str | None = Query(None, description="Filtrer par métier"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les artisans du carnet d'adresses."""
    from src.services.maison import get_artisans_crud_service

    def _query():
        service = get_artisans_crud_service()
        return {"items": service.get_all_artisans(filtre_metier=metier)}

    return await executer_async(_query)


@router.get("/artisans/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_artisans(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques artisans (nb métiers, dépenses, interventions)."""
    from src.services.maison import get_artisans_crud_service

    def _query():
        service = get_artisans_crud_service()
        return service.get_stats_artisans()

    return await executer_async(_query)


@router.get("/artisans/{artisan_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_artisan(
    artisan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'un artisan."""
    from src.services.maison import get_artisans_crud_service

    def _query():
        service = get_artisans_crud_service()
        result = service.get_artisan_by_id(artisan_id)
        if not result:
            raise HTTPException(status_code=404, detail="Artisan non trouvé")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/artisans", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_artisan(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un artisan au carnet."""
    from src.services.maison import get_artisans_crud_service

    def _query():
        service = get_artisans_crud_service()
        return model_to_dict(service.create_artisan(payload))

    return await executer_async(_query)


@router.patch("/artisans/{artisan_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_artisan(
    artisan_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un artisan."""
    from src.services.maison import get_artisans_crud_service

    def _query():
        service = get_artisans_crud_service()
        return model_to_dict(service.update_artisan(artisan_id, payload))

    return await executer_async(_query)


@router.delete("/artisans/{artisan_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_artisan(
    artisan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un artisan et ses interventions."""
    from src.services.maison import get_artisans_crud_service

    def _query():
        service = get_artisans_crud_service()
        service.delete_artisan(artisan_id)
        return MessageResponse(message="Artisan supprimé")

    return await executer_async(_query)


@router.get("/artisans/{artisan_id}/interventions", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_interventions(
    artisan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des interventions d'un artisan."""
    from src.services.maison import get_artisans_crud_service

    def _query():
        service = get_artisans_crud_service()
        return {"items": service.get_interventions(artisan_id)}

    return await executer_async(_query)


@router.post("/artisans/{artisan_id}/interventions", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_intervention(
    artisan_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une intervention d'un artisan."""
    from src.services.maison import get_artisans_crud_service

    payload["artisan_id"] = artisan_id

    def _query():
        service = get_artisans_crud_service()
        return model_to_dict(service.create_intervention(payload))

    return await executer_async(_query)


@router.delete("/artisans/interventions/{intervention_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_intervention(
    intervention_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une intervention."""
    from src.services.maison import get_artisans_crud_service

    def _query():
        service = get_artisans_crud_service()
        service.delete_intervention(intervention_id)
        return MessageResponse(message="Intervention supprimée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# CONTRATS (assurances, énergie, etc.)
# ═══════════════════════════════════════════════════════════


@router.get("/contrats", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_contrats(
    type_contrat: str | None = Query(None, description="Filtrer par type"),
    statut: str | None = Query(None, description="Filtrer par statut"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les contrats de la maison."""
    from src.services.maison import get_contrats_crud_service

    def _query():
        service = get_contrats_crud_service()
        return {"items": service.get_all_contrats(filtre_type=type_contrat, filtre_statut=statut)}

    return await executer_async(_query)


@router.get("/contrats/alertes", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_contrats(
    jours: int = Query(60, ge=1, le=365, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Contrats à renouveler ou résilier prochainement."""
    from src.services.maison import get_contrats_crud_service

    def _query():
        service = get_contrats_crud_service()
        return {"items": service.get_alertes_contrats(jours_horizon=jours)}

    return await executer_async(_query)


@router.get("/contrats/resume-financier", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def resume_financier_contrats(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Résumé financier des contrats (mensuel/annuel par type)."""
    from src.services.maison import get_contrats_crud_service

    def _query():
        service = get_contrats_crud_service()
        return service.get_resume_financier()

    return await executer_async(_query)


@router.get("/contrats/{contrat_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_contrat(
    contrat_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'un contrat."""
    from src.services.maison import get_contrats_crud_service

    def _query():
        service = get_contrats_crud_service()
        result = service.get_contrat_by_id(contrat_id)
        if not result:
            raise HTTPException(status_code=404, detail="Contrat non trouvé")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/contrats", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_contrat(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un contrat."""
    from src.services.maison import get_contrats_crud_service

    def _query():
        service = get_contrats_crud_service()
        return model_to_dict(service.create_contrat(payload))

    return await executer_async(_query)


@router.patch("/contrats/{contrat_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_contrat(
    contrat_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un contrat."""
    from src.services.maison import get_contrats_crud_service

    def _query():
        service = get_contrats_crud_service()
        return model_to_dict(service.update_contrat(contrat_id, payload))

    return await executer_async(_query)


@router.delete("/contrats/{contrat_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_contrat(
    contrat_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un contrat."""
    from src.services.maison import get_contrats_crud_service

    def _query():
        service = get_contrats_crud_service()
        service.delete_contrat(contrat_id)
        return MessageResponse(message="Contrat supprimé")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# GARANTIES & INCIDENTS SAV
# ═══════════════════════════════════════════════════════════


@router.get("/garanties", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_garanties(
    statut: str | None = Query(None, description="Filtrer par statut"),
    piece: str | None = Query(None, description="Filtrer par pièce"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les garanties enregistrées."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        return {"items": service.get_all_garanties(filtre_statut=statut, filtre_piece=piece)}

    return await executer_async(_query)


@router.get("/garanties/alertes", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_garanties(
    jours: int = Query(60, ge=1, le=365, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Garanties arrivant à expiration."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        return {"items": service.get_alertes_garanties(jours_horizon=jours)}

    return await executer_async(_query)


@router.get("/garanties/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_garanties(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques garanties (total, actives, expirées, valeur)."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        return service.get_stats_garanties()

    return await executer_async(_query)


@router.get("/garanties/alertes-predictives", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_predictives_garanties(
    horizon_mois: int = Query(12, ge=1, le=36, description="Horizon prédictif en mois"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Retourne les appareils approchant leur fin de vie théorique.

    Croise les garanties avec le catalogue d'entretien pour estimer :
    - l'âge actuel de l'appareil
    - les mois restants estimés
    - l'action recommandée (SAV, remplacement, surveillance)
    """
    from src.services.maison import get_garanties_crud_service, obtenir_service_catalogue_entretien

    def _query():
        from datetime import date

        service = get_garanties_crud_service()
        catalogue = obtenir_service_catalogue_entretien()
        garanties = service.get_all_garanties()

        items: list[dict[str, Any]] = []
        for g in garanties:
            type_objet = (getattr(g, "type_objet", None) or getattr(g, "nom_appareil", "")).strip()
            if not type_objet:
                continue

            duree_vie_ans = catalogue.obtenir_duree_vie(type_objet)
            if not duree_vie_ans:
                continue

            date_achat = getattr(g, "date_achat", None)
            if not date_achat:
                continue

            age_mois = (date.today().year - date_achat.year) * 12 + (date.today().month - date_achat.month)
            restant_mois = int(duree_vie_ans * 12 - age_mois)

            if restant_mois > horizon_mois:
                continue

            if restant_mois <= 0:
                niveau = "CRITIQUE"
                action = "Prévoir remplacement et vérifier extension/prise en charge SAV"
            elif restant_mois <= 3:
                niveau = "HAUTE"
                action = "Anticiper SAV ou devis de remplacement"
            else:
                niveau = "MOYENNE"
                action = "Surveiller la performance et planifier l'entretien"

            items.append(
                {
                    "garantie_id": g.id,
                    "nom_appareil": getattr(g, "nom_appareil", type_objet),
                    "piece": getattr(g, "piece", None),
                    "date_achat": date_achat,
                    "duree_vie_ans": duree_vie_ans,
                    "age_mois": age_mois,
                    "mois_restants_estimes": restant_mois,
                    "niveau": niveau,
                    "action_recommandee": action,
                    "action_url": f"/maison/garanties/{g.id}",
                }
            )

        ordre = {"CRITIQUE": 0, "HAUTE": 1, "MOYENNE": 2, "BASSE": 3}
        items.sort(key=lambda x: (ordre.get(x["niveau"], 9), x["mois_restants_estimes"]))
        return {"items": items}

    return await executer_async(_query)


@router.get("/garanties/{garantie_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_garantie(
    garantie_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'une garantie."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        result = service.get_garantie_by_id(garantie_id)
        if not result:
            raise HTTPException(status_code=404, detail="Garantie non trouvée")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/garanties", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_garantie(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une garantie."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        return model_to_dict(service.create_garantie(payload))

    return await executer_async(_query)


@router.patch("/garanties/{garantie_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_garantie(
    garantie_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour une garantie."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        return model_to_dict(service.update_garantie(garantie_id, payload))

    return await executer_async(_query)


@router.delete("/garanties/{garantie_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_garantie(
    garantie_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une garantie et ses incidents."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        service.delete_garantie(garantie_id)
        return MessageResponse(message="Garantie supprimée")

    return await executer_async(_query)


@router.get("/garanties/{garantie_id}/incidents", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_incidents_garantie(
    garantie_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les incidents SAV d'une garantie."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        return {"items": service.get_incidents(garantie_id)}

    return await executer_async(_query)


@router.post("/garanties/{garantie_id}/incidents", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_incident_garantie(
    garantie_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre un incident SAV."""
    from src.services.maison import get_garanties_crud_service

    payload["garantie_id"] = garantie_id

    def _query():
        service = get_garanties_crud_service()
        return model_to_dict(service.create_incident(payload))

    return await executer_async(_query)


@router.patch("/garanties/incidents/{incident_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_incident_garantie(
    incident_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour le statut/coût d'un incident SAV."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        return model_to_dict(service.update_incident(incident_id, payload))

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# DIAGNOSTICS IMMOBILIERS & ESTIMATIONS
# ═══════════════════════════════════════════════════════════


@router.get("/diagnostics", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_diagnostics(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les diagnostics immobiliers (DPE, amiante, plomb...)."""
    from src.services.maison import get_diagnostics_crud_service

    def _query():
        service = get_diagnostics_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.get("/diagnostics/alertes", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_diagnostics(
    jours: int = Query(90, ge=1, le=365, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Diagnostics dont la validité expire bientôt."""
    from src.services.maison import get_diagnostics_crud_service

    def _query():
        service = get_diagnostics_crud_service()
        return {"items": service.get_alertes_validite(jours_horizon=jours)}

    return await executer_async(_query)


@router.get("/diagnostics/validite-types", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def validite_types_diagnostics(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Durées de validité par type de diagnostic."""
    from src.services.maison import get_diagnostics_crud_service

    def _query():
        service = get_diagnostics_crud_service()
        return service.get_validite_par_type()

    return await executer_async(_query)


@router.post("/diagnostics", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_diagnostic(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre un diagnostic immobilier."""
    from src.services.maison import get_diagnostics_crud_service

    def _query():
        service = get_diagnostics_crud_service()
        return model_to_dict(service.create(payload))

    return await executer_async(_query)


@router.patch("/diagnostics/{diagnostic_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_diagnostic(
    diagnostic_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un diagnostic."""
    from src.services.maison import get_diagnostics_crud_service

    def _query():
        service = get_diagnostics_crud_service()
        return model_to_dict(service.update(diagnostic_id, payload))

    return await executer_async(_query)


@router.delete("/diagnostics/{diagnostic_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_diagnostic(
    diagnostic_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un diagnostic."""
    from src.services.maison import get_diagnostics_crud_service

    def _query():
        service = get_diagnostics_crud_service()
        service.delete(diagnostic_id)
        return MessageResponse(message="Diagnostic supprimé")

    return await executer_async(_query)


@router.get("/estimations", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_estimations(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les estimations immobilières."""
    from src.services.maison import get_estimations_crud_service

    def _query():
        service = get_estimations_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.get("/estimations/derniere", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def derniere_estimation(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Dernière estimation immobilière."""
    from src.services.maison import get_estimations_crud_service

    def _query():
        service = get_estimations_crud_service()
        result = service.get_derniere_estimation()
        if not result:
            raise HTTPException(status_code=404, detail="Aucune estimation trouvée")
        return result

    return await executer_async(_query)


@router.post("/estimations", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_estimation(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une estimation immobilière."""
    from src.services.maison import get_estimations_crud_service

    def _query():
        service = get_estimations_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.delete("/estimations/{estimation_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_estimation(
    estimation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une estimation."""
    from src.services.maison import get_estimations_crud_service

    def _query():
        service = get_estimations_crud_service()
        service.delete(estimation_id)
        return MessageResponse(message="Estimation supprimée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ÉCO-TIPS (actions écologiques)
# ═══════════════════════════════════════════════════════════


@router.get("/eco-tips", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_eco_tips(
    actif_only: bool = Query(False, description="Seulement les actions actives"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les actions écologiques."""
    from src.services.maison import get_eco_tips_crud_service

    def _query():
        service = get_eco_tips_crud_service()
        return {"items": service.get_all_actions(actif_only=actif_only)}

    return await executer_async(_query)


@router.get("/eco-tips/{action_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_eco_tip(
    action_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'une action écologique."""
    from src.services.maison import get_eco_tips_crud_service

    def _query():
        service = get_eco_tips_crud_service()
        result = service.get_action_by_id(action_id)
        if not result:
            raise HTTPException(status_code=404, detail="Action non trouvée")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/eco-tips", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_eco_tip(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une action écologique."""
    from src.services.maison import get_eco_tips_crud_service

    def _query():
        service = get_eco_tips_crud_service()
        return model_to_dict(service.create_action(payload))

    return await executer_async(_query)


@router.patch("/eco-tips/{action_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_eco_tip(
    action_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour une action écologique."""
    from src.services.maison import get_eco_tips_crud_service

    def _query():
        service = get_eco_tips_crud_service()
        return model_to_dict(service.update_action(action_id, payload))

    return await executer_async(_query)


@router.delete("/eco-tips/{action_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_eco_tip(
    action_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une action écologique."""
    from src.services.maison import get_eco_tips_crud_service

    def _query():
        service = get_eco_tips_crud_service()
        service.delete_action(action_id)
        return MessageResponse(message="Action supprimée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# CHARGES RÉCURRENTES
# ═══════════════════════════════════════════════════════════


@router.get("/charges", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_charges(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les charges récurrentes (contrats et abonnements actifs)."""
    from src.services.maison import get_contrats_crud_service

    def _query():
        service = get_contrats_crud_service()
        contrats = service.get_all_contrats(statut="actif")
        items = contrats if isinstance(contrats, list) else []
        return {"items": [str(c) for c in items], "total": len(items)}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# DÉPENSES MAISON
# ═══════════════════════════════════════════════════════════


@router.get("/depenses", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_depenses(
    mois: int | None = Query(None, ge=1, le=12, description="Mois (1-12)"),
    annee: int | None = Query(None, ge=2020, description="Année"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les dépenses maison (par mois ou année)."""
    from src.services.maison import get_depenses_crud_service

    def _query():
        service = get_depenses_crud_service()
        if mois and annee:
            return {"items": service.get_depenses_mois(mois, annee)}
        elif annee:
            return {"items": service.get_depenses_annee(annee)}
        else:
            today = date.today()
            return {"items": service.get_depenses_mois(today.month, today.year)}

    return await executer_async(_query)


@router.get("/depenses/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_depenses(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques globales des dépenses (tendance, moyenne, delta)."""
    from src.services.maison import get_depenses_crud_service

    def _query():
        service = get_depenses_crud_service()
        return service.get_stats_globales()

    return await executer_async(_query)


@router.get("/depenses/historique/{categorie}", responses=REPONSES_LISTE)
@gerer_exception_api
async def historique_depenses_categorie(
    categorie: str,
    nb_mois: int = Query(12, ge=1, le=36, description="Nombre de mois d'historique"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des dépenses par catégorie."""
    from src.services.maison import get_depenses_crud_service

    def _query():
        service = get_depenses_crud_service()
        return {"items": service.get_historique_categorie(categorie, nb_mois=nb_mois)}

    return await executer_async(_query)


@router.get("/depenses/energie/{type_energie}", responses=REPONSES_LISTE)
@gerer_exception_api
async def historique_energie(
    type_energie: str,
    nb_mois: int = Query(12, ge=1, le=36, description="Nombre de mois d'historique"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique de consommation énergétique avec tendance."""
    from src.services.maison import get_depenses_crud_service

    def _query():
        service = get_depenses_crud_service()
        return service.charger_historique_energie(type_energie, nb_mois=nb_mois)

    return await executer_async(_query)


@router.get("/energie/tendances", responses=REPONSES_LISTE)
@gerer_exception_api
async def tendances_energie(
    type_compteur: str = Query("electricite", description="electricite | eau | gaz"),
    nb_mois: int = Query(12, ge=2, le=36, description="Nombre de mois à analyser"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Tendances de consommation mensuelle avec détection d'anomalies (écart > 20 % vs moyenne)."""
    from src.core.models.maison_extensions import ReleveCompteur
    from sqlalchemy import func

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            rows = (
                session.query(
                    func.date_trunc("month", ReleveCompteur.date_releve).label("mois"),
                    func.sum(ReleveCompteur.consommation_periode).label("conso"),
                )
                .filter(ReleveCompteur.type_compteur == type_compteur)
                .filter(ReleveCompteur.consommation_periode.isnot(None))
                .group_by(func.date_trunc("month", ReleveCompteur.date_releve))
                .order_by(func.date_trunc("month", ReleveCompteur.date_releve))
                .limit(nb_mois)
                .all()
            )

            points = [
                {"mois": str(r.mois)[:7], "conso": float(r.conso or 0)}
                for r in rows
            ]

            if points:
                moyenne = sum(p["conso"] for p in points) / len(points)
                for p in points:
                    ecart_pct = ((p["conso"] - moyenne) / moyenne * 100) if moyenne else 0
                    p["anomalie"] = abs(ecart_pct) > 20
                    p["ecart_pct"] = round(ecart_pct, 1)
            else:
                moyenne = 0.0

            return {
                "type": type_compteur,
                "points": points,
                "moyenne": round(moyenne, 2),
                "total": len(points),
            }

    return await executer_async(_query)


@router.get("/energie/previsions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def previsions_energie_ia(
    type_compteur: str = Query("electricite", description="electricite | eau | gaz"),
    nb_mois: int = Query(6, ge=3, le=24, description="Nombre de mois pour la régression"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Prévision de consommation du mois prochain par régression linéaire."""
    from datetime import date

    from sqlalchemy import func

    from src.core.models.maison_extensions import ReleveCompteur

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            rows = (
                session.query(
                    func.date_trunc("month", ReleveCompteur.date_releve).label("mois"),
                    func.sum(ReleveCompteur.consommation_periode).label("conso"),
                )
                .filter(ReleveCompteur.type_compteur == type_compteur)
                .filter(ReleveCompteur.consommation_periode.isnot(None))
                .group_by(func.date_trunc("month", ReleveCompteur.date_releve))
                .order_by(func.date_trunc("month", ReleveCompteur.date_releve))
                .limit(nb_mois)
                .all()
            )

            points = [float(r.conso or 0) for r in rows]
            n = len(points)

            if n < 3:
                return {
                    "type": type_compteur,
                    "mois_prochain": None,
                    "consommation_prevue": None,
                    "tendance": "insuffisant",
                    "confiance": 0.0,
                    "message": f"Seulement {n} mois disponible(s) — il faut au moins 3 relevés mensuels.",
                }

            x_vals = list(range(n))
            x_bar = sum(x_vals) / n
            y_bar = sum(points) / n
            ss_xy = sum((x_vals[i] - x_bar) * (points[i] - y_bar) for i in range(n))
            ss_xx = sum((x_vals[i] - x_bar) ** 2 for i in range(n))
            a = ss_xy / ss_xx if ss_xx else 0.0
            b = y_bar - a * x_bar
            conso_prevue = max(0.0, a * n + b)

            ss_res = sum((points[i] - (a * x_vals[i] + b)) ** 2 for i in range(n))
            ss_tot = sum((points[i] - y_bar) ** 2 for i in range(n))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot else 0.0
            confiance = round(max(0.0, min(1.0, r_squared)), 2)

            variation_pct = (a / y_bar * 100) if y_bar else 0.0
            if variation_pct > 5:
                tendance = "hausse"
            elif variation_pct < -5:
                tendance = "baisse"
            else:
                tendance = "stable"

            today = date.today()
            mois_label = f"{today.year + 1}-01" if today.month == 12 else f"{today.year}-{today.month + 1:02d}"

            return {
                "type": type_compteur,
                "mois_prochain": mois_label,
                "consommation_prevue": round(conso_prevue, 1),
                "tendance": tendance,
                "confiance": confiance,
                "pente_mensuelle": round(a, 2),
                "nb_mois_analyses": n,
            }

    return await executer_async(_query)


@router.get("/depenses/{depense_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_depense(
    depense_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'une dépense."""
    from src.services.maison import get_depenses_crud_service

    def _query():
        service = get_depenses_crud_service()
        result = service.get_depense_by_id(depense_id)
        if not result:
            raise HTTPException(status_code=404, detail="Dépense non trouvée")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/depenses", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_depense(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une dépense maison."""
    from src.services.maison import get_depenses_crud_service

    def _query():
        service = get_depenses_crud_service()
        return model_to_dict(service.create_depense(payload))

    return await executer_async(_query)


@router.patch("/depenses/{depense_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_depense(
    depense_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour une dépense."""
    from src.services.maison import get_depenses_crud_service

    def _query():
        service = get_depenses_crud_service()
        return model_to_dict(service.update_depense(depense_id, payload))

    return await executer_async(_query)


@router.delete("/depenses/{depense_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_depense(
    depense_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une dépense."""
    from src.services.maison import get_depenses_crud_service

    def _query():
        service = get_depenses_crud_service()
        service.delete_depense(depense_id)
        return MessageResponse(message="Dépense supprimée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# NUISIBLES (traitements)
# ═══════════════════════════════════════════════════════════


@router.get("/nuisibles", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_nuisibles(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les traitements anti-nuisibles."""
    from src.services.maison import get_nuisibles_crud_service

    def _query():
        service = get_nuisibles_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.get("/nuisibles/prochains", responses=REPONSES_LISTE)
@gerer_exception_api
async def prochains_traitements(
    jours: int = Query(30, ge=1, le=180, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Traitements à effectuer prochainement."""
    from src.services.maison import get_nuisibles_crud_service

    def _query():
        service = get_nuisibles_crud_service()
        return {"items": service.get_prochains_traitements(jours_horizon=jours)}

    return await executer_async(_query)


@router.post("/nuisibles", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_traitement_nuisible(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre un traitement anti-nuisible."""
    from src.services.maison import get_nuisibles_crud_service

    def _query():
        service = get_nuisibles_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.patch("/nuisibles/{traitement_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_traitement_nuisible(
    traitement_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un traitement."""
    from src.services.maison import get_nuisibles_crud_service

    def _query():
        service = get_nuisibles_crud_service()
        return service.update(traitement_id, payload)

    return await executer_async(_query)


@router.delete("/nuisibles/{traitement_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_traitement_nuisible(
    traitement_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un traitement."""
    from src.services.maison import get_nuisibles_crud_service

    def _query():
        service = get_nuisibles_crud_service()
        service.delete(traitement_id)
        return MessageResponse(message="Traitement supprimé")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# DEVIS COMPARATIFS
# ═══════════════════════════════════════════════════════════


@router.get("/devis", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_devis(
    projet_id: int | None = Query(None, description="Filtrer par projet"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les devis comparatifs."""
    from src.services.maison import get_devis_crud_service

    def _query():
        service = get_devis_crud_service()
        return {"items": service.get_all(projet_id=projet_id)}

    return await executer_async(_query)


@router.post("/devis", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_devis(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un devis."""
    from src.services.maison import get_devis_crud_service

    def _query():
        service = get_devis_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.patch("/devis/{devis_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_devis(
    devis_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un devis."""
    from src.services.maison import get_devis_crud_service

    def _query():
        service = get_devis_crud_service()
        return service.update(devis_id, payload)

    return await executer_async(_query)


@router.delete("/devis/{devis_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_devis(
    devis_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un devis et ses lignes."""
    from src.services.maison import get_devis_crud_service

    def _query():
        service = get_devis_crud_service()
        service.delete(devis_id)
        return MessageResponse(message="Devis supprimé")

    return await executer_async(_query)


@router.post("/devis/{devis_id}/lignes", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def ajouter_ligne_devis(
    devis_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute une ligne à un devis."""
    from src.services.maison import get_devis_crud_service

    payload["devis_id"] = devis_id

    def _query():
        service = get_devis_crud_service()
        return service.add_ligne(payload)

    return await executer_async(_query)


@router.post("/devis/{devis_id}/choisir", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def choisir_devis(
    devis_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Accepte un devis (rejette automatiquement les autres du même projet)."""
    from src.services.maison import get_devis_crud_service

    def _query():
        service = get_devis_crud_service()
        return service.choisir_devis(devis_id)

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ENTRETIEN SAISONNIER
# ═══════════════════════════════════════════════════════════


@router.get("/entretien-saisonnier", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_entretien_saisonnier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les tâches d'entretien saisonnier."""
    from src.services.maison import get_entretien_saisonnier_crud_service

    def _query():
        service = get_entretien_saisonnier_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.get("/entretien-saisonnier/alertes", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_entretien_saisonnier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Tâches saisonnières à faire ce mois-ci."""
    from src.services.maison import get_entretien_saisonnier_crud_service

    def _query():
        service = get_entretien_saisonnier_crud_service()
        return {"items": service.get_alertes_saisonnieres()}

    return await executer_async(_query)


@router.post("/entretien-saisonnier", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_entretien_saisonnier(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une tâche d'entretien saisonnier."""
    from src.services.maison import get_entretien_saisonnier_crud_service

    def _query():
        service = get_entretien_saisonnier_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.delete("/entretien-saisonnier/{entretien_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_entretien_saisonnier(
    entretien_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une tâche d'entretien saisonnier."""
    from src.services.maison import get_entretien_saisonnier_crud_service

    def _query():
        service = get_entretien_saisonnier_crud_service()
        service.delete(entretien_id)
        return MessageResponse(message="Tâche saisonnière supprimée")

    return await executer_async(_query)


@router.patch("/entretien-saisonnier/{entretien_id}/fait", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def marquer_entretien_saisonnier_fait(
    entretien_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Marque une tâche saisonnière comme faite."""
    from src.services.maison import get_entretien_saisonnier_crud_service

    def _query():
        service = get_entretien_saisonnier_crud_service()
        return service.marquer_fait(entretien_id)

    return await executer_async(_query)


@router.post("/entretien-saisonnier/reset", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def reset_entretien_saisonnier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Réinitialise la checklist saisonnière pour la nouvelle année."""
    from src.services.maison import get_entretien_saisonnier_crud_service

    def _query():
        service = get_entretien_saisonnier_crud_service()
        service.reset_annuel()
        return {"message": "Checklist saisonnière réinitialisée"}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# RELEVÉS COMPTEURS
# ═══════════════════════════════════════════════════════════


@router.get("/releves", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_releves(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les relevés de compteurs (eau, gaz, électricité)."""
    from src.services.maison import get_releves_crud_service

    def _query():
        service = get_releves_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.post("/releves", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_releve(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre un relevé de compteur."""
    from src.services.maison import get_releves_crud_service

    def _query():
        service = get_releves_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.delete("/releves/{releve_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_releve(
    releve_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un relevé."""
    from src.services.maison import get_releves_crud_service

    def _query():
        service = get_releves_crud_service()
        service.delete(releve_id)
        return MessageResponse(message="Relevé supprimé")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# VISUALISATION PLAN MAISON
# ═══════════════════════════════════════════════════════════


@router.get("/visualisation/pieces", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_pieces(
    etage: int | None = Query(None, description="Filtrer par étage"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les pièces avec détails (objets, travaux, état visuel)."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        return {"items": service.obtenir_pieces_avec_details(etage=etage)}

    return await executer_async(_query)


@router.get("/visualisation/etages", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lister_etages(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les étages disponibles."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        return {"etages": service.obtenir_etages_disponibles()}

    return await executer_async(_query)


@router.get("/visualisation/pieces/{piece_id}/historique", responses=REPONSES_LISTE)
@gerer_exception_api
async def historique_piece(
    piece_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des travaux dans une pièce."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        return service.obtenir_historique_piece(piece_id)

    return await executer_async(_query)


@router.get("/visualisation/pieces/{piece_id}/objets", responses=REPONSES_LISTE)
@gerer_exception_api
async def objets_piece(
    piece_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Objets/meubles dans une pièce."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        return {"items": service.obtenir_objets_piece(piece_id)}

    return await executer_async(_query)


@router.post("/visualisation/positions", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def sauvegarder_positions(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Sauvegarde le layout drag-and-drop des pièces."""
    from src.services.maison import get_visualisation_service

    def _query():
        service = get_visualisation_service()
        service.sauvegarder_positions(payload.get("pieces", []))
        return {"message": "Positions sauvegardées"}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# BRIEFING MAISON (contexte quotidien)
# ═══════════════════════════════════════════════════════════


@router.get("/briefing", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def briefing_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Briefing quotidien contextuel avec tâches, alertes, météo, projets."""
    from src.services.maison import get_contexte_maison_service

    def _query():
        service = get_contexte_maison_service()
        briefing = service.obtenir_briefing()
        if briefing is None:
            return {}
        return briefing.model_dump(mode="json")

    return await executer_async(_query)


@router.get("/alertes", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Toutes les alertes maison triées par urgence."""
    from src.services.maison import get_contexte_maison_service

    def _query():
        service = get_contexte_maison_service()
        alertes = service.obtenir_toutes_alertes()
        return {"items": [a.model_dump(mode="json") for a in alertes]}

    return await executer_async(_query)


@router.get("/taches-jour", responses=REPONSES_LISTE)
@gerer_exception_api
async def taches_jour_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Tâches du jour avec statut et détails."""
    from src.services.maison import get_contexte_maison_service

    def _query():
        service = get_contexte_maison_service()
        taches = service.obtenir_taches_jour()
        return {"items": [t.model_dump(mode="json") for t in taches]}

    return await executer_async(_query)


@router.post("/entretien/sync-catalogue", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def sync_catalogue_entretien(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Force la synchronisation catalogue → tâches d'entretien."""
    from src.services.maison import get_catalogue_entretien_service

    def _query():
        service = get_catalogue_entretien_service()
        result = service.sync_catalogue()
        if result is None:
            return {"message": "Sync échouée"}
        return result.model_dump()

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# RAPPELS MAISON (notifications push)
# ═══════════════════════════════════════════════════════════


@router.post("/rappels/envoyer", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def envoyer_rappels_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Évalue et envoie les rappels push maison (garanties, contrats, entretien, gel, cellier)."""
    from src.services.maison import get_notifications_maison_service

    def _query():
        service = get_notifications_maison_service()
        result = service.evaluer_et_envoyer_rappels()
        if result is None:
            return {"rappels_envoyes": 0, "rappels_ignores": 0, "erreurs": ["Service indisponible"]}
        return result.model_dump()

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# MÉNAGE — Planning semaine & préférences
# ═══════════════════════════════════════════════════════════


@router.get("/menage/planning-semaine", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def planning_semaine_menage(
    date_debut: date | None = Query(None, description="Date début semaine (lundi)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Planning ménage hebdomadaire optimisé par l'IA."""
    from src.services.maison import get_entretien_service

    def _query():
        service = get_entretien_service()
        planning = service.generer_planning_semaine()
        if planning is None:
            return {"planning": {}}
        return {"planning": planning, "date_debut": str(date_debut or date.today())}

    return await executer_async(_query)


@router.post("/menage/preferences", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def sauvegarder_preferences_menage(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Sauvegarde les préférences ménage utilisateur."""
    # Stockage simple dans cache applicatif (remplacement complet)
    from src.core.caching import obtenir_cache

    cache = obtenir_cache()
    cle = f"preferences_menage_{user.get('sub', 'default')}"
    cache.set(cle, payload, ttl=365 * 24 * 3600)
    return {"message": "Préférences sauvegardées", "preferences": payload}


# ═══════════════════════════════════════════════════════════
# FICHE TÂCHE ASSISTÉE
# ═══════════════════════════════════════════════════════════


@router.get("/fiche-tache", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_fiche_tache(
    type: str = Query(..., description="Type: entretien, travaux, jardin, lessive"),
    id: int | None = Query(None, description="ID de la tâche (si entretien)"),
    nom: str | None = Query(None, description="Nom de la tâche (recherche catalogue)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Fiche tâche assistée : étapes, produits, durée, astuce connectée."""
    from src.services.maison import get_fiche_tache_service

    def _query():
        service = get_fiche_tache_service()
        fiche = service.obtenir_fiche(type_tache=type, id_tache=id, nom_tache=nom)
        if fiche is None:
            return {"message": "Tâche non trouvée dans le catalogue"}
        return fiche.model_dump() if hasattr(fiche, "model_dump") else fiche

    return await executer_async(_query)


@router.post("/fiche-tache-ia", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def generer_fiche_tache_ia(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère une fiche tâche personnalisée via IA Mistral."""
    from src.services.maison import get_fiche_tache_service

    def _query():
        service = get_fiche_tache_service()
        nom_tache = payload.get("nom", "")
        contexte = payload.get("contexte", "")
        fiche = service.generer_fiche_ia(nom_tache=nom_tache, contexte=contexte)
        return fiche.model_dump() if hasattr(fiche, "model_dump") else fiche

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# GUIDE LESSIVE & ÉLECTROMÉNAGER
# ═══════════════════════════════════════════════════════════


@router.get("/guide", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def guide_pratique(
    type: str = Query(..., description="Type: lessive, electromenager, travaux"),
    tache: str | None = Query(None, description="Tache ou problème (ex: vin, odeurs)"),
    tissu: str | None = Query(None, description="Type tissu pour lessive"),
    appareil: str | None = Query(None, description="Appareil électroménager"),
    probleme: str | None = Query(None, description="Problème constaté"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Guide pratique : lessive anti-taches, dépannage électroménager, travaux."""
    from src.services.maison import get_fiche_tache_service

    def _query():
        service = get_fiche_tache_service()
        return service.consulter_guide(
            type_guide=type,
            tache=tache,
            tissu=tissu,
            appareil=appareil,
            probleme=probleme,
        )

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ROUTINES PAR DÉFAUT
# ═══════════════════════════════════════════════════════════


@router.post("/routines/initialiser-defaut", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def initialiser_routines_defaut(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée les 3 routines par défaut (matin, soir, weekly) depuis le JSON de référence."""
    from src.services.maison import get_entretien_service

    def _query():
        service = get_entretien_service()
        nb = service.initialiser_routines_defaut()
        return {"routines_creees": nb, "message": f"{nb} routine(s) créée(s)"}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# HUB DATA (stats dashboard)
# ═══════════════════════════════════════════════════════════


@router.get("/hub/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_hub_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques agrégées pour le dashboard maison."""
    from src.services.maison import get_hub_data_service

    def _query():
        service = get_hub_data_service()
        return service.obtenir_stats_db()

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# DOMOTIQUE
# ═══════════════════════════════════════════════════════════


@router.get("/domotique/astuces", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def astuces_domotique(
    categorie: str | None = None,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les astuces et appareils domotique du catalogue."""
    import json
    from pathlib import Path

    def _query():
        chemin = Path("data/reference/astuces_domotique.json")
        if not chemin.exists():
            return {"categories": [], "conseils_generaux": []}
        with open(chemin, encoding="utf-8") as f:
            data = json.load(f)
        if categorie:
            data["categories"] = [
                c for c in data.get("categories", []) if c.get("id") == categorie
            ]
        return data

    return await executer_async(_query)


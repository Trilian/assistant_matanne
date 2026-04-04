"""
Routes API pour le batch cooking.

CRUD complet pour les sessions, étapes et préparations batch cooking.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.batch_cooking import (
    GenererSessionDepuisPlanningRequest,
    GenererSessionDepuisPlanningResponse,
    SessionBatchCreate,
    SessionBatchPatch,
    SessionBatchResponse,
)
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import (
    construire_reponse_paginee,
    executer_async,
    executer_avec_session,
    gerer_exception_api,
)

router = APIRouter(prefix="/api/v1/batch-cooking", tags=["Batch Cooking"])


def _serialiser_session(s: Any) -> dict[str, Any]:
    """Sérialise une session batch cooking en dict."""
    return {
        "id": s.id,
        "nom": s.nom,
        "date_session": s.date_session.isoformat() if s.date_session else None,
        "heure_debut": str(s.heure_debut) if s.heure_debut else None,
        "heure_fin": str(s.heure_fin) if s.heure_fin else None,
        "duree_estimee": s.duree_estimee,
        "duree_reelle": s.duree_reelle,
        "statut": s.statut,
        "avec_jules": s.avec_jules,
        "planning_id": s.planning_id,
        "recettes_selectionnees": s.recettes_selectionnees or [],
        "robots_utilises": s.robots_utilises or [],
        "genere_par_ia": s.genere_par_ia,
        "etapes_count": len(s.etapes) if s.etapes else 0,
        "progression": s.progression if hasattr(s, "progression") else 0.0,
    }


@router.get("", response_model=ReponsePaginee[SessionBatchResponse], responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    statut: str | None = Query(None, description="Filtrer par statut"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les sessions de batch cooking avec pagination."""
    from src.core.models import SessionBatchCooking

    def _query():
        with executer_avec_session() as session:
            query = session.query(SessionBatchCooking)

            if statut:
                query = query.filter(SessionBatchCooking.statut == statut)

            total = query.count()
            items = (
                query.order_by(SessionBatchCooking.date_session.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [_serialiser_session(s) for s in items],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.post(
    "/generer-depuis-planning",
    response_model=GenererSessionDepuisPlanningResponse,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def generer_session_depuis_planning(
    donnees: GenererSessionDepuisPlanningRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère une session batch à partir d'un planning hebdomadaire.

    Collecte toutes les recettes du planning, filtre celles compatibles avec batch cooking,
    calcule durée totale, identifie robots compatibles.
    """
    from src.core.models import Planning, Recette, Repas, SessionBatchCooking

    def _generate():
        with executer_avec_session() as session:
            # Vérifier planning existe
            planning = session.query(Planning).filter(Planning.id == donnees.planning_id).first()
            if not planning:
                raise HTTPException(status_code=404, detail="Planning non trouvé")

            # Collecter tous les repas avec recette_id
            repas_list = (
                session.query(Repas)
                .filter(
                    Repas.planning_id == donnees.planning_id,
                    Repas.recette_id.isnot(None),
                )
                .all()
            )

            # Collecter tous les ID de recettes (plat + entrée + dessert + dessert_jules)
            recette_ids = set()
            for r in repas_list:
                if r.recette_id:
                    recette_ids.add(r.recette_id)
                if r.entree_recette_id:
                    recette_ids.add(r.entree_recette_id)
                if r.dessert_recette_id:
                    recette_ids.add(r.dessert_recette_id)
                if r.dessert_jules_recette_id:
                    recette_ids.add(r.dessert_jules_recette_id)

            if not recette_ids:
                raise HTTPException(
                    status_code=422, detail="Aucune recette trouvée dans le planning"
                )

            # Charger les recettes
            recettes_objs = session.query(Recette).filter(Recette.id.in_(recette_ids)).all()

            # Filtrer celles compatibles batch cooking (ou toutes si aucune marquée)
            recettes_batch = [r for r in recettes_objs if r.compatible_batch]
            if not recettes_batch:
                # Fallback: toutes les recettes
                recettes_batch = recettes_objs

            # Calculer durée totale (temps_preparation + temps_cuisson)
            duree_estimee = sum(r.temps_preparation + (r.temps_cuisson or 0) for r in recettes_batch)

            # Identifier robots compatibles (au moins une recette)
            robots_utilises = []
            for r in recettes_batch:
                if r.compatible_cookeo and "Cookeo" not in robots_utilises:
                    robots_utilises.append("Cookeo")
                if r.compatible_monsieur_cuisine and "Monsieur Cuisine" not in robots_utilises:
                    robots_utilises.append("Monsieur Cuisine")
                if r.compatible_airfryer and "Airfryer" not in robots_utilises:
                    robots_utilises.append("Airfryer")
                if r.compatible_multicooker and "Multicooker" not in robots_utilises:
                    robots_utilises.append("Multicooker")

            # Nom auto-généré si non fourni
            nom = donnees.nom or f"Batch {planning.nom} ({donnees.date_session.strftime('%d/%m')})"

            # Créer la session
            nouvelle = SessionBatchCooking(
                nom=nom,
                date_session=donnees.date_session,
                duree_estimee=duree_estimee,
                avec_jules=donnees.avec_jules,
                planning_id=donnees.planning_id,
                recettes_selectionnees=[r.id for r in recettes_batch],
                robots_utilises=robots_utilises,
                statut="planifiee",
                genere_par_ia=False,
            )
            session.add(nouvelle)
            session.commit()
            session.refresh(nouvelle)

            return {
                "session_id": nouvelle.id,
                "nom": nouvelle.nom,
                "nb_recettes": len(recettes_batch),
                "recettes": [
                    {"id": r.id, "nom": r.nom, "portions": r.portions} for r in recettes_batch
                ],
                "duree_estimee": duree_estimee,
                "robots_utilises": robots_utilises,
            }

    return await executer_async(_generate)


@router.get("/{session_id}", response_model=SessionBatchResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_session(
    session_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère une session batch cooking avec ses étapes."""
    from src.core.models import SessionBatchCooking

    def _query():
        with executer_avec_session() as session:
            s = session.query(SessionBatchCooking).filter(
                SessionBatchCooking.id == session_id
            ).first()
            if not s:
                raise HTTPException(status_code=404, detail="Session non trouvée")

            result = _serialiser_session(s)
            result["etapes"] = [
                {
                    "id": e.id,
                    "ordre": e.ordre,
                    "groupe_parallele": e.groupe_parallele,
                    "titre": e.titre,
                    "duree_minutes": e.duree_minutes,
                    "robots_requis": e.robots_requis or [],
                    "statut": e.statut,
                    "est_terminee": e.est_terminee if hasattr(e, "est_terminee") else False,
                }
                for e in sorted((s.etapes or []), key=lambda x: x.ordre)
            ]
            return result

    return await executer_async(_query)


@router.post("", response_model=SessionBatchResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_session(
    donnees: SessionBatchCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une nouvelle session de batch cooking."""
    from src.core.models import SessionBatchCooking

    def _create():
        with executer_avec_session() as session:
            nouvelle = SessionBatchCooking(
                nom=donnees.nom,
                date_session=donnees.date_session,
                duree_estimee=donnees.duree_estimee,
                avec_jules=donnees.avec_jules,
                planning_id=donnees.planning_id,
                recettes_selectionnees=donnees.recettes_selectionnees,
                robots_utilises=donnees.robots_utilises,
                statut="planifiee",
            )
            session.add(nouvelle)
            session.commit()
            session.refresh(nouvelle)
            return _serialiser_session(nouvelle)

    return await executer_async(_create)


@router.patch("/{session_id}", response_model=SessionBatchResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_session(
    session_id: int,
    patch: SessionBatchPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour partiellement une session batch cooking."""
    from src.core.models import SessionBatchCooking

    def _update():
        with executer_avec_session() as session:
            s = session.query(SessionBatchCooking).filter(
                SessionBatchCooking.id == session_id
            ).first()
            if not s:
                raise HTTPException(status_code=404, detail="Session non trouvée")

            updates = patch.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour")

            ancien_statut = s.statut
            for key, value in updates.items():
                setattr(s, key, value)

            session.commit()
            session.refresh(s)

            if ancien_statut != "terminee" and s.statut == "terminee":
                try:
                    from src.services.core.events import obtenir_bus

                    obtenir_bus().emettre(
                        "batch_cooking.termine",
                        {
                            "session_id": s.id,
                            "planning_id": s.planning_id,
                            "recettes_selectionnees": s.recettes_selectionnees or [],
                            "date_session": s.date_session.isoformat() if s.date_session else None,
                        },
                        source="api.batch_cooking.patch",
                    )
                except Exception:
                    logger.debug("Échec publication événement batch_cooking.termine (non bloquant)")

            return _serialiser_session(s)

    return await executer_async(_update)


@router.delete("/{session_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_session(
    session_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime une session batch cooking."""
    from src.core.models import SessionBatchCooking

    def _delete():
        with executer_avec_session() as session:
            s = session.query(SessionBatchCooking).filter(
                SessionBatchCooking.id == session_id
            ).first()
            if not s:
                raise HTTPException(status_code=404, detail="Session non trouvée")

            session.delete(s)
            session.commit()
            return {"message": "Session supprimée", "id": session_id}

    return await executer_async(_delete)


# ═══════════════════════════════════════════════════════════
# PRÉPARATIONS STOCKÉES
# ═══════════════════════════════════════════════════════════


@router.get("/preparations", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_preparations(
    consomme: bool | None = Query(None, description="Filtrer par consommé / non consommé"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les préparations batch en stock."""
    from src.core.models import PreparationBatch

    def _query():
        with executer_avec_session() as session:
            query = session.query(PreparationBatch)

            if consomme is not None:
                query = query.filter(PreparationBatch.consomme == consomme)

            items = query.order_by(PreparationBatch.date_peremption.asc().nullslast()).all()

            return {
                "items": [
                    {
                        "id": p.id,
                        "nom": p.nom,
                        "portions_initiales": p.portions_initiales,
                        "portions_restantes": p.portions_restantes,
                        "date_preparation": p.date_preparation.isoformat()
                        if p.date_preparation
                        else None,
                        "date_peremption": p.date_peremption.isoformat()
                        if p.date_peremption
                        else None,
                        "localisation": p.localisation,
                        "container": p.container,
                        "consomme": p.consomme,
                        "jours_avant_peremption": p.jours_avant_peremption
                        if hasattr(p, "jours_avant_peremption")
                        else None,
                        "alerte_peremption": p.alerte_peremption
                        if hasattr(p, "alerte_peremption")
                        else False,
                    }
                    for p in items
                ],
            }

    return await executer_async(_query)


@router.post(
    "/preparations/{preparation_id}/consommer",
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def consommer_preparation(
    preparation_id: int,
    portions: int = Query(1, ge=1, description="Nombre de portions à consommer"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Consomme des portions d'une préparation stockée."""
    from src.core.models import PreparationBatch

    def _query():
        with executer_avec_session() as session:
            prep = session.query(PreparationBatch).filter_by(id=preparation_id).first()
            if not prep:
                raise HTTPException(status_code=404, detail="Préparation non trouvée")
            if prep.consomme:
                raise HTTPException(status_code=400, detail="Préparation déjà entièrement consommée")

            restant = prep.consommer_portion(portions)
            session.commit()

            return {
                "id": prep.id,
                "nom": prep.nom,
                "portions_restantes": restant,
                "consomme": prep.consomme,
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# CONFIG BATCH COOKING
# ═══════════════════════════════════════════════════════════


@router.get("/config", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_config(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère la configuration batch cooking de l'utilisateur."""
    from src.core.models import ConfigBatchCooking

    def _query():
        with executer_avec_session() as session:
            config = session.query(ConfigBatchCooking).first()
            if not config:
                return {
                    "jours_batch": [],
                    "heure_debut_preferee": None,
                    "duree_max_session": None,
                    "avec_jules_par_defaut": False,
                    "robots_disponibles": [],
                    "objectif_portions_semaine": 0,
                }

            return {
                "jours_batch": config.jours_batch or [],
                "heure_debut_preferee": str(config.heure_debut_preferee)
                if config.heure_debut_preferee
                else None,
                "duree_max_session": config.duree_max_session,
                "avec_jules_par_defaut": config.avec_jules_par_defaut,
                "robots_disponibles": config.robots_disponibles or [],
                "objectif_portions_semaine": config.objectif_portions_semaine,
            }

    return await executer_async(_query)

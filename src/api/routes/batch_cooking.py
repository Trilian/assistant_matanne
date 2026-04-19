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
    ConfigBatchResponse,
    ConfigBatchUpdate,
    GenererSessionDepuisPlanningRequest,
    GenererSessionDepuisPlanningResponse,
    RecettesDepuisPlanningResponse,
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
    REPONSES_IA,
    REPONSES_LISTE,
)
from src.api.schemas.ia_transverses import BatchCookingIntelligentResponse
from src.api.utils import (
    construire_reponse_paginee,
    executer_async,
    executer_avec_session,
    gerer_exception_api,
)
from src.services.cuisine.service_ia import obtenir_service_innovations_cuisine

router = APIRouter(prefix="/api/v1/batch-cooking", tags=["Batch Cooking"])


@router.get("/intelligent", response_model=BatchCookingIntelligentResponse, responses=REPONSES_IA)
@gerer_exception_api
async def suggestions_batch_cooking_intelligentes(
    user: dict[str, Any] = Depends(require_auth),
) -> BatchCookingIntelligentResponse:
    """Alias métier pour les suggestions de batch cooking intelligentes."""
    service = obtenir_service_innovations_cuisine()
    user_id = str(user.get("id") or "")
    result = service.proposer_batch_cooking_intelligent(user_id=user_id)
    return result or BatchCookingIntelligentResponse()


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
        "preparations_simples": s.preparations_simples if hasattr(s, "preparations_simples") and s.preparations_simples else [],
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


@router.get(
    "/recettes-depuis-planning",
    response_model=RecettesDepuisPlanningResponse,
    responses=REPONSES_CRUD_LECTURE,
)
@gerer_exception_api
async def lister_recettes_depuis_planning(
    planning_id: int = Query(..., description="ID du planning source"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les recettes présentes dans un planning et les préparations sans recette.

    Utilisé pour pré-remplir l'étape de sélection du dialog batch cooking.
    """
    from src.core.models import Planning, Recette, Repas

    def _query():
        with executer_avec_session() as session:
            planning = session.query(Planning).filter(Planning.id == planning_id).first()
            if not planning:
                raise HTTPException(status_code=404, detail="Planning non trouvé")

            repas_list = session.query(Repas).filter(Repas.planning_id == planning_id).all()

            # Collecter les IDs de recettes depuis tous les champs FK
            recette_ids: set[int] = set()
            for r in repas_list:
                for fk in (
                    r.recette_id,
                    r.entree_recette_id,
                    r.dessert_recette_id,
                    r.dessert_jules_recette_id,
                    r.legumes_recette_id,
                    r.feculents_recette_id,
                    r.proteine_accompagnement_recette_id,
                ):
                    if fk:
                        recette_ids.add(fk)

            recettes_objs = (
                session.query(Recette).filter(Recette.id.in_(recette_ids)).all()
                if recette_ids
                else []
            )

            # Collecter les textes libres d'accompagnement (pas de recette associée)
            preparations_simples: list[str] = []
            seen: set[str] = set()
            for r in repas_list:
                for texte in (
                    r.legumes if not r.legumes_recette_id else None,
                    r.feculents if not r.feculents_recette_id else None,
                    r.proteine_accompagnement if not r.proteine_accompagnement_recette_id else None,
                ):
                    if texte and texte.strip() and texte.strip() not in seen:
                        seen.add(texte.strip())
                        preparations_simples.append(texte.strip())

            return {
                "recettes": [
                    {
                        "id": rec.id,
                        "nom": rec.nom,
                        "type_repas": rec.type_repas or "diner",
                        "compatible_batch": bool(rec.compatible_batch),
                    }
                    for rec in recettes_objs
                ],
                "preparations_simples": preparations_simples,
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
    """Génère une session batch à partir d'un planning hebdomadaire ou d'une sélection.

    Si `recettes_selectionnees` est fourni, utilise directement ces IDs.
    Sinon, collecte toutes les recettes du planning (comportement hérité).
    """
    from src.core.models import Planning, Recette, Repas, SessionBatchCooking

    def _generate():
        with executer_avec_session() as session:
            planning = session.query(Planning).filter(Planning.id == donnees.planning_id).first()
            if not planning:
                raise HTTPException(status_code=404, detail="Planning non trouvé")

            # Cas 1 : l'utilisateur a fourni une sélection explicite de recettes
            if donnees.recettes_selectionnees:
                recettes_batch = (
                    session.query(Recette)
                    .filter(Recette.id.in_(donnees.recettes_selectionnees))
                    .all()
                )
                if not recettes_batch:
                    raise HTTPException(
                        status_code=422, detail="Aucune recette trouvée pour les IDs fournis"
                    )
            else:
                # Cas 2 (héritage) : collecter toutes les recettes du planning
                repas_list = (
                    session.query(Repas)
                    .filter(
                        Repas.planning_id == donnees.planning_id,
                        Repas.recette_id.isnot(None),
                    )
                    .all()
                )

                # Filtre par jours_cibles si fourni (logique héritée)
                if donnees.jours_cibles is not None:
                    jours_set = set(donnees.jours_cibles)
                    repas_list = [
                        r for r in repas_list
                        if r.date_repas is not None and r.date_repas.weekday() in jours_set
                    ]

                recette_ids: set[int] = set()
                for r in repas_list:
                    for fk in (r.recette_id, r.entree_recette_id, r.dessert_recette_id, r.dessert_jules_recette_id):
                        if fk:
                            recette_ids.add(fk)

                if not recette_ids:
                    raise HTTPException(
                        status_code=422, detail="Aucune recette trouvée dans le planning"
                    )

                recettes_batch = session.query(Recette).filter(Recette.id.in_(recette_ids)).all()

            # Identifier robots compatibles
            robots_utilises: list[str] = []
            for r in recettes_batch:
                if r.compatible_cookeo and "Cookeo" not in robots_utilises:
                    robots_utilises.append("Cookeo")
                if r.compatible_monsieur_cuisine and "Monsieur Cuisine" not in robots_utilises:
                    robots_utilises.append("Monsieur Cuisine")
                if r.compatible_airfryer and "Airfryer" not in robots_utilises:
                    robots_utilises.append("Airfryer")
                if r.compatible_multicooker and "Multicooker" not in robots_utilises:
                    robots_utilises.append("Multicooker")

            # Durée estimée avec parallélisation
            duree_brute = sum(r.temps_preparation + (r.temps_cuisson or 0) for r in recettes_batch)
            nb_robots = max(1, len(robots_utilises))
            facteur_parallelisation = min(nb_robots, 2.5)
            duree_estimee = max(30, int(duree_brute / facteur_parallelisation))

            nom = donnees.nom or f"Batch {planning.nom} ({donnees.date_session.strftime('%d/%m')})"
            preparations_simples = donnees.preparations_simples or []

            nouvelle = SessionBatchCooking(
                nom=nom,
                date_session=donnees.date_session,
                duree_estimee=duree_estimee,
                avec_jules=donnees.avec_jules,
                planning_id=donnees.planning_id,
                recettes_selectionnees=[r.id for r in recettes_batch],
                robots_utilises=robots_utilises,
                preparations_simples=preparations_simples,
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



@router.get("/{session_id:int}", response_model=SessionBatchResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_session(
    session_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère une session batch cooking avec ses étapes."""
    from src.core.models import SessionBatchCooking

    def _query():
        with executer_avec_session() as session:
            s = (
                session.query(SessionBatchCooking)
                .filter(SessionBatchCooking.id == session_id)
                .first()
            )
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
                    "description": e.description,
                    "est_supervision": e.est_supervision,
                    "temperature": e.temperature,
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
                preparations_simples=donnees.preparations_simples or [],
                statut="planifiee",
            )
            session.add(nouvelle)
            session.commit()
            session.refresh(nouvelle)
            return _serialiser_session(nouvelle)

    return await executer_async(_create)


@router.patch(
    "/{session_id:int}", response_model=SessionBatchResponse, responses=REPONSES_CRUD_ECRITURE
)
@gerer_exception_api
async def modifier_session(
    session_id: int,
    maj: SessionBatchPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour partiellement une session batch cooking."""
    from src.core.models import SessionBatchCooking

    def _update():
        with executer_avec_session() as session:
            s = (
                session.query(SessionBatchCooking)
                .filter(SessionBatchCooking.id == session_id)
                .first()
            )
            if not s:
                raise HTTPException(status_code=404, detail="Session non trouvée")

            updates = maj.model_dump(exclude_unset=True)
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


@router.post(
    "/{session_id:int}/generer-etapes",
    response_model=SessionBatchResponse,
    responses=REPONSES_IA,
)
@gerer_exception_api
async def generer_etapes_session(
    session_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère les étapes IA pour une session batch cooking et les persiste en base.

    Utilise le pipeline détaillé (generer_plan_depuis_planning) qui produit des
    instructions concrètes avec grammes/températures/programmes exact et une
    timeline assignant chaque étape à un appareil (track). Fallback sur le
    pipeline simplifié si le pipeline détaillé échoue.
    """
    from src.core.models import EtapeBatchCooking, Recette, Repas, SessionBatchCooking
    from src.services.cuisine.batch_cooking import obtenir_service_batch_cooking

    # Mapping type_repas DB → clé planning_data ("midi"/"soir")
    _TYPE_REPAS_MAP = {
        "dejeuner": "midi",
        "diner": "soir",
        "repas": "midi",
        "gouter": "soir",
    }
    # Mapping noms display (stockés dans robots_utilises) → clés ROBOTS_INFO
    _ROBOTS_NORMALIZE = {
        "Cookeo": "cookeo",
        "Monsieur Cuisine": "monsieur_cuisine",
        "Airfryer": "airfryer",
        "Multicooker": "multicooker",
        "Four": "four",
        "Plaques": "plaques",
    }
    _JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    def _generate():
        with executer_avec_session() as session:
            s = (
                session.query(SessionBatchCooking)
                .filter(SessionBatchCooking.id == session_id)
                .first()
            )
            if not s:
                raise HTTPException(status_code=404, detail="Session non trouvée")

            recettes_ids: list[int] = s.recettes_selectionnees or []
            if not recettes_ids:
                raise HTTPException(
                    status_code=422,
                    detail="La session ne contient aucune recette",
                )

            robots_raw: list[str] = s.robots_utilises or []
            # Normaliser les noms d'appareils pour le service IA
            robots_user = [
                _ROBOTS_NORMALIZE.get(r, r.lower().replace(" ", "_")) for r in robots_raw
            ] or ["four", "plaques"]

            service = obtenir_service_batch_cooking()

            # ── Pipeline détaillé ──────────────────────────────────────────────
            # Construire planning_data depuis le planning lié ou depuis les recettes
            planning_data: dict = {}
            if s.planning_id:
                repas_list = (
                    session.query(Repas)
                    .filter(
                        Repas.planning_id == s.planning_id,
                        Repas.recette_id.in_(recettes_ids),
                    )
                    .all()
                )
                recette_cache: dict[int, str] = {
                    r.id: r.nom
                    for r in session.query(Recette).filter(Recette.id.in_(recettes_ids)).all()
                }
                for repas in repas_list:
                    if not repas.recette_id:
                        continue
                    nom_recette = recette_cache.get(repas.recette_id, "Recette")
                    type_key = _TYPE_REPAS_MAP.get(repas.type_repas, "midi")
                    jour_key = _JOURS_FR[repas.date_repas.weekday()]
                    repas_data: dict = {
                        "nom": nom_recette,
                        "est_rechauffe": False,
                    }
                    # Inclure les accompagnements pour que l'IA planifie leur préparation
                    if getattr(repas, "legumes", None):
                        repas_data["legumes"] = repas.legumes
                    if getattr(repas, "feculents", None):
                        repas_data["feculents"] = repas.feculents
                    if getattr(repas, "proteine_accompagnement", None):
                        repas_data["proteine_accompagnement"] = repas.proteine_accompagnement
                    if getattr(repas, "entree", None):
                        repas_data["entree"] = repas.entree
                    planning_data.setdefault(jour_key, {})[type_key] = repas_data
            if not planning_data:
                # Pas de planning lié ou planning vide → construire depuis les IDs
                recettes_objs = (
                    session.query(Recette).filter(Recette.id.in_(recettes_ids)).all()
                )
                for i, r in enumerate(recettes_objs):
                    planning_data[f"Plat {i + 1}"] = {
                        "midi": {"nom": r.nom, "est_rechauffe": False}
                    }

            type_session = "collective" if s.avec_jules else "solo"
            plan_detaille = service.generer_plan_depuis_planning(
                planning_data=planning_data,
                type_session=type_session,
                avec_jules=s.avec_jules,
                robots_user=robots_user,
            )

            timeline: list[dict] = plan_detaille.get("timeline", []) if plan_detaille else []

            if timeline:
                # ── Convertir la timeline en étapes avec groupe_parallele ──────
                timeline_sorted = sorted(timeline, key=lambda x: x.get("debut_min", 0))
                groupe_courant = 0
                fin_max = 0
                etapes_a_creer: list[EtapeBatchCooking] = []

                for i, entry in enumerate(timeline_sorted):
                    debut = entry.get("debut_min", 0)
                    fin = entry.get("fin_min", debut)
                    if i > 0 and debut >= fin_max:
                        groupe_courant += 1
                    fin_max = max(fin_max, fin)

                    # track = "vous" pour tâche manuelle, nom robot sinon
                    track = entry.get("track") or entry.get("robot") or "vous"
                    robots_requis = [track] if track and track != "vous" else []

                    etapes_a_creer.append(
                        EtapeBatchCooking(
                            session_id=s.id,
                            ordre=i + 1,
                            groupe_parallele=groupe_courant,
                            titre=entry.get("tache", ""),
                            description=entry.get("detail") or entry.get("description"),
                            duree_minutes=max(0, fin - debut) or None,
                            robots_requis=robots_requis,
                            est_supervision=bool(robots_requis),
                            temperature=entry.get("temperature"),
                            statut="a_faire",
                        )
                    )

                duree_ia = plan_detaille.get("session", {}).get("duree_estimee_minutes")

            else:
                # ── Fallback : pipeline simplifié ─────────────────────────────
                logger.warning(
                    "Pipeline détaillé sans timeline pour session %d, fallback simplifié",
                    session_id,
                )
                plan = service.generer_plan_ia(
                    recettes_ids=recettes_ids,
                    robots_disponibles=robots_raw,
                    avec_jules=s.avec_jules,
                )
                if not plan or not plan.etapes:
                    raise HTTPException(
                        status_code=503,
                        detail="La génération IA n'a pas produit d'étapes. Réessayez.",
                    )
                etapes_a_creer = [
                    EtapeBatchCooking(
                        session_id=s.id,
                        ordre=etape_ia.ordre,
                        groupe_parallele=etape_ia.groupe_parallele,
                        titre=etape_ia.titre,
                        description=etape_ia.description,
                        duree_minutes=etape_ia.duree_minutes,
                        robots_requis=etape_ia.robots or [],
                        est_supervision=etape_ia.est_supervision,
                        alerte_bruit=etape_ia.alerte_bruit,
                        temperature=etape_ia.temperature,
                        statut="a_faire",
                    )
                    for etape_ia in plan.etapes
                ]
                duree_ia = plan.duree_totale_estimee

            # ── Persister les étapes ─────────────────────────────────────────
            for etape_existante in list(s.etapes or []):
                session.delete(etape_existante)
            session.flush()

            for nouv in etapes_a_creer:
                session.add(nouv)

            s.genere_par_ia = True
            if duree_ia:
                s.duree_estimee = duree_ia
            session.commit()
            session.refresh(s)

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
                    "est_terminee": e.est_terminee,
                    "description": e.description,
                    "est_supervision": e.est_supervision,
                    "temperature": e.temperature,
                }
                for e in sorted(s.etapes, key=lambda x: x.ordre)
            ]
            return result

    return await executer_async(_generate)


@router.delete("/{session_id:int}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_session(
    session_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime une session batch cooking."""
    from src.core.models import SessionBatchCooking

    def _delete():
        with executer_avec_session() as session:
            s = (
                session.query(SessionBatchCooking)
                .filter(SessionBatchCooking.id == session_id)
                .first()
            )
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
                raise HTTPException(
                    status_code=400, detail="Préparation déjà entièrement consommée"
                )

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


@router.get("/config", response_model=ConfigBatchResponse, responses=REPONSES_CRUD_LECTURE)
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
                    "jours_batch": [2, 6],
                    "heure_debut_preferee": "10:00",
                    "duree_max_session": 180,
                    "avec_jules_par_defaut": True,
                    "robots_disponibles": ["four", "plaques"],
                    "objectif_portions_semaine": 20,
                    "couverture_jours": {"2": [2, 3, 4], "6": [6, 0, 1, 2]},
                }

            return {
                "jours_batch": config.jours_batch or [2, 6],
                "heure_debut_preferee": str(config.heure_debut_preferee)
                if config.heure_debut_preferee
                else None,
                "duree_max_session": config.duree_max_session,
                "avec_jules_par_defaut": config.avec_jules_par_defaut,
                "robots_disponibles": config.robots_disponibles or [],
                "objectif_portions_semaine": config.objectif_portions_semaine,
                "couverture_jours": config.couverture_jours,
            }

    return await executer_async(_query)


@router.put("/config", response_model=ConfigBatchResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def mettre_a_jour_config(
    donnees: ConfigBatchUpdate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour la configuration batch cooking de l'utilisateur."""
    from datetime import time as dtime

    from src.services.cuisine.batch_cooking import obtenir_service_batch_cooking

    def _update():
        with executer_avec_session() as session:
            service = obtenir_service_batch_cooking()

            # Convertir heure_debut_preferee string "HH:MM" → time
            heure_debut = None
            if donnees.heure_debut_preferee:
                try:
                    h, m = donnees.heure_debut_preferee.split(":")
                    heure_debut = dtime(int(h), int(m))
                except (ValueError, AttributeError):
                    raise HTTPException(
                        status_code=422,
                        detail="Format heure invalide — attendu HH:MM",
                    )

            config = service.update_config(
                jours_batch=donnees.jours_batch,
                heure_debut=heure_debut,
                duree_max=donnees.duree_max_session,
                avec_jules=donnees.avec_jules_par_defaut,
                robots=donnees.robots_disponibles,
                objectif_portions=donnees.objectif_portions_semaine,
                couverture_jours=donnees.couverture_jours,
                notes=donnees.notes,
            )
            if not config:
                raise HTTPException(status_code=500, detail="Échec mise à jour config")

            return {
                "jours_batch": config.jours_batch or [],
                "heure_debut_preferee": str(config.heure_debut_preferee)
                if config.heure_debut_preferee
                else None,
                "duree_max_session": config.duree_max_session,
                "avec_jules_par_defaut": config.avec_jules_par_defaut,
                "robots_disponibles": config.robots_disponibles or [],
                "objectif_portions_semaine": config.objectif_portions_semaine,
                "couverture_jours": config.couverture_jours,
            }

    return await executer_async(_update)

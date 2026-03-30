"""Routes API pour le module Habitat."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.habitat import (
    AnnonceHabitatCreate,
    CritereImmoCreate,
    CritereScenarioCreate,
    PieceHabitatCreate,
    PlanHabitatCreate,
    ProjetDecoHabitatCreate,
    ScenarioHabitatCreate,
    ScenarioHabitatPatch,
    ZoneJardinHabitatCreate,
)
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.core.models.habitat_projet import (
    AnnonceHabitat,
    CritereImmoHabitat,
    CritereScenarioHabitat,
    PieceHabitat,
    PlanHabitat,
    ProjetDecoHabitat,
    ScenarioHabitat,
    ZoneJardinHabitat,
)
from src.services.habitat import obtenir_service_scenarios_habitat

router = APIRouter(prefix="/api/v1/habitat", tags=["Habitat"])


def _to_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


@router.get("/hub", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def habitat_hub(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Résumé consolidé du module Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return {
                "scenarios": session.query(ScenarioHabitat).count(),
                "annonces": session.query(AnnonceHabitat).count(),
                "plans": session.query(PlanHabitat).count(),
                "projets_deco": session.query(ProjetDecoHabitat).count(),
                "zones_jardin": session.query(ZoneJardinHabitat).count(),
            }

    return await executer_async(_query)


@router.get("/scenarios", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_scenarios(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Liste les scénarios Habitat avec leur score global."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            service = obtenir_service_scenarios_habitat()
            items = session.query(ScenarioHabitat).order_by(ScenarioHabitat.score_global.desc()).all()
            result = []
            for scenario in items:
                score = service.calculer_score_global(session, scenario.id)
                scenario.score_global = score
                result.append(
                    {
                        "id": scenario.id,
                        "nom": scenario.nom,
                        "description": scenario.description,
                        "budget_estime": _to_float(scenario.budget_estime),
                        "surface_finale_m2": _to_float(scenario.surface_finale_m2),
                        "nb_chambres": scenario.nb_chambres,
                        "score_global": _to_float(score),
                        "avantages": scenario.avantages or [],
                        "inconvenients": scenario.inconvenients or [],
                        "notes": scenario.notes,
                        "statut": scenario.statut,
                    }
                )
            session.flush()
            return {"items": result}

    return await executer_async(_query)


@router.post("/scenarios", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_scenario(
    payload: ScenarioHabitatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un scénario Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            scenario = ScenarioHabitat(**payload.model_dump())
            session.add(scenario)
            session.flush()
            return {"id": scenario.id, "nom": scenario.nom, "statut": scenario.statut}

    return await executer_async(_query)


@router.patch("/scenarios/{scenario_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_scenario(
    scenario_id: int,
    payload: ScenarioHabitatPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un scénario Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            scenario = session.query(ScenarioHabitat).filter(ScenarioHabitat.id == scenario_id).first()
            if not scenario:
                raise HTTPException(status_code=404, detail="Scenario habitat non trouve")
            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(scenario, key, value)
            session.flush()
            return {
                "id": scenario.id,
                "nom": scenario.nom,
                "statut": scenario.statut,
                "score_global": _to_float(scenario.score_global),
            }

    return await executer_async(_query)


@router.delete("/scenarios/{scenario_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_scenario(
    scenario_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un scénario Habitat."""

    def _query() -> MessageResponse:
        with executer_avec_session() as session:
            scenario = session.query(ScenarioHabitat).filter(ScenarioHabitat.id == scenario_id).first()
            if not scenario:
                raise HTTPException(status_code=404, detail="Scenario habitat non trouve")
            session.delete(scenario)
            return MessageResponse(message="Scenario supprime")

    return await executer_async(_query)


@router.post("/scenarios/{scenario_id}/criteres", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def ajouter_critere_scenario(
    scenario_id: int,
    payload: CritereScenarioCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un critère à un scénario puis recalcule son score."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            scenario = session.query(ScenarioHabitat).filter(ScenarioHabitat.id == scenario_id).first()
            if not scenario:
                raise HTTPException(status_code=404, detail="Scenario habitat non trouve")
            critere = CritereScenarioHabitat(scenario_id=scenario_id, **payload.model_dump())
            session.add(critere)
            session.flush()

            service = obtenir_service_scenarios_habitat()
            scenario.score_global = service.calculer_score_global(session, scenario_id)
            session.flush()

            return {
                "id": critere.id,
                "scenario_id": scenario_id,
                "nom": critere.nom,
                "poids": _to_float(critere.poids),
                "note": _to_float(critere.note),
                "score_global": _to_float(scenario.score_global),
            }

    return await executer_async(_query)


@router.get("/scenarios/comparaison", responses=REPONSES_LISTE)
@gerer_exception_api
async def comparer_scenarios(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Retourne les scénarios ordonnés du meilleur score au plus faible."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            service = obtenir_service_scenarios_habitat()
            scenarios = session.query(ScenarioHabitat).all()
            resultat = []
            for scenario in scenarios:
                score = service.calculer_score_global(session, scenario.id)
                scenario.score_global = score
                resultat.append(
                    {
                        "id": scenario.id,
                        "nom": scenario.nom,
                        "score_global": _to_float(score),
                        "budget_estime": _to_float(scenario.budget_estime),
                        "surface_finale_m2": _to_float(scenario.surface_finale_m2),
                        "nb_chambres": scenario.nb_chambres,
                    }
                )
            session.flush()
            resultat.sort(key=lambda x: x.get("score_global") or 0, reverse=True)
            return {"items": resultat}

    return await executer_async(_query)


@router.get("/criteres-immo", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_criteres_immo(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Liste les critères de recherche immobilière."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            items = session.query(CritereImmoHabitat).order_by(CritereImmoHabitat.id.desc()).all()
            return {
                "items": [
                    {
                        "id": item.id,
                        "nom": item.nom,
                        "departements": item.departements or [],
                        "villes": item.villes or [],
                        "rayon_km": item.rayon_km,
                        "budget_min": _to_float(item.budget_min),
                        "budget_max": _to_float(item.budget_max),
                        "seuil_alerte": _to_float(item.seuil_alerte),
                        "actif": item.actif,
                    }
                    for item in items
                ]
            }

    return await executer_async(_query)


@router.post("/criteres-immo", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_critere_immo(
    payload: CritereImmoCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un critère de veille immobilière."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            item = CritereImmoHabitat(**payload.model_dump())
            session.add(item)
            session.flush()
            return {"id": item.id, "nom": item.nom, "actif": item.actif}

    return await executer_async(_query)


@router.get("/annonces", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_annonces(
    statut: str | None = Query(None),
    source: str | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les annonces immobilières."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            query = session.query(AnnonceHabitat)
            if statut:
                query = query.filter(AnnonceHabitat.statut == statut)
            if source:
                query = query.filter(AnnonceHabitat.source == source)
            items = query.order_by(AnnonceHabitat.score_pertinence.desc()).all()
            return {
                "items": [
                    {
                        "id": a.id,
                        "source": a.source,
                        "url_source": a.url_source,
                        "titre": a.titre,
                        "prix": _to_float(a.prix),
                        "surface_m2": _to_float(a.surface_m2),
                        "ville": a.ville,
                        "statut": a.statut,
                        "score_pertinence": _to_float(a.score_pertinence),
                    }
                    for a in items
                ]
            }

    return await executer_async(_query)


@router.post("/annonces", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_annonce(
    payload: AnnonceHabitatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une annonce (entrée manuelle ou import scraper)."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            annonce = AnnonceHabitat(**payload.model_dump())
            session.add(annonce)
            session.flush()
            return {"id": annonce.id, "source": annonce.source, "statut": annonce.statut}

    return await executer_async(_query)


@router.patch("/annonces/{annonce_id}/statut", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def changer_statut_annonce(
    annonce_id: int,
    statut: str,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour le statut de traitement d'une annonce."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            annonce = session.query(AnnonceHabitat).filter(AnnonceHabitat.id == annonce_id).first()
            if not annonce:
                raise HTTPException(status_code=404, detail="Annonce non trouvee")
            annonce.statut = statut
            session.flush()
            return {"id": annonce.id, "statut": annonce.statut}

    return await executer_async(_query)


@router.get("/plans", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_plans(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Liste les plans Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            items = session.query(PlanHabitat).order_by(PlanHabitat.modifie_le.desc()).all()
            return {
                "items": [
                    {
                        "id": p.id,
                        "scenario_id": p.scenario_id,
                        "nom": p.nom,
                        "type_plan": p.type_plan,
                        "surface_totale_m2": _to_float(p.surface_totale_m2),
                        "budget_estime": _to_float(p.budget_estime),
                        "version": p.version,
                    }
                    for p in items
                ]
            }

    return await executer_async(_query)


@router.post("/plans", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_plan(
    payload: PlanHabitatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un plan Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            plan = PlanHabitat(**payload.model_dump())
            session.add(plan)
            session.flush()
            return {"id": plan.id, "nom": plan.nom, "type_plan": plan.type_plan}

    return await executer_async(_query)


@router.get("/plans/{plan_id}/pieces", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_pieces(plan_id: int, user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Liste les pièces associées à un plan."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            items = session.query(PieceHabitat).filter(PieceHabitat.plan_id == plan_id).all()
            return {
                "items": [
                    {
                        "id": p.id,
                        "plan_id": p.plan_id,
                        "nom": p.nom,
                        "type_piece": p.type_piece,
                        "surface_m2": _to_float(p.surface_m2),
                    }
                    for p in items
                ]
            }

    return await executer_async(_query)


@router.post("/plans/{plan_id}/pieces", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_piece(
    plan_id: int,
    payload: PieceHabitatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute une pièce à un plan."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            plan = session.query(PlanHabitat).filter(PlanHabitat.id == plan_id).first()
            if not plan:
                raise HTTPException(status_code=404, detail="Plan non trouve")
            piece = PieceHabitat(plan_id=plan_id, **payload.model_dump())
            session.add(piece)
            session.flush()
            return {"id": piece.id, "plan_id": piece.plan_id, "nom": piece.nom}

    return await executer_async(_query)


@router.get("/deco/projets", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_projets_deco(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Liste les projets déco Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            items = session.query(ProjetDecoHabitat).order_by(ProjetDecoHabitat.id.desc()).all()
            return {
                "items": [
                    {
                        "id": p.id,
                        "piece_id": p.piece_id,
                        "nom_piece": p.nom_piece,
                        "style": p.style,
                        "budget_prevu": _to_float(p.budget_prevu),
                        "budget_depense": _to_float(p.budget_depense),
                        "statut": p.statut,
                    }
                    for p in items
                ]
            }

    return await executer_async(_query)


@router.post("/deco/projets", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_projet_deco(
    payload: ProjetDecoHabitatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un projet déco Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            projet = ProjetDecoHabitat(**payload.model_dump())
            session.add(projet)
            session.flush()
            return {"id": projet.id, "nom_piece": projet.nom_piece, "statut": projet.statut}

    return await executer_async(_query)


@router.get("/jardin/zones", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_zones_jardin(
    plan_id: int | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les zones de paysagisme Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            query = session.query(ZoneJardinHabitat)
            if plan_id is not None:
                query = query.filter(ZoneJardinHabitat.plan_id == plan_id)
            items = query.order_by(ZoneJardinHabitat.id.desc()).all()
            return {
                "items": [
                    {
                        "id": z.id,
                        "plan_id": z.plan_id,
                        "nom": z.nom,
                        "type_zone": z.type_zone,
                        "surface_m2": _to_float(z.surface_m2),
                        "budget_estime": _to_float(z.budget_estime),
                    }
                    for z in items
                ]
            }

    return await executer_async(_query)


@router.post("/jardin/zones", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_zone_jardin(
    payload: ZoneJardinHabitatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une zone d'aménagement paysager."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            plan = session.query(PlanHabitat).filter(PlanHabitat.id == payload.plan_id).first()
            if not plan:
                raise HTTPException(status_code=404, detail="Plan non trouve")
            zone = ZoneJardinHabitat(**payload.model_dump())
            session.add(zone)
            session.flush()
            return {"id": zone.id, "plan_id": zone.plan_id, "nom": zone.nom}

    return await executer_async(_query)

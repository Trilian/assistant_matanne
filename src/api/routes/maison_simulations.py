"""
Routes API Maison — Simulations, Plans, Terrain.

Endpoints pour :
- CRUD simulations de rénovation
- CRUD scénarios
- Comparaisons multi-scénarios
- CRUD plans 2D/3D
- CRUD zones terrain

Sous-routeur inclus dans maison.py.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.maison import (
    ComparaisonScenariosResponse,
    PlanMaisonCreate,
    PlanMaisonPatch,
    PlanMaisonResponse,
    ScenarioCreate,
    ScenarioPatch,
    ScenarioResponse,
    SimulationCreate,
    SimulationPatch,
    SimulationResponse,
    ZoneTerrainCreate,
    ZoneTerrainPatch,
    ZoneTerrainResponse,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.core.backup.utils_serialization import model_to_dict

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Maison - Simulations"])

# ════════════════════════════════════════════════════════════════════════════
# SIMULATIONS RÉNOVATION
# ════════════════════════════════════════════════════════════════════════════


@router.get("/simulations", response_model=dict)
@gerer_exception_api
async def lister_simulations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    statut: str | None = Query(None, description="Filtrer par statut"),
    type_projet: str | None = Query(None, description="Filtrer par type de projet"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les simulations de rénovation."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.lister_simulations(
            statut=statut,
            type_projet=type_projet,
            page=page,
            page_size=page_size,
        )

    return await executer_async(_query)


@router.get("/simulations/{simulation_id}", response_model=SimulationResponse)
@gerer_exception_api
async def obtenir_simulation(
    simulation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère une simulation avec ses scénarios."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.obtenir_simulation(simulation_id)

    return await executer_async(_query)


@router.post("/simulations", response_model=SimulationResponse, status_code=201)
@gerer_exception_api
async def creer_simulation(
    data: SimulationCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une nouvelle simulation de rénovation."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.creer_simulation(data.model_dump(exclude_unset=True))

    return await executer_async(_query)


@router.patch("/simulations/{simulation_id}", response_model=SimulationResponse)
@gerer_exception_api
async def modifier_simulation(
    simulation_id: int,
    data: SimulationPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie une simulation."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.modifier_simulation(
            simulation_id,
            data.model_dump(exclude_unset=True),
        )

    return await executer_async(_query)


@router.delete("/simulations/{simulation_id}")
@gerer_exception_api
async def supprimer_simulation(
    simulation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une simulation et ses scénarios."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        service.supprimer_simulation(simulation_id)
        return {"message": f"Simulation {simulation_id} supprimée"}

    return await executer_async(_query)


@router.post("/simulations/{simulation_id}/dupliquer", response_model=SimulationResponse)
@gerer_exception_api
async def dupliquer_simulation(
    simulation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Duplique une simulation avec ses scénarios."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.dupliquer_simulation(simulation_id)

    return await executer_async(_query)


# ════════════════════════════════════════════════════════════════════════════
# SCÉNARIOS
# ════════════════════════════════════════════════════════════════════════════


@router.get("/simulations/{simulation_id}/scenarios", response_model=list[ScenarioResponse])
@gerer_exception_api
async def lister_scenarios(
    simulation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> list[dict[str, Any]]:
    """Liste les scénarios d'une simulation."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.lister_scenarios(simulation_id)

    return await executer_async(_query)


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
@gerer_exception_api
async def obtenir_scenario(
    scenario_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère un scénario."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.obtenir_scenario(scenario_id)

    return await executer_async(_query)


@router.post(
    "/simulations/{simulation_id}/scenarios",
    response_model=ScenarioResponse,
    status_code=201,
)
@gerer_exception_api
async def creer_scenario(
    simulation_id: int,
    data: ScenarioCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un scénario dans une simulation."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.creer_scenario(
            simulation_id,
            data.model_dump(exclude_unset=True),
        )

    return await executer_async(_query)


@router.patch("/scenarios/{scenario_id}", response_model=ScenarioResponse)
@gerer_exception_api
async def modifier_scenario(
    scenario_id: int,
    data: ScenarioPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie un scénario."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.modifier_scenario(
            scenario_id,
            data.model_dump(exclude_unset=True),
        )

    return await executer_async(_query)


@router.delete("/scenarios/{scenario_id}")
@gerer_exception_api
async def supprimer_scenario(
    scenario_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un scénario."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        service.supprimer_scenario(scenario_id)
        return {"message": f"Scénario {scenario_id} supprimé"}

    return await executer_async(_query)


@router.get(
    "/simulations/{simulation_id}/comparer",
    response_model=ComparaisonScenariosResponse,
)
@gerer_exception_api
async def comparer_scenarios(
    simulation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Compare tous les scénarios d'une simulation."""

    def _query():
        from src.services.maison.simulation_service import get_simulation_service

        service = get_simulation_service()
        return service.comparer_scenarios(simulation_id)

    return await executer_async(_query)


# ════════════════════════════════════════════════════════════════════════════
# PLANS MAISON (2D/3D)
# ════════════════════════════════════════════════════════════════════════════


@router.get("/plans", response_model=dict)
@gerer_exception_api
async def lister_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type_plan: str | None = Query(None, description="Filtrer par type"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les plans."""

    def _query():
        from src.services.maison.plan_2d_service import get_plan_2d_service

        service = get_plan_2d_service()
        return service.lister_plans(
            type_plan=type_plan,
            page=page,
            page_size=page_size,
        )

    return await executer_async(_query)


@router.get("/plans/{plan_id}", response_model=PlanMaisonResponse)
@gerer_exception_api
async def obtenir_plan(
    plan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère un plan."""

    def _query():
        from src.services.maison.plan_2d_service import get_plan_2d_service

        service = get_plan_2d_service()
        return service.obtenir_plan(plan_id)

    return await executer_async(_query)


@router.post("/plans", response_model=PlanMaisonResponse, status_code=201)
@gerer_exception_api
async def creer_plan(
    data: PlanMaisonCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un nouveau plan."""

    def _query():
        from src.services.maison.plan_2d_service import get_plan_2d_service

        service = get_plan_2d_service()
        return service.creer_plan(data.model_dump(exclude_unset=True))

    return await executer_async(_query)


@router.patch("/plans/{plan_id}", response_model=PlanMaisonResponse)
@gerer_exception_api
async def modifier_plan(
    plan_id: int,
    data: PlanMaisonPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie un plan."""

    def _query():
        from src.services.maison.plan_2d_service import get_plan_2d_service

        service = get_plan_2d_service()
        return service.modifier_plan(
            plan_id,
            data.model_dump(exclude_unset=True),
        )

    return await executer_async(_query)


@router.delete("/plans/{plan_id}")
@gerer_exception_api
async def supprimer_plan(
    plan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un plan."""

    def _query():
        from src.services.maison.plan_2d_service import get_plan_2d_service

        service = get_plan_2d_service()
        service.supprimer_plan(plan_id)
        return {"message": f"Plan {plan_id} supprimé"}

    return await executer_async(_query)


@router.post("/plans/{plan_id}/dupliquer", response_model=PlanMaisonResponse)
@gerer_exception_api
async def dupliquer_plan(
    plan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Duplique un plan."""

    def _query():
        from src.services.maison.plan_2d_service import get_plan_2d_service

        service = get_plan_2d_service()
        return service.dupliquer_plan(plan_id)

    return await executer_async(_query)


@router.post("/plans/{plan_id}/canvas")
@gerer_exception_api
async def sauvegarder_canvas(
    plan_id: int,
    donnees: dict = None,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Sauvegarde les données canvas (react-konva) d'un plan."""
    if donnees is None:
        donnees = {}

    def _query():
        from src.services.maison.plan_2d_service import get_plan_2d_service

        service = get_plan_2d_service()
        service.sauvegarder_canvas(plan_id, donnees)
        return {"message": "Canvas sauvegardé"}

    return await executer_async(_query)


@router.get("/plans/{plan_id}/canvas")
@gerer_exception_api
async def charger_canvas(
    plan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Charge les données canvas pour l'édition."""

    def _query():
        from src.services.maison.plan_2d_service import get_plan_2d_service

        service = get_plan_2d_service()
        return service.charger_canvas(plan_id)

    return await executer_async(_query)


# ════════════════════════════════════════════════════════════════════════════
# ZONES TERRAIN
# ════════════════════════════════════════════════════════════════════════════


@router.get("/zones-terrain", response_model=dict)
@gerer_exception_api
async def lister_zones_terrain(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type_zone: str | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les zones du terrain."""

    def _query():
        from src.core.db import obtenir_contexte_db
        from src.core.models.maison_extensions import ZoneTerrain

        with obtenir_contexte_db() as db:
            query = db.query(ZoneTerrain)
            if type_zone:
                query = query.filter(ZoneTerrain.type_zone == type_zone)

            total = query.count()
            items = (
                query.order_by(ZoneTerrain.nom)
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [model_to_dict(z) for z in items],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    return await executer_async(_query)


@router.post("/zones-terrain", response_model=ZoneTerrainResponse, status_code=201)
@gerer_exception_api
async def creer_zone_terrain(
    data: ZoneTerrainCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une zone du terrain."""

    def _query():
        from src.core.db import obtenir_contexte_db
        from src.core.models.maison_extensions import ZoneTerrain

        with obtenir_contexte_db() as db:
            zone = ZoneTerrain(**data.model_dump(exclude_unset=True))
            db.add(zone)
            db.commit()
            db.refresh(zone)
            return model_to_dict(zone)

    return await executer_async(_query)


@router.patch("/zones-terrain/{zone_id}", response_model=ZoneTerrainResponse)
@gerer_exception_api
async def modifier_zone_terrain(
    zone_id: int,
    data: ZoneTerrainPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie une zone du terrain."""

    def _query():
        from src.core.db import obtenir_contexte_db
        from src.core.models.maison_extensions import ZoneTerrain

        with obtenir_contexte_db() as db:
            zone = db.query(ZoneTerrain).filter_by(id=zone_id).first()
            if not zone:
                raise ValueError(f"Zone {zone_id} introuvable")

            for key, value in data.model_dump(exclude_unset=True).items():
                if value is not None:
                    setattr(zone, key, value)

            db.commit()
            db.refresh(zone)
            return model_to_dict(zone)

    return await executer_async(_query)


@router.delete("/zones-terrain/{zone_id}")
@gerer_exception_api
async def supprimer_zone_terrain(
    zone_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une zone du terrain."""

    def _query():
        from src.core.db import obtenir_contexte_db
        from src.core.models.maison_extensions import ZoneTerrain

        with obtenir_contexte_db() as db:
            zone = db.query(ZoneTerrain).filter_by(id=zone_id).first()
            if not zone:
                raise ValueError(f"Zone {zone_id} introuvable")
            db.delete(zone)
            db.commit()
            return {"message": f"Zone {zone_id} supprimée"}

    return await executer_async(_query)

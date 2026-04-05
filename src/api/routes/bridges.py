"""
Routes API — Bridges inter-modules (B5).

Documents expirés, planning unifié, alertes météo→entretien.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_LISTE
from src.api.schemas.ia_bridges import (
    BudgetUnifieResponse,
    DocumentsExpiresResponse,
    ImpactDemenagementResponse,
    PlanningUnifieResponse,
    TerroirRecettesResponse,
    VerificationStockRecetteResponse,
    WidgetSaisonJardinResponse,
    WidgetVeilleImmoResponse,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bridges", tags=["Bridges Inter-Modules"])


@router.get("/catalogue", responses=REPONSES_LISTE)
@gerer_exception_api
async def catalogue_bridges(
    user: dict = Depends(require_auth),
):
    """Expose le catalogue consolidé des bridges legacy et stables."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.obtenir_catalogue_consolidation()


@router.get("/documents-expires", response_model=DocumentsExpiresResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def documents_expires(
    jours_avant: int = Query(30, ge=1, le=365, description="Horizon en jours"),
    user: dict = Depends(require_auth),
):
    """Liste les documents expirés ou expirant bientôt (B5.3)."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    alertes = service.documents_expires_alertes(jours_avant=jours_avant)

    nb_expires = sum(1 for a in alertes if a.get("est_expire"))
    nb_bientot = len(alertes) - nb_expires

    return {
        "alertes": alertes,
        "nb_expires": nb_expires,
        "nb_bientot": nb_bientot,
    }


@router.get("/planning-unifie", response_model=PlanningUnifieResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def planning_unifie(
    nb_jours: int = Query(7, ge=1, le=30, description="Nombre de jours à afficher"),
    user: dict = Depends(require_auth),
):
    """Planning unifié multi-modules: entretien + activités (B5.5 / B2.8)."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    taches = service.entretien_planning_unifie(nb_jours=nb_jours)

    nb_en_retard = sum(1 for t in taches if t.get("en_retard"))

    return {
        "taches": taches,
        "nb_total": len(taches),
        "nb_en_retard": nb_en_retard,
    }


@router.get("/recolte-recettes", responses=REPONSES_LISTE)
@gerer_exception_api
async def recolte_recettes(
    ingredient: str = Query(..., min_length=2, description="Ingrédient récolté"),
    user: dict = Depends(require_auth),
):
    """Trouve des recettes utilisant un ingrédient récolté au jardin (B5.1)."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    recettes = service.recolte_vers_recettes(ingredient)

    return {
        "ingredient": ingredient,
        "recettes": recettes,
        "nb_recettes": len(recettes),
    }


@router.get("/anniversaire-menu-festif", responses=REPONSES_LISTE)
@gerer_exception_api
async def anniversaire_menu_festif(
    jours_horizon: int = Query(14, ge=1, le=60, description="Horizon en jours"),
    user: dict = Depends(require_auth),
):
    """Suggère un menu festif pour l'anniversaire le plus proche."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.anniversaire_vers_menu_festif(jours_horizon=jours_horizon)


@router.get("/energie-heures-creuses", responses=REPONSES_LISTE)
@gerer_exception_api
async def energie_heures_creuses(
    user: dict = Depends(require_auth),
):
    """IM-5: Recommande les créneaux HC/HP pour les machines énergivores."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.energie_hc_hp_vers_planning_machines()


@router.post("/meteo-entretien", responses=REPONSES_LISTE)
@gerer_exception_api
async def meteo_entretien(
    conditions: dict[str, Any],
    user: dict = Depends(require_auth),
):
    """Génère des alertes entretien basées sur les conditions météo (B5.8)."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    alertes = service.meteo_vers_entretien(conditions)

    return {"alertes": alertes, "nb_alertes": len(alertes)}


# ═══════════════════════════════════════════════════════════
# P3 — BRIDGES INTER-MODULES ENRICHIS
# ═══════════════════════════════════════════════════════════


@router.get("/terroir-recettes", response_model=TerroirRecettesResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def terroir_recettes(
    localisation: str | None = Query(None, description="Localisation ou région"),
    user: dict = Depends(require_auth),
):
    """P3-A1: Suggère des recettes régionales basées sur la localisation."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.terroir_vers_recettes(localisation=localisation)


@router.get("/budget-unifie", response_model=BudgetUnifieResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def budget_unifie(
    mois: int | None = Query(None, ge=1, le=12, description="Mois (1-12)"),
    annee: int | None = Query(None, ge=2020, le=2100, description="Année"),
    user: dict = Depends(require_auth),
):
    """P3-A2: Budget unifié charges maison + dépenses famille."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.budget_unifie(mois=mois, annee=annee)


@router.get("/impact-demenagement/{scenario_id}", response_model=ImpactDemenagementResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def impact_demenagement(
    scenario_id: int,
    user: dict = Depends(require_auth),
):
    """P3-A3: Évalue l'impact familial d'un scénario de déménagement."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.impact_demenagement(scenario_id=scenario_id)


@router.get("/widget-veille-immo", response_model=WidgetVeilleImmoResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def widget_veille_immo(
    user: dict = Depends(require_auth),
):
    """P3-A4: Données pour le widget veille immobilière du dashboard."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.widget_veille_immo()


@router.get("/widget-saison-jardin", response_model=WidgetSaisonJardinResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def widget_saison_jardin(
    user: dict = Depends(require_auth),
):
    """P3-A5: Données saisonnières du jardin pour le widget dashboard."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.widget_saison_jardin()


@router.get("/activites-jules-potager", responses=REPONSES_LISTE)
@gerer_exception_api
async def activites_jules_potager(
    user: dict = Depends(require_auth),
):
    """P3-A6: Activités jardinage adaptées à Jules."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.activites_jules_potager()


@router.get("/verification-stock-recette/{recette_id}", response_model=VerificationStockRecetteResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def verification_stock_recette(
    recette_id: int,
    user: dict = Depends(require_auth),
):
    """P3-B3: Vérifie le stock pour une recette planifiée."""
    from src.services.ia.inter_modules import obtenir_service_bridges

    service = obtenir_service_bridges()
    return service.verifier_stock_recette(recette_id=recette_id)

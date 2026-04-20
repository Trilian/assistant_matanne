"""Routes API pour le module Habitat."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.schemas.habitat import (
    AnnonceHabitatCreate,
    CritereImmoCreate,
    CritereScenarioCreate,
    GenerationImageHabitatCreate,
    PieceHabitatCreate,
    PlanHabitatConfiguration3DUpdate,
    PlanHabitatAnalyseCreate,
    PlanHabitatCanvasPayload,
    PlanHabitatCreate,
    ProjetDecoDepenseCreate,
    ProjetDecoHabitatCreate,
    ProjetDecoSuggestionCreate,
    ScenarioHabitatCreate,
    ScenarioHabitatPatch,
    SynchronisationVeilleHabitatCreate,
    ZoneJardinHabitatCreate,
    ZoneJardinHabitatPatch,
)
from src.api.schemas.ia_transverses import (
    AnomaliesEnergieResponse,
    ComparateurEnergieRequest,
    ComparateurEnergieResponse,
    EnergieTempsReelResponse,
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
from src.services.habitat.deco_service import obtenir_service_deco_habitat
from src.services.habitat.dvf_service import obtenir_service_dvf_habitat
from src.services.habitat.plans_ai_service import obtenir_service_plans_habitat
from src.services.habitat.scenarios_service import obtenir_service_scenarios_habitat
from src.services.habitat.service_ia import obtenir_service_innovations_habitat
from src.services.habitat.veille_service import obtenir_service_veille_habitat
from src.services.integrations.image_generation import obtenir_service_generation_image

router = APIRouter(prefix="/api/v1/vision-maison", tags=["Vision Maison"])
REPONSES_LISTE_TYPED = cast(dict[int | str, dict[str, Any]], REPONSES_LISTE)
REPONSES_CRUD_LECTURE_TYPED = cast(dict[int | str, dict[str, Any]], REPONSES_CRUD_LECTURE)
REPONSES_CRUD_CREATION_TYPED = cast(dict[int | str, dict[str, Any]], REPONSES_CRUD_CREATION)
REPONSES_CRUD_SUPPRESSION_TYPED = cast(dict[int | str, dict[str, Any]], REPONSES_CRUD_SUPPRESSION)


def _to_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _charger_canvas_plan(plan: PlanHabitat) -> dict[str, Any]:
    donnees = cast(dict[str, Any], plan.donnees_pieces or {})
    return {
        "id": plan.id,
        "nom": plan.nom,
        "type_plan": plan.type_plan,
        "version": plan.version,
        "largeur_canvas": int(donnees.get("largeur_canvas") or 1200),
        "hauteur_canvas": int(donnees.get("hauteur_canvas") or 800),
        "donnees_canvas": cast(dict[str, Any], donnees.get("canvas_2d") or {}),
    }


@router.get("/hub", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def habitat_hub(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Résumé consolidé du module Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            alertes = obtenir_service_veille_habitat().lister_alertes(session)
            depenses_deco = session.query(ProjetDecoHabitat).all()
            return {
                "scenarios": session.query(ScenarioHabitat).count(),
                "annonces": session.query(AnnonceHabitat).count(),
                "plans": session.query(PlanHabitat).count(),
                "projets_deco": session.query(ProjetDecoHabitat).count(),
                "zones_jardin": session.query(ZoneJardinHabitat).count(),
                "alertes": len(alertes),
                "annonces_a_traiter": session.query(AnnonceHabitat)
                .filter(AnnonceHabitat.statut.in_(["nouveau", "alerte"]))
                .count(),
                "budget_deco_total": round(
                    sum(float(item.budget_prevu or 0) for item in depenses_deco), 2
                ),
                "budget_deco_depense": round(
                    sum(float(item.budget_depense or 0) for item in depenses_deco), 2
                ),
            }

    return await executer_async(_query)


@router.get(
    "/anomalies-energie",
    response_model=AnomaliesEnergieResponse,
    responses=REPONSES_CRUD_LECTURE_TYPED,
)
@gerer_exception_api
async def obtenir_anomalies_energie(
    user: dict[str, Any] = Depends(require_auth),
) -> AnomaliesEnergieResponse:
    """Alias métier pour la détection d'anomalies énergie."""
    service = obtenir_service_innovations_habitat()
    result = service.detecter_anomalies_energie()
    return result or AnomaliesEnergieResponse()


@router.post(
    "/comparateur-energie",
    response_model=ComparateurEnergieResponse,
    responses=REPONSES_CRUD_CREATION_TYPED,
)
@gerer_exception_api
async def comparer_fournisseurs_energie(
    body: ComparateurEnergieRequest,
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
) -> ComparateurEnergieResponse:
    """Alias métier pour le comparateur de fournisseurs énergie."""
    service = obtenir_service_innovations_habitat()
    result = service.comparer_fournisseurs_energie(
        prix_kwh_actuel_eur=body.prix_kwh_actuel_eur,
        abonnement_mensuel_eur=body.abonnement_mensuel_eur,
    )
    return result or ComparateurEnergieResponse()


@router.get(
    "/energie-temps-reel",
    response_model=EnergieTempsReelResponse,
    responses=REPONSES_CRUD_LECTURE_TYPED,
)
@gerer_exception_api
async def obtenir_energie_temps_reel(
    user: dict[str, Any] = Depends(require_auth),
) -> EnergieTempsReelResponse:
    """Alias métier pour le tableau énergie temps réel."""
    service = obtenir_service_innovations_habitat()
    result = service.obtenir_tableau_bord_energie_temps_reel()
    return result or EnergieTempsReelResponse()


@router.post("/veille/synchroniser", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
@gerer_exception_api
async def synchroniser_veille(
    payload: SynchronisationVeilleHabitatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Lance une synchronisation réelle des sources immobilières."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            service = obtenir_service_veille_habitat()
            return service.synchroniser_annonces(
                session,
                user_id=str(user.get("id") or "dev"),
                critere_id=payload.critere_id,
                limite_par_source=payload.limite_par_source,
                sources=payload.sources,
                envoyer_alertes=payload.envoyer_alertes,
            )

    return await executer_async(_query)


@router.get("/veille/alertes", responses=REPONSES_LISTE_TYPED)
@gerer_exception_api
async def lister_alertes_veille(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Retourne les meilleures opportunités détectées par la veille."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return {"items": obtenir_service_veille_habitat().lister_alertes(session)}

    return await executer_async(_query)


@router.get("/veille/carte", responses=REPONSES_LISTE_TYPED)
@gerer_exception_api
async def carte_veille(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Agrège les annonces par ville avec coordonnées pour affichage carte."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return {"items": obtenir_service_veille_habitat().carte_annonces(session)}

    return await executer_async(_query)


@router.get("/marche/dvf", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def marche_dvf(
    departement: str | None = Query(None),
    code_postal: str | None = Query(None),
    commune: str | None = Query(None),
    type_local: str | None = Query(None),
    nb_pieces_min: int | None = Query(None, ge=1),
    surface_min_m2: float | None = Query(None, ge=0),
    limite: int = Query(180, ge=25, le=250),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Expose un historique de marche Habitat fonde sur les transactions DVF publiques."""

    return obtenir_service_dvf_habitat().obtenir_historique_marche(
        departement=departement,
        code_postal=code_postal,
        commune=commune,
        type_local=type_local,
        nb_pieces_min=nb_pieces_min,
        surface_min_m2=surface_min_m2,
        limite=limite,
    )


@router.get("/marche/barometre", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def marche_barometre(
    type_local: str | None = Query(None),
    ma_commune: str | None = Query(None),
    mon_code_postal: str | None = Query(None),
    limite_par_ville: int = Query(80, ge=25, le=150),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Baromètre national : compare prix/m² de villes de référence via DVF.

    Paramètres optionnels `ma_commune` / `mon_code_postal` permettent d'inclure
    la zone locale dans la comparaison pour se situer par rapport aux références.
    """

    return await executer_async(
        lambda: obtenir_service_dvf_habitat().obtenir_barometre(
            type_local=type_local,
            ma_commune=ma_commune,
            mon_code_postal=mon_code_postal,
            limite_par_ville=limite_par_ville,
        )
    )


@router.get("/scenarios", responses=REPONSES_LISTE_TYPED)
@gerer_exception_api
async def lister_scenarios(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Liste les scénarios Habitat avec leur score global."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            service = obtenir_service_scenarios_habitat()
            items = (
                session.query(ScenarioHabitat).order_by(ScenarioHabitat.score_global.desc()).all()
            )
            result: list[dict[str, Any]] = []
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


@router.post("/scenarios", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
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


@router.patch("/scenarios/{scenario_id}", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def modifier_scenario(
    scenario_id: int,
    payload: ScenarioHabitatPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un scénario Habitat."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            scenario = (
                session.query(ScenarioHabitat).filter(ScenarioHabitat.id == scenario_id).first()
            )
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


@router.delete("/scenarios/{scenario_id}", responses=REPONSES_CRUD_SUPPRESSION_TYPED)
@gerer_exception_api
async def supprimer_scenario(
    scenario_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un scénario Habitat."""

    def _query() -> MessageResponse:
        with executer_avec_session() as session:
            scenario = (
                session.query(ScenarioHabitat).filter(ScenarioHabitat.id == scenario_id).first()
            )
            if not scenario:
                raise HTTPException(status_code=404, detail="Scenario habitat non trouve")
            session.delete(scenario)
            return MessageResponse(message="Scenario supprime")

    return await executer_async(_query)


@router.post(
    "/scenarios/{scenario_id}/criteres", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED
)
@gerer_exception_api
async def ajouter_critere_scenario(
    scenario_id: int,
    payload: CritereScenarioCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un critère à un scénario puis recalcule son score."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            scenario = (
                session.query(ScenarioHabitat).filter(ScenarioHabitat.id == scenario_id).first()
            )
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


@router.get("/scenarios/comparaison", responses=REPONSES_LISTE_TYPED)
@gerer_exception_api
async def comparer_scenarios(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Retourne les scénarios ordonnés du meilleur score au plus faible."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            service = obtenir_service_scenarios_habitat()
            scenarios = session.query(ScenarioHabitat).all()
            resultat: list[dict[str, Any]] = []
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


@router.get("/criteres-immo", responses=REPONSES_LISTE_TYPED)
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


@router.post("/criteres-immo", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
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


@router.get("/annonces", responses=REPONSES_LISTE_TYPED)
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
                        "surface_terrain_m2": _to_float(a.surface_terrain_m2),
                        "nb_pieces": a.nb_pieces,
                        "ville": a.ville,
                        "code_postal": a.code_postal,
                        "statut": a.statut,
                        "score_pertinence": _to_float(a.score_pertinence),
                        "prix_m2_secteur": _to_float(a.prix_m2_secteur),
                        "ecart_prix_pct": _to_float(a.ecart_prix_pct),
                    }
                    for a in items
                ]
            }

    return await executer_async(_query)


@router.post("/annonces", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
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


@router.patch("/annonces/{annonce_id}/statut", responses=REPONSES_CRUD_LECTURE_TYPED)
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


@router.get("/plans", responses=REPONSES_LISTE_TYPED)
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
                        "image_importee_url": p.image_importee_url,
                        "surface_totale_m2": _to_float(p.surface_totale_m2),
                        "budget_estime": _to_float(p.budget_estime),
                        "version": p.version,
                        "suggestions_ia": cast(dict[str, Any], p.donnees_pieces or {}).get(
                            "suggestions_ia", []
                        ),
                    }
                    for p in items
                ]
            }

    return await executer_async(_query)


@router.post("/plans/{plan_id}/analyser", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
@gerer_exception_api
async def analyser_plan_habitat(
    plan_id: int,
    payload: PlanHabitatAnalyseCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse un plan Habitat avec le pipeline IA."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return obtenir_service_plans_habitat().analyser_plan(
                session,
                plan_id=plan_id,
                prompt_utilisateur=payload.prompt_utilisateur,
                generer_image=payload.generer_image,
            )

    return await executer_async(_query)


@router.get("/plans/{plan_id}/historique-ia", responses=REPONSES_LISTE_TYPED)
@gerer_exception_api
async def historique_plan_habitat(
    plan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des analyses et propositions IA sur un plan."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return {"items": obtenir_service_plans_habitat().historique_plan(session, plan_id)}

    return await executer_async(_query)


@router.post("/plans", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
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


@router.get("/plans/{plan_id}/canvas", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def charger_canvas_plan(
    plan_id: int, user: dict[str, Any] = Depends(require_auth)
) -> dict[str, Any]:
    """Charge le canvas 2D du plan Habitat pour l'éditeur technique."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            plan = session.query(PlanHabitat).filter(PlanHabitat.id == plan_id).first()
            if not plan:
                raise HTTPException(status_code=404, detail="Plan non trouve")
            return _charger_canvas_plan(plan)

    return await executer_async(_query)


@router.post("/plans/{plan_id}/canvas", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def sauvegarder_canvas_plan(
    plan_id: int,
    payload: PlanHabitatCanvasPayload,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Sauvegarde le canvas 2D du plan Habitat dans la même source de vérité."""

    def _query() -> MessageResponse:
        with executer_avec_session() as session:
            plan = session.query(PlanHabitat).filter(PlanHabitat.id == plan_id).first()
            if not plan:
                raise HTTPException(status_code=404, detail="Plan non trouve")

            donnees = cast(dict[str, Any], plan.donnees_pieces or {})
            donnees["canvas_2d"] = payload.donnees_canvas
            donnees["largeur_canvas"] = payload.largeur_canvas
            donnees["hauteur_canvas"] = payload.hauteur_canvas
            plan.donnees_pieces = donnees
            plan.version = int(plan.version or 1) + 1
            session.flush()
            return MessageResponse(message="Canvas 2D sauvegarde")

    return await executer_async(_query)


@router.get("/plans/{plan_id}/pieces", responses=REPONSES_LISTE_TYPED)
@gerer_exception_api
async def lister_pieces(
    plan_id: int, user: dict[str, Any] = Depends(require_auth)
) -> dict[str, Any]:
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


@router.get("/plans/{plan_id}/configuration-3d", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def obtenir_configuration_3d_plan(
    plan_id: int, user: dict[str, Any] = Depends(require_auth)
) -> dict[str, Any]:
    """Retourne la configuration 3D persistée d'un plan et ses variantes."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            plan = session.query(PlanHabitat).filter(PlanHabitat.id == plan_id).first()
            if not plan:
                raise HTTPException(status_code=404, detail="Plan non trouve")

            donnees = cast(dict[str, Any], plan.donnees_pieces or {})
            configuration_3d = cast(dict[str, Any], donnees.get("configuration_3d") or {})
            return {
                "plan_id": plan.id,
                "configuration_courante": configuration_3d.get(
                    "configuration_courante",
                    {"layout_edition": [], "palette_par_type": {}},
                ),
                "variantes": configuration_3d.get("variantes", []),
                "variante_active_id": configuration_3d.get("variante_active_id"),
            }

    return await executer_async(_query)


@router.put("/plans/{plan_id}/configuration-3d", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def sauvegarder_configuration_3d_plan(
    plan_id: int,
    payload: PlanHabitatConfiguration3DUpdate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Sauvegarde la configuration 3D d'un plan et ses variantes nommées."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            plan = session.query(PlanHabitat).filter(PlanHabitat.id == plan_id).first()
            if not plan:
                raise HTTPException(status_code=404, detail="Plan non trouve")

            donnees = cast(dict[str, Any], plan.donnees_pieces or {})
            variantes = []
            for variante in payload.variantes:
                data = variante.model_dump()
                if not data.get("id"):
                    data["id"] = uuid4().hex[:12]
                variantes.append(data)

            donnees["configuration_3d"] = {
                "configuration_courante": payload.configuration_courante.model_dump(),
                "variantes": variantes,
                "variante_active_id": payload.variante_active_id,
            }
            plan.donnees_pieces = donnees
            session.flush()

            return {
                "plan_id": plan.id,
                "configuration_courante": donnees["configuration_3d"]["configuration_courante"],
                "variantes": donnees["configuration_3d"]["variantes"],
                "variante_active_id": donnees["configuration_3d"].get("variante_active_id"),
            }

    return await executer_async(_query)


@router.post("/plans/{plan_id}/pieces", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
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


@router.get("/deco/projets", responses=REPONSES_LISTE_TYPED)
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
                        "palette_couleurs": cast(list[Any], p.palette_couleurs or []),
                        "inspirations": cast(list[Any], p.inspirations or []),
                        "budget_prevu": _to_float(p.budget_prevu),
                        "budget_depense": _to_float(p.budget_depense),
                        "statut": p.statut,
                    }
                    for p in items
                ]
            }

    return await executer_async(_query)


@router.post(
    "/deco/projets/{projet_id}/suggestions", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED
)
@gerer_exception_api
async def suggerer_projet_deco(
    projet_id: int,
    payload: ProjetDecoSuggestionCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère un concept déco avancé avec option d'image."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return obtenir_service_deco_habitat().generer_concept(
                session,
                projet_id=projet_id,
                brief=payload.brief,
                generer_image=payload.generer_image,
            )

    return await executer_async(_query)


@router.post(
    "/deco/projets/{projet_id}/depenses", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED
)
@gerer_exception_api
async def synchroniser_depense_deco(
    projet_id: int,
    payload: ProjetDecoDepenseCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Synchronise une dépense déco vers les dépenses maison."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return obtenir_service_deco_habitat().synchroniser_depense(
                session,
                projet_id=projet_id,
                montant=float(payload.montant),
                fournisseur=payload.fournisseur,
                note=payload.note,
                categorie_depense=payload.categorie_depense,
            )

    return await executer_async(_query)


@router.post("/deco/images", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
@gerer_exception_api
async def generer_image_deco(
    payload: GenerationImageHabitatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Expose le service Hugging Face pour créer une inspiration visuelle Habitat."""

    return obtenir_service_generation_image().generer_image(
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
    )


@router.post("/deco/projets", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
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


@router.get("/jardin/zones", responses=REPONSES_LISTE_TYPED)
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
                        "position_x": _to_float(z.position_x),
                        "position_y": _to_float(z.position_y),
                        "largeur": _to_float(z.largeur),
                        "longueur": _to_float(z.longueur),
                        "donnees_canvas": cast(dict[str, Any], z.donnees_canvas or {}),
                        "plantes": cast(list[Any], z.plantes or []),
                        "amenagements": cast(list[Any], z.amenagements or []),
                        "budget_estime": _to_float(z.budget_estime),
                    }
                    for z in items
                ]
            }

    return await executer_async(_query)


@router.patch("/jardin/zones/{zone_id}", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def modifier_zone_jardin(
    zone_id: int,
    payload: ZoneJardinHabitatPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour les coordonnées et données canvas d'une zone jardin."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            zone = session.query(ZoneJardinHabitat).filter(ZoneJardinHabitat.id == zone_id).first()
            if not zone:
                raise HTTPException(status_code=404, detail="Zone jardin non trouvee")
            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(zone, key, value)
            session.flush()
            return {
                "id": zone.id,
                "nom": zone.nom,
                "position_x": _to_float(zone.position_x),
                "position_y": _to_float(zone.position_y),
                "largeur": _to_float(zone.largeur),
                "longueur": _to_float(zone.longueur),
            }

    return await executer_async(_query)


@router.get("/jardin/resume", responses=REPONSES_CRUD_LECTURE_TYPED)
@gerer_exception_api
async def resume_jardin(
    plan_id: int | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne un résumé budgétaire et surfacique du canvas paysager."""

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            return obtenir_service_deco_habitat().resume_jardin(session, plan_id)

    return await executer_async(_query)


@router.post("/jardin/zones", status_code=201, responses=REPONSES_CRUD_CREATION_TYPED)
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

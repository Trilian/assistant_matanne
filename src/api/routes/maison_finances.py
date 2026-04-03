"""
Routes API Maison - Finances (dépenses, abonnements, artisans, etc.).

Sous-routeur inclus dans maison.py.
"""

import base64
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

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

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ARTISANS (carnet d'adresses)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/artisans", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_artisans(
    metier: str | None = Query(None, description="Filtrer par mÃ©tier"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les artisans du carnet d'adresses."""
    from src.services.maison import obtenir_artisans_crud_service

    def _query():
        service = obtenir_artisans_crud_service()
        return {"items": service.get_all_artisans(filtre_metier=metier)}

    return await executer_async(_query)


@router.get("/artisans/stats", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def stats_artisans(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Statistiques artisans (nb mÃ©tiers, dÃ©penses, interventions)."""
    from src.services.maison import obtenir_artisans_crud_service

    def _query():
        service = obtenir_artisans_crud_service()
        return service.get_stats_artisans()

    return await executer_async(_query)


@router.get("/artisans/{artisan_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_artisan(
    artisan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©tail d'un artisan."""
    from src.services.maison import obtenir_artisans_crud_service

    def _query():
        service = obtenir_artisans_crud_service()
        result = service.get_artisan_by_id(artisan_id)
        if not result:
            raise HTTPException(status_code=404, detail="Artisan non trouvÃ©")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/artisans", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_artisan(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un artisan au carnet."""
    from src.services.maison import obtenir_artisans_crud_service

    def _query():
        service = obtenir_artisans_crud_service()
        return model_to_dict(service.create_artisan(payload))

    return await executer_async(_query)


@router.patch("/artisans/{artisan_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_artisan(
    artisan_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour un artisan."""
    from src.services.maison import obtenir_artisans_crud_service

    def _query():
        service = obtenir_artisans_crud_service()
        return model_to_dict(service.update_artisan(artisan_id, payload))

    return await executer_async(_query)


@router.delete("/artisans/{artisan_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_artisan(
    artisan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un artisan et ses interventions."""
    from src.services.maison import obtenir_artisans_crud_service

    def _query():
        service = obtenir_artisans_crud_service()
        service.delete_artisan(artisan_id)
        return MessageResponse(message="Artisan supprimÃ©")

    return await executer_async(_query)


@router.get("/artisans/{artisan_id}/interventions", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_interventions(
    artisan_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des interventions d'un artisan."""
    from src.services.maison import obtenir_artisans_crud_service

    def _query():
        service = obtenir_artisans_crud_service()
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
    from src.services.maison import obtenir_artisans_crud_service

    payload["artisan_id"] = artisan_id

    def _query():
        service = obtenir_artisans_crud_service()
        return model_to_dict(service.create_intervention(payload))

    return await executer_async(_query)


@router.delete("/artisans/interventions/{intervention_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_intervention(
    intervention_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une intervention."""
    from src.services.maison import obtenir_artisans_crud_service

    def _query():
        service = obtenir_artisans_crud_service()
        service.delete_intervention(intervention_id)
        return MessageResponse(message="Intervention supprimÃ©e")

    return await executer_async(_query)



# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ═══════════════════════════════════════════════════════════
# ABONNEMENTS (comparateur)
# ═══════════════════════════════════════════════════════════


@router.get("/abonnements", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_abonnements(
    type_abonnement: str | None = Query(None, description="Filtrer par type"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les abonnements maison."""
    def _query():
        with executer_avec_session() as session:
            from src.core.models.abonnements import Abonnement
            query = session.query(Abonnement)
            if type_abonnement:
                query = query.filter(Abonnement.type_abonnement == type_abonnement)
            items = query.order_by(Abonnement.type_abonnement).all()
            return {"items": [model_to_dict(a) for a in items]}
    return await executer_async(_query)


@router.get("/abonnements/resume", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def resume_abonnements(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Résumé financier des abonnements (total mensuel, annuel, par type)."""
    def _query():
        with executer_avec_session() as session:
            from src.core.models.abonnements import Abonnement
            abos = session.query(Abonnement).all()
            total_mensuel = sum(float(a.prix_mensuel or 0) for a in abos)
            par_type: dict[str, float] = {}
            for a in abos:
                t = a.type_abonnement
                par_type[t] = par_type.get(t, 0) + float(a.prix_mensuel or 0)
            return {
                "total_mensuel": round(total_mensuel, 2),
                "total_annuel": round(total_mensuel * 12, 2),
                "par_type": {k: round(v, 2) for k, v in par_type.items()},
            }
    return await executer_async(_query)


@router.get("/abonnements/{abonnement_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_abonnement(
    abonnement_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détail d'un abonnement."""
    def _query():
        with executer_avec_session() as session:
            from src.core.models.abonnements import Abonnement
            abo = session.query(Abonnement).get(abonnement_id)
            if not abo:
                raise HTTPException(status_code=404, detail="Abonnement introuvable")
            return model_to_dict(abo)
    return await executer_async(_query)


@router.post("/abonnements", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_abonnement(
    data: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un abonnement."""
    def _query():
        with executer_avec_session() as session:
            from src.core.models.abonnements import Abonnement
            abo = Abonnement(**data)
            session.add(abo)
            session.commit()
            session.refresh(abo)
            return model_to_dict(abo)
    return await executer_async(_query)


@router.patch("/abonnements/{abonnement_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_abonnement(
    abonnement_id: int,
    data: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un abonnement."""
    def _query():
        with executer_avec_session() as session:
            from src.core.models.abonnements import Abonnement
            abo = session.query(Abonnement).get(abonnement_id)
            if not abo:
                raise HTTPException(status_code=404, detail="Abonnement introuvable")
            for key, value in data.items():
                if hasattr(abo, key):
                    setattr(abo, key, value)
            session.commit()
            session.refresh(abo)
            return model_to_dict(abo)
    return await executer_async(_query)


@router.delete("/abonnements/{abonnement_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_abonnement(
    abonnement_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un abonnement."""
    def _query():
        with executer_avec_session() as session:
            from src.core.models.abonnements import Abonnement
            abo = session.query(Abonnement).get(abonnement_id)
            if not abo:
                raise HTTPException(status_code=404, detail="Abonnement introuvable")
            session.delete(abo)
            session.commit()
            return MessageResponse(message="Abonnement supprimé")
    return await executer_async(_query)



# DIAGNOSTICS IMMOBILIERS & ESTIMATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/diagnostics", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_diagnostics(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les diagnostics immobiliers (DPE, amiante, plomb...)."""
    from src.services.maison import obtenir_diagnostics_crud_service

    def _query():
        service = obtenir_diagnostics_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.get("/diagnostics/alertes", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_diagnostics(
    jours: int = Query(90, ge=1, le=365, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Diagnostics dont la validitÃ© expire bientÃ´t."""
    from src.services.maison import obtenir_diagnostics_crud_service

    def _query():
        service = obtenir_diagnostics_crud_service()
        return {"items": service.get_alertes_validite(jours_horizon=jours)}

    return await executer_async(_query)


@router.get("/diagnostics/validite-types", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def validite_types_diagnostics(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DurÃ©es de validitÃ© par type de diagnostic."""
    from src.services.maison import obtenir_diagnostics_crud_service

    def _query():
        service = obtenir_diagnostics_crud_service()
        return service.get_validite_par_type()

    return await executer_async(_query)


@router.post("/diagnostics/ia-photo", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def diagnostic_photo_ia(
    photo: UploadFile = File(..., description="Photo de la piÃ¨ce Ã  diagnostiquer"),
    piece: str = Query("maison", description="Nom de la piÃ¨ce (cuisine, salle de bain, etc.)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse une photo de maison et propose un diagnostic IA (Pixtral)."""
    TYPES_AUTORISES = {"image/jpeg", "image/png", "image/webp"}
    if photo.content_type not in TYPES_AUTORISES:
        raise HTTPException(
            status_code=422,
            detail=f"Type non supportÃ©: {photo.content_type}. Utilisez JPEG, PNG ou WebP.",
        )

    contenu = await photo.read()
    if len(contenu) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 10 Mo)")

    from src.services.integrations.multimodal import obtenir_multimodal_service

    service = obtenir_multimodal_service()
    diagnostic = await service.diagnostiquer_photo_maison(contenu, piece=piece)

    if not diagnostic:
        return {
            "piece": piece,
            "urgence_globale": "faible",
            "resume": "Aucune analyse exploitable (photo peu lisible ou hors contexte).",
            "problemes_detectes": [],
            "estimation_cout_min": 0,
            "estimation_cout_max": 0,
            "actions_48h": ["Refaire une photo nette de la zone concernÃ©e."],
        }

    return diagnostic.model_dump()


@router.post("/diagnostics", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_diagnostic(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre un diagnostic immobilier."""
    from src.services.maison import obtenir_diagnostics_crud_service

    def _query():
        service = obtenir_diagnostics_crud_service()
        return model_to_dict(service.create(payload))

    return await executer_async(_query)


@router.patch("/diagnostics/{diagnostic_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_diagnostic(
    diagnostic_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour un diagnostic."""
    from src.services.maison import obtenir_diagnostics_crud_service

    def _query():
        service = obtenir_diagnostics_crud_service()
        return model_to_dict(service.update(diagnostic_id, payload))

    return await executer_async(_query)


@router.delete("/diagnostics/{diagnostic_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_diagnostic(
    diagnostic_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un diagnostic."""
    from src.services.maison import obtenir_diagnostics_crud_service

    def _query():
        service = obtenir_diagnostics_crud_service()
        service.delete(diagnostic_id)
        return MessageResponse(message="Diagnostic supprimÃ©")

    return await executer_async(_query)


@router.get("/estimations", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_estimations(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les estimations immobiliÃ¨res."""
    from src.services.maison import obtenir_estimations_crud_service

    def _query():
        service = obtenir_estimations_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.get("/estimations/derniere", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def derniere_estimation(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DerniÃ¨re estimation immobiliÃ¨re."""
    from src.services.maison import obtenir_estimations_crud_service

    def _query():
        service = obtenir_estimations_crud_service()
        result = service.get_derniere_estimation()
        if not result:
            raise HTTPException(status_code=404, detail="Aucune estimation trouvÃ©e")
        return result

    return await executer_async(_query)


@router.post("/estimations", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_estimation(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une estimation immobiliÃ¨re."""
    from src.services.maison import obtenir_estimations_crud_service

    def _query():
        service = obtenir_estimations_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.delete("/estimations/{estimation_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_estimation(
    estimation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une estimation."""
    from src.services.maison import obtenir_estimations_crud_service

    def _query():
        service = obtenir_estimations_crud_service()
        service.delete(estimation_id)
        return MessageResponse(message="Estimation supprimÃ©e")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ã‰CO-TIPS (actions Ã©cologiques)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/eco-tips", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_eco_tips(
    actif_only: bool = Query(False, description="Seulement les actions actives"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les actions Ã©cologiques."""
    from src.services.maison import obtenir_eco_tips_crud_service

    def _query():
        service = obtenir_eco_tips_crud_service()
        return {"items": service.get_all_actions(actif_only=actif_only)}

    return await executer_async(_query)


@router.get("/eco-tips/{action_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_eco_tip(
    action_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©tail d'une action Ã©cologique."""
    from src.services.maison import obtenir_eco_tips_crud_service

    def _query():
        service = obtenir_eco_tips_crud_service()
        result = service.get_action_by_id(action_id)
        if not result:
            raise HTTPException(status_code=404, detail="Action non trouvÃ©e")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/eco-tips", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_eco_tip(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """CrÃ©e une action Ã©cologique."""
    from src.services.maison import obtenir_eco_tips_crud_service

    def _query():
        service = obtenir_eco_tips_crud_service()
        return model_to_dict(service.create_action(payload))

    return await executer_async(_query)


@router.patch("/eco-tips/{action_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_eco_tip(
    action_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour une action Ã©cologique."""
    from src.services.maison import obtenir_eco_tips_crud_service

    def _query():
        service = obtenir_eco_tips_crud_service()
        return model_to_dict(service.update_action(action_id, payload))

    return await executer_async(_query)


@router.delete("/eco-tips/{action_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_eco_tip(
    action_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une action Ã©cologique."""
    from src.services.maison import obtenir_eco_tips_crud_service

    def _query():
        service = obtenir_eco_tips_crud_service()
        service.delete_action(action_id)
        return MessageResponse(message="Action supprimÃ©e")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DÃ‰PENSES MAISON
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/depenses", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_depenses(
    mois: int | None = Query(None, ge=1, le=12, description="Mois (1-12)"),
    annee: int | None = Query(None, ge=2020, description="AnnÃ©e"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les dÃ©penses maison (par mois ou annÃ©e)."""
    from src.services.maison import obtenir_depenses_crud_service

    def _query():
        service = obtenir_depenses_crud_service()
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
    """Statistiques globales des dÃ©penses (tendance, moyenne, delta)."""
    from src.services.maison import obtenir_depenses_crud_service

    def _query():
        service = obtenir_depenses_crud_service()
        return service.get_stats_globales()

    return await executer_async(_query)


@router.get("/depenses/historique/{categorie}", responses=REPONSES_LISTE)
@gerer_exception_api
async def historique_depenses_categorie(
    categorie: str,
    nb_mois: int = Query(12, ge=1, le=36, description="Nombre de mois d'historique"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique des dÃ©penses par catÃ©gorie."""
    from src.services.maison import obtenir_depenses_crud_service

    def _query():
        service = obtenir_depenses_crud_service()
        return {"items": service.get_historique_categorie(categorie, nb_mois=nb_mois)}

    return await executer_async(_query)


@router.get("/depenses/energie/{type_energie}", responses=REPONSES_LISTE)
@gerer_exception_api
async def historique_energie(
    type_energie: str,
    nb_mois: int = Query(12, ge=1, le=36, description="Nombre de mois d'historique"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Historique de consommation Ã©nergÃ©tique avec tendance."""
    from src.services.maison import obtenir_depenses_crud_service

    def _query():
        service = obtenir_depenses_crud_service()
        return {"items": service.charger_historique_energie(type_energie, nb_mois=nb_mois)}

    return await executer_async(_query)


@router.get("/energie/tendances", responses=REPONSES_LISTE)
@gerer_exception_api
async def tendances_energie(
    type_compteur: str = Query("electricite", description="electricite | eau | gaz"),
    nb_mois: int = Query(12, ge=2, le=36, description="Nombre de mois Ã  analyser"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Tendances de consommation mensuelle avec dÃ©tection d'anomalies (Ã©cart > 20 % vs moyenne)."""
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


@router.get("/energie/anomalies-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def anomalies_energie_ia(
    type_compteur: str = Query("electricite", description="electricite | eau | gaz"),
    nb_mois: int = Query(12, ge=3, le=36, description="Nombre de mois a analyser"),
    seuil_pct: float = Query(20.0, ge=5.0, le=80.0, description="Seuil d'ecart (%) pour considerer une anomalie"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Detecte les anomalies energie avec scoring et explications IA."""

    def _query() -> dict[str, Any]:
        from src.services.maison.energie_anomalies_ia import (
            obtenir_service_energie_anomalies_ia,
        )

        service = obtenir_service_energie_anomalies_ia()
        return service.analyser_anomalies(
            type_compteur=type_compteur,
            nb_mois=nb_mois,
            seuil_pct=seuil_pct,
        )

    return await executer_async(_query)


@router.get("/energie/previsions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def previsions_energie_ia(
    type_compteur: str = Query("electricite", description="electricite | eau | gaz"),
    nb_mois: int = Query(6, ge=3, le=24, description="Nombre de mois pour la rÃ©gression"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """PrÃ©vision de consommation du mois prochain par rÃ©gression linÃ©aire."""
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
                    "message": f"Seulement {n} mois disponible(s) â€” il faut au moins 3 relevÃ©s mensuels.",
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


@router.post("/depenses/import-ticket", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def importer_depenses_depuis_ticket(
    photo: UploadFile = File(..., description="Photo du ticket de caisse (JPEG/PNG/WebP)"),
    confirmer: bool = Query(False, description="Si true, importe les dépenses dans la base"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse un ticket de caisse et propose un aperçu des dépenses à importer."""
    types_autorises = {"image/jpeg", "image/png", "image/webp"}
    if photo.content_type not in types_autorises:
        raise HTTPException(status_code=422, detail="Type de fichier non supporté (JPEG/PNG/WebP)")

    contenu = await photo.read()
    if not contenu:
        raise HTTPException(status_code=422, detail="Fichier vide")
    if len(contenu) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 10 Mo)")

    from src.services.integrations.ticket_caisse import scanner_ticket_vision, ticket_vers_depenses
    from src.services.maison import obtenir_depenses_crud_service

    image_base64 = base64.b64encode(contenu).decode("utf-8")
    ticket = scanner_ticket_vision(image_base64)
    depenses_brutes = ticket_vers_depenses(ticket)

    apercu = [
        {
            "libelle": d.get("description", "Achat ticket"),
            "montant": float(d.get("montant", 0.0) or 0.0),
            "categorie": d.get("rayon") or "courses",
            "date": d.get("date").isoformat() if hasattr(d.get("date"), "isoformat") else None,
            "fournisseur": d.get("magasin") or ticket.magasin or None,
            "notes": "Import ticket caisse",
        }
        for d in depenses_brutes
        if float(d.get("montant", 0.0) or 0.0) > 0
    ]

    if not confirmer:
        return {
            "confirmer": False,
            "nb_detectees": len(apercu),
            "confiance_ocr": ticket.confiance_ocr,
            "magasin": ticket.magasin,
            "total_ticket": ticket.total,
            "depenses": apercu,
        }

    def _importer() -> dict[str, Any]:
        service = obtenir_depenses_crud_service()
        imports: list[dict[str, Any]] = []
        for d in apercu:
            cree = service.create_depense(d)
            imports.append(model_to_dict(cree))

        return {
            "confirmer": True,
            "nb_importees": len(imports),
            "depenses": imports,
            "magasin": ticket.magasin,
            "confiance_ocr": ticket.confiance_ocr,
        }

    return await executer_async(_importer)


@router.get("/depenses/{depense_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_depense(
    depense_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """DÃ©tail d'une dÃ©pense."""
    from src.services.maison import obtenir_depenses_crud_service

    def _query():
        service = obtenir_depenses_crud_service()
        result = service.get_depense_by_id(depense_id)
        if not result:
            raise HTTPException(status_code=404, detail="DÃ©pense non trouvÃ©e")
        return model_to_dict(result)

    return await executer_async(_query)


@router.post("/depenses", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_depense(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre une dÃ©pense maison."""
    from src.services.maison import obtenir_depenses_crud_service

    def _query():
        service = obtenir_depenses_crud_service()
        return model_to_dict(service.create_depense(payload))

    return await executer_async(_query)


@router.patch("/depenses/{depense_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_depense(
    depense_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour une dÃ©pense."""
    from src.services.maison import obtenir_depenses_crud_service

    def _query():
        service = obtenir_depenses_crud_service()
        return model_to_dict(service.update_depense(depense_id, payload))

    return await executer_async(_query)


@router.delete("/depenses/{depense_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_depense(
    depense_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une dÃ©pense."""
    from src.services.maison import obtenir_depenses_crud_service

    def _query():
        service = obtenir_depenses_crud_service()
        service.delete_depense(depense_id)
        return MessageResponse(message="DÃ©pense supprimÃ©e")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSEILLER IA MAISON
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/conseiller/conseil", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_conseil_ia(
    section: str = Query("default", description="Section maison (travaux, finances, provisions, jardin, documents, equipements)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne 3 Ã  5 conseils IA contextuels pour la section demandÃ©e."""
    from src.services.maison.conseiller_service import obtenir_conseiller_maison_service

    def _query():
        service = obtenir_conseiller_maison_service()
        conseil = service.obtenir_conseil(section)
        if conseil is None:
            return {"section": section, "conseils": [], "message": "Aucun conseil disponible"}
        return conseil

    return await executer_async(_query)


@router.get("/conseils-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_conseils_hub_ia(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne 4-6 conseils structurÃ©s pour le hub maison, triÃ©s par urgence."""
    from src.services.maison.conseiller_service import obtenir_conseiller_maison_service

    def _query():
        service = obtenir_conseiller_maison_service()
        conseils = service.obtenir_conseils_hub() or []
        return {"items": conseils}

    return await executer_async(_query)


@router.post("/assistant/chat", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def chat_assistant_maison(
    body: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Chat libre avec l'assistant IA maison."""
    from src.services.maison.conseiller_service import obtenir_conseiller_maison_service

    message = body.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Le message ne peut pas Ãªtre vide")

    contexte = body.get("contexte", "maison")

    def _query():
        service = obtenir_conseiller_maison_service()
        reponse = service.chat_assistant(message, contexte)
        return {"reponse": reponse, "message": message}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# NUISIBLES (traitements)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DEVIS COMPARATIFS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/devis", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_devis(
    projet_id: int | None = Query(None, description="Filtrer par projet"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les devis comparatifs."""
    from src.services.maison import obtenir_devis_crud_service

    def _query():
        service = obtenir_devis_crud_service()
        return {"items": service.get_all(projet_id=projet_id)}

    return await executer_async(_query)


@router.post("/devis", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_devis(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """CrÃ©e un devis."""
    from src.services.maison import obtenir_devis_crud_service

    def _query():
        service = obtenir_devis_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.patch("/devis/{devis_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_devis(
    devis_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met Ã  jour un devis."""
    from src.services.maison import obtenir_devis_crud_service

    def _query():
        service = obtenir_devis_crud_service()
        return service.update(devis_id, payload)

    return await executer_async(_query)


@router.delete("/devis/{devis_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_devis(
    devis_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un devis et ses lignes."""
    from src.services.maison import obtenir_devis_crud_service

    def _query():
        service = obtenir_devis_crud_service()
        service.delete(devis_id)
        return MessageResponse(message="Devis supprimÃ©")

    return await executer_async(_query)


@router.post("/devis/{devis_id}/lignes", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def ajouter_ligne_devis(
    devis_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute une ligne Ã  un devis."""
    from src.services.maison import obtenir_devis_crud_service

    payload["devis_id"] = devis_id

    def _query():
        service = obtenir_devis_crud_service()
        return service.add_ligne(payload)

    return await executer_async(_query)


@router.post("/devis/{devis_id}/choisir", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def choisir_devis(
    devis_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Accepte un devis (rejette automatiquement les autres du mÃªme projet)."""
    from src.services.maison import obtenir_devis_crud_service

    def _query():
        service = obtenir_devis_crud_service()
        return service.choisir_devis(devis_id)

    return await executer_async(_query)


# RELEVÃ‰S COMPTEURS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/releves", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_releves(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les relevÃ©s de compteurs (eau, gaz, Ã©lectricitÃ©)."""
    from src.services.maison import obtenir_releves_crud_service

    def _query():
        service = obtenir_releves_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.post("/releves", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_releve(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enregistre un relevÃ© de compteur."""
    from src.services.maison import obtenir_releves_crud_service

    def _query():
        service = obtenir_releves_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.delete("/releves/{releve_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_releve(
    releve_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un relevÃ©."""
    from src.services.maison import obtenir_releves_crud_service

    def _query():
        service = obtenir_releves_crud_service()
        service.delete(releve_id)
        return MessageResponse(message="RelevÃ© supprimÃ©")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VISUALISATION PLAN MAISON


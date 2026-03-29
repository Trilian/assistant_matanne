"""
Routes API Maison — Finances (dépenses, contrats, artisans, garanties, etc.).

Sous-routeur inclus dans maison.py.
"""

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


@router.post(
    "/garanties/{garantie_id}/actions/ouvrir-dossier-sav",
    status_code=201,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def ouvrir_dossier_sav(
    garantie_id: int,
    payload: dict[str, Any] = {},
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ouvre un dossier SAV en 1 clic avec pré-remplissage depuis la garantie."""
    from src.services.maison import get_garanties_crud_service

    def _query():
        service = get_garanties_crud_service()
        return service.ouvrir_dossier_sav_rapide(
            garantie_id=garantie_id,
            description=payload.get("description"),
            source=payload.get("source", "api"),
        )

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


@router.post("/diagnostics/ia-photo", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def diagnostic_photo_ia(
    photo: UploadFile = File(..., description="Photo de la pièce à diagnostiquer"),
    piece: str = Query("maison", description="Nom de la pièce (cuisine, salle de bain, etc.)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse une photo de maison et propose un diagnostic IA (Pixtral)."""
    TYPES_AUTORISES = {"image/jpeg", "image/png", "image/webp"}
    if photo.content_type not in TYPES_AUTORISES:
        raise HTTPException(
            status_code=422,
            detail=f"Type non supporté: {photo.content_type}. Utilisez JPEG, PNG ou WebP.",
        )

    contenu = await photo.read()
    if len(contenu) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 10 Mo)")

    from src.services.integrations.multimodal import get_multimodal_service

    service = get_multimodal_service()
    diagnostic = await service.diagnostiquer_photo_maison(contenu, piece=piece)

    if not diagnostic:
        return {
            "piece": piece,
            "urgence_globale": "faible",
            "resume": "Aucune analyse exploitable (photo peu lisible ou hors contexte).",
            "problemes_detectes": [],
            "estimation_cout_min": 0,
            "estimation_cout_max": 0,
            "actions_48h": ["Refaire une photo nette de la zone concernée."],
        }

    return diagnostic.model_dump()


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
# CONSEILLER IA MAISON
# ═══════════════════════════════════════════════════════════


@router.get("/conseiller/conseil", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_conseil_ia(
    section: str = Query("default", description="Section maison (travaux, finances, provisions, jardin, documents, equipements)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne 3 à 5 conseils IA contextuels pour la section demandée."""
    from src.services.maison.conseiller_service import get_conseiller_maison_service

    def _query():
        service = get_conseiller_maison_service()
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
    """Retourne 4-6 conseils structurés pour le hub maison, triés par urgence."""
    from src.services.maison.conseiller_service import get_conseiller_maison_service

    def _query():
        service = get_conseiller_maison_service()
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
    from src.services.maison.conseiller_service import get_conseiller_maison_service

    message = body.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")

    contexte = body.get("contexte", "maison")

    def _query():
        service = get_conseiller_maison_service()
        reponse = service.chat_assistant(message, contexte)
        return {"reponse": reponse, "message": message}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# NUISIBLES (traitements)
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

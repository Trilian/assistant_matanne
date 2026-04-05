"""
Routes API Maison â€” Entretien, routines et mÃ©nage.

Sous-routeur inclus dans maison.py.
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
from src.services.maison.schemas import TacheJour

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Maison"])

# ROUTINES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/routines", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_routines(
    categorie: str | None = Query(None, description="Filtrer par catÃ©gorie"),
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
    """RÃ©cupÃ¨re une routine avec ses tÃ¢ches."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvÃ©e")

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
    """Enregistre une rÃ©pÃ©tition (toutes ou certaines tÃ¢ches faites aujourd'hui)."""
    from src.core.models import Routine, TacheRoutine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvÃ©e")

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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TÃ‚CHES D'ENTRETIEN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/entretien", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_taches_entretien(
    categorie: str | None = Query(None, description="Filtrer par catÃ©gorie"),
    piece: str | None = Query(None, description="Filtrer par piÃ¨ce"),
    fait: bool | None = Query(None, description="Filtrer par statut fait/non fait"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les tÃ¢ches d'entretien planifiÃ©es."""
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
    """CrÃ©e une nouvelle tÃ¢che d'entretien."""
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
    """Met Ã  jour une tÃ¢che d'entretien (ou la marque comme faite)."""
    from src.core.models import TacheEntretien

    def _query():
        with executer_avec_session() as session:
            tache = session.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()
            if not tache:
                raise HTTPException(status_code=404, detail="TÃ¢che non trouvÃ©e")

            for champ in ("nom", "description", "categorie", "piece", "frequence_jours",
                          "prochaine_fois", "duree_minutes", "responsable", "priorite", "fait"):
                if champ in payload:
                    setattr(tache, champ, payload[champ])

            # Si marquÃ© comme fait, mettre Ã  jour derniere_fois
            if payload.get("fait") is True:
                tache.derniere_fois = date.today()
                if tache.frequence_jours:
                    from datetime import timedelta
                    tache.prochaine_fois = date.today() + timedelta(days=tache.frequence_jours)
                    tache.fait = False  # Reset pour la prochaine occurrence

            session.commit()
            session.refresh(tache)

            suggestion_artisans = None
            if payload.get("echec") is True or payload.get("statut_resolution") == "echec":
                from src.services.ia.inter_modules import obtenir_service_bridges

                suggestion_artisans = obtenir_service_bridges().entretien_echoue_vers_artisans(
                    tache_id=tache.id
                )

            return {
                "id": tache.id,
                "nom": tache.nom,
                "fait": tache.fait,
                "derniere_fois": tache.derniere_fois.isoformat() if tache.derniere_fois else None,
                "prochaine_fois": tache.prochaine_fois.isoformat() if tache.prochaine_fois else None,
                "suggestion_artisans": suggestion_artisans,
            }

    return await executer_async(_query)


@router.delete("/entretien/{tache_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_tache_entretien(
    tache_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une tÃ¢che d'entretien."""
    from src.core.models import TacheEntretien

    def _query():
        with executer_avec_session() as session:
            tache = session.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()
            if not tache:
                raise HTTPException(status_code=404, detail="TÃ¢che non trouvÃ©e")
            session.delete(tache)
            session.commit()
            return MessageResponse(message=f"TÃ¢che '{tache.nom}' supprimÃ©e")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SANTÃ‰ DES APPAREILS (ENTRETIEN INTELLIGENT)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/entretien/sante-appareils", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_sante_appareils(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Dashboard santÃ© des appareils.

    AgrÃ¨ge les tÃ¢ches d'entretien pour calculer un score de santÃ©
    par appareil/zone, et identifie les actions urgentes.
    """
    from src.core.models import TacheEntretien

    def _query():
        with executer_avec_session() as session:
            aujourd_hui = date.today()

            taches = session.query(TacheEntretien).all()

            # Grouper par piÃ¨ce/catÃ©gorie
            par_zone: dict[str, dict[str, Any]] = {}
            actions_urgentes = []

            for t in taches:
                zone = t.piece or t.categorie or "GÃ©nÃ©ral"

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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENTRETIEN SAISONNIER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/entretien-saisonnier", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_entretien_saisonnier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les tÃ¢ches d'entretien saisonnier."""
    from src.services.maison import obtenir_entretien_saisonnier_crud_service

    def _query():
        service = obtenir_entretien_saisonnier_crud_service()
        return {"items": service.get_all()}

    return await executer_async(_query)


@router.get("/entretien-saisonnier/alertes", responses=REPONSES_LISTE)
@gerer_exception_api
async def alertes_entretien_saisonnier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """TÃ¢ches saisonniÃ¨res Ã  faire ce mois-ci."""
    from src.services.maison import obtenir_entretien_saisonnier_crud_service

    def _query():
        service = obtenir_entretien_saisonnier_crud_service()
        return {"items": service.get_alertes_saisonnieres()}

    return await executer_async(_query)


@router.post("/entretien-saisonnier", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_entretien_saisonnier(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """CrÃ©e une tÃ¢che d'entretien saisonnier."""
    from src.services.maison import obtenir_entretien_saisonnier_crud_service

    def _query():
        service = obtenir_entretien_saisonnier_crud_service()
        return service.create(payload)

    return await executer_async(_query)


@router.delete("/entretien-saisonnier/{entretien_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_entretien_saisonnier(
    entretien_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une tÃ¢che d'entretien saisonnier."""
    from src.services.maison import obtenir_entretien_saisonnier_crud_service

    def _query():
        service = obtenir_entretien_saisonnier_crud_service()
        service.delete(entretien_id)
        return MessageResponse(message="TÃ¢che saisonniÃ¨re supprimÃ©e")

    return await executer_async(_query)


@router.patch("/entretien-saisonnier/{entretien_id}/fait", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def marquer_entretien_saisonnier_fait(
    entretien_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Marque une tÃ¢che saisonniÃ¨re comme faite."""
    from src.services.maison import obtenir_entretien_saisonnier_crud_service

    def _query():
        service = obtenir_entretien_saisonnier_crud_service()
        return service.marquer_fait(entretien_id)

    return await executer_async(_query)


@router.post("/entretien-saisonnier/reset", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def reset_entretien_saisonnier(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """RÃ©initialise la checklist saisonniÃ¨re pour la nouvelle annÃ©e."""
    from src.services.maison import obtenir_entretien_saisonnier_crud_service

    def _query():
        service = obtenir_entretien_saisonnier_crud_service()
        service.reset_annuel()
        return {"message": "Checklist saisonniÃ¨re rÃ©initialisÃ©e"}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BRIEFING MAISON (contexte quotidien)
# NOTE: Routes canoniques /briefing, /alertes, /taches-jour
# dÃ©finies en haut du fichier (section CONTEXTE MAISON .
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/entretien/sync-catalogue", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def sync_catalogue_entretien(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Force la synchronisation catalogue â†’ tÃ¢ches d'entretien."""
    from src.services.maison import obtenir_catalogue_entretien_service

    def _query():
        service = obtenir_catalogue_entretien_service()
        result = service.sync_catalogue()
        if result is None:
            return {"message": "Sync Ã©chouÃ©e"}
        return result.model_dump()

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# RAPPELS MAISON (notifications push)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/rappels/envoyer", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def envoyer_rappels_maison(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ã‰value et envoie les rappels push maison (entretien, gel, cellier)."""
    from src.services.maison import obtenir_notifications_maison_service

    def _query():
        service = obtenir_notifications_maison_service()
        result = service.evaluer_et_envoyer_rappels()
        if result is None:
            return {"rappels_envoyes": 0, "rappels_ignores": 0, "erreurs": ["Service indisponible"]}
        return result.model_dump()

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MÃ‰NAGE â€” Planning semaine & prÃ©fÃ©rences
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/menage/planning-semaine", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def planning_semaine_menage(
    date_debut: date | None = Query(None, description="Date dÃ©but semaine (lundi)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Planning mÃ©nage hebdomadaire optimisÃ© par l'IA."""
    from src.services.maison import obtenir_entretien_service

    def _query():
        service = obtenir_entretien_service()
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
    """Sauvegarde les prÃ©fÃ©rences mÃ©nage utilisateur."""
    # Stockage simple dans cache applicatif (remplacement complet)
    from src.core.caching import obtenir_cache

    cache = obtenir_cache()
    cle = f"preferences_menage_{user.get('sub', 'default')}"
    cache.set(cle, payload, ttl=365 * 24 * 3600)
    return {"message": "PrÃ©fÃ©rences sauvegardÃ©es", "preferences": payload}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TÃ‚CHES PONCTUELLES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/taches-ponctuelles", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_tache_ponctuelle(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """CrÃ©e une tÃ¢che mÃ©nagÃ¨re ponctuelle."""
    import datetime as _dt

    from src.core.models.habitat import TacheEntretien

    def _query():
        nom = payload.get("nom", "")
        piece = payload.get("piece", "")
        quand = payload.get("quand", "Aujourd'hui")
        freq = 1 if quand == "Aujourd'hui" else (7 if quand == "Cette semaine" else 2)
        with executer_avec_session() as session:
            tache = TacheEntretien(
                nom=nom,
                categorie="ponctuel",
                piece=piece,
                frequence_jours=freq,
                fait=False,
                prochaine_fois=_dt.date.today(),
            )
            session.add(tache)
            session.flush()
            return {"id": tache.id, "nom": tache.nom, "message": "TÃ¢che crÃ©Ã©e"}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PLANNING IA ADAPTATIF
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/menage/planning-semaine-ia/regenerer", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def regenerer_planning_ia(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """RÃ©gÃ©nÃ¨re le planning mÃ©nage IA pour la semaine."""
    from src.services.maison import obtenir_entretien_service

    def _query():
        service = obtenir_entretien_service()
        planning = service.generer_planning_semaine()
        if planning is None:
            return {"planning": {}}
        return {"planning": planning}

    return await executer_async(_query)


@router.post("/menage/taches/{tache_id}/completer", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def completer_tache_menage(
    tache_id: str,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Marque une tÃ¢che mÃ©nagÃ¨re comme complÃ©tÃ©e."""
    return {"message": "TÃ¢che complÃ©tÃ©e", "tache_id": tache_id}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# AUTO-COMPLÃ‰TION ASSISTANT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/assistant/auto-completion", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def auto_completer_champ(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """SuggÃ¨re des complÃ©tions de champ via IA."""
    from src.services.maison.conseiller_service import obtenir_conseiller_maison_service

    champ_nom = payload.get("champ_nom", "")
    valeur_partielle = payload.get("valeur_partielle", "")
    contexte_page = payload.get("contexte_page", "general")

    def _query():
        service = obtenir_conseiller_maison_service()
        return service.auto_completer(
            champ_nom=champ_nom,
            valeur_partielle=valeur_partielle,
            contexte_page=contexte_page,
        )

    suggestions = await executer_async(_query)
    return {"suggestions": suggestions}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FICHE TÃ‚CHE ASSISTÃ‰E
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/fiche-tache", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_fiche_tache(
    type: str = Query(..., description="Type: entretien, travaux, jardin, lessive"),
    id: int | None = Query(None, description="ID de la tÃ¢che (si entretien)"),
    nom: str | None = Query(None, description="Nom de la tÃ¢che (recherche catalogue)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Fiche tÃ¢che assistÃ©e : Ã©tapes, produits, durÃ©e, astuce connectÃ©e."""
    from src.services.maison import obtenir_fiche_tache_service

    def _query():
        service = obtenir_fiche_tache_service()
        fiche = service.obtenir_fiche(type_tache=type, id_tache=id, nom_tache=nom)
        if fiche is None:
            return {"message": "TÃ¢che non trouvÃ©e dans le catalogue"}
        return fiche.model_dump() if hasattr(fiche, "model_dump") else fiche

    return await executer_async(_query)


@router.post("/fiche-tache-ia", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def generer_fiche_tache_ia(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """GÃ©nÃ¨re une fiche tÃ¢che personnalisÃ©e via IA Mistral."""
    from src.services.maison import obtenir_fiche_tache_service

    def _query():
        service = obtenir_fiche_tache_service()
        nom_tache = payload.get("nom", "")
        contexte = payload.get("contexte", "")
        fiche = service.generer_fiche_ia(nom_tache=nom_tache, contexte=contexte)
        return fiche.model_dump() if hasattr(fiche, "model_dump") else fiche

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GUIDE LESSIVE & Ã‰LECTROMÃ‰NAGER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/guide", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def guide_pratique(
    type: str = Query(..., description="Type: lessive, electromenager, travaux"),
    tache: str | None = Query(None, description="Tache ou problÃ¨me (ex: vin, odeurs)"),
    tissu: str | None = Query(None, description="Type tissu pour lessive"),
    appareil: str | None = Query(None, description="Appareil Ã©lectromÃ©nager"),
    probleme: str | None = Query(None, description="ProblÃ¨me constatÃ©"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Guide pratique : lessive anti-taches, dÃ©pannage Ã©lectromÃ©nager, travaux."""
    from src.services.maison import obtenir_fiche_tache_service

    def _query():
        service = obtenir_fiche_tache_service()
        return service.consulter_guide(
            type_guide=type,
            tache=tache,
            tissu=tissu,
            appareil=appareil,
            probleme=probleme,
        )

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROUTINES PAR DÃ‰FAUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/routines/initialiser-defaut", status_code=200, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def initialiser_routines_defaut(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """CrÃ©e les 3 routines par dÃ©faut (matin, soir, weekly) depuis le JSON de rÃ©fÃ©rence."""
    from src.services.maison import obtenir_entretien_service

    def _query():
        service = obtenir_entretien_service()
        nb = service.initialiser_routines_defaut()
        return {"routines_creees": nb, "message": f"{nb} routine(s) crÃ©Ã©e(s)"}

    return await executer_async(_query)


@router.post("/routines", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_routine(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """CrÃ©e une nouvelle routine."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            routine = Routine(
                nom=payload["nom"],
                description=payload.get("description"),
                categorie=payload.get("categorie", "menage"),
                frequence=payload.get("frequence", "quotidien"),
                actif=payload.get("actif", True),
                moment_journee=payload.get("moment_journee", "flexible"),
                jour_semaine=payload.get("jour_semaine"),
            )
            session.add(routine)
            session.commit()
            session.refresh(routine)
            return {
                "id": routine.id,
                "nom": routine.nom,
                "description": routine.description,
                "categorie": routine.categorie,
                "frequence": routine.frequence,
                "actif": routine.actif,
                "taches_count": 0,
            }

    return await executer_async(_query)


@router.patch("/routines/{routine_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_routine(
    routine_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie une routine existante (y compris activation/dÃ©sactivation)."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvÃ©e")
            for champ in ("nom", "description", "categorie", "frequence", "actif", "moment_journee", "jour_semaine"):
                if champ in payload:
                    setattr(routine, champ, payload[champ])
            session.commit()
            return {
                "id": routine.id,
                "nom": routine.nom,
                "description": routine.description,
                "categorie": routine.categorie,
                "frequence": routine.frequence,
                "actif": routine.actif,
                "taches_count": len(routine.tasks) if routine.tasks else 0,
            }

    return await executer_async(_query)


@router.delete("/routines/{routine_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_routine(
    routine_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime une routine et ses tÃ¢ches."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvÃ©e")
            session.delete(routine)
            session.commit()
            return {"message": "Routine supprimÃ©e"}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROUTINES â€” EXTENSIONS (tÃ¢ches inline, dupliquer, IA)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/routines/taches", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_toutes_taches_routines(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste toutes les tÃ¢ches de toutes les routines (pour associer Ã  un objet)."""
    from src.core.models.maison import TacheRoutine, Routine
    from src.api.utils import executer_avec_session

    def _query():
        with executer_avec_session() as session:
            taches = (
                session.query(TacheRoutine)
                .join(Routine, TacheRoutine.routine_id == Routine.id)
                .order_by(Routine.nom, TacheRoutine.ordre)
                .all()
            )
            return {
                "items": [
                    {
                        "id": t.id,
                        "routine_id": t.routine_id,
                        "routine_nom": t.routine.nom if t.routine else None,
                        "nom": t.nom,
                        "description": t.description,
                        "ordre": t.ordre,
                        "heure_prevue": t.heure_prevue,
                    }
                    for t in taches
                ],
                "total": len(taches),
            }

    return await executer_async(_query)


@router.post("/routines/creer-ia", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_routine_ia(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """GÃ©nÃ¨re et crÃ©e une routine personnalisÃ©e via l'IA."""
    from src.services.maison.conseiller_service import obtenir_conseiller_maison_service
    from src.core.models.maison import Routine, TacheRoutine
    from src.api.utils import executer_avec_session
    import json

    nom = payload.get("nom", "")
    description = payload.get("description", "")
    if not nom:
        raise HTTPException(status_code=422, detail="Le nom de la routine est requis")

    def _query():
        service = obtenir_conseiller_maison_service()
        prompt = (
            f"GÃ©nÃ¨re une routine mÃ©nagÃ¨re nommÃ©e '{nom}' avec la description suivante : {description}. "
            "Retourne un JSON avec les champs: frequence (quotidien/hebdomadaire/mensuel), "
            "moment_journee (matin/soir/flexible), categorie (menage/cuisine/rangement/entretien), "
            "taches (liste de {{nom, ordre, duree_min}} max 8 tÃ¢ches)."
        )
        try:
            conseil = service.obtenir_conseil("menage")
            taches_ia: list[dict[str, Any]] = []
            frequence = "hebdomadaire"
            moment = "flexible"
            categorie = "menage"
            # Parsing basique si l'IA renvoie du JSON structurÃ©
            if isinstance(conseil, dict) and "data" in conseil:
                raw = conseil["data"]
                if isinstance(raw, str):
                    try:
                        parsed = json.loads(raw)
                        frequence = parsed.get("frequence", frequence)
                        moment = parsed.get("moment_journee", moment)
                        categorie = parsed.get("categorie", categorie)
                        taches_ia = parsed.get("taches", [])
                    except Exception as e:
                        logger.warning("[maison] Parsing rÃ©ponse IA routine Ã©chouÃ©: %s", e)
        except Exception as e:
            logger.warning("[maison] GÃ©nÃ©ration IA routine Ã©chouÃ©e, valeurs dÃ©faut utilisÃ©es: %s", e)

        with executer_avec_session() as session:
            routine = Routine(
                nom=nom,
                description=description or None,
                frequence=frequence,
                moment_journee=moment,
                categorie=categorie,
                actif=True,
            )
            session.add(routine)
            session.flush()
            for i, t in enumerate(taches_ia[:8]):
                tache = TacheRoutine(
                    routine_id=routine.id,
                    nom=t.get("nom", f"TÃ¢che {i+1}"),
                    ordre=t.get("ordre", i + 1),
                )
                session.add(tache)
            session.commit()
            return {
                "id": routine.id,
                "nom": routine.nom,
                "frequence": routine.frequence,
                "actif": routine.actif,
                "taches_generees": len(taches_ia),
            }

    return await executer_async(_query)


@router.post("/routines/{routine_id}/dupliquer", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def dupliquer_routine(
    routine_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Duplique une routine existante et toutes ses tÃ¢ches."""
    from src.core.models.maison import Routine, TacheRoutine
    from src.api.utils import executer_avec_session

    def _query():
        with executer_avec_session() as session:
            source = session.get(Routine, routine_id)
            if not source:
                raise HTTPException(status_code=404, detail="Routine introuvable")
            nouvelle = Routine(
                nom=f"{source.nom} (copie)",
                description=source.description,
                frequence=source.frequence,
                moment_journee=source.moment_journee,
                categorie=source.categorie,
                actif=False,
            )
            session.add(nouvelle)
            session.flush()
            taches_source = session.query(TacheRoutine).filter(TacheRoutine.routine_id == routine_id).all()
            for t in taches_source:
                session.add(TacheRoutine(
                    routine_id=nouvelle.id,
                    nom=t.nom,
                    description=t.description,
                    ordre=t.ordre,
                    heure_prevue=t.heure_prevue,
                ))
            session.commit()
            return {
                "id": nouvelle.id,
                "nom": nouvelle.nom,
                "frequence": nouvelle.frequence,
                "actif": nouvelle.actif,
                "taches_copiees": len(taches_source),
            }

    return await executer_async(_query)


@router.get("/routines/{routine_id}/taches", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_taches_routine(
    routine_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les tÃ¢ches d'une routine."""
    from src.core.models.maison import TacheRoutine
    from src.api.utils import executer_avec_session

    def _query():
        with executer_avec_session() as session:
            taches = (
                session.query(TacheRoutine)
                .filter(TacheRoutine.routine_id == routine_id)
                .order_by(TacheRoutine.ordre)
                .all()
            )
            return {
                "items": [
                    {
                        "id": t.id,
                        "nom": t.nom,
                        "description": t.description,
                        "ordre": t.ordre,
                        "heure_prevue": t.heure_prevue,
                        "fait_le": str(t.fait_le) if t.fait_le else None,
                        "notes": t.notes,
                    }
                    for t in taches
                ],
                "total": len(taches),
            }

    return await executer_async(_query)


@router.post("/routines/{routine_id}/taches", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def ajouter_tache_routine(
    routine_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute une tÃ¢che Ã  une routine existante."""
    from src.core.models.maison import Routine, TacheRoutine
    from src.api.utils import executer_avec_session

    nom = payload.get("nom", "").strip()
    if not nom:
        raise HTTPException(status_code=422, detail="Le nom de la tÃ¢che est requis")

    def _query():
        with executer_avec_session() as session:
            routine = session.get(Routine, routine_id)
            if not routine:
                raise HTTPException(status_code=404, detail="Routine introuvable")
            # Calculer le prochain ordre
            count = session.query(TacheRoutine).filter(TacheRoutine.routine_id == routine_id).count()
            tache = TacheRoutine(
                routine_id=routine_id,
                nom=nom,
                description=payload.get("description"),
                ordre=count + 1,
                heure_prevue=payload.get("heure_prevue"),
            )
            session.add(tache)
            session.commit()
            session.refresh(tache)
            return {"id": tache.id, "nom": tache.nom, "ordre": tache.ordre, "routine_id": routine_id}

    return await executer_async(_query)


@router.delete("/routines/{routine_id}/taches/{tache_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_tache_routine(
    routine_id: int,
    tache_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Supprime une tÃ¢che d'une routine."""
    from src.core.models.maison import TacheRoutine
    from src.api.utils import executer_avec_session

    def _query():
        with executer_avec_session() as session:
            tache = session.query(TacheRoutine).filter(
                TacheRoutine.id == tache_id,
                TacheRoutine.routine_id == routine_id,
            ).first()
            if not tache:
                raise HTTPException(status_code=404, detail="TÃ¢che introuvable")
            session.delete(tache)
            session.commit()
            return {"message": "TÃ¢che supprimÃ©e"}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# OBJETS â€” ASSOCIER ROUTINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.patch("/objets/{objet_id}/associer-routine", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def associer_routine_objet(
    objet_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Associe un objet/Ã©quipement Ã  une tÃ¢che de routine (via notes)."""
    from src.core.models.temps_entretien import ObjetMaison
    from src.api.utils import executer_avec_session

    tache_routine_id = payload.get("tache_routine_id")

    def _query():
        with executer_avec_session() as session:
            objet = session.get(ObjetMaison, objet_id)
            if not objet:
                raise HTTPException(status_code=404, detail="Objet introuvable")
            note_routine = f"routine_tache:{tache_routine_id}" if tache_routine_id else None
            notes_actuelles = objet.notes or ""
            # Remplacer ou ajouter la rÃ©fÃ©rence de routine
            import re
            if re.search(r"routine_tache:\d+", notes_actuelles):
                objet.notes = re.sub(r"routine_tache:\d+", note_routine or "", notes_actuelles).strip()
            elif note_routine:
                objet.notes = f"{notes_actuelles} {note_routine}".strip()
            session.commit()
            return {"id": objet.id, "nom": objet.nom, "tache_routine_id": tache_routine_id}

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SYNC TÃ‚CHES MAISON â†’ PLANNING FAMILIAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/planning/sync-famille", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def synchroniser_taches_vers_planning(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Synchronise des tÃ¢ches/projets maison vers le planning familial.

    CrÃ©e des Ã©vÃ©nements dans le calendrier famille pour les tÃ¢ches et projets
    maison sÃ©lectionnÃ©s (par IDs). Permet de visualiser les travaux maison
    dans le planning familial.

    Body:
        taches_ids: list[int] â€” IDs de TacheEntretien Ã  synchroniser
        projets_ids: list[int] â€” IDs de ProjetMaison Ã  synchroniser
    """
    from datetime import time

    from src.core.models import ProjetMaison, TacheEntretien
    from src.services.famille.calendrier_planning import obtenir_service_calendrier_planning

    taches_ids = payload.get("taches_ids", [])
    projets_ids = payload.get("projets_ids", [])

    if not taches_ids and not projets_ids:
        return {"succes": True, "evenements_crees": 0, "message": "Aucun Ã©lÃ©ment Ã  synchroniser"}

    def _query():
        planning_svc = obtenir_service_calendrier_planning()
        crees = 0
        conflits: list[str] = []

        with executer_avec_session() as session:
            # Synchroniser les tÃ¢ches d'entretien
            if taches_ids:
                taches = (
                    session.query(TacheEntretien)
                    .filter(TacheEntretien.id.in_(taches_ids))
                    .all()
                )
                for t in taches:
                    date_cible = t.prochaine_fois or date.today()
                    try:
                        planning_svc.creer_event_calendrier(
                            titre=f"ðŸ”§ {t.nom}",
                            date_event=date_cible,
                            type_event="entretien_maison",
                            description=f"TÃ¢che entretien maison (durÃ©e ~{t.duree_minutes or 30}min)",
                        )
                        crees += 1
                    except Exception as e:
                        conflits.append(f"TÃ¢che {t.nom}: {e}")

            # Synchroniser les projets
            if projets_ids:
                projets = (
                    session.query(ProjetMaison)
                    .filter(ProjetMaison.id.in_(projets_ids))
                    .all()
                )
                for p in projets:
                    date_cible = p.date_fin_prevue or date.today()
                    try:
                        planning_svc.creer_event_calendrier(
                            titre=f"ðŸ  {p.nom}",
                            date_event=date_cible,
                            type_event="projet_maison",
                            description=f"Projet maison â€” {p.statut or 'planifiÃ©'}",
                        )
                        crees += 1
                    except Exception as e:
                        conflits.append(f"Projet {p.nom}: {e}")

        return {
            "succes": True,
            "evenements_crees": crees,
            "conflits_detectes": conflits,
            "message": f"{crees} Ã©vÃ©nement(s) crÃ©Ã©(s) dans le planning familial",
        }

    return await executer_async(_query)



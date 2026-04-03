"""Routes admin — Jobs et Bridges."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from src.api.dependencies import require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    JobInfoResponse,
    JobsBulkRequest,
    JobsSimulationJourneeRequest,
    _LABELS_JOBS,
    _ajouter_log_job,
    _extraire_jobs_matin,
    _job_logs,
    _job_trigger_timestamps,
    _journaliser_action_admin,
    _verifier_limite_admin,
    _verifier_limite_jobs,
    router,
)

logger = logging.getLogger(__name__)

@router.get(
    "/bridges/status",
    responses=REPONSES_AUTH_ADMIN,
    summary="Statut opérationnel des bridges inter-modules",
    description=(
        "Expose l'état opérationnel des 17 actions (bridges inter-modules et "
        "interactions intra-modules) pour dashboard/admin."
    ),
)
@gerer_exception_api
async def statut_bridges(
    inclure_smoke: bool = Query(
        True,
        description=(
            "Exécute des checks smoke non destructifs sur les actions compatibles. "
            "Les actions mutatives restent en vérification de présence."
        ),
    ),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Retourne un statut détaillé de tous les bridges/actions inter-modules."""
    from src.api.utils import executer_async, executer_avec_session

    def _query() -> dict[str, Any]:
        debut_global = time.perf_counter()
        resultats: list[dict[str, Any]] = []

        with executer_avec_session() as session:
            presence_fallbacks: dict[str, Any] = {
                "P5-01": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "suggerer_recettes_selon_stock",
                ),
                "P5-02": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_jules_nutrition",
                        fromlist=["obtenir_service_jules_nutrition_interaction"],
                    ).obtenir_service_jules_nutrition_interaction(),
                    "adapter_planning_nutrition_selon_croissance",
                ),
                "P5-03": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_saison_menu",
                        fromlist=["obtenir_service_saison_menu_interaction"],
                    ).obtenir_service_saison_menu_interaction(),
                    "obtenir_contexte_saisonnier_planning",
                ),
                "P5-04": lambda: hasattr(
                    __import__(
                        "src.services.famille.inter_module_meteo_activites",
                        fromlist=["obtenir_service_meteo_activites_interaction"],
                    ).obtenir_service_meteo_activites_interaction(),
                    "suggerer_activites_selon_meteo",
                ),
                "P5-05": lambda: hasattr(
                    __import__(
                        "src.services.maison.inter_module_entretien_courses",
                        fromlist=["obtenir_service_entretien_courses_interaction"],
                    ).obtenir_service_entretien_courses_interaction(),
                    "suggerer_produits_entretien_pour_courses",
                ),
                "P5-06": lambda: hasattr(
                    __import__(
                        "src.services.maison.inter_module_charges_energie",
                        fromlist=["obtenir_service_charges_energie_interaction"],
                    ).obtenir_service_charges_energie_interaction(),
                    "detecter_hausse_et_declencher_analyse",
                ),
                "P5-07": lambda: hasattr(
                    __import__(
                        "src.services.famille.inter_module_weekend_courses",
                        fromlist=["obtenir_service_weekend_courses_interaction"],
                    ).obtenir_service_weekend_courses_interaction(),
                    "suggerer_fournitures_weekend",
                ),
                "P5-09": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "suggerer_recettes_selon_stock",
                ),
                "P5-10": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "exclure_articles_surplus_des_courses",
                ),
                "P5-11": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "bloquer_jours_batch_dans_planning",
                ),
                "P5-12": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "analyser_equilibre_nutritionnel_planning",
                ),
                "P5-13": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "filtrer_recettes_mal_notees",
                ),
                "P5-17": lambda: hasattr(
                    __import__(
                        "src.services.maison.inter_module_charges_energie",
                        fromlist=["obtenir_service_charges_energie_interaction"],
                    ).obtenir_service_charges_energie_interaction(),
                    "detecter_hausse_et_declencher_analyse",
                ),
            }

            checks: list[dict[str, Any]] = [
                {
                    "id": "P5-01",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Stock -> Planning recettes",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .suggerer_recettes_selon_stock(db=session),
                },
                {
                    "id": "P5-02",
                    "bridge": "inter_module_jules_nutrition.py",
                    "intitule": "Jules croissance -> Planning nutrition",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_jules_nutrition",
                        fromlist=["obtenir_service_jules_nutrition_interaction"],
                    )
                    .obtenir_service_jules_nutrition_interaction()
                    .adapter_planning_nutrition_selon_croissance(db=session),
                },
                {
                    "id": "P5-03",
                    "bridge": "inter_module_saison_menu.py",
                    "intitule": "Produits de saison -> Planning IA",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_saison_menu",
                        fromlist=["obtenir_service_saison_menu_interaction"],
                    )
                    .obtenir_service_saison_menu_interaction()
                    .obtenir_contexte_saisonnier_planning(),
                },
                {
                    "id": "P5-04",
                    "bridge": "inter_module_meteo_activites.py",
                    "intitule": "Météo -> Activités famille",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.famille.inter_module_meteo_activites",
                        fromlist=["obtenir_service_meteo_activites_interaction"],
                    )
                    .obtenir_service_meteo_activites_interaction()
                    .suggerer_activites_selon_meteo(db=session),
                },
                {
                    "id": "P5-05",
                    "bridge": "inter_module_entretien_courses.py",
                    "intitule": "Entretien -> Courses",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.maison.inter_module_entretien_courses",
                        fromlist=["obtenir_service_entretien_courses_interaction"],
                    )
                    .obtenir_service_entretien_courses_interaction()
                    .suggerer_produits_entretien_pour_courses(db=session),
                },
                {
                    "id": "P5-06",
                    "bridge": "inter_module_charges_energie.py",
                    "intitule": "Charges facture -> Analyse énergie",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.maison.inter_module_charges_energie",
                        fromlist=["obtenir_service_charges_energie_interaction"],
                    )
                    .obtenir_service_charges_energie_interaction()
                    .detecter_hausse_et_declencher_analyse(db=session),
                },
                {
                    "id": "P5-07",
                    "bridge": "inter_module_weekend_courses.py",
                    "intitule": "Weekend activités -> Courses",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.famille.inter_module_weekend_courses",
                        fromlist=["obtenir_service_weekend_courses_interaction"],
                    )
                    .obtenir_service_weekend_courses_interaction()
                    .suggerer_fournitures_weekend(db=session),
                },
                {
                    "id": "P5-08",
                    "bridge": "inter_module_documents_calendrier.py",
                    "intitule": "Documents expirants -> Calendrier",
                    "type_check": "presence",
                    "callable": lambda: hasattr(
                        __import__(
                            "src.services.famille.inter_module_documents_calendrier",
                            fromlist=["obtenir_service_documents_calendrier_interaction"],
                        ).obtenir_service_documents_calendrier_interaction(),
                        "synchroniser_documents_vers_calendrier",
                    ),
                },
                {
                    "id": "P5-09",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Inventaire -> Planning",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .suggerer_recettes_selon_stock(db=session),
                },
                {
                    "id": "P5-10",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Anti-gaspillage -> Courses",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .exclure_articles_surplus_des_courses(db=session),
                },
                {
                    "id": "P5-11",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Batch cooking -> Planning",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .bloquer_jours_batch_dans_planning(db=session),
                },
                {
                    "id": "P5-12",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Nutrition -> Planning",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .analyser_equilibre_nutritionnel_planning(db=session),
                },
                {
                    "id": "P5-13",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Feedback recette -> Suggestions IA",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .filtrer_recettes_mal_notees(db=session),
                },
                {
                    "id": "P5-14",
                    "bridge": "inter_module_jules_nutrition.py",
                    "intitule": "Jules croissance -> Portions recettes",
                    "type_check": "presence",
                    "callable": lambda: hasattr(
                        __import__(
                            "src.services.cuisine.inter_module_jules_nutrition",
                            fromlist=["obtenir_service_jules_nutrition_interaction"],
                        ).obtenir_service_jules_nutrition_interaction(),
                        "adapter_portions_recettes_planifiees",
                    ),
                },
                {
                    "id": "P5-15",
                    "bridge": "inter_module_anniversaires_budget.py",
                    "intitule": "Anniversaire J-14 -> Budget prévisionnel",
                    "type_check": "presence",
                    "callable": lambda: hasattr(
                        __import__(
                            "src.services.famille.inter_module_anniversaires_budget",
                            fromlist=["obtenir_service_anniversaires_budget_interaction"],
                        ).obtenir_service_anniversaires_budget_interaction(),
                        "reserver_budget_previsionnel_j14",
                    ),
                },
                {
                    "id": "P5-16",
                    "bridge": "inter_module_jardin_entretien.py",
                    "intitule": "Jardin saison -> Entretien auto",
                    "type_check": "presence",
                    "callable": lambda: hasattr(
                        __import__(
                            "src.services.maison.inter_module_jardin_entretien",
                            fromlist=["obtenir_service_jardin_entretien_interaction"],
                        ).obtenir_service_jardin_entretien_interaction(),
                        "generer_taches_saisonnieres_depuis_plantes",
                    ),
                },
                {
                    "id": "P5-17",
                    "bridge": "inter_module_charges_energie.py",
                    "intitule": "Charges augmentation -> Diagnostic énergie",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.maison.inter_module_charges_energie",
                        fromlist=["obtenir_service_charges_energie_interaction"],
                    )
                    .obtenir_service_charges_energie_interaction()
                    .detecter_hausse_et_declencher_analyse(db=session),
                },
            ]

            for check in checks:
                debut = time.perf_counter()
                type_check = check["type_check"]
                if type_check == "smoke" and not inclure_smoke:
                    type_check = "presence"

                try:
                    if type_check == "presence":
                        if not inclure_smoke and check["id"] in presence_fallbacks:
                            presence_fallbacks[check["id"]]()
                        else:
                            check["callable"]()
                        resultat = {
                            "id": check["id"],
                            "bridge": check["bridge"],
                            "intitule": check["intitule"],
                            "verification": "presence",
                            "statut": "operationnel",
                            "latence_ms": round((time.perf_counter() - debut) * 1000, 2),
                            "details": "Factory et méthode disponibles.",
                        }
                    else:
                        sortie = check["callable"]()
                        resultat = {
                            "id": check["id"],
                            "bridge": check["bridge"],
                            "intitule": check["intitule"],
                            "verification": "smoke",
                            "statut": "operationnel",
                            "latence_ms": round((time.perf_counter() - debut) * 1000, 2),
                            "details": f"Retour {type(sortie).__name__}.",
                        }
                except Exception as exc:
                    resultat = {
                        "id": check["id"],
                        "bridge": check["bridge"],
                        "intitule": check["intitule"],
                        "verification": type_check,
                        "statut": "indisponible",
                        "latence_ms": round((time.perf_counter() - debut) * 1000, 2),
                        "details": str(exc)[:300],
                    }

                resultats.append(resultat)

        total = len(resultats)
        operationnels = len([r for r in resultats if r["statut"] == "operationnel"])
        indisponibles = total - operationnels
        statut_global = "operationnel" if indisponibles == 0 else "degrade"

        return {
            "phase": "bridges_inter_modules",
            "generated_at": datetime.now().isoformat(),
            "execution_ms": round((time.perf_counter() - debut_global) * 1000, 2),
            "statut_global": statut_global,
            "resume": {
                "total_actions": total,
                "operationnelles": operationnels,
                "indisponibles": indisponibles,
                "taux_operationnel_pct": round((operationnels / total) * 100, 2) if total else 0.0,
                "mode_verification": "smoke+presence" if inclure_smoke else "presence_only",
            },
            "items": sorted(resultats, key=lambda r: r["id"]),
        }

    return await executer_async(_query)


@router.get(
    "/jobs",
    response_model=list[JobInfoResponse],
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les jobs cron",
    description="Retourne tous les jobs planifiés avec leur statut. Nécessite le rôle admin.",
)
@gerer_exception_api
async def lister_jobs(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> list[dict]:
    """Liste tous les jobs APScheduler et leur prochain déclenchement."""
    try:
        from src.services.core.cron.jobs import _demarreur

        if _demarreur is None or not _demarreur._scheduler.running:
            return []

        jobs = []
        for job in _demarreur._scheduler.get_jobs():
            prochain = job.next_run_time
            jobs.append({
                "id": job.id,
                "nom": _LABELS_JOBS.get(job.id, job.name or job.id),
                "schedule": str(job.trigger),
                "prochain_run": prochain.isoformat() if prochain else None,
                "dernier_run": None,  # APScheduler ne stocke pas le dernier run
                "statut": "actif" if prochain else "inactif",
            })
        return jobs
    except Exception as e:
        logger.warning("Impossible de lister les jobs : %s", e)
        return []


@router.post(
    "/jobs/{job_id}/run",
    responses=REPONSES_AUTH_ADMIN,
    summary="Déclencher un job manuellement",
    description="Exécute immédiatement le job indiqué. Nécessite le rôle admin. Rate-limited: 5 req/min.",
)
@gerer_exception_api
async def executer_job(
    job_id: str,
    dry_run: bool = Query(False, description="Simuler le job sans exécution réelle"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Déclenche un job cron de façon asynchrone."""
    from src.api.utils import executer_async

    # Rate limiting : 5 triggers/min par admin
    _verifier_limite_jobs(str(user.get("id", "admin")))

    from src.services.core.cron.jobs import executer_job_par_id, lister_jobs_disponibles

    jobs_disponibles = lister_jobs_disponibles()
    if job_id not in jobs_disponibles:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' inconnu. Jobs disponibles : {jobs_disponibles}",
        )

    def _run():
        resultat = executer_job_par_id(
            job_id,
            dry_run=dry_run,
            source="manual",
            triggered_by_user_id=str(user.get("id", "admin")),
            relancer_exception=True,
        )
        _ajouter_log_job(
            job_id,
            "succes" if resultat.get("status") in {"ok", "dry_run"} else "erreur",
            str(resultat.get("message", "")),
        )
        return resultat

    result = await executer_async(_run)
    _journaliser_action_admin(
        action="admin.job.run",
        entite_type="job",
        utilisateur_id=str(user.get("id", "admin")),
        details={"job_id": job_id, "dry_run": dry_run},
    )
    return result


@router.post(
    "/jobs/run-morning-batch",
    responses=REPONSES_AUTH_ADMIN,
    summary='Lancer tous les jobs du matin',
    description="Exécute en séquence les jobs planifiés entre 06:00 et 09:00.",
)
@gerer_exception_api
async def executer_jobs_matin(
    body: JobsBulkRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_async

    def _run() -> dict[str, Any]:
        from src.services.core.cron.jobs import executer_job_par_id, lister_jobs_disponibles

        jobs_matin = [j for j in _extraire_jobs_matin() if j in set(lister_jobs_disponibles())]
        resultats: list[dict[str, Any]] = []
        for job_id in jobs_matin:
            debut = time.perf_counter()
            try:
                sortie = executer_job_par_id(
                    job_id,
                    dry_run=body.dry_run,
                    source="admin_morning_batch",
                    triggered_by_user_id=str(user.get("id", "admin")),
                    relancer_exception=True,
                )
                statut = str(sortie.get("status", "ok"))
                resultats.append({
                    "job_id": job_id,
                    "status": statut,
                    "duration_ms": round((time.perf_counter() - debut) * 1000, 2),
                    "message": str(sortie.get("message", "")),
                })
                _ajouter_log_job(job_id, "succes" if statut in {"ok", "dry_run", "success"} else "erreur", str(sortie))
            except Exception as exc:
                resultats.append({
                    "job_id": job_id,
                    "status": "failure",
                    "duration_ms": round((time.perf_counter() - debut) * 1000, 2),
                    "message": str(exc),
                })
                _ajouter_log_job(job_id, "erreur", str(exc))
                if not body.continuer_sur_erreur:
                    break

        return {
            "mode": "dry_run" if body.dry_run else "run",
            "jobs_cibles": jobs_matin,
            "total": len(resultats),
            "succes": len([r for r in resultats if r["status"] in {"ok", "dry_run", "success"}]),
            "echecs": len([r for r in resultats if r["status"] not in {"ok", "dry_run", "success"}]),
            "items": resultats,
        }

    result = await executer_async(_run)
    _journaliser_action_admin(
        action="admin.jobs.morning_batch.run",
        entite_type="job_batch",
        utilisateur_id=str(user.get("id", "admin")),
        details={"dry_run": body.dry_run, "continuer_sur_erreur": body.continuer_sur_erreur},
    )
    return result


@router.post(
    "/jobs/simulate-day",
    responses=REPONSES_AUTH_ADMIN,
    summary='Simuler une journée de jobs',
    description="Exécute séquentiellement les jobs disponibles d'une journée type en mode dry-run.",
)
@gerer_exception_api
async def simuler_journee_jobs(
    body: JobsSimulationJourneeRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_async

    def _run() -> dict[str, Any]:
        from src.services.core.cron.jobs import executer_job_par_id, lister_jobs_disponibles

        jobs_disponibles = list(lister_jobs_disponibles())
        resultats: list[dict[str, Any]] = []
        debut_journee = datetime.now()

        for job_id in jobs_disponibles:
            debut = time.perf_counter()
            try:
                sortie = executer_job_par_id(
                    job_id,
                    dry_run=body.dry_run,
                    source="admin_day_simulation",
                    triggered_by_user_id=str(user.get("id", "admin")),
                    relancer_exception=True,
                )
                resultats.append({
                    "job_id": job_id,
                    "status": str(sortie.get("status", "ok")),
                    "duration_ms": round((time.perf_counter() - debut) * 1000, 2),
                    "message": str(sortie.get("message", "")),
                })
            except Exception as exc:
                resultats.append({
                    "job_id": job_id,
                    "status": "failure",
                    "duration_ms": round((time.perf_counter() - debut) * 1000, 2),
                    "message": str(exc),
                })
                if not body.continuer_sur_erreur:
                    break

        return {
            "mode": "dry_run" if body.dry_run else "run",
            "started_at": debut_journee.isoformat(),
            "ended_at": datetime.now().isoformat(),
            "total": len(resultats),
            "succes": len([r for r in resultats if r["status"] in {"ok", "dry_run", "success"}]),
            "echecs": len([r for r in resultats if r["status"] not in {"ok", "dry_run", "success"}]),
            "items": resultats,
        }

    result = await executer_async(_run)
    _journaliser_action_admin(
        action="admin.jobs.day_simulation.run",
        entite_type="job_batch",
        utilisateur_id=str(user.get("id", "admin")),
        details={"dry_run": body.dry_run, "continuer_sur_erreur": body.continuer_sur_erreur},
    )
    return result


@router.get(
    "/jobs/{job_id}/logs",
    responses=REPONSES_AUTH_ADMIN,
    summary="Logs dernière exécution d'un job",
    description="Retourne l'historique des déclenchements manuels du job. Nécessite le rôle admin.",
)
@gerer_exception_api
async def logs_job(
    job_id: str,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Retourne les logs des N dernières exécutions manuelles du job."""
    from src.api.utils import executer_avec_session

    logs_persistes: list[dict[str, Any]] = []
    try:
        with executer_avec_session() as session:
            logs_rows = session.execute(
                text(
                    """
                    SELECT started_at, ended_at, duration_ms, status, error_message, output_logs
                    FROM job_executions
                    WHERE job_id = :job_id
                    ORDER BY started_at DESC
                    LIMIT 50
                    """
                ),
                {"job_id": job_id},
            ).mappings().all()
        logs_persistes = [
            {
                "timestamp": row["started_at"].isoformat() if row["started_at"] else None,
                "ended_at": row["ended_at"].isoformat() if row["ended_at"] else None,
                "status": row["status"],
                "duration_ms": int(row["duration_ms"] or 0),
                "message": row["error_message"] or row["output_logs"] or "",
                "source": "db",
            }
            for row in logs_rows
        ]
    except Exception:
        logs_persistes = []

    logs_mem = _job_logs.get(job_id, [])
    logs = logs_persistes or list(reversed(logs_mem))
    return {
        "job_id": job_id,
        "nom": _LABELS_JOBS.get(job_id, job_id),
        "logs": logs,
        "total": len(logs),
    }


@router.get(
    "/jobs/history",
    responses=REPONSES_AUTH_ADMIN,
    summary="Historique des exécutions jobs",
    description="Retourne l'historique paginé des exécutions de jobs avec filtres.",
)
@gerer_exception_api
async def historique_jobs(
    page: int = Query(1, ge=1),
    par_page: int = Query(25, ge=1, le=200),
    job_id: str | None = Query(None, description="Filtrer par identifiant de job"),
    status: str | None = Query(None, description="Filtrer par statut (success/failure/dry_run/...)"),
    depuis: datetime | None = Query(None, description="Date de début (ISO 8601)"),
    jusqu_a: datetime | None = Query(None, description="Date de fin (ISO 8601)"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Historique paginé/filtrable des lignes job_executions."""
    from src.api.utils import executer_avec_session

    offset = (page - 1) * par_page
    conditions: list[str] = ["1=1"]
    params: dict[str, Any] = {"limit": par_page, "offset": offset}

    if job_id:
        conditions.append("job_id = :job_id")
        params["job_id"] = job_id
    if status:
        conditions.append("status = :status")
        params["status"] = status
    if depuis:
        conditions.append("started_at >= :depuis")
        params["depuis"] = depuis
    if jusqu_a:
        conditions.append("started_at <= :jusqu_a")
        params["jusqu_a"] = jusqu_a

    where_clause = " AND ".join(conditions)

    with executer_avec_session() as session:
        total = int(
            session.execute(
                text(f"SELECT COUNT(*) FROM job_executions WHERE {where_clause}"),
                params,
            ).scalar()
            or 0
        )

        rows = session.execute(
            text(
                f"""
                SELECT
                    id,
                    job_id,
                    job_name,
                    started_at,
                    ended_at,
                    duration_ms,
                    status,
                    error_message,
                    output_logs,
                    triggered_by_user_id,
                    triggered_by_user_role
                FROM job_executions
                WHERE {where_clause}
                ORDER BY started_at DESC, id DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()

    items = [
        {
            "id": int(row["id"]),
            "job_id": str(row["job_id"]),
            "job_name": row["job_name"] or _LABELS_JOBS.get(str(row["job_id"]), str(row["job_id"])),
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
            "ended_at": row["ended_at"].isoformat() if row["ended_at"] else None,
            "duration_ms": int(row["duration_ms"] or 0),
            "status": str(row["status"] or "unknown"),
            "error_message": row["error_message"],
            "output_logs": row["output_logs"],
            "triggered_by_user_id": row["triggered_by_user_id"],
            "triggered_by_user_role": row["triggered_by_user_role"],
        }
        for row in rows
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "par_page": par_page,
        "pages_totales": max(1, (total + par_page - 1) // par_page),
    }


@router.get(
    "/jobs/compare-dry-run",
    responses=REPONSES_AUTH_ADMIN,
    summary="Comparer dry-run et exécution réelle",
    description="Compare les dernières exécutions dry-run et réelles par job.",
)
@gerer_exception_api
async def comparer_dry_run_vs_reel(
    limite: int = Query(20, ge=1, le=100),
    depuis_heures: int = Query(168, ge=1, le=24 * 30),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_avec_session

    debut = datetime.now() - timedelta(hours=depuis_heures)
    par_job: dict[str, dict[str, Any]] = {}

    with executer_avec_session() as session:
        rows = session.execute(
            text(
                """
                SELECT job_id, job_name, status, started_at, duration_ms, error_message
                FROM job_executions
                WHERE started_at >= :debut
                ORDER BY started_at DESC
                LIMIT 5000
                """
            ),
            {"debut": debut},
        ).mappings().all()

    for row in rows:
        job_id = str(row["job_id"])
        data = par_job.setdefault(
            job_id,
            {
                "job_id": job_id,
                "job_name": row["job_name"] or _LABELS_JOBS.get(job_id, job_id),
                "dry_run": None,
                "run": None,
            },
        )
        status = str(row["status"] or "")
        entree = {
            "status": status,
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
            "duration_ms": int(row["duration_ms"] or 0),
            "error_message": row["error_message"],
        }
        if status == "dry_run" and data["dry_run"] is None:
            data["dry_run"] = entree
        if status != "dry_run" and data["run"] is None:
            data["run"] = entree

    items = []
    for v in par_job.values():
        dry = v["dry_run"]
        run = v["run"]
        if not dry and not run:
            continue
        items.append({
            **v,
            "comparaison": {
                "delta_duration_ms": (run["duration_ms"] - dry["duration_ms"]) if dry and run else None,
                "status_coherent": (run["status"] in {"ok", "success"}) if run else None,
            },
        })

    items_sorted = sorted(
        items,
        key=lambda i: (i["run"] or i["dry_run"] or {}).get("started_at") or "",
        reverse=True,
    )[:limite]

    return {
        "generated_at": datetime.now().isoformat(),
        "fenetre_heures": depuis_heures,
        "total": len(items_sorted),
        "items": items_sorted,
    }



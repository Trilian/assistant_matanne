"""Routes admin — Infrastructure (DB, Config, Console, DevTools)."""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from src.api.dependencies import require_auth, require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    AdminQuickCommandRequest,
    ConfigAdminExportRequest,
    ConfigAdminImportRequest,
    DbExportRequest,
    DbImportRequest,
    FeatureFlagsUpdateRequest,
    FlowSimulationRequest,
    ResetModuleRequest,
    RuntimeConfigUpdateRequest,
    _FEATURE_FLAGS_PAR_DEFAUT,
    _LABELS_JOBS,
    _MODULES_RESETABLES,
    _NAMESPACE_FEATURE_FLAGS,
    _NAMESPACE_RUNTIME_CONFIG,
    _RUNTIME_CONFIG_PAR_DEFAUT,
    _VUES_SQL_AUTORISEES,
    _admin_timestamps,
    _catalogue_actions_services,
    _cibles_resync,
    _ecrire_namespace_persistant,
    _exporter_config_admin,
    _executer_action_service,
    _importer_config_admin,
    _lire_namespace_persistant,
    _normaliser_nom_table,
    _parser_commande_rapide,
    _resumer_api_metrics,
    _serialiser_valeur_export_db,
    _simuler_flux_admin,
    _simuler_test_e2e_one_click,
    _verifier_limite_admin,
    est_mode_test_actif,
    _journaliser_action_admin,
    router,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# DB COHÉRENCE
# ═══════════════════════════════════════════════════════════


@router.get(
    "/db/coherence",
    responses=REPONSES_AUTH_ADMIN,
    summary="Test cohérence base de données",
    description="Lance des vérifications rapides d'intégrité DB. Nécessite le rôle admin.",
)
@gerer_exception_api
async def coherence_db(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Vérifie la cohérence de la base de données (checks rapides)."""
    from src.api.utils import executer_async, executer_avec_session

    def _check():
        resultats: list[dict] = []
        erreurs: list[str] = []

        with executer_avec_session() as session:
            # 1. Connexion DB
            try:
                session.execute(__import__("sqlalchemy").text("SELECT 1"))
                resultats.append({"check": "connexion_db", "status": "ok"})
            except Exception as exc:
                erreurs.append(f"connexion_db: {exc}")
                resultats.append({"check": "connexion_db", "status": "erreur", "detail": str(exc)})

            # 2. Tables principales présentes
            tables_essentielles = [
                "recettes", "articles_courses", "listes_courses",
                "inventaire_items", "profils_utilisateurs",
            ]
            try:
                from sqlalchemy import text

                for table in tables_essentielles:
                    try:
                        session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                        resultats.append({"check": f"table_{table}", "status": "ok"})
                    except Exception as exc:
                        erreurs.append(f"table_{table}: {exc}")
                        resultats.append({"check": f"table_{table}", "status": "erreur", "detail": str(exc)})
            except Exception as exc:
                erreurs.append(f"vérification tables: {exc}")

            # 3. Articles de courses sans liste parent (orphelins)
            try:
                from sqlalchemy import text

                row = session.execute(
                    text(
                        "SELECT COUNT(*) FROM articles_courses ac "
                        "LEFT JOIN listes_courses lc ON lc.id = ac.liste_id "
                        "WHERE lc.id IS NULL"
                    )
                ).scalar()
                resultats.append({
                    "check": "articles_orphelins",
                    "status": "ok" if (row or 0) == 0 else "avertissement",
                    "detail": f"{row} article(s) orphelin(s)",
                })
            except Exception as exc:
                logger.debug("Check articles orphelins ignoré: %s", exc)

        statut_global = "erreur" if erreurs else "ok"
        return {
            "status": statut_global,
            "checks": resultats,
            "erreurs": erreurs,
            "total_checks": len(resultats),
            "checks_ok": sum(1 for c in resultats if c["status"] == "ok"),
        }

    return await executer_async(_check)


@router.get(
    "/db/export",
    responses=REPONSES_AUTH_ADMIN,
    summary="Exporter la base en JSON",
    description="Exporte un snapshot JSON des tables publiques (dev/test recommandé).",
)
@gerer_exception_api
async def exporter_db_json(
    format: str = Query("json", pattern="^json$"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Exporte les données des tables publiques en JSON."""
    from src.api.utils import executer_avec_session

    with executer_avec_session() as session:
        rows = session.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            )
        ).mappings().all()

        tables = [str(row["table_name"]) for row in rows if row.get("table_name")]
        data: dict[str, list[dict[str, Any]]] = {}

        for table_name in tables:
            safe_table = _normaliser_nom_table(table_name)
            records = session.execute(
                text(f'SELECT * FROM "{safe_table}"')
            ).mappings().all()
            data[safe_table] = [
                {k: _serialiser_valeur_export_db(v) for k, v in dict(record).items()}
                for record in records
            ]

    _journaliser_action_admin(
        action="admin.db.export",
        entite_type="database",
        utilisateur_id=str(user.get("id", "admin")),
        details={"tables": len(data)},
    )
    return {
        "format": format,
        "exported_at": datetime.now().isoformat(),
        "tables": data,
        "total_tables": len(data),
    }


@router.post(
    "/db/import",
    responses=REPONSES_AUTH_ADMIN,
    summary="Importer un snapshot JSON en base",
    description="Restaure des données depuis un payload JSON table->records (mode merge ou replace).",
)
@gerer_exception_api
async def importer_db_json(
    body: DbImportRequest = Body(...),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Importe des données JSON en base, table par table."""
    from src.api.utils import executer_avec_session
    from src.core.config import obtenir_parametres

    env = obtenir_parametres().ENV.lower()
    if env not in {"development", "dev", "test"}:
        raise HTTPException(status_code=403, detail="Import DB autorisé uniquement en dev/test.")

    resultats: dict[str, Any] = {}
    with executer_avec_session() as session:
        for table_name, records in body.tables.items():
            safe_table = _normaliser_nom_table(table_name)
            if not isinstance(records, list):
                raise HTTPException(status_code=422, detail=f"Format invalide pour la table {safe_table}.")

            if not body.merge:
                session.execute(text(f'TRUNCATE TABLE "{safe_table}" RESTART IDENTITY CASCADE'))

            imported = 0
            for record in records:
                if not isinstance(record, dict) or not record:
                    continue
                colonnes = [k for k in record.keys() if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(k))]
                if not colonnes:
                    continue
                placeholders = ", ".join(f":{c}" for c in colonnes)
                cols_sql = ", ".join(f'"{c}"' for c in colonnes)
                stmt = text(f'INSERT INTO "{safe_table}" ({cols_sql}) VALUES ({placeholders})')
                session.execute(stmt, {c: record.get(c) for c in colonnes})
                imported += 1

            resultats[safe_table] = {"imported": imported, "merge": body.merge}
        session.commit()

    _journaliser_action_admin(
        action="admin.db.import",
        entite_type="database",
        utilisateur_id=str(user.get("id", "admin")),
        details={"tables": list(resultats.keys()), "merge": body.merge},
    )
    return {
        "status": "ok",
        "imported_tables": len(resultats),
        "resultats": resultats,
    }


# ═══════════════════════════════════════════════════════════
# DASHBOARD ADMIN CONSOLIDÉ
# ═══════════════════════════════════════════════════════════


@router.get(
    "/dashboard",
    responses=REPONSES_AUTH_ADMIN,
    summary="Dashboard admin consolidé",
    description="Retourne une vue consolidée des métriques admin (audit, jobs, services, cache, sécurité).",
)
@gerer_exception_api
async def dashboard_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Vue consolidée pour le cockpit admin."""
    from src.api.utils import executer_async, executer_avec_session

    def _query():
        from src.services.core.cron.jobs import _demarreur
        from src.services.core.registry import registre

        jobs = []
        if _demarreur is not None and _demarreur._scheduler.running:
            jobs = list(_demarreur._scheduler.get_jobs())

        jobs_actifs = sum(1 for j in jobs if j.next_run_time is not None)

        try:
            from src.core.caching import obtenir_cache

            cache_stats = (
                obtenir_cache().obtenir_statistiques() if hasattr(obtenir_cache(), "obtenir_statistiques") else {}
            )
        except Exception:
            cache_stats = {}

        security_24h = 0
        dernieres_executions_jobs: list[dict[str, Any]] = []
        metriques_ia: dict[str, Any] = {}
        with executer_avec_session() as session:
            security_24h = int(
                session.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM logs_securite
                        WHERE created_at >= NOW() - INTERVAL '24 HOURS'
                        """
                    )
                ).scalar()
                or 0
            )

            rows = session.execute(
                text(
                    """
                    SELECT job_id, status, started_at, duration_ms
                    FROM job_executions
                    ORDER BY started_at DESC
                    LIMIT 8
                    """
                )
            ).mappings().all()
            dernieres_executions_jobs = [
                {
                    "job_id": str(r["job_id"]),
                    "job_name": _LABELS_JOBS.get(str(r["job_id"]), str(r["job_id"])),
                    "status": str(r["status"] or "unknown"),
                    "started_at": r["started_at"].isoformat() if r["started_at"] else None,
                    "duration_ms": int(r["duration_ms"] or 0),
                }
                for r in rows
            ]

        try:
            metriques_ia = _resumer_api_metrics().get("ai", {})
        except Exception:
            metriques_ia = {}

        return {
            "generated_at": datetime.now().isoformat(),
            "jobs": {
                "total": len(jobs),
                "actifs": jobs_actifs,
                "inactifs": max(0, len(jobs) - jobs_actifs),
            },
            "services": registre.health_check_global(),
            "metriques_services": registre.obtenir_metriques(),
            "cache": cache_stats,
            "security": {
                "events_24h": security_24h,
            },
            "jobs_recents": dernieres_executions_jobs,
            "ia": metriques_ia,
            "feature_flags": _lire_namespace_persistant(
                _NAMESPACE_FEATURE_FLAGS,
                _FEATURE_FLAGS_PAR_DEFAUT,
            ),
        }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SERVICE ACTIONS MANUELLES
# ═══════════════════════════════════════════════════════════


@router.get(
    "/services/actions",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les actions de service manuelles",
    description="Catalogue d'actions de services exécutables manuellement depuis l'admin.",
)
@gerer_exception_api
async def lister_actions_services(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {
        "items": _catalogue_actions_services(),
        "total": len(_catalogue_actions_services()),
        "enabled": bool(flags.get("admin.service_actions_enabled", True)),
    }


@router.post(
    "/services/actions/{action_id}/run",
    responses=REPONSES_AUTH_ADMIN,
    summary="Exécuter une action de service",
    description="Lance une action de service whitelistée (avec support dry-run selon l'action).",
)
@gerer_exception_api
async def executer_action_service(
    action_id: str,
    body: ServiceActionRunRequest,
    dry_run: bool = Query(False, description="Simulation sans écriture"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_async

    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    if not bool(flags.get("admin.service_actions_enabled", True)):
        raise HTTPException(status_code=403, detail="Les actions de service manuelles sont désactivées.")

    result = await executer_async(
        lambda: _executer_action_service(action_id, dry_run=dry_run, params=body.params)
    )
    _journaliser_action_admin(
        action="admin.service_action.run",
        entite_type="service_action",
        utilisateur_id=str(user.get("id", "admin")),
        details={"action_id": action_id, "dry_run": dry_run},
    )
    return result


# ═══════════════════════════════════════════════════════════
# FEATURE FLAGS & CONFIG RUNTIME
# ═══════════════════════════════════════════════════════════


@router.get(
    "/feature-flags",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lire les feature flags",
    description="Retourne les feature flags runtime modifiables depuis l'admin.",
)
@gerer_exception_api
async def lire_feature_flags(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {"flags": flags, "total": len(flags)}


@router.put(
    "/feature-flags",
    responses=REPONSES_AUTH_ADMIN,
    summary="Mettre à jour les feature flags",
    description="Met à jour les feature flags runtime côté admin.",
)
@gerer_exception_api
async def mettre_a_jour_feature_flags(
    body: FeatureFlagsUpdateRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _ecrire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, body.flags)
    _journaliser_action_admin(
        action="admin.feature_flags.update",
        entite_type="feature_flag",
        utilisateur_id=str(user.get("id", "admin")),
        details={"updates": body.flags},
    )
    return {"status": "ok", "flags": flags, "total": len(flags)}


@router.get(
    "/mode-test",
    responses=REPONSES_AUTH_ADMIN,
    summary="État du mode test",
    description="Retourne si le mode test admin est actif. "
    "Quand actif : logs verbose, rate-limiting désactivé, IDs internes visibles.",
)
@gerer_exception_api
async def lire_mode_test(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    return {"mode_test": est_mode_test_actif()}


@router.put(
    "/mode-test",
    responses=REPONSES_AUTH_ADMIN,
    summary="Activer / désactiver le mode test",
    description="Bascule le mode test admin.",
)
@gerer_exception_api
async def basculer_mode_test(
    body: dict[str, bool],
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    actif = bool(body.get("enabled", False))
    _ecrire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, {"admin.mode_test": actif})
    _journaliser_action_admin(
        action="admin.mode_test.toggle",
        entite_type="feature_flag",
        utilisateur_id=str(user.get("id", "admin")),
        details={"mode_test": actif},
    )
    return {"status": "ok", "mode_test": actif}


@router.get(
    "/maintenance",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lire le mode maintenance",
    description="Retourne l'état du mode maintenance (feature flag runtime).",
)
@gerer_exception_api
async def lire_mode_maintenance(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {"maintenance_mode": bool(flags.get("admin.maintenance_mode", False))}


@router.put(
    "/maintenance",
    responses=REPONSES_AUTH_ADMIN,
    summary="Basculer le mode maintenance",
    description="Active ou désactive le mode maintenance global.",
)
@gerer_exception_api
async def basculer_mode_maintenance(
    body: MaintenanceModeRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _ecrire_namespace_persistant(
        _NAMESPACE_FEATURE_FLAGS,
        {"admin.maintenance_mode": body.enabled},
    )
    # Activation instantanée in-process (pas de délai de cache DB)
    from src.api.main import activer_maintenance
    activer_maintenance(body.enabled)
    _journaliser_action_admin(
        action="admin.maintenance.toggle",
        entite_type="feature_flag",
        utilisateur_id=str(user.get("id", "admin")),
        details={"maintenance_mode": body.enabled},
    )
    return {"status": "ok", "maintenance_mode": bool(flags.get("admin.maintenance_mode", False))}


@router.get(
    "/public/maintenance",
    summary="État public du mode maintenance",
    description="Endpoint lecture seule pour afficher un bandeau maintenance côté UI.",
)
@gerer_exception_api
async def lire_mode_maintenance_public(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {"maintenance_mode": bool(flags.get("admin.maintenance_mode", False))}


@router.get(
    "/runtime-config",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lire la configuration runtime admin",
    description="Retourne la configuration runtime éditable et quelques valeurs système en lecture seule.",
)
@gerer_exception_api
async def lire_runtime_config(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.core.config import obtenir_parametres

    params = obtenir_parametres()
    runtime = _lire_namespace_persistant(_NAMESPACE_RUNTIME_CONFIG, _RUNTIME_CONFIG_PAR_DEFAUT)
    readonly = {
        "env": params.ENV,
        "debug": params.DEBUG,
        "mistral_model": params.MISTRAL_MODEL,
        "cache_enabled": params.CACHE_ENABLED,
        "log_level": params.LOG_LEVEL,
    }
    return {"values": runtime, "readonly": readonly}


@router.put(
    "/runtime-config",
    responses=REPONSES_AUTH_ADMIN,
    summary="Mettre à jour la configuration runtime admin",
    description="Met à jour la configuration runtime éditable stockée côté serveur.",
)
@gerer_exception_api
async def mettre_a_jour_runtime_config(
    body: RuntimeConfigUpdateRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    values = _ecrire_namespace_persistant(_NAMESPACE_RUNTIME_CONFIG, body.values)
    _journaliser_action_admin(
        action="admin.runtime_config.update",
        entite_type="runtime_config",
        utilisateur_id=str(user.get("id", "admin")),
        details={"updates": body.values},
    )
    return {"status": "ok", "values": values}


@router.get(
    "/config/export",
    responses=REPONSES_AUTH_ADMIN,
    summary="Exporter la configuration admin",
    description="Exporte les feature flags et la configuration runtime persistée.",
)
@gerer_exception_api
async def exporter_config_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    return _exporter_config_admin()


@router.post(
    "/config/import",
    responses=REPONSES_AUTH_ADMIN,
    summary="Importer la configuration admin",
    description="Importe les feature flags et la configuration runtime persistée.",
)
@gerer_exception_api
async def importer_config_admin(
    body: ConfigImportRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    result = _importer_config_admin(body)
    _journaliser_action_admin(
        action="admin.config.import",
        entite_type="runtime_config",
        utilisateur_id=str(user.get("id", "admin")),
        details={
            "merge": body.merge,
            "feature_flags": list((body.feature_flags or {}).keys()),
            "runtime_config": list((body.runtime_config or {}).keys()),
        },
    )
    return {"status": "ok", **result}


# ═══════════════════════════════════════════════════════════
# D1 — Console commande rapide admin
# ═══════════════════════════════════════════════════════════


class AdminQuickCommandRequest(BaseModel):
    """Requête pour la console de commande rapide admin."""

    commande: str


_COMMANDES_RAPIDES: dict[str, str] = {
    "run job": "Exécuter un job CRON — ex: run job rappels_famille",
    "clear cache": "Vider le cache — ex: clear cache (tout) ou clear cache recettes*",
    "list jobs": "Lister tous les jobs disponibles",
    "test complet": "Simuler un test E2E one-click (recette -> planning -> courses -> checkout -> inventaire)",
    "health": "Vérifier la santé des services",
    "stats cache": "Afficher les statistiques du cache",
    "maintenance on": "Activer le mode maintenance",
    "maintenance off": "Désactiver le mode maintenance",
    "help": "Afficher l'aide des commandes",
}


def _parser_commande_rapide(commande: str) -> dict[str, Any]:
    """Parse et exécute une commande rapide admin.

    Commandes supportées :
    - run job <job_id> [--dry-run]
    - clear cache [pattern]
    - list jobs
    - health
    - stats cache
    - maintenance on|off
    - help
    """
    commande = commande.strip()
    cmd_lower = commande.lower()

    if cmd_lower == "help" or cmd_lower == "?":
        return {
            "type": "help",
            "commandes": _COMMANDES_RAPIDES,
            "message": "Commandes disponibles",
        }

    if cmd_lower == "list jobs":
        from src.services.core.cron.jobs import lister_jobs_disponibles

        jobs = lister_jobs_disponibles()
        return {
            "type": "list_jobs",
            "jobs": jobs,
            "total": len(jobs),
            "message": f"{len(jobs)} jobs disponibles",
        }

    if cmd_lower == "test complet":
        return {
            "type": "test_e2e",
            "result": _simuler_test_e2e_one_click("admin"),
            "message": "Simulation E2E one-click exécutée",
        }

    if cmd_lower.startswith("run job "):
        parts = commande[8:].strip().split()
        job_id = parts[0] if parts else ""
        dry_run = "--dry-run" in parts

        if not job_id:
            return {"type": "error", "message": "Usage: run job <job_id> [--dry-run]"}

        from src.services.core.cron.jobs import executer_job_par_id

        try:
            result = executer_job_par_id(job_id, dry_run=dry_run, source="admin_console")
            return {"type": "job_result", "result": result, "message": f"Job '{job_id}' exécuté"}
        except ValueError as e:
            return {"type": "error", "message": str(e)}

    if cmd_lower.startswith("clear cache"):
        pattern = commande[11:].strip() or "*"
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            nb = 0
            if pattern == "*" or not pattern:
                if hasattr(cache, "vider"):
                    cache.vider()
                    nb = -1  # Tout vidé
            elif hasattr(cache, "invalider"):
                nb = cache.invalider(pattern)
            return {
                "type": "cache_cleared",
                "pattern": pattern,
                "nb_invalidees": nb,
                "message": f"Cache vidé (pattern: {pattern})",
            }
        except Exception as e:
            return {"type": "error", "message": f"Erreur cache: {e}"}

    if cmd_lower == "health":
        try:
            from src.services.core.registry import obtenir_registre_services

            registre = obtenir_registre_services()
            health = registre.health_check()
            return {
                "type": "health",
                "result": health,
                "message": f"Santé: {health.get('global_status', 'unknown')}",
            }
        except Exception as e:
            return {"type": "error", "message": f"Erreur health: {e}"}

    if cmd_lower == "stats cache":
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            stats = cache.obtenir_statistiques() if hasattr(cache, "obtenir_statistiques") else {}
            return {
                "type": "cache_stats",
                "result": stats,
                "message": "Statistiques cache",
            }
        except Exception as e:
            return {"type": "error", "message": f"Erreur stats cache: {e}"}

    if cmd_lower in ("maintenance on", "maintenance off"):
        activer = cmd_lower == "maintenance on"
        try:
            from src.core.db import obtenir_contexte_db

            with obtenir_contexte_db() as session:
                session.execute(
                    text(
                        """
                        INSERT INTO etats_persistants (namespace, cle, valeur, user_id, created_at, modified_at)
                        VALUES ('admin_feature_flags', 'admin.maintenance_mode', :val, 'system', NOW(), NOW())
                        ON CONFLICT (namespace, cle) DO UPDATE SET valeur = :val, modified_at = NOW()
                        """
                    ),
                    {"val": json.dumps(activer)},
                )
                session.commit()
            return {
                "type": "maintenance",
                "enabled": activer,
                "message": f"Mode maintenance {'activé' if activer else 'désactivé'}",
            }
        except Exception as e:
            return {"type": "error", "message": f"Erreur maintenance: {e}"}

    return {"type": "error", "message": f"Commande inconnue: '{commande}'. Tapez 'help' pour l'aide."}


@router.post(
    "/quick-command",
    responses=REPONSES_AUTH_ADMIN,
    summary="Console commande rapide admin",
    description="Exécute une commande rapide admin (run job, clear cache, health, etc.).",
)
@gerer_exception_api
async def executer_commande_rapide(
    body: AdminQuickCommandRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    result = _parser_commande_rapide(body.commande)
    _journaliser_action_admin(
        action="admin.quick_command",
        entite_type="console",
        utilisateur_id=str(user.get("id", "admin")),
        details={"commande": body.commande, "type_resultat": result.get("type")},
    )
    return {"status": "ok", **result}


@router.post(
    "/flow-simulator",
    responses=REPONSES_AUTH_ADMIN,
    summary="Simuler un flux",
    description="Prévisualise un flux inter-modules/admin sans exécution réelle.",
)
@gerer_exception_api
async def simuler_flux_admin(
    body: FlowSimulationRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    cible_user_id = body.user_id or str(user.get("id", "admin"))
    result = _simuler_flux_admin(body, cible_user_id)
    _journaliser_action_admin(
        action="admin.flow.simulate",
        entite_type="simulation",
        utilisateur_id=str(user.get("id", "admin")),
        details={"scenario": body.scenario, "target_user_id": cible_user_id},
    )
    return result


@router.post(
    "/tests/e2e-one-click",
    responses=REPONSES_AUTH_ADMIN,
    summary="Test E2E one-click (simulation)",
    description="Simule le flux recette->planning->courses->checkout->inventaire en une seule requête.",
)
@gerer_exception_api
async def lancer_test_e2e_one_click(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    cible_user_id = str(user.get("id", "admin"))
    result = _simuler_test_e2e_one_click(cible_user_id)
    _journaliser_action_admin(
        action="admin.tests.e2e_one_click",
        entite_type="simulation",
        utilisateur_id=cible_user_id,
        details={"workflow": result.get("workflow")},
    )
    return result


@router.get(
    "/live-snapshot",
    responses=REPONSES_AUTH_ADMIN,
    summary="Snapshot live admin",
    description="Retourne un snapshot temps réel du cockpit admin.",
)
@gerer_exception_api
async def snapshot_live_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_avec_session

    cache_stats = {}
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        if hasattr(cache, "obtenir_statistiques"):
            cache_stats = cache.obtenir_statistiques()
    except Exception:
        cache_stats = {}

    executions_recentes: dict[str, int] = {"success": 0, "failure": 0, "dry_run": 0}
    evenements_securite_1h = 0
    try:
        with executer_avec_session() as session:
            rows = session.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS total
                    FROM job_executions
                    WHERE started_at >= NOW() - INTERVAL '24 HOURS'
                    GROUP BY status
                    """
                )
            ).mappings().all()
            for row in rows:
                status = str(row["status"] or "unknown")
                executions_recentes[status] = int(row["total"] or 0)

            evenements_securite_1h = int(
                session.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM logs_securite
                        WHERE created_at >= NOW() - INTERVAL '1 HOUR'
                        """
                    )
                ).scalar()
                or 0
            )
    except Exception:
        executions_recentes = {"success": 0, "failure": 0, "dry_run": 0}
        evenements_securite_1h = 0

    return {
        "generated_at": datetime.now().isoformat(),
        "api": _resumer_api_metrics(),
        "cache": cache_stats,
        "jobs": {"last_24h": executions_recentes},
        "security": {"events_1h": evenements_securite_1h},
    }


# ═══════════════════════════════════════════════════════════
# FORCER RE-SYNC EXTERNES
# ═══════════════════════════════════════════════════════════


@router.get(
    "/resync/targets",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les cibles de re-sync",
    description="Catalogue des synchronisations externes déclenchables manuellement.",
)
@gerer_exception_api
async def lister_cibles_resync(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {
        "items": _cibles_resync(),
        "total": len(_cibles_resync()),
        "enabled": bool(flags.get("admin.resync_enabled", True)),
    }


@router.post(
    "/resync/{target_id}",
    responses=REPONSES_AUTH_ADMIN,
    summary="Forcer une synchronisation externe",
    description="Déclenche une synchronisation externe (Garmin, Google Calendar, OpenFoodFacts).",
)
@gerer_exception_api
async def forcer_resync(
    target_id: str,
    dry_run: bool = Query(False, description="Simuler sans exécution"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.services.core.cron.jobs import executer_job_par_id

    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    if not bool(flags.get("admin.resync_enabled", True)):
        raise HTTPException(status_code=403, detail="Les actions de re-sync sont désactivées.")

    cible = next((c for c in _cibles_resync() if c["id"] == target_id), None)
    if cible is None:
        raise HTTPException(status_code=404, detail=f"Cible de re-sync inconnue: {target_id}")

    result = executer_job_par_id(
        cible["job_id"],
        dry_run=dry_run,
        source="manual",
        triggered_by_user_id=str(user.get("id", "admin")),
        relancer_exception=False,
    )
    _journaliser_action_admin(
        action="admin.resync.run",
        entite_type="resync",
        utilisateur_id=str(user.get("id", "admin")),
        details={"target": target_id, "dry_run": dry_run},
    )
    return {"target": target_id, **result}


# ═══════════════════════════════════════════════════════════
# SEED DEV
# ═══════════════════════════════════════════════════════════


@router.post(
    "/seed/dev",
    responses=REPONSES_AUTH_ADMIN,
    summary="Injecter des données seed (dev)",
    description="Injecte des données de seed en environnement dev/test uniquement.",
)
@gerer_exception_api
async def injecter_seed_dev(
    body: SeedDataRequest,
    dry_run: bool = Query(False, description="Simulation sans écriture"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.core.config import obtenir_parametres

    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    if not bool(flags.get("admin.seed_dev_enabled", True)):
        raise HTTPException(status_code=403, detail="Le seed dev est désactivé.")

    env = obtenir_parametres().ENV.lower()
    if env not in {"development", "dev", "test"}:
        raise HTTPException(status_code=403, detail="Le seed est autorisé uniquement en dev/test.")

    if body.scope != "recettes_standard":
        raise HTTPException(status_code=422, detail=f"Scope seed non supporté: {body.scope}")

    seed_file = Path("data/seed/recettes_standard.json")
    if dry_run:
        total = 0
        try:
            payload = json.loads(seed_file.read_text(encoding="utf-8"))
            total = len(payload.get("recettes_standard", []))
        except Exception:
            total = 0

        return {
            "status": "dry_run",
            "scope": body.scope,
            "file": str(seed_file),
            "recettes_detectees": total,
            "message": "Simulation uniquement - aucune écriture DB.",
        }

    from scripts.db.import_recettes import importer_recettes_standard

    imported = int(importer_recettes_standard())
    _journaliser_action_admin(
        action="admin.seed.run",
        entite_type="seed",
        utilisateur_id=str(user.get("id", "admin")),
        details={"scope": body.scope, "imported": imported},
    )
    return {
        "status": "ok",
        "scope": body.scope,
        "imported": imported,
        "message": f"Seed terminé ({imported} recette(s) importée(s)).",
    }


@router.get(
    "/sql-views",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les vues SQL exposées",
    description="Retourne la liste des vues SQL disponibles via l'API admin (lecture seule).",
)
@gerer_exception_api
async def lister_vues_sql(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Liste blanche des vues SQL consultables depuis l'admin."""
    return {
        "items": [
            {"nom": nom_vue, "endpoint": f"/api/v1/admin/sql-views/{nom_vue}"}
            for nom_vue in _VUES_SQL_AUTORISEES
        ],
        "total": len(_VUES_SQL_AUTORISEES),
    }


@router.get(
    "/sql-views/{view_name}",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lire une vue SQL exposée",
    description="Exécute un SELECT paginé en lecture seule sur une vue SQL autorisée.",
)
@gerer_exception_api
async def lire_vue_sql(
    view_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Retourne les lignes d'une vue SQL autorisée."""
    from sqlalchemy import text

    from src.api.utils import executer_avec_session

    if view_name not in _VUES_SQL_AUTORISEES:
        raise HTTPException(
            status_code=404,
            detail=f"Vue SQL '{view_name}' non exposée.",
        )

    offset = (page - 1) * page_size

    with executer_avec_session() as session:
        total = int(
            session.execute(text(f"SELECT COUNT(*) FROM {view_name}")).scalar() or 0
        )
        rows = session.execute(
            text(
                f"SELECT * FROM {view_name} "
                "ORDER BY 1 "
                "LIMIT :limit OFFSET :offset"
            ),
            {"limit": page_size, "offset": offset},
        ).mappings().all()

    items = [dict(row) for row in rows]
    return {
        "view": view_name,
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages_totales": max(1, (total + page_size - 1) // page_size),
    }


# ═══════════════════════════════════════════════════════════
# PHASE 10 — RESET MODULE + LOGS WS ADMIN
# ═══════════════════════════════════════════════════════════


_MODULES_RESETABLES = {
    "courses": ["listes_courses", "articles_courses"],
    "inventaire": ["articles_inventaire"],
    "planning": ["repas", "plannings"],
    "jeux": ["paris_sportifs"],
}


class ResetModuleRequest(BaseModel):
    """Requête de réinitialisation d'un module."""

    module: str
    confirmer: bool = False


@router.post(
    "/reset-module",
    responses=REPONSES_AUTH_ADMIN,
    summary="Réinitialiser un module (données de test)",
)
@gerer_exception_api
async def reset_module(
    body: ResetModuleRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Remet à zéro les données d'un module (courses, inventaire, planning, jeux).

    Nécessite `confirmer: true` pour exécuter.
    """
    from src.core.config import obtenir_parametres

    env = obtenir_parametres().ENV.lower()
    if env not in {"development", "dev", "test"}:
        raise HTTPException(status_code=403, detail="Reset module autorisé uniquement en dev/test.")

    if body.module not in _MODULES_RESETABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Module '{body.module}' non réinitialisable. Modules disponibles: {list(_MODULES_RESETABLES.keys())}",
        )

    if not body.confirmer:
        tables = _MODULES_RESETABLES[body.module]
        return {
            "status": "preview",
            "module": body.module,
            "tables_affectees": tables,
            "message": f"⚠️ Ceci supprimera toutes les données de {body.module}. Envoyez 'confirmer: true' pour exécuter.",
        }

    from src.api.utils import executer_avec_session

    tables = _MODULES_RESETABLES[body.module]
    resultats = {}

    with executer_avec_session() as session:
        for table in tables:
            try:
                count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0
                session.execute(text(f"DELETE FROM {table}"))
                resultats[table] = {"supprimees": count}
            except Exception as exc:
                resultats[table] = {"erreur": str(exc)}
        session.commit()

    _journaliser_action_admin(
        action="admin.reset_module",
        entite_type=body.module,
        utilisateur_id=str(user.get("id", "admin")),
        details={"tables": tables, "resultats": resultats},
    )

    return {
        "status": "ok",
        "module": body.module,
        "resultats": resultats,
    }


@router.get(
    "/logs/stream-info",
    responses=REPONSES_AUTH_ADMIN,
    summary="Informations sur le stream de logs",
)
@gerer_exception_api
async def logs_stream_info(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Retourne les informations pour se connecter au stream de logs temps réel.

    Le stream est disponible via WebSocket sur /api/v1/ws/admin/logs.
    """
    return {
        "websocket_url": "/api/v1/ws/admin/logs",
        "description": "Stream de logs structurés en temps réel (WebSocket)",
        "message_format": {
            "type": "log_entry",
            "timestamp": "ISO 8601",
            "level": "DEBUG|INFO|WARNING|ERROR",
            "module": "src.api.routes.admin",
            "message": "Texte du log",
        },
    }

"""Jobs CRON pour admin, backup et automatisations."""

from __future__ import annotations

import json
import logging
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Callable, cast

from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

logger = logging.getLogger(__name__)


def executer_job_rappels_jardin_saisonniers(
    envoyer_notif_tous_users: Callable[..., dict[str, bool]],
) -> None:
    """D5: Rappels jardin saisonniers — hebdomadaire lundi 07h."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        aujourd_hui = date.today()
        mois = aujourd_hui.month

        if mois in (3, 4, 5):
            saison = "printemps"
        elif mois in (6, 7, 8):
            saison = "ete"
        elif mois in (9, 10, 11):
            saison = "automne"
        else:
            saison = "hiver"

        catalogue_path = Path("data/reference/plantes_catalogue.json")
        rappels: list[str] = []

        if catalogue_path.exists():
            catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
            plantes: list[dict[str, Any]]
            if isinstance(catalogue, list):
                plantes = [cast(dict[str, Any], p) for p in catalogue if isinstance(p, dict)]
            elif isinstance(catalogue, dict):
                brut = catalogue.get("plantes", [])
                plantes = [cast(dict[str, Any], p) for p in brut if isinstance(p, dict)] if isinstance(brut, list) else []
            else:
                plantes = []

            for plante in plantes:
                nom = str(plante.get("nom", ""))
                saisons = plante.get("saisons", {})
                if not isinstance(saisons, dict):
                    continue
                actions_saison = saisons.get(saison, [])
                if isinstance(actions_saison, list):
                    for action in actions_saison:
                        rappels.append(f"• {nom}: {str(action)}")
                elif isinstance(actions_saison, str) and actions_saison:
                    rappels.append(f"• {nom}: {actions_saison}")

        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import text as sql_text

                plantes_db = session.execute(
                    sql_text(
                        """
                        SELECT nom, type_plante, emplacement
                        FROM plantes_jardin
                        WHERE actif = true
                        ORDER BY nom
                        LIMIT 20
                        """
                    )
                ).fetchall()
                if plantes_db:
                    rappels.append("\n🌱 Vos plantes actives:")
                    for p in plantes_db:
                        rappels.append(f"  • {p.nom} ({p.type_plante or 'non classé'}) — {p.emplacement or '?'}")
        except Exception:
            logger.debug("Table plantes_jardin non disponible")

        if not rappels:
            logger.info("D5: Aucun rappel jardin pour la saison %s", saison)
            return

        emoji_saison = {"printemps": "🌸", "ete": "☀️", "automne": "🍂", "hiver": "❄️"}
        message = (
            f"{emoji_saison.get(saison, '🌿')} Rappels jardin — {saison.capitalize()}\n\n"
            + "\n".join(rappels[:15])
        )

        dispatcher = get_dispatcher_notifications()
        envoyer_notif_tous_users(
            dispatcher,
            message=message,
            canaux=["push", "ntfy"],
            titre=f"Jardin — {saison.capitalize()}",
        )
        logger.info("D5: %d rappel(s) jardin envoyé(s) pour %s", len(rappels), saison)
    except Exception:
        logger.exception("Erreur job D5 rappels jardin saisonniers")


def executer_job_verification_sante_systeme(
    obtenir_admin_user_ids: Callable[[], list[str]],
) -> None:
    """D6: Vérification santé système — horaire, alerte ntfy si service down."""
    try:
        alertes: list[str] = []
        services_ok = 0
        services_total = 0

        services_total += 1
        try:
            from src.core.db import obtenir_contexte_db

            with obtenir_contexte_db() as session:
                from sqlalchemy import text as sql_text

                session.execute(sql_text("SELECT 1")).scalar()
            services_ok += 1
        except Exception as e:
            alertes.append(f"🔴 Base de données: {str(e)[:100]}")

        services_total += 1
        try:
            from src.services.core.registry import obtenir_registre

            registre = obtenir_registre()
            health = registre.health_check_global()
            if health.get("global_status") == "healthy":
                services_ok += 1
            else:
                erreurs = health.get("erreurs", [])
                if erreurs:
                    alertes.append(f"🟡 Registre services: {'; '.join(erreurs[:3])}")
                else:
                    services_ok += 1
        except Exception as e:
            alertes.append(f"🔴 Registre services: {str(e)[:100]}")

        services_total += 1
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            if hasattr(cache, "obtenir_statistiques"):
                cache.obtenir_statistiques()
            services_ok += 1
        except Exception as e:
            alertes.append(f"🟡 Cache: {str(e)[:100]}")

        services_total += 1
        try:
            usage = shutil.disk_usage("/")
            pct_libre = usage.free / usage.total * 100
            if pct_libre < 10:
                alertes.append(f"🔴 Disque: seulement {pct_libre:.1f}% libre")
            else:
                services_ok += 1
        except Exception:
            services_ok += 1

        if alertes:
            message = (
                f"⚠️ Santé système — {services_ok}/{services_total} services OK\n\n"
                + "\n".join(alertes)
            )
            try:
                dispatcher = get_dispatcher_notifications()
                for admin_id in obtenir_admin_user_ids():
                    dispatcher.envoyer(
                        user_id=admin_id,
                        message=message,
                        canaux=["ntfy"],
                        titre="Alerte santé système",
                    )
            except Exception:
                logger.error("Impossible d'envoyer l'alerte santé système")
            logger.warning("D6: %d alerte(s) santé système", len(alertes))
        else:
            logger.info("D6: Tous les services OK (%d/%d)", services_ok, services_total)
    except Exception:
        logger.exception("Erreur job D6 vérification santé système")


def executer_job_backup_auto_hebdo_json() -> None:
    """D7: Backup automatique hebdomadaire JSON — dimanche 04h."""
    try:
        from src.core.db import obtenir_contexte_db

        backup_dir = Path("data/exports/backup_auto")
        backup_dir.mkdir(parents=True, exist_ok=True)

        aujourd_hui = date.today()
        filename = f"backup_{aujourd_hui:%Y%m%d}.json"
        filepath = backup_dir / filename

        tables_critiques = [
            "recettes",
            "plannings",
            "listes_courses",
            "articles_courses",
            "inventaire",
            "enfants",
            "jalons_enfant",
            "depenses",
            "budgets_mensuels",
            "projets_maison",
            "plantes_jardin",
            "routines",
            "profils_utilisateurs",
            "documents_famille",
            "contacts_famille",
        ]

        export_data: dict[str, list[dict[str, Any]]] = {}
        total_rows = 0

        with obtenir_contexte_db() as session:
            from sqlalchemy import text as sql_text

            for table_name in tables_critiques:
                try:
                    result = session.execute(sql_text(f"SELECT * FROM {table_name} LIMIT 10000"))  # noqa: S608
                    mappings = result.mappings().all()
                    rows = [dict(m) for m in mappings]
                    cleaned_rows: list[dict[str, Any]] = []
                    for row in rows:
                        cleaned = {}
                        for k, v in row.items():
                            if isinstance(v, (datetime, date)):
                                cleaned[k] = v.isoformat()
                            elif hasattr(v, "__str__"):
                                cleaned[k] = str(v)
                            else:
                                cleaned[k] = v
                        cleaned_rows.append(cleaned)
                    export_data[table_name] = cleaned_rows
                    total_rows += len(cleaned_rows)
                except Exception:
                    logger.debug("Table %s non disponible pour backup", table_name)
                    export_data[table_name] = []

        backup_payload = {
            "exported_at": datetime.now(UTC).isoformat(),
            "version": "1.0",
            "tables": export_data,
            "total_tables": len(export_data),
            "total_rows": total_rows,
        }

        filepath.write_text(json.dumps(backup_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("D7: Backup JSON créé: %s (%d lignes, %d tables)", filename, total_rows, len(export_data))

        # Envoyer email de confirmation backup
        try:
            taille_octets = filepath.stat().st_size
            if taille_octets >= 1_048_576:
                taille_str = f"{taille_octets / 1_048_576:.1f} Mo"
            else:
                taille_str = f"{taille_octets / 1024:.0f} Ko"

            dispatcher = get_dispatcher_notifications()
            dispatcher.envoyer(
                user_id="admin",
                message=f"Backup hebdomadaire réussi: {filename} ({total_rows} lignes)",
                canaux=["email"],
                type_email="confirmation_backup",
                backup={
                    "date": aujourd_hui.isoformat(),
                    "filename": filename,
                    "total_rows": total_rows,
                    "tables_count": len(export_data),
                    "taille_fichier": taille_str,
                },
            )
        except Exception:
            logger.debug("D7: Email de confirmation backup non envoyé (non bloquant)")

        backups = sorted(backup_dir.glob("backup_*.json"), reverse=True)
        for old_backup in backups[4:]:
            old_backup.unlink()
            logger.info("D7: Ancien backup supprimé: %s", old_backup.name)

    except Exception:
        logger.exception("Erreur job D7 backup auto hebdo JSON")

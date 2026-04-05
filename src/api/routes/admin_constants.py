"""Constantes pour les routes admin."""

from __future__ import annotations

from typing import Any


# ═══════════════════════════════════════════════════════════
# LABELS JOBS
# ═══════════════════════════════════════════════════════════

_LABELS_JOBS: dict[str, str] = {
    "rappels_famille": "Rappels famille quotidiens (07h00)",
    "rappels_maison": "Rappels maison quotidiens (08h00)",
    "rappels_generaux": "Rappels intelligents (08h30)",
    "entretien_saisonnier": "Entretien saisonnier (lun 06h00)",
    "push_quotidien": "Push Web quotidien (09h00)",
    "enrichissement_catalogues": "Enrichissement catalogues IA (1er/mois 03h00)",
    "digest_ntfy": "Digest ntfy.sh (09h00)",
    "digest_notifications_queue": "Flush digest notifications (toutes les 2h)",
    "rappel_courses": "Rappel courses ntfy.sh (18h00)",
    "push_contextuel_soir": "Push contextuel soir (18h00)",
    "resume_hebdo": "Résumé hebdomadaire (lun 07h30)",
    "peremptions_urgentes": "Alerte péremptions urgentes (08h00)",
    "score_bienetre": "Score bien-être Jules (dim 20h00)",
    "planning_semaine_si_vide": "J-03 Vérification planning semaine suivante (dim 20h00)",
    "alertes_peremption_48h": "J-04 Alertes péremption 48h (06h00)",
    "rapport_mensuel_budget": "J-07 Rapport mensuel budget (1er/mois 08h15)",
    "score_weekend": "J-08 Score weekend (ven 17h00)",
    "rapport_jardin": "J-10 Rapport jardin hebdo (mer 20h00)",
    "score_bien_etre_hebdo": "J-11 Score bien-être hebdo (dim 20h00)",
    "sync_calendrier_scolaire": "INNO-14 Sync calendrier scolaire auto (05h30)",
    "garmin_sync_matinal": "Sync Garmin automatique matinale (06h00)",
    "automations_runner": "Exécution automations (toutes les 5 min)",
    "sync_google_calendar": "J1 Sync Google Calendar (quotidien 23h00)",
    "alerte_stock_bas": "J3 Alerte stock bas → liste courses (07h00)",
    "archive_batches_expires": "J4 Archivage préparations batch expirées (02h00)",
    "rapport_maison_mensuel": "J5 Rapport maison mensuel (1er/mois 09h30)",
    "sync_openfoodfacts": "J6 Sync cache OpenFoodFacts (dim 03h00)",
    "prediction_courses_weekly": "JOB-1 Prédiction courses hebdo (dim 10h00)",
    "sync_jeux_budget": "JOB-2 Sync jeux -> budget (22h00)",
    "analyse_nutrition_hebdo": "JOB-3 Analyse nutrition hebdo (dim 20h00)",
    "alertes_energie": "JOB-4 Alertes énergie (07h00)",
    "nettoyage_logs": "JOB-5 Nettoyage logs > 90j (dim 04h00)",
    "check_garmin_anomalies": "JOB-6 Anomalies Garmin (08h00)",
    "resume_jardin_saisonnier": "JOB-7 Résumé jardin saisonnier (1er 08h00)",
    "expiration_documents": "JOB-8 Expiration documents (09h00)",
    "job_expiration_recettes_suggestion": "Ingrédients expirants → suggestion recettes (10h00)",
    "job_stock_prediction_reapprovisionnement": "Prédiction réapprovisionnement inventaire (lun 08h00)",
    "job_variete_repas_alerte": "Alerte variété repas (dim 17h00)",
    "job_tendances_activites_famille": "Tendances activités famille (dim 19h30)",
    "job_energie_peak_detection": "Détection pics énergie (19h00)",
    "job_nutrition_adultes_weekly": "Bilan nutrition adultes Garmin (dim 20h15)",
    "job_briefing_matinal_push": "Briefing matinal IA (07h00)",
    "job_jardin_feedback_planning": "Feedback jardin → planning (dim 18h30)",
    "briefing_matinal_ia": "Résumé matinal IA (07h00)",
    "comparateur_abonnements": "Comparateur abonnements (lun 08h00)",
    "rapport_nutritionnel_jules": "Rapport nutritionnel Jules (dim 19h00)",
    "nettoyage_notifications_30j": "Nettoyage notifications 30 jours (1er/mois 02h30)",
    "prediction_depenses": "Prédiction dépenses (15 du mois 08h30)",
    "alerte_plantes_arrosage": "Alerte plantes / arrosage (08h00)",
    "sync_tirages_euromillions": "Sync tirages Euromillions (mar/ven 22h30)",
    "s16_resume_weekend_telegram": "Résumé weekend suggestions Telegram (ven 18h00)",
    "s16_rappel_entretien_telegram": "Rappel entretien maison Telegram (08h10)",
    "s16_bilan_nutrition_telegram": "Bilan nutrition semaine Telegram (dim 20h30)",
    "s16_rapport_famille_mensuel": "Rapport mensuel famille complet email/PDF (1er 09h00)",
    "s16_rapport_maison_trimestriel": "Rapport trimestriel maison email/PDF (T+1 09h10)",
}

_NOTIFICATION_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "telegram": [
        {"id": "recette_du_jour", "label": "Suggestion recette du jour", "trigger": "CRON 11:30"},
        {"id": "diagnostic_maison", "label": "Alerte diagnostic maison", "trigger": "Événement"},
        {"id": "resume_weekend", "label": "Résumé weekend suggestions", "trigger": "CRON ven 18:00"},
        {"id": "budget_depassement", "label": "Alerte budget dépassement", "trigger": "Événement"},
        {"id": "bilan_nutrition", "label": "Bilan nutrition semaine", "trigger": "CRON dim 20:30"},
        {"id": "rappel_entretien", "label": "Rappel entretien maison", "trigger": "CRON quotidien"},
        {"id": "commande_vocale", "label": "Commande vocale rapide", "trigger": "À la demande"},
    ],
    "email": [
        {"id": "rapport_famille_mensuel_complet", "label": "Rapport mensuel famille complet", "trigger": "Mensuel 1er 09:00"},
        {"id": "rapport_maison_trimestriel", "label": "Rapport trimestriel maison", "trigger": "Trimestriel"},
    ],
}

# Vues SQL explicitement autorisées (lecture seule)
_VUES_SQL_AUTORISEES: tuple[str, ...] = (
    "v_objets_a_remplacer",
    "v_temps_par_activite_30j",
    "v_budget_travaux_par_piece",
    "v_charge_semaine",
)

_NAMESPACE_FEATURE_FLAGS = "admin_feature_flags"
_NAMESPACE_RUNTIME_CONFIG = "admin_runtime_config"

_FEATURE_FLAGS_PAR_DEFAUT: dict[str, bool] = {
    "admin.service_actions_enabled": True,
    "admin.resync_enabled": True,
    "admin.seed_dev_enabled": True,
    "admin.mode_test": False,
    "admin.maintenance_mode": False,
    "jeux.bankroll_page_enabled": True,
    "outils.notes_tags_ui_enabled": True,
}

_RUNTIME_CONFIG_PAR_DEFAUT: dict[str, Any] = {
    "dashboard.refresh_seconds": 300,
    "notifications.digest_interval_minutes": 120,
    "admin.max_jobs_triggers_per_min": 5,
}

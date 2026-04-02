"""Configuration centralisée des planifications CRON.

Ce module isole la matrice de scheduling pour réduire la taille de ``jobs.py``.
"""

from apscheduler.triggers.cron import CronTrigger


def configurer_jobs_planifies(planifier_job) -> None:
    """Enregistre toutes les planifications via le callback fourni."""
    planifier_job("rappels_famille", CronTrigger(hour=7, minute=0))
    planifier_job("rappels_maison", CronTrigger(hour=8, minute=0))
    planifier_job("rappels_generaux", CronTrigger(hour=8, minute=30))
    planifier_job("entretien_saisonnier", CronTrigger(day_of_week="mon", hour=6, minute=0))
    planifier_job("push_quotidien", CronTrigger(hour=9, minute=0))
    planifier_job("enrichissement_catalogues", CronTrigger(day=1, hour=3, minute=0))
    planifier_job("digest_ntfy", CronTrigger(hour=9, minute=0), replace_existing=True)
    planifier_job("digest_whatsapp_matinal", CronTrigger(hour=7, minute=30), replace_existing=True)
    planifier_job("digest_notifications_queue", CronTrigger(hour="*/2", minute=5), replace_existing=True)
    planifier_job("rappel_courses", CronTrigger(hour=18, minute=0), replace_existing=True)
    planifier_job("push_contextuel_soir", CronTrigger(hour=18, minute=0), replace_existing=True)
    planifier_job("resume_hebdo", CronTrigger(day_of_week="mon", hour=7, minute=30), replace_existing=True)
    planifier_job("planning_semaine_si_vide", CronTrigger(day_of_week="sun", hour=19, minute=0), replace_existing=True)
    planifier_job("alertes_peremption_48h", CronTrigger(hour=6, minute=0), replace_existing=True)
    planifier_job("rapport_mensuel_budget", CronTrigger(day=1, hour=8, minute=15), replace_existing=True)
    planifier_job("score_weekend", CronTrigger(day_of_week="fri", hour=17, minute=0), replace_existing=True)
    planifier_job("rapport_jardin", CronTrigger(day_of_week="wed", hour=20, minute=0), replace_existing=True)
    planifier_job("score_bien_etre_hebdo", CronTrigger(day_of_week="sun", hour=20, minute=0), replace_existing=True)
    planifier_job("garmin_sync_matinal", CronTrigger(hour=6, minute=0), replace_existing=True)
    planifier_job("automations_runner", CronTrigger(minute="*/5"), replace_existing=True)
    planifier_job("points_famille_hebdo", CronTrigger(day_of_week="sun", hour=20, minute=0), replace_existing=True)
    planifier_job("sync_google_calendar", CronTrigger(hour=23, minute=0), replace_existing=True)
    planifier_job("sync_veille_habitat", CronTrigger(hour=12, minute=15), replace_existing=True)
    planifier_job("alerte_stock_bas", CronTrigger(hour=7, minute=0), replace_existing=True)
    planifier_job("archive_batches_expires", CronTrigger(hour=2, minute=0), replace_existing=True)
    planifier_job("rapport_maison_mensuel", CronTrigger(day=1, hour=9, minute=30), replace_existing=True)
    planifier_job("sync_openfoodfacts", CronTrigger(day_of_week="sun", hour=3, minute=0), replace_existing=True)

    # Phase 7 — Jobs CRON & notifications
    planifier_job("recap_weekend_dimanche_soir", CronTrigger(day_of_week="sun", hour=20, minute=0), replace_existing=True)
    planifier_job("nettoyage_cache_7j", CronTrigger(hour=2, minute=0), replace_existing=True)
    planifier_job("backup_donnees_critiques", CronTrigger(hour=1, minute=0), replace_existing=True)
    planifier_job("sync_tirages_loto_euromillions", CronTrigger(day_of_week="tue,fri", hour=22, minute=0), replace_existing=True)
    planifier_job("rapport_budget_hebdo", CronTrigger(day_of_week="sun", hour=18, minute=0), replace_existing=True)
    planifier_job("maj_donnees_meteo", CronTrigger(hour=6, minute=0), replace_existing=True)
    planifier_job("anniversaires_j30", CronTrigger(hour=8, minute=0), replace_existing=True)
    planifier_job("analyse_tendances_mensuelles", CronTrigger(day=1, hour=9, minute=0), replace_existing=True)
    planifier_job("purge_logs_anciens_mensuelle", CronTrigger(day=1, hour=3, minute=0), replace_existing=True)
    planifier_job("recette_du_jour_push", CronTrigger(hour=11, minute=30), replace_existing=True)
    planifier_job("stock_critique_zero", CronTrigger(hour="*/3", minute=0), replace_existing=True)
    planifier_job("resultat_tirage_loto", CronTrigger(day_of_week="tue,fri", hour=22, minute=15), replace_existing=True)
    planifier_job("nouvelle_recette_saison", CronTrigger(day=1, hour=11, minute=0), replace_existing=True)
    planifier_job("tache_jardin_saisonniere", CronTrigger(month="3,6,9,12", day=1, hour=6, minute=0), replace_existing=True)
    planifier_job("astuce_anti_gaspillage", CronTrigger(hour=12, minute=0), replace_existing=True)

    # Jobs existants conservés
    planifier_job("prediction_courses_weekly", CronTrigger(day_of_week="fri", hour=16, minute=0), replace_existing=True)
    planifier_job("sync_jeux_budget", CronTrigger(hour=22, minute=0), replace_existing=True)
    planifier_job("analyse_nutrition_hebdo", CronTrigger(day_of_week="sun", hour=20, minute=0), replace_existing=True)
    planifier_job("alertes_energie", CronTrigger(hour=7, minute=0), replace_existing=True)
    planifier_job("nettoyage_logs", CronTrigger(day_of_week="sun", hour=4, minute=0), replace_existing=True)
    planifier_job("check_garmin_anomalies", CronTrigger(hour=8, minute=0), replace_existing=True)
    planifier_job("resume_jardin_saisonnier", CronTrigger(day=1, hour=8, minute=0), replace_existing=True)
    planifier_job("expiration_documents", CronTrigger(hour=9, minute=0), replace_existing=True)
    planifier_job("sync_calendrier_scolaire", CronTrigger(hour=5, minute=30), replace_existing=True)
    planifier_job("sync_routines_planning", CronTrigger(hour=5, minute=45), replace_existing=True)
    planifier_job("sync_recoltes_inventaire", CronTrigger(hour=6, minute=15), replace_existing=True)
    planifier_job("suggestions_activites_meteo", CronTrigger(hour=7, minute=15), replace_existing=True)

    # Phase 8 — Jobs CRON additionnels
    planifier_job("rappel_documents_expirants", CronTrigger(hour=8, minute=0), replace_existing=True)
    planifier_job("rapport_mensuel_auto", CronTrigger(day=1, hour=8, minute=0), replace_existing=True)
    planifier_job("bilan_energetique", CronTrigger(day=1, hour=8, minute=30), replace_existing=True)
    planifier_job("rappel_vaccins", CronTrigger(day_of_week="mon", hour=9, minute=0), replace_existing=True)
    planifier_job("sync_entretien_budget", CronTrigger(day=1, hour=6, minute=0), replace_existing=True)
    planifier_job("sync_voyages_calendrier", CronTrigger(hour=6, minute=30), replace_existing=True)
    planifier_job("sync_charges_dashboard", CronTrigger(hour=7, minute=30), replace_existing=True)

    # Phase 10 — Jobs CRON Innovations
    planifier_job("optimisation_routines", CronTrigger(day=15, hour=10, minute=0), replace_existing=True)
    planifier_job("suggestions_saison", CronTrigger(day=1, hour=9, minute=0), replace_existing=True)
    planifier_job("purge_historique_jeux", CronTrigger(day=1, hour=3, minute=30), replace_existing=True)
    planifier_job("veille_emploi", CronTrigger(hour=7, minute=0), replace_existing=True)

    # Nouveaux jobs
    planifier_job("alertes_budget_seuil", CronTrigger(hour=20, minute=0), replace_existing=True)
    planifier_job("resume_hebdo_ia", CronTrigger(day_of_week="sun", hour=20, minute=30), replace_existing=True)

    # Nouveaux jobs
    planifier_job("rappels_jardin_saisonniers", CronTrigger(day_of_week="mon", hour=7, minute=0), replace_existing=True)
    planifier_job("verification_sante_systeme", CronTrigger(minute=0), replace_existing=True)
    planifier_job("backup_auto_hebdo_json", CronTrigger(day_of_week="sun", hour=4, minute=0), replace_existing=True)

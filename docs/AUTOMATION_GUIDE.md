# Automation Guide

> Référence pratique des automatisations planifiées et des règles Si->Alors.

---

## Deux mécanismes à distinguer

### 1. Jobs planifiés APScheduler

Ils sont déclarés dans :

- `src/services/core/cron/jobs_schedule.py` pour la matrice horaire
- `src/services/core/cron/jobs.py` pour le registre, l'exécution tracée et les effets métier

La matrice centrale contient actuellement 89 planifications explicites.

### 2. Automations métier Si->Alors

Elles sont exposées via :

- `src/api/routes/automations.py`
- `src/services/utilitaires/automations_engine.py`

Le job `automations_runner` les évalue toutes les 5 minutes.

---

## Inventaire rapide des familles de jobs

| Famille | Exemples | Fréquence typique |
| --- | --- | --- |
| Rappels quotidiens | `rappels_famille`, `rappels_maison`, `rappels_generaux` | quotidien matin |
| Notifications et digests | `digest_ntfy`, `digest_telegram_matinal`, `push_contextuel_soir`, `recette_du_jour_push` | quotidien / intra-journée |
| Planning et synchronisations | `planning_semaine_si_vide`, `sync_google_calendar`, `sync_routines_planning`, `sync_voyages_calendrier` | quotidien / hebdomadaire |
| Inventaire et courses | `alertes_peremption_48h`, `alerte_stock_bas`, `archive_batches_expires`, `prediction_courses_weekly` | quotidien / hebdomadaire |
| Rapports | `rapport_mensuel_budget`, `rapport_maison_mensuel`, `s16_rapport_famille_mensuel`, `s21_rapport_mensuel_unifie_email` | hebdomadaire / mensuel / trimestriel |
| IA et enrichissement | `enrichissement_catalogues`, `analyse_nutrition_hebdo`, `health_check_services_ia`, `resume_hebdo_ia` | quotidien à mensuel |
| Jardin, énergie, maison | `rapport_jardin`, `alertes_energie`, `tache_jardin_saisonniere`, `sync_veille_habitat` | quotidien / saisonnier |
| Jeux et résultats | `sync_tirages_loto_euromillions`, `sync_resultats_paris_auto`, `resultat_tirage_loto` | intra-journée / tirages |
| Maintenance | `nettoyage_cache_7j`, `purge_logs_anciens_mensuelle`, `backup_auto_hebdo_json`, `verification_sante_systeme` | horaire / quotidien / mensuel |

Pour la liste exhaustive des IDs, voir `docs/CRON_JOBS.md` et `lister_jobs_disponibles()`.

---

## Configuration

### Démarrage

Le scheduler est démarré dans le cycle de vie FastAPI via `demarrer_scheduler()` puis arrêté proprement à l'extinction.

### Fuseau et comportement

- fuseau cible : `Europe/Paris`
- `coalesce=True` pour fusionner les exécutions manquées
- `max_instances=1` pour éviter les doubles exécutions d'un même job

### Variables utiles

- `CRON_DEFAULT_USER_IDS`
- `ADMIN_USER_IDS`
- `ENVIRONMENT`

---

## Suivi et monitoring

### Historique d'exécution

Chaque exécution peut être tracée dans `job_executions` avec :

- `job_id`, `job_name`
- `started_at`, `ended_at`, `duration_ms`
- `status` (`running`, `success`, `failure`, `dry_run`)
- `error_message`, `output_logs`
- `triggered_by_user_id`, `triggered_by_user_role`

### Admin API

Les endpoints admin les plus utiles pour l'exploitation :

- `GET /api/v1/admin/jobs`
- `POST /api/v1/admin/jobs/{job_id}/run`
- `POST /api/v1/admin/jobs/run-all`
- `PUT /api/v1/admin/jobs/{job_id}/schedule`
- `POST /api/v1/admin/jobs/run-morning-batch`
- `POST /api/v1/admin/jobs/simulate-day`
- `GET /api/v1/admin/cockpit`

### Alertes d'échec

`_notifier_echec_job_admin()` envoie une alerte aux admins lorsqu'un job échoue.

---

## Retry, diagnostic et exécution manuelle

Le coeur d'exécution passe par `_executer_job_trace()` dans `src/services/core/cron/jobs.py`.

Effets utiles :

- création d'un historique exploitable
- support `dry_run`
- capture des erreurs et durées
- notification admin en cas d'échec

Workflow recommandé :

1. lister le job cible
2. lancer un `dry_run`
3. vérifier le résultat et l'impact attendu
4. exécuter en réel si le diagnostic est concluant
5. vérifier `job_executions` et les logs admin

---

## Automations Si->Alors

Le moteur `automations_runner` évalue périodiquement les règles actives stockées en base.

Déclencheurs actuellement documentés dans `docs/AUTOMATIONS.md` :

- stock bas
- péremption proche
- dépassement budget
- alerte météo
- anniversaire proche
- tâche en retard
- inactivité Garmin
- expiration de document
- recette sans photo

Actions supportées :

- ajouter à une liste de courses
- suggérer une recette
- créer une tâche maison
- ajouter au planning
- notifier
- archiver
- générer un rapport PDF

---

## Bonnes pratiques

- ne pas ajouter un job sans l'enregistrer à la fois dans le registre et dans la matrice de planification
- préférer des jobs idempotents
- réserver les notifications multi-canaux aux cas utiles pour limiter le bruit
- documenter tout nouveau job dans `docs/CRON_JOBS.md` et, si pertinent, dans ce guide
- utiliser les endpoints admin pour les diagnostics plutôt que des manipulations ad hoc en production

# Cron Jobs

> Référence des tâches planifiées APScheduler, de leur utilité et des procédures de diagnostic.

---

## Démarrage

Le scheduler est démarré depuis le cycle de vie FastAPI:

- bootstrap: `src/api/main.py`
- configuration: `src/services/core/cron/jobs.py`
- helpers package: `src/services/core/cron/__init__.py`

Le fuseau horaire utilisé par le scheduler principal est `Europe/Paris`.

---

## Jobs principaux

| ID | Horaire | Objet | Notes |
|----|---------|-------|-------|
| `rappels_famille` | Quotidien 07:00 | Rappels anniversaires, documents, crèche, jalons | WhatsApp si au moins un rappel |
| `rappels_maison` | Quotidien 08:00 | Garanties, contrats, entretien | Service maison |
| `rappels_generaux` | Quotidien 08:30 | Rappels intelligents + repas du soir | ntfy + push |
| `entretien_saisonnier` | Lundi 06:00 | Vérification entretien saisonnier | Maison |
| `push_quotidien` | Quotidien 09:00 | Push urgents | charge les abonnés DB en priorité |
| `digest_whatsapp_matinal` | Quotidien 07:30 | Digest WhatsApp matinal | repas du jour, tâches, péremptions + boutons interactifs |
| `digest_ntfy` | Quotidien 09:00 | Digest ntfy | résumé quotidien |
| `rappel_courses` | Quotidien 18:00 | Rappel liste de courses | WhatsApp |
| `push_contextuel_soir` | Quotidien 18:00 | Préparation du lendemain | ntfy + push |
| `resume_hebdo` | Lundi 07:30 | Résumé hebdo | ntfy, email, whatsapp |
| `planning_semaine_si_vide` | Dimanche 20:00 | Vérifier planning semaine suivante | rappel si vide |
| `alertes_peremption_48h` | Quotidien 06:00 | Produits à péremption proche | email critique si besoin |
| `rapport_mensuel_budget` | Le 1er 08:15 | Rapport budget | multi-canal |
| `score_weekend` | Vendredi 17:00 | Score et contexte weekend | ntfy + whatsapp |
| `controle_contrats_garanties` | Le 1er 09:00 | Contrats et garanties | email si critique |
| `rapport_jardin` | Mercredi 20:00 | Rapport jardin | ntfy + whatsapp |
| `score_bien_etre_hebdo` | Dimanche 20:00 | Score bien-être | priorité variable |
| `garmin_sync_matinal` | Quotidien 06:00 | Synchronisation Garmin | profils connectés uniquement |
| `automations_runner` | Toutes les 5 min | Exécution des règles Si→Alors | moteur simple actuel |
| `points_famille_hebdo` | Dimanche 20:00 | Calcul points famille | gamification |
| `sync_google_calendar` | Quotidien 23:00 | Planning -> Google Calendar | J1 |
| `alerte_stock_bas` | Quotidien 07:00 | Stock bas -> liste courses | J3 |
| `archive_batches_expires` | Quotidien 02:00 | Archivage batch expiré | J4 |
| `rapport_maison_mensuel` | Le 1er 09:30 | Synthèse maison | J5 |
| `sync_openfoodfacts` | Dimanche 03:00 | Refresh cache OpenFoodFacts | J6 |

---

## Détail par famille

### Rappels et notifications

- `rappels_famille`
- `rappels_maison`
- `rappels_generaux`
- `push_quotidien`
- `digest_ntfy`
- `push_contextuel_soir`

### Planification, santé, budget

- `resume_hebdo`
- `planning_semaine_si_vide`
- `rapport_mensuel_budget`
- `score_weekend`
- `score_bien_etre_hebdo`
- `garmin_sync_matinal`
- `points_famille_hebdo`
- `sync_google_calendar`

### Cuisine et inventaire

- `rappel_courses`
- `alertes_peremption_48h`
- `alerte_stock_bas`
- `archive_batches_expires`
- `sync_openfoodfacts`

### Maison et automatisations

- `entretien_saisonnier`
- `controle_contrats_garanties`
- `rapport_jardin`
- `rapport_maison_mensuel`
- `automations_runner`

---

## Particularités importantes

### Multi-utilisateur

Les notifications déclenchées par les jobs principaux passent désormais par:

- `_obtenir_user_ids_actifs()`
- `_envoyer_notif_tous_users()`

Effet:

- les jobs ne sont plus limités à l'identifiant hardcodé historique
- fallback possible via `CRON_DEFAULT_USER_IDS` si la base n'est pas disponible

### Déclenchement manuel depuis l'admin

Routes disponibles:

- `GET /api/v1/admin/jobs`
- `POST /api/v1/admin/jobs/{job_id}/run`
- `GET /api/v1/admin/jobs/{job_id}/logs`

### Historique actuel

L'historique des exécutions manuelles est conservé en mémoire de processus seulement. Il n'existe pas encore de table `job_executions` persistante.

---

## Dépannage rapide

### Aucun job visible dans l'admin

- vérifier que l'API a démarré sans erreur
- vérifier le lancement du scheduler dans `src/api/main.py`
- vérifier que `DémarreurCron` a bien été initialisé

### Un job ne fait rien

- lancer le job manuellement depuis l'admin
- vérifier si les préconditions métier sont remplies
- regarder les logs applicatifs backend

### Les notifications de job ne partent pas

- vérifier les abonnements push et la configuration des canaux
- vérifier le dispatcher de notifications
- vérifier la récupération des utilisateurs actifs si le job diffuse à tous les comptes

### Un job lié à Google Calendar échoue

- vérifier les calendriers externes actifs en base
- vérifier les credentials et refresh tokens Google
- vérifier que le fournisseur vaut bien `google`

### Un job Garmin ne synchronise rien

- vérifier que des profils ont `garmin_connected = true`
- vérifier les credentials OAuth Garmin
- vérifier les logs de sync par profil

---

## Gaps connus

- pas de retry riche ni backoff centralisé par job
- pas de notification d'échec admin systématique
- pas de métriques persistantes de durée
- pas d'historique persistant des exécutions

Ces points sont déjà identifiés dans le planning pour la phase jobs et automatisations.
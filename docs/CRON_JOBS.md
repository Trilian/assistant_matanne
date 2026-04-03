# Cron Jobs

> Référence complète des 68 tâches planifiées APScheduler — horaires, canaux, dépendances et procédures de diagnostic.
>
> **Dernière mise à jour** : 1er avril 2026

---

## Démarrage

Le scheduler est démarré depuis le cycle de vie FastAPI :

- **Bootstrap** : `src/api/main.py` (lifespan context)
- **Configuration** : `src/services/core/cron/jobs.py` → `_configurer_jobs()`
- **Helpers** : `src/services/core/cron/__init__.py`
- **Classe** : `DémarreurCron` (APScheduler `BackgroundScheduler`)

**Fuseau horaire** : `Europe/Paris`

**Configuration APScheduler** :

```python
BackgroundScheduler(
    job_defaults={"coalesce": True, "max_instances": 1},
    timezone="Europe/Paris",
)
```

- `coalesce=True` : si un job a été raté (downtime), il ne s'exécute qu'une seule fois au redémarrage
- `max_instances=1` : jamais d'exécution parallèle d'un même job

---

## Inventaire complet — 68 jobs

### Rappels et notifications quotidiennes (12 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `rappels_famille` | Quotidien 07:00 | Rappels anniversaires, documents, crèche, jalons | Telegram |
| `rappels_maison` | Quotidien 08:00 | Entretien maison | Service interne |
| `rappels_generaux` | Quotidien 08:30 | Rappels intelligents : stock bas | ntfy + push |
| `push_quotidien` | Quotidien 09:00 | Push Web urgents (VAPID) | push |
| `digest_ntfy` | Quotidien 09:00 | Digest quotidien ntfy.sh (tâches + rappels) | ntfy |
| `digest_Telegram_matinal` | Quotidien 07:30 | Digest matinal (repas, tâches, péremptions) | Telegram |
| `digest_notifications_queue` | Toutes les 2h à :05 | Flush file d'attente digest (notifications throttlées) | Multi-canal |
| `rappel_courses` | Quotidien 18:00 | Rappel articles en attente dans la liste de courses | ntfy + Telegram |
| `push_contextuel_soir` | Quotidien 18:00 | Préparation du lendemain (planning + météo) | push + ntfy |
| `anniversaires_j30` | Quotidien 08:00 | Anniversaires dans les 30 prochains jours | push + Telegram |
| `recette_du_jour_push` | Quotidien 11:30 | Recette du jour (si planning actif) | push |
| `resultat_tirage_loto` | Mar/Ven après 22:15 | Notification résultats tirage | push + Telegram |

### Résumés hebdomadaires (6 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `resume_hebdo` | Lundi 07:30 | Résumé hebdomadaire agrégé | ntfy + email + Telegram |
| `resume_hebdo_ia` | Dimanche 20:30 | Résumé narratif IA de la semaine | Telegram + email |
| `score_weekend` | Vendredi 17:00 | Score weekend (activités + météo + contexte Jules) | ntfy + Telegram |
| `score_bien_etre_hebdo` | Dimanche 20:00 | Score bien-être hebdomadaire | ntfy + Telegram (si alerte) |
| `rapport_jardin` | Mercredi 20:00 | Rapport jardin (arrosage + récoltes/plantations) | ntfy + Telegram |
| `rapport_budget_hebdo` | Dimanche 18:00 | Résumé budget hebdomadaire | Telegram |

### Rapports mensuels et analyses (9 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `rapport_mensuel_budget` | Le 1er à 08:15 | Rapport budget mensuel (famille + maison + jeux) | ntfy + email + Telegram |
| `rapport_mensuel_auto` | Le 1er à 08:00 | Rapport mensuel consolidé automatique | ntfy + email + Telegram |
| `rapport_maison_mensuel` | Le 1er à 09:30 | Synthèse maison (projets actifs, entretien 30j, dépenses) | ntfy + email |
| `bilan_energetique` | Le 1er à 08:30 | Bilan énergie mensuel (conso, comparaison N-1) | ntfy + email |
| `analyse_tendances_mensuelles` | Le 1er à 09:00 | Analyse tendances mensuelles | email |
| `resume_jardin_saisonnier` | Le 1er à 08:00 | Résumé jardin mensuel + recommandations | ntfy + email |
| `optimisation_routines` | Le 15 à 10:00 | Analyse efficacité routines via IA | Service interne |

### Inventaire et péremptions (6 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `alertes_peremption_48h` | Quotidien 06:00 | Alertes péremption 48h (email si <24h critique) | ntfy + Telegram + email (si urgent) |
| `alerte_stock_bas` | Quotidien 07:00 | Stock bas : ajout auto à la liste de courses | ntfy |
| `stock_critique_zero` | Toutes les 3h à :00 | Alerte stock critique (quantité ≤ 0) | push + ntfy + Telegram |
| `astuce_anti_gaspillage` | Quotidien 12:00 | Astuce anti-gaspillage si 3+ articles proches péremption | push |
| `archive_batches_expires` | Quotidien 02:00 | Archivage préparations batch cooking expirées | Service interne |
| `sync_openfoodfacts` | Dimanche 03:00 | Refresh cache OpenFoodFacts (articles scannés, 30j) | Service interne |

### Planning et programmation (5 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `planning_semaine_si_vide` | Dimanche 19:00 | J-3 : vérifie planning, propose menu IA si vide | Telegram + push |
| `sync_google_calendar` | Quotidien 23:00 | Sync planning repas + activités → Google Calendar | Service interne |
| `sync_routines_planning` | Quotidien 05:45 | Sync routines actives dans planning quotidien | Service interne |
| `sync_calendrier_scolaire` | Quotidien 05:30 | Resync calendriers scolaires actifs | Service interne |
| `sync_voyages_calendrier` | Quotidien 06:30 | Sync voyages planifiés vers événements calendrier | Service interne |

### Intégrations et synchronisations (9 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `garmin_sync_matinal` | Quotidien 06:00 | Sync données Garmin (profils connectés, lookback 2j) | Service interne |
| `sync_jeux_budget` | Quotidien 22:00 | Sync gains/pertes jeux → budget famille | Service interne |
| `sync_recoltes_inventaire` | Quotidien 06:15 | Auto-sync récoltes jardin → inventaire cuisine | Service interne |
| `suggestions_activites_meteo` | Quotidien 07:15 | Suggestions activités selon prévisions météo | ntfy + push |
| `sync_veille_habitat` | Quotidien 12:15 | Sync alertes emploi habitat + push meilleurs résultats | Service interne |
| `sync_contrats_alertes` | Lundi 09:00 | Sync contrats + alertes hebdo (horizon 60j) | ntfy + push |
| `sync_charges_dashboard` | Quotidien 07:30 | Sync charges fixes vers métriques dashboard | Service interne |
| `sync_entretien_budget` | Le 1er à 06:00 | Sync coûts entretien mois précédent → dépenses | Service interne |
| `sync_tirages_loto_euromillions` | Mar/Ven 22:00 | Sync tirages Loto/EuroMillions | push |

### IA et analyses (5 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `prediction_courses_weekly` | Dimanche 10:00 | Pré-remplissage liste courses depuis historique | ntfy + push |
| `analyse_nutrition_hebdo` | Dimanche 20:00 | Analyse nutritionnelle simple sur repas planifiés | ntfy + email |
| `recap_weekend_dimanche_soir` | Dimanche 20:00 | Récap weekend dimanche soir | Telegram + push |
| `suggestions_saison` | Le 1er à 09:00 | Mise en avant produits de saison du mois | ntfy |
| `nouvelle_recette_saison` | Le 1er à 11:00 | Push recette saisonnière du mois | push |

### Maintenance et nettoyage (7 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `entretien_saisonnier` | Lundi 06:00 | Vérification tâches entretien saisonnières | Service interne |
| `enrichissement_catalogues` | Le 1er à 03:00 | Enrichissement IA des catalogues de référence | Service interne |
| `nettoyage_cache_7j` | Quotidien 02:00 | Purge cache applicatif | Service interne |
| `backup_donnees_critiques` | Quotidien 01:00 | Snapshot JSON des tables critiques | Service interne |
| `nettoyage_logs` | Dimanche 04:00 | Purge logs audit/sécurité > 90 jours | Service interne |
| `purge_logs_anciens_mensuelle` | Le 1er à 03:00 | Purge mensuelle logs anciens | Service interne |
| `purge_historique_jeux` | Le 1er à 03:30 | Archivage paris sportifs > 12 mois | Service interne |

### Santé et bien-être (3 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `rappel_vaccins` | Lundi 09:00 | Rappels vaccins (horizon 30j + retards) | push + ntfy + Telegram |
| `rappel_documents_expirants` | Quotidien 08:00 | Rappels documents famille expirants (urgence graduée) | push + ntfy + email |
| `check_garmin_anomalies` | Quotidien 08:00 | Alerte si inactivité Garmin > 3 jours | ntfy + push |

### Automatisations (1 job)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `automations_runner` | Toutes les 5 min | Exécution règles Si→Alors actives | Service interne |

### Gamification et performance (2 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `points_famille_hebdo` | Dimanche 20:00 | Calcul points famille + déblocage badges | push (badges) |
| `maj_donnees_meteo` | Quotidien 06:00 | Préchargement données météo 7 jours | Service interne |

### Énergie et jardin (2 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `alertes_energie` | Quotidien 07:00 | Détection anomalies énergie (vs moyenne historique) | ntfy + push + email |
| `tache_jardin_saisonniere` | Trimestriel (Mar/Jun/Sep/Dec) 06:00 | Rappels tâches jardin saisonnières | push + ntfy |

### Veille et budget (2 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `veille_emploi` | Quotidien 07:00 | Veille marché emploi quotidienne (multi-sites) | Service interne |
| `alertes_budget_seuil` | Quotidien 20:00 | Alerte si catégorie > 80% du budget mensuel | Service interne |

---

## Registre des jobs

Tous les jobs sont enregistrés dans le dictionnaire `_REGISTRE_JOBS` :

- **Clé** : identifiant du job (str)
- **Valeur** : tuple (nom affiché, fonction)

Le registre est construit de manière incrémentale :

1. Jobs initiaux (28 jobs de base)
2. Jobs cron supplémentaires
3. Jobs notifications, contrats et documents
4. Jobs innovations, gamification et automations
5. Jobs IA avancée et résumés narratifs

Fonctions de gestion :

- `lister_jobs_disponibles()` → liste triée de tous les IDs exécutables
- `executer_job_par_id(job_id, dry_run=False)` → exécution par ID avec support dry-run

---

## Multi-utilisateur

Les notifications déclenchées par les jobs passent par :

- `_obtenir_user_ids_actifs()` — récupère les IDs utilisateurs actifs depuis la base
- `_envoyer_notif_tous_users()` — diffuse la notification à tous les utilisateurs actifs

Fallback : variable `CRON_DEFAULT_USER_IDS` (CSV) si la base n'est pas disponible.

---

## Variables d'environnement

| Variable | Usage | Défaut |
| ---------- | ------- | -------- |
| `CRON_DEFAULT_USER_IDS` | IDs utilisateurs fallback (CSV) | `"matanne"` |
| `ADMIN_USER_IDS` | IDs admin pour alertes d'échec (CSV) | Premier utilisateur actif |
| `ENVIRONMENT` | Mode dev/prod (affecte logging) | `"production"` |

---

## Déclenchement manuel depuis l'admin

Routes disponibles :

```http
GET    /api/v1/admin/jobs              # Liste de tous les jobs
POST   /api/v1/admin/jobs/{job_id}/run # Exécution manuelle (dry_run optionnel)
GET    /api/v1/admin/jobs/{job_id}/logs # Historique des 50 dernières exécutions
GET    /api/v1/admin/jobs/history      # Historique paginé avec filtres
```

---

## Historique d'exécution

L'historique est persisté dans la table `job_executions` (consolidée dans `sql/schema/03_systeme.sql`).

Colonnes : `id`, `job_id`, `job_name`, `started_at`, `ended_at`, `duration_ms`, `status` (`running`/`success`/`failure`/`dry_run`), `error_message`, `output_logs`, `triggered_by_user_id`, `triggered_by_user_role` (`admin`/`system`), `created_at`, `modified_at`.

Fonctions internes :

- `_creer_execution_job(job_id, source)` — crée un enregistrement au démarrage
- `_finaliser_execution_job(execution_id, status, error_message)` — met à jour en fin d'exécution
- `_executer_job_trace()` — exécute le job avec tracing complet, métriques et gestion d'erreurs
- `_notifier_echec_job_admin()` — notifie les admins en cas d'échec (push + email)

---

## Dépannage rapide

### Aucun job visible dans l'admin

- Vérifier que l'API a démarré sans erreur
- Vérifier le lancement du scheduler dans `src/api/main.py`
- Vérifier que `DémarreurCron` a bien été initialisé
- Contrôler le mapping `_LABELS_JOBS` dans `src/api/routes/admin.py`

### Un job ne fait rien

- Lancer le job manuellement depuis l'admin (`POST .../run`)
- Vérifier les préconditions métier (utilisateurs actifs, données en base)
- Regarder les logs applicatifs backend

### Les notifications de job ne partent pas

- Vérifier les abonnements push et la configuration des canaux
- Vérifier le dispatcher de notifications (`notif_dispatcher.py`)
- Vérifier la récupération des utilisateurs actifs

### Un job Google Calendar échoue

- Vérifier les calendriers externes actifs en base
- Vérifier les credentials et refresh tokens Google
- Vérifier que le fournisseur vaut bien `google`

### Un job Garmin ne synchronise rien

- Vérifier que des profils ont `garmin_connected = true`
- Vérifier les credentials OAuth Garmin
- Vérifier les logs de sync par profil

---

## Limitations connues

- Pas de retry riche ni backoff centralisé par job
- Notification d'échec admin partielle (via `_notifier_echec_job_admin()`, pas systématique)

Ces points sont identifiés dans le planning pour amélioration future.


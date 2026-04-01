# Cron Jobs

> R?f?rence compl?te des 68 t?ches planifi?es APScheduler ? horaires, canaux, d?pendances et proc?dures de diagnostic.
>
> **Derni?re mise ? jour** : 1er avril 2026

---

## D?marrage

Le scheduler est d?marr? depuis le cycle de vie FastAPI :

- **Bootstrap** : `src/api/main.py` (lifespan context)
- **Configuration** : `src/services/core/cron/jobs.py` ? `_configurer_jobs()`
- **Helpers** : `src/services/core/cron/__init__.py`
- **Classe** : `D?marreurCron` (APScheduler `BackgroundScheduler`)

**Fuseau horaire** : `Europe/Paris`

**Configuration APScheduler** :

```python
BackgroundScheduler(
    job_defaults={"coalesce": True, "max_instances": 1},
    timezone="Europe/Paris",
)
```

- `coalesce=True` : si un job a ?t? rat? (downtime), il ne s'ex?cute qu'une seule fois au red?marrage
- `max_instances=1` : jamais d'ex?cution parall?le d'un m?me job

---

## Inventaire complet ? 68 jobs

### Rappels et notifications quotidiennes (12 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `rappels_famille` | Quotidien 07:00 | Rappels anniversaires, documents, cr?che, jalons | WhatsApp |
| `rappels_maison` | Quotidien 08:00 | Garanties, contrats, entretien | Service interne |
| `rappels_generaux` | Quotidien 08:30 | Rappels intelligents : stock bas, garanties | ntfy + push |
| `push_quotidien` | Quotidien 09:00 | Push Web urgents (VAPID) | push |
| `digest_ntfy` | Quotidien 09:00 | Digest quotidien ntfy.sh (t?ches + rappels) | ntfy |
| `digest_whatsapp_matinal` | Quotidien 07:30 | Digest matinal (repas, t?ches, p?remptions) | WhatsApp |
| `digest_notifications_queue` | Toutes les 2h ? :05 | Flush file d'attente digest (notifications throttl?es) | Multi-canal |
| `rappel_courses` | Quotidien 18:00 | Rappel articles en attente dans la liste de courses | ntfy + WhatsApp |
| `push_contextuel_soir` | Quotidien 18:00 | Pr?paration du lendemain (planning + m?t?o) | push + ntfy |
| `anniversaires_j30` | Quotidien 08:00 | Anniversaires dans les 30 prochains jours | push + WhatsApp |
| `recette_du_jour_push` | Quotidien 11:30 | Recette du jour (si planning actif) | push |
| `resultat_tirage_loto` | Mar/Ven apr?s 22:15 | Notification r?sultats tirage | push + WhatsApp |

### R?sum?s hebdomadaires (6 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `resume_hebdo` | Lundi 07:30 | R?sum? hebdomadaire agr?g? | ntfy + email + WhatsApp |
| `resume_hebdo_ia` | Dimanche 20:30 | R?sum? narratif IA de la semaine | WhatsApp + email |
| `score_weekend` | Vendredi 17:00 | Score weekend (activit?s + m?t?o + contexte Jules) | ntfy + WhatsApp |
| `score_bien_etre_hebdo` | Dimanche 20:00 | Score bien-?tre hebdomadaire | ntfy + WhatsApp (si alerte) |
| `rapport_jardin` | Mercredi 20:00 | Rapport jardin (arrosage + r?coltes/plantations) | ntfy + WhatsApp |
| `rapport_budget_hebdo` | Dimanche 18:00 | R?sum? budget hebdomadaire | WhatsApp |

### Rapports mensuels et analyses (9 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `rapport_mensuel_budget` | Le 1er ? 08:15 | Rapport budget mensuel (famille + maison + jeux) | ntfy + email + WhatsApp |
| `rapport_mensuel_auto` | Le 1er ? 08:00 | Rapport mensuel consolid? automatique | ntfy + email + WhatsApp |
| `rapport_maison_mensuel` | Le 1er ? 09:30 | Synth?se maison (projets actifs, entretien 30j, d?penses) | ntfy + email |
| `controle_contrats_garanties` | Le 1er ? 09:00 | Contr?le contrats/garanties (horizon 3 mois) | ntfy + WhatsApp + email (si urgent) |
| `check_garanties_expirant` | Lundi 09:15 | Garanties expirant sous 60 jours | ntfy + email (si <14j) |
| `bilan_energetique` | Le 1er ? 08:30 | Bilan ?nergie mensuel (conso, comparaison N-1) | ntfy + email |
| `analyse_tendances_mensuelles` | Le 1er ? 09:00 | Analyse tendances mensuelles | email |
| `resume_jardin_saisonnier` | Le 1er ? 08:00 | R?sum? jardin mensuel + recommandations | ntfy + email |
| `optimisation_routines` | Le 15 ? 10:00 | Analyse efficacit? routines via IA | Service interne |

### Inventaire et p?remptions (6 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `alertes_peremption_48h` | Quotidien 06:00 | Alertes p?remption 48h (email si <24h critique) | ntfy + WhatsApp + email (si urgent) |
| `alerte_stock_bas` | Quotidien 07:00 | Stock bas : ajout auto ? la liste de courses | ntfy |
| `stock_critique_zero` | Toutes les 3h ? :00 | Alerte stock critique (quantit? = 0) | push + ntfy + WhatsApp |
| `astuce_anti_gaspillage` | Quotidien 12:00 | Astuce anti-gaspillage si 3+ articles proches p?remption | push |
| `archive_batches_expires` | Quotidien 02:00 | Archivage pr?parations batch cooking expir?es | Service interne |
| `sync_openfoodfacts` | Dimanche 03:00 | Refresh cache OpenFoodFacts (articles scann?s, 30j) | Service interne |

### Planning et programmation (5 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `planning_semaine_si_vide` | Dimanche 19:00 | J-3 : v?rifie planning, propose menu IA si vide | WhatsApp + push |
| `sync_google_calendar` | Quotidien 23:00 | Sync planning repas + activit?s ? Google Calendar | Service interne |
| `sync_routines_planning` | Quotidien 05:45 | Sync routines actives dans planning quotidien | Service interne |
| `sync_calendrier_scolaire` | Quotidien 05:30 | Resync calendriers scolaires actifs | Service interne |
| `sync_voyages_calendrier` | Quotidien 06:30 | Sync voyages planifi?s vers ?v?nements calendrier | Service interne |

### Int?grations et synchronisations (9 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `garmin_sync_matinal` | Quotidien 06:00 | Sync donn?es Garmin (profils connect?s, lookback 2j) | Service interne |
| `sync_jeux_budget` | Quotidien 22:00 | Sync gains/pertes jeux ? budget famille | Service interne |
| `sync_recoltes_inventaire` | Quotidien 06:15 | Auto-sync r?coltes jardin ? inventaire cuisine | Service interne |
| `suggestions_activites_meteo` | Quotidien 07:15 | Suggestions activit?s selon pr?visions m?t?o | ntfy + push |
| `sync_veille_habitat` | Quotidien 12:15 | Sync alertes emploi habitat + push meilleurs r?sultats | Service interne |
| `sync_contrats_alertes` | Lundi 09:00 | Sync contrats + alertes hebdo (horizon 60j) | ntfy + push |
| `sync_charges_dashboard` | Quotidien 07:30 | Sync charges fixes vers m?triques dashboard | Service interne |
| `sync_entretien_budget` | Le 1er ? 06:00 | Sync co?ts entretien mois pr?c?dent ? d?penses | Service interne |
| `sync_tirages_loto_euromillions` | Mar/Ven 22:00 | Sync tirages Loto/EuroMillions | push |

### IA et analyses (5 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `prediction_courses_weekly` | Dimanche 10:00 | Pr?-remplissage liste courses depuis historique | ntfy + push |
| `analyse_nutrition_hebdo` | Dimanche 20:00 | Analyse nutritionnelle simple sur repas planifi?s | ntfy + email |
| `recap_weekend_dimanche_soir` | Dimanche 20:00 | R?cap weekend dimanche soir | WhatsApp + push |
| `suggestions_saison` | Le 1er ? 09:00 | Mise en avant produits de saison du mois | ntfy |
| `nouvelle_recette_saison` | Le 1er ? 11:00 | Push recette saisonni?re du mois | push |

### Maintenance et nettoyage (7 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `entretien_saisonnier` | Lundi 06:00 | V?rification t?ches entretien saisonni?res | Service interne |
| `enrichissement_catalogues` | Le 1er ? 03:00 | Enrichissement IA des catalogues de r?f?rence | Service interne |
| `nettoyage_cache_7j` | Quotidien 02:00 | Purge cache applicatif | Service interne |
| `backup_donnees_critiques` | Quotidien 01:00 | Snapshot JSON des tables critiques | Service interne |
| `nettoyage_logs` | Dimanche 04:00 | Purge logs audit/s?curit? > 90 jours | Service interne |
| `purge_logs_anciens_mensuelle` | Le 1er ? 03:00 | Purge mensuelle logs anciens | Service interne |
| `purge_historique_jeux` | Le 1er ? 03:30 | Archivage paris sportifs > 12 mois | Service interne |

### Sant? et bien-?tre (3 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `rappel_vaccins` | Lundi 09:00 | Rappels vaccins (horizon 30j + retards) | push + ntfy + WhatsApp |
| `rappel_documents_expirants` | Quotidien 08:00 | Rappels documents famille expirants (urgence gradu?e) | push + ntfy + email |
| `check_garmin_anomalies` | Quotidien 08:00 | Alerte si inactivit? Garmin > 3 jours | ntfy + push |

### Automatisations (1 job)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `automations_runner` | Toutes les 5 min | Ex?cution r?gles Si?Alors actives | Service interne |

### Gamification et performance (2 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `points_famille_hebdo` | Dimanche 20:00 | Calcul points famille + d?blocage badges | push (badges) |
| `maj_donnees_meteo` | Quotidien 06:00 | Pr?chargement donn?es m?t?o 7 jours | Service interne |

### ?nergie et jardin (2 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `alertes_energie` | Quotidien 07:00 | D?tection anomalies ?nergie (vs moyenne historique) | ntfy + push + email |
| `tache_jardin_saisonniere` | Trimestriel (Mar/Jun/Sep/Dec) 06:00 | Rappels t?ches jardin saisonni?res | push + ntfy |

### Veille et budget (2 jobs)

| ID | Horaire | Objet | Canaux |
| ---- | --------- | ------- | -------- |
| `veille_emploi` | Quotidien 07:00 | Veille march? emploi quotidienne (multi-sites) | Service interne |
| `alertes_budget_seuil` | Quotidien 20:00 | Alerte si cat?gorie > 80% du budget mensuel | Service interne |

---

## Registre des jobs

Tous les jobs sont enregistr?s dans le dictionnaire `_REGISTRE_JOBS` :

- **Cl?** : identifiant du job (str)
- **Valeur** : tuple (nom affich?, fonction)

Le registre est construit de mani?re incr?mentale :

1. Jobs initiaux (28 jobs de base)
2. Ajouts Phase 7 (jobs cron suppl?mentaires)
3. Ajouts Phase 8 (notifications, contrats, documents)
4. Ajouts Phase 10 (innovations, gamification, automations)
5. Ajouts Phase B (IA avanc?e, r?sum?s narratifs)

Fonctions de gestion :

- `lister_jobs_disponibles()` ? liste tri?e de tous les IDs ex?cutables
- `executer_job_par_id(job_id, dry_run=False)` ? ex?cution par ID avec support dry-run

---

## Multi-utilisateur

Les notifications d?clench?es par les jobs passent par :

- `_obtenir_user_ids_actifs()` ? r?cup?re les IDs utilisateurs actifs depuis la base
- `_envoyer_notif_tous_users()` ? diffuse la notification ? tous les utilisateurs actifs

Fallback : variable `CRON_DEFAULT_USER_IDS` (CSV) si la base n'est pas disponible.

---

## Variables d'environnement

| Variable | Usage | D?faut |
| ---------- | ------- | -------- |
| `CRON_DEFAULT_USER_IDS` | IDs utilisateurs fallback (CSV) | `"matanne"` |
| `ADMIN_USER_IDS` | IDs admin pour alertes d'?chec (CSV) | Premier utilisateur actif |
| `ENVIRONMENT` | Mode dev/prod (affecte logging) | `"production"` |

---

## D?clenchement manuel depuis l'admin

Routes disponibles :

```http
GET    /api/v1/admin/jobs              # Liste de tous les jobs
POST   /api/v1/admin/jobs/{job_id}/run # Ex?cution manuelle (dry_run optionnel)
GET    /api/v1/admin/jobs/{job_id}/logs # Historique des 50 derni?res ex?cutions
GET    /api/v1/admin/jobs/history      # Historique pagin? avec filtres
```

---

## Historique d'ex?cution

L'historique est persist? dans la table `job_executions` (consolid?e dans `sql/schema/03_systeme.sql`).

Colonnes : `id`, `job_id`, `job_name`, `started_at`, `ended_at`, `duration_ms`, `status` (`running`/`success`/`failure`/`dry_run`), `error_message`, `output_logs`, `triggered_by_user_id`, `triggered_by_user_role` (`admin`/`system`), `created_at`, `modified_at`.

Fonctions internes :

- `_creer_execution_job(job_id, source)` ? cr?e un enregistrement au d?marrage
- `_finaliser_execution_job(execution_id, status, error_message)` ? met ? jour en fin d'ex?cution
- `_executer_job_trace()` ? ex?cute le job avec tracing complet, m?triques et gestion d'erreurs
- `_notifier_echec_job_admin()` ? notifie les admins en cas d'?chec (push + email)

---

## D?pannage rapide

### Aucun job visible dans l'admin

- V?rifier que l'API a d?marr? sans erreur
- V?rifier le lancement du scheduler dans `src/api/main.py`
- V?rifier que `D?marreurCron` a bien ?t? initialis?
- Contr?ler le mapping `_LABELS_JOBS` dans `src/api/routes/admin.py`

### Un job ne fait rien

- Lancer le job manuellement depuis l'admin (`POST .../run`)
- V?rifier les pr?conditions m?tier (utilisateurs actifs, donn?es en base)
- Regarder les logs applicatifs backend

### Les notifications de job ne partent pas

- V?rifier les abonnements push et la configuration des canaux
- V?rifier le dispatcher de notifications (`notif_dispatcher.py`)
- V?rifier la r?cup?ration des utilisateurs actifs

### Un job Google Calendar ?choue

- V?rifier les calendriers externes actifs en base
- V?rifier les credentials et refresh tokens Google
- V?rifier que le fournisseur vaut bien `google`

### Un job Garmin ne synchronise rien

- V?rifier que des profils ont `garmin_connected = true`
- V?rifier les credentials OAuth Garmin
- V?rifier les logs de sync par profil

---

## Limitations connues

- Pas de retry riche ni backoff centralis? par job
- Notification d'?chec admin partielle (via `_notifier_echec_job_admin()`, pas syst?matique)

Ces points sont identifi?s dans le planning pour am?lioration future.

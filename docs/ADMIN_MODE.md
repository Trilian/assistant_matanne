# Admin Mode

> Guide opérationnel du mode admin et des actions runtime exposées par l'API.

---

## Périmètre

Le mode admin couvre les opérations sensibles exposées sous `/api/v1/admin` :

- supervision des services et du scheduler
- déclenchement manuel des jobs et simulations
- notifications de test et preview de templates
- lecture et édition des feature flags runtime
- maintenance, mode test, actions de re-sync et console rapide
- audit, event bus, import/export de configuration et outils de diagnostic

Le routeur admin est composé depuis :

- `src/api/routes/admin.py`
- `src/api/routes/admin_audit.py`
- `src/api/routes/admin_jobs.py`
- `src/api/routes/admin_operations.py`
- `src/api/routes/admin_infra.py`

Le code déclare actuellement 65 endpoints admin.

---

## Accès et garde-fous

- rôle requis : `admin`
- rate limiting global admin : `10 req/min`
- rate limiting pour les triggers de jobs : `5 déclenchements/min/admin`
- journalisation des actions mutatives via le service d'audit
- `dry_run` disponible sur une partie des opérations critiques

Contrôles techniques :

- dépendance `require_role("admin")`
- dépendance globale `_verifier_limite_admin`
- limite dédiée `_verifier_limite_jobs`

---

## Capacités principales

| Zone | Endpoints clés | Ce que ça permet |
| --- | --- | --- |
| Jobs | `/jobs`, `/jobs/{job_id}/run`, `/jobs/run-all`, `/jobs/{job_id}/schedule` | lister, simuler, exécuter, replanifier |
| Services | `/services/health`, `/services/actions`, `/services/actions/{action_id}/run` | vérifier la santé, exécuter des actions whitelistées |
| Notifications | `/notifications/test`, `/notifications/test-all`, `/notifications/templates/*` | tester les canaux et prévisualiser les templates |
| Runtime | `/feature-flags`, `/runtime-config`, `/mode-test`, `/maintenance` | piloter les drapeaux et modes globaux |
| Diagnostic | `/quick-command`, `/flow-simulator`, `/cockpit`, `/metrics/api` | diagnostic rapide et simulation |
| Audit | `/audit-logs`, `/audit-stats`, `/events`, `/events/replay` | tracer et rejouer l'activité |
| Data/infra | `/db/*`, `/config/export`, `/config/import`, `/seed/*` | opérations encadrées d'infrastructure |

---

## Feature flags runtime

Flags par défaut documentés dans `src/api/routes/admin_constants.py` :

- `admin.service_actions_enabled`
- `admin.resync_enabled`
- `admin.seed_dev_enabled`
- `admin.mode_test`
- `admin.maintenance_mode`
- `jeux.bankroll_page_enabled`
- `outils.notes_tags_ui_enabled`

Configuration runtime par défaut :

- `dashboard.refresh_seconds`
- `notifications.digest_interval_minutes`
- `admin.max_jobs_triggers_per_min`

---

## Procédures courantes

### Vérifier l'état global

1. Appeler `GET /api/v1/admin/cockpit`
2. Contrôler le nombre de jobs actifs, les jobs récents et la santé des services
3. Compléter par `GET /api/v1/admin/services/health` si un service semble dégradé

### Déclencher un job en sécurité

1. Lister les jobs avec `GET /api/v1/admin/jobs`
2. Tester d'abord `POST /api/v1/admin/jobs/{job_id}/run?dry_run=true`
3. Exécuter réellement si le résultat est conforme
4. Consulter l'historique via `GET /api/v1/admin/jobs/{job_id}/logs`

### Exécuter un lot de jobs

Utiliser `POST /api/v1/admin/jobs/run-all` avec :

- `dry_run` pour une simulation globale
- `continuer_sur_erreur` si le lot ne doit pas s'arrêter au premier échec
- `inclure_jobs_inactifs` seulement pour un diagnostic approfondi

### Modifier un schedule sans redéploiement

1. Appeler `PUT /api/v1/admin/jobs/{job_id}/schedule`
2. Fournir un cron au format `m h dom mon dow`
3. Vérifier la nouvelle `next_run_time` retournée par l'API

### Tester un canal de notification

1. `POST /api/v1/admin/notifications/test` pour un canal unique
2. `POST /api/v1/admin/notifications/test-all` pour la cascade complète
3. `GET /api/v1/admin/notifications/templates` et `preview` pour valider le rendu

### Basculer maintenance ou mode test

- `PUT /api/v1/admin/maintenance`
- `PUT /api/v1/admin/mode-test`

Le mode test rend l'admin plus verbeux et desserre certains garde-fous de diagnostic. Le mode maintenance agit comme drapeau global lisible aussi via `/api/v1/admin/public/maintenance`.

### Utiliser la console rapide

`POST /api/v1/admin/quick-command` supporte notamment :

- `list jobs`
- `run job <job_id> [--dry-run]`
- `clear cache [pattern]`
- `health`
- `stats cache`
- `maintenance on|off`

---

## Monitoring et sources de vérité

### Scheduler et jobs

- bootstrap du scheduler : `src/api/main.py`
- implémentation centrale : `src/services/core/cron/jobs.py`
- matrice de scheduling : `src/services/core/cron/jobs_schedule.py`
- historique persistant : table `job_executions`

### Audit et métriques

- actions admin journalisées via `_journaliser_action_admin`
- métriques services via le registre de services
- résumé métriques API/IA disponible dans le cockpit admin
- Prometheus disponible si activé dans l'application principale

### Cache et santé infra

- stats cache via `obtenir_cache().obtenir_statistiques()`
- événements sécurité 24h et jobs récents exposés par le cockpit

---

## Bonnes pratiques

- commencer par un `dry_run` pour tout job mutatif
- privilégier les actions whitelistées plutôt que des manipulations directes en base
- tracer toute action manuelle sensible par l'audit admin
- utiliser la replanification dynamique seulement comme mesure opérationnelle, pas comme configuration produit durable
- ne pas activer le mode maintenance sans communication utilisateur si le frontend public est exposé

---

## Liens utiles

- `docs/ADMIN_QUICK_REFERENCE.md`
- `docs/ADMIN_RUNBOOK.md`
- `docs/CRON_JOBS.md`
- `docs/AUTOMATIONS.md`
- `docs/MONITORING.md`

# Admin — Référence rapide

> Aide-mémoire pour les opérations admin les plus fréquentes sur l'API.

---

## Accès et garde-fous

- **Préfixe** : `/api/v1/admin`
- **Rôle requis** : `admin`
- **Rate limit** : `10 req/min` global, `5 déclenchements/min` pour les jobs
- **Réflexe sécurité** : lancer un `dry_run` dès qu'une action modifie des données

---

## Endpoints à connaître

| Zone | Endpoint | Usage rapide |
| --- | --- | --- |
| Cockpit | `GET /cockpit` | vue d'ensemble santé + jobs + événements |
| Jobs | `GET /jobs` | lister tous les jobs disponibles |
| Jobs | `POST /jobs/{job_id}/run?dry_run=true` | simulation sécurisée |
| Jobs | `POST /jobs/run-all` | exécution groupée contrôlée |
| Jobs | `PUT /jobs/{job_id}/schedule` | replanifier sans redéploiement |
| Jobs | `POST /jobs/run-morning-batch` | rejouer le lot du matin |
| Jobs | `POST /jobs/simulate-day` | simulation d'une journée complète |
| Services | `GET /services/health` | état des dépendances et services métiers |
| Notifications | `POST /notifications/test` | tester un canal unique |
| Notifications | `POST /notifications/test-all` | valider la cascade multi-canale |
| Runtime | `GET /feature-flags` | lire les drapeaux actifs |
| Runtime | `PUT /feature-flags` | basculer un flag runtime |
| Runtime | `PUT /maintenance` | activer / couper le mode maintenance |
| Runtime | `PUT /mode-test` | activer le mode test admin |
| Audit | `GET /audit-logs` | consulter l'historique des actions |
| Events | `GET /events` | inspecter le bus d'événements |
| Events | `POST /events/trigger` | injecter un événement de test |
| Config | `GET /config/export` | exporter runtime + flags |
| Config | `POST /config/import` | réimporter une configuration |

---

## Séquences recommandées

### 1. Vérifier un incident de production

1. `GET /api/v1/admin/cockpit`
2. `GET /api/v1/admin/services/health`
3. `GET /api/v1/admin/jobs/history`
4. `GET /api/v1/admin/audit-logs?limit=50`

### 2. Rejouer un job sans risque

1. `GET /api/v1/admin/jobs`
2. `POST /api/v1/admin/jobs/{job_id}/run?dry_run=true`
3. Contrôler la sortie et les logs
4. Relancer sans `dry_run` si tout est conforme

### 3. Tester un flux inter-module

1. `GET /api/v1/admin/bridges/status?inclure_smoke=true`
2. `POST /api/v1/admin/events/trigger`
3. `GET /api/v1/admin/events?limite=30`

---

## Quick commands utiles

La console rapide (`POST /api/v1/admin/quick-command`) supporte notamment :

- `list jobs`
- `run job <job_id> --dry-run`
- `health`
- `clear cache [pattern]`
- `stats cache`
- `maintenance on|off`

---

## Feature flags fréquents

| Flag | Rôle |
| --- | --- |
| `admin.service_actions_enabled` | autorise les actions admin whitelistées |
| `admin.resync_enabled` | active les endpoints de resynchronisation |
| `admin.seed_dev_enabled` | autorise les seeds et jeux de données dev |
| `admin.mode_test` | rend l'admin plus verbeux pour les diagnostics |
| `admin.maintenance_mode` | drapeau de maintenance global |

---

## Références longues

- `docs/ADMIN_MODE.md` — guide opérationnel complet
- `docs/ADMIN_RUNBOOK.md` — procédures détaillées
- `docs/CRON_JOBS.md` — inventaire complet des jobs
- `docs/AUTOMATIONS.md` — moteur Si→Alors et exploitation runtime

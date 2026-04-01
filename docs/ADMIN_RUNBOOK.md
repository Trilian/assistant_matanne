# Admin Runbook

> Guide op?rationnel complet du mode administration : 51 endpoints, jobs, cache, notifications, sant? des services, feature flags, simulations et gestion des utilisateurs.
>
> **Derni?re mise ? jour** : 1er avril 2026

---

## Vue d'ensemble

Le module admin centralise les op?rations sensibles expos?es par l'API et l'interface Next.js.

- **Backend** : `src/api/routes/admin.py` (51 endpoints)
- **Frontend** : `frontend/src/app/(app)/admin/`
- **Acc?s** : r?le `admin` obligatoire (`require_role("admin")`)
- **Rate limiting** : 10 req/min standard, 5 req/min pour triggers jobs

---

## Pr?-requis

- ?tre authentifi? avec un utilisateur ayant le r?le `admin`
- Backend d?marr? avec le scheduler actif
- Frontend d?marr? pour utiliser les ?crans d'administration
- Variables d'environnement correctement configur?es pour les canaux test?s

```bash
python manage.py run
cd frontend && npm run dev
```

---

## Navigation admin

| Page | URL | Fonctionnalit?s |
| ------ | ----- | ----------------- |
| Tableau de bord | `/admin` | Vue globale, alertes, anomalies |
| Jobs planifi?s | `/admin/jobs` | Liste, ex?cution manuelle, logs |
| Scheduler visuel | `/admin/scheduler` | Timeline CRON, filtre par cat?gorie, prochain run |
| Console rapide | `/admin/console` | Commandes admin (`run job`, `clear cache`, `health`) |
| Logs temps r?el | `/admin/logs` | Flux WebSocket logs + m?triques live |
| Services | `/admin/services` | Sant?, cache, resync |
| Notifications | `/admin/notifications` | Tests canaux |
| Utilisateurs | `/admin/utilisateurs` | Gestion comptes |

Protection : route API via `require_role("admin")` + layout frontend via `admin/layout.tsx`.

---

## R?f?rence compl?te des endpoints (51)

### Audit et s?curit? (6 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/audit-logs` | Logs d'audit pagin?s avec filtres (action, entit?, p?riode) |
| `GET` | `/api/v1/admin/audit-stats` | Statistiques agr?g?es (comptages par action/entit?/source) |
| `GET` | `/api/v1/admin/audit-export` | Export CSV des logs d'audit (max 10k lignes) |
| `GET` | `/api/v1/admin/security-logs` | ?v?nements s?curit? temps r?el (auth, rate limiting, actions admin) |
| `GET` | `/api/v1/admin/events` | Historique event bus + m?triques (30 derniers ?v?nements) |
| `POST` | `/api/v1/admin/events/trigger` | D?clencher manuellement un ?v?nement domaine (test) |

### Jobs et planification (5 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/jobs` | Liste tous les 68 jobs avec prochain run |
| `POST` | `/api/v1/admin/jobs/{job_id}/run` | D?clencher un job manuellement (dry-run optionnel, rate-limited 5/min) |
| `GET` | `/api/v1/admin/jobs/{job_id}/logs` | Historique des 50 derni?res ex?cutions |
| `GET` | `/api/v1/admin/jobs/history` | Historique pagin? avec filtres |
| `POST` | `/api/v1/admin/quick-command` | Console rapide admin (help, run job, clear cache, maintenance) |
| `GET` | `/api/v1/admin/bridges/phase5/status` | Statut de tous les bridges Phase 5 (smoke + pr?sence) |

### Notifications (4 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `POST` | `/api/v1/admin/notifications/test` | Test sur un canal (ntfy/push/email/whatsapp) |
| `POST` | `/api/v1/admin/notifications/test-all` | Test multi-canal avec failover |
| `GET` | `/api/v1/admin/notifications/channels` | Canaux configur?s + statut |
| `GET` | `/api/v1/admin/notifications/queue` | File d'attente notifications digest |

### Cache et performance (4 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/cache/stats` | Hit/miss ratio, taille m?moire/fichier, entr?es par pattern |
| `POST` | `/api/v1/admin/cache/clear` | Vider tout le cache (L1 + L3) |
| `POST` | `/api/v1/admin/cache/purge` | Purge par motif (`planning_*`, `recettes_*`, `suggestions_*`) |
| `POST` | `/api/v1/admin/cache/invalidate/{pattern}` | Invalidation s?lective avec m?triques |

### Services et sant? (5 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/services/health` | Sant? globale du registre de services |
| `GET` | `/api/v1/admin/services/actions` | Catalogue d'actions service ex?cutables |
| `POST` | `/api/v1/admin/services/{action}/run` | Ex?cuter une action service (dry-run possible) |
| `GET` | `/api/v1/admin/services/resync` | Cibles de resync (Garmin, Google Calendar, OpenFoodFacts) |
| `POST` | `/api/v1/admin/services/resync/{target}` | Forcer une resync externe |

### Utilisateurs et impersonation (4 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/users` | Liste utilisateurs avec r?le/statut/created_at |
| `POST` | `/api/v1/admin/users/{id}/disable` | D?sactiver un compte |
| `POST` | `/api/v1/admin/users/{id}/impersonate` | Token d'impersonation 1h (audit logged) |
| `GET` | `/api/v1/admin/users/{id}/activity` | R?sum? activit? r?cente |

### Base de donn?es (5 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/db/coherence` | V?rification coh?rence DB (FK, RLS) |
| `GET` | `/api/v1/admin/db/views` | Liste vues SQL read-only autoris?es |
| `POST` | `/api/v1/admin/db/query` | Ex?cuter SQL read-only (whitelist enforced) |
| `GET` | `/api/v1/admin/db/export` | Export table JSON/CSV |
| `POST` | `/api/v1/admin/db/import` | Import donn?es (merge ou replace) |

### Feature flags et configuration (6 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/feature-flags` | Liste feature flags (admin, jeux, outils) |
| `PUT` | `/api/v1/admin/feature-flags` | Modifier feature flags (persistant) |
| `GET` | `/api/v1/admin/runtime-config` | Configuration runtime (db.refresh_seconds, etc.) |
| `PUT` | `/api/v1/admin/runtime-config` | Modifier config runtime (persistant) |
| `GET` | `/api/v1/admin/config/export` | Export toute la config (flags + runtime) |
| `POST` | `/api/v1/admin/config/import` | Import config (merge ou replace) |

### Tests et simulation (5 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `POST` | `/api/v1/admin/simulate/flow` | Simuler flux inter-modules sans effets de bord |
| `POST` | `/api/v1/admin/seed/data` | Seed donn?es de r?f?rence |
| `PUT` | `/api/v1/admin/mode/maintenance` | Activer/d?sactiver mode maintenance |
| `POST` | `/api/v1/admin/ai/console` | Prompt LLM direct (temp?rature/tokens configurables) |
| `PUT` | `/api/v1/admin/mode/test` | Activer/d?sactiver mode test |

### M?triques et cockpit (2 endpoints)

| M?thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/metrics/api` | Requ?tes HTTP total, top endpoints, latence (avg/p95) |
| `GET` | `/api/v1/admin/cockpit` | Dashboard ex?cutif (uptimes, alertes, anomalies) |

---

## Proc?dures op?rationnelles

### Jobs planifi?s

**Consulter les jobs** :

1. Ouvrir `/admin/jobs`
2. V?rifier la liste, l'horaire cron, le prochain run et le statut

**D?clencher manuellement** :

1. Depuis `/admin/jobs`, cliquer sur le bouton d'ex?cution du job cibl?
2. Optionnel : cocher `dry_run` pour simuler sans effets
3. L'ex?cution est journalis?e dans `job_executions` et audit?e (`admin.job.run`)

**Consulter les logs** :

```http
GET /api/v1/admin/jobs/{job_id}/logs
```

### Cache applicatif

**Consulter les statistiques** :

```http
GET /api/v1/admin/cache/stats
```

? Volume m?moire/fichier, hit ratio, entr?es par pattern

**Purger par motif** :

```http
POST /api/v1/admin/cache/purge
{"pattern": "planning_*"}
```

Cas d'usage : donn?e fig?e, r?ponse IA obsol?te, test propre

**Vider compl?tement** :

```http
POST /api/v1/admin/cache/clear
```

R?server aux cas : incoh?rence g?n?rale, mont?e de version, test perf ? froid

### Sant? des services

```http
GET /api/v1/admin/services/health
```

Remonte : `global_status`, nombre services enregistr?s/instanci?s/sains, erreurs

Quand intervenir : `global_status = error`, services critiques non instanciables

### Notifications de test

```http
POST /api/v1/admin/notifications/test
{"canal": "ntfy", "titre": "Test admin", "message": "Validation"}
```

Points d'attention :

- `push` n?cessite un abonnement navigateur actif
- `email` n?cessite config Resend valide
- `whatsapp` d?pend de la config Meta Cloud API

### Gestion utilisateurs

```http
GET /api/v1/admin/users?par_page=100
POST /api/v1/admin/users/{id}/disable
{"raison": "Compte de test obsol?te"}
```

Bonnes pratiques : raison explicite, ne pas d?sactiver le dernier admin, v?rifier impacts sur les jobs multi-utilisateurs.

### Feature flags

```http
GET /api/v1/admin/feature-flags
PUT /api/v1/admin/feature-flags
{"flag_name": true}
```

### Simulation de flux

```http
POST /api/v1/admin/simulate/flow
{"type": "peremption_j2"}
```

Simule le flux inter-module sans effets de bord (utile pour valider le wiring).

---

## Proc?dures de diagnostic

### Le planning ou les suggestions semblent bloqu?s

1. V?rifier l'?tat global des services dans `/admin/services`
2. Purger le cache par motif cibl? (`planning_*` ou `suggestions_*`)
3. Relancer le job concern? si le probl?me d?pend d'une t?che planifi?e
4. Consulter les logs d'audit pour confirmer l'action ex?cut?e

### Les notifications n'arrivent plus

1. Envoyer un test via `/admin/notifications`
2. Contr?ler les abonnements push et la configuration du canal
3. V?rifier les pr?f?rences utilisateur si seul un utilisateur est affect?
4. Consulter les logs backend du dispatcher

### Un cron job critique n'a pas tourn?

1. V?rifier la pr?sence du job dans `/admin/jobs`
2. Regarder le prochain run et les logs du job
3. Lancer un trigger manuel pour distinguer probl?me scheduler vs m?tier
4. Si n?cessaire, red?marrer l'API pour recr?er le scheduler

---

## R?f?rences associ?es

- `docs/CRON_JOBS.md` ? R?f?rence compl?te des 68 jobs
- `docs/NOTIFICATIONS.md` ? Syst?me de notifications
- `docs/TROUBLESHOOTING.md` ? Guide de d?pannage
- `docs/DEVELOPER_SETUP.md` ? Setup d?veloppeur

# Admin Runbook

> Guide opérationnel complet du mode administration : 51 endpoints, jobs, cache, notifications, santé des services, feature flags, simulations et gestion des utilisateurs.
>
> **Dernière mise à jour** : 1er avril 2026

---

## Vue d'ensemble

Le module admin centralise les opérations sensibles exposées par l'API et l'interface Next.js.

- **Backend** : `src/api/routes/admin.py` (51 endpoints)
- **Frontend** : `frontend/src/app/(app)/admin/`
- **Accès** : rôle `admin` obligatoire (`require_role("admin")`)
- **Rate limiting** : 10 req/min standard, 5 req/min pour triggers jobs

---

## Pré-requis

- Être authentifié avec un utilisateur ayant le rôle `admin`
- Backend démarré avec le scheduler actif
- Frontend démarré pour utiliser les écrans d'administration
- Variables d'environnement correctement configurées pour les canaux testés

```bash
python manage.py run
cd frontend && npm run dev
```

---

## Navigation admin

| Page | URL | Fonctionnalités |
| ------ | ----- | ----------------- |
| Tableau de bord | `/admin` | Vue globale, alertes, anomalies |
| Jobs planifiés | `/admin/jobs` | Liste, exécution manuelle, logs |
| Services | `/admin/services` | Santé, cache, resync |
| Notifications | `/admin/notifications` | Tests canaux |
| Utilisateurs | `/admin/utilisateurs` | Gestion comptes |

Protection : route API via `require_role("admin")` + layout frontend via `admin/layout.tsx`.

---

## Référence complète des endpoints (51)

### Audit et sécurité (6 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/audit-logs` | Logs d'audit paginés avec filtres (action, entité, période) |
| `GET` | `/api/v1/admin/audit-stats` | Statistiques agrégées (comptages par action/entité/source) |
| `GET` | `/api/v1/admin/audit-export` | Export CSV des logs d'audit (max 10k lignes) |
| `GET` | `/api/v1/admin/security-logs` | Événements sécurité temps réel (auth, rate limiting, actions admin) |
| `GET` | `/api/v1/admin/events` | Historique event bus + métriques (30 derniers événements) |
| `POST` | `/api/v1/admin/events/trigger` | Déclencher manuellement un événement domaine (test) |

### Jobs et planification (5 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/jobs` | Liste tous les 68 jobs avec prochain run |
| `POST` | `/api/v1/admin/jobs/{job_id}/run` | Déclencher un job manuellement (dry-run optionnel, rate-limited 5/min) |
| `GET` | `/api/v1/admin/jobs/{job_id}/logs` | Historique des 50 dernières exécutions |
| `GET` | `/api/v1/admin/jobs/history` | Historique paginé avec filtres |
| `GET` | `/api/v1/admin/bridges/phase5/status` | Statut de tous les bridges Phase 5 (smoke + présence) |

### Notifications (4 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `POST` | `/api/v1/admin/notifications/test` | Test sur un canal (ntfy/push/email/whatsapp) |
| `POST` | `/api/v1/admin/notifications/test-all` | Test multi-canal avec failover |
| `GET` | `/api/v1/admin/notifications/channels` | Canaux configurés + statut |
| `GET` | `/api/v1/admin/notifications/queue` | File d'attente notifications digest |

### Cache et performance (4 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/cache/stats` | Hit/miss ratio, taille mémoire/fichier, entrées par pattern |
| `POST` | `/api/v1/admin/cache/clear` | Vider tout le cache (L1 + L3) |
| `POST` | `/api/v1/admin/cache/purge` | Purge par motif (`planning_*`, `recettes_*`, `suggestions_*`) |
| `POST` | `/api/v1/admin/cache/invalidate/{pattern}` | Invalidation sélective avec métriques |

### Services et santé (5 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/services/health` | Santé globale du registre de services |
| `GET` | `/api/v1/admin/services/actions` | Catalogue d'actions service exécutables |
| `POST` | `/api/v1/admin/services/{action}/run` | Exécuter une action service (dry-run possible) |
| `GET` | `/api/v1/admin/services/resync` | Cibles de resync (Garmin, Google Calendar, OpenFoodFacts) |
| `POST` | `/api/v1/admin/services/resync/{target}` | Forcer une resync externe |

### Utilisateurs et impersonation (4 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/users` | Liste utilisateurs avec rôle/statut/created_at |
| `POST` | `/api/v1/admin/users/{id}/disable` | Désactiver un compte |
| `POST` | `/api/v1/admin/users/{id}/impersonate` | Token d'impersonation 1h (audit logged) |
| `GET` | `/api/v1/admin/users/{id}/activity` | Résumé activité récente |

### Base de données (5 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/db/coherence` | Vérification cohérence DB (FK, RLS) |
| `GET` | `/api/v1/admin/db/views` | Liste vues SQL read-only autorisées |
| `POST` | `/api/v1/admin/db/query` | Exécuter SQL read-only (whitelist enforced) |
| `GET` | `/api/v1/admin/db/export` | Export table JSON/CSV |
| `POST` | `/api/v1/admin/db/import` | Import données (merge ou replace) |

### Feature flags et configuration (6 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/feature-flags` | Liste feature flags (admin, jeux, outils) |
| `PUT` | `/api/v1/admin/feature-flags` | Modifier feature flags (persistant) |
| `GET` | `/api/v1/admin/runtime-config` | Configuration runtime (db.refresh_seconds, etc.) |
| `PUT` | `/api/v1/admin/runtime-config` | Modifier config runtime (persistant) |
| `GET` | `/api/v1/admin/config/export` | Export toute la config (flags + runtime) |
| `POST` | `/api/v1/admin/config/import` | Import config (merge ou replace) |

### Tests et simulation (5 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `POST` | `/api/v1/admin/simulate/flow` | Simuler flux inter-modules sans effets de bord |
| `POST` | `/api/v1/admin/seed/data` | Seed données de référence |
| `PUT` | `/api/v1/admin/mode/maintenance` | Activer/désactiver mode maintenance |
| `POST` | `/api/v1/admin/ai/console` | Prompt LLM direct (température/tokens configurables) |
| `PUT` | `/api/v1/admin/mode/test` | Activer/désactiver mode test |

### Métriques et cockpit (2 endpoints)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/admin/metrics/api` | Requêtes HTTP total, top endpoints, latence (avg/p95) |
| `GET` | `/api/v1/admin/cockpit` | Dashboard exécutif (uptimes, alertes, anomalies) |

---

## Procédures opérationnelles

### Jobs planifiés

**Consulter les jobs** :

1. Ouvrir `/admin/jobs`
2. Vérifier la liste, l'horaire cron, le prochain run et le statut

**Déclencher manuellement** :

1. Depuis `/admin/jobs`, cliquer sur le bouton d'exécution du job ciblé
2. Optionnel : cocher `dry_run` pour simuler sans effets
3. L'exécution est journalisée dans `job_executions` et auditée (`admin.job.run`)

**Consulter les logs** :

```http
GET /api/v1/admin/jobs/{job_id}/logs
```

### Cache applicatif

**Consulter les statistiques** :

```http
GET /api/v1/admin/cache/stats
```

→ Volume mémoire/fichier, hit ratio, entrées par pattern

**Purger par motif** :

```http
POST /api/v1/admin/cache/purge
{"pattern": "planning_*"}
```

Cas d'usage : donnée figée, réponse IA obsolète, test propre

**Vider complètement** :

```http
POST /api/v1/admin/cache/clear
```

Réserver aux cas : incohérence générale, montée de version, test perf à froid

### Santé des services

```http
GET /api/v1/admin/services/health
```

Remonte : `global_status`, nombre services enregistrés/instanciés/sains, erreurs

Quand intervenir : `global_status = error`, services critiques non instanciables

### Notifications de test

```http
POST /api/v1/admin/notifications/test
{"canal": "ntfy", "titre": "Test admin", "message": "Validation"}
```

Points d'attention :

- `push` nécessite un abonnement navigateur actif
- `email` nécessite config Resend valide
- `whatsapp` dépend de la config Meta Cloud API

### Gestion utilisateurs

```http
GET /api/v1/admin/users?par_page=100
POST /api/v1/admin/users/{id}/disable
{"raison": "Compte de test obsolète"}
```

Bonnes pratiques : raison explicite, ne pas désactiver le dernier admin, vérifier impacts sur les jobs multi-utilisateurs.

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

## Procédures de diagnostic

### Le planning ou les suggestions semblent bloqués

1. Vérifier l'état global des services dans `/admin/services`
2. Purger le cache par motif ciblé (`planning_*` ou `suggestions_*`)
3. Relancer le job concerné si le problème dépend d'une tâche planifiée
4. Consulter les logs d'audit pour confirmer l'action exécutée

### Les notifications n'arrivent plus

1. Envoyer un test via `/admin/notifications`
2. Contrôler les abonnements push et la configuration du canal
3. Vérifier les préférences utilisateur si seul un utilisateur est affecté
4. Consulter les logs backend du dispatcher

### Un cron job critique n'a pas tourné

1. Vérifier la présence du job dans `/admin/jobs`
2. Regarder le prochain run et les logs du job
3. Lancer un trigger manuel pour distinguer problème scheduler vs métier
4. Si nécessaire, redémarrer l'API pour recréer le scheduler

---

## Références associées

- `docs/CRON_JOBS.md` — Référence complète des 68 jobs
- `docs/NOTIFICATIONS.md` — Système de notifications
- `docs/TROUBLESHOOTING.md` — Guide de dépannage
- `docs/DEVELOPER_SETUP.md` — Setup développeur

# Admin Runbook

> Guide opérationnel du mode administration: jobs, cache, notifications, santé des services et gestion des utilisateurs.

---

## Vue d'ensemble

Le module admin centralise les opérations sensibles exposées par l'API et l'interface Next.js.

- Backend: `src/api/routes/admin.py`
- Frontend: `frontend/src/app/(app)/admin/`
- Accès: rôle `admin` obligatoire côté API et côté frontend

Les principales capacités disponibles aujourd'hui sont:

- consultation des logs d'audit
- exécution manuelle des jobs planifiés
- consultation des derniers logs de jobs déclenchés manuellement
- tests de notifications (`ntfy`, `push`, `email`, `whatsapp`)
- consultation de l'état de santé des services
- statistiques et purge du cache
- liste et désactivation des comptes utilisateurs

---

## Pré-requis

- être authentifié avec un utilisateur ayant le rôle `admin`
- backend démarré avec le scheduler actif
- frontend démarré pour utiliser les écrans d'administration
- variables d'environnement correctement configurées pour les canaux testés

Vérifications rapides:

```bash
python manage.py run
cd frontend && npm run dev
```

---

## Navigation admin

Pages disponibles dans l'interface:

- `/admin` : tableau de bord global
- `/admin/jobs` : jobs planifiés, exécution manuelle et logs
- `/admin/services` : santé des services et cache
- `/admin/notifications` : tests de canaux
- `/admin/utilisateurs` : gestion des comptes

Protection en place:

- route API protégée via `require_role("admin")`
- layout frontend protégé via `frontend/src/app/(app)/admin/layout.tsx`

---

## Jobs planifiés

### Consulter les jobs

Interface:

- ouvrir `/admin/jobs`
- vérifier la liste, le cron, le prochain run et le statut

API:

```http
GET /api/v1/admin/jobs
```

### Déclencher un job manuellement

Interface:

- depuis `/admin/jobs`, cliquer sur le bouton d'exécution du job ciblé
- vérifier le retour visuel de succès ou d'échec

API:

```http
POST /api/v1/admin/jobs/{job_id}/run
```

Effets actuels:

- le job est importé dynamiquement depuis `src.services.core.cron.jobs`
- l'exécution est journalisée en mémoire pour consultation immédiate
- une action d'audit `admin.job.run` est enregistrée

### Consulter les logs d'un job

```http
GET /api/v1/admin/jobs/{job_id}/logs
```

Limitation actuelle:

- l'historique retourné correspond aux déclenchements manuels observés par le processus courant
- il ne s'agit pas encore d'un historique persistant en base

### Si un job ne s'affiche pas

Causes probables:

- le scheduler n'a pas démarré
- le backend a démarré sans charger `src.services.core.cron.jobs`
- le job a été retiré ou renommé sans mise à jour du mapping admin

Vérifications:

- contrôler le démarrage du scheduler dans `src/api/main.py`
- contrôler la configuration des jobs dans `src/services/core/cron/jobs.py`
- vérifier le mapping `_LABELS_JOBS` et `_JOBS_DISPONIBLES` dans `src/api/routes/admin.py`

---

## Cache applicatif

### Consulter les statistiques

```http
GET /api/v1/admin/cache/stats
```

Utiliser cette vue pour vérifier:

- volume du cache mémoire et fichier
- hit ratio
- comportement après invalidation

### Purger par motif

Interface:

- onglet `Cache` dans `/admin/services`
- saisir un motif, par exemple `planning_*` ou `suggestions_*`

API:

```http
POST /api/v1/admin/cache/purge
Content-Type: application/json

{ "pattern": "planning_*" }
```

À utiliser quand:

- une donnée semble figée après modification métier
- un service IA renvoie une réponse devenue obsolète
- une campagne de test nécessite un recalcul propre

### Vider complètement le cache

```http
POST /api/v1/admin/cache/clear
```

À réserver aux cas suivants:

- diagnostic d'incohérence généralisée
- montée de version importante
- test de performance à froid

---

## Santé des services

### Contrôler l'état global

```http
GET /api/v1/admin/services/health
```

Le résultat remonte notamment:

- `global_status`
- nombre total de services enregistrés
- nombre de services instanciés
- nombre de services sains
- éventuelles erreurs de santé

Quand intervenir:

- `global_status = error`
- un service critique n'est plus instanciable
- la page admin remonte plusieurs erreurs récurrentes

Actions possibles:

- redémarrer l'API
- consulter les logs applicatifs
- vider le cache si la panne est liée à des données corrompues
- tester directement l'endpoint métier concerné

---

## Notifications de test

### Envoyer un test depuis l'admin

Canaux supportés:

- `ntfy`
- `push`
- `email`
- `whatsapp`

API:

```http
POST /api/v1/admin/notifications/test
Content-Type: application/json

{
  "canal": "ntfy",
  "titre": "Test depuis l'admin",
  "message": "Notification de validation"
}
```

Points d'attention:

- `push` nécessite un abonnement actif côté navigateur
- `email` nécessite une adresse cible et une configuration fournisseur valide
- `whatsapp` dépend de la configuration Meta Cloud API

Si un test échoue:

- vérifier la configuration des secrets
- contrôler les logs backend
- vérifier que le canal est bien activé dans l'environnement courant

---

## Utilisateurs

### Lister les comptes

```http
GET /api/v1/admin/users?par_page=100
```

Utiliser cette vue pour vérifier:

- nombre de comptes
- répartition des rôles
- comptes inactifs
- dates de création

### Désactiver un compte

Interface:

- ouvrir `/admin/utilisateurs`
- cliquer sur l'action de désactivation
- renseigner éventuellement une raison

API:

```http
POST /api/v1/admin/users/{id}/disable
Content-Type: application/json

{ "raison": "Compte de test obsolète" }
```

Bonnes pratiques:

- documenter une raison explicite
- éviter de désactiver le dernier compte admin actif
- vérifier les impacts sur les jobs multi-utilisateurs si le compte était utilisé comme référence fonctionnelle

---

## Audit logs

### Consulter les logs

```http
GET /api/v1/admin/audit-logs?page=1&par_page=25
GET /api/v1/admin/audit-logs?action=admin.job.run
GET /api/v1/admin/audit-logs?entite_type=job
```

### Exporter les logs

```http
GET /api/v1/admin/audit-export
```

Usage recommandé:

- tracer les opérations d'administration
- comprendre qui a exécuté un job ou désactivé un compte
- constituer un export CSV avant nettoyage manuel ou analyse externe

---

## Procédures courantes

### Le planning ou les suggestions semblent bloqués

1. Vérifier l'état global des services dans `/admin/services`.
2. Purger le cache par motif ciblé, par exemple `planning_*` ou `suggestions_*`.
3. Relancer le job concerné si le problème dépend d'une tâche planifiée.
4. Contrôler les logs d'audit pour confirmer l'action exécutée.

### Les notifications n'arrivent plus

1. Envoyer un test via `/admin/notifications`.
2. Contrôler les abonnements push et la configuration du canal concerné.
3. Vérifier les préférences utilisateur si seul un utilisateur est affecté.
4. Consulter les logs backend du dispatcher de notifications.

### Un cron job critique n'a pas tourné

1. Vérifier la présence du job dans `/admin/jobs`.
2. Regarder le prochain run et les logs du job.
3. Lancer un trigger manuel pour distinguer problème de scheduler et problème métier.
4. Si nécessaire, redémarrer l'API pour recréer le scheduler.

---

## Limitations connues

- pas encore d'historique persistant des exécutions de jobs
- pas encore de mode dry-run générique
- pas encore de feature flags administrables depuis l'UI
- certaines pages admin consomment encore directement `clientApi` sans client dédié consolidé

---

## Références associées

- `docs/CRON_JOBS.md`
- `docs/NOTIFICATIONS.md`
- `docs/TROUBLESHOOTING.md`
- `docs/DEVELOPER_SETUP.md`
# Admin Guide — Assistant MaTanne

> Guide opératoire du module administration.

---

## Objectif

Le module admin permet de:

- superviser les services
- lancer des jobs manuellement
- tester les notifications
- auditer l'activité
- diagnostiquer les problèmes de cohérence/cache

---

## Accès et sécurité

Toutes les routes admin sont protégées par rôle `admin`.

Pré-requis:

- être authentifié
- posséder le rôle admin dans le profil

Contrôles:

- `Depends(require_role("admin"))`
- rate limiting sur les actions sensibles (ex: exécution manuelle de jobs)
- audit log sur actions mutantes

---

## Endpoints principaux

Référence: `src/api/routes/admin.py`

- `GET /api/v1/admin/audit-logs`
- `GET /api/v1/admin/audit-stats`
- `GET /api/v1/admin/audit-export`
- `GET /api/v1/admin/jobs`
- `POST /api/v1/admin/jobs/{id}/run`
- `GET /api/v1/admin/jobs/{id}/logs`
- `POST /api/v1/admin/quick-command`
- `GET /api/v1/admin/services/health`
- `POST /api/v1/admin/notifications/test`
- `GET /api/v1/admin/cache/stats`
- `POST /api/v1/admin/cache/clear`
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users/{id}/disable`
- `GET /api/v1/admin/db/coherence`

---

## Procédures courantes

### 1) Vérifier la santé des services

1. Ouvrir la page admin services
2. Appeler `GET /services/health`
3. Vérifier services en erreur ou dégradés

### 2) Lancer un job manuellement

1. Aller sur la section jobs
2. Identifier le job cible
3. Exécuter `POST /jobs/{id}/run`
4. Consulter `GET /jobs/{id}/logs`

### 3) Tester la chaîne de notifications

1. Ouvrir l'outil de test notifications
2. Déclencher `POST /notifications/test`
3. Valider la réception par canal (ntfy/push/email/WhatsApp)

### 4) Vider le cache en sécurité

1. Vérifier les stats cache
2. Déclencher `POST /cache/clear`
3. Re-vérifier les hit/miss après quelques requêtes

---

## Diagnostic incidents

### Jobs ne s'exécutent plus

- vérifier scheduler actif
- vérifier logs job
- tester déclenchement manuel
- inspecter exceptions DB/externes

### Notifications absentes

- lancer un test unitaire via route admin
- vérifier configuration canal
- vérifier quotas/rate limits
- vérifier logs webhooks (WhatsApp)

### Incohérence de données

- exécuter `/db/coherence`
- recouper avec `scripts/audit_orm_sql.py`
- valider les dernières migrations SQL

---

## Bonnes pratiques exploitation

- privilégier le test manuel d'un job avant activation massive
- garder une traçabilité des actions admin sensibles
- ne pas vider le cache pendant des opérations critiques
- confirmer les permissions avant désactivation d'utilisateurs

---

## Roadmap admin

- persistance DB de l'historique jobs
- mode dry-run des jobs
- simulateur de flux inter-modules
- dashboard admin temps réel (latence, req/s, cache)

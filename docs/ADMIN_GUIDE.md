# Admin Guide â€” Assistant MaTanne

> Guide opÃ©ratoire du module administration.

---

## Objectif

Le module admin permet de:

- superviser les services
- lancer des jobs manuellement
- tester les notifications
- auditer l'activitÃ©
- diagnostiquer les problÃ¨mes de cohÃ©rence/cache

---

## AccÃ¨s et sÃ©curitÃ©

Toutes les routes admin sont protÃ©gÃ©es par rÃ´le `admin`.

PrÃ©-requis:

- Ãªtre authentifiÃ©
- possÃ©der le rÃ´le admin dans le profil

ContrÃ´les:

- `Depends(require_role("admin"))`
- rate limiting sur les actions sensibles (ex: exÃ©cution manuelle de jobs)
- audit log sur actions mutantes

---

## Endpoints principaux

RÃ©fÃ©rence: `src/api/routes/admin.py`

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

## ProcÃ©dures courantes

### 1) VÃ©rifier la santÃ© des services

1. Ouvrir la page admin services
2. Appeler `GET /services/health`
3. VÃ©rifier services en erreur ou dÃ©gradÃ©s

### 2) Lancer un job manuellement

1. Aller sur la section jobs
2. Identifier le job cible
3. ExÃ©cuter `POST /jobs/{id}/run`
4. Consulter `GET /jobs/{id}/logs`

### 3) Tester la chaÃ®ne de notifications

1. Ouvrir l'outil de test notifications
2. DÃ©clencher `POST /notifications/test`
3. Valider la rÃ©ception par canal (ntfy/push/email/Telegram)

### 4) Vider le cache en sÃ©curitÃ©

1. VÃ©rifier les stats cache
2. DÃ©clencher `POST /cache/clear`
3. Re-vÃ©rifier les hit/miss aprÃ¨s quelques requÃªtes

---

## Diagnostic incidents

### Jobs ne s'exÃ©cutent plus

- vÃ©rifier scheduler actif
- vÃ©rifier logs job
- tester dÃ©clenchement manuel
- inspecter exceptions DB/externes

### Notifications absentes

- lancer un test unitaire via route admin
- vÃ©rifier configuration canal
- vÃ©rifier quotas/rate limits
- vÃ©rifier logs webhooks (Telegram)

### IncohÃ©rence de donnÃ©es

- exÃ©cuter `/db/coherence`
- recouper avec `scripts/audit_orm_sql.py`
- valider les derniÃ¨res migrations SQL

---

## Bonnes pratiques exploitation

- privilÃ©gier le test manuel d'un job avant activation massive
- garder une traÃ§abilitÃ© des actions admin sensibles
- ne pas vider le cache pendant des opÃ©rations critiques
- confirmer les permissions avant dÃ©sactivation d'utilisateurs

---

## Roadmap admin

- persistance DB de l'historique jobs
- mode dry-run des jobs
- simulateur de flux inter-modules
- dashboard admin temps rÃ©el (latence, req/s, cache)


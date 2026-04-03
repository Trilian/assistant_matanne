# Troubleshooting

> Guide rapide pour diagnostiquer les pannes les plus fréquentes en développement et en exploitation légère.

---

## Backend ne démarre pas

Vérifier:

- la configuration `.env.local`
- la disponibilité de `DATABASE_URL`
- les imports récents dans `src/api/main.py`
- les traces liées au scheduler dans les logs de démarrage

Commandes utiles:

```bash
python manage.py run
python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect(); print('OK')"
```

---

## Frontend ne parle plus à l'API

Vérifier:

- `NEXT_PUBLIC_API_URL`
- que le backend écoute bien sur `http://localhost:8000`
- les règles CORS
- l'état d'authentification et le token côté frontend

---

## Scheduler ou jobs absents

Symptômes:

- page `/admin/jobs` vide
- aucun job visible
- notifications planifiées non envoyées

Vérifications:

- démarrage du scheduler dans `src/api/main.py`
- configuration `DémarreurCron` dans `src/services/core/cron/jobs.py`
- logs backend au boot

---

## Cache incohérent

Symptômes:

- données qui semblent figées
- suggestions qui ne se recalculent pas
- tableau de bord en retard après mutation

Actions:

- utiliser `/admin/services`
- purger par motif avant de vider tout le cache
- vérifier si le flux concerné utilise `@avec_cache`

---

## Notifications non reçues

Vérifier:

- abonnement push actif
- préférences de canaux par catégorie
- secrets email ou Telegram selon le canal visé
- test canal depuis l'admin

---

## Garmin ou Google Calendar ne synchronisent pas

Vérifier:

- connexions externes réellement actives en base
- refresh tokens valides
- exceptions par profil dans les logs backend
- exécution manuelle du job correspondant depuis l'admin

---

## Automations inactives

Vérifier:

- qu'il existe des règles actives en base
- que le déclencheur utilisé est supporté par le moteur
- que l'action visée est prise en charge
- que le job `automations_runner` tourne bien

---

## Page admin en erreur

Vérifier:

- que l'utilisateur a bien le rôle `admin`
- que l'API admin répond
- que les endpoints `jobs`, `services/health` et `users` ne renvoient pas d'erreur
- le composant d'erreur `frontend/src/app/(app)/admin/error.tsx`

---

## Tests cassés après mise à jour docs ou code

Vérifier:

- backend: `pytest -v`
- frontend: `cd frontend && npm test`
- build frontend: `cd frontend && npx next build`

Si la panne ne concerne que l'admin ou les jobs, tester d'abord les routes admin et le scheduler.

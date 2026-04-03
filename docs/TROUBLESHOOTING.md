# Troubleshooting

> Guide rapide pour diagnostiquer les pannes les plus frÃ©quentes en dÃ©veloppement et en exploitation lÃ©gÃ¨re.

---

## Backend ne dÃ©marre pas

VÃ©rifier:

- la configuration `.env.local`
- la disponibilitÃ© de `DATABASE_URL`
- les imports rÃ©cents dans `src/api/main.py`
- les traces liÃ©es au scheduler dans les logs de dÃ©marrage

Commandes utiles:

```bash
python manage.py run
python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect(); print('OK')"
```

---

## Frontend ne parle plus Ã  l'API

VÃ©rifier:

- `NEXT_PUBLIC_API_URL`
- que le backend Ã©coute bien sur `http://localhost:8000`
- les rÃ¨gles CORS
- l'Ã©tat d'authentification et le token cÃ´tÃ© frontend

---

## Scheduler ou jobs absents

SymptÃ´mes:

- page `/admin/jobs` vide
- aucun job visible
- notifications planifiÃ©es non envoyÃ©es

VÃ©rifications:

- dÃ©marrage du scheduler dans `src/api/main.py`
- configuration `DÃ©marreurCron` dans `src/services/core/cron/jobs.py`
- logs backend au boot

---

## Cache incohÃ©rent

SymptÃ´mes:

- donnÃ©es qui semblent figÃ©es
- suggestions qui ne se recalculent pas
- tableau de bord en retard aprÃ¨s mutation

Actions:

- utiliser `/admin/services`
- purger par motif avant de vider tout le cache
- vÃ©rifier si le flux concernÃ© utilise `@avec_cache`

---

## Notifications non reÃ§ues

VÃ©rifier:

- abonnement push actif
- prÃ©fÃ©rences de canaux par catÃ©gorie
- secrets email ou Telegram selon le canal visÃ©
- test canal depuis l'admin

---

## Garmin ou Google Calendar ne synchronisent pas

VÃ©rifier:

- connexions externes rÃ©ellement actives en base
- refresh tokens valides
- exceptions par profil dans les logs backend
- exÃ©cution manuelle du job correspondant depuis l'admin

---

## Automations inactives

VÃ©rifier:

- qu'il existe des rÃ¨gles actives en base
- que le dÃ©clencheur utilisÃ© est supportÃ© par le moteur
- que l'action visÃ©e est prise en charge
- que le job `automations_runner` tourne bien

---

## Page admin en erreur

VÃ©rifier:

- que l'utilisateur a bien le rÃ´le `admin`
- que l'API admin rÃ©pond
- que les endpoints `jobs`, `services/health` et `users` ne renvoient pas d'erreur
- le composant d'erreur `frontend/src/app/(app)/admin/error.tsx`

---

## Tests cassÃ©s aprÃ¨s mise Ã  jour docs ou code

VÃ©rifier:

- backend: `pytest -v`
- frontend: `cd frontend && npm test`
- build frontend: `cd frontend && npx next build`

Si la panne ne concerne que l'admin ou les jobs, tester d'abord les routes admin et le scheduler.

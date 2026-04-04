# Security

Reference securite applicative (backend + frontend).

## Authentification

- JWT Bearer sur l'API (`Authorization: Bearer <token>`).
- Dependances FastAPI centralisees: `require_auth`, `require_role`.
- Validation token: `src/api/auth.py` + `src/api/dependencies.py`.
- Mode dev autorise uniquement sur liste blanche d'environnements (`development`, `dev`, `local`, `test`, `testing`).

## Autorisation

- Endpoints sensibles proteges par role (ex: admin).
- Endpoint metriques Prometheus reserve admin.
- Journalisation des evenements de securite en cas d'echec auth/role.

## Protection API

- Rate limiting middleware:
  - Standard: 60 req/min
  - IA: 10 req/min
- Security headers middleware actif.
- CORS configure explicitement dans `src/api/main.py`.
- ETag middleware pour cache HTTP et reduction de charge.

## Base de donnees

- Politique SQL-first avec RLS activee dans les scripts schema.
- Sessions DB centralisees via context managers/decorateurs.
- Pas de creation manuelle d'engine/session dans les routes.

## Secrets

- Variables d'environnement via `.env.local`/env systeme.
- Aucun secret hardcode en production.
- Rotation des cles recommandee pour: JWT, VAPID, webhooks, OAuth fournisseurs.

## Integrations externes

- Telegram webhook avec verification `hub.verify_token`.
- Webhooks sortants executes avec gestion d'erreurs resiliente.
- Sentry active via DSN uniquement si configure.
- Extension Chrome Carrefour Drive: permissions a garder minimales et revue manuelle a chaque evolution du `manifest.json`.

## Revue periodique

- Revoir les dependances backend/frontend a chaque sprint de maintenance (updates de securite, breaking changes, paquets non maintenus).
- Verifier les permissions OAuth / webhooks / extension navigateur apres chaque nouvelle integration.
- Revalider les headers de securite et les secrets critiques apres toute modification de config ou de deploiement.

## Checklist rapide

- Verifier `ENVIRONMENT` en production.
- Verifier la presence des secrets critiques.
- Verifier les roles admin minimaux.
- Verifier CORS et rate limits apres ajout d'endpoint.


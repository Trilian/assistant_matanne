# Monitoring

Reference monitoring, metriques et observabilite.

## Stack

- Prometheus endpoint: `GET /metrics/prometheus`.
- Sentry: active si `SENTRY_DSN` est configure.
- Health checks: endpoints sante API + checks metiers.
- Metrics middleware: compteurs/latence/repartition erreurs.

## Endpoint Prometheus

- Route: `src/api/prometheus.py`
- Protection: role admin requis.
- Expose notamment:
  - `matanne_http_requests_total`
  - `matanne_http_request_duration_seconds`
  - `matanne_rate_limit_hits_total`
  - `matanne_ai_requests_total`
  - `matanne_ai_tokens_used_total`
  - `matanne_uptime_seconds`

## Health

- Health API de base via routes sante.
- Verification globale via modules monitoring core.
- A utiliser pour readiness/liveness checks.

## Logs

- Logs structures backend (niveau configurable).
- Event bus: audit logs des evenements emis.
- Jobs cron: logs d'execution + erreurs.

## Alerting recommande

- Taux d'erreurs HTTP 5xx.
- Latence p95/p99.
- Rate-limit hits anormaux.
- Echecs cron repetes.
- Consommation tokens IA.

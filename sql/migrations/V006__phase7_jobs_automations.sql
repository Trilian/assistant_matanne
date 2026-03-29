-- ─────────────────────────────────────────────────────────────────────────────
-- Migration V006 — Phase 7 : Jobs & Automatisations
-- Date : 2026-03-29
-- Réf.  : ADM-4/J2/J5 (historique jobs + métriques durée)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS job_executions (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    job_name VARCHAR(255),
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_ms INTEGER,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    output_logs TEXT,
    triggered_by_user_id VARCHAR(255),
    triggered_by_user_role VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_job_executions_job_id
    ON job_executions(job_id);

CREATE INDEX IF NOT EXISTS ix_job_executions_status
    ON job_executions(status);

CREATE INDEX IF NOT EXISTS ix_job_executions_started_at
    ON job_executions(started_at DESC);

CREATE INDEX IF NOT EXISTS ix_job_executions_created_at
    ON job_executions(created_at DESC);

CREATE INDEX IF NOT EXISTS ix_job_executions_job_started
    ON job_executions(job_id, started_at DESC);

COMMENT ON TABLE job_executions IS
    'Historique des exécutions cron et manuelles (admin) avec durée et erreurs.';

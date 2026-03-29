-- ─────────────────────────────────────────────────────────────────────────────
-- Migration V004 — Sprint 11 F4 : table logs_securite + RLS admin-only
-- Date : 2026-03-29
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS logs_securite (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    ip VARCHAR(45),
    user_agent VARCHAR(500),
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_logs_securite_user_id ON logs_securite(user_id);
CREATE INDEX IF NOT EXISTS ix_logs_securite_event_type ON logs_securite(event_type);
CREATE INDEX IF NOT EXISTS ix_logs_securite_created_at ON logs_securite(created_at);
CREATE INDEX IF NOT EXISTS ix_logs_securite_event_type_created_at ON logs_securite(event_type, created_at);
CREATE INDEX IF NOT EXISTS ix_logs_securite_user_created_at ON logs_securite(user_id, created_at);

ALTER TABLE IF EXISTS public.logs_securite ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_access_logs_securite" ON public.logs_securite;
CREATE POLICY "service_role_access_logs_securite"
    ON public.logs_securite
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "authenticated_deny_logs_securite" ON public.logs_securite;
CREATE POLICY "authenticated_deny_logs_securite"
    ON public.logs_securite
    FOR ALL TO authenticated
    USING (false)
    WITH CHECK (false);

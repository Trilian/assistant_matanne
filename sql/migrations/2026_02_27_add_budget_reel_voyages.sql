-- Migration: add budget_reel to voyages
-- Date: 2026-02-27
BEGIN;
ALTER TABLE IF EXISTS voyages
ADD COLUMN IF NOT EXISTS budget_reel double precision;
COMMIT;
-- Rollback notes:
-- ALTER TABLE voyages DROP COLUMN IF EXISTS budget_reel;

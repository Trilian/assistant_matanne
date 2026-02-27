-- Migration: add date_debut and date_fin to albums_famille
-- Date: 2026-02-27
BEGIN;
ALTER TABLE IF EXISTS albums_famille
ADD COLUMN IF NOT EXISTS date_debut date;
ALTER TABLE IF EXISTS albums_famille
ADD COLUMN IF NOT EXISTS date_fin date;
COMMIT;
-- Rollback notes:
-- ALTER TABLE albums_famille DROP COLUMN IF EXISTS date_debut;
-- ALTER TABLE albums_famille DROP COLUMN IF EXISTS date_fin;

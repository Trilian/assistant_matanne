-- Migration: add missing column `type_energie` to `releves_energie`
-- Idempotent: safe to run multiple times
BEGIN;
-- Add the column if it does not exist (default to 'electricite' for older rows)
ALTER TABLE IF EXISTS releves_energie
ADD COLUMN IF NOT EXISTS type_energie VARCHAR(50) DEFAULT 'electricite';
-- Ensure column is NOT NULL (set default previously to avoid NULLs)
ALTER TABLE IF EXISTS releves_energie
ALTER COLUMN type_energie
SET NOT NULL;
-- Create index on type if missing
CREATE INDEX IF NOT EXISTS idx_energie_type ON releves_energie(type_energie);
COMMIT;

-- Migration 010: Add updated_at column to recettes and modeles_courses
-- This fixes the PostgreSQL trigger error where the trigger expects updated_at

-- 1. Add updated_at to recettes
ALTER TABLE recettes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 2. Add updated_at to modeles_courses
ALTER TABLE modeles_courses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 3. Update any NULL values with modifie_le or NOW()
UPDATE recettes SET updated_at = COALESCE(modifie_le, NOW()) WHERE updated_at IS NULL;
UPDATE modeles_courses SET updated_at = COALESCE(modifie_le, NOW()) WHERE updated_at IS NULL;

-- 4. Make columns NOT NULL
ALTER TABLE recettes ALTER COLUMN updated_at SET NOT NULL;
ALTER TABLE modeles_courses ALTER COLUMN updated_at SET NOT NULL;

-- Verify the columns exist
SELECT column_name FROM information_schema.columns 
WHERE table_name IN ('recettes', 'modeles_courses') 
AND column_name = 'updated_at'
ORDER BY table_name;

-- =============================================================================
-- Migration: Add recette equilibre fields for meal planning
-- Date: 2026-02-01
-- Description: Add est_vegetarien and type_proteines columns to recettes table
--              for balanced meal planning functionality
-- =============================================================================

-- 1. Add est_vegetarien column for filtering vegetarian recipes
ALTER TABLE recettes 
ADD COLUMN est_vegetarien BOOLEAN NOT NULL DEFAULT false;

-- 2. Create index on est_vegetarien for fast filtering
CREATE INDEX idx_recettes_est_vegetarien ON recettes (est_vegetarien);

-- 3. Add type_proteines column for meal planning equilibration
-- Values: 'poisson', 'viande', 'volaille', 'vegetarien', 'mixte'
ALTER TABLE recettes 
ADD COLUMN type_proteines VARCHAR(100) NULL;

-- =============================================================================
-- Rollback script (in case of need):
-- =============================================================================
-- DROP INDEX IF EXISTS idx_recettes_est_vegetarien;
-- ALTER TABLE recettes DROP COLUMN IF EXISTS type_proteines;
-- ALTER TABLE recettes DROP COLUMN IF EXISTS est_vegetarien;

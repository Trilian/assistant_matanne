-- ============================================================================
-- Migration 023: Suppression des colonnes timestamp en double
-- Date: 20260220
-- Description: Supprime les colonnes updated_at redondantes dans recettes
--              et modeles_courses (remplacées par modifie_le)
-- ============================================================================
BEGIN;
-- Copier les données de updated_at vers modifie_le si modifie_le est NULL
UPDATE recettes
SET modifie_le = updated_at
WHERE modifie_le IS NULL
    AND updated_at IS NOT NULL;
-- Supprimer updated_at de recettes
ALTER TABLE IF EXISTS recettes DROP COLUMN IF EXISTS updated_at;
-- Supprimer updated_at de modeles_courses
ALTER TABLE IF EXISTS modeles_courses DROP COLUMN IF EXISTS updated_at;
COMMIT;

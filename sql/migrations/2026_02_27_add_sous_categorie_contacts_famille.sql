-- Migration: add sous_categorie to contacts_famille
-- Date: 2026-02-27
-- Adds a nullable varchar(100) column `sous_categorie` to the contacts_famille table
BEGIN;
-- Add column if it does not exist (safe for idempotent runs)
ALTER TABLE IF EXISTS contacts_famille
ADD COLUMN IF NOT EXISTS sous_categorie varchar(100);
COMMIT;
-- Rollback notes:
-- To remove the column if necessary:
-- ALTER TABLE contacts_famille DROP COLUMN IF EXISTS sous_categorie;

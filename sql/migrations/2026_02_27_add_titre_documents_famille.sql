-- Migration: add titre to documents_famille and backfill from fichier_nom if present
-- Date: 2026-02-27
BEGIN;
ALTER TABLE IF EXISTS documents_famille
ADD COLUMN IF NOT EXISTS titre varchar(200);
-- If the table has a 'fichier_nom' column, copy values into 'titre' where titre is null
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'documents_famille'
        AND column_name = 'fichier_nom'
) THEN EXECUTE 'UPDATE documents_famille SET titre = fichier_nom WHERE titre IS NULL AND fichier_nom IS NOT NULL';
END IF;
END $$;
COMMIT;
-- Rollback notes:
-- ALTER TABLE documents_famille DROP COLUMN IF EXISTS titre;

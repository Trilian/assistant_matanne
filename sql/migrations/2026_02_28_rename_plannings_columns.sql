-- 2026-02-28 - Rename and backfill plannings columns to match SQLAlchemy model
-- Safety: uses IF NOT EXISTS / existence checks, non-destructive updates.
-- Note: keep original columns (statut, prompt_ia) until post-checks; DO NOT DROP automatically.
BEGIN;
-- 1) Add `nom` if missing and backfill with a deterministic placeholder
ALTER TABLE plannings
ADD COLUMN IF NOT EXISTS nom VARCHAR(200);
UPDATE plannings
SET nom = ('Planning ' || id::text)
WHERE nom IS NULL;
-- 2) Rename semaine_du -> semaine_debut if present
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'plannings'
        AND column_name = 'semaine_du'
) THEN
ALTER TABLE plannings
    RENAME COLUMN semaine_du TO semaine_debut;
END IF;
END $$;
-- 3) Rename semaine_au -> semaine_fin if present
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'plannings'
        AND column_name = 'semaine_au'
) THEN
ALTER TABLE plannings
    RENAME COLUMN semaine_au TO semaine_fin;
END IF;
END $$;
-- 4) Add `actif` boolean and backfill from `statut` if available
ALTER TABLE plannings
ADD COLUMN IF NOT EXISTS actif BOOLEAN DEFAULT FALSE;
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'plannings'
        AND column_name = 'statut'
) THEN -- Conservative mapping: consider common 'active' statuses as TRUE
UPDATE plannings
SET actif = TRUE
WHERE statut IN ('actif', 'active', 'publie', 'publié', 'published');
END IF;
END $$;
-- 5) Add `notes` and copy `prompt_ia` if present
ALTER TABLE plannings
ADD COLUMN IF NOT EXISTS notes TEXT;
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'plannings'
        AND column_name = 'prompt_ia'
) THEN
UPDATE plannings
SET notes = prompt_ia
WHERE notes IS NULL;
END IF;
END $$;
-- 6) Ensure index on semaine_debut exists
CREATE INDEX IF NOT EXISTS ix_plannings_semaine_debut ON plannings(semaine_debut);
COMMIT;
-- Rollback notes:
-- This file intentionally does not DROP/RENAME original columns back.
-- To rollback: manually reverse each step (rename columns back, remove added columns)

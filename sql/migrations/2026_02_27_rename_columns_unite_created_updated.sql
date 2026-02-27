-- Migration: rename columns to French attribute names and add new child fields
-- Up: apply changes
BEGIN;
-- 1) Rename ingredients.unite_mesure -> unite (if exists)
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'ingredients'
        AND column_name = 'unite_mesure'
) THEN
ALTER TABLE ingredients
    RENAME COLUMN unite_mesure TO unite;
END IF;
END $$;
-- 2) Rename taches_entretien.created_at -> cree_le and updated_at -> modifie_le
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'taches_entretien'
        AND column_name = 'created_at'
) THEN
ALTER TABLE taches_entretien
    RENAME COLUMN created_at TO cree_le;
END IF;
IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'taches_entretien'
        AND column_name = 'updated_at'
) THEN
ALTER TABLE taches_entretien
    RENAME COLUMN updated_at TO modifie_le;
END IF;
END $$;
-- 3) Add new columns to profils_enfants: taille_vetements (jsonb) and pointure (varchar)
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'profils_enfants'
        AND column_name = 'taille_vetements'
) THEN
ALTER TABLE profils_enfants
ADD COLUMN taille_vetements jsonb DEFAULT '{}'::jsonb;
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'profils_enfants'
        AND column_name = 'pointure'
) THEN
ALTER TABLE profils_enfants
ADD COLUMN pointure varchar(50);
END IF;
END $$;
COMMIT;
-- Down: revert changes (best-effort)
-- To roll back, reverse the above operations. Note: renaming back will fail if the target name already exists.
-- Example rollback statements (execute manually with caution):
-- ALTER TABLE ingredients RENAME COLUMN unite TO unite_mesure;
-- ALTER TABLE taches_entretien RENAME COLUMN cree_le TO created_at;
-- ALTER TABLE taches_entretien RENAME COLUMN modifie_le TO updated_at;
-- ALTER TABLE profils_enfants DROP COLUMN IF EXISTS taille_vetements;
-- ALTER TABLE profils_enfants DROP COLUMN IF EXISTS pointure;

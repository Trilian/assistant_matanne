BEGIN;
-- Rename old english columns if present (Postgres doesn't support RENAME COLUMN IF EXISTS)
DO $$ BEGIN IF EXISTS(
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'preferences_notifications'
        AND column_name = 'created_at'
) THEN EXECUTE 'ALTER TABLE preferences_notifications RENAME COLUMN created_at TO cree_le';
END IF;
IF EXISTS(
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'preferences_notifications'
        AND column_name = 'updated_at'
) THEN EXECUTE 'ALTER TABLE preferences_notifications RENAME COLUMN updated_at TO modifie_le';
END IF;
END;
$$;
ALTER TABLE IF EXISTS preferences_notifications
ADD COLUMN IF NOT EXISTS cree_le timestamptz DEFAULT now(),
    ADD COLUMN IF NOT EXISTS modifie_le timestamptz DEFAULT now();
CREATE OR REPLACE FUNCTION update_modifie_le_column() RETURNS TRIGGER AS $$ BEGIN NEW.modifie_le = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_trigger
    WHERE tgname = 'trg_update_modifie_le_preferences_notifications'
) THEN CREATE TRIGGER trg_update_modifie_le_preferences_notifications BEFORE
UPDATE ON preferences_notifications FOR EACH ROW EXECUTE FUNCTION update_modifie_le_column();
END IF;
END;
$$;
COMMIT;

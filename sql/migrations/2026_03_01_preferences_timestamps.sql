-- Idempotent migration: ensure french timestamp columns exist and are kept up-to-date
BEGIN;

-- Rename old english columns if present
ALTER TABLE IF EXISTS preferences_notifications
  RENAME COLUMN IF EXISTS created_at TO cree_le;

ALTER TABLE IF EXISTS preferences_notifications
  RENAME COLUMN IF EXISTS updated_at TO modifie_le;

-- Add columns if missing
ALTER TABLE IF EXISTS preferences_notifications
  ADD COLUMN IF NOT EXISTS cree_le timestamptz DEFAULT now(),
  ADD COLUMN IF NOT EXISTS modifie_le timestamptz DEFAULT now();

-- Create or replace function to update modifie_le on UPDATE
CREATE OR REPLACE FUNCTION update_modifie_le_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.modifie_le = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger
    WHERE tgname = 'trg_update_modifie_le_preferences_notifications'
  ) THEN
    CREATE TRIGGER trg_update_modifie_le_preferences_notifications
    BEFORE UPDATE ON preferences_notifications
    FOR EACH ROW EXECUTE FUNCTION update_modifie_le_column();
  END IF;
END;
$$;

COMMIT;

-- Migration: Rename date_cuisson → date_preparation + add feedback column
-- Table: historique_recettes

-- Rename column (idempotent check)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'historique_recettes' AND column_name = 'date_cuisson'
    ) THEN
        ALTER TABLE historique_recettes RENAME COLUMN date_cuisson TO date_preparation;
    END IF;
END $$;

-- Add feedback column if not present
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'historique_recettes' AND column_name = 'feedback'
    ) THEN
        ALTER TABLE historique_recettes
            ADD COLUMN feedback VARCHAR(20) DEFAULT 'neutral';

        ALTER TABLE historique_recettes
            ADD CONSTRAINT ck_historique_feedback_valide
            CHECK (feedback IS NULL OR feedback IN ('like', 'dislike', 'neutral'));
    END IF;
END $$;

-- Update index if needed (drop old, create new)
DROP INDEX IF EXISTS ix_historique_recettes_date_cuisson;
CREATE INDEX IF NOT EXISTS ix_historique_recettes_date_preparation
    ON historique_recettes (date_preparation);

-- Migration 003: Add cree_le column to historique_recettes
-- This adds the missing timestamp column that the HistoriqueRecette model expects

-- Check if column exists before adding (prevents errors if already added)
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name='historique_recettes' AND column_name='cree_le'
  ) THEN
    ALTER TABLE historique_recettes ADD COLUMN cree_le TIMESTAMP NOT NULL DEFAULT NOW();
  END IF;
END $$;

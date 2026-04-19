-- Migration: ajout colonne preparations_simples dans sessions_batch_cooking
-- Date: 2026-04-19
-- Objectif: stocker les préparations sans recette associée (accompagnements texte libre)

ALTER TABLE sessions_batch_cooking
    ADD COLUMN IF NOT EXISTS preparations_simples JSONB NOT NULL DEFAULT '[]'::jsonb;

COMMENT ON COLUMN sessions_batch_cooking.preparations_simples IS
    'Liste de préparations sans recette associée (légumes vapeur, carottes râpées, etc.)';

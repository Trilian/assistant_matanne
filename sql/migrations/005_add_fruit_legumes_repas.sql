-- Migration 005: Ajout des champs fruit et legumes sur la table repas
-- Date: 2026-04-15
-- Objectif:
--   - fruit: fruit entier ou compote au goûter (texte libre, contrainte IA uniquement)
--   - legumes: légumes accompagnement pour déjeuner/dîner (texte libre)

ALTER TABLE repas ADD COLUMN IF NOT EXISTS fruit VARCHAR(200);
ALTER TABLE repas ADD COLUMN IF NOT EXISTS legumes VARCHAR(200);

COMMENT ON COLUMN repas.fruit IS 'Fruit entier ou compote (goûter) — texte libre, ex: Pomme, Compote poire';
COMMENT ON COLUMN repas.legumes IS 'Légumes accompagnement (déjeuner/dîner) — texte libre, ex: Haricots verts, Courgettes sautées';

-- Migration: add entrée/dessert/dessert_jules columns to repas table
-- Supports full meal structure: entrée → plat → dessert (+ dessert Jules)
BEGIN;

-- Entrée (texte libre + FK optionnelle)
ALTER TABLE IF EXISTS repas
ADD COLUMN IF NOT EXISTS entree VARCHAR(200);

ALTER TABLE IF EXISTS repas
ADD COLUMN IF NOT EXISTS entree_recette_id INTEGER;

ALTER TABLE IF EXISTS repas
ADD CONSTRAINT fk_repas_entree_recette
FOREIGN KEY (entree_recette_id) REFERENCES recettes(id) ON DELETE SET NULL;

-- Dessert famille (texte libre + FK optionnelle)
ALTER TABLE IF EXISTS repas
ADD COLUMN IF NOT EXISTS dessert VARCHAR(200);

ALTER TABLE IF EXISTS repas
ADD COLUMN IF NOT EXISTS dessert_recette_id INTEGER;

ALTER TABLE IF EXISTS repas
ADD CONSTRAINT fk_repas_dessert_recette
FOREIGN KEY (dessert_recette_id) REFERENCES recettes(id) ON DELETE SET NULL;

-- Dessert Jules (texte libre + FK optionnelle)
ALTER TABLE IF EXISTS repas
ADD COLUMN IF NOT EXISTS dessert_jules VARCHAR(200);

ALTER TABLE IF EXISTS repas
ADD COLUMN IF NOT EXISTS dessert_jules_recette_id INTEGER;

ALTER TABLE IF EXISTS repas
ADD CONSTRAINT fk_repas_dessert_jules_recette
FOREIGN KEY (dessert_jules_recette_id) REFERENCES recettes(id) ON DELETE SET NULL;

COMMIT;

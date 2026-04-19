-- Migration: Supprimer les champs instructions Jules du planning
-- Les instructions de préparation Jules sont désormais dans versions_recette (type_version='jules')
-- générées automatiquement lors de la création d'un planning si jules_present=True.
-- dessert_jules et dessert_jules_recette_id sont conservés (concept planification, pas instructions).

ALTER TABLE repas
    DROP COLUMN IF EXISTS plat_jules,
    DROP COLUMN IF EXISTS notes_jules,
    DROP COLUMN IF EXISTS adaptation_auto;

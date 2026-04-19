-- Migration : supprimer la colonne vestigiale articles_data de modeles_courses
-- La table articles_modeles (relation relationnelle) est le seul stockage utilisé
-- articles_data (JSONB) n'est lu ni écrit par aucun service ou route.

ALTER TABLE modeles_courses DROP COLUMN IF EXISTS articles_data;

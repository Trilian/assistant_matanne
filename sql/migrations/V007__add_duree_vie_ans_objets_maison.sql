-- Migration V007: Ajout colonne duree_vie_ans sur objets_maison
-- Durée de vie estimée de l'appareil (en années), distincte de la garantie.

ALTER TABLE objets_maison
    ADD COLUMN IF NOT EXISTS duree_vie_ans INTEGER;

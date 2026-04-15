-- Migration 005: Ajout colonne couverture_jours sur config_batch_cooking
-- Stocke le mapping jour_batch → jours couverts pour le filtrage des recettes
-- Ex: {"2": [2, 3, 4], "6": [6, 0, 1, 2]}
-- Mercredi (2) prépare pour mer soir + jeu + ven
-- Dimanche (6) prépare pour dim soir + lun + mar + mer midi

ALTER TABLE config_batch_cooking
    ADD COLUMN IF NOT EXISTS couverture_jours JSONB;

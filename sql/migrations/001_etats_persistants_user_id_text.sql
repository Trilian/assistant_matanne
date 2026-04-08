-- Migration: Changer user_id UUID → VARCHAR(255) dans etats_persistants
-- Raison: le code utilise des valeurs non-UUID comme "global", "default",
--         et des event_ids comme "planning.modifie_1775655694650".
--
-- À exécuter dans Supabase SQL Editor ou via psql.

ALTER TABLE etats_persistants
    ALTER COLUMN user_id TYPE VARCHAR(255) USING user_id::text;

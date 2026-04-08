-- Migration: Ajouter les colonnes manquantes dans elements_jardin
-- Raison: Le modèle SQLAlchemy référence ces colonnes mais elles
--         n'existent pas dans le schéma DB actuel.
--
-- Erreurs corrigées:
--   - column elements_jardin.location does not exist
--     → "location" est mappé sur la colonne "emplacement" (déjà présente)
--     → Aucune migration nécessaire pour "location"
--
--   - column elements_jardin.date_recolte_prevue does not exist
--     → Ajout de la colonne date_recolte_prevue
--
-- À exécuter dans Supabase SQL Editor ou via psql.

ALTER TABLE elements_jardin
    ADD COLUMN IF NOT EXISTS date_recolte_prevue DATE;

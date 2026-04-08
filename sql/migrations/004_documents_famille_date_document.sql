-- Migration: Ajouter la colonne date_document à documents_famille
-- Raison: Le modèle SQLAlchemy DocumentFamille référence date_document (Date)
--         mais cette colonne n'existe pas dans le schéma DB actuel.
--
-- Erreur corrigée:
--   - column documents_famille.date_document does not exist
--
-- À exécuter dans Supabase SQL Editor ou via psql.

ALTER TABLE documents_famille
    ADD COLUMN IF NOT EXISTS date_document DATE;

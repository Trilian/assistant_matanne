-- Migration: Ajout des colonnes Jules et contexte au tableau repas
-- Date: 2026-04-07
-- Raison: Colonnes présentes dans le modèle SQLAlchemy mais absentes du schéma initial

ALTER TABLE repas
    ADD COLUMN IF NOT EXISTS plat_jules TEXT,
    ADD COLUMN IF NOT EXISTS notes_jules TEXT,
    ADD COLUMN IF NOT EXISTS adaptation_auto BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS contexte_meteo VARCHAR(50);

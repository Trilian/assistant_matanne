-- Migration V006: Ajout des colonnes 2FA sur profils_utilisateurs
-- Les colonnes two_factor_enabled, two_factor_secret et backup_codes
-- sont présentes dans le modèle SQLAlchemy mais absentes du schéma DB.

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS two_factor_secret VARCHAR(255),
    ADD COLUMN IF NOT EXISTS backup_codes JSONB;

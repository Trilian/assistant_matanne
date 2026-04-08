-- Migration V002 : Colonnes manquantes sur anniversaires_famille
-- Le modèle SQLAlchemy référence idees_cadeaux et actif qui n'existent pas en DB.

ALTER TABLE anniversaires_famille
    ADD COLUMN IF NOT EXISTS idees_cadeaux TEXT,
    ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT true;

CREATE INDEX IF NOT EXISTS ix_anniversaires_actif ON anniversaires_famille(actif);

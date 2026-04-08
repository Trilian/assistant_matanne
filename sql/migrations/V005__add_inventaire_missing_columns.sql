-- Migration V005 : Colonnes manquantes sur inventaire
-- Le modèle SQLAlchemy contient date_entree mais la table DB de production ne l'a pas.
-- Fix pour : column inventaire.date_entree does not exist → 500

ALTER TABLE inventaire
    ADD COLUMN IF NOT EXISTS date_entree DATE NOT NULL DEFAULT CURRENT_DATE;

CREATE INDEX IF NOT EXISTS ix_inventaire_date_entree ON inventaire(date_entree);

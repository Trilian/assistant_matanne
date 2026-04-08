-- Migration V007 : Ajout de rappel_jours_avant sur evenements_familiaux
-- La colonne est présente dans le modèle SQLAlchemy EvenementFamilial
-- mais absente du schéma DB en production.
-- Cause : 503 sur GET /api/v1/famille/evenements

ALTER TABLE evenements_familiaux
    ADD COLUMN IF NOT EXISTS rappel_jours_avant INTEGER NOT NULL DEFAULT 7;

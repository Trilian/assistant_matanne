-- Migration: Ajouter les colonnes manquantes détectées en production
-- Raison: Les modèles SQLAlchemy référencent ces colonnes mais elles
--         n'existent pas dans le schéma DB actuel.
--
-- Erreurs corrigées:
--   - column routines.frequence does not exist
--   - column elements_jardin.type does not exist
--   - column documents_famille.fichier_nom does not exist
--   - column documents_famille.actif does not exist
--
-- À exécuter dans Supabase SQL Editor ou via psql.

-- routines.frequence
ALTER TABLE routines
    ADD COLUMN IF NOT EXISTS frequence VARCHAR(50) NOT NULL DEFAULT 'quotidien';

-- elements_jardin.type
ALTER TABLE elements_jardin
    ADD COLUMN IF NOT EXISTS type VARCHAR(100) NOT NULL DEFAULT 'plante';

-- documents_famille.fichier_nom
ALTER TABLE documents_famille
    ADD COLUMN IF NOT EXISTS fichier_nom VARCHAR(200);

-- documents_famille.actif
ALTER TABLE documents_famille
    ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT TRUE;

CREATE INDEX IF NOT EXISTS ix_documents_famille_actif ON documents_famille (actif);

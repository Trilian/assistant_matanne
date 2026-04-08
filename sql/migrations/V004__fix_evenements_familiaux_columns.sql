-- Migration V004 : Synchronisation evenements_familiaux avec le modèle ORM EvenementFamilial
-- Le modèle ORM utilise date_evenement (DATE), actif (BOOLEAN), notes (TEXT)
-- mais la table DB de production a date_debut (TIMESTAMPTZ), pas d'actif, description.
-- Fix pour : /famille/aujourd-hui-histoire → 503

-- Ajouter date_evenement à partir de date_debut
ALTER TABLE evenements_familiaux
    ADD COLUMN IF NOT EXISTS date_evenement DATE;

UPDATE evenements_familiaux
SET date_evenement = date_debut::DATE
WHERE date_evenement IS NULL;

ALTER TABLE evenements_familiaux
    ALTER COLUMN date_evenement SET DEFAULT CURRENT_DATE;

-- Ajouter actif (toutes les lignes existantes sont considérées actives)
ALTER TABLE evenements_familiaux
    ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT TRUE;

-- Ajouter notes (copie de description pour conserver les données existantes)
ALTER TABLE evenements_familiaux
    ADD COLUMN IF NOT EXISTS notes TEXT;

UPDATE evenements_familiaux
SET notes = description
WHERE notes IS NULL AND description IS NOT NULL;

-- Index utiles pour les requêtes par jour/mois
CREATE INDEX IF NOT EXISTS ix_evenements_familiaux_date_evenement
    ON evenements_familiaux(date_evenement);

CREATE INDEX IF NOT EXISTS ix_evenements_familiaux_actif
    ON evenements_familiaux(actif);

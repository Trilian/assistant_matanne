-- Migration V008: Colonnes manquantes sur plusieurs tables
-- Correction des divergences modèles SQLAlchemy vs schéma DB de production.

-- evenements_familiaux : colonne rappel_jours_avant
ALTER TABLE evenements_familiaux
    ADD COLUMN IF NOT EXISTS rappel_jours_avant INTEGER NOT NULL DEFAULT 7;

-- routines : colonne categorie
ALTER TABLE routines
    ADD COLUMN IF NOT EXISTS categorie VARCHAR(100);

CREATE INDEX IF NOT EXISTS ix_routines_categorie ON routines(categorie);

-- projets : colonnes dates manquantes
ALTER TABLE projets
    ADD COLUMN IF NOT EXISTS date_debut DATE,
    ADD COLUMN IF NOT EXISTS date_fin_prevue DATE,
    ADD COLUMN IF NOT EXISTS date_fin_reelle DATE;

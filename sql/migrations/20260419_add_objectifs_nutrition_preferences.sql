-- Migration : ajouter les objectifs nutritionnels quotidiens configurables
-- Permet de remplacer les constantes hardcodées dans le frontend nutrition/page.tsx

ALTER TABLE preferences_utilisateurs
    ADD COLUMN IF NOT EXISTS objectif_calories INTEGER NOT NULL DEFAULT 2000,
    ADD COLUMN IF NOT EXISTS objectif_proteines INTEGER NOT NULL DEFAULT 60,
    ADD COLUMN IF NOT EXISTS objectif_lipides INTEGER NOT NULL DEFAULT 70,
    ADD COLUMN IF NOT EXISTS objectif_glucides INTEGER NOT NULL DEFAULT 260;

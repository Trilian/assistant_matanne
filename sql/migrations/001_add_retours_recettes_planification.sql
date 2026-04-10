-- Migration 001: Ajout des colonnes de planification sur retours_recettes
-- Ces colonnes permettent de suivre si une recette est planifiée cette semaine.
-- Elles sont requises par le modèle ORM RetourRecette et les routes de planification.

ALTER TABLE retours_recettes
    ADD COLUMN IF NOT EXISTS planifie_cette_semaine BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS date_planifie TIMESTAMP WITH TIME ZONE;

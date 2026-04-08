-- Migration V003 : Ajout de la colonne heure_debut dans activites_famille
-- La colonne est définie dans le modèle SQLAlchemy mais absente de la DB de production.
-- Fix pour : ScoreBienEtreService.calculer_score → 500/503 et /score-bienetre.

ALTER TABLE activites_famille
    ADD COLUMN IF NOT EXISTS heure_debut TIME;

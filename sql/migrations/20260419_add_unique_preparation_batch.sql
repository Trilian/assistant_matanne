-- Migration : index d'unicité partiel sur preparations_batch(session_id, recette_id)
-- Empêche les doublons de préparation pour la même recette dans la même session.
-- L'index est partiel : ne s'applique que si les deux colonnes sont non NULL.

CREATE UNIQUE INDEX IF NOT EXISTS uq_prep_session_recette
    ON preparations_batch (session_id, recette_id)
    WHERE session_id IS NOT NULL AND recette_id IS NOT NULL;

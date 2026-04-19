-- Migration: ajout colonne user_id dans historique_achats
-- Date: 2026-04-19
-- Objectif: isoler les données d'apprentissage IA par utilisateur pour éviter
--           la contamination des prédictions entre utilisateurs différents.

ALTER TABLE historique_achats
    ADD COLUMN IF NOT EXISTS user_id VARCHAR(100);

COMMENT ON COLUMN historique_achats.user_id IS
    'Identifiant de l''utilisateur propriétaire (NULL = données legacy partagées)';

CREATE INDEX IF NOT EXISTS ix_historique_achats_user_id ON historique_achats(user_id);
CREATE INDEX IF NOT EXISTS ix_historique_achats_user_nom ON historique_achats(user_id, article_nom);

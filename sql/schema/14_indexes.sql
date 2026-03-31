-- ============================================================================
-- ASSISTANT MATANNE — Index supplémentaires
-- ============================================================================
-- Index composites et index de performance ajoutés après V005.
-- La majorité des index sont inline avec les CREATE TABLE dans les fichiers
-- de domaine (03-11). Ce fichier contient uniquement les index additionnels.
-- ============================================================================

-- Consolidation V005 : Index composites porte-parole performance
CREATE INDEX IF NOT EXISTS ix_repas_planning_date ON repas(planning_id, date_repas);
CREATE INDEX IF NOT EXISTS ix_repas_planning_type ON repas(planning_id, type_repas);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_achete ON articles_courses(liste_id, achete);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_priorite ON articles_courses(liste_id, priorite);
CREATE INDEX IF NOT EXISTS ix_inventaire_peremption_quantite ON inventaire(date_peremption, quantite)
    WHERE date_peremption IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_ingredient_date ON historique_inventaire(ingredient_id, date_modification);
CREATE INDEX IF NOT EXISTS ix_listes_courses_statut_semaine ON listes_courses(statut, semaine_du);
CREATE INDEX IF NOT EXISTS ix_plannings_actif_semaine ON plannings(actif, semaine_debut) WHERE actif = TRUE;

-- Index migration V001-V004 (absorbés)
CREATE INDEX IF NOT EXISTS idx_articles_inventaire_peremption
    ON articles_inventaire(date_peremption);
CREATE INDEX IF NOT EXISTS idx_repas_planning_planning_date
    ON repas_planning(planning_id, date_repas);
CREATE INDEX IF NOT EXISTS idx_historique_actions_user_date
    ON historique_actions(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_paris_sportifs_statut_user
    ON paris_sportifs(statut, user_id);

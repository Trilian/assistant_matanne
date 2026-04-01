-- ============================================================================
-- ASSISTANT MATANNE — Index supplémentaires & contraintes CHECK
-- ============================================================================
-- Index composites et index de performance ajoutés après V005.
-- Contraintes CHECK pour les enums VARCHAR (V005 absorbé).
-- La majorité des index sont inline avec les CREATE TABLE dans les fichiers
-- de domaine (03-11). Ce fichier contient uniquement les index additionnels.
-- ============================================================================

-- Consolidation V005 : Index composites performance
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

-- ============================================================================
-- V005 : Contraintes CHECK pour les enums VARCHAR clés
-- ============================================================================
ALTER TABLE repas
    ADD CONSTRAINT IF NOT EXISTS ck_repas_type_repas
    CHECK (type_repas IN (
        'petit_dejeuner', 'brunch', 'dejeuner', 'gouter', 'diner',
        'collation', 'autre'
    ));

ALTER TABLE listes_courses
    ADD CONSTRAINT IF NOT EXISTS ck_listes_courses_statut
    CHECK (statut IN ('active', 'en_cours', 'completee', 'archivee', 'annulee'));

ALTER TABLE recettes
    ADD CONSTRAINT IF NOT EXISTS ck_recettes_difficulte
    CHECK (difficulte IN ('facile', 'moyen', 'difficile', 'expert'));

ALTER TABLE recettes
    ADD CONSTRAINT IF NOT EXISTS ck_recettes_saison
    CHECK (saison IN ('printemps', 'ete', 'automne', 'hiver', 'toute_annee', 'toute_année'));

ALTER TABLE articles_courses
    ADD CONSTRAINT IF NOT EXISTS ck_articles_courses_priorite
    CHECK (priorite IN ('haute', 'moyenne', 'basse', 'urgente'));

ALTER TABLE articles_modeles
    ADD CONSTRAINT IF NOT EXISTS ck_articles_modeles_priorite
    CHECK (priorite IN ('haute', 'moyenne', 'basse', 'urgente'));

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sessions_batch_cooking') THEN
        ALTER TABLE sessions_batch_cooking
            ADD CONSTRAINT IF NOT EXISTS ck_batch_statut
            CHECK (statut IN ('planifie', 'en_cours', 'termine', 'annule', 'pause'));
    END IF;
END $$;

-- ============================================================================
-- V005 : Standardisation user_id + commentaires CASCADE
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'logs_securite'
          AND column_name = 'user_id'
          AND data_type = 'character varying'
    ) THEN
        ALTER TABLE logs_securite ALTER COLUMN user_id TYPE TEXT;
    END IF;
END $$;

COMMENT ON COLUMN logs_securite.user_id IS
    'UUID Supabase Auth (auth.uid()) au format texte. Peut être NULL pour les événements système.';
COMMENT ON COLUMN garmin_tokens.user_id IS
    'FK → profils_utilisateurs(id) INTEGER. Intentionnellement entier.';
COMMENT ON COLUMN activites_garmin.user_id IS
    'FK → profils_utilisateurs(id) INTEGER. Intentionnellement entier.';

-- Nettoyage legacy
DROP TABLE IF EXISTS liste_courses CASCADE;
DROP INDEX IF EXISTS idx_repas_planning_id;
DROP INDEX IF EXISTS idx_historique_inventaire_article_id;

-- Commentaires CASCADE
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_repas_recette') THEN
        COMMENT ON CONSTRAINT fk_repas_recette ON repas IS
            'SET NULL intentionnel : la suppression d''une recette ne supprime pas le repas planifié.';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_batch_meals_recette') THEN
        COMMENT ON CONSTRAINT fk_batch_meals_recette ON repas_batch IS
            'SET NULL intentionnel : la suppression d''une recette ne supprime pas le batch.';
    END IF;
END $$;

-- Commentaires vues
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'v_objets_a_remplacer') THEN
        COMMENT ON VIEW v_objets_a_remplacer IS
            'Objets de la maison avec statut a_changer/a_acheter/a_reparer.';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'v_temps_par_activite_30j') THEN
        COMMENT ON VIEW v_temps_par_activite_30j IS
            'Agrégation des sessions de travail des 30 derniers jours.';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'v_budget_travaux_par_piece') THEN
        COMMENT ON VIEW v_budget_travaux_par_piece IS
            'Budget cumulé des travaux par pièce maison.';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'v_taches_jour') THEN
        COMMENT ON VIEW v_taches_jour IS
            'Tâches home à faire ou en cours avec date_due <= demain.';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_views WHERE viewname = 'v_charge_semaine') THEN
        COMMENT ON VIEW v_charge_semaine IS
            'Charge quotidienne estimée pour les 7 prochains jours.';
    END IF;
END $$;


-- ============================================================================
-- Phase A — Index supplémentaires sur colonnes fréquentes
-- ============================================================================
-- Audit A4.4 : colonnes user_id, date, statut fréquemment filtrées

-- activites_famille : recherche par user_id + date
CREATE INDEX IF NOT EXISTS ix_activites_famille_user_date
    ON activites_famille(user_id, date_prevue DESC);

-- depenses : recherche par user_id + mois
CREATE INDEX IF NOT EXISTS ix_depenses_user_date
    ON depenses(user_id, date_depense DESC);

-- notes : recherche par user_id + date
CREATE INDEX IF NOT EXISTS ix_notes_user_cree_le
    ON notes(user_id, cree_le DESC);

-- projets_maison : filtrage par statut
CREATE INDEX IF NOT EXISTS ix_projets_maison_statut
    ON projets_maison(statut);

-- entretien_maison : prochaine_date pour les alertes
CREATE INDEX IF NOT EXISTS ix_entretien_maison_prochaine_date
    ON entretien_maison(prochaine_date)
    WHERE prochaine_date IS NOT NULL;

-- journal_bord : recherche par user_id + date
CREATE INDEX IF NOT EXISTS ix_journal_bord_user_date
    ON journal_bord(user_id, date_entree DESC);

-- etat_persistant : recherche par namespace + user_id (très fréquent)
CREATE INDEX IF NOT EXISTS ix_etat_persistant_namespace_user
    ON etat_persistant(namespace, user_id);

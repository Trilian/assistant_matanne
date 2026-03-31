-- ============================================================================
-- ASSISTANT MATANNE — Migrations absorbées (V005-V007)
-- ============================================================================
-- Ce fichier contient les changements des migrations V005, V006, V007
-- qui ont été absorbés dans le script principal.
-- Contexte : stratégie SQL-first (pas d'Alembic auto).
-- ============================================================================

-- PARTIE 11 : VÉRIFICATION FINALE
-- ============================================================================
SELECT tablename,
    (
        SELECT COUNT(*)
        FROM information_schema.columns c
        WHERE c.table_name = t.tablename
    ) AS nb_colonnes
FROM pg_tables t
WHERE schemaname = 'public'
ORDER BY tablename;
COMMIT;
-- ============================================================================
-- INDEXES MANQUANTS (SQL2)
-- ============================================================================
-- idx_articles_courses_liste_achete already created in section 4.13 above

CREATE INDEX IF NOT EXISTS idx_articles_inventaire_peremption
    ON articles_inventaire(date_peremption);

CREATE INDEX IF NOT EXISTS idx_repas_planning_planning_date
    ON repas_planning(planning_id, date_repas);

CREATE INDEX IF NOT EXISTS idx_historique_actions_user_date
    ON historique_actions(user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_paris_sportifs_statut_user
    ON paris_sportifs(statut, user_id);

-- ============================================================================
-- TRIGGER : listes_courses.modifie_le (SQL4)
-- ============================================================================
CREATE OR REPLACE FUNCTION update_liste_courses_modifie_le()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE listes_courses
    SET modifie_le = NOW()
    WHERE id = COALESCE(NEW.liste_id, OLD.liste_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_articles_courses_update_liste ON articles_courses;
CREATE TRIGGER trg_articles_courses_update_liste
    AFTER INSERT OR UPDATE OR DELETE ON articles_courses
    FOR EACH ROW EXECUTE FUNCTION update_liste_courses_modifie_le();

-- ============================================================================
-- TRIGGER : invalidation cache planning (SQL5)
-- ============================================================================
CREATE OR REPLACE FUNCTION notify_planning_changed()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id TEXT;
BEGIN
    SELECT p.cree_par INTO v_user_id
    FROM plannings p
    WHERE p.id = COALESCE(NEW.planning_id, OLD.planning_id)
    LIMIT 1;
    PERFORM pg_notify('planning_changed', COALESCE(v_user_id, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_repas_planning_notify ON repas_planning;
CREATE TRIGGER trg_repas_planning_notify
    AFTER INSERT OR UPDATE OR DELETE ON repas_planning
    FOR EACH ROW EXECUTE FUNCTION notify_planning_changed();

-- ============================================================================
-- CONSOLIDATION V005 : Index composites + CHECK enums + commentaires
-- (Migration V005__phase2_sql_consolidation.sql absorbée)
-- ============================================================================

-- user_id logs_securite : VARCHAR(255) → TEXT
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

-- Index composites
CREATE INDEX IF NOT EXISTS ix_repas_planning_date ON repas(planning_id, date_repas);
CREATE INDEX IF NOT EXISTS ix_repas_planning_type ON repas(planning_id, type_repas);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_achete ON articles_courses(liste_id, achete);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_priorite ON articles_courses(liste_id, priorite);
CREATE INDEX IF NOT EXISTS ix_inventaire_peremption_quantite ON inventaire(date_peremption, quantite)
    WHERE date_peremption IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_ingredient_date ON historique_inventaire(ingredient_id, date_modification);
CREATE INDEX IF NOT EXISTS ix_listes_courses_statut_semaine ON listes_courses(statut, semaine_du);
CREATE INDEX IF NOT EXISTS ix_plannings_actif_semaine ON plannings(actif, semaine_debut) WHERE actif = TRUE;

-- CHECK enums
ALTER TABLE repas ADD CONSTRAINT IF NOT EXISTS ck_repas_type_repas
    CHECK (type_repas IN ('petit_dejeuner','brunch','dejeuner','gouter','diner','collation','autre'));
ALTER TABLE listes_courses ADD CONSTRAINT IF NOT EXISTS ck_listes_courses_statut
    CHECK (statut IN ('active','en_cours','completee','archivee','annulee'));
ALTER TABLE recettes ADD CONSTRAINT IF NOT EXISTS ck_recettes_difficulte
    CHECK (difficulte IN ('facile','moyen','difficile','expert'));
ALTER TABLE recettes ADD CONSTRAINT IF NOT EXISTS ck_recettes_saison
    CHECK (saison IN ('printemps','ete','automne','hiver','toute_annee','toute_année'));
ALTER TABLE articles_courses ADD CONSTRAINT IF NOT EXISTS ck_articles_courses_priorite
    CHECK (priorite IN ('haute','moyenne','basse','urgente'));
ALTER TABLE articles_modeles ADD CONSTRAINT IF NOT EXISTS ck_articles_modeles_priorite
    CHECK (priorite IN ('haute','moyenne','basse','urgente'));
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sessions_batch_cooking') THEN
        ALTER TABLE sessions_batch_cooking
            ADD CONSTRAINT IF NOT EXISTS ck_batch_statut
            CHECK (statut IN ('planifie','en_cours','termine','annule','pause'));
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
-- CONSOLIDATION V006 : Table job_executions
-- (Migration V006__phase7_jobs_automations.sql absorbée)
-- ============================================================================

CREATE TABLE IF NOT EXISTS job_executions (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    job_name VARCHAR(255),
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_ms INTEGER,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    output_logs TEXT,
    triggered_by_user_id VARCHAR(255),
    triggered_by_user_role VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_job_executions_job_id ON job_executions(job_id);
CREATE INDEX IF NOT EXISTS ix_job_executions_status ON job_executions(status);
CREATE INDEX IF NOT EXISTS ix_job_executions_started_at ON job_executions(started_at DESC);
CREATE INDEX IF NOT EXISTS ix_job_executions_created_at ON job_executions(created_at DESC);
CREATE INDEX IF NOT EXISTS ix_job_executions_job_started ON job_executions(job_id, started_at DESC);

COMMENT ON TABLE job_executions IS
    'Historique des exécutions cron et manuelles (admin) avec durée et erreurs.';

-- ============================================================================
-- CONSOLIDATION V007 : Module Habitat
-- (Migration V007__module_habitat.sql absorbée)
-- ============================================================================

CREATE TABLE IF NOT EXISTS habitat_scenarios (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    budget_estime DECIMAL(12,2),
    surface_finale_m2 DECIMAL(8,2),
    nb_chambres INTEGER,
    score_global DECIMAL(5,2),
    avantages JSONB DEFAULT '[]'::jsonb,
    inconvenients JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    statut VARCHAR(50) DEFAULT 'brouillon',
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habitat_criteres (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER NOT NULL REFERENCES habitat_scenarios(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    poids DECIMAL(4,2) DEFAULT 1.00,
    note DECIMAL(3,1),
    commentaire TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habitat_criteres_immo (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) DEFAULT 'Recherche principale',
    departements JSONB DEFAULT '[]'::jsonb,
    villes JSONB DEFAULT '[]'::jsonb,
    rayon_km INTEGER DEFAULT 10,
    budget_min DECIMAL(12,2),
    budget_max DECIMAL(12,2),
    surface_min_m2 DECIMAL(8,2),
    surface_terrain_min_m2 DECIMAL(10,2),
    nb_pieces_min INTEGER,
    nb_chambres_min INTEGER,
    type_bien VARCHAR(50),
    criteres_supplementaires JSONB DEFAULT '{}'::jsonb,
    seuil_alerte DECIMAL(5,2) DEFAULT 0.70,
    actif BOOLEAN DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habitat_annonces (
    id SERIAL PRIMARY KEY,
    critere_id INTEGER REFERENCES habitat_criteres_immo(id) ON DELETE SET NULL,
    source VARCHAR(100) NOT NULL,
    url_source VARCHAR(500) NOT NULL,
    titre VARCHAR(500),
    prix DECIMAL(12,2),
    surface_m2 DECIMAL(8,2),
    surface_terrain_m2 DECIMAL(10,2),
    nb_pieces INTEGER,
    ville VARCHAR(200),
    code_postal VARCHAR(10),
    departement VARCHAR(3),
    photos JSONB DEFAULT '[]'::jsonb,
    description_brute TEXT,
    score_pertinence DECIMAL(5,2),
    statut VARCHAR(50) DEFAULT 'nouveau',
    prix_m2_secteur DECIMAL(8,2),
    ecart_prix_pct DECIMAL(5,2),
    hash_dedup VARCHAR(64),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habitat_plans (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES habitat_scenarios(id) ON DELETE SET NULL,
    nom VARCHAR(200) NOT NULL,
    type_plan VARCHAR(50) NOT NULL,
    image_importee_url VARCHAR(500),
    donnees_pieces JSONB NOT NULL DEFAULT '{}'::jsonb,
    contraintes JSONB DEFAULT '{}'::jsonb,
    surface_totale_m2 DECIMAL(8,2),
    budget_estime DECIMAL(12,2),
    notes TEXT,
    version INTEGER DEFAULT 1,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habitat_pieces (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES habitat_plans(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    type_piece VARCHAR(50),
    surface_m2 DECIMAL(6,2),
    position_x DECIMAL(8,2),
    position_y DECIMAL(8,2),
    largeur DECIMAL(8,2),
    longueur DECIMAL(8,2),
    hauteur_plafond DECIMAL(4,2),
    couleur_mur VARCHAR(7),
    sol_type VARCHAR(50),
    meubles JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habitat_modifications_plan (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES habitat_plans(id) ON DELETE CASCADE,
    prompt_utilisateur TEXT NOT NULL,
    analyse_ia JSONB NOT NULL DEFAULT '{}'::jsonb,
    image_generee_url VARCHAR(500),
    acceptee BOOLEAN,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habitat_projets_deco (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER REFERENCES habitat_pieces(id) ON DELETE SET NULL,
    nom_piece VARCHAR(200) NOT NULL,
    style VARCHAR(100),
    palette_couleurs JSONB DEFAULT '[]'::jsonb,
    inspirations JSONB DEFAULT '[]'::jsonb,
    budget_prevu DECIMAL(10,2),
    budget_depense DECIMAL(10,2) DEFAULT 0,
    statut VARCHAR(50) DEFAULT 'idee',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habitat_zones_jardin (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES habitat_plans(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    type_zone VARCHAR(100),
    surface_m2 DECIMAL(8,2),
    altitude_relative DECIMAL(4,2),
    position_x DECIMAL(8,2),
    position_y DECIMAL(8,2),
    largeur DECIMAL(8,2),
    longueur DECIMAL(8,2),
    donnees_canvas JSONB DEFAULT '{}'::jsonb,
    plantes JSONB DEFAULT '[]'::jsonb,
    amenagements JSONB DEFAULT '[]'::jsonb,
    budget_estime DECIMAL(10,2),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_habitat_scenarios_statut ON habitat_scenarios(statut);
CREATE INDEX IF NOT EXISTS idx_habitat_scenarios_score ON habitat_scenarios(score_global);
CREATE INDEX IF NOT EXISTS idx_habitat_criteres_scenario ON habitat_criteres(scenario_id);
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_statut ON habitat_annonces(statut);
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_source ON habitat_annonces(source);
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_ville ON habitat_annonces(ville);
CREATE INDEX IF NOT EXISTS idx_habitat_plans_type ON habitat_plans(type_plan);
CREATE INDEX IF NOT EXISTS idx_habitat_pieces_plan ON habitat_pieces(plan_id);
CREATE INDEX IF NOT EXISTS idx_habitat_zones_jardin_plan ON habitat_zones_jardin(plan_id);

-- ============================================================================ 
-- FIN DU SCRIPT — ~143 tables créées (consolidation complète)
-- ============================================================================ 
--
-- Inclut:
--   - 94 tables originales (INIT_COMPLET v2)
--   - 5 tables Jeux extensions (Euromillions, cotes historique, mise responsable)
--   - 15 tables Maison extensions (contrats, artisans, garanties, cellier, etc.)
--   - 7 tables Utilitaires (notes, journal, contacts, liens, mots de passe, etc.)
--   - 30 entretiens saisonniers prédéfinis
--   - Migrations V003-V007 absorbées (canaux notifications, logs sécurité,
--     index composites, CHECK enums, job_executions, module habitat)
--                   lecture seule sur tables système/référence
--   anon          : Aucun accès
--
-- ============================================================================

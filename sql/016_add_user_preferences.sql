-- Migration: Add user preferences, recipe feedbacks, openfoodfacts cache, and external calendar config tables
-- Date: 2025-01-15
-- Description: Nouveaux modèles pour l'apprentissage IA et les intégrations externes
-- À exécuter sur Supabase via SQL Editor

-- ═══════════════════════════════════════════════════════════
-- TABLE: user_preferences
-- Préférences alimentaires persistantes pour l'IA
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL UNIQUE,
    
    -- Composition familiale
    nb_adultes INTEGER DEFAULT 2,
    jules_present BOOLEAN DEFAULT TRUE,
    jules_age_mois INTEGER DEFAULT 19,
    
    -- Contraintes temps
    temps_semaine VARCHAR(20) DEFAULT 'normal',
    temps_weekend VARCHAR(20) DEFAULT 'long',
    
    -- Préférences alimentaires (JSONB arrays)
    aliments_exclus JSONB DEFAULT '[]'::JSONB,
    aliments_favoris JSONB DEFAULT '[]'::JSONB,
    
    -- Équilibre nutritionnel
    poisson_par_semaine INTEGER DEFAULT 2,
    vegetarien_par_semaine INTEGER DEFAULT 1,
    viande_rouge_max INTEGER DEFAULT 2,
    
    -- Équipements (JSONB arrays)
    robots JSONB DEFAULT '["thermomix", "airfryer", "cookeo"]'::JSONB,
    magasins_preferes JSONB DEFAULT '[]'::JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id ON user_preferences(user_id);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_user_preferences_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER trg_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_user_preferences_timestamp();


-- ═══════════════════════════════════════════════════════════
-- TABLE: recipe_feedbacks
-- Apprentissage IA des goûts via 👍/👎
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS recipe_feedbacks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    recette_id INTEGER NOT NULL REFERENCES recettes(id) ON DELETE CASCADE,
    
    -- Feedback
    feedback VARCHAR(20) NOT NULL DEFAULT 'neutral'
        CHECK (feedback IN ('like', 'dislike', 'neutral')),
    contexte VARCHAR(200),
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contrainte: un seul feedback par utilisateur/recette
    UNIQUE (user_id, recette_id)
);

-- Index pour requêtes fréquentes
CREATE INDEX IF NOT EXISTS ix_recipe_feedbacks_user_id ON recipe_feedbacks(user_id);
CREATE INDEX IF NOT EXISTS ix_recipe_feedbacks_recette_id ON recipe_feedbacks(recette_id);
CREATE INDEX IF NOT EXISTS ix_recipe_feedbacks_feedback ON recipe_feedbacks(feedback);


-- ═══════════════════════════════════════════════════════════
-- TABLE: openfoodfacts_cache
-- Cache des produits scannés via OpenFoodFacts API
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS openfoodfacts_cache (
    id SERIAL PRIMARY KEY,
    code_barres VARCHAR(50) NOT NULL UNIQUE,
    
    -- Données produit
    nom VARCHAR(300),
    marque VARCHAR(200),
    categorie VARCHAR(200),
    
    -- Scores nutritionnels
    nutriscore CHAR(1),
    nova_group INTEGER,
    ecoscore CHAR(1),
    
    -- Données complètes
    nutrition_data JSONB,
    allergenes JSONB DEFAULT '[]'::JSONB,
    image_url VARCHAR(500),
    
    -- Timestamps
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour recherche par code-barres
CREATE INDEX IF NOT EXISTS ix_openfoodfacts_cache_code_barres ON openfoodfacts_cache(code_barres);


-- ═══════════════════════════════════════════════════════════
-- TABLE: external_calendar_configs
-- Configuration calendriers externes (Google, Apple, etc.)
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS external_calendar_configs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    provider VARCHAR(20) NOT NULL
        CHECK (provider IN ('google', 'apple', 'outlook', 'ical_url')),
    name VARCHAR(200) NOT NULL,
    
    -- OAuth tokens (chiffrés en production)
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMPTZ,
    
    -- Paramètres de synchronisation
    sync_enabled BOOLEAN DEFAULT TRUE,
    sync_direction VARCHAR(20) DEFAULT 'import'
        CHECK (sync_direction IN ('import', 'export', 'both')),
    
    -- Timestamps
    last_sync TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contrainte: un seul calendrier par user/provider/name
    UNIQUE (user_id, provider, name)
);

-- Index pour requêtes
CREATE INDEX IF NOT EXISTS ix_external_calendar_configs_user_id ON external_calendar_configs(user_id);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_external_calendar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_external_calendar_updated_at ON external_calendar_configs;
CREATE TRIGGER trg_external_calendar_updated_at
    BEFORE UPDATE ON external_calendar_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_external_calendar_timestamp();


-- ═══════════════════════════════════════════════════════════
-- COMMENTAIRES DE DOCUMENTATION
-- ═══════════════════════════════════════════════════════════

COMMENT ON TABLE user_preferences IS 'Préférences utilisateur persistantes pour personnalisation IA';
COMMENT ON TABLE recipe_feedbacks IS 'Feedbacks 👍/👎 sur les recettes pour apprentissage IA';
COMMENT ON TABLE openfoodfacts_cache IS 'Cache local des produits OpenFoodFacts scannés';
COMMENT ON TABLE external_calendar_configs IS 'Configuration des calendriers externes (Google, Apple, etc.)';

COMMENT ON COLUMN user_preferences.aliments_exclus IS 'Liste JSONB des ingrédients à exclure (allergies, préférences)';
COMMENT ON COLUMN user_preferences.robots IS 'Liste JSONB des robots de cuisine disponibles';
COMMENT ON COLUMN recipe_feedbacks.feedback IS 'Type de feedback: like, dislike, neutral';
COMMENT ON COLUMN recipe_feedbacks.contexte IS 'Contexte du repas: batch_cooking, semaine, weekend';
COMMENT ON COLUMN openfoodfacts_cache.nutriscore IS 'Score nutritionnel A-E';
COMMENT ON COLUMN openfoodfacts_cache.nova_group IS 'Groupe NOVA 1-4 (transformation)';
COMMENT ON COLUMN external_calendar_configs.sync_direction IS 'Direction de sync: import, export, both';


-- ═══════════════════════════════════════════════════════════
-- VÉRIFICATION
-- ═══════════════════════════════════════════════════════════

DO $$
BEGIN
    RAISE NOTICE '✅ Migration terminée avec succès!';
    RAISE NOTICE '   - user_preferences';
    RAISE NOTICE '   - recipe_feedbacks';
    RAISE NOTICE '   - openfoodfacts_cache';
    RAISE NOTICE '   - external_calendar_configs';
END $$;

-- ═══════════════════════════════════════════════════════════════════════════
-- Migration: Famille Refonte
-- Date: 2026-02-02
-- Description: Nouveaux modèles pour hub famille (UserProfile, Garmin, Weekend, Achats)
-- ═══════════════════════════════════════════════════════════════════════════

-- ────────────────────────────────────────────────────────────────────────────
-- 1. TABLE user_profiles - Profils Anne et Mathieu
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    avatar_emoji VARCHAR(10) DEFAULT '👤',
    
    -- Objectifs fitness
    objectif_pas INTEGER DEFAULT 8000,
    objectif_calories INTEGER DEFAULT 2000,
    objectif_minutes_actives INTEGER DEFAULT 30,
    
    -- Statut Garmin
    garmin_connected BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Créer les profils Anne et Mathieu
INSERT INTO user_profiles (username, display_name, avatar_emoji, objectif_pas, objectif_calories)
VALUES 
    ('anne', 'Anne', '👩', 8000, 1800),
    ('mathieu', 'Mathieu', '👨', 10000, 2200)
ON CONFLICT (username) DO NOTHING;


-- ────────────────────────────────────────────────────────────────────────────
-- 2. TABLE garmin_tokens - Tokens OAuth Garmin
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS garmin_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- OAuth 1.0a tokens
    oauth_token VARCHAR(255) NOT NULL,
    oauth_token_secret VARCHAR(255) NOT NULL,
    
    -- Metadata
    last_sync TIMESTAMP WITH TIME ZONE,
    is_valid BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Un seul token actif par user
    CONSTRAINT uq_garmin_tokens_user UNIQUE (user_id)
);


-- ────────────────────────────────────────────────────────────────────────────
-- 3. TABLE garmin_activities - Activités synchronisées
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS garmin_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Identifiant Garmin
    garmin_activity_id VARCHAR(50) UNIQUE,
    
    -- Infos activité
    activity_type VARCHAR(50) NOT NULL DEFAULT 'other',
    activity_name VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_seconds INTEGER DEFAULT 0,
    
    -- Métriques
    distance_meters FLOAT DEFAULT 0,
    calories INTEGER DEFAULT 0,
    steps INTEGER DEFAULT 0,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    avg_speed FLOAT,
    elevation_gain FLOAT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_garmin_activities_user_date 
    ON garmin_activities(user_id, start_time DESC);


-- ────────────────────────────────────────────────────────────────────────────
-- 4. TABLE garmin_daily_summaries - Résumés quotidiens
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS garmin_daily_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Date du résumé
    summary_date DATE NOT NULL,
    
    -- Métriques journalières
    total_steps INTEGER DEFAULT 0,
    total_distance_meters FLOAT DEFAULT 0,
    total_calories INTEGER DEFAULT 0,
    active_minutes INTEGER DEFAULT 0,
    floors_climbed INTEGER DEFAULT 0,
    
    -- Sommeil
    sleep_duration_seconds INTEGER,
    sleep_score INTEGER,
    
    -- Stress & énergie
    avg_stress_level INTEGER,
    body_battery_high INTEGER,
    body_battery_low INTEGER,
    
    -- FC repos
    resting_heart_rate INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Un résumé par user par jour
    CONSTRAINT uq_garmin_daily_user_date UNIQUE (user_id, summary_date)
);

CREATE INDEX IF NOT EXISTS idx_garmin_daily_user_date 
    ON garmin_daily_summaries(user_id, summary_date DESC);


-- ────────────────────────────────────────────────────────────────────────────
-- 5. TABLE food_logs - Journal alimentaire
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS food_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Date et repas
    log_date DATE NOT NULL DEFAULT CURRENT_DATE,
    meal_type VARCHAR(20) NOT NULL DEFAULT 'dejeuner',  -- petit_dejeuner, dejeuner, diner, snack
    
    -- Description
    description TEXT NOT NULL,
    
    -- Estimation calories (optionnel)
    calories INTEGER,
    
    -- Qualité perçue (1-5)
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_food_logs_user_date 
    ON food_logs(user_id, log_date DESC);


-- ────────────────────────────────────────────────────────────────────────────
-- 6. TABLE weekend_activities - Activités weekend planifiées
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS weekend_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Planning
    activity_date DATE NOT NULL,
    time_slot VARCHAR(20) DEFAULT 'matin',  -- matin, apres_midi, soir, journee
    
    -- Infos activité
    activity_type VARCHAR(50) NOT NULL DEFAULT 'autre',
    title VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    
    -- Budget
    estimated_cost DECIMAL(10,2) DEFAULT 0,
    actual_cost DECIMAL(10,2),
    
    -- Adaptation Jules
    adapte_jules BOOLEAN DEFAULT TRUE,
    age_minimum_mois INTEGER,
    
    -- Évaluation (après l'activité)
    is_completed BOOLEAN DEFAULT FALSE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    
    -- Source
    source VARCHAR(50) DEFAULT 'manuel',  -- manuel, ai_suggestion, recommandation
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_weekend_activities_date 
    ON weekend_activities(activity_date DESC);


-- ────────────────────────────────────────────────────────────────────────────
-- 7. TABLE family_purchases - Liste d'achats famille
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS family_purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Catégorie et groupe
    category VARCHAR(50) NOT NULL DEFAULT 'autre',
    -- Categories: vetement, jouet, equipement, electromenager, mobilier, autre
    
    group_target VARCHAR(20) NOT NULL DEFAULT 'famille',
    -- Groups: jules, anne, mathieu, maison, famille
    
    -- Infos article
    title VARCHAR(255) NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    
    -- Taille (pour vêtements)
    size VARCHAR(20),
    
    -- Prix
    estimated_price DECIMAL(10,2),
    actual_price DECIMAL(10,2),
    
    -- Priorité
    priority VARCHAR(20) DEFAULT 'normal',
    -- Priorities: urgent, haute, normal, basse, plus_tard
    
    -- Magasin suggéré
    store VARCHAR(100),
    url VARCHAR(500),
    
    -- Statut
    status VARCHAR(20) DEFAULT 'en_attente',
    -- Status: en_attente, achete, annule
    
    purchased_date DATE,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_family_purchases_status 
    ON family_purchases(status, priority);

CREATE INDEX IF NOT EXISTS idx_family_purchases_group 
    ON family_purchases(group_target);


-- ────────────────────────────────────────────────────────────────────────────
-- 8. TRIGGERS pour updated_at
-- ────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_garmin_tokens_updated_at ON garmin_tokens;
CREATE TRIGGER update_garmin_tokens_updated_at
    BEFORE UPDATE ON garmin_tokens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_weekend_activities_updated_at ON weekend_activities;
CREATE TRIGGER update_weekend_activities_updated_at
    BEFORE UPDATE ON weekend_activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_family_purchases_updated_at ON family_purchases;
CREATE TRIGGER update_family_purchases_updated_at
    BEFORE UPDATE ON family_purchases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ────────────────────────────────────────────────────────────────────────────
-- 9. RLS (Row Level Security) - Optionnel
-- ────────────────────────────────────────────────────────────────────────────
-- ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE garmin_tokens ENABLE ROW LEVEL SECURITY;
-- ... etc


-- ════════════════════════════════════════════════════════════════════════════
-- FIN MIGRATION
-- ════════════════════════════════════════════════════════════════════════════

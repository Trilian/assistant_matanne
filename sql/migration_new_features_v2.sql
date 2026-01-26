-- ═══════════════════════════════════════════════════════════════════════════════
-- MIGRATION: Nouvelles fonctionnalités Assistant Matanne
-- Date: 2026-01-26
-- Version: 2.0 - Sans dépendances familles (table non existante)
-- Description: Tables pour budget, météo, backup, calendrier, notifications
-- ═══════════════════════════════════════════════════════════════════════════════

-- À exécuter sur Supabase SQL Editor

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════════
-- 1. TABLE DÉPENSES (Budget Tracker)
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS depenses (
    id BIGSERIAL PRIMARY KEY,
    montant DECIMAL(10, 2) NOT NULL,
    categorie VARCHAR(50) NOT NULL DEFAULT 'autre',
    description TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    recurrence VARCHAR(20), -- 'mensuel', 'hebdomadaire', etc.
    tags JSONB DEFAULT '[]',
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_depenses_date ON depenses(date);
CREATE INDEX IF NOT EXISTS idx_depenses_categorie ON depenses(categorie);
CREATE INDEX IF NOT EXISTS idx_depenses_user ON depenses(user_id);

-- Contrainte sur les catégories valides
ALTER TABLE depenses DROP CONSTRAINT IF EXISTS check_categorie_valide;
ALTER TABLE depenses ADD CONSTRAINT check_categorie_valide CHECK (
    categorie IN (
        'alimentation', 'transport', 'logement', 'sante', 
        'loisirs', 'vetements', 'education', 'cadeaux',
        'abonnements', 'restaurant', 'vacances', 'bebe', 'autre'
    )
);

COMMENT ON TABLE depenses IS 'Suivi des dépenses familiales';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 2. TABLE BUDGETS MENSUELS
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS budgets_mensuels (
    id BIGSERIAL PRIMARY KEY,
    mois DATE NOT NULL, -- Premier jour du mois
    budget_total DECIMAL(10, 2) NOT NULL DEFAULT 0,
    budgets_par_categorie JSONB DEFAULT '{}',
    notes TEXT,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(mois, user_id)
);

CREATE INDEX IF NOT EXISTS idx_budgets_mois ON budgets_mensuels(mois);
CREATE INDEX IF NOT EXISTS idx_budgets_user ON budgets_mensuels(user_id);

COMMENT ON TABLE budgets_mensuels IS 'Budgets mensuels par catégorie';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 3. TABLE ALERTES MÉTÉO
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS alertes_meteo (
    id BIGSERIAL PRIMARY KEY,
    type_alerte VARCHAR(30) NOT NULL, -- 'gel', 'canicule', 'pluie_forte', etc.
    niveau VARCHAR(20) NOT NULL DEFAULT 'info', -- 'info', 'attention', 'danger'
    titre VARCHAR(200) NOT NULL,
    message TEXT,
    conseil_jardin TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    temperature DECIMAL(5, 2),
    lu BOOLEAN DEFAULT FALSE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alertes_meteo_date ON alertes_meteo(date_debut);
CREATE INDEX IF NOT EXISTS idx_alertes_meteo_type ON alertes_meteo(type_alerte);
CREATE INDEX IF NOT EXISTS idx_alertes_meteo_user ON alertes_meteo(user_id);

COMMENT ON TABLE alertes_meteo IS 'Alertes météo pour le jardin';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 4. TABLE CONFIGURATION MÉTÉO
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS config_meteo (
    id BIGSERIAL PRIMARY KEY,
    latitude DECIMAL(10, 7) DEFAULT 48.8566,
    longitude DECIMAL(10, 7) DEFAULT 2.3522,
    ville VARCHAR(100) DEFAULT 'Paris',
    surface_jardin_m2 DECIMAL(10, 2) DEFAULT 50,
    notifications_gel BOOLEAN DEFAULT TRUE,
    notifications_canicule BOOLEAN DEFAULT TRUE,
    notifications_pluie BOOLEAN DEFAULT TRUE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE config_meteo IS 'Configuration météo par utilisateur';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 5. TABLE BACKUPS
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS backups (
    id BIGSERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    tables_included JSONB DEFAULT '[]',
    row_counts JSONB DEFAULT '{}',
    size_bytes BIGINT DEFAULT 0,
    compressed BOOLEAN DEFAULT TRUE,
    storage_path VARCHAR(500), -- Chemin Supabase Storage
    version VARCHAR(20) DEFAULT '1.0.0',
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_backups_date ON backups(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_backups_user ON backups(user_id);

COMMENT ON TABLE backups IS 'Historique des sauvegardes';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 6. TABLE CALENDRIERS EXTERNES
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS calendriers_externes (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL, -- 'google', 'apple', 'ical', 'outlook'
    nom VARCHAR(200) NOT NULL,
    url TEXT,
    credentials JSONB, -- Tokens OAuth chiffrés
    enabled BOOLEAN DEFAULT TRUE,
    sync_interval_minutes INT DEFAULT 60,
    last_sync TIMESTAMPTZ,
    sync_direction VARCHAR(20) DEFAULT 'bidirectional', -- 'import', 'export', 'bidirectional'
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_calendriers_provider ON calendriers_externes(provider);
CREATE INDEX IF NOT EXISTS idx_calendriers_user ON calendriers_externes(user_id);

COMMENT ON TABLE calendriers_externes IS 'Calendriers externes synchronisés';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 7. TABLE ÉVÉNEMENTS CALENDRIER
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS evenements_calendrier (
    id BIGSERIAL PRIMARY KEY,
    uid VARCHAR(255) NOT NULL, -- UID iCal unique
    titre VARCHAR(300) NOT NULL,
    description TEXT,
    date_debut TIMESTAMPTZ NOT NULL,
    date_fin TIMESTAMPTZ,
    lieu VARCHAR(300),
    all_day BOOLEAN DEFAULT FALSE,
    recurrence_rule TEXT, -- RRULE iCal
    rappel_minutes INT,
    source_calendrier_id BIGINT REFERENCES calendriers_externes(id) ON DELETE SET NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(uid, user_id)
);

CREATE INDEX IF NOT EXISTS idx_evenements_date ON evenements_calendrier(date_debut);
CREATE INDEX IF NOT EXISTS idx_evenements_user ON evenements_calendrier(user_id);

COMMENT ON TABLE evenements_calendrier IS 'Événements de calendrier synchronisés';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 8. TABLE ABONNEMENTS PUSH
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS push_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL UNIQUE,
    p256dh_key TEXT NOT NULL,
    auth_key TEXT NOT NULL,
    device_info JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_push_user ON push_subscriptions(user_id);

COMMENT ON TABLE push_subscriptions IS 'Abonnements notifications push';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 9. TABLE PRÉFÉRENCES NOTIFICATIONS
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS notification_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    courses_rappel BOOLEAN DEFAULT TRUE,
    repas_suggestion BOOLEAN DEFAULT TRUE,
    stock_alerte BOOLEAN DEFAULT TRUE,
    meteo_alerte BOOLEAN DEFAULT TRUE,
    budget_alerte BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '07:00',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE notification_preferences IS 'Préférences de notification par utilisateur';


-- ═══════════════════════════════════════════════════════════════════════════════
-- 10. TABLE RECETTES IMPORTÉES (tracking source)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vérifier si la table recettes existe avant d'ajouter des colonnes
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'recettes') THEN
        ALTER TABLE recettes ADD COLUMN IF NOT EXISTS source_url TEXT;
        ALTER TABLE recettes ADD COLUMN IF NOT EXISTS source_site VARCHAR(100);
        ALTER TABLE recettes ADD COLUMN IF NOT EXISTS imported_at TIMESTAMPTZ;
    END IF;
END $$;


-- ═══════════════════════════════════════════════════════════════════════════════
-- 11. FONCTIONS UTILITAIRES
-- ═══════════════════════════════════════════════════════════════════════════════

-- Fonction pour calculer le total des dépenses d'un mois
CREATE OR REPLACE FUNCTION get_depenses_mois(p_user_id UUID, p_mois DATE)
RETURNS TABLE(
    categorie VARCHAR,
    total DECIMAL,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.categorie,
        SUM(d.montant) as total,
        COUNT(*) as count
    FROM depenses d
    WHERE d.user_id = p_user_id
      AND DATE_TRUNC('month', d.date) = DATE_TRUNC('month', p_mois)
    GROUP BY d.categorie
    ORDER BY total DESC;
END;
$$ LANGUAGE plpgsql;


-- Fonction pour obtenir le résumé budgétaire
CREATE OR REPLACE FUNCTION get_resume_budget(p_user_id UUID, p_mois DATE)
RETURNS JSONB AS $$
DECLARE
    v_budget_total DECIMAL;
    v_depenses_total DECIMAL;
    v_result JSONB;
BEGIN
    -- Récupérer le budget du mois
    SELECT budget_total INTO v_budget_total
    FROM budgets_mensuels
    WHERE user_id = p_user_id
      AND mois = DATE_TRUNC('month', p_mois);
    
    -- Calculer le total des dépenses
    SELECT COALESCE(SUM(montant), 0) INTO v_depenses_total
    FROM depenses
    WHERE user_id = p_user_id
      AND DATE_TRUNC('month', date) = DATE_TRUNC('month', p_mois);
    
    v_result := jsonb_build_object(
        'mois', p_mois,
        'budget_total', COALESCE(v_budget_total, 0),
        'depenses_total', v_depenses_total,
        'reste', COALESCE(v_budget_total, 0) - v_depenses_total,
        'pourcentage_utilise', 
            CASE WHEN COALESCE(v_budget_total, 0) > 0 
                 THEN ROUND((v_depenses_total / v_budget_total * 100)::numeric, 1)
                 ELSE 0 
            END
    );
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════════
-- 12. ROW LEVEL SECURITY (RLS)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Activer RLS sur les nouvelles tables
ALTER TABLE depenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets_mensuels ENABLE ROW LEVEL SECURITY;
ALTER TABLE alertes_meteo ENABLE ROW LEVEL SECURITY;
ALTER TABLE config_meteo ENABLE ROW LEVEL SECURITY;
ALTER TABLE backups ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendriers_externes ENABLE ROW LEVEL SECURITY;
ALTER TABLE evenements_calendrier ENABLE ROW LEVEL SECURITY;
ALTER TABLE push_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- Policies basées sur user_id (l'utilisateur ne voit que ses propres données)
DROP POLICY IF EXISTS depenses_user_policy ON depenses;
CREATE POLICY depenses_user_policy ON depenses
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS budgets_user_policy ON budgets_mensuels;
CREATE POLICY budgets_user_policy ON budgets_mensuels
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS alertes_user_policy ON alertes_meteo;
CREATE POLICY alertes_user_policy ON alertes_meteo
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS config_meteo_user_policy ON config_meteo;
CREATE POLICY config_meteo_user_policy ON config_meteo
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS backups_user_policy ON backups;
CREATE POLICY backups_user_policy ON backups
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS calendriers_user_policy ON calendriers_externes;
CREATE POLICY calendriers_user_policy ON calendriers_externes
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS evenements_user_policy ON evenements_calendrier;
CREATE POLICY evenements_user_policy ON evenements_calendrier
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS push_user_policy ON push_subscriptions;
CREATE POLICY push_user_policy ON push_subscriptions
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS notif_prefs_user_policy ON notification_preferences;
CREATE POLICY notif_prefs_user_policy ON notification_preferences
    FOR ALL USING (user_id = auth.uid());


-- ═══════════════════════════════════════════════════════════════════════════════
-- 13. TRIGGERS UPDATED_AT
-- ═══════════════════════════════════════════════════════════════════════════════

-- Fonction trigger générique
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer aux nouvelles tables
DROP TRIGGER IF EXISTS update_depenses_updated_at ON depenses;
CREATE TRIGGER update_depenses_updated_at
    BEFORE UPDATE ON depenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_budgets_updated_at ON budgets_mensuels;
CREATE TRIGGER update_budgets_updated_at
    BEFORE UPDATE ON budgets_mensuels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_config_meteo_updated_at ON config_meteo;
CREATE TRIGGER update_config_meteo_updated_at
    BEFORE UPDATE ON config_meteo
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_calendriers_updated_at ON calendriers_externes;
CREATE TRIGGER update_calendriers_updated_at
    BEFORE UPDATE ON calendriers_externes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_evenements_updated_at ON evenements_calendrier;
CREATE TRIGGER update_evenements_updated_at
    BEFORE UPDATE ON evenements_calendrier
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_notif_prefs_updated_at ON notification_preferences;
CREATE TRIGGER update_notif_prefs_updated_at
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


COMMIT;

-- ═══════════════════════════════════════════════════════════════════════════════
-- FIN DE LA MIGRATION
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vérification après exécution:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

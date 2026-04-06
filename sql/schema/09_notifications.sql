-- ============================================================================
-- ASSISTANT MATANNE — Tables Notifications
-- ============================================================================
-- Contient : abonnements_push, preferences_notifications, webhooks_abonnements
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS abonnements_push (
    id BIGSERIAL PRIMARY KEY,
    endpoint TEXT NOT NULL,
    p256dh_key TEXT NOT NULL,
    auth_key TEXT NOT NULL,
    device_info JSONB DEFAULT '{}',
    user_id UUID,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    dernier_ping TIMESTAMP WITH TIME ZONE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_push_subscriptions_endpoint ON abonnements_push(endpoint);
CREATE INDEX IF NOT EXISTS ix_push_subscriptions_user ON abonnements_push(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preferences_notifications (
    id BIGSERIAL PRIMARY KEY,
    courses_rappel BOOLEAN NOT NULL DEFAULT TRUE,
    repas_suggestion BOOLEAN NOT NULL DEFAULT TRUE,
    stock_alerte BOOLEAN NOT NULL DEFAULT TRUE,
    meteo_alerte BOOLEAN NOT NULL DEFAULT TRUE,
    budget_alerte BOOLEAN NOT NULL DEFAULT TRUE,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '07:00',
    modules_actifs JSONB DEFAULT '{}'::jsonb,
    canal_prefere VARCHAR(20) DEFAULT 'push',
    -- canaux par catégorie
    canaux_par_categorie JSONB DEFAULT '{"rappels":["push","ntfy"],"alertes":["push","ntfy","email"],"resumes":["email"]}'::jsonb,
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_notification_prefs_user ON preferences_notifications(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS webhooks_abonnements (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    evenements JSONB NOT NULL DEFAULT '[]'::jsonb,
    secret VARCHAR(128) NOT NULL,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT,
    derniere_livraison TIMESTAMP WITH TIME ZONE,
    nb_echecs_consecutifs INTEGER NOT NULL DEFAULT 0,
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_webhooks_user ON webhooks_abonnements(user_id);



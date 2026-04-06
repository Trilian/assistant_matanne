-- ============================================================================
-- ASSISTANT MATANNE — Tables Finances
-- ============================================================================
-- Contient : depenses, budgets_mensuels, calendriers_externes,
--            configs_calendriers_externes, evenements_calendrier
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS depenses (
    id BIGSERIAL PRIMARY KEY,
    montant NUMERIC(10, 2) NOT NULL,
    categorie VARCHAR(50) NOT NULL DEFAULT 'autre',
    description TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    recurrence VARCHAR(20),
    tags JSONB DEFAULT '[]',
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_depense_montant_positif CHECK (montant > 0),
    CONSTRAINT check_categorie_valide CHECK (
        categorie IN (
            'alimentation',
            'transport',
            'logement',
            'sante',
            'loisirs',
            'vetements',
            'education',
            'cadeaux',
            'abonnements',
            'restaurant',
            'vacances',
            'bebe',
            'autre'
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_depenses_categorie ON depenses(categorie);
CREATE INDEX IF NOT EXISTS ix_depenses_date ON depenses(date);
CREATE INDEX IF NOT EXISTS ix_depenses_user_id ON depenses(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS budgets_mensuels (
    id BIGSERIAL PRIMARY KEY,
    mois DATE NOT NULL,
    budget_total NUMERIC(10, 2) NOT NULL DEFAULT 0,
    budgets_par_categorie JSONB DEFAULT '{}',
    notes TEXT,
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_budget_total_positif CHECK (budget_total >= 0)
);
CREATE INDEX IF NOT EXISTS ix_budgets_mensuels_mois ON budgets_mensuels(mois);
CREATE INDEX IF NOT EXISTS ix_budgets_mensuels_user ON budgets_mensuels(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_budget_mois_user ON budgets_mensuels(mois, user_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS calendriers_externes (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    nom VARCHAR(200) NOT NULL,
    url TEXT,
    credentials JSONB,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sync_interval_minutes INTEGER NOT NULL DEFAULT 60,
    last_sync TIMESTAMP WITH TIME ZONE,
    sync_direction VARCHAR(20) NOT NULL DEFAULT 'bidirectional',
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_calendriers_externes_provider ON calendriers_externes(provider);
CREATE INDEX IF NOT EXISTS ix_calendriers_externes_user ON calendriers_externes(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS configs_calendriers_externes (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    provider VARCHAR(20) NOT NULL DEFAULT 'google',
    name VARCHAR(200) NOT NULL DEFAULT 'Mon Calendrier',
    calendar_url VARCHAR(500),
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP WITH TIME ZONE,
    sync_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sync_direction VARCHAR(20) NOT NULL DEFAULT 'import',
    last_sync TIMESTAMP WITH TIME ZONE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_calendar_provider CHECK (
        provider IN ('google', 'apple', 'outlook', 'ical_url')
    )
);
CREATE INDEX IF NOT EXISTS ix_external_cal_user ON configs_calendriers_externes(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_calendar ON configs_calendriers_externes(user_id, provider, name);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS evenements_calendrier (
    id BIGSERIAL PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    titre VARCHAR(300) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    date_fin TIMESTAMP WITH TIME ZONE,
    lieu VARCHAR(300),
    all_day BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence_rule TEXT,
    rappel_minutes INTEGER,
    source_calendrier_id BIGINT,
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_evenements_calendrier_source FOREIGN KEY (source_calendrier_id) REFERENCES calendriers_externes(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS ix_evenements_calendrier_date ON evenements_calendrier(date_debut);
CREATE INDEX IF NOT EXISTS ix_evenements_calendrier_user ON evenements_calendrier(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_event_uid_user ON evenements_calendrier(uid, user_id);


-- Source: 11_utilitaires.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Utilitaires
-- ============================================================================
-- Contient : notes_memos, journal_bord, contacts_utiles, liens_favoris,
--            mots_de_passe_maison, presse_papier_entrees, releves_energie,
--            voyages, checklists_voyage, templates_checklist, minuteur_sessions
-- ============================================================================


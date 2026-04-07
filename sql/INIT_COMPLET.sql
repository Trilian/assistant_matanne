-- ============================================================================
-- ASSISTANT MATANNE — SCRIPT D'INITIALISATION COMPLET
-- ============================================================================
-- Version    : 3.1 (régénéré automatiquement)
-- Généré le  : 2026-04-06 08:48 UTC
-- Source     : sql/schema/*.sql (21 fichiers, ~5208 lignes)
-- Cible      : Supabase PostgreSQL
-- ============================================================================
--
-- ⚠️  NE PAS MODIFIER CE FICHIER DIRECTEMENT.
--     Modifier les fichiers dans sql/schema/ puis relancer:
--       python scripts/db/regenerate_init.py
--
-- Workflow SQL-first:
--   - Nouvelles tables → ajouter dans sql/schema/0X_domaine.sql
--   - Modifications  → créer sql/migrations/VNNN__description.sql
--   - Réinitialisation complète → exécuter ce fichier (DROP CASCADE)
--
-- Usage:
--   psql $DATABASE_URL -f sql/INIT_COMPLET.sql
--   (ou Supabase SQL Editor)
--
-- ============================================================================


-- Source: 01_extensions.sql
-- ============================================================================
-- ASSISTANT MATANNE — Extensions & Transaction
-- ============================================================================
-- Extensions PostgreSQL requises et démarrage de la transaction.
-- Ce fichier est le PREMIER à être exécuté par regenerate_init.py
-- ============================================================================

BEGIN;

-- Source: 02_functions.sql
-- PARTIE 1 : FONCTIONS TRIGGER
-- ============================================================================
CREATE OR REPLACE FUNCTION update_modifie_le_column() RETURNS TRIGGER AS $$ BEGIN NEW.modifie_le = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION update_modifie_le_bis_column() RETURNS TRIGGER AS $$ BEGIN NEW.modifie_le = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- ============================================================================
-- PARTIE 8 : FONCTIONS HELPER
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_temps_entretien_par_mois(
        p_annee INTEGER DEFAULT EXTRACT(
            YEAR
            FROM NOW()
        )::INTEGER,
        p_mois INTEGER DEFAULT NULL
    ) RETURNS TABLE (
        mois INTEGER,
        annee INTEGER,
        type_activite VARCHAR,
        nb_sessions BIGINT,
        duree_totale_minutes BIGINT
    ) AS $$ BEGIN RETURN QUERY
SELECT EXTRACT(
        MONTH
        FROM s.debut
    )::INTEGER AS mois,
    EXTRACT(
        YEAR
        FROM s.debut
    )::INTEGER AS annee,
    s.type_activite,
    COUNT(*)::BIGINT AS nb_sessions,
    COALESCE(SUM(s.duree_minutes), 0)::BIGINT AS duree_totale_minutes
FROM sessions_travail s
WHERE EXTRACT(
        YEAR
        FROM s.debut
    )::INTEGER = p_annee
    AND (
        p_mois IS NULL
        OR EXTRACT(
            MONTH
            FROM s.debut
        )::INTEGER = p_mois
    )
    AND s.fin IS NOT NULL
GROUP BY EXTRACT(
        MONTH
        FROM s.debut
    ),
    EXTRACT(
        YEAR
        FROM s.debut
    ),
    s.type_activite
ORDER BY mois,
    type_activite;
END;
$$ LANGUAGE plpgsql;
-- ============================================================================

-- Source: 03_systeme.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Système
-- ============================================================================
-- Contient : schema_migrations, profils_utilisateurs, preferences_utilisateurs,
--            config_meteo, alertes_meteo, sauvegardes, historique_actions,
--            etats_persistants, gamification, automations, logs_securite,
--            job_executions, openfoodfacts_cache
-- ============================================================================

-- Source: 03_systeme.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Système
-- ============================================================================
-- Contient : schema_migrations, profils_utilisateurs, preferences_utilisateurs,
--            config_meteo, alertes_meteo, sauvegardes, historique_actions,
--            etats_persistants, gamification, automations, logs_securite,
--            job_executions, openfoodfacts_cache
-- ============================================================================
-- PARTIE 2 : TABLE DE SUIVI DES MIGRATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    checksum VARCHAR(64),
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- ============================================================================
-- PARTIE 3 : TABLES AUTONOMES (sans dépendances FK)
-- ============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.01 INGREDIENTS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.02 USER_PROFILES


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profils_utilisateurs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(200),
    avatar_emoji VARCHAR(10) DEFAULT '👤',
    -- Infos santé
    date_naissance DATE,
    taille_cm INTEGER,
    poids_kg FLOAT,
    objectif_poids_kg FLOAT,
    -- Objectifs fitness
    objectif_pas_quotidien INTEGER NOT NULL DEFAULT 10000,
    objectif_calories_brulees INTEGER NOT NULL DEFAULT 500,
    objectif_minutes_actives INTEGER NOT NULL DEFAULT 30,
    -- Garmin
    garmin_connected BOOLEAN NOT NULL DEFAULT FALSE,
    -- Sécurité
    pin_hash VARCHAR(255),
    sections_protegees JSONB,
    -- Préférences avancées
    preferences_modules JSONB,
    theme_prefere VARCHAR(20) DEFAULT 'auto',
    -- Timestamps
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_profils_username ON profils_utilisateurs(username);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.03 RECETTES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.04 PLANNINGS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.05 LISTES_COURSES (en-tête)


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.06 MODELES_COURSES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.07 CHILD_PROFILES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.08 HEALTH_ROUTINES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.09 HEALTH_OBJECTIVES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.10 PROJECTS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.11 ROUTINES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.12 GARDEN_ITEMS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.13 TEMPLATES_SEMAINE


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.14 CONFIG_BATCH_COOKING


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.15 JEUX_EQUIPES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.16 JEUX_TIRAGES_LOTO


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.17 JEUX_STATS_LOTO


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.18 JEUX_HISTORIQUE


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.19 JEUX_SERIES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.20 JEUX_CONFIGURATION


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.21 WEEKEND_ACTIVITIES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.22 FAMILY_PURCHASES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.23 FAMILY_ACTIVITIES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.24 FAMILY_BUDGETS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.25 SHOPPING_ITEMS_FAMILLE


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.25b HISTORIQUE_ACHATS (apprentissage fréquence IA)


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.26 CALENDAR_EVENTS


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS evenements_planning (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    date_fin TIMESTAMP WITH TIME ZONE,
    lieu VARCHAR(200),
    type_event VARCHAR(50) NOT NULL DEFAULT 'autre',
    couleur VARCHAR(20),
    rappel_avant_minutes INTEGER,
    -- Récurrence
    recurrence_type VARCHAR(20),
    recurrence_interval INTEGER DEFAULT 1,
    recurrence_jours VARCHAR(20),
    recurrence_fin DATE,
    parent_event_id INTEGER REFERENCES evenements_planning(id),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_event_rappel_positif CHECK (
        rappel_avant_minutes IS NULL
        OR rappel_avant_minutes >= 0
    )
);
CREATE INDEX IF NOT EXISTS ix_calendar_events_date_debut ON evenements_planning(date_debut);
CREATE INDEX IF NOT EXISTS ix_calendar_events_type ON evenements_planning(type_event);
CREATE INDEX IF NOT EXISTS idx_date_type ON evenements_planning(date_debut, type_event);
CREATE INDEX IF NOT EXISTS idx_date_range ON evenements_planning(date_debut, date_fin);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.27 FURNITURE


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.28 HOUSE_EXPENSES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.29 ECO_ACTIONS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.30 MAINTENANCE_TASKS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.31 HOUSE_STOCKS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.32 USER_PREFERENCES


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preferences_utilisateurs (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    nb_adultes INTEGER NOT NULL DEFAULT 2,
    jules_present BOOLEAN NOT NULL DEFAULT TRUE,
    jules_age_mois INTEGER NOT NULL DEFAULT 19,
    temps_semaine VARCHAR(20) NOT NULL DEFAULT 'normal',
    temps_weekend VARCHAR(20) NOT NULL DEFAULT 'long',
    aliments_exclus JSONB NOT NULL DEFAULT '[]',
    aliments_favoris JSONB NOT NULL DEFAULT '[]',
    aliments_exclus_jules JSONB NOT NULL DEFAULT '[]',
    poisson_par_semaine INTEGER NOT NULL DEFAULT 2,
    vegetarien_par_semaine INTEGER NOT NULL DEFAULT 1,
    viande_rouge_max INTEGER NOT NULL DEFAULT 2,
    robots JSONB NOT NULL DEFAULT '[]',
    magasins_preferes JSONB NOT NULL DEFAULT '[]',
    taille_vetements_anne JSONB NOT NULL DEFAULT '{}',
    taille_vetements_mathieu JSONB NOT NULL DEFAULT '{}',
    style_achats_anne JSONB NOT NULL DEFAULT '{}',
    style_achats_mathieu JSONB NOT NULL DEFAULT '{}',
    interets_gaming JSONB NOT NULL DEFAULT '[]',
    interets_culture JSONB NOT NULL DEFAULT '[]',
    equipement_activites JSONB NOT NULL DEFAULT '{}',
    config_garde JSONB NOT NULL DEFAULT '{}',
    config_dashboard JSONB NOT NULL DEFAULT '{}',
    preferences_apprises JSONB NOT NULL DEFAULT '{}',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_preferences_user_id ON preferences_utilisateurs(user_id);
CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id ON preferences_utilisateurs(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.33 OPENFOODFACTS_CACHE


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS openfoodfacts_cache (
    id SERIAL PRIMARY KEY,
    code_barres VARCHAR(50) NOT NULL,
    nom VARCHAR(300),
    marque VARCHAR(200),
    categorie VARCHAR(200),
    nutriscore VARCHAR(1),
    nova_group INTEGER,
    ecoscore VARCHAR(1),
    nutrition_data JSONB,
    allergenes JSONB DEFAULT '[]',
    image_url VARCHAR(500),
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_openfoodfacts_code ON openfoodfacts_cache(code_barres);
CREATE INDEX IF NOT EXISTS ix_openfoodfacts_code ON openfoodfacts_cache(code_barres);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.34 DEPENSES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.35 BUDGETS_MENSUELS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.36 ALERTES_METEO


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alertes_meteo (
    id BIGSERIAL PRIMARY KEY,
    type_alerte VARCHAR(30) NOT NULL,
    niveau VARCHAR(20) NOT NULL DEFAULT 'info',
    titre VARCHAR(200) NOT NULL,
    message TEXT,
    conseil_jardin TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    temperature NUMERIC(5, 2),
    lu BOOLEAN NOT NULL DEFAULT FALSE,
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_alertes_meteo_type ON alertes_meteo(type_alerte);
CREATE INDEX IF NOT EXISTS ix_alertes_meteo_date ON alertes_meteo(date_debut);
CREATE INDEX IF NOT EXISTS ix_alertes_meteo_user ON alertes_meteo(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.37 CONFIG_METEO


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS config_meteo (
    id BIGSERIAL PRIMARY KEY,
    latitude NUMERIC(10, 7) NOT NULL DEFAULT 48.8566,
    longitude NUMERIC(10, 7) NOT NULL DEFAULT 2.3522,
    ville VARCHAR(100) NOT NULL DEFAULT 'Paris',
    surface_jardin_m2 NUMERIC(10, 2) NOT NULL DEFAULT 50,
    notifications_gel BOOLEAN NOT NULL DEFAULT TRUE,
    notifications_canicule BOOLEAN NOT NULL DEFAULT TRUE,
    notifications_pluie BOOLEAN NOT NULL DEFAULT TRUE,
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_config_meteo_user ON config_meteo(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.38 BACKUPS


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sauvegardes (
    id BIGSERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    tables_included JSONB DEFAULT '[]',
    row_counts JSONB DEFAULT '{}',
    size_bytes BIGINT NOT NULL DEFAULT 0,
    compressed BOOLEAN NOT NULL DEFAULT TRUE,
    storage_path VARCHAR(500),
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    user_id UUID,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_backups_user ON sauvegardes(user_id);
CREATE INDEX IF NOT EXISTS ix_backups_cree_le ON sauvegardes(cree_le);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.39 ACTION_HISTORY


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historique_actions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BIGINT,
    entity_name VARCHAR(255),
    description TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    cree_le TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS logs_securite (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    ip VARCHAR(45),
    user_agent VARCHAR(500),
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_logs_securite_user_id ON logs_securite(user_id);
CREATE INDEX IF NOT EXISTS ix_logs_securite_event_type ON logs_securite(event_type);
CREATE INDEX IF NOT EXISTS ix_logs_securite_created_at ON logs_securite(created_at);
CREATE INDEX IF NOT EXISTS ix_logs_securite_event_type_created_at ON logs_securite(event_type, created_at);
CREATE INDEX IF NOT EXISTS ix_logs_securite_user_created_at ON logs_securite(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_action_history_user_id ON historique_actions(user_id);
CREATE INDEX IF NOT EXISTS idx_action_history_action_type ON historique_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_action_history_cree_le ON historique_actions(cree_le DESC);
CREATE INDEX IF NOT EXISTS idx_action_history_entity ON historique_actions(entity_type, entity_id);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.40 CALENDRIERS_EXTERNES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.41 PUSH_SUBSCRIPTIONS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.42 NOTIFICATION_PREFERENCES


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.42b WEBHOOKS_ABONNEMENTS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.42c ETATS_PERSISTANTS


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS etats_persistants (
    id SERIAL PRIMARY KEY,
    namespace VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL,
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_pstate_namespace_user UNIQUE (namespace, user_id)
);
CREATE INDEX IF NOT EXISTS ix_pstate_namespace ON etats_persistants(namespace);
CREATE INDEX IF NOT EXISTS ix_pstate_user ON etats_persistants(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.43 EXTERNAL_CALENDAR_CONFIGS


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.44 PLANS_JARDIN


-- ─────────────────────────────────────────────────────────────────────────────
-- 3.45 PIECES_MAISON


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.01 GARMIN_TOKENS (→ profils_utilisateurs)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.02 GARMIN_ACTIVITIES (→ profils_utilisateurs)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.03 GARMIN_DAILY_SUMMARIES (→ profils_utilisateurs)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.04 FOOD_LOGS (→ profils_utilisateurs)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.04B GAMIFICATION_POINTS (→ profils_utilisateurs)


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS points_utilisateurs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    semaine_debut DATE NOT NULL,
    points_sport INTEGER NOT NULL DEFAULT 0,
    points_alimentation INTEGER NOT NULL DEFAULT 0,
    points_anti_gaspi INTEGER NOT NULL DEFAULT 0,
    total_points INTEGER NOT NULL DEFAULT 0,
    details JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_points_utilisateur_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_points_user_semaine ON points_utilisateurs(user_id, semaine_debut);
CREATE INDEX IF NOT EXISTS ix_points_utilisateurs_user ON points_utilisateurs(user_id);
CREATE INDEX IF NOT EXISTS ix_points_utilisateurs_semaine ON points_utilisateurs(semaine_debut);


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.04C GAMIFICATION_BADGES (→ profils_utilisateurs)


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS badges_utilisateurs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    badge_type VARCHAR(100) NOT NULL,
    badge_label VARCHAR(150) NOT NULL,
    acquis_le DATE NOT NULL DEFAULT CURRENT_DATE,
    meta JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_badges_utilisateur_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_badges_user_type_date ON badges_utilisateurs(user_id, badge_type, acquis_le);
CREATE INDEX IF NOT EXISTS ix_badges_utilisateurs_user ON badges_utilisateurs(user_id);
CREATE INDEX IF NOT EXISTS ix_badges_utilisateurs_type ON badges_utilisateurs(badge_type);


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.04D AUTOMATIONS (→ profils_utilisateurs)


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS automations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    nom VARCHAR(150) NOT NULL,
    declencheur JSONB NOT NULL,
    action JSONB NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    derniere_execution TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_automations_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_automations_user ON automations(user_id);
CREATE INDEX IF NOT EXISTS ix_automations_active ON automations(active);


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.04E JOB_EXECUTIONS (historique cron & exécutions manuelles admin)

-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.04F IA_SUGGESTIONS_HISTORIQUE (historique des suggestions IA)

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ia_suggestions_historique (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    type_suggestion VARCHAR(100) NOT NULL,
    module VARCHAR(100) NOT NULL,
    prompt_resume TEXT,
    suggestion JSONB NOT NULL DEFAULT '{}'::jsonb,
    contexte JSONB DEFAULT '{}'::jsonb,
    modele_ia VARCHAR(100),
    tokens_utilises INTEGER,
    duree_ms INTEGER,
    acceptee BOOLEAN,
    feedback_note INTEGER,
    feedback_texte TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_ia_feedback_note CHECK (feedback_note IS NULL OR (feedback_note >= 1 AND feedback_note <= 5)),
    CONSTRAINT ck_ia_type_suggestion CHECK (type_suggestion IN (
        'recette', 'planning', 'courses', 'activite', 'entretien',
        'diagnostic', 'voyage', 'cadeau', 'travaux', 'budget',
        'anti_gaspillage', 'batch_cooking', 'weekend', 'jules',
        'chat', 'proactive', 'autre'
    ))
);
CREATE INDEX IF NOT EXISTS ix_ia_suggestions_user ON ia_suggestions_historique(user_id);
CREATE INDEX IF NOT EXISTS ix_ia_suggestions_type ON ia_suggestions_historique(type_suggestion);
CREATE INDEX IF NOT EXISTS ix_ia_suggestions_module ON ia_suggestions_historique(module);
CREATE INDEX IF NOT EXISTS ix_ia_suggestions_created ON ia_suggestions_historique(cree_le DESC);
CREATE INDEX IF NOT EXISTS ix_ia_suggestions_acceptee ON ia_suggestions_historique(acceptee)
    WHERE acceptee IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ia_suggestions_user_type_date ON ia_suggestions_historique(user_id, type_suggestion, cree_le DESC);


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.05 RECETTE_INGREDIENTS (→ recettes, ingredients)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.06 ETAPES_RECETTE (→ recettes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.07 VERSIONS_RECETTE (→ recettes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.08 HISTORIQUE_RECETTES (→ recettes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.09 BATCH_MEALS (→ recettes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.10 RECIPE_FEEDBACKS (→ recettes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.11 INVENTAIRE (→ ingredients)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.12 HISTORIQUE_INVENTAIRE (→ inventaire, ingredients)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.13 ARTICLES_COURSES (→ listes_courses, ingredients)
-- Anciennement liste_courses. Renommé en articles_courses pour cohérence.


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.14 ARTICLES_MODELES (→ modeles_courses, ingredients)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.15 REPAS (→ plannings, recettes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.16 TEMPLATE_ITEMS (→ templates_semaine)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.17 WELLBEING_ENTRIES (→ profils_enfants)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.18 MILESTONES (→ profils_enfants)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.19 HEALTH_ENTRIES (→ routines_sante)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.20 PROJECT_TASKS (→ projets)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.21 ROUTINE_TASKS (→ routines)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.22 GARDEN_LOGS (→ elements_jardin)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.23 JEUX_MATCHS (→ jeux_equipes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.24 JEUX_PARIS_SPORTIFS (→ jeux_matchs)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.25 JEUX_GRILLES_LOTO (→ jeux_tirages_loto)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.26 JEUX_ALERTES (→ jeux_series)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.27 SESSIONS_BATCH_COOKING (→ plannings)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.28 ETAPES_BATCH_COOKING (→ sessions_batch_cooking, recettes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.29 PREPARATIONS_BATCH (→ sessions_batch_cooking, recettes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.30 EVENEMENTS_CALENDRIER (→ calendriers_externes)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.31 ZONES_JARDIN (→ plans_jardin)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.32 PLANTES_JARDIN (→ zones_jardin)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.33 ACTIONS_PLANTES (→ plantes_jardin)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.34 OBJETS_MAISON (→ pieces_maison)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.35 SESSIONS_TRAVAIL


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.36 VERSIONS_PIECES


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.37 COUTS_TRAVAUX (→ versions_pieces)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.38 LOGS_STATUT_OBJETS


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX VACCINS (→ profils_enfants) — Carnet de santé numérique


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX RENDEZ_VOUS_MEDICAUX — Suivi médical famille


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX MESURES_CROISSANCE (→ profils_enfants) — Courbes OMS


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX NORMES_OMS — Retirée du schéma actif
-- La courbe de croissance OMS n'est plus une fonctionnalité produit exposée.
-- Le suivi Jules reste centré sur les jalons, l'alimentation, les activités
-- et le carnet vaccinal à partir de 6 ans.


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX CONTACTS_FAMILLE — Répertoire familial


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX ANNIVERSAIRES_FAMILLE — Dates importantes et rappels


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX CHECKLISTS_ANNIVERSAIRE — Listes de tâches pour préparer les anniversaires


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checklists_anniversaire (
    id SERIAL PRIMARY KEY,
    anniversaire_id INTEGER NOT NULL REFERENCES anniversaires_famille(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    budget_total FLOAT,
    date_limite DATE,
    completee BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    maj_auto_le TIMESTAMP,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_checklists_anniversaire_anniversaire_id ON checklists_anniversaire(anniversaire_id);
CREATE INDEX IF NOT EXISTS ix_checklists_anniversaire_completee ON checklists_anniversaire(completee);

CREATE TABLE IF NOT EXISTS items_checklist_anniversaire (
    id SERIAL PRIMARY KEY,
    checklist_id INTEGER NOT NULL REFERENCES checklists_anniversaire(id) ON DELETE CASCADE,
    categorie VARCHAR(50) NOT NULL,
    libelle VARCHAR(300) NOT NULL,
    budget_estime FLOAT,
    budget_reel FLOAT,
    fait BOOLEAN NOT NULL DEFAULT FALSE,
    priorite VARCHAR(20) NOT NULL DEFAULT 'moyenne',
    responsable VARCHAR(50),
    quand VARCHAR(20),
    source VARCHAR(20) NOT NULL DEFAULT 'manuel',
    score_pertinence FLOAT,
    raison_suggestion TEXT,
    ordre INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_items_checklist_anniversaire_checklist_id ON items_checklist_anniversaire(checklist_id);
CREATE INDEX IF NOT EXISTS ix_items_checklist_anniversaire_categorie ON items_checklist_anniversaire(categorie);
CREATE INDEX IF NOT EXISTS ix_items_checklist_anniversaire_fait ON items_checklist_anniversaire(fait);
CREATE INDEX IF NOT EXISTS ix_items_checklist_anniversaire_source ON items_checklist_anniversaire(source);


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX EVENEMENTS_FAMILIAUX — Calendrier partagé


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX VOYAGES — Mode voyage famille


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX TEMPLATES_CHECKLIST — Templates de checklists réutilisables


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX CHECKLISTS_VOYAGE (→ voyages, templates_checklist)


-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX DOCUMENTS_FAMILLE — Coffre-fort numérique


-- ─────────────────────────────────────────────────────────────────────────────
-- 5.01 PREFERENCES_HOME


-- ─────────────────────────────────────────────────────────────────────────────
-- 5.02 TACHES_HOME (→ zones_jardin, pieces_maison)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5.03 STATS_HOME


-- ─────────────────────────────────────────────────────────────────────────────
-- 5.04 PLANTES_CATALOGUE


-- ─────────────────────────────────────────────────────────────────────────────
-- 5.05 RECOLTES (→ plantes_jardin, zones_jardin)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5.06 OBJECTIFS_AUTONOMIE


-- ─────────────────────────────────────────────────────────────────────────────
-- 5.07 DEPENSES_HOME


-- ─────────────────────────────────────────────────────────────────────────────
-- 5.08 BUDGETS_HOME


-- ─────────────────────────────────────────────────────────────────────────────
-- 5B.01 JEUX_TIRAGES_EUROMILLIONS


-- ─────────────────────────────────────────────────────────────────────────────
-- 5B.02 JEUX_GRILLES_EUROMILLIONS (→ jeux_tirages_euromillions)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5B.03 JEUX_STATS_EUROMILLIONS


-- ─────────────────────────────────────────────────────────────────────────────
-- 5B.04 JEUX_COTES_HISTORIQUE (→ jeux_matchs)


-- ─────────────────────────────────────────────────────────────────────────────
-- BANKROLL HISTORIQUE 


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_bankroll_historique (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    montant FLOAT NOT NULL,
    variation FLOAT NOT NULL DEFAULT 0.0,
    date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_bankroll_historique_user ON jeux_bankroll_historique(user_id, date DESC);

-- ============================================================================
-- PARTIE 5C : TABLES MAISON EXTENSIONS (artisans, cellier, diagnostics, etc.)
-- ============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.01 ARTISANS


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.02 INTERVENTIONS_ARTISANS (→ artisans)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.06 ARTICLES_CELLIER


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.07 DIAGNOSTICS_MAISON


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.08 ESTIMATIONS_IMMOBILIERES


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.09 CHECKLISTS_VACANCES


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.10 ITEMS_CHECKLIST (→ checklists_vacances)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.11 TRAITEMENTS_NUISIBLES (→ artisans)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.12 DEVIS_COMPARATIFS (→ projets, artisans)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.13 LIGNES_DEVIS (→ devis_comparatifs)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.14 ENTRETIENS_SAISONNIERS (→ artisans)


-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.15 RELEVES_COMPTEURS


-- ─────────────────────────────────────────────────────────────────────────────
-- 5D.01 NOTES_MEMOS


-- ─────────────────────────────────────────────────────────────────────────────
-- 5D.02 JOURNAL_BORD


-- ─────────────────────────────────────────────────────────────────────────────
-- 5D.03 CONTACTS_UTILES


-- ─────────────────────────────────────────────────────────────────────────────
-- 5D.04 LIENS_FAVORIS


-- ─────────────────────────────────────────────────────────────────────────────
-- 5D.05 MOTS_DE_PASSE_MAISON


-- ─────────────────────────────────────────────────────────────────────────────
-- 5D.06 PRESSE_PAPIER_ENTREES


-- ─────────────────────────────────────────────────────────────────────────────
-- 5D.07 RELEVES_ENERGIE


-- Source: 04_cuisine.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Cuisine
-- ============================================================================
-- Contient : ingredients, recettes, inventaire, listes_courses, plannings,
--            modeles_courses, templates_semaine, batch_cooking, ...
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Table congélation — persistance des articles congelés
-- Remplace le stockage mémoire de congelation.py

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS batch_cooking_congelation (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_congelation DATE NOT NULL DEFAULT CURRENT_DATE,
    date_limite DATE NOT NULL,
    portions INTEGER NOT NULL DEFAULT 1,
    categorie VARCHAR(50) NOT NULL DEFAULT 'autre',
    recette_id INTEGER,
    session_id INTEGER,
    notes TEXT,
    consomme BOOLEAN NOT NULL DEFAULT FALSE,
    date_consommation DATE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_congelation_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT fk_congelation_session FOREIGN KEY (session_id) REFERENCES sessions_batch_cooking(id) ON DELETE SET NULL,
    CONSTRAINT ck_congelation_portions_positive CHECK (portions > 0),
    CONSTRAINT ck_congelation_categorie CHECK (categorie IN (
        'viande', 'poisson', 'legume', 'fruit', 'plat_cuisine',
        'soupe', 'sauce', 'pain', 'patisserie', 'herbes', 'autre'
    ))
);
CREATE INDEX IF NOT EXISTS ix_congelation_date_limite ON batch_cooking_congelation(date_limite);
CREATE INDEX IF NOT EXISTS ix_congelation_categorie ON batch_cooking_congelation(categorie);
CREATE INDEX IF NOT EXISTS ix_congelation_consomme ON batch_cooking_congelation(consomme);
CREATE INDEX IF NOT EXISTS ix_congelation_recette ON batch_cooking_congelation(recette_id);
CREATE INDEX IF NOT EXISTS idx_congelation_consomme_limite ON batch_cooking_congelation(consomme, date_limite)
    WHERE consomme = FALSE;


-- Source: 05_famille.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Famille
-- ============================================================================
-- Contient : profils_enfants, activités_famille, budgets_famille, Garmin,
--            santé, jalons, contacts, documents, anniversaires
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Abonnements maison (eau, électricité, gaz, assurances, téléphone, internet)

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historique_notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    canal VARCHAR(20) NOT NULL,
    titre VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    type_evenement VARCHAR(100),
    categorie VARCHAR(50) NOT NULL DEFAULT 'autres',
    lu BOOLEAN NOT NULL DEFAULT FALSE,
    action_effectuee VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_historique_notifications_user ON historique_notifications(user_id);
CREATE INDEX IF NOT EXISTS ix_historique_notifications_lu ON historique_notifications(user_id, lu);
CREATE INDEX IF NOT EXISTS ix_historique_notifications_categorie ON historique_notifications(categorie);
CREATE INDEX IF NOT EXISTS ix_historique_notifications_cree_le ON historique_notifications(cree_le DESC);


-- Source: 10_finances.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Finances
-- ============================================================================
-- Contient : depenses, budgets_mensuels, calendriers_externes,
--            configs_calendriers_externes, evenements_calendrier
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS minuteur_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    label VARCHAR(200) NOT NULL,
    duree_secondes INTEGER NOT NULL CHECK (duree_secondes > 0),
    recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL,
    date_debut TIMESTAMP,
    date_fin TIMESTAMP,
    terminee BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_minuteur_user_id ON minuteur_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_minuteur_active ON minuteur_sessions(active);
CREATE INDEX IF NOT EXISTS idx_minuteur_cree_le ON minuteur_sessions(cree_le DESC);
-- ============================================================================


-- Source: 12_triggers.sql


-- Source: 04_cuisine.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Cuisine
-- ============================================================================
-- Contient : ingredients, recettes, inventaire, listes_courses, plannings,
--            modeles_courses, templates_semaine, batch_cooking, ...
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100) NOT NULL DEFAULT 'Autre',
    unite VARCHAR(50) NOT NULL DEFAULT 'pièce',
    calories_pour_100g FLOAT,
    saison VARCHAR(50),
    allergene BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ingredients_nom ON ingredients(nom);
CREATE INDEX IF NOT EXISTS ix_ingredients_categorie ON ingredients(categorie);
CREATE INDEX IF NOT EXISTS ix_ingredients_saison ON ingredients(saison);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recettes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    -- Temps & Portions
    temps_preparation INTEGER NOT NULL DEFAULT 0,
    temps_cuisson INTEGER NOT NULL DEFAULT 0,
    portions INTEGER NOT NULL DEFAULT 4,
    difficulte VARCHAR(50) NOT NULL DEFAULT 'moyen',
    -- Catégorisation
    type_repas VARCHAR(50) NOT NULL DEFAULT 'dîner',
    saison VARCHAR(50) NOT NULL DEFAULT 'toute_année',
    categorie VARCHAR(100) NOT NULL DEFAULT 'Plat',
    -- Flags - Tags système
    est_rapide BOOLEAN NOT NULL DEFAULT FALSE,
    est_equilibre BOOLEAN NOT NULL DEFAULT FALSE,
    est_vegetarien BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_bebe BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_batch BOOLEAN NOT NULL DEFAULT FALSE,
    congelable BOOLEAN NOT NULL DEFAULT FALSE,
    -- Types de protéines
    type_proteines VARCHAR(100),
    -- Bio & Local
    est_bio BOOLEAN NOT NULL DEFAULT FALSE,
    est_local BOOLEAN NOT NULL DEFAULT FALSE,
    score_bio INTEGER NOT NULL DEFAULT 0,
    score_local INTEGER NOT NULL DEFAULT 0,
    -- Robots compatibles
    compatible_cookeo BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_monsieur_cuisine BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_airfryer BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_multicooker BOOLEAN NOT NULL DEFAULT FALSE,
    -- Nutrition
    calories INTEGER,
    proteines FLOAT,
    lipides FLOAT,
    glucides FLOAT,
    -- IA
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    score_ia FLOAT,
    -- Media
    url_image VARCHAR(500),
    url_source VARCHAR(500),
    -- Timestamps
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_temps_preparation_positif CHECK (temps_preparation >= 0),
    CONSTRAINT ck_temps_cuisson_positif CHECK (temps_cuisson >= 0),
    CONSTRAINT ck_portions_positive CHECK (portions > 0)
);
CREATE INDEX IF NOT EXISTS ix_recettes_nom ON recettes(nom);
CREATE INDEX IF NOT EXISTS ix_recettes_type_repas ON recettes(type_repas);
CREATE INDEX IF NOT EXISTS ix_recettes_saison ON recettes(saison);
CREATE INDEX IF NOT EXISTS ix_recettes_categorie ON recettes(categorie);
CREATE INDEX IF NOT EXISTS ix_recettes_est_rapide ON recettes(est_rapide);
CREATE INDEX IF NOT EXISTS ix_recettes_est_vegetarien ON recettes(est_vegetarien);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_bebe ON recettes(compatible_bebe);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_batch ON recettes(compatible_batch);
CREATE INDEX IF NOT EXISTS ix_recettes_est_bio ON recettes(est_bio);
CREATE INDEX IF NOT EXISTS ix_recettes_est_local ON recettes(est_local);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_cookeo ON recettes(compatible_cookeo);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_monsieur_cuisine ON recettes(compatible_monsieur_cuisine);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_airfryer ON recettes(compatible_airfryer);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plannings (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    semaine_debut DATE NOT NULL,
    semaine_fin DATE NOT NULL,
    etat VARCHAR(20) NOT NULL DEFAULT 'brouillon',
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- Compatibilité rerun / bases legacy : s'assurer que les colonnes existent
-- avant de créer les index associés.
ALTER TABLE IF EXISTS plannings
    ADD COLUMN IF NOT EXISTS etat VARCHAR(20) NOT NULL DEFAULT 'brouillon';
CREATE INDEX IF NOT EXISTS ix_plannings_semaine_debut ON plannings(semaine_debut);
CREATE INDEX IF NOT EXISTS ix_plannings_etat ON plannings(etat);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS listes_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    etat VARCHAR(20) NOT NULL DEFAULT 'brouillon',
    archivee BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- Compatibilité rerun / bases legacy : s'assurer que les colonnes existent
-- avant de créer les index associés.
ALTER TABLE IF EXISTS listes_courses
    ADD COLUMN IF NOT EXISTS etat VARCHAR(20) NOT NULL DEFAULT 'brouillon',
    ADD COLUMN IF NOT EXISTS archivee BOOLEAN NOT NULL DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS ix_listes_courses_etat ON listes_courses(etat);
CREATE INDEX IF NOT EXISTS ix_listes_courses_archivee ON listes_courses(archivee);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS modeles_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    utilisateur_id VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    articles_data JSONB
);
CREATE INDEX IF NOT EXISTS ix_modeles_courses_nom ON modeles_courses(nom);
CREATE INDEX IF NOT EXISTS ix_modeles_courses_utilisateur_id ON modeles_courses(utilisateur_id);
CREATE INDEX IF NOT EXISTS ix_modeles_courses_actif ON modeles_courses(actif);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS templates_semaine (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS config_batch_cooking (
    id SERIAL PRIMARY KEY,
    jours_batch JSONB NOT NULL DEFAULT '[6]',
    heure_debut_preferee TIME DEFAULT '10:00',
    duree_max_session INTEGER NOT NULL DEFAULT 180,
    avec_jules_par_defaut BOOLEAN NOT NULL DEFAULT TRUE,
    robots_disponibles JSONB NOT NULL DEFAULT '["four", "plaques"]',
    preferences_stockage JSONB,
    objectif_portions_semaine INTEGER NOT NULL DEFAULT 20,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_config_batch_duree_positive CHECK (duree_max_session > 0),
    CONSTRAINT ck_config_batch_objectif_positif CHECK (objectif_portions_semaine > 0)
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recette_ingredients (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantite FLOAT NOT NULL,
    unite VARCHAR(50) NOT NULL,
    optionnel BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_recette_ing_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT fk_recette_ing_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_positive CHECK (quantite > 0)
);
CREATE INDEX IF NOT EXISTS ix_recette_ingredients_recette ON recette_ingredients(recette_id);
CREATE INDEX IF NOT EXISTS ix_recette_ingredients_ingredient ON recette_ingredients(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_recette_ingredients_ingredient_id ON recette_ingredients(ingredient_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS etapes_recette (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    ordre INTEGER NOT NULL,
    titre VARCHAR(200),
    description TEXT NOT NULL,
    duree INTEGER,
    robots_optionnels JSONB,
    temperature INTEGER,
    est_supervision BOOLEAN DEFAULT FALSE,
    groupe_parallele INTEGER DEFAULT 0,
    CONSTRAINT fk_etapes_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_ordre_positif CHECK (ordre > 0)
);
CREATE INDEX IF NOT EXISTS ix_etapes_recette_recette ON etapes_recette(recette_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS versions_recette (
    id SERIAL PRIMARY KEY,
    recette_base_id INTEGER NOT NULL,
    type_version VARCHAR(50) NOT NULL,
    instructions_modifiees TEXT,
    ingredients_modifies JSONB,
    notes_bebe TEXT,
    etapes_paralleles_batch JSONB,
    temps_optimise_batch INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_versions_recette FOREIGN KEY (recette_base_id) REFERENCES recettes(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_versions_recette_base ON versions_recette(recette_base_id);
CREATE INDEX IF NOT EXISTS ix_versions_recette_type ON versions_recette(type_version);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historique_recettes (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    date_preparation DATE NOT NULL,
    portions_cuisinees INTEGER NOT NULL DEFAULT 1,
    note INTEGER,
    avis TEXT,
    feedback VARCHAR(20) DEFAULT 'neutral',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_historique_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_note_valide CHECK (
        note IS NULL
        OR (
            note >= 0
            AND note <= 5
        )
    ),
    CONSTRAINT ck_portions_cuisinees_positive CHECK (portions_cuisinees > 0)
);
-- Compatibilité rerun / bases legacy : garantir les colonnes indexées avant
-- la création des index sur un schéma déjà existant.
ALTER TABLE IF EXISTS historique_recettes
    ADD COLUMN IF NOT EXISTS date_preparation DATE DEFAULT CURRENT_DATE,
    ADD COLUMN IF NOT EXISTS portions_cuisinees INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS feedback VARCHAR(20) DEFAULT 'neutral';
CREATE INDEX IF NOT EXISTS ix_historique_recettes_recette ON historique_recettes(recette_id);
CREATE INDEX IF NOT EXISTS ix_historique_recettes_date ON historique_recettes(date_preparation);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS repas_batch (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions_creees INTEGER NOT NULL DEFAULT 4,
    portions_restantes INTEGER NOT NULL DEFAULT 4,
    date_preparation DATE NOT NULL,
    date_peremption DATE NOT NULL,
    container_type VARCHAR(100),
    localisation VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_batch_meals_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL
);
-- Compatibilité rerun / bases legacy : garantir les colonnes indexées avant
-- la création des index sur un schéma déjà existant.
ALTER TABLE IF EXISTS repas_batch
    ADD COLUMN IF NOT EXISTS date_preparation DATE DEFAULT CURRENT_DATE,
    ADD COLUMN IF NOT EXISTS date_peremption DATE,
    ADD COLUMN IF NOT EXISTS portions_creees INTEGER NOT NULL DEFAULT 4,
    ADD COLUMN IF NOT EXISTS portions_restantes INTEGER NOT NULL DEFAULT 4,
    ADD COLUMN IF NOT EXISTS localisation VARCHAR(200);
CREATE INDEX IF NOT EXISTS ix_batch_meals_recette ON repas_batch(recette_id);
CREATE INDEX IF NOT EXISTS ix_batch_meals_date_prep ON repas_batch(date_preparation);
CREATE INDEX IF NOT EXISTS ix_batch_meals_date_peremption ON repas_batch(date_peremption);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS retours_recettes (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    recette_id INTEGER NOT NULL,
    feedback VARCHAR(20) NOT NULL DEFAULT 'neutral',
    contexte VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_recipe_feedbacks_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_feedback_type CHECK (feedback IN ('like', 'dislike', 'neutral'))
);
CREATE INDEX IF NOT EXISTS ix_recipe_feedbacks_user ON retours_recettes(user_id);
CREATE INDEX IF NOT EXISTS ix_recipe_feedbacks_recette ON retours_recettes(recette_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_recipe_feedback ON retours_recettes(user_id, recette_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventaire (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 0.0,
    quantite_min FLOAT NOT NULL DEFAULT 1.0,
    emplacement VARCHAR(100),
    date_peremption DATE,
    derniere_maj TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    photo_url VARCHAR(500),
    photo_filename VARCHAR(200),
    photo_uploaded_at TIMESTAMP WITH TIME ZONE,
    code_barres VARCHAR(50),
    prix_unitaire FLOAT,
    CONSTRAINT fk_inventaire_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_inventaire_positive CHECK (quantite >= 0),
    CONSTRAINT ck_seuil_positif CHECK (quantite_min >= 0)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_inventaire_ingredient ON inventaire(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_inventaire_ingredient ON inventaire(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_inventaire_emplacement ON inventaire(emplacement);
CREATE INDEX IF NOT EXISTS ix_inventaire_peremption ON inventaire(date_peremption);
CREATE INDEX IF NOT EXISTS ix_inventaire_derniere_maj ON inventaire(derniere_maj);
CREATE UNIQUE INDEX IF NOT EXISTS uq_code_barres ON inventaire(code_barres);
CREATE INDEX IF NOT EXISTS ix_inventaire_code_barres ON inventaire(code_barres);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historique_inventaire (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    type_modification VARCHAR(50) NOT NULL,
    quantite_avant FLOAT,
    quantite_apres FLOAT,
    quantite_min_avant FLOAT,
    quantite_min_apres FLOAT,
    date_peremption_avant DATE,
    date_peremption_apres DATE,
    emplacement_avant VARCHAR(100),
    emplacement_apres VARCHAR(100),
    date_modification TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    utilisateur VARCHAR(100),
    notes TEXT,
    CONSTRAINT fk_hist_inv_article FOREIGN KEY (article_id) REFERENCES inventaire(id) ON DELETE CASCADE,
    CONSTRAINT fk_hist_inv_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_article ON historique_inventaire(article_id);
CREATE INDEX IF NOT EXISTS idx_historique_inventaire_article_id ON historique_inventaire(article_id);
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_ingredient ON historique_inventaire(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_type ON historique_inventaire(type_modification);
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_date ON historique_inventaire(date_modification);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles_courses (
    id SERIAL PRIMARY KEY,
    liste_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantite_necessaire FLOAT NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    achete BOOLEAN NOT NULL DEFAULT FALSE,
    suggere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    achete_le TIMESTAMP WITH TIME ZONE,
    rayon_magasin VARCHAR(100),
    magasin_cible VARCHAR(50),
    prix_unitaire FLOAT,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_articles_courses_liste FOREIGN KEY (liste_id) REFERENCES listes_courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_articles_courses_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_articles_courses_positive CHECK (quantite_necessaire > 0)
);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_id ON articles_courses(liste_id);
CREATE INDEX IF NOT EXISTS ix_articles_courses_ingredient_id ON articles_courses(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_articles_courses_priorite ON articles_courses(priorite);
CREATE INDEX IF NOT EXISTS ix_articles_courses_achete ON articles_courses(achete);
CREATE INDEX IF NOT EXISTS ix_articles_courses_cree_le ON articles_courses(cree_le);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles_modeles (
    id SERIAL PRIMARY KEY,
    modele_id INTEGER NOT NULL,
    ingredient_id INTEGER,
    nom_article VARCHAR(100) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1.0,
    unite VARCHAR(20) NOT NULL DEFAULT 'pièce',
    rayon_magasin VARCHAR(100) NOT NULL DEFAULT 'Autre',
    priorite VARCHAR(20) NOT NULL DEFAULT 'moyenne',
    notes TEXT,
    ordre INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_articles_modeles_modele FOREIGN KEY (modele_id) REFERENCES modeles_courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_articles_modeles_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_article_modele_quantite_positive CHECK (quantite > 0),
        CONSTRAINT ck_article_modele_priorite_valide CHECK (
            priorite IN ('haute', 'moyenne', 'basse')
        )
);
CREATE INDEX IF NOT EXISTS ix_articles_modeles_modele ON articles_modeles(modele_id);
CREATE INDEX IF NOT EXISTS ix_articles_modeles_ingredient ON articles_modeles(ingredient_id);


-- ─── Correspondances Carrefour Drive ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS correspondances_drive (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER,
    nom_article VARCHAR(200) NOT NULL,
    produit_drive_id VARCHAR(100) NOT NULL,
    produit_drive_nom VARCHAR(300) NOT NULL,
    produit_drive_ean VARCHAR(50),
    produit_drive_url VARCHAR(500),
    quantite_par_defaut FLOAT NOT NULL DEFAULT 1.0,
    nb_utilisations INTEGER NOT NULL DEFAULT 0,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_correspondances_drive_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE SET NULL,
    CONSTRAINT ck_correspondance_drive_quantite_positive CHECK (quantite_par_defaut > 0)
);
CREATE INDEX IF NOT EXISTS ix_correspondances_drive_nom_article ON correspondances_drive(nom_article);
CREATE INDEX IF NOT EXISTS ix_correspondances_drive_produit_id ON correspondances_drive(produit_drive_id);
CREATE INDEX IF NOT EXISTS ix_correspondances_drive_ingredient ON correspondances_drive(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_correspondances_drive_actif ON correspondances_drive(actif);
CREATE UNIQUE INDEX IF NOT EXISTS ix_correspondances_drive_article_produit ON correspondances_drive(nom_article, produit_drive_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS repas (
    id SERIAL PRIMARY KEY,
    planning_id INTEGER NOT NULL,
    recette_id INTEGER,
    date_repas DATE NOT NULL,
    type_repas VARCHAR(50) NOT NULL DEFAULT 'dîner',
    portion_ajustee INTEGER,
    prepare BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    entree VARCHAR(200),
    entree_recette_id INTEGER,
    dessert VARCHAR(200),
    dessert_recette_id INTEGER,
    dessert_jules VARCHAR(200),
    dessert_jules_recette_id INTEGER,
    plat_jules TEXT,
    notes_jules TEXT,
    adaptation_auto BOOLEAN NOT NULL DEFAULT TRUE,
    contexte_meteo VARCHAR(50),
    CONSTRAINT fk_repas_planning FOREIGN KEY (planning_id) REFERENCES plannings(id) ON DELETE CASCADE,
    CONSTRAINT fk_repas_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL,
        CONSTRAINT fk_repas_entree_recette FOREIGN KEY (entree_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
        CONSTRAINT fk_repas_dessert_recette FOREIGN KEY (dessert_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
        CONSTRAINT fk_repas_dessert_jules_recette FOREIGN KEY (dessert_jules_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
        CONSTRAINT ck_repas_portions_valides CHECK (
            portion_ajustee IS NULL
            OR (
                portion_ajustee > 0
                AND portion_ajustee <= 20
            )
        )
);
CREATE INDEX IF NOT EXISTS ix_repas_planning ON repas(planning_id);
CREATE INDEX IF NOT EXISTS idx_repas_planning_id ON repas(planning_id);
CREATE INDEX IF NOT EXISTS ix_repas_recette ON repas(recette_id);
CREATE INDEX IF NOT EXISTS ix_repas_date ON repas(date_repas);
CREATE INDEX IF NOT EXISTS ix_repas_type ON repas(type_repas);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS elements_templates (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    jour_semaine INTEGER NOT NULL,
    heure_debut VARCHAR(5) NOT NULL,
    heure_fin VARCHAR(5),
    titre VARCHAR(200) NOT NULL,
    type_event VARCHAR(50) DEFAULT 'autre',
    lieu VARCHAR(200),
    couleur VARCHAR(20),
    CONSTRAINT fk_template_items_template FOREIGN KEY (template_id) REFERENCES templates_semaine(id) ON DELETE CASCADE,
    CONSTRAINT ck_template_jour_valide CHECK (
        jour_semaine >= 0
        AND jour_semaine <= 6
    )
);
CREATE INDEX IF NOT EXISTS idx_template_jour ON elements_templates(template_id, jour_semaine);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions_batch_cooking (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_session DATE NOT NULL,
    heure_debut TIME,
    heure_fin TIME,
    duree_estimee INTEGER NOT NULL DEFAULT 120,
    duree_reelle INTEGER,
    statut VARCHAR(20) NOT NULL DEFAULT 'planifiee',
    avec_jules BOOLEAN NOT NULL DEFAULT FALSE,
    planning_id INTEGER,
    recettes_selectionnees JSONB,
    robots_utilises JSONB,
    notes_avant TEXT,
    notes_apres TEXT,
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    nb_portions_preparees INTEGER NOT NULL DEFAULT 0,
    nb_recettes_completees INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_sessions_batch_planning FOREIGN KEY (planning_id) REFERENCES plannings(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_session_duree_estimee_positive CHECK (duree_estimee > 0),
        CONSTRAINT ck_session_duree_reelle_positive CHECK (
            duree_reelle IS NULL
            OR duree_reelle > 0
        ),
        CONSTRAINT ck_session_portions_positive CHECK (nb_portions_preparees >= 0),
        CONSTRAINT ck_session_recettes_positive CHECK (nb_recettes_completees >= 0)
);
CREATE INDEX IF NOT EXISTS ix_sessions_batch_date ON sessions_batch_cooking(date_session);
CREATE INDEX IF NOT EXISTS ix_sessions_batch_statut ON sessions_batch_cooking(statut);
CREATE INDEX IF NOT EXISTS ix_sessions_batch_planning ON sessions_batch_cooking(planning_id);
CREATE INDEX IF NOT EXISTS idx_session_date_statut ON sessions_batch_cooking(date_session, statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS etapes_batch_cooking (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    recette_id INTEGER,
    ordre INTEGER NOT NULL,
    groupe_parallele INTEGER NOT NULL DEFAULT 0,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    duree_minutes INTEGER NOT NULL DEFAULT 10,
    duree_reelle INTEGER,
    robots_requis JSONB,
    est_supervision BOOLEAN NOT NULL DEFAULT FALSE,
    alerte_bruit BOOLEAN NOT NULL DEFAULT FALSE,
    temperature INTEGER,
    statut VARCHAR(20) NOT NULL DEFAULT 'a_faire',
    heure_debut TIMESTAMP WITH TIME ZONE,
    heure_fin TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    timer_actif BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_etapes_batch_session FOREIGN KEY (session_id) REFERENCES sessions_batch_cooking(id) ON DELETE CASCADE,
    CONSTRAINT fk_etapes_batch_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_etape_batch_ordre_positif CHECK (ordre > 0),
        CONSTRAINT ck_etape_batch_duree_positive CHECK (duree_minutes > 0),
        CONSTRAINT ck_etape_batch_duree_reelle_positive CHECK (
            duree_reelle IS NULL
            OR duree_reelle > 0
        )
);
CREATE INDEX IF NOT EXISTS ix_etapes_batch_session ON etapes_batch_cooking(session_id);
CREATE INDEX IF NOT EXISTS ix_etapes_batch_recette ON etapes_batch_cooking(recette_id);
CREATE INDEX IF NOT EXISTS idx_etape_session_ordre ON etapes_batch_cooking(session_id, ordre);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preparations_batch (
    id SERIAL PRIMARY KEY,
    session_id INTEGER,
    recette_id INTEGER,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions_initiales INTEGER NOT NULL DEFAULT 4,
    portions_restantes INTEGER NOT NULL DEFAULT 4,
    date_preparation DATE NOT NULL,
    date_peremption DATE NOT NULL,
    localisation VARCHAR(50) NOT NULL DEFAULT 'frigo',
    container VARCHAR(100),
    etagere VARCHAR(50),
    repas_attribues JSONB,
    notes TEXT,
    photo_url VARCHAR(500),
    consomme BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_prep_batch_session FOREIGN KEY (session_id) REFERENCES sessions_batch_cooking(id) ON DELETE
    SET NULL,
        CONSTRAINT fk_prep_batch_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_prep_portions_initiales_positive CHECK (portions_initiales > 0),
        CONSTRAINT ck_prep_portions_restantes_positive CHECK (portions_restantes >= 0)
);
-- Compatibilité rerun / bases legacy : garantir les colonnes indexées avant
-- la création des index sur un schéma déjà existant.
ALTER TABLE IF EXISTS preparations_batch
    ADD COLUMN IF NOT EXISTS date_preparation DATE DEFAULT CURRENT_DATE,
    ADD COLUMN IF NOT EXISTS date_peremption DATE,
    ADD COLUMN IF NOT EXISTS localisation VARCHAR(50) DEFAULT 'frigo',
    ADD COLUMN IF NOT EXISTS consomme BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS portions_initiales INTEGER NOT NULL DEFAULT 4,
    ADD COLUMN IF NOT EXISTS portions_restantes INTEGER NOT NULL DEFAULT 4;
CREATE INDEX IF NOT EXISTS ix_prep_batch_session ON preparations_batch(session_id);
CREATE INDEX IF NOT EXISTS ix_prep_batch_recette ON preparations_batch(recette_id);
CREATE INDEX IF NOT EXISTS ix_prep_batch_date ON preparations_batch(date_preparation);
CREATE INDEX IF NOT EXISTS ix_prep_batch_peremption ON preparations_batch(date_peremption);
CREATE INDEX IF NOT EXISTS ix_prep_batch_localisation ON preparations_batch(localisation);
CREATE INDEX IF NOT EXISTS ix_prep_batch_consomme ON preparations_batch(consomme);
CREATE INDEX IF NOT EXISTS idx_prep_localisation_peremption ON preparations_batch(localisation, date_peremption);
CREATE INDEX IF NOT EXISTS idx_prep_consomme_peremption ON preparations_batch(consomme, date_peremption);



-- Source: 05_famille.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Famille
-- ============================================================================
-- Contient : profils_enfants, activités_famille, budgets_famille, Garmin,
--            santé, jalons, contacts, documents, anniversaires
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profils_enfants (
    id SERIAL PRIMARY KEY,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    taille_vetements JSONB DEFAULT '{}'::jsonb,
    pointure VARCHAR(50),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS routines_sante (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    jours JSONB DEFAULT '[]'::jsonb,
    heure_preferee VARCHAR(10),
    duree_minutes INTEGER NOT NULL DEFAULT 30,
    rappel BOOLEAN NOT NULL DEFAULT TRUE,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_health_routines_type ON routines_sante(type_routine);
CREATE INDEX IF NOT EXISTS ix_health_routines_actif ON routines_sante(actif);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS objectifs_sante (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    valeur_cible FLOAT NOT NULL,
    unite VARCHAR(50) NOT NULL,
    valeur_actuelle FLOAT,
    date_debut DATE NOT NULL DEFAULT CURRENT_DATE,
    date_cible DATE NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_objective_valeur_positive CHECK (valeur_cible > 0),
    CONSTRAINT ck_objective_dates CHECK (date_debut <= date_cible)
);
CREATE INDEX IF NOT EXISTS ix_health_objectives_categorie ON objectifs_sante(categorie);
CREATE INDEX IF NOT EXISTS ix_health_objectives_statut ON objectifs_sante(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activites_weekend (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_activite VARCHAR(100) NOT NULL,
    date_prevue DATE NOT NULL,
    heure_debut VARCHAR(10),
    duree_estimee_h FLOAT,
    lieu VARCHAR(200),
    adresse TEXT,
    latitude FLOAT,
    longitude FLOAT,
    adapte_jules BOOLEAN NOT NULL DEFAULT TRUE,
    age_min_mois INTEGER,
    cout_estime FLOAT,
    cout_reel FLOAT,
    meteo_requise VARCHAR(50),
    statut VARCHAR(50) NOT NULL DEFAULT 'planifié',
    note_lieu INTEGER,
    commentaire TEXT,
    a_refaire BOOLEAN,
    participants JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_weekend_note_range CHECK (
        note_lieu IS NULL
        OR (
            note_lieu >= 1
            AND note_lieu <= 5
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_weekend_activities_type ON activites_weekend(type_activite);
CREATE INDEX IF NOT EXISTS ix_weekend_activities_date ON activites_weekend(date_prevue);
CREATE INDEX IF NOT EXISTS ix_weekend_activities_statut ON activites_weekend(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS achats_famille (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(50) NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    prix_estime FLOAT,
    prix_reel FLOAT,
    url VARCHAR(500),
    image_url VARCHAR(500),
    magasin VARCHAR(200),
    taille VARCHAR(50),
    age_recommande_mois INTEGER,
    achete BOOLEAN NOT NULL DEFAULT FALSE,
    date_achat DATE,
    suggere_par VARCHAR(50),
    pour_qui VARCHAR(50) NOT NULL DEFAULT 'famille',
    a_revendre BOOLEAN NOT NULL DEFAULT FALSE,
    prix_revente_estime FLOAT,
    vendu_le DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- Compatibilité rerun / bases legacy : garantir les colonnes indexées et les
-- champs ajoutés tardivement avant la création des index.
ALTER TABLE IF EXISTS achats_famille
    ADD COLUMN IF NOT EXISTS categorie VARCHAR(50),
    ADD COLUMN IF NOT EXISTS priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    ADD COLUMN IF NOT EXISTS achete BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS pour_qui VARCHAR(50) NOT NULL DEFAULT 'famille',
    ADD COLUMN IF NOT EXISTS a_revendre BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS prix_revente_estime FLOAT,
    ADD COLUMN IF NOT EXISTS vendu_le DATE;
CREATE INDEX IF NOT EXISTS ix_family_purchases_categorie ON achats_famille(categorie);
CREATE INDEX IF NOT EXISTS ix_family_purchases_priorite ON achats_famille(priorite);
CREATE INDEX IF NOT EXISTS ix_family_purchases_achete ON achats_famille(achete);
CREATE INDEX IF NOT EXISTS ix_achats_famille_pour_qui ON achats_famille(pour_qui);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activites_famille (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_activite VARCHAR(100) NOT NULL,
    date_prevue DATE NOT NULL,
    heure_debut TIME,
    duree_heures FLOAT,
    lieu VARCHAR(200),
    qui_participe JSONB,
    age_minimal_recommande INTEGER,
    cout_estime FLOAT,
    cout_reel FLOAT,
    statut VARCHAR(50) NOT NULL DEFAULT 'planifié',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_activite_duree_positive CHECK (
        duree_heures IS NULL
        OR duree_heures > 0
    ),
    CONSTRAINT ck_activite_age_positif CHECK (
        age_minimal_recommande IS NULL
        OR age_minimal_recommande >= 0
    )
);
CREATE INDEX IF NOT EXISTS ix_family_activities_type ON activites_famille(type_activite);
CREATE INDEX IF NOT EXISTS ix_family_activities_date ON activites_famille(date_prevue);
CREATE INDEX IF NOT EXISTS ix_family_activities_statut ON activites_famille(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS budgets_famille (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    categorie VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    montant FLOAT NOT NULL,
    magasin VARCHAR(200),
    est_recurrent BOOLEAN NOT NULL DEFAULT FALSE,
    frequence_recurrence VARCHAR(50),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_budget_montant_positive CHECK (montant > 0)
);
CREATE INDEX IF NOT EXISTS ix_family_budgets_date ON budgets_famille(date);
CREATE INDEX IF NOT EXISTS ix_family_budgets_categorie ON budgets_famille(categorie);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles_achats_famille (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1.0,
    prix_estime FLOAT NOT NULL DEFAULT 0.0,
    liste VARCHAR(50) NOT NULL DEFAULT 'Nous',
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    date_ajout TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    date_achat TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_shopping_items_titre ON articles_achats_famille(titre);
CREATE INDEX IF NOT EXISTS ix_shopping_items_categorie ON articles_achats_famille(categorie);
CREATE INDEX IF NOT EXISTS ix_shopping_items_liste ON articles_achats_famille(liste);
CREATE INDEX IF NOT EXISTS ix_shopping_items_actif ON articles_achats_famille(actif);
CREATE INDEX IF NOT EXISTS ix_shopping_items_date ON articles_achats_famille(date_ajout);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historique_achats (
    id SERIAL PRIMARY KEY,
    article_nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100),
    rayon_magasin VARCHAR(100),
    derniere_achat TIMESTAMP WITH TIME ZONE NOT NULL,
    frequence_jours INTEGER,
    nb_achats INTEGER NOT NULL DEFAULT 1,
    prix_dernier FLOAT,
    prix_moyen FLOAT
);
CREATE INDEX IF NOT EXISTS ix_historique_achats_nom ON historique_achats(article_nom);
CREATE INDEX IF NOT EXISTS ix_historique_achats_date ON historique_achats(derniere_achat);
CREATE INDEX IF NOT EXISTS ix_historique_achats_nom_date ON historique_achats(article_nom, derniere_achat);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS garmin_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    oauth_token VARCHAR(500) NOT NULL,
    oauth_token_secret VARCHAR(500) NOT NULL,
    garmin_user_id VARCHAR(100),
    derniere_sync TIMESTAMP WITH TIME ZONE,
    sync_active BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_tokens_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_garmin_tokens_user_id ON garmin_tokens(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activites_garmin (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    garmin_activity_id VARCHAR(100) NOT NULL,
    type_activite VARCHAR(50) NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    duree_secondes INTEGER NOT NULL,
    distance_metres FLOAT,
    calories INTEGER,
    fc_moyenne INTEGER,
    fc_max INTEGER,
    vitesse_moyenne FLOAT,
    allure_moyenne FLOAT,
    elevation_gain INTEGER,
    raw_data JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_activities_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE,
    CONSTRAINT ck_garmin_duree_positive CHECK (duree_secondes > 0)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_garmin_activity_id ON activites_garmin(garmin_activity_id);
CREATE INDEX IF NOT EXISTS ix_garmin_activities_user ON activites_garmin(user_id);
CREATE INDEX IF NOT EXISTS ix_garmin_activities_type ON activites_garmin(type_activite);
CREATE INDEX IF NOT EXISTS ix_garmin_activities_date ON activites_garmin(date_debut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resumes_quotidiens_garmin (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    pas INTEGER NOT NULL DEFAULT 0,
    distance_metres INTEGER NOT NULL DEFAULT 0,
    calories_totales INTEGER NOT NULL DEFAULT 0,
    calories_actives INTEGER NOT NULL DEFAULT 0,
    minutes_actives INTEGER NOT NULL DEFAULT 0,
    minutes_tres_actives INTEGER NOT NULL DEFAULT 0,
    fc_repos INTEGER,
    fc_min INTEGER,
    fc_max INTEGER,
    sommeil_total_minutes INTEGER,
    sommeil_profond_minutes INTEGER,
    sommeil_leger_minutes INTEGER,
    sommeil_rem_minutes INTEGER,
    stress_moyen INTEGER,
    body_battery_max INTEGER,
    body_battery_min INTEGER,
    raw_data JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_daily_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_garmin_daily_user ON resumes_quotidiens_garmin(user_id);
CREATE INDEX IF NOT EXISTS ix_garmin_daily_date ON resumes_quotidiens_garmin(date);
CREATE UNIQUE INDEX IF NOT EXISTS uq_garmin_daily_user_date ON resumes_quotidiens_garmin(user_id, date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS journaux_alimentaires (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    heure TIMESTAMP WITH TIME ZONE,
    repas VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    calories_estimees INTEGER,
    proteines_g FLOAT,
    glucides_g FLOAT,
    lipides_g FLOAT,
    qualite INTEGER,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_food_logs_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE,
    CONSTRAINT ck_food_qualite_range CHECK (
        qualite IS NULL
        OR (
            qualite >= 1
            AND qualite <= 5
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_food_logs_user ON journaux_alimentaires(user_id);
CREATE INDEX IF NOT EXISTS ix_food_logs_date ON journaux_alimentaires(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS entrees_bien_etre (
    id SERIAL PRIMARY KEY,
    child_id INTEGER,
    username VARCHAR(200),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    mood VARCHAR(100),
    sleep_hours FLOAT,
    activity VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_wellbeing_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_wellbeing_child ON entrees_bien_etre(child_id);
CREATE INDEX IF NOT EXISTS ix_wellbeing_username ON entrees_bien_etre(username);
CREATE INDEX IF NOT EXISTS ix_wellbeing_date ON entrees_bien_etre(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jalons (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    date_atteint DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    contexte_narratif TEXT,
    lieu VARCHAR(200),
    emotion_parents VARCHAR(50),
    age_mois_atteint INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_milestones_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_milestones_child ON jalons(child_id);
CREATE INDEX IF NOT EXISTS idx_jalons_profil_id ON jalons(child_id);
CREATE INDEX IF NOT EXISTS ix_milestones_categorie ON jalons(categorie);
CREATE INDEX IF NOT EXISTS ix_milestones_date ON jalons(date_atteint);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS entrees_sante (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    type_activite VARCHAR(100) NOT NULL,
    duree_minutes INTEGER NOT NULL,
    intensite VARCHAR(50),
    calories_brulees INTEGER,
    note_energie INTEGER,
    note_moral INTEGER,
    ressenti TEXT,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_health_entries_routine FOREIGN KEY (routine_id) REFERENCES routines_sante(id) ON DELETE CASCADE,
    CONSTRAINT ck_entry_duree_positive CHECK (duree_minutes > 0),
    CONSTRAINT ck_entry_energie CHECK (
        note_energie IS NULL
        OR (
            note_energie >= 1
            AND note_energie <= 10
        )
    ),
    CONSTRAINT ck_entry_moral CHECK (
        note_moral IS NULL
        OR (
            note_moral >= 1
            AND note_moral <= 10
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_health_entries_routine ON entrees_sante(routine_id);
CREATE INDEX IF NOT EXISTS ix_health_entries_date ON entrees_sante(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vaccins (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    date_vaccination DATE NOT NULL,
    numero_lot VARCHAR(100),
    medecin VARCHAR(200),
    lieu VARCHAR(200),
    rappel_prevu DATE,
    dose_numero INTEGER DEFAULT 1,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_vaccins_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE CASCADE,
    CONSTRAINT ck_vaccins_dose_positive CHECK (dose_numero > 0)
);
CREATE INDEX IF NOT EXISTS ix_vaccins_child ON vaccins(child_id);
CREATE INDEX IF NOT EXISTS ix_vaccins_rappel ON vaccins(rappel_prevu);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rendez_vous_medicaux (
    id SERIAL PRIMARY KEY,
    child_id INTEGER,
    membre_famille VARCHAR(100),
    specialite VARCHAR(100) NOT NULL,
    medecin VARCHAR(200),
    date_rdv TIMESTAMP WITH TIME ZONE NOT NULL,
    lieu VARCHAR(300),
    motif TEXT,
    compte_rendu TEXT,
    ordonnance TEXT,
    prochain_rdv DATE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_rdv_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS ix_rdv_child ON rendez_vous_medicaux(child_id);
CREATE INDEX IF NOT EXISTS ix_rdv_date ON rendez_vous_medicaux(date_rdv);
CREATE INDEX IF NOT EXISTS ix_rdv_membre ON rendez_vous_medicaux(membre_famille);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mesures_croissance (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL,
    date_mesure DATE NOT NULL,
    age_mois NUMERIC(5, 1) NOT NULL,
    poids_kg NUMERIC(5, 2),
    taille_cm NUMERIC(5, 1),
    perimetre_cranien_cm NUMERIC(5, 1),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_croissance_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE CASCADE,
    CONSTRAINT ck_croissance_age_positif CHECK (age_mois >= 0),
    CONSTRAINT ck_croissance_poids_positif CHECK (
        poids_kg IS NULL
        OR poids_kg > 0
    ),
    CONSTRAINT ck_croissance_taille_positive CHECK (
        taille_cm IS NULL
        OR taille_cm > 0
    )
);
CREATE INDEX IF NOT EXISTS ix_croissance_child ON mesures_croissance(child_id);
CREATE INDEX IF NOT EXISTS ix_croissance_date ON mesures_croissance(date_mesure);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts_famille (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    prenom VARCHAR(200),
    telephone VARCHAR(30),
    email VARCHAR(300),
    adresse TEXT,
    categorie VARCHAR(50) NOT NULL DEFAULT 'famille',
    relation VARCHAR(100),
    notes TEXT,
    est_urgence BOOLEAN NOT NULL DEFAULT FALSE,
    sous_categorie VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_contacts_categorie CHECK (
        categorie IN (
            'medical',
            'garde',
            'education',
            'administration',
            'famille',
            'urgence'
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_contacts_categorie ON contacts_famille(categorie);
CREATE INDEX IF NOT EXISTS ix_contacts_urgence ON contacts_famille(est_urgence)
WHERE est_urgence = TRUE;


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS anniversaires_famille (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_naissance DATE NOT NULL,
    relation VARCHAR(100),
    notes TEXT,
    rappel_jours_avant JSONB DEFAULT '[7, 1]',
    historique_cadeaux JSONB DEFAULT '[]',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_anniversaires_date ON anniversaires_famille(date_naissance);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS evenements_familiaux (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    date_fin TIMESTAMP WITH TIME ZONE,
    lieu VARCHAR(300),
    type_evenement VARCHAR(50) NOT NULL DEFAULT 'famille',
    recurrence VARCHAR(30),
    rappel_minutes INTEGER,
    participants JSONB DEFAULT '[]',
    couleur VARCHAR(20),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_evt_type CHECK (
        type_evenement IN (
            'famille',
            'medical',
            'scolaire',
            'loisir',
            'administratif',
            'couple'
        )
    ),
    CONSTRAINT ck_evt_dates CHECK (
        date_fin IS NULL
        OR date_fin >= date_debut
    )
);
CREATE INDEX IF NOT EXISTS ix_evenements_date_debut ON evenements_familiaux(date_debut);
CREATE INDEX IF NOT EXISTS ix_evenements_type ON evenements_familiaux(type_evenement);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents_famille (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(300) NOT NULL,
    titre VARCHAR(200),
    type_document VARCHAR(50) NOT NULL,
    fichier_url VARCHAR(500),
    date_expiration DATE,
    membre_famille VARCHAR(100),
    notes TEXT,
    tags JSONB DEFAULT '[]',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_doc_type CHECK (
        type_document IN (
            'identite',
            'medical',
            'scolaire',
            'administratif',
            'assurance',
            'autre'
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_documents_type ON documents_famille(type_document);
CREATE INDEX IF NOT EXISTS ix_documents_expiration ON documents_famille(date_expiration)
WHERE date_expiration IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_documents_membre ON documents_famille(membre_famille);

-- ============================================================================
-- PARTIE 5 : TABLES MAISON (sans modèles ORM — migration 020)
-- ============================================================================


-- Source: 06_maison.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Maison
-- ============================================================================
-- Contient : projets, routines, jardin, entretien, stocks, pièces,
--            objets, artisans, énergie, maison extensions
-- ============================================================================


-- Source: 06a_projets.sql
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Projets & Routines
-- ============================================================================
-- Contient : projets, routines, tâches projet, tâches routine
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS projets (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_debut DATE,
    date_fin DATE,
    budget_estime FLOAT,
    budget_reel FLOAT,
    categorie VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_projects_statut ON projets(statut);
CREATE INDEX IF NOT EXISTS ix_projects_categorie ON projets(categorie);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    jours JSONB DEFAULT '[]',
    heure_debut VARCHAR(10),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    moment_journee VARCHAR(20) NOT NULL DEFAULT 'flexible',
    jour_semaine INTEGER,
    derniere_completion DATE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_routines_type ON routines(type_routine);
CREATE INDEX IF NOT EXISTS ix_routines_actif ON routines(actif);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS taches_projets (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'à_faire',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_echeance DATE,
    assigne_a VARCHAR(200),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_project_tasks_project FOREIGN KEY (project_id) REFERENCES projets(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_project_tasks_project ON taches_projets(project_id);
CREATE INDEX IF NOT EXISTS ix_project_tasks_statut ON taches_projets(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS taches_routines (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    ordre INTEGER NOT NULL DEFAULT 1,
    heure_prevue VARCHAR(5),
    fait_le DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_routine_tasks_routine FOREIGN KEY (routine_id) REFERENCES routines(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_routine_tasks_routine ON taches_routines(routine_id);



-- Source: 06b_entretien.sql
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Entretien & Organisation
-- ============================================================================
-- Contient : entretien, checklists vacances
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS taches_entretien (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(50) NOT NULL,
    piece VARCHAR(50),
    frequence_jours INTEGER,
    derniere_fois DATE,
    prochaine_fois DATE,
    duree_minutes INTEGER NOT NULL DEFAULT 30,
    responsable VARCHAR(50),
    priorite VARCHAR(20) NOT NULL DEFAULT 'normale',
    fait BOOLEAN NOT NULL DEFAULT FALSE,
    integrer_planning BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_categorie ON taches_entretien(categorie);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_prochaine ON taches_entretien(prochaine_fois);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_fait ON taches_entretien(fait);


-- ─────────────────────────────────────────────────────────────────────────────
-- La table legacy `preferences_home` a été retirée : les préférences passent
-- désormais par `preferences_utilisateurs` et la configuration applicative.


-- ─────────────────────────────────────────────────────────────────────────────
-- Les anciennes tables `taches_home` et `stats_home` ont été retirées du schéma
-- actif : les besoins courants passent désormais par `taches_entretien` et les
-- vues SQL de planning maison.


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checklists_vacances (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_voyage VARCHAR(50) NOT NULL,
    destination VARCHAR(200),
    duree_jours INTEGER,
    date_depart DATE,
    date_retour DATE,
    terminee BOOLEAN DEFAULT FALSE,
    archivee BOOLEAN DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_checklists_type_voyage ON checklists_vacances(type_voyage);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS items_checklist (
    id SERIAL PRIMARY KEY,
    checklist_id INTEGER NOT NULL REFERENCES checklists_vacances(id) ON DELETE CASCADE,
    libelle VARCHAR(300) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    ordre INTEGER DEFAULT 0,
    fait BOOLEAN DEFAULT FALSE,
    responsable VARCHAR(50),
    quand VARCHAR(20),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_items_checklist_checklist ON items_checklist(checklist_id);



-- Source: 06c_jardin.sql
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Jardin & Autonomie
-- ============================================================================
-- Contient : jardin, plans, zones, plantes, récoltes, autonomie alimentaire
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS elements_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_plante VARCHAR(100) NOT NULL,
    emplacement VARCHAR(200),
    date_plantation DATE,
    frequence_arrosage VARCHAR(50),
    derniere_action DATE,
    statut VARCHAR(50) NOT NULL DEFAULT 'actif',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_garden_items_type ON elements_jardin(type_plante);
CREATE INDEX IF NOT EXISTS ix_garden_items_statut ON elements_jardin(statut);
CREATE INDEX IF NOT EXISTS ix_garden_items_derniere_action ON elements_jardin(derniere_action);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plans_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    largeur NUMERIC(6, 2) NOT NULL,
    hauteur NUMERIC(6, 2) NOT NULL,
    description TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_plans_jardin_nom ON plans_jardin(nom);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS journaux_jardin (
    id SERIAL PRIMARY KEY,
    garden_item_id INTEGER,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    action VARCHAR(200) NOT NULL,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garden_logs_item FOREIGN KEY (garden_item_id) REFERENCES elements_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_garden_logs_item ON journaux_jardin(garden_item_id);
CREATE INDEX IF NOT EXISTS ix_garden_logs_date ON journaux_jardin(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS zones_jardin (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER,
    nom VARCHAR(100) NOT NULL,
    type_zone VARCHAR(50) NOT NULL,
    superficie_m2 NUMERIC(8, 2),
    exposition VARCHAR(10),
    type_sol VARCHAR(50),
    arrosage_auto BOOLEAN DEFAULT FALSE,
    description TEXT,
    -- Positions 2D (canvas)
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    largeur_px INTEGER DEFAULT 100,
    hauteur_px INTEGER DEFAULT 100,
    couleur VARCHAR(20) DEFAULT '#4CAF50',
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_zones_jardin_plan_id FOREIGN KEY (plan_id) REFERENCES plans_jardin(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS idx_zones_jardin_type ON zones_jardin(type_zone);
CREATE INDEX IF NOT EXISTS idx_zones_jardin_plan_id ON zones_jardin(plan_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plantes_jardin (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL,
    nom VARCHAR(100) NOT NULL,
    variete VARCHAR(100),
    etat VARCHAR(20) DEFAULT 'bon',
    date_plantation DATE,
    mois_semis VARCHAR(100),
    mois_recolte VARCHAR(100),
    arrosage VARCHAR(50),
    notes TEXT,
    position_x NUMERIC(8, 2),
    position_y NUMERIC(8, 2),
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_plantes_jardin_zone FOREIGN KEY (zone_id) REFERENCES zones_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_plantes_jardin_zone ON plantes_jardin(zone_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS actions_plantes (
    id SERIAL PRIMARY KEY,
    plante_id INTEGER NOT NULL,
    type_action VARCHAR(50) NOT NULL,
    date_action DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite NUMERIC(8, 2),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_actions_plantes_plante_id FOREIGN KEY (plante_id) REFERENCES plantes_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_plante_id ON actions_plantes(plante_id);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_type_action ON actions_plantes(type_action);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_date_action ON actions_plantes(date_action);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plantes_catalogue (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    nom_latin VARCHAR(150),
    famille VARCHAR(50),
    varietes JSONB DEFAULT '[]',
    mois_semis_interieur JSONB DEFAULT '[]',
    mois_semis_exterieur JSONB DEFAULT '[]',
    mois_plantation JSONB DEFAULT '[]',
    mois_recolte JSONB DEFAULT '[]',
    compagnons_positifs JSONB DEFAULT '[]',
    compagnons_negatifs JSONB DEFAULT '[]',
    espacement_cm INTEGER DEFAULT 30,
    profondeur_semis_cm INTEGER DEFAULT 2,
    jours_germination INTEGER DEFAULT 10,
    jours_jusqu_recolte INTEGER DEFAULT 60,
    arrosage VARCHAR(20) DEFAULT 'regulier' CHECK (
        arrosage IN ('quotidien', 'regulier', 'modere', 'faible')
    ),
    exposition VARCHAR(20) DEFAULT 'soleil' CHECK (
        exposition IN ('soleil', 'mi_ombre', 'ombre')
    ),
    rendement_kg_m2 DECIMAL(4, 2) DEFAULT 2.0,
    besoin_famille_4_kg_an DECIMAL(6, 2),
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_plantes_catalogue_famille ON plantes_catalogue(famille);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recoltes (
    id SERIAL PRIMARY KEY,
    plante_jardin_id INTEGER REFERENCES plantes_jardin(id) ON DELETE CASCADE,
    zone_jardin_id INTEGER REFERENCES zones_jardin(id) ON DELETE CASCADE,
    legume VARCHAR(100) NOT NULL,
    date_recolte DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite_kg DECIMAL(6, 2) NOT NULL,
    qualite VARCHAR(20) DEFAULT 'bonne' CHECK (
        qualite IN ('excellente', 'bonne', 'moyenne', 'passable')
    ),
    destination VARCHAR(20) DEFAULT 'frais' CHECK (
        destination IN ('frais', 'conserve', 'congele', 'donne', 'perdu')
    ),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_recoltes_date ON recoltes(date_recolte);
CREATE INDEX IF NOT EXISTS idx_recoltes_legume ON recoltes(legume);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS objectifs_autonomie (
    id SERIAL PRIMARY KEY,
    legume VARCHAR(100) NOT NULL UNIQUE,
    besoin_kg_an DECIMAL(6, 2) NOT NULL,
    surface_ideale_m2 DECIMAL(6, 2),
    production_kg_an DECIMAL(6, 2) DEFAULT 0,
    surface_actuelle_m2 DECIMAL(6, 2) DEFAULT 0,
    pourcentage_atteint INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN besoin_kg_an > 0 THEN LEAST(
                100,
                ROUND((production_kg_an / besoin_kg_an) * 100)
            )
            ELSE 0
        END
    ) STORED,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);



-- Source: 06d_equipements.sql
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Equipements & Travaux
-- ============================================================================
-- Contient : meubles, stocks, pièces, objets, artisans, devis, diagnostics
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meubles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    piece VARCHAR(50) NOT NULL,
    categorie VARCHAR(100),
    prix_estime NUMERIC(10, 2),
    prix_max NUMERIC(10, 2),
    prix_reel NUMERIC(10, 2),
    statut VARCHAR(20) NOT NULL DEFAULT 'souhaite',
    priorite VARCHAR(20) NOT NULL DEFAULT 'normale',
    magasin VARCHAR(200),
    url VARCHAR(500),
    reference VARCHAR(100),
    largeur_cm INTEGER,
    hauteur_cm INTEGER,
    profondeur_cm INTEGER,
    date_souhait DATE NOT NULL DEFAULT CURRENT_DATE,
    date_achat DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_furniture_piece ON meubles(piece);
CREATE INDEX IF NOT EXISTS ix_furniture_statut ON meubles(statut);
CREATE INDEX IF NOT EXISTS ix_furniture_priorite ON meubles(priorite);
CREATE INDEX IF NOT EXISTS ix_furniture_date_achat ON meubles(date_achat);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stocks_maison (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100) NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 0,
    unite VARCHAR(20) NOT NULL DEFAULT 'unité',
    seuil_alerte INTEGER NOT NULL DEFAULT 1,
    emplacement VARCHAR(200),
    prix_unitaire NUMERIC(10, 2),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_house_stocks_categorie ON stocks_maison(categorie);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pieces_maison (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    etage INTEGER DEFAULT 0,
    superficie_m2 NUMERIC(6, 2),
    type_piece VARCHAR(50),
    description TEXT,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    largeur_px INTEGER DEFAULT 100,
    hauteur_px INTEGER DEFAULT 100,
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pieces_maison_type ON pieces_maison(type_piece);
-- ============================================================================
-- PARTIE 4 : TABLES AVEC DÉPENDANCES FK
-- ============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS objets_maison (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50),
    statut VARCHAR(50) DEFAULT 'fonctionne',
    priorite_remplacement VARCHAR(20),
    date_achat DATE,
    duree_garantie_mois INTEGER,
    prix_achat NUMERIC(10, 2),
    prix_remplacement_estime NUMERIC(10, 2),
    marque VARCHAR(100),
    modele VARCHAR(100),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_objets_maison_piece FOREIGN KEY (piece_id) REFERENCES pieces_maison(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_objets_maison_piece ON objets_maison(piece_id);
CREATE INDEX IF NOT EXISTS idx_objets_maison_categorie ON objets_maison(categorie);
CREATE INDEX IF NOT EXISTS idx_objets_maison_statut ON objets_maison(statut);
CREATE INDEX IF NOT EXISTS idx_objets_maison_date_achat ON objets_maison(date_achat);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions_travail (
    id SERIAL PRIMARY KEY,
    type_activite VARCHAR(50) NOT NULL,
    zone_jardin_id INTEGER,
    piece_id INTEGER,
    description TEXT,
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP,
    duree_minutes INTEGER,
    notes TEXT,
    difficulte INTEGER,
    satisfaction INTEGER,
    cree_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT ck_sessions_duree_positive CHECK (
        duree_minutes IS NULL
        OR duree_minutes >= 0
    ),
    CONSTRAINT ck_difficulte_range CHECK (
        difficulte IS NULL
        OR (
            difficulte >= 1
            AND difficulte <= 5
        )
    ),
    CONSTRAINT ck_satisfaction_range CHECK (
        satisfaction IS NULL
        OR (
            satisfaction >= 1
            AND satisfaction <= 5
        )
    )
);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_type ON sessions_travail(type_activite);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_zone ON sessions_travail(zone_jardin_id);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_piece ON sessions_travail(piece_id);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_type_debut ON sessions_travail(type_activite, debut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS versions_pieces (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER NOT NULL REFERENCES pieces_maison(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    type_modification VARCHAR(50) NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_modification DATE NOT NULL,
    cout_total NUMERIC(10, 2),
    photo_avant_url VARCHAR(500),
    photo_apres_url VARCHAR(500),
    cree_le TIMESTAMP DEFAULT NOW(),
    cree_par VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS idx_versions_pieces_piece ON versions_pieces(piece_id);
CREATE INDEX IF NOT EXISTS idx_versions_pieces_piece_version ON versions_pieces(piece_id, version);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS couts_travaux (
    id SERIAL PRIMARY KEY,
    version_id INTEGER NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    libelle VARCHAR(200) NOT NULL,
    montant NUMERIC(10, 2) NOT NULL,
    fournisseur VARCHAR(200),
    facture_ref VARCHAR(100),
    date_paiement DATE,
    cree_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_couts_travaux_version FOREIGN KEY (version_id) REFERENCES versions_pieces(id) ON DELETE CASCADE,
    CONSTRAINT ck_cout_montant_positif CHECK (montant >= 0)
);
CREATE INDEX IF NOT EXISTS idx_couts_travaux_version ON couts_travaux(version_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS logs_statut_objets (
    id SERIAL PRIMARY KEY,
    objet_id INTEGER NOT NULL,
    ancien_statut VARCHAR(50),
    nouveau_statut VARCHAR(50) NOT NULL,
    raison TEXT,
    prix_estime NUMERIC(10, 2),
    priorite VARCHAR(20),
    ajoute_courses BOOLEAN DEFAULT FALSE,
    ajoute_budget BOOLEAN DEFAULT FALSE,
    date_changement TIMESTAMP DEFAULT NOW(),
    change_par VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS idx_logs_statut_objet ON logs_statut_objets(objet_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS artisans (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    entreprise VARCHAR(200),
    metier VARCHAR(50) NOT NULL,
    specialite VARCHAR(200),
    telephone VARCHAR(20),
    telephone2 VARCHAR(20),
    email VARCHAR(200),
    adresse TEXT,
    zone_intervention VARCHAR(200),
    note INTEGER,
    recommande BOOLEAN DEFAULT TRUE,
    site_web VARCHAR(500),
    siret VARCHAR(20),
    assurance_decennale BOOLEAN DEFAULT FALSE,
    qualifications TEXT,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_artisans_metier ON artisans(metier);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS interventions_artisans (
    id SERIAL PRIMARY KEY,
    artisan_id INTEGER NOT NULL REFERENCES artisans(id) ON DELETE CASCADE,
    date_intervention DATE NOT NULL,
    description TEXT NOT NULL,
    piece VARCHAR(50),
    montant_devis NUMERIC(10, 2),
    montant_facture NUMERIC(10, 2),
    paye BOOLEAN DEFAULT FALSE,
    satisfaction INTEGER,
    commentaire TEXT,
    facture_path VARCHAR(500),
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_interventions_artisans_artisan ON interventions_artisans(artisan_id);
CREATE INDEX IF NOT EXISTS ix_interventions_artisans_date ON interventions_artisans(date_intervention);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles_cellier (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    sous_categorie VARCHAR(100),
    marque VARCHAR(100),
    code_barres VARCHAR(50),
    quantite INTEGER DEFAULT 1,
    unite VARCHAR(20) DEFAULT 'unité',
    seuil_alerte INTEGER DEFAULT 1,
    date_achat DATE,
    dlc DATE,
    dluo DATE,
    emplacement VARCHAR(100),
    prix_unitaire NUMERIC(10, 2),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_articles_cellier_categorie ON articles_cellier(categorie);
CREATE INDEX IF NOT EXISTS ix_articles_cellier_code_barres ON articles_cellier(code_barres);
CREATE INDEX IF NOT EXISTS ix_articles_cellier_dlc ON articles_cellier(dlc);
CREATE INDEX IF NOT EXISTS ix_articles_cellier_date_achat ON articles_cellier(date_achat);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS diagnostics_maison (
    id SERIAL PRIMARY KEY,
    type_diagnostic VARCHAR(50) NOT NULL,
    resultat VARCHAR(100),
    resultat_detail TEXT,
    diagnostiqueur VARCHAR(200),
    numero_certification VARCHAR(100),
    date_realisation DATE NOT NULL,
    date_validite DATE,
    duree_validite_ans INTEGER,
    score_energie VARCHAR(5),
    score_ges VARCHAR(5),
    consommation_kwh_m2 FLOAT,
    emission_co2_m2 FLOAT,
    surface_m2 FLOAT,
    document_path VARCHAR(500),
    alerte_active BOOLEAN DEFAULT TRUE,
    alerte_jours_avant INTEGER DEFAULT 60,
    recommandations TEXT,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_diagnostics_type ON diagnostics_maison(type_diagnostic);
CREATE INDEX IF NOT EXISTS ix_diagnostics_validite ON diagnostics_maison(date_validite);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS estimations_immobilieres (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    date_estimation DATE NOT NULL,
    valeur_basse NUMERIC(12, 2),
    valeur_moyenne NUMERIC(12, 2) NOT NULL,
    valeur_haute NUMERIC(12, 2),
    prix_m2 NUMERIC(10, 2),
    surface_m2 FLOAT,
    nb_pieces INTEGER,
    code_postal VARCHAR(10),
    commune VARCHAR(100),
    nb_transactions_comparees INTEGER,
    prix_m2_quartier NUMERIC(10, 2),
    evolution_annuelle_pct FLOAT,
    investissement_travaux NUMERIC(12, 2),
    plus_value_estimee NUMERIC(12, 2),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS traitements_nuisibles (
    id SERIAL PRIMARY KEY,
    type_nuisible VARCHAR(50) NOT NULL,
    zone VARCHAR(100),
    est_preventif BOOLEAN DEFAULT FALSE,
    produit VARCHAR(200),
    methode VARCHAR(200),
    est_bio BOOLEAN DEFAULT FALSE,
    date_traitement DATE NOT NULL,
    date_prochain_traitement DATE,
    frequence_jours INTEGER,
    efficacite INTEGER,
    probleme_resolu BOOLEAN DEFAULT FALSE,
    fait_par VARCHAR(100),
    artisan_id INTEGER REFERENCES artisans(id),
    cout NUMERIC(10, 2),
    fiche_securite TEXT,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_traitements_type ON traitements_nuisibles(type_nuisible);
CREATE INDEX IF NOT EXISTS ix_traitements_prochain ON traitements_nuisibles(date_prochain_traitement);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS devis_comparatifs (
    id SERIAL PRIMARY KEY,
    projet_id INTEGER REFERENCES projets(id),
    artisan_id INTEGER REFERENCES artisans(id),
    reference VARCHAR(100),
    description TEXT NOT NULL,
    date_demande DATE,
    date_reception DATE,
    date_validite DATE,
    montant_ht NUMERIC(12, 2),
    montant_ttc NUMERIC(12, 2) NOT NULL,
    tva_pct FLOAT,
    delai_travaux_jours INTEGER,
    date_debut_prevue DATE,
    statut VARCHAR(20) DEFAULT 'demande',
    choisi BOOLEAN DEFAULT FALSE,
    note_globale INTEGER,
    commentaire TEXT,
    document_path VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_devis_projet ON devis_comparatifs(projet_id);
CREATE INDEX IF NOT EXISTS ix_devis_artisan ON devis_comparatifs(artisan_id);
CREATE INDEX IF NOT EXISTS ix_devis_statut ON devis_comparatifs(statut);
CREATE INDEX IF NOT EXISTS ix_devis_date_validite ON devis_comparatifs(date_validite)
    WHERE date_validite IS NOT NULL;


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lignes_devis (
    id SERIAL PRIMARY KEY,
    devis_id INTEGER NOT NULL REFERENCES devis_comparatifs(id) ON DELETE CASCADE,
    description VARCHAR(500) NOT NULL,
    quantite FLOAT DEFAULT 1.0,
    unite VARCHAR(20),
    prix_unitaire_ht NUMERIC(10, 2) NOT NULL,
    montant_ht NUMERIC(10, 2) NOT NULL,
    type_ligne VARCHAR(30) DEFAULT 'fourniture',
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_lignes_devis_devis ON lignes_devis(devis_id);



-- Source: 06e_energie.sql
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Energie & Charges
-- ============================================================================
-- Contient : dépenses, abonnements, écologie, entretiens saisonniers, compteurs
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS depenses_maison (
    id SERIAL PRIMARY KEY,
    categorie VARCHAR(50) NOT NULL,
    mois INTEGER NOT NULL,
    annee INTEGER NOT NULL,
    montant NUMERIC(10, 2) NOT NULL,
    consommation FLOAT,
    unite_consommation VARCHAR(20),
    fournisseur VARCHAR(200),
    numero_contrat VARCHAR(100),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_house_mois_valide CHECK (
        mois >= 1
        AND mois <= 12
    ),
    CONSTRAINT ck_house_montant_positif CHECK (montant >= 0),
    CONSTRAINT ck_house_consommation_positive CHECK (
        consommation IS NULL
        OR consommation >= 0
    )
);
CREATE INDEX IF NOT EXISTS ix_house_expenses_categorie ON depenses_maison(categorie);
CREATE INDEX IF NOT EXISTS ix_house_expenses_annee ON depenses_maison(annee);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS actions_ecologiques (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_action VARCHAR(50) NOT NULL,
    ancien_produit VARCHAR(200),
    nouveau_produit VARCHAR(200),
    cout_ancien_mensuel NUMERIC(10, 2),
    cout_nouveau_initial NUMERIC(10, 2),
    economie_mensuelle NUMERIC(10, 2),
    date_debut DATE NOT NULL DEFAULT CURRENT_DATE,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_eco_actions_type ON actions_ecologiques(type_action);


-- ─────────────────────────────────────────────────────────────────────────────
-- Les anciennes tables `depenses_home` et `budgets_home` ont été retirées.
-- Les usages actifs passent par `depenses_maison`, les abonnements et les
-- agrégations budgétaires exposées côté API.
-- ============================================================================
-- PARTIE 5B : TABLES JEUX EXTENSIONS (Euromillions, Cotes, Mise Responsable)
-- ============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS abonnements (
    id SERIAL PRIMARY KEY,
    type_abonnement VARCHAR(50) NOT NULL,
    fournisseur VARCHAR(200) NOT NULL,
    numero_contrat VARCHAR(100),
    prix_mensuel NUMERIC(10, 2),
    date_debut DATE,
    date_fin_engagement DATE,
    meilleur_prix_trouve NUMERIC(10, 2),
    fournisseur_alternatif VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_abonnements_type ON abonnements(type_abonnement);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS entretiens_saisonniers (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(50) NOT NULL,
    saison VARCHAR(20) NOT NULL,
    mois_recommande INTEGER,
    mois_rappel INTEGER,
    frequence VARCHAR(30) DEFAULT 'annuel',
    fait_cette_annee BOOLEAN DEFAULT FALSE,
    date_derniere_realisation DATE,
    date_prochaine DATE,
    professionnel_requis BOOLEAN DEFAULT FALSE,
    artisan_id INTEGER REFERENCES artisans(id),
    cout_estime NUMERIC(10, 2),
    duree_minutes INTEGER,
    obligatoire BOOLEAN DEFAULT FALSE,
    reglementation TEXT,
    alerte_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_entretiens_saisonniers_categorie ON entretiens_saisonniers(categorie);
CREATE INDEX IF NOT EXISTS ix_entretiens_saisonniers_saison ON entretiens_saisonniers(saison);
CREATE INDEX IF NOT EXISTS ix_entretiens_saisonniers_prochaine ON entretiens_saisonniers(date_prochaine);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS releves_compteurs (
    id SERIAL PRIMARY KEY,
    type_compteur VARCHAR(30) NOT NULL,
    numero_compteur VARCHAR(50),
    date_releve DATE NOT NULL,
    valeur FLOAT NOT NULL,
    unite VARCHAR(10) DEFAULT 'm³',
    consommation_periode FLOAT,
    nb_jours_periode INTEGER,
    consommation_jour FLOAT,
    objectif_jour FLOAT,
    anomalie_detectee BOOLEAN DEFAULT FALSE,
    commentaire_anomalie TEXT,
    photo_path VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_releves_type ON releves_compteurs(type_compteur);
CREATE INDEX IF NOT EXISTS ix_releves_date ON releves_compteurs(date_releve);




-- Source: 07_habitat.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Habitat
-- ============================================================================
-- Contient : habitat_scenarios, habitat_plans, habitat_pieces,
--            habitat_criteres_immo, habitat_annonces, habitat_projets_deco
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS idx_habitat_scenarios_statut ON habitat_scenarios(statut);
CREATE INDEX IF NOT EXISTS idx_habitat_scenarios_score ON habitat_scenarios(score_global);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_criteres (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER NOT NULL REFERENCES habitat_scenarios(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    poids DECIMAL(4,2) DEFAULT 1.00,
    note DECIMAL(3,1),
    commentaire TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_habitat_criteres_scenario ON habitat_criteres(scenario_id);


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_statut ON habitat_annonces(statut);
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_source ON habitat_annonces(source);
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_ville ON habitat_annonces(ville);


-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS idx_habitat_plans_type ON habitat_plans(type_plan);


-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS idx_habitat_pieces_plan ON habitat_pieces(plan_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_modifications_plan (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES habitat_plans(id) ON DELETE CASCADE,
    prompt_utilisateur TEXT NOT NULL,
    analyse_ia JSONB NOT NULL DEFAULT '{}'::jsonb,
    image_generee_url VARCHAR(500),
    acceptee BOOLEAN,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS idx_habitat_zones_jardin_plan ON habitat_zones_jardin(plan_id);


-- Source: 08_jeux.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Jeux
-- ============================================================================
-- Contient : jeux_equipes, jeux_matchs, paris_sportifs, loto, euromillions,
--            séries, alertes, cotes_historique
-- ============================================================================


-- Source: 08_jeux.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Jeux
-- ============================================================================
-- Contient : jeux_equipes, jeux_matchs, paris_sportifs, loto, euromillions,
--            séries, alertes, cotes_historique
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_equipes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    nom_court VARCHAR(50),
    championnat VARCHAR(50) NOT NULL,
    pays VARCHAR(50),
    logo_url VARCHAR(255),
    matchs_joues INTEGER NOT NULL DEFAULT 0,
    victoires INTEGER NOT NULL DEFAULT 0,
    nuls INTEGER NOT NULL DEFAULT 0,
    defaites INTEGER NOT NULL DEFAULT 0,
    buts_marques INTEGER NOT NULL DEFAULT 0,
    buts_encaisses INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_tirages_loto (
    id SERIAL PRIMARY KEY,
    date_tirage DATE NOT NULL,
    numero_1 INTEGER NOT NULL,
    numero_2 INTEGER NOT NULL,
    numero_3 INTEGER NOT NULL,
    numero_4 INTEGER NOT NULL,
    numero_5 INTEGER NOT NULL,
    numero_chance INTEGER NOT NULL,
    jackpot_euros INTEGER,
    gagnants_rang1 INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_tirages_loto_date ON jeux_tirages_loto(date_tirage);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_stats_loto (
    id SERIAL PRIMARY KEY,
    date_calcul TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    frequences_numeros JSONB,
    frequences_chance JSONB,
    numeros_chauds JSONB,
    numeros_froids JSONB,
    numeros_retard JSONB,
    somme_moyenne FLOAT,
    paires_frequentes JSONB,
    nb_tirages_analyses INTEGER NOT NULL DEFAULT 0
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_historique (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    type_jeu VARCHAR(20) NOT NULL,
    nb_paris INTEGER NOT NULL DEFAULT 0,
    mises_totales NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    gains_totaux NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    paris_gagnes INTEGER NOT NULL DEFAULT 0,
    paris_perdus INTEGER NOT NULL DEFAULT 0,
    predictions_correctes INTEGER NOT NULL DEFAULT 0,
    predictions_totales INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_series (
    id SERIAL PRIMARY KEY,
    type_jeu VARCHAR(20) NOT NULL,
    championnat VARCHAR(50),
    marche VARCHAR(50) NOT NULL,
    serie_actuelle INTEGER NOT NULL DEFAULT 0,
    frequence FLOAT NOT NULL DEFAULT 0.0,
    nb_occurrences INTEGER NOT NULL DEFAULT 0,
    nb_total INTEGER NOT NULL DEFAULT 0,
    derniere_occurrence DATE,
    derniere_mise_a_jour TIMESTAMP,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_jeux_series_type_jeu_championnat ON jeux_series(type_jeu, championnat);
CREATE INDEX IF NOT EXISTS ix_jeux_series_type_jeu_marche ON jeux_series(type_jeu, marche);
CREATE INDEX IF NOT EXISTS ix_jeux_series_value ON jeux_series((frequence * serie_actuelle) DESC);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_configuration (
    id SERIAL PRIMARY KEY,
    cle VARCHAR(50) NOT NULL UNIQUE,
    valeur TEXT NOT NULL,
    description TEXT,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_matchs (
    id SERIAL PRIMARY KEY,
    equipe_domicile_id INTEGER NOT NULL,
    equipe_exterieur_id INTEGER NOT NULL,
    championnat VARCHAR(50) NOT NULL,
    journee INTEGER,
    date_match DATE NOT NULL,
    heure VARCHAR(5),
    score_domicile INTEGER,
    score_exterieur INTEGER,
    resultat VARCHAR(10),
    joue BOOLEAN NOT NULL DEFAULT FALSE,
    cote_domicile FLOAT,
    cote_nul FLOAT,
    cote_exterieur FLOAT,
    prediction_resultat VARCHAR(10),
    prediction_proba_dom FLOAT,
    prediction_proba_nul FLOAT,
    prediction_proba_ext FLOAT,
    prediction_confiance FLOAT,
    prediction_raison TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_jeux_matchs_dom FOREIGN KEY (equipe_domicile_id) REFERENCES jeux_equipes(id),
    CONSTRAINT fk_jeux_matchs_ext FOREIGN KEY (equipe_exterieur_id) REFERENCES jeux_equipes(id)
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_paris_sportifs (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL,
    type_pari VARCHAR(30) NOT NULL DEFAULT '1N2',
    prediction VARCHAR(20) NOT NULL,
    cote FLOAT NOT NULL,
    mise NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    statut VARCHAR(20) NOT NULL DEFAULT 'en_attente',
    gain NUMERIC(10, 2),
    est_virtuel BOOLEAN NOT NULL DEFAULT TRUE,
    confiance_prediction FLOAT,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_jeux_paris_match FOREIGN KEY (match_id) REFERENCES jeux_matchs(id)
);
CREATE INDEX IF NOT EXISTS ix_jeux_paris_match_id ON jeux_paris_sportifs(match_id);
CREATE INDEX IF NOT EXISTS ix_jeux_paris_statut ON jeux_paris_sportifs(statut);
CREATE INDEX IF NOT EXISTS ix_jeux_paris_cree_le ON jeux_paris_sportifs(cree_le);
CREATE INDEX IF NOT EXISTS idx_paris_match_date ON jeux_paris_sportifs(match_id, cree_le);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_grilles_loto (
    id SERIAL PRIMARY KEY,
    tirage_id INTEGER,
    numero_1 INTEGER NOT NULL,
    numero_2 INTEGER NOT NULL,
    numero_3 INTEGER NOT NULL,
    numero_4 INTEGER NOT NULL,
    numero_5 INTEGER NOT NULL,
    numero_chance INTEGER NOT NULL,
    est_virtuelle BOOLEAN NOT NULL DEFAULT TRUE,
    source_prediction VARCHAR(50) NOT NULL DEFAULT 'manuel',
    mise NUMERIC(10, 2) NOT NULL DEFAULT 2.20,
    numeros_trouves INTEGER,
    chance_trouvee BOOLEAN,
    gain NUMERIC(10, 2),
    rang INTEGER,
    date_creation TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    notes TEXT,
    CONSTRAINT fk_jeux_grilles_tirage FOREIGN KEY (tirage_id) REFERENCES jeux_tirages_loto(id)
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_alertes (
    id SERIAL PRIMARY KEY,
    serie_id INTEGER NOT NULL,
    type_jeu VARCHAR(20) NOT NULL,
    championnat VARCHAR(50),
    marche VARCHAR(50) NOT NULL,
    value_alerte FLOAT NOT NULL,
    serie_alerte INTEGER NOT NULL,
    frequence_alerte FLOAT NOT NULL,
    seuil_utilise FLOAT NOT NULL DEFAULT 2.0,
    notifie BOOLEAN NOT NULL DEFAULT FALSE,
    date_notification TIMESTAMP,
    resultat_verifie BOOLEAN NOT NULL DEFAULT FALSE,
    resultat_correct BOOLEAN,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jeux_alertes_serie FOREIGN KEY (serie_id) REFERENCES jeux_series(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_jeux_alertes_notifie ON jeux_alertes(notifie)
WHERE notifie = FALSE;
CREATE INDEX IF NOT EXISTS ix_jeux_alertes_resultat ON jeux_alertes(resultat_verifie, resultat_correct);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_tirages_euromillions (
    id SERIAL PRIMARY KEY,
    date_tirage DATE NOT NULL,
    numero_1 INTEGER NOT NULL CHECK (
        numero_1 BETWEEN 1 AND 50
    ),
    numero_2 INTEGER NOT NULL CHECK (
        numero_2 BETWEEN 1 AND 50
    ),
    numero_3 INTEGER NOT NULL CHECK (
        numero_3 BETWEEN 1 AND 50
    ),
    numero_4 INTEGER NOT NULL CHECK (
        numero_4 BETWEEN 1 AND 50
    ),
    numero_5 INTEGER NOT NULL CHECK (
        numero_5 BETWEEN 1 AND 50
    ),
    etoile_1 INTEGER NOT NULL CHECK (
        etoile_1 BETWEEN 1 AND 12
    ),
    etoile_2 INTEGER NOT NULL CHECK (
        etoile_2 BETWEEN 1 AND 12
    ),
    jackpot NUMERIC(15, 2),
    nb_gagnants_rang1 INTEGER DEFAULT 0,
    rapport_rang1 NUMERIC(15, 2),
    code_my_million VARCHAR(10),
    donnees_json JSONB,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (date_tirage)
);
CREATE INDEX IF NOT EXISTS idx_tirages_euromillions_date ON jeux_tirages_euromillions(date_tirage DESC);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_grilles_euromillions (
    id SERIAL PRIMARY KEY,
    tirage_id INTEGER REFERENCES jeux_tirages_euromillions(id) ON DELETE
    SET NULL,
        numeros INTEGER [] NOT NULL,
        etoiles INTEGER [] NOT NULL,
        strategie VARCHAR(50),
        mise NUMERIC(10, 2) DEFAULT 2.50,
        gain NUMERIC(15, 2) DEFAULT 0,
        rang INTEGER,
        est_virtuelle BOOLEAN DEFAULT TRUE,
        cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_grilles_euromillions_tirage ON jeux_grilles_euromillions(tirage_id);
CREATE INDEX IF NOT EXISTS idx_grilles_euromillions_date ON jeux_grilles_euromillions(cree_le DESC);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_stats_euromillions (
    id SERIAL PRIMARY KEY,
    date_calcul DATE NOT NULL,
    frequences_numeros JSONB NOT NULL DEFAULT '{}',
    frequences_etoiles JSONB NOT NULL DEFAULT '{}',
    numeros_chauds JSONB DEFAULT '[]',
    numeros_froids JSONB DEFAULT '[]',
    etoiles_chaudes JSONB DEFAULT '[]',
    etoiles_froides JSONB DEFAULT '[]',
    patterns JSONB DEFAULT '{}',
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (date_calcul)
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_cotes_historique (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES jeux_matchs(id) ON DELETE CASCADE,
    bookmaker VARCHAR(100) NOT NULL,
    marche VARCHAR(50) NOT NULL DEFAULT '1x2',
    cote_domicile NUMERIC(8, 3),
    cote_nul NUMERIC(8, 3),
    cote_exterieur NUMERIC(8, 3),
    donnees_json JSONB,
    timestamp_cote TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cotes_hist_match ON jeux_cotes_historique(match_id);
CREATE INDEX IF NOT EXISTS idx_cotes_hist_timestamp ON jeux_cotes_historique(timestamp_cote DESC);
CREATE INDEX IF NOT EXISTS idx_cotes_hist_bookmaker ON jeux_cotes_historique(bookmaker);


-- Source: 09_notifications.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Notifications
-- ============================================================================
-- Contient : abonnements_push, preferences_notifications, webhooks_abonnements,
--            historique_notifications
-- ============================================================================


-- Source: 09_notifications.sql
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



-- Source: 10_finances.sql
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


-- Source: 11_utilitaires.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Utilitaires
-- ============================================================================
-- Contient : notes_memos, journal_bord, contacts_utiles, liens_favoris,
--            mots_de_passe_maison, presse_papier_entrees, releves_energie,
--            voyages, checklists_voyage, templates_checklist
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS voyages (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    destination VARCHAR(300) NOT NULL,
    date_depart DATE NOT NULL,
    date_retour DATE NOT NULL,
    type_voyage VARCHAR(50) DEFAULT 'vacances',
    budget_prevu NUMERIC(10, 2),
    budget_depense NUMERIC(10, 2) DEFAULT 0,
    statut VARCHAR(30) NOT NULL DEFAULT 'planifie',
    notes TEXT,
    reservations JSONB DEFAULT '[]',
    budget_reel FLOAT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_voyage_dates CHECK (date_retour >= date_depart),
    CONSTRAINT ck_voyage_statut CHECK (
        statut IN ('planifie', 'en_cours', 'termine', 'annule')
    )
);
CREATE INDEX IF NOT EXISTS ix_voyages_depart ON voyages(date_depart);
CREATE INDEX IF NOT EXISTS ix_voyages_statut ON voyages(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS templates_checklist (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_voyage VARCHAR(50),
    description TEXT,
    articles JSONB NOT NULL DEFAULT '[]',
    est_defaut BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_templates_type ON templates_checklist(type_voyage);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checklists_voyage (
    id SERIAL PRIMARY KEY,
    voyage_id INTEGER NOT NULL,
    template_id INTEGER,
    nom VARCHAR(200) NOT NULL,
    articles JSONB NOT NULL DEFAULT '[]',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_checklist_voyage FOREIGN KEY (voyage_id) REFERENCES voyages(id) ON DELETE CASCADE,
    CONSTRAINT fk_checklist_template FOREIGN KEY (template_id) REFERENCES templates_checklist(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS ix_checklists_voyage ON checklists_voyage(voyage_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notes_memos (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    contenu TEXT,
    categorie VARCHAR(50) DEFAULT 'general',
    couleur VARCHAR(20) DEFAULT '#ffffff',
    epingle BOOLEAN DEFAULT FALSE,
    archive BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notes_memos_categorie ON notes_memos(categorie);
CREATE INDEX IF NOT EXISTS idx_notes_memos_epingle ON notes_memos(epingle)
WHERE epingle = TRUE;
CREATE INDEX IF NOT EXISTS idx_notes_memos_archive ON notes_memos(archive);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS journal_bord (
    id BIGSERIAL PRIMARY KEY,
    date_entree DATE NOT NULL UNIQUE,
    contenu TEXT,
    humeur VARCHAR(20),
    energie INTEGER CHECK (
        energie BETWEEN 1 AND 10
    ),
    gratitudes JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_journal_date ON journal_bord(date_entree DESC);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts_utiles (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) DEFAULT 'autre',
    telephone VARCHAR(30),
    email VARCHAR(200),
    adresse TEXT,
    specialite VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contacts_utiles_categorie ON contacts_utiles(categorie);
CREATE INDEX IF NOT EXISTS idx_contacts_utiles_nom ON contacts_utiles(nom);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS liens_favoris (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    categorie VARCHAR(100),
    tags JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_liens_categorie ON liens_favoris(categorie);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mots_de_passe_maison (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) DEFAULT 'autre',
    identifiant VARCHAR(200),
    mot_de_passe_chiffre TEXT NOT NULL,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mdp_categorie ON mots_de_passe_maison(categorie);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS presse_papier_entrees (
    id BIGSERIAL PRIMARY KEY,
    contenu TEXT NOT NULL,
    auteur VARCHAR(100),
    cree_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pp_cree_le ON presse_papier_entrees(cree_le DESC);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS releves_energie (
    id BIGSERIAL PRIMARY KEY,
    categorie VARCHAR(30) NOT NULL CHECK (categorie IN ('electricite', 'gaz', 'eau')),
    date_releve DATE NOT NULL,
    valeur NUMERIC(12, 2) NOT NULL CHECK (valeur > 0),
    cout_reel NUMERIC(10, 2),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_energie_categorie ON releves_energie(categorie);
CREATE INDEX IF NOT EXISTS idx_energie_date ON releves_energie(date_releve DESC);



-- Source: 12_triggers.sql
-- PARTIE 6 : TRIGGERS (modifie_le)
-- ============================================================================
-- Tables avec colonne modifie_le
DO $$
DECLARE t TEXT;
tables_modifie_le TEXT [] := ARRAY [
        'profils_utilisateurs', 'garmin_tokens', 'recettes', 'activites_weekend',
        'achats_famille', 'jeux_equipes', 'jeux_matchs', 'config_batch_cooking',
        'sessions_batch_cooking', 'preparations_batch', 'batch_cooking_congelation',
        'plannings',
    'modeles_courses', 'templates_semaine', 'points_utilisateurs', 'automations',
        'contacts_famille', 'anniversaires_famille', 'evenements_familiaux',
        'voyages', 'checklists_voyage', 'documents_famille',
        -- Maison extensions
        'artisans', 'interventions_artisans',
        'articles_cellier', 'diagnostics_maison',
        'estimations_immobilieres', 'checklists_vacances', 'items_checklist',
        'traitements_nuisibles', 'devis_comparatifs', 'entretiens_saisonniers',
        -- Utilitaires
        'notes_memos', 'journal_bord', 'contacts_utiles', 'liens_favoris',
        'mots_de_passe_maison', 'releves_energie', 'minuteur_sessions',
        -- Notifications
        'historique_notifications',
        -- Tables anciennement updated_at (colonnes renommées modifie_le)
        'listes_courses', 'meubles', 'taches_entretien', 'stocks_maison',
        'preferences_utilisateurs', 'depenses', 'budgets_mensuels', 'config_meteo',
        'calendriers_externes', 'preferences_notifications',
        'configs_calendriers_externes', 'evenements_calendrier',
        'plans_jardin', 'zones_jardin', 'plantes_jardin',
        'pieces_maison', 'objets_maison',
        'objectifs_autonomie', 'abonnements'
    ];
BEGIN FOREACH t IN ARRAY tables_modifie_le LOOP EXECUTE format(
    'DROP TRIGGER IF EXISTS trigger_update_modifie_le ON %I',
    t
);
EXECUTE format(
    '
            CREATE TRIGGER trigger_update_modifie_le
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_modifie_le_column()
        ',
    t
);
END LOOP;
END $$;

-- ============================================================================
-- Trigger : mise à jour listes_courses.modifie_le via articles_courses
-- (V005 absorbé)
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
-- Trigger : invalidation cache planning via repas
-- (V005 absorbé)
-- ============================================================================
CREATE OR REPLACE FUNCTION notify_planning_changed()
RETURNS TRIGGER AS $$
BEGIN
    -- cree_par n'existe pas dans plannings, on envoie l'id du planning comme payload
    PERFORM pg_notify('planning_changed', COALESCE(CAST(COALESCE(NEW.planning_id, OLD.planning_id) AS TEXT), ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_repas_planning_notify ON repas;
CREATE TRIGGER trg_repas_planning_notify
    AFTER INSERT OR UPDATE OR DELETE ON repas
    FOR EACH ROW EXECUTE FUNCTION notify_planning_changed();
-- ============================================================================

-- Source: 13_views.sql

-- Source: 13_views.sql
-- PARTIE 7 : VUES UTILES
-- ============================================================================
-- Vue: Objets à remplacer avec priorité
DROP VIEW IF EXISTS v_objets_a_remplacer CASCADE;
CREATE VIEW v_objets_a_remplacer AS
SELECT o.id,
    o.nom,
    o.categorie,
    o.statut,
    o.priorite_remplacement,
    o.prix_remplacement_estime,
    p.nom AS piece,
    p.etage
FROM objets_maison o
    JOIN pieces_maison p ON o.piece_id = p.id
WHERE o.statut IN ('a_changer', 'a_acheter', 'a_reparer')
ORDER BY CASE
        o.priorite_remplacement
        WHEN 'urgente' THEN 1
        WHEN 'haute' THEN 2
        WHEN 'normale' THEN 3
        WHEN 'basse' THEN 4
        ELSE 5
    END,
    o.prix_remplacement_estime DESC NULLS LAST;
-- Vue: Temps par activité (30 derniers jours)
DROP VIEW IF EXISTS v_temps_par_activite_30j CASCADE;
CREATE VIEW v_temps_par_activite_30j AS
SELECT type_activite,
    COUNT(*) AS nb_sessions,
    COALESCE(SUM(duree_minutes), 0) AS duree_totale_minutes,
    ROUND(AVG(duree_minutes)::numeric, 1) AS duree_moyenne_minutes,
    ROUND(AVG(difficulte)::numeric, 1) AS difficulte_moyenne,
    ROUND(AVG(satisfaction)::numeric, 1) AS satisfaction_moyenne
FROM sessions_travail
WHERE debut >= NOW() - INTERVAL '30 days'
    AND fin IS NOT NULL
GROUP BY type_activite
ORDER BY duree_totale_minutes DESC;
-- Vue: Budget travaux par pièce
DROP VIEW IF EXISTS v_budget_travaux_par_piece CASCADE;
CREATE VIEW v_budget_travaux_par_piece AS
SELECT p.id AS piece_id,
    p.nom AS piece,
    COUNT(DISTINCT v.id) AS nb_versions,
    COALESCE(SUM(c.montant), 0) AS cout_total,
    COUNT(DISTINCT c.id) AS nb_lignes_cout,
    MAX(v.date_modification) AS derniere_modif
FROM pieces_maison p
    LEFT JOIN versions_pieces v ON v.piece_id = p.id
    LEFT JOIN couts_travaux c ON c.version_id = v.id
GROUP BY p.id,
    p.nom
ORDER BY cout_total DESC;
-- Vue: Tâches du jour
-- S'appuie désormais sur `taches_entretien` (table active) au lieu de la
-- table legacy `taches_home` retirée du schéma courant.
DROP VIEW IF EXISTS v_taches_jour CASCADE;
CREATE VIEW v_taches_jour AS
SELECT
    t.id,
    'entretien'::VARCHAR(20) AS domaine,
    'entretien_planifie'::VARCHAR(50) AS type_tache,
    t.nom AS titre,
    t.description,
    COALESCE(t.duree_minutes, 15) AS duree_min,
    t.priorite,
    t.prochaine_fois AS date_due,
    t.derniere_fois AS date_faite,
    CASE
        WHEN COALESCE(t.fait, FALSE) THEN 'fait'
        ELSE 'a_faire'
    END::VARCHAR(20) AS statut,
    FALSE AS generee_auto,
    'taches_entretien'::VARCHAR(50) AS source,
    t.id AS source_id,
    NULL::INTEGER AS zone_jardin_id,
    NULL::INTEGER AS piece_id,
    t.cree_le,
    t.modifie_le,
    NULL::VARCHAR(100) AS zone_nom,
    t.piece AS piece_nom,
    CASE
        WHEN t.priorite = 'urgente' THEN 1
        WHEN t.priorite = 'haute' THEN 2
        WHEN t.priorite = 'normale' THEN 3
        WHEN t.priorite = 'basse' THEN 4
        ELSE 5
    END AS priorite_ordre
FROM taches_entretien t
WHERE COALESCE(t.fait, FALSE) = FALSE
    AND COALESCE(t.integrer_planning, TRUE) = TRUE
    AND (
        t.prochaine_fois IS NULL
        OR t.prochaine_fois <= CURRENT_DATE + 1
    )
ORDER BY priorite_ordre,
    t.prochaine_fois NULLS LAST,
    t.nom;

-- Vue: Charge semaine
DROP VIEW IF EXISTS v_charge_semaine CASCADE;
CREATE VIEW v_charge_semaine AS
SELECT d.jour,
    COALESCE(SUM(t.duree_minutes), 0) AS temps_prevu_min,
    COUNT(t.id) AS nb_taches,
    CASE
        WHEN COALESCE(SUM(t.duree_minutes), 0) > 120 THEN 'surcharge'
        WHEN COALESCE(SUM(t.duree_minutes), 0) > 90 THEN 'charge'
        WHEN COALESCE(SUM(t.duree_minutes), 0) > 60 THEN 'normal'
        ELSE 'leger'
    END AS niveau_charge
FROM (
        SELECT generate_series(
                CURRENT_DATE,
                CURRENT_DATE + INTERVAL '6 days',
                INTERVAL '1 day'
            )::DATE AS jour
    ) d
    LEFT JOIN taches_entretien t ON t.prochaine_fois = d.jour
    AND COALESCE(t.fait, FALSE) = FALSE
    AND COALESCE(t.integrer_planning, TRUE) = TRUE
GROUP BY d.jour
ORDER BY d.jour;

-- Vue: Pourcentage autonomie alimentaire
-- SQL3: v_autonomie supprimée (vue Streamlit obsolète, non utilisée par FastAPI)

-- ============================================================================


-- Source: 14_indexes.sql
-- ============================================================================
-- ASSISTANT MATANNE — Index supplémentaires
-- ============================================================================
-- Index composites et index de performance ajoutés après V005.
-- La majorité des index sont inline avec les CREATE TABLE dans les fichiers
-- de domaine (03-11). Ce fichier contient uniquement les index additionnels.
-- ============================================================================

-- Consolidation V005 : index composites alignés sur le schéma actuel
CREATE INDEX IF NOT EXISTS ix_repas_planning_date ON repas(planning_id, date_repas);
CREATE INDEX IF NOT EXISTS ix_repas_planning_type ON repas(planning_id, type_repas);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_achete ON articles_courses(liste_id, achete);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_priorite ON articles_courses(liste_id, priorite);
CREATE INDEX IF NOT EXISTS ix_inventaire_peremption_quantite ON inventaire(date_peremption, quantite)
    WHERE date_peremption IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_ingredient_date ON historique_inventaire(ingredient_id, date_modification);
CREATE INDEX IF NOT EXISTS ix_listes_courses_statut_semaine ON listes_courses(etat, cree_le DESC);
CREATE INDEX IF NOT EXISTS ix_plannings_actif_semaine ON plannings(etat, semaine_debut)
    WHERE etat = 'valide';

-- Index migration V001-V004 (absorbés) → redirigés vers les tables/colonnes
-- actuelles pour rester compatibles lors des réexécutions de l'init.
CREATE INDEX IF NOT EXISTS idx_articles_inventaire_peremption
    ON inventaire(date_peremption);
CREATE INDEX IF NOT EXISTS idx_repas_planning_planning_date
    ON repas(planning_id, date_repas);
CREATE INDEX IF NOT EXISTS idx_historique_actions_user_date
    ON historique_actions(user_id, cree_le);
CREATE INDEX IF NOT EXISTS idx_paris_sportifs_statut_user
    ON jeux_paris_sportifs(statut, cree_le DESC);

-- Source: 15_rls_policies.sql
-- PARTIE 9 : ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Stratégie RLS :
--   service_role  : Accès complet (backend FastAPI via DATABASE_URL)
--   authenticated : Filtrage par user_id sur les tables avec user_id
--                   Accès complet sur les tables partagées (sans user_id)
--   anon          : Aucun accès (PostgREST avec clé anonyme bloqué)
--
-- IMPORTANT : Les tables avec une colonne user_id filtrent par auth.uid().
--             Les tables sans user_id sont accessibles à tous les authentifiés.
--             Les tables de configuration/référence sont en lecture seule pour authenticated.

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.1 Tables avec user_id UUID → filtrage par auth.uid()
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE t TEXT;
user_id_tables TEXT[] := ARRAY[
    'calendriers_externes', 'evenements_calendrier',
    'depenses', 'budgets_mensuels',
    'alertes_meteo', 'config_meteo',
    'sauvegardes',
    'abonnements_push', 'preferences_notifications',
    'webhooks_abonnements'
];
BEGIN FOREACH t IN ARRAY user_id_tables LOOP
    EXECUTE format('ALTER TABLE IF EXISTS public.%I ENABLE ROW LEVEL SECURITY', t);
    -- service_role : accès complet
    EXECUTE format('DROP POLICY IF EXISTS "service_role_access_%s" ON public.%I', t, t);
    EXECUTE format('CREATE POLICY "service_role_access_%s" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)', t, t);
    -- authenticated : filtrage par user_id = auth.uid()
    EXECUTE format('DROP POLICY IF EXISTS "authenticated_access_%s" ON public.%I', t, t);
    EXECUTE format('CREATE POLICY "authenticated_access_%s" ON public.%I FOR ALL TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid())', t, t);
END LOOP;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.2 Tables avec user_id VARCHAR → filtrage par auth.uid()::text
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE t TEXT;
user_id_varchar_tables TEXT[] := ARRAY[
    'preferences_utilisateurs', 'retours_recettes',
    'configs_calendriers_externes', 'etats_persistants',
    'historique_actions', 'ia_suggestions_historique',
    'historique_notifications', 'minuteur_sessions'
];
BEGIN FOREACH t IN ARRAY user_id_varchar_tables LOOP
    EXECUTE format('ALTER TABLE IF EXISTS public.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS "service_role_access_%s" ON public.%I', t, t);
    EXECUTE format('CREATE POLICY "service_role_access_%s" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)', t, t);
    EXECUTE format('DROP POLICY IF EXISTS "authenticated_access_%s" ON public.%I', t, t);
    EXECUTE format('CREATE POLICY "authenticated_access_%s" ON public.%I FOR ALL TO authenticated USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text)', t, t);
END LOOP;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.3 Tables partagées (sans user_id) → accès complet authenticated
--     Données familiales partagées entre tous les utilisateurs du foyer
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE t TEXT;
shared_tables TEXT[] := ARRAY[
    -- Cuisine
    'ingredients', 'recettes', 'recette_ingredients', 'etapes_recette',
    'versions_recette', 'historique_recettes',
    -- Batch Cooking
    'repas_batch', 'config_batch_cooking', 'sessions_batch_cooking',
    'etapes_batch_cooking', 'preparations_batch', 'batch_cooking_congelation',
    -- Inventaire & Courses
    'inventaire', 'historique_inventaire', 'listes_courses',
    'modeles_courses', 'articles_modeles', 'articles_achats_famille',
    -- Planning & Calendrier
    'plannings', 'repas', 'evenements_planning', 'templates_semaine', 'elements_templates',
    -- Famille
    'profils_enfants', 'entrees_bien_etre', 'jalons',
    'activites_famille', 'budgets_famille', 'achats_famille',
    'activites_weekend', 'anniversaires_famille', 'evenements_familiaux',
    'contacts_famille', 'documents_famille',
    -- Santé & Fitness
    'profils_utilisateurs', 'routines_sante', 'objectifs_sante', 'entrees_sante',
    'journaux_alimentaires', 'garmin_tokens', 'activites_garmin', 'resumes_quotidiens_garmin',
    'points_utilisateurs', 'badges_utilisateurs', 'automations',
    'vaccins', 'rendez_vous_medicaux', 'mesures_croissance',
    -- Finances
    'depenses_maison',
    -- Habitat
    'meubles', 'stocks_maison', 'taches_entretien', 'actions_ecologiques',
    'habitat_scenarios', 'habitat_criteres', 'habitat_criteres_immo',
    'habitat_annonces', 'habitat_plans', 'habitat_pieces',
    'habitat_modifications_plan', 'habitat_projets_deco', 'habitat_zones_jardin',
    -- Maison
    'projets', 'taches_projets', 'routines', 'taches_routines',
    'elements_jardin', 'journaux_jardin',
    -- Jeux
    'jeux_equipes', 'jeux_matchs', 'jeux_paris_sportifs',
    'jeux_tirages_loto', 'jeux_grilles_loto', 'jeux_stats_loto',
    'jeux_historique', 'jeux_series', 'jeux_alertes', 'jeux_configuration',
    'jeux_tirages_euromillions', 'jeux_grilles_euromillions', 'jeux_stats_euromillions',
    'jeux_cotes_historique', 'jeux_bankroll_historique',
    -- Temps Entretien & Jardin
    'plans_jardin', 'zones_jardin', 'plantes_jardin', 'actions_plantes',
    'pieces_maison', 'objets_maison', 'sessions_travail',
    'versions_pieces', 'couts_travaux', 'logs_statut_objets',
    'recoltes', 'objectifs_autonomie',
    -- Maison extensions
    'artisans', 'interventions_artisans', 'articles_cellier', 'diagnostics_maison',
    'estimations_immobilieres', 'checklists_vacances', 'items_checklist',
    'traitements_nuisibles', 'devis_comparatifs', 'lignes_devis',
    'entretiens_saisonniers', 'releves_compteurs',
    -- Utilitaires
    'notes_memos', 'journal_bord', 'contacts_utiles', 'liens_favoris',
    'mots_de_passe_maison', 'presse_papier_entrees', 'releves_energie',
    -- Voyages
    'voyages', 'checklists_voyage', 'templates_checklist',
    -- OpenFoodFacts cache
    'openfoodfacts_cache'
];
BEGIN FOREACH t IN ARRAY shared_tables LOOP
    EXECUTE format('ALTER TABLE IF EXISTS public.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS "service_role_access_%s" ON public.%I', t, t);
    EXECUTE format('CREATE POLICY "service_role_access_%s" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)', t, t);
    EXECUTE format('DROP POLICY IF EXISTS "authenticated_access_%s" ON public.%I', t, t);
    EXECUTE format('CREATE POLICY "authenticated_access_%s" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)', t, t);
END LOOP;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.4 Tables système/référence → lecture seule pour authenticated
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE t TEXT;
readonly_tables TEXT[] := ARRAY[
    'schema_migrations',
    'plantes_catalogue'
];
BEGIN FOREACH t IN ARRAY readonly_tables LOOP
    EXECUTE format('ALTER TABLE IF EXISTS public.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS "service_role_access_%s" ON public.%I', t, t);
    EXECUTE format('CREATE POLICY "service_role_access_%s" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)', t, t);
    EXECUTE format('DROP POLICY IF EXISTS "authenticated_read_%s" ON public.%I', t, t);
    EXECUTE format('CREATE POLICY "authenticated_read_%s" ON public.%I FOR SELECT TO authenticated USING (true)', t, t);
    -- Drop any old full-access policy
    EXECUTE format('DROP POLICY IF EXISTS "authenticated_access_%s" ON public.%I', t, t);
END LOOP;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.5 Logs sécurité admin-only
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE IF EXISTS public.logs_securite ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_access_logs_securite" ON public.logs_securite;
CREATE POLICY "service_role_access_logs_securite"
    ON public.logs_securite
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "authenticated_deny_logs_securite" ON public.logs_securite;
CREATE POLICY "authenticated_deny_logs_securite"
    ON public.logs_securite
    FOR ALL TO authenticated
    USING (false)
    WITH CHECK (false);
-- ============================================================================

-- Source: 16_seed_data.sql

-- Source: 16_seed_data.sql
-- PARTIE 10 : DONNÉES DE RÉFÉRENCE
-- ============================================================================
-- Profils utilisateurs par défaut (Anne & Mathieu)
INSERT INTO profils_utilisateurs (
        username,
        display_name,
        avatar_emoji,
        objectif_pas_quotidien,
        objectif_calories_brulees,
        objectif_minutes_actives,
        garmin_connected,
        theme_prefere,
        preferences_modules,
        cree_le,
        modifie_le
    )
VALUES (
        'anne',
        'Anne',
        '👩',
        10000,
        500,
        30,
        FALSE,
        'auto',
        '{
        "cuisine": {"nb_suggestions_ia": 5, "types_cuisine_preferes": [], "duree_max_batch_min": 120},
        "famille": {"activites_favorites_jules": [], "frequence_rappels_routines": "quotidien"},
        "maison": {"seuil_alerte_entretien_jours": 7},
        "planning": {"horizon_defaut": "semaine"},
        "budget": {"seuils_alerte_pct": 80}
    }'::jsonb,
        NOW(),
        NOW()
    ) ON CONFLICT (username) DO NOTHING;
INSERT INTO profils_utilisateurs (
        username,
        display_name,
        avatar_emoji,
        objectif_pas_quotidien,
        objectif_calories_brulees,
        objectif_minutes_actives,
        garmin_connected,
        theme_prefere,
        preferences_modules,
        cree_le,
        modifie_le
    )
VALUES (
        'mathieu',
        'Mathieu',
        '👨',
        10000,
        500,
        30,
        FALSE,
        'auto',
        '{
        "cuisine": {"nb_suggestions_ia": 5, "types_cuisine_preferes": [], "duree_max_batch_min": 120},
        "famille": {"activites_favorites_jules": [], "frequence_rappels_routines": "quotidien"},
        "maison": {"seuil_alerte_entretien_jours": 7},
        "planning": {"horizon_defaut": "semaine"},
        "budget": {"seuils_alerte_pct": 80}
    }'::jsonb,
        NOW(),
        NOW()
    ) ON CONFLICT (username) DO NOTHING;

-- Catalogue de base d'ingrédients
INSERT INTO ingredients (nom, categorie, unite, calories_pour_100g, saison, allergene)
VALUES ('Tomate', 'Légumes', 'g', 18, 'été', FALSE),
    ('Courgette', 'Légumes', 'g', 17, 'été', FALSE),
    ('Carotte', 'Légumes', 'g', 41, 'automne', FALSE),
    ('Pomme de terre', 'Féculents', 'g', 77, 'toute_année', FALSE),
    ('Poulet', 'Protéines', 'g', 165, 'toute_année', FALSE),
    ('Saumon', 'Protéines', 'g', 208, 'toute_année', FALSE),
    ('Riz complet', 'Féculents', 'g', 111, 'toute_année', FALSE),
    ('Lentilles', 'Légumineuses', 'g', 116, 'toute_année', FALSE),
    ('Yaourt nature', 'Produits laitiers', 'g', 63, 'toute_année', TRUE),
    ('Banane', 'Fruits', 'g', 89, 'toute_année', FALSE)
ON CONFLICT (nom) DO NOTHING;

-- Référentiel OMS retiré du seed de base : la courbe de croissance n'est plus
-- une fonctionnalité active dans l'application.

-- Catalogue plantes baseline
INSERT INTO plantes_catalogue (
        nom,
        nom_latin,
        famille,
        mois_semis_interieur,
        mois_semis_exterieur,
        mois_plantation,
        mois_recolte,
        espacement_cm,
        profondeur_semis_cm,
        jours_germination,
        jours_jusqu_recolte,
        arrosage,
        exposition,
        rendement_kg_m2,
        besoin_famille_4_kg_an
    )
VALUES (
        'Tomate',
        'Solanum lycopersicum',
        'Solanacées',
        '[2,3,4]'::jsonb,
        '[4,5]'::jsonb,
        '[4,5]'::jsonb,
        '[7,8,9]'::jsonb,
        50,
        1,
        8,
        85,
        'regulier',
        'soleil',
        4.00,
        40.00
    ),
    (
        'Courgette',
        'Cucurbita pepo',
        'Cucurbitacées',
        '[3,4]'::jsonb,
        '[4,5]'::jsonb,
        '[5,6]'::jsonb,
        '[7,8,9]'::jsonb,
        80,
        2,
        7,
        75,
        'regulier',
        'soleil',
        3.50,
        25.00
    ),
    (
        'Carotte',
        'Daucus carota',
        'Apiacées',
        '[2,3]'::jsonb,
        '[3,4,5,6]'::jsonb,
        '[3,4,5,6]'::jsonb,
        '[6,7,8,9,10]'::jsonb,
        8,
        1,
        12,
        95,
        'modere',
        'soleil',
        2.20,
        20.00
    ),
    (
        'Haricot vert',
        'Phaseolus vulgaris',
        'Fabacées',
        '[4,5]'::jsonb,
        '[5,6,7]'::jsonb,
        '[5,6,7]'::jsonb,
        '[7,8,9]'::jsonb,
        30,
        2,
        8,
        60,
        'regulier',
        'soleil',
        1.80,
        15.00
    )
ON CONFLICT (nom) DO NOTHING;

-- Configuration jeux par défaut
INSERT INTO jeux_configuration (cle, valeur, description)
VALUES (
        'seuil_value_alerte',
        '2.0',
        'Seuil de value minimum pour créer une alerte'
    ),
    (
        'seuil_value_haute',
        '2.5',
        'Seuil de value pour opportunité haute'
    ),
    (
        'seuil_series_minimum',
        '3',
        'Série minimum significative'
    ),
    (
        'sync_paris_interval_hours',
        '6',
        'Intervalle sync paris en heures'
    ),
    (
        'sync_loto_days',
        'mon,wed,sat',
        'Jours de sync loto'
    ),
    ('sync_loto_hour', '21:30', 'Heure de sync loto') ON CONFLICT (cle) DO NOTHING;
-- Les seeds `preferences_home` et `budgets_home` ont été retirés avec les
-- anciennes tables legacy correspondantes.
-- Objectifs autonomie alimentaire
INSERT INTO objectifs_autonomie (legume, besoin_kg_an, surface_ideale_m2)
VALUES ('Tomate', 40.00, 8.00),
    ('Courgette', 25.00, 6.00),
    ('Haricot vert', 15.00, 5.00),
    ('Pomme de terre', 80.00, 20.00),
    ('Carotte', 20.00, 4.00),
    ('Salade', 30.00, 3.00),
    ('Poireau', 15.00, 3.00),
    ('Oignon', 10.00, 2.00),
    ('Ail', 3.00, 1.00),
    ('Fraise', 10.00, 4.00) ON CONFLICT (legume) DO NOTHING;
-- Entretiens saisonniers prédéfinis
INSERT INTO entretiens_saisonniers (
        nom,
        description,
        categorie,
        saison,
        mois_recommande,
        mois_rappel,
        frequence,
        professionnel_requis,
        obligatoire,
        cout_estime,
        duree_minutes
    )
VALUES -- AUTOMNE
    (
        'Entretien chaudière',
        'Visite annuelle obligatoire de la chaudière gaz/fioul',
        'chauffage',
        'automne',
        9,
        8,
        'annuel',
        TRUE,
        TRUE,
        150.00,
        60
    ),
    (
        'Ramonage cheminée',
        'Ramonage obligatoire des conduits de fumée (1 à 2 fois/an)',
        'chauffage',
        'automne',
        10,
        9,
        'annuel',
        TRUE,
        TRUE,
        80.00,
        45
    ),
    (
        'Purge des radiateurs',
        'Purger les radiateurs avant mise en route du chauffage',
        'chauffage',
        'automne',
        10,
        9,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Nettoyage gouttières',
        'Retirer les feuilles mortes des gouttières',
        'toiture',
        'automne',
        11,
        10,
        'semestriel',
        FALSE,
        FALSE,
        0.00,
        60
    ),
    (
        'Vérification toiture',
        'Contrôle visuel tuiles/ardoises, étanchéité',
        'toiture',
        'automne',
        10,
        9,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Isolation fenêtres',
        'Vérifier joints fenêtres, calfeutrage si nécessaire',
        'isolation',
        'automne',
        10,
        9,
        'annuel',
        FALSE,
        FALSE,
        20.00,
        60
    ),
    (
        'Rentrer plantes fragiles',
        'Mettre à l''abri les plantes gélives',
        'jardin',
        'automne',
        10,
        9,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Préparer la tondeuse (hivernage)',
        'Vidanger, nettoyer, ranger la tondeuse pour l''hiver',
        'jardin',
        'automne',
        11,
        10,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        45
    ),
    -- HIVER
    (
        'Vérification détecteurs fumée',
        'Tester les détecteurs, changer les piles si besoin',
        'securite',
        'hiver',
        1,
        12,
        'semestriel',
        FALSE,
        TRUE,
        10.00,
        15
    ),
    (
        'Contrôle VMC',
        'Nettoyage bouches VMC et vérification fonctionnement',
        'ventilation',
        'hiver',
        1,
        12,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Couper eau extérieure',
        'Fermer les robinets extérieurs et purger pour éviter le gel',
        'plomberie',
        'hiver',
        12,
        11,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        15
    ),
    (
        'Vérifier isolation combles',
        'Contrôle visuel isolation toiture/combles',
        'isolation',
        'hiver',
        1,
        12,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    -- PRINTEMPS
    (
        'Entretien climatisation',
        'Nettoyage filtres et vérification avant été',
        'climatisation',
        'printemps',
        4,
        3,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Nettoyage terrasse',
        'Nettoyage haute pression terrasse, dalles, mobilier',
        'exterieur',
        'printemps',
        4,
        3,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        120
    ),
    (
        'Révision tondeuse',
        'Remise en service tondeuse, affûtage lame, huile',
        'jardin',
        'printemps',
        3,
        2,
        'annuel',
        FALSE,
        FALSE,
        15.00,
        30
    ),
    (
        'Vernissage/traitement bois extérieur',
        'Traitement mobilier jardin, clôtures, portail bois',
        'exterieur',
        'printemps',
        4,
        3,
        'annuel',
        FALSE,
        FALSE,
        50.00,
        180
    ),
    (
        'Vérification étanchéité toiture',
        'Post-hiver: contrôle fuites après gel/neige',
        'toiture',
        'printemps',
        3,
        2,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Nettoyage gouttières (printemps)',
        'Second nettoyage annuel des gouttières',
        'toiture',
        'printemps',
        4,
        3,
        'semestriel',
        FALSE,
        FALSE,
        0.00,
        60
    ),
    (
        'Traitement anti-mousse toiture',
        'Application produit anti-mousse sur tuiles',
        'toiture',
        'printemps',
        4,
        3,
        'annuel',
        FALSE,
        FALSE,
        40.00,
        120
    ),
    (
        'Remettre eau extérieure',
        'Réouvrir robinets extérieurs après risque gel',
        'plomberie',
        'printemps',
        3,
        2,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        10
    ),
    -- ÉTÉ
    (
        'Entretien portail automatique',
        'Graissage, vérification cellules, télécommandes',
        'exterieur',
        'ete',
        6,
        5,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Contrôle extincteurs',
        'Vérification pression, date péremption',
        'securite',
        'ete',
        6,
        5,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        15
    ),
    (
        'Traitement bois charpente',
        'Traitement préventif anti-insectes xylophages',
        'toiture',
        'ete',
        7,
        6,
        'annuel',
        TRUE,
        FALSE,
        200.00,
        240
    ),
    (
        'Vérification tableau électrique',
        'Contrôle visuel disjoncteurs, test différentiel',
        'electricite',
        'ete',
        6,
        5,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        20
    ),
    (
        'Nettoyage chauffe-eau',
        'Vidange partielle et détartrage',
        'plomberie',
        'ete',
        7,
        6,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        45
    ),
    -- TOUTE L'ANNÉE
    (
        'Relevé compteurs eau',
        'Relevé index compteurs pour suivi consommation',
        'plomberie',
        'toute_annee',
        NULL,
        NULL,
        'trimestriel',
        FALSE,
        FALSE,
        0.00,
        5
    ),
    (
        'Test alarme',
        'Tester le système d''alarme et changer piles détecteurs',
        'securite',
        'toute_annee',
        NULL,
        NULL,
        'trimestriel',
        FALSE,
        FALSE,
        0.00,
        15
    ),
    (
        'Contrôle pression chaudière',
        'Vérifier entre 1 et 1.5 bar',
        'chauffage',
        'toute_annee',
        NULL,
        NULL,
        'trimestriel',
        FALSE,
        FALSE,
        0.00,
        5
    ),
    (
        'Nettoyage filtres aspirateur',
        'Nettoyer/remplacer les filtres',
        'menage',
        'toute_annee',
        NULL,
        NULL,
        'trimestriel',
        FALSE,
        FALSE,
        10.00,
        15
    ),
    (
        'Vérification joints salle de bain',
        'Contrôle moisissures, étanchéité joints silicone',
        'plomberie',
        'toute_annee',
        NULL,
        NULL,
        'semestriel',
        FALSE,
        FALSE,
        15.00,
        20
    ) ON CONFLICT DO NOTHING;
-- Préférences de notification par défaut
INSERT INTO preferences_notifications (
        courses_rappel,
        repas_suggestion,
        stock_alerte,
        meteo_alerte,
        budget_alerte,
        quiet_hours_start,
        quiet_hours_end,
        modules_actifs,
        canal_prefere,
        cree_le,
        modifie_le
    )
VALUES (
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        '22:00',
        '07:00',
        '{
        "cuisine": {"suggestions_repas": true, "stock_bas": true, "batch_cooking": false},
        "famille": {"routines_jules": true, "activites_weekend": true, "achats_planifier": false},
        "maison": {"entretien_programme": true, "charges_payer": true, "jardin_arrosage": false},
        "planning": {"rappels_evenements": true, "taches_retard": true},
        "budget": {"depassement_seuil": true, "resume_mensuel": false}
    }'::jsonb,
        'push',
        NOW(),
        NOW()
    ) ON CONFLICT DO NOTHING;
-- Grants Supabase
GRANT SELECT,
    INSERT,
    UPDATE,
    DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE,
    SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
-- ============================================================================

-- Source: 17_migrations_absorbees.sql
-- ============================================================================
-- ASSISTANT MATANNE — Migrations absorbees (SQL-first)
-- ============================================================================
-- Objectif: conserver un script idempotent pour aligner les schemas existants
-- avec les conventions actuelles quand les colonnes ont evolue.
-- ============================================================================

-- workflow validation v2 (planning + courses)

-- Plannings: ajoute `etat` si absent, puis migre depuis `actif` si present.
ALTER TABLE plannings
    ADD COLUMN IF NOT EXISTS etat VARCHAR(20) NOT NULL DEFAULT 'brouillon';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'plannings' AND column_name = 'actif'
    ) THEN
        UPDATE plannings
        SET etat = CASE
            WHEN actif IS TRUE THEN 'valide'
            ELSE 'archive'
        END
        WHERE etat = 'brouillon';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_plannings_etat ON plannings(etat);

-- Listes de courses: ajoute `etat` et `archivee`, puis migre depuis `statut` si present.
ALTER TABLE listes_courses
    ADD COLUMN IF NOT EXISTS etat VARCHAR(20) NOT NULL DEFAULT 'brouillon';

ALTER TABLE listes_courses
    ADD COLUMN IF NOT EXISTS archivee BOOLEAN NOT NULL DEFAULT FALSE;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'listes_courses' AND column_name = 'statut'
    ) THEN
        UPDATE listes_courses
        SET etat = CASE
            WHEN statut IN ('active', 'en_cours') THEN 'active'
            WHEN statut IN ('completee', 'archivee') THEN 'terminee'
            ELSE 'brouillon'
        END
        WHERE etat = 'brouillon';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_listes_courses_etat ON listes_courses(etat);
CREATE INDEX IF NOT EXISTS ix_listes_courses_archivee ON listes_courses(archivee);

-- Source: migrations/V001__add_repas_jules_columns.sql
-- ============================================================================
-- MIGRATION V001 — Ajout colonnes Jules et contexte sur la table repas
-- ============================================================================
-- Colonnes présentes dans le modèle SQLAlchemy mais absentes du schéma initial.
-- Idempotent : ADD COLUMN IF NOT EXISTS.

ALTER TABLE repas
    ADD COLUMN IF NOT EXISTS plat_jules TEXT,
    ADD COLUMN IF NOT EXISTS notes_jules TEXT,
    ADD COLUMN IF NOT EXISTS adaptation_auto BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS contexte_meteo VARCHAR(50);


-- Source: 99_footer.sql
-- ============================================================================
-- ASSISTANT MATANNE — Vérification finale & COMMIT
-- ============================================================================

-- Grants Supabase (déjà dans seed_data, ici pour réexécution idempotente)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Vérification finale
SELECT tablename,
    (SELECT COUNT(*) FROM information_schema.columns c
     WHERE c.table_name = t.tablename) AS nb_colonnes
FROM pg_tables t
WHERE schemaname = 'public'
ORDER BY tablename;

COMMIT;

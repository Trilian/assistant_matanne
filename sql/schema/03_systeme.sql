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
CREATE TABLE schema_migrations (
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
CREATE TABLE profils_utilisateurs (
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
CREATE TABLE evenements_planning (
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
CREATE TABLE preferences_utilisateurs (
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
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_preferences_user_id ON preferences_utilisateurs(user_id);
CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id ON preferences_utilisateurs(user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.33 OPENFOODFACTS_CACHE

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE openfoodfacts_cache (
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
CREATE TABLE alertes_meteo (
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
CREATE TABLE config_meteo (
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
CREATE TABLE sauvegardes (
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
CREATE TABLE historique_actions (
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

CREATE TABLE logs_securite (
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
CREATE TABLE points_utilisateurs (
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
CREATE TABLE badges_utilisateurs (
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
CREATE TABLE automations (
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
-- 4.13 ARTICLES_COURSES (→ listes_courses, ingredients) — Sprint 12 A5
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
-- 4.XX NORMES_OMS — Référentiel percentiles

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE normes_oms (
    id SERIAL PRIMARY KEY,
    sexe VARCHAR(10) NOT NULL,
    type_mesure VARCHAR(30) NOT NULL,
    age_mois NUMERIC(5, 1) NOT NULL,
    p3 NUMERIC(6, 2) NOT NULL,
    p15 NUMERIC(6, 2) NOT NULL,
    p50 NUMERIC(6, 2) NOT NULL,
    p85 NUMERIC(6, 2) NOT NULL,
    p97 NUMERIC(6, 2) NOT NULL,
    CONSTRAINT ck_normes_sexe CHECK (sexe IN ('garcon', 'fille')),
    CONSTRAINT ck_normes_type CHECK (
        type_mesure IN ('poids', 'taille', 'perimetre_cranien')
    )
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_normes_oms ON normes_oms(sexe, type_mesure, age_mois);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX CONTACTS_FAMILLE — Répertoire familial

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX ANNIVERSAIRES_FAMILLE — Dates importantes et rappels

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.XX CHECKLISTS_ANNIVERSAIRE — Listes de tâches pour préparer les anniversaires

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE checklists_anniversaire (
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

CREATE TABLE items_checklist_anniversaire (
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
-- 5.07 CONTRATS

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.08 FACTURES (→ contrats)

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.09 COMPARATIFS (→ contrats)

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.10 DEPENSES_HOME (→ contrats, factures)

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.11 BUDGETS_HOME

-- ─────────────────────────────────────────────────────────────────────────────
-- 5B.01 JEUX_TIRAGES_EUROMILLIONS

-- ─────────────────────────────────────────────────────────────────────────────
-- 5B.02 JEUX_GRILLES_EUROMILLIONS (→ jeux_tirages_euromillions)

-- ─────────────────────────────────────────────────────────────────────────────
-- 5B.03 JEUX_STATS_EUROMILLIONS

-- ─────────────────────────────────────────────────────────────────────────────
-- 5B.04 JEUX_COTES_HISTORIQUE (→ jeux_matchs)

-- ─────────────────────────────────────────────────────────────────────────────
-- BANKROLL HISTORIQUE (CT-09 Sprint 4)

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE jeux_bankroll_historique (
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
-- PARTIE 5C : TABLES MAISON EXTENSIONS (contrats, artisans, garanties, etc.)
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.01 CONTRATS_MAISON

-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.02 ARTISANS

-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.03 INTERVENTIONS_ARTISANS (→ artisans)

-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.04 GARANTIES

-- ─────────────────────────────────────────────────────────────────────────────
-- 5C.05 INCIDENTS_SAV (→ garanties, artisans)

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


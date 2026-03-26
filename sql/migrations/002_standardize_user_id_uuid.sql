-- ============================================================
-- Migration V002 : Standardiser user_id VARCHAR → UUID
-- ============================================================
-- Objectif : Aligner les colonnes user_id VARCHAR sur le type UUID
--            utilisé par Supabase Auth (auth.uid()).
-- Tables concernées (user_id VARCHAR non UUID) :
--   - preferences_utilisateurs  : VARCHAR(100)
--   - historique_actions        : VARCHAR(255)
--   - etats_persistants         : VARCHAR(100)
--   - configs_calendriers_externes : VARCHAR(100)
--   - retours_recettes          : VARCHAR(100)
--
-- IMPORTANT : Appliquer manuellement dans Supabase SQL Editor
--             ou via psql en production.
--             S'assurer que les valeurs existantes sont des UUID valides
--             AVANT d'exécuter (vérification ci-dessous).
-- ============================================================

-- ── Vérification préalable ──────────────────────────────────
-- Exécuter ces requêtes AVANT la migration pour détecter les
-- valeurs non-UUID qui bloqueraient le cast :

/*
SELECT 'preferences_utilisateurs' AS table_name, user_id
FROM preferences_utilisateurs
WHERE user_id !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$';

SELECT 'historique_actions' AS table_name, user_id
FROM historique_actions
WHERE user_id !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$';

SELECT 'etats_persistants' AS table_name, user_id
FROM etats_persistants
WHERE user_id !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
  AND user_id != 'default';

SELECT 'configs_calendriers_externes' AS table_name, user_id
FROM configs_calendriers_externes
WHERE user_id !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$';

SELECT 'retours_recettes' AS table_name, user_id
FROM retours_recettes
WHERE user_id !~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$';
*/

-- ============================================================
-- DÉBUT DE LA MIGRATION
-- ============================================================

BEGIN;

-- ── 1. preferences_utilisateurs ─────────────────────────────
-- Supprimer l'ancien index unique avant l'ALTER
DROP INDEX IF EXISTS uq_user_preferences_user_id;
DROP INDEX IF EXISTS ix_user_preferences_user_id;

ALTER TABLE preferences_utilisateurs
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

-- Recréer les index
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_preferences_user_id
    ON preferences_utilisateurs(user_id);
CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id
    ON preferences_utilisateurs(user_id);

-- ── 2. historique_actions ────────────────────────────────────
DROP INDEX IF EXISTS idx_action_history_user_id;

ALTER TABLE historique_actions
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

CREATE INDEX IF NOT EXISTS idx_action_history_user_id
    ON historique_actions(user_id);

-- ── 3. etats_persistants ─────────────────────────────────────
-- Note : la valeur par défaut 'default' n'est pas un UUID valide.
-- Les lignes avec user_id = 'default' doivent être supprimées ou
-- migrées vers un UUID système avant l'ALTER.
-- On retire d'abord le DEFAULT qui référence 'default' (non-UUID).
DROP INDEX IF EXISTS uq_pstate_namespace_user;
DROP INDEX IF EXISTS ix_pstate_user;

ALTER TABLE etats_persistants
    ALTER COLUMN user_id DROP DEFAULT,
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

CREATE INDEX IF NOT EXISTS ix_pstate_user
    ON etats_persistants(user_id);
ALTER TABLE etats_persistants
    ADD CONSTRAINT uq_pstate_namespace_user UNIQUE (namespace, user_id);

-- ── 4. configs_calendriers_externes ─────────────────────────
DROP INDEX IF EXISTS ix_external_cal_user;
DROP INDEX IF EXISTS uq_user_calendar;

ALTER TABLE configs_calendriers_externes
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

CREATE INDEX IF NOT EXISTS ix_external_cal_user
    ON configs_calendriers_externes(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_calendar
    ON configs_calendriers_externes(user_id, provider, name);

-- ── 5. retours_recettes ──────────────────────────────────────
DROP INDEX IF EXISTS ix_recipe_feedbacks_user;
DROP INDEX IF EXISTS uq_user_recipe_feedback;

ALTER TABLE retours_recettes
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

CREATE INDEX IF NOT EXISTS ix_recipe_feedbacks_user
    ON retours_recettes(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_recipe_feedback
    ON retours_recettes(user_id, recette_id);

COMMIT;

-- ============================================================
-- ROLLBACK (si nécessaire)
-- ============================================================
/*
BEGIN;

ALTER TABLE preferences_utilisateurs
    ALTER COLUMN user_id TYPE VARCHAR(100) USING user_id::TEXT;
ALTER TABLE historique_actions
    ALTER COLUMN user_id TYPE VARCHAR(255) USING user_id::TEXT;
ALTER TABLE etats_persistants
    ALTER COLUMN user_id TYPE VARCHAR(100) USING user_id::TEXT;
ALTER TABLE configs_calendriers_externes
    ALTER COLUMN user_id TYPE VARCHAR(100) USING user_id::TEXT;
ALTER TABLE retours_recettes
    ALTER COLUMN user_id TYPE VARCHAR(100) USING user_id::TEXT;

COMMIT;
*/

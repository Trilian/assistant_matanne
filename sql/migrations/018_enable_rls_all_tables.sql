-- ============================================================================
-- Migration 018: Enable Row Level Security on all public tables
-- Date: 2026-02-16
-- Description: Active RLS sur toutes les tables publiques pour sécuriser
--              l'accès via PostgREST et l'API Supabase
-- Issue: Supabase linter détecte 78 tables sans RLS activé
-- ============================================================================
-- ============================================================================
-- UPGRADE
-- ============================================================================
BEGIN;
-- ----------------------------------------------------------------------------
-- Table de migration (accès limité au service_role uniquement)
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.schema_migrations ENABLE ROW LEVEL SECURITY;
-- Politiques pour table de migration (service_role uniquement)
DROP POLICY IF EXISTS "service_role_schema_migrations" ON public.schema_migrations;
CREATE POLICY "service_role_schema_migrations" ON public.schema_migrations FOR ALL TO service_role USING (true) WITH CHECK (true);
-- ----------------------------------------------------------------------------
-- Tables Jeux (paris sportifs & loto)
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.jeux_series ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_alertes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_configuration ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_stats_loto ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_historique ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_equipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_matchs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_paris_sportifs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_tirages_loto ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.jeux_grilles_loto ENABLE ROW LEVEL SECURITY;
-- Politiques jeux (authenticated + service_role)
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'jeux_series', 'jeux_alertes', 'jeux_configuration',
        'jeux_stats_loto', 'jeux_historique', 'jeux_equipes',
        'jeux_matchs', 'jeux_paris_sportifs', 'jeux_tirages_loto',
        'jeux_grilles_loto'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Utilisateurs et Profils
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.child_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.notification_preferences ENABLE ROW LEVEL SECURITY;
-- Politiques profils utilisateurs
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'user_profiles', 'user_preferences', 'child_profiles',
        'notification_preferences'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Recettes et Cuisine
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.recettes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.recette_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.etapes_recette ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.versions_recette ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.historique_recettes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.recipe_feedbacks ENABLE ROW LEVEL SECURITY;
-- Politiques recettes
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'recettes', 'recette_ingredients', 'ingredients',
        'etapes_recette', 'versions_recette', 'historique_recettes',
        'recipe_feedbacks'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Batch Cooking
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.batch_meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.sessions_batch_cooking ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.etapes_batch_cooking ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.preparations_batch ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.config_batch_cooking ENABLE ROW LEVEL SECURITY;
-- Politiques batch cooking
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'batch_meals', 'sessions_batch_cooking', 'etapes_batch_cooking',
        'preparations_batch', 'config_batch_cooking'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Inventaire et Courses
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.inventaire ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.historique_inventaire ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.listes_courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.liste_courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.modeles_courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.articles_modeles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.shopping_items_famille ENABLE ROW LEVEL SECURITY;
-- Politiques inventaire et courses
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'inventaire', 'historique_inventaire', 'listes_courses',
        'liste_courses', 'modeles_courses', 'articles_modeles',
        'shopping_items_famille'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Planning et Calendrier
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.plannings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.repas ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.calendriers_externes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.evenements_calendrier ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.external_calendar_configs ENABLE ROW LEVEL SECURITY;
-- Politiques planning
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'plannings', 'repas', 'calendar_events', 'calendriers_externes',
        'evenements_calendrier', 'external_calendar_configs'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Famille (Jules, activités, achats)
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.family_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.family_budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.family_purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.weekend_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.wellbeing_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.milestones ENABLE ROW LEVEL SECURITY;
-- Politiques famille
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'family_activities', 'family_budgets', 'family_purchases',
        'weekend_activities', 'wellbeing_entries', 'milestones'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Santé et Fitness
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.health_objectives ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.health_routines ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.health_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.food_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.garmin_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.garmin_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.garmin_daily_summaries ENABLE ROW LEVEL SECURITY;
-- Politiques santé (données sensibles)
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'health_objectives', 'health_routines', 'health_entries',
        'food_logs', 'garmin_tokens', 'garmin_activities',
        'garmin_daily_summaries'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Maison et Jardin
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.house_stock ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.house_stocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.house_expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.furniture ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.garden_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.garden_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.garden_zones ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.maintenance_tasks ENABLE ROW LEVEL SECURITY;
-- Politiques maison et jardin
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'house_stock', 'house_stocks', 'house_expenses', 'furniture',
        'garden_items', 'garden_logs', 'garden_zones', 'maintenance_tasks'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Projets et Routines
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.project_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.routines ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.routine_tasks ENABLE ROW LEVEL SECURITY;
-- Politiques projets et routines
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'projects', 'project_tasks', 'routines', 'routine_tasks'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Budget et Dépenses
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.depenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.budgets_mensuels ENABLE ROW LEVEL SECURITY;
-- Politiques budget
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(ARRAY ['depenses', 'budgets_mensuels']) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Tables Système et Notifications
-- ----------------------------------------------------------------------------
ALTER TABLE IF EXISTS public.eco_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.openfoodfacts_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.alertes_meteo ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.backups ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.push_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.config_meteo ENABLE ROW LEVEL SECURITY;
-- Politiques système
DO $$
DECLARE t TEXT;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'eco_actions', 'openfoodfacts_cache', 'alertes_meteo',
        'backups', 'push_subscriptions', 'config_meteo'
    ]
    ) LOOP EXECUTE format(
        'DROP POLICY IF EXISTS "authenticated_access_%I" ON public.%I',
        t,
        t
    );
EXECUTE format(
    'CREATE POLICY "authenticated_access_%I" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
    t,
    t
);
EXECUTE format(
    'DROP POLICY IF EXISTS "service_role_access_%I" ON public.%I',
    t,
    t
);
EXECUTE format(
    'CREATE POLICY "service_role_access_%I" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
    t,
    t
);
END LOOP;
END $$;
-- ----------------------------------------------------------------------------
-- Vérification finale: Toutes les tables avec RLS activé
-- ----------------------------------------------------------------------------
DO $$
DECLARE tables_without_rls TEXT [];
t TEXT;
BEGIN
SELECT array_agg(tablename) INTO tables_without_rls
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename NOT IN (
        SELECT relname
        FROM pg_class
        WHERE relnamespace = 'public'::regnamespace
            AND relrowsecurity = true
    );
IF tables_without_rls IS NOT NULL
AND array_length(tables_without_rls, 1) > 0 THEN RAISE NOTICE 'Tables sans RLS: %',
tables_without_rls;
ELSE RAISE NOTICE 'RLS activé sur toutes les tables publiques';
END IF;
END $$;
COMMIT;
-- ============================================================================
-- NOTES D'IMPLÉMENTATION
-- ============================================================================
--
-- Stratégie RLS:
-- 1. service_role: Accès complet (utilisé par Streamlit backend via DATABASE_URL)
-- 2. authenticated: Accès complet (pour future auth Supabase si implémentée)
-- 3. anon: Pas d'accès (PostgREST avec clé anonyme bloqué)
--
-- Cette configuration:
-- ✓ Bloque l'accès via l'API publique Supabase (anon key)
-- ✓ Permet l'accès backend Streamlit (service_role)
-- ✓ Prépare pour auth utilisateur future (authenticated)
--
-- Tables avec données sensibles (tokens, session_id):
-- - garmin_tokens: oauth_token
-- - external_calendar_configs: access_token, refresh_token
-- - push_subscriptions: auth_key
-- - etapes_batch_cooking: session_id
-- - preparations_batch: session_id
--
-- Ces tables ont les mêmes politiques mais pourraient avoir des règles
-- plus restrictives si l'app évolue vers multi-utilisateur.
-- ============================================================================
-- ============================================================================
-- DOWNGRADE (à exécuter manuellement si rollback nécessaire)
-- ============================================================================
-- BEGIN;
--
-- -- Désactiver RLS sur toutes les tables
-- DO $$
-- DECLARE
--     r RECORD;
-- BEGIN
--     FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
--         EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY', r.tablename);
--         -- Les politiques sont automatiquement ignorées quand RLS est désactivé
--     END LOOP;
-- END $$;
--
-- COMMIT;
-- ============================================================================
-- ============================================================================
-- QUERIES DE VÉRIFICATION
-- ============================================================================
--
-- Vérifier le statut RLS de toutes les tables:
-- SELECT
--     schemaname,
--     tablename,
--     CASE
--         WHEN relrowsecurity THEN '✓ RLS ON'
--         ELSE '✗ RLS OFF'
--     END as rls_status
-- FROM pg_tables t
-- JOIN pg_class c ON t.tablename = c.relname
-- WHERE schemaname = 'public'
-- ORDER BY tablename;
--
-- Lister les politiques par table:
-- SELECT
--     schemaname,
--     tablename,
--     policyname,
--     roles,
--     cmd,
--     qual
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;
-- ============================================================================

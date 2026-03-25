-- ============================================================================
-- V001 — Correctif sécurité RLS : filtrage par auth.uid()
-- ============================================================================
-- Date : 2026-03-25
-- Description : Les policies RLS étaient trop permissives (USING (true)).
--   Ce correctif restreint l'accès aux tables avec user_id pour que chaque
--   utilisateur ne voie que ses propres données.
--
-- Tables affectées :
--   - Tables avec user_id UUID : calendriers_externes, evenements_calendrier,
--     depenses, budgets_mensuels, alertes_meteo, config_meteo, sauvegardes,
--     abonnements_push, preferences_notifications, webhooks_abonnements
--   - Tables avec user_id VARCHAR : preferences_utilisateurs, retours_recettes,
--     configs_calendriers_externes, etats_persistants, historique_actions
--   - Tables système/référence : passage en lecture seule pour authenticated
--
-- Pré-requis : INIT_COMPLET.sql déjà appliqué
-- ============================================================================

BEGIN;

-- 1. Tables avec user_id UUID → filtrage par auth.uid()
DO $$
DECLARE t TEXT;
tables_uuid TEXT[] := ARRAY[
    'calendriers_externes', 'evenements_calendrier',
    'depenses', 'budgets_mensuels',
    'alertes_meteo', 'config_meteo',
    'sauvegardes',
    'abonnements_push', 'preferences_notifications',
    'webhooks_abonnements'
];
BEGIN FOREACH t IN ARRAY tables_uuid LOOP
    -- Supprimer l'ancienne policy permissive
    EXECUTE format('DROP POLICY IF EXISTS "authenticated_access_%s" ON public.%I', t, t);
    -- Créer la policy filtrant par user_id
    EXECUTE format(
        'CREATE POLICY "authenticated_access_%s" ON public.%I FOR ALL TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid())',
        t, t
    );
END LOOP;
END $$;

-- 2. Tables avec user_id VARCHAR → filtrage par auth.uid()::text
DO $$
DECLARE t TEXT;
tables_varchar TEXT[] := ARRAY[
    'preferences_utilisateurs', 'retours_recettes',
    'configs_calendriers_externes', 'etats_persistants',
    'historique_actions'
];
BEGIN FOREACH t IN ARRAY tables_varchar LOOP
    EXECUTE format('DROP POLICY IF EXISTS "authenticated_access_%s" ON public.%I', t, t);
    EXECUTE format(
        'CREATE POLICY "authenticated_access_%s" ON public.%I FOR ALL TO authenticated USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text)',
        t, t
    );
END LOOP;
END $$;

-- 3. Tables système/référence → lecture seule pour authenticated
DO $$
DECLARE t TEXT;
tables_readonly TEXT[] := ARRAY[
    'schema_migrations',
    'normes_oms', 'plantes_catalogue',
    'preferences_home', 'taches_home', 'stats_home',
    'contrats', 'factures', 'comparatifs', 'depenses_home', 'budgets_home'
];
BEGIN FOREACH t IN ARRAY tables_readonly LOOP
    EXECUTE format('DROP POLICY IF EXISTS "authenticated_access_%s" ON public.%I', t, t);
    EXECUTE format(
        'CREATE POLICY "authenticated_read_%s" ON public.%I FOR SELECT TO authenticated USING (true)',
        t, t
    );
END LOOP;
END $$;

-- Tracker cette migration
INSERT INTO schema_migrations (numero, description)
VALUES ('V001', 'RLS security fix: filtrage par auth.uid()')
ON CONFLICT DO NOTHING;

COMMIT;

-- ============================================================================
-- ROLLBACK (si nécessaire) :
-- Restaurer les anciennes policies permissives :
--   DO $$ ... CREATE POLICY ... USING (true) WITH CHECK (true) ... END $$;
-- ============================================================================

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
    'jeux_cotes_historique',
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
    'normes_oms', 'plantes_catalogue',
    -- Legacy migration tables (read-only, données historiques)
    'preferences_home', 'taches_home', 'stats_home',
    'factures', 'comparatifs', 'depenses_home', 'budgets_home'
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

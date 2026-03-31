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

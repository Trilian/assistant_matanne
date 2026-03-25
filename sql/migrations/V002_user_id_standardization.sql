-- ============================================================================
-- V002 — Standardisation user_id : VARCHAR → UUID + tables manquantes
-- ============================================================================
-- Date : 2026-03-25
-- Description : Certaines tables utilisent user_id VARCHAR(100) au lieu de UUID.
--   Cela empêche le filtrage RLS par auth.uid() (qui retourne un UUID).
--   Ce script :
--   1. Convertit les colonnes user_id VARCHAR → UUID là où c'est possible
--   2. Crée les tables manquantes (webhooks_abonnements, etats_persistants)
--
-- ATTENTION : Cette migration nécessite que les valeurs user_id existantes
--   soient des UUID valides (format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).
--   Si ce n'est pas le cas, un nettoyage préalable est nécessaire.
--
-- Tables affectées :
--   - preferences_utilisateurs (user_id VARCHAR(100) → UUID)
--   - configs_calendriers_externes (user_id VARCHAR(100) → UUID)
--   - retours_recettes (user_id VARCHAR(100) → UUID)
-- ============================================================================

BEGIN;

-- 1. Créer tables manquantes (idempotent)
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

CREATE TABLE IF NOT EXISTS etats_persistants (
    id SERIAL PRIMARY KEY,
    namespace VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL DEFAULT 'default',
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_pstate_namespace_user'
    ) THEN
        ALTER TABLE etats_persistants ADD CONSTRAINT uq_pstate_namespace_user UNIQUE (namespace, user_id);
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS ix_pstate_namespace ON etats_persistants(namespace);
CREATE INDEX IF NOT EXISTS ix_pstate_user ON etats_persistants(user_id);

-- 2. Convertir user_id VARCHAR → UUID (si les données le permettent)
-- NOTE : Décommenter ces blocs uniquement après vérification que les
--        valeurs user_id existantes sont des UUID valides.
--        En mode développement avec user_id = "dev-user", cette migration
--        ne peut PAS être appliquée directement.

-- ALTER TABLE preferences_utilisateurs
--     ALTER COLUMN user_id TYPE UUID USING user_id::uuid;
-- ALTER TABLE configs_calendriers_externes
--     ALTER COLUMN user_id TYPE UUID USING user_id::uuid;
-- ALTER TABLE retours_recettes
--     ALTER COLUMN user_id TYPE UUID USING user_id::uuid;

-- Tracker cette migration
INSERT INTO schema_migrations (numero, description)
VALUES ('V002', 'Standardisation user_id + tables manquantes')
ON CONFLICT DO NOTHING;

COMMIT;

-- ============================================================================
-- ROLLBACK :
-- DROP TABLE IF EXISTS webhooks_abonnements;
-- DROP TABLE IF EXISTS etats_persistants;
-- Pour la conversion UUID → VARCHAR :
--   ALTER TABLE preferences_utilisateurs ALTER COLUMN user_id TYPE VARCHAR(100);
-- ============================================================================

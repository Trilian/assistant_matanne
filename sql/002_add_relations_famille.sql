-- ============================================================
-- MIGRATION SUPABASE - Mises à jour relations Famille
-- ============================================================
-- Ajoute/met à jour les relations bidirectionnelles
-- Date: 2026-01-24
-- Version: 1.1
-- ============================================================

-- Cette migration suppose que child_profiles existe
-- (créée lors de la migration 001_add_famille_models.sql)

-- ============================================================
-- 1. CRÉER WELLBEING_ENTRIES SI N'EXISTE PAS
-- ============================================================
CREATE TABLE IF NOT EXISTS wellbeing_entries (
    id BIGSERIAL PRIMARY KEY,
    child_id BIGINT REFERENCES child_profiles(id) ON DELETE CASCADE,
    username VARCHAR(200),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    mood VARCHAR(100),
    sleep_hours FLOAT,
    activity VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wellbeing_entries_child_id 
ON wellbeing_entries(child_id);

CREATE INDEX IF NOT EXISTS idx_wellbeing_entries_date 
ON wellbeing_entries(date);

-- ============================================================
-- 2. AJOUTER CONTRAINTES FK SI N'EXISTENT PAS
-- ============================================================

-- wellbeing_entries → child_profiles (si pas déjà présent)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_wellbeing_child_profiles'
    ) THEN
        ALTER TABLE wellbeing_entries
        ADD CONSTRAINT fk_wellbeing_child_profiles
        FOREIGN KEY (child_id) REFERENCES child_profiles(id) ON DELETE CASCADE;
    END IF;
END
$$;

-- milestones → child_profiles (si pas déjà présent)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_milestones_child_profiles'
    ) THEN
        ALTER TABLE milestones
        ADD CONSTRAINT fk_milestones_child_profiles
        FOREIGN KEY (child_id) REFERENCES child_profiles(id) ON DELETE CASCADE;
    END IF;
END
$$;

-- health_entries → health_routines (si pas déjà présent)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_health_entries_health_routines'
    ) THEN
        ALTER TABLE health_entries
        ADD CONSTRAINT fk_health_entries_health_routines
        FOREIGN KEY (routine_id) REFERENCES health_routines(id) ON DELETE CASCADE;
    END IF;
END
$$;

-- ============================================================
-- 3. INDICES DE PERFORMANCE (IF NOT EXISTS)
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_wellbeing_entries_child_id 
ON wellbeing_entries(child_id);

CREATE INDEX IF NOT EXISTS idx_milestones_child_id
ON milestones(child_id);

CREATE INDEX IF NOT EXISTS idx_health_entries_routine_id
ON health_entries(routine_id);

-- ============================================================
-- RÉSUMÉ DES CHANGEMENTS
-- ============================================================
/*
Tables créées:
✅ wellbeing_entries (avec FK à child_profiles)

Contraintes FK ajoutées:
✅ wellbeing_entries → child_profiles
✅ milestones → child_profiles
✅ health_entries → health_routines

Indices créés:
✅ idx_wellbeing_entries_child_id
✅ idx_wellbeing_entries_date
✅ idx_milestones_child_id
✅ idx_health_entries_routine_id

Note: Utilise DO $$ ... $$ pour éviter les erreurs 
si les contraintes existent déjà
*/

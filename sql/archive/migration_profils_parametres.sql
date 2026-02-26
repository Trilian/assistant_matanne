-- ═══════════════════════════════════════════════════════════
-- MIGRATION: Profils & Paramètres — Colonnes sécurité, préférences, notifications
-- Date: 2026-02
-- Description: Ajoute les colonnes nécessaires au module Paramètres étendu
--   - profils_utilisateurs: pin_hash, sections_protegees, preferences_modules, theme_prefere
--   - preferences_notifications: modules_actifs, canal_prefere
--   - Seed data: Anne & Mathieu (si absents)
-- ═══════════════════════════════════════════════════════════

-- IMPORTANT: Exécuter cette migration sur la base Supabase APRÈS INIT_COMPLET.sql
-- ou sur une base existante qui ne possède pas encore ces colonnes.

BEGIN;

-- ═══════════════════════════════════════════════════════════
-- PARTIE 1: Nouvelles colonnes profils_utilisateurs
-- ═══════════════════════════════════════════════════════════

-- PIN de sécurité (hash SHA-256)
ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS pin_hash VARCHAR(255);

-- Sections protégées par PIN (liste JSON, ex: ["budget", "sante", "admin"])
ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS sections_protegees JSONB;

-- Préférences par module (JSON structuré par domaine)
ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS preferences_modules JSONB;

-- Thème d'affichage préféré (auto, clair, sombre)
ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS theme_prefere VARCHAR(20) DEFAULT 'auto';

-- ═══════════════════════════════════════════════════════════
-- PARTIE 2: Nouvelles colonnes preferences_notifications
-- ═══════════════════════════════════════════════════════════

-- Modules actifs pour les notifications (JSON par module)
ALTER TABLE preferences_notifications
    ADD COLUMN IF NOT EXISTS modules_actifs JSONB DEFAULT '{}'::jsonb;

-- Canal de notification préféré (push, email, sms)
ALTER TABLE preferences_notifications
    ADD COLUMN IF NOT EXISTS canal_prefere VARCHAR(20) DEFAULT 'push';

-- ═══════════════════════════════════════════════════════════
-- PARTIE 3: Alignement profils_utilisateurs avec le modèle ORM
-- ═══════════════════════════════════════════════════════════
-- Le modèle ORM utilise username/display_name au lieu de nom,
-- et a des colonnes fitness supplémentaires.
-- Ces ALTER n'échouent pas si les colonnes existent déjà (IF NOT EXISTS).

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS username VARCHAR(50);

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS display_name VARCHAR(100);

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS avatar_emoji VARCHAR(10) DEFAULT '👤';

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS date_naissance DATE;

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS objectif_poids_kg FLOAT;

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS objectif_calories_brulees INTEGER DEFAULT 500;

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS objectif_minutes_actives INTEGER DEFAULT 30;

ALTER TABLE profils_utilisateurs
    ADD COLUMN IF NOT EXISTS garmin_connected BOOLEAN DEFAULT FALSE;

-- Index unique sur username (si pas encore présent)
CREATE UNIQUE INDEX IF NOT EXISTS uq_profils_username
    ON profils_utilisateurs(username);

-- ═══════════════════════════════════════════════════════════
-- PARTIE 4: Seed Data — Profils Anne & Mathieu
-- ═══════════════════════════════════════════════════════════

-- Insère Anne si absente (ON CONFLICT sur username)
INSERT INTO profils_utilisateurs (
    username, display_name, email, avatar_emoji,
    taille_cm, poids_kg, objectif_pas_quotidien,
    objectif_calories_brulees, objectif_minutes_actives,
    garmin_connected, theme_prefere, preferences_modules,
    cree_le, modifie_le
) VALUES (
    'anne', 'Anne', NULL, '👩',
    NULL, NULL, 10000,
    500, 30,
    FALSE, 'auto', '{
        "cuisine": {"nb_suggestions_ia": 5, "types_cuisine_preferes": [], "duree_max_batch_min": 120},
        "famille": {"activites_favorites_jules": [], "frequence_rappels_routines": "quotidien"},
        "maison": {"seuil_alerte_entretien_jours": 7},
        "planning": {"horizon_defaut": "semaine"},
        "budget": {"seuils_alerte_pct": 80}
    }'::jsonb,
    NOW(), NOW()
) ON CONFLICT (username) DO NOTHING;

-- Insère Mathieu si absent (ON CONFLICT sur username)
INSERT INTO profils_utilisateurs (
    username, display_name, email, avatar_emoji,
    taille_cm, poids_kg, objectif_pas_quotidien,
    objectif_calories_brulees, objectif_minutes_actives,
    garmin_connected, theme_prefere, preferences_modules,
    cree_le, modifie_le
) VALUES (
    'mathieu', 'Mathieu', NULL, '👨',
    NULL, NULL, 10000,
    500, 30,
    FALSE, 'auto', '{
        "cuisine": {"nb_suggestions_ia": 5, "types_cuisine_preferes": [], "duree_max_batch_min": 120},
        "famille": {"activites_favorites_jules": [], "frequence_rappels_routines": "quotidien"},
        "maison": {"seuil_alerte_entretien_jours": 7},
        "planning": {"horizon_defaut": "semaine"},
        "budget": {"seuils_alerte_pct": 80}
    }'::jsonb,
    NOW(), NOW()
) ON CONFLICT (username) DO NOTHING;

-- Insère les préférences de notification par défaut (si absentes)
INSERT INTO preferences_notifications (
    courses_rappel, repas_suggestion, stock_alerte,
    meteo_alerte, budget_alerte,
    quiet_hours_start, quiet_hours_end,
    modules_actifs, canal_prefere,
    created_at, updated_at
) VALUES (
    TRUE, TRUE, TRUE,
    TRUE, TRUE,
    '22:00', '07:00',
    '{
        "cuisine": {"suggestions_repas": true, "stock_bas": true, "batch_cooking": false},
        "famille": {"routines_jules": true, "activites_weekend": true, "achats_planifier": false},
        "maison": {"entretien_programme": true, "charges_payer": true, "jardin_arrosage": false},
        "planning": {"rappels_evenements": true, "taches_retard": true},
        "budget": {"depassement_seuil": true, "resume_mensuel": false}
    }'::jsonb,
    'push',
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════
-- PARTIE 5: Vérification
-- ═══════════════════════════════════════════════════════════

-- Vérifie les colonnes ajoutées
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'profils_utilisateurs'
  AND column_name IN ('pin_hash', 'sections_protegees', 'preferences_modules', 'theme_prefere', 'username')
ORDER BY column_name;

SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'preferences_notifications'
  AND column_name IN ('modules_actifs', 'canal_prefere')
ORDER BY column_name;

-- Vérifie les profils insérés
SELECT id, username, display_name, avatar_emoji, theme_prefere
FROM profils_utilisateurs
ORDER BY id;

COMMIT;

-- ═══════════════════════════════════════════════════════════
-- FIN DE LA MIGRATION
-- ═══════════════════════════════════════════════════════════

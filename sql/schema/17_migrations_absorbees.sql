-- ============================================================================
-- ASSISTANT MATANNE — Migrations absorbées (V005-V007)
-- ============================================================================
-- Ce fichier contient les changements des migrations V005, V006, V007
-- qui ont été absorbés dans le script principal.
-- Contexte : stratégie SQL-first (pas d'Alembic auto).
-- ============================================================================

-- V005 : index composites + contraintes CHECK
-- -> absorbés dans `14_indexes.sql` pour conserver un point d'entrée unique.

-- V006 : nettoyage des tables legacy maison / santé
-- Ces suppressions sont idempotentes afin de pouvoir réappliquer le script
-- sur une base existante sans erreur.
DROP VIEW IF EXISTS v_taches_jour CASCADE;
DROP VIEW IF EXISTS v_charge_semaine CASCADE;

DROP TABLE IF EXISTS archive_articles CASCADE;
DROP TABLE IF EXISTS journal_sante CASCADE;
DROP TABLE IF EXISTS stats_home CASCADE;
DROP TABLE IF EXISTS taches_home CASCADE;

-- V007 : nettoyage d'indexes legacy absorbés dans le schéma principal.
DROP INDEX IF EXISTS idx_taches_home_domaine;
DROP INDEX IF EXISTS idx_taches_home_statut;
DROP INDEX IF EXISTS idx_taches_home_date_due;
DROP INDEX IF EXISTS idx_taches_home_source;
DROP INDEX IF EXISTS idx_stats_home_date;


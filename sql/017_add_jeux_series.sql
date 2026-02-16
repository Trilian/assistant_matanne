-- ============================================================================
-- Migration 017: Add series tracking models for jeux
-- Date: 2026-02-16
-- Description: Tables pour le tracking des séries (loi des séries)
--   - jeux_series: Track série actuelle par marché/numéro
--   - jeux_alertes: Alertes d'opportunités
--   - jeux_configuration: Configuration des seuils
-- ============================================================================
-- ============================================================================
-- UPGRADE
-- ============================================================================
BEGIN;
-- ----------------------------------------------------------------------------
-- Table: jeux_series
-- Stocke les séries en cours pour chaque marché (paris) ou numéro (loto)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jeux_series (
    id SERIAL PRIMARY KEY,
    type_jeu VARCHAR(20) NOT NULL,
    -- 'paris' ou 'loto'
    championnat VARCHAR(50),
    -- Championnat (paris only, NULL pour loto)
    marche VARCHAR(50) NOT NULL,
    -- Ex: 'domicile_mi_temps', '7', 'chance_42'
    serie_actuelle INTEGER NOT NULL DEFAULT 0,
    -- Nb événements depuis dernière occurrence
    frequence FLOAT NOT NULL DEFAULT 0.0,
    -- Fréquence historique (0.0 à 1.0)
    nb_occurrences INTEGER NOT NULL DEFAULT 0,
    -- Nb total d'occurrences historiques
    nb_total INTEGER NOT NULL DEFAULT 0,
    -- Nb total d'événements analysés
    derniere_occurrence DATE,
    -- Date dernière occurrence de l'événement
    derniere_mise_a_jour TIMESTAMP,
    -- Dernière mise à jour de la série
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Index pour recherches fréquentes
CREATE INDEX IF NOT EXISTS ix_jeux_series_type_jeu_championnat ON jeux_series(type_jeu, championnat);
CREATE INDEX IF NOT EXISTS ix_jeux_series_type_jeu_marche ON jeux_series(type_jeu, marche);
-- Index pour calcul des opportunités (value = frequence × serie)
CREATE INDEX IF NOT EXISTS ix_jeux_series_value ON jeux_series((frequence * serie_actuelle) DESC);
COMMENT ON TABLE jeux_series IS 'Tracking des séries pour la loi des séries (Paris & Loto)';
COMMENT ON COLUMN jeux_series.type_jeu IS 'Type de jeu: paris ou loto';
COMMENT ON COLUMN jeux_series.marche IS 'Identifiant marché: domicile_mi_temps, exterieur_final, ou numéro loto';
COMMENT ON COLUMN jeux_series.serie_actuelle IS 'Nombre d''événements depuis dernière occurrence';
COMMENT ON COLUMN jeux_series.frequence IS 'Fréquence historique = nb_occurrences / nb_total';
-- ----------------------------------------------------------------------------
-- Table: jeux_alertes
-- Historique des alertes créées quand value >= seuil
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jeux_alertes (
    id SERIAL PRIMARY KEY,
    serie_id INTEGER NOT NULL REFERENCES jeux_series(id) ON DELETE CASCADE,
    type_jeu VARCHAR(20) NOT NULL,
    -- 'paris' ou 'loto'
    championnat VARCHAR(50),
    -- Championnat (paris only)
    marche VARCHAR(50) NOT NULL,
    -- Marché concerné
    value_alerte FLOAT NOT NULL,
    -- Value au moment de l'alerte
    serie_alerte INTEGER NOT NULL,
    -- Série au moment de l'alerte
    frequence_alerte FLOAT NOT NULL,
    -- Fréquence au moment de l'alerte
    seuil_utilise FLOAT NOT NULL DEFAULT 2.0,
    -- Seuil qui a déclenché l'alerte
    notifie BOOLEAN NOT NULL DEFAULT FALSE,
    -- Notification envoyée?
    date_notification TIMESTAMP,
    -- Date d'envoi notification
    resultat_verifie BOOLEAN NOT NULL DEFAULT FALSE,
    -- Résultat vérifié?
    resultat_correct BOOLEAN,
    -- Prédiction correcte? (NULL = pas vérifié)
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Index pour alertes non notifiées
CREATE INDEX IF NOT EXISTS ix_jeux_alertes_notifie ON jeux_alertes(notifie)
WHERE notifie = FALSE;
-- Index pour analyse des résultats
CREATE INDEX IF NOT EXISTS ix_jeux_alertes_resultat ON jeux_alertes(resultat_verifie, resultat_correct);
COMMENT ON TABLE jeux_alertes IS 'Historique des alertes d''opportunités (value >= seuil)';
COMMENT ON COLUMN jeux_alertes.value_alerte IS 'Value = frequence × serie au moment de l''alerte';
COMMENT ON COLUMN jeux_alertes.resultat_correct IS 'TRUE si l''événement est arrivé après l''alerte';
-- ----------------------------------------------------------------------------
-- Table: jeux_configuration
-- Configuration paramétrable des seuils et intervalles
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jeux_configuration (
    id SERIAL PRIMARY KEY,
    cle VARCHAR(50) NOT NULL UNIQUE,
    -- Clé de configuration
    valeur TEXT NOT NULL,
    -- Valeur (string, convertir selon usage)
    description TEXT,
    -- Description pour UI
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE jeux_configuration IS 'Configuration des seuils et paramètres jeux';
-- Insérer configurations par défaut
INSERT INTO jeux_configuration (cle, valeur, description)
VALUES (
        'seuil_value_alerte',
        '2.0',
        'Seuil de value minimum pour créer une alerte'
    ),
    (
        'seuil_value_haute',
        '2.5',
        'Seuil de value pour opportunité haute (indicateur vert)'
    ),
    (
        'seuil_series_minimum',
        '3',
        'Série minimum pour considérer comme significatif'
    ),
    (
        'sync_paris_interval_hours',
        '6',
        'Intervalle de synchronisation paris sportifs en heures'
    ),
    (
        'sync_loto_days',
        'mon,wed,sat',
        'Jours de synchronisation loto (lun, mer, sam)'
    ),
    (
        'sync_loto_hour',
        '21:30',
        'Heure de synchronisation loto après tirage'
    ) ON CONFLICT (cle) DO NOTHING;
COMMIT;
-- ============================================================================
-- DOWNGRADE (à exécuter manuellement si rollback nécessaire)
-- ============================================================================
-- BEGIN;
-- DROP TABLE IF EXISTS jeux_configuration CASCADE;
-- DROP TABLE IF EXISTS jeux_alertes CASCADE;
-- DROP TABLE IF EXISTS jeux_series CASCADE;
-- COMMIT;
-- ============================================================================
-- QUERIES UTILES
-- ============================================================================
-- Trouver les opportunités actuelles (value >= 2.0)
-- SELECT
--     type_jeu,
--     championnat,
--     marche,
--     serie_actuelle,
--     frequence,
--     ROUND((frequence * serie_actuelle)::numeric, 2) as value,
--     derniere_occurrence
-- FROM jeux_series
-- WHERE (frequence * serie_actuelle) >= 2.0
-- ORDER BY (frequence * serie_actuelle) DESC;
-- Stats des alertes
-- SELECT
--     type_jeu,
--     COUNT(*) as total_alertes,
--     COUNT(*) FILTER (WHERE resultat_correct = TRUE) as corrects,
--     COUNT(*) FILTER (WHERE resultat_correct = FALSE) as incorrects,
--     ROUND(100.0 * COUNT(*) FILTER (WHERE resultat_correct = TRUE) /
--           NULLIF(COUNT(*) FILTER (WHERE resultat_verifie = TRUE), 0), 1) as taux_reussite
-- FROM jeux_alertes
-- GROUP BY type_jeu;

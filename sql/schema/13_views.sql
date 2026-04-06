-- PARTIE 7 : VUES UTILES
-- ============================================================================
-- Vue: Objets à remplacer avec priorité
DROP VIEW IF EXISTS v_objets_a_remplacer CASCADE;
CREATE VIEW v_objets_a_remplacer AS
SELECT o.id,
    o.nom,
    o.categorie,
    o.statut,
    o.priorite_remplacement,
    o.prix_remplacement_estime,
    p.nom AS piece,
    p.etage
FROM objets_maison o
    JOIN pieces_maison p ON o.piece_id = p.id
WHERE o.statut IN ('a_changer', 'a_acheter', 'a_reparer')
ORDER BY CASE
        o.priorite_remplacement
        WHEN 'urgente' THEN 1
        WHEN 'haute' THEN 2
        WHEN 'normale' THEN 3
        WHEN 'basse' THEN 4
        ELSE 5
    END,
    o.prix_remplacement_estime DESC NULLS LAST;
-- Vue: Temps par activité (30 derniers jours)
DROP VIEW IF EXISTS v_temps_par_activite_30j CASCADE;
CREATE VIEW v_temps_par_activite_30j AS
SELECT type_activite,
    COUNT(*) AS nb_sessions,
    COALESCE(SUM(duree_minutes), 0) AS duree_totale_minutes,
    ROUND(AVG(duree_minutes)::numeric, 1) AS duree_moyenne_minutes,
    ROUND(AVG(difficulte)::numeric, 1) AS difficulte_moyenne,
    ROUND(AVG(satisfaction)::numeric, 1) AS satisfaction_moyenne
FROM sessions_travail
WHERE debut >= NOW() - INTERVAL '30 days'
    AND fin IS NOT NULL
GROUP BY type_activite
ORDER BY duree_totale_minutes DESC;
-- Vue: Budget travaux par pièce
DROP VIEW IF EXISTS v_budget_travaux_par_piece CASCADE;
CREATE VIEW v_budget_travaux_par_piece AS
SELECT p.id AS piece_id,
    p.nom AS piece,
    COUNT(DISTINCT v.id) AS nb_versions,
    COALESCE(SUM(c.montant), 0) AS cout_total,
    COUNT(DISTINCT c.id) AS nb_lignes_cout,
    MAX(v.date_modification) AS derniere_modif
FROM pieces_maison p
    LEFT JOIN versions_pieces v ON v.piece_id = p.id
    LEFT JOIN couts_travaux c ON c.version_id = v.id
GROUP BY p.id,
    p.nom
ORDER BY cout_total DESC;
-- Vue: Tâches du jour
-- S'appuie désormais sur `taches_entretien` (table active) au lieu de la
-- table legacy `taches_home` retirée du schéma courant.
DROP VIEW IF EXISTS v_taches_jour CASCADE;
CREATE VIEW v_taches_jour AS
SELECT
    t.id,
    'entretien'::VARCHAR(20) AS domaine,
    'entretien_planifie'::VARCHAR(50) AS type_tache,
    t.nom AS titre,
    t.description,
    COALESCE(t.duree_minutes, 15) AS duree_min,
    t.priorite,
    t.prochaine_fois AS date_due,
    t.derniere_fois AS date_faite,
    CASE
        WHEN COALESCE(t.fait, FALSE) THEN 'fait'
        ELSE 'a_faire'
    END::VARCHAR(20) AS statut,
    FALSE AS generee_auto,
    'taches_entretien'::VARCHAR(50) AS source,
    t.id AS source_id,
    NULL::INTEGER AS zone_jardin_id,
    NULL::INTEGER AS piece_id,
    t.cree_le,
    t.modifie_le,
    NULL::VARCHAR(100) AS zone_nom,
    t.piece AS piece_nom,
    CASE
        WHEN t.priorite = 'urgente' THEN 1
        WHEN t.priorite = 'haute' THEN 2
        WHEN t.priorite = 'normale' THEN 3
        WHEN t.priorite = 'basse' THEN 4
        ELSE 5
    END AS priorite_ordre
FROM taches_entretien t
WHERE COALESCE(t.fait, FALSE) = FALSE
    AND COALESCE(t.integrer_planning, TRUE) = TRUE
    AND (
        t.prochaine_fois IS NULL
        OR t.prochaine_fois <= CURRENT_DATE + 1
    )
ORDER BY priorite_ordre,
    t.prochaine_fois NULLS LAST,
    t.nom;

-- Vue: Charge semaine
DROP VIEW IF EXISTS v_charge_semaine CASCADE;
CREATE VIEW v_charge_semaine AS
SELECT d.jour,
    COALESCE(SUM(t.duree_minutes), 0) AS temps_prevu_min,
    COUNT(t.id) AS nb_taches,
    CASE
        WHEN COALESCE(SUM(t.duree_minutes), 0) > 120 THEN 'surcharge'
        WHEN COALESCE(SUM(t.duree_minutes), 0) > 90 THEN 'charge'
        WHEN COALESCE(SUM(t.duree_minutes), 0) > 60 THEN 'normal'
        ELSE 'leger'
    END AS niveau_charge
FROM (
        SELECT generate_series(
                CURRENT_DATE,
                CURRENT_DATE + INTERVAL '6 days',
                INTERVAL '1 day'
            )::DATE AS jour
    ) d
    LEFT JOIN taches_entretien t ON t.prochaine_fois = d.jour
    AND COALESCE(t.fait, FALSE) = FALSE
    AND COALESCE(t.integrer_planning, TRUE) = TRUE
GROUP BY d.jour
ORDER BY d.jour;

-- Vue: Pourcentage autonomie alimentaire
-- SQL3: v_autonomie supprimée (vue Streamlit obsolète, non utilisée par FastAPI)

-- ============================================================================


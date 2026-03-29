-- ─────────────────────────────────────────────────────────────────────────────
-- Migration V005 — Phase 2 : Consolidation SQL
-- Date : 2026-03-29
-- Réf.  : S1/SQL-1 (UUID user_id), SQL-2 (cleanup legacy), SQL-3 (CASCADE),
--          SQL-4 (index manquants), SQL-5 (docs vues), SQL-6 (CHECK enums)
-- ─────────────────────────────────────────────────────────────────────────────

-- ===========================================================================
-- 2.1 — SQL-1 : Standardiser user_id
-- ===========================================================================
-- logs_securite.user_id : VARCHAR(255) → TEXT
-- (stocke un UUID Supabase auth sous forme texte — TEXT est plus idiomatique
--  que VARCHAR(255) et n'introduit pas de limite arbitraire)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'logs_securite'
          AND column_name = 'user_id'
          AND data_type = 'character varying'
    ) THEN
        ALTER TABLE logs_securite ALTER COLUMN user_id TYPE TEXT;
        COMMENT ON COLUMN logs_securite.user_id IS
            'UUID Supabase Auth (auth.uid()) au format texte. '
            'Peut être NULL pour les événements système.';
    END IF;
END $$;

-- Note : les colonnes user_id INTEGER dans garmin_tokens, activites_garmin, etc.
-- sont des FK vers profils_utilisateurs(id) SERIAL — intentionnellement entiers.
-- Elles ne doivent PAS être converties en UUID.
-- Convention documentation pour ces FK :
COMMENT ON COLUMN garmin_tokens.user_id IS
    'FK → profils_utilisateurs(id) INTEGER. Intentionnellement entier.';

COMMENT ON COLUMN activites_garmin.user_id IS
    'FK → profils_utilisateurs(id) INTEGER. Intentionnellement entier.';

-- ===========================================================================
-- 2.2 — SQL-2 : Nettoyage table legacy liste_courses
-- ===========================================================================
-- La table legacy 'liste_courses' est déjà supprimée dans INIT_COMPLET via
-- 'DROP TABLE IF EXISTS liste_courses CASCADE' (ligne 55).
-- Si elle existe encore dans un schéma déployé avant INIT_COMPLET, on la supprime.
DROP TABLE IF EXISTS liste_courses CASCADE;

-- Index du doublon identifié dans repas :
DROP INDEX IF EXISTS idx_repas_planning_id;
-- (doublon de ix_repas_planning sur repas(planning_id))

-- Index du doublon identifié dans historique_inventaire :
DROP INDEX IF EXISTS idx_historique_inventaire_article_id;
-- (doublon de ix_historique_inventaire_article sur historique_inventaire(article_id))

-- ===========================================================================
-- 2.3 — SQL-3 : Convention CASCADE documentée
-- ===========================================================================
-- Convention appliquée dans ce schéma :
-- • ON DELETE CASCADE     → enfants forts (ingrédients d'une recette, étapes,
--                           articles d'une liste, repas d'un planning)
-- • ON DELETE SET NULL    → références faibles (recette supprimée ≠ repas supprimé)
-- • ON DELETE RESTRICT    → entités parentes protégées (utilisateur ne peut pas
--                           être supprimé si des données enfants existent)
--
-- Les FK existantes respectent déjà globalement cette convention.
-- On ajoute des commentaires pour les cas ambigus :
COMMENT ON CONSTRAINT fk_repas_recette ON repas IS
    'SET NULL intentionnel : la suppression d''une recette ne supprime pas le repas planifié.';

COMMENT ON CONSTRAINT fk_batch_meals_recette ON repas_batch IS
    'SET NULL intentionnel : la suppression d''une recette ne supprime pas le batch.';

-- ===========================================================================
-- 2.4 — SQL-4 : Index composites manquants
-- ===========================================================================

-- repas(planning_id, date_repas) — requête principale : semaine d'un planning
CREATE INDEX IF NOT EXISTS ix_repas_planning_date
    ON repas(planning_id, date_repas);

-- repas(planning_id, type_repas) — filtrage par type de repas dans un planning
CREATE INDEX IF NOT EXISTS ix_repas_planning_type
    ON repas(planning_id, type_repas);

-- articles_courses(liste_id, achete) — articles restants à acheter dans une liste
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_achete
    ON articles_courses(liste_id, achete);

-- articles_courses(liste_id, priorite) — tri par priorité dans une liste
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_priorite
    ON articles_courses(liste_id, priorite);

-- inventaire(date_peremption, quantite) — alertes péremption avec stock non nul
CREATE INDEX IF NOT EXISTS ix_inventaire_peremption_quantite
    ON inventaire(date_peremption, quantite)
    WHERE date_peremption IS NOT NULL;

-- historique_inventaire(ingredient_id, date_modification) — historique d'un ingrédient
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_ingredient_date
    ON historique_inventaire(ingredient_id, date_modification);

-- listes_courses(statut, semaine_du) — listes actives par semaine
CREATE INDEX IF NOT EXISTS ix_listes_courses_statut_semaine
    ON listes_courses(statut, semaine_du);

-- plannings(actif, semaine_debut) — planning actif de la semaine courante
CREATE INDEX IF NOT EXISTS ix_plannings_actif_semaine
    ON plannings(actif, semaine_debut)
    WHERE actif = TRUE;

-- ===========================================================================
-- 2.6 — SQL-6 : Contraintes CHECK pour les enums VARCHAR clés
-- ===========================================================================

-- repas.type_repas (valeurs issues du modèle Pydantic TypeRepas)
ALTER TABLE repas
    ADD CONSTRAINT IF NOT EXISTS ck_repas_type_repas
    CHECK (type_repas IN (
        'petit_dejeuner', 'brunch', 'dejeuner', 'gouter', 'diner',
        'collation', 'autre'
    ));

-- listes_courses.statut
ALTER TABLE listes_courses
    ADD CONSTRAINT IF NOT EXISTS ck_listes_courses_statut
    CHECK (statut IN ('active', 'en_cours', 'completee', 'archivee', 'annulee'));

-- recettes.difficulte
ALTER TABLE recettes
    ADD CONSTRAINT IF NOT EXISTS ck_recettes_difficulte
    CHECK (difficulte IN ('facile', 'moyen', 'difficile', 'expert'));

-- recettes.saison
ALTER TABLE recettes
    ADD CONSTRAINT IF NOT EXISTS ck_recettes_saison
    CHECK (saison IN ('printemps', 'ete', 'automne', 'hiver', 'toute_annee', 'toute_année'));

-- articles_courses.priorite
ALTER TABLE articles_courses
    ADD CONSTRAINT IF NOT EXISTS ck_articles_courses_priorite
    CHECK (priorite IN ('haute', 'moyenne', 'basse', 'urgente'));

-- articles_modeles.priorite
ALTER TABLE articles_modeles
    ADD CONSTRAINT IF NOT EXISTS ck_articles_modeles_priorite
    CHECK (priorite IN ('haute', 'moyenne', 'basse', 'urgente'));

-- sessions_batch_cooking.statut  (si la table existe)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sessions_batch_cooking') THEN
        ALTER TABLE sessions_batch_cooking
            ADD CONSTRAINT IF NOT EXISTS ck_batch_statut
            CHECK (statut IN ('planifie', 'en_cours', 'termine', 'annule', 'pause'));
    END IF;
END $$;

-- repas_batch (préparations batch) — pas de colonne statut, intentionnel

-- ===========================================================================
-- 2.5 — SQL-5 : Documentation des vues SQL
-- ===========================================================================

COMMENT ON VIEW v_objets_a_remplacer IS
    'Objets de la maison ayant le statut a_changer, a_acheter ou a_reparer, '
    'ordonnés par priorité de remplacement puis par coût estimé décroissant. '
    'Utilisée par : GET /api/v1/maison/suggestions-renouvellement';

COMMENT ON VIEW v_temps_par_activite_30j IS
    'Agrégation des sessions de travail des 30 derniers jours, groupées par '
    'type d''activité. Retourne durée totale, durée moyenne, difficulté et '
    'satisfaction moyennes. '
    'Utilisée par : services/maison/stats';

COMMENT ON VIEW v_budget_travaux_par_piece IS
    'Budget cumulé des travaux par pièce maison, calculé depuis les versions_pieces '
    'et les couts_travaux. Ordonnée par coût total décroissant. '
    'Utilisée par : GET /api/v1/maison/maison-finances/budget-pieces';

COMMENT ON VIEW v_taches_jour IS
    'Tâches home (taches_home) à faire ou en cours avec date_due <= demain, '
    'jointurées avec zones_jardin et pieces_maison. Ordonnées par priorité. '
    'Utilisée par : GET /api/v1/maison/briefing → BriefingMaison';

COMMENT ON VIEW v_charge_semaine IS
    'Charge quotidienne estimée pour les 7 prochains jours, basée sur les '
    'taches_home planifiées. Niveaux : leger / normal / charge / surcharge. '
    'Utilisée par : GET /api/v1/maison/hub/stats';

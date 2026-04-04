-- PARTIE 6 : TRIGGERS (modifie_le)
-- ============================================================================
-- Tables avec colonne modifie_le
DO $$
DECLARE t TEXT;
tables_modifie_le TEXT [] := ARRAY [
        'profils_utilisateurs', 'garmin_tokens', 'recettes', 'activites_weekend',
        'achats_famille', 'jeux_equipes', 'jeux_matchs', 'config_batch_cooking',
        'sessions_batch_cooking', 'preparations_batch', 'batch_cooking_congelation',
        'plannings',
    'modeles_courses', 'templates_semaine', 'points_utilisateurs', 'automations',
        'contacts_famille', 'anniversaires_famille', 'evenements_familiaux',
        'voyages', 'checklists_voyage', 'documents_famille',
        -- Maison extensions
        'artisans', 'interventions_artisans',
        'articles_cellier', 'diagnostics_maison',
        'estimations_immobilieres', 'checklists_vacances', 'items_checklist',
        'traitements_nuisibles', 'devis_comparatifs', 'entretiens_saisonniers',
        -- Utilitaires
        'notes_memos', 'journal_bord', 'contacts_utiles', 'liens_favoris',
        'mots_de_passe_maison', 'releves_energie', 'minuteur_sessions',
        -- Notifications
        'historique_notifications',
        -- Tables anciennement updated_at (colonnes renommées modifie_le)
        'listes_courses', 'meubles', 'taches_entretien', 'stocks_maison',
        'preferences_utilisateurs', 'depenses', 'budgets_mensuels', 'config_meteo',
        'calendriers_externes', 'preferences_notifications',
        'configs_calendriers_externes', 'evenements_calendrier',
        'plans_jardin', 'zones_jardin', 'plantes_jardin',
        'pieces_maison', 'objets_maison',
        'preferences_home', 'objectifs_autonomie',
        'abonnements', 'budgets_home'
    ];
BEGIN FOREACH t IN ARRAY tables_modifie_le LOOP EXECUTE format(
    'DROP TRIGGER IF EXISTS trigger_update_modifie_le ON %I',
    t
);
EXECUTE format(
    '
            CREATE TRIGGER trigger_update_modifie_le
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_modifie_le_column()
        ',
    t
);
END LOOP;
END $$;

-- ============================================================================
-- Trigger : mise à jour listes_courses.modifie_le via articles_courses
-- (V005 absorbé)
-- ============================================================================
CREATE OR REPLACE FUNCTION update_liste_courses_modifie_le()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE listes_courses
    SET modifie_le = NOW()
    WHERE id = COALESCE(NEW.liste_id, OLD.liste_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_articles_courses_update_liste ON articles_courses;
CREATE TRIGGER trg_articles_courses_update_liste
    AFTER INSERT OR UPDATE OR DELETE ON articles_courses
    FOR EACH ROW EXECUTE FUNCTION update_liste_courses_modifie_le();

-- ============================================================================
-- Trigger : invalidation cache planning via repas_planning
-- (V005 absorbé)
-- ============================================================================
CREATE OR REPLACE FUNCTION notify_planning_changed()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id TEXT;
BEGIN
    SELECT p.cree_par INTO v_user_id
    FROM plannings p
    WHERE p.id = COALESCE(NEW.planning_id, OLD.planning_id)
    LIMIT 1;
    PERFORM pg_notify('planning_changed', COALESCE(v_user_id, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_repas_planning_notify ON repas_planning;
CREATE TRIGGER trg_repas_planning_notify
    AFTER INSERT OR UPDATE OR DELETE ON repas_planning
    FOR EACH ROW EXECUTE FUNCTION notify_planning_changed();
-- ============================================================================

-- Source: 13_views.sql

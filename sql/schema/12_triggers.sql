-- PARTIE 6 : TRIGGERS (modifie_le)
-- ============================================================================
-- Tables avec colonne modifie_le
DO $$
DECLARE t TEXT;
tables_modifie_le TEXT [] := ARRAY [
        'profils_utilisateurs', 'garmin_tokens', 'recettes', 'activites_weekend',
        'achats_famille', 'jeux_equipes', 'jeux_matchs', 'config_batch_cooking',
        'sessions_batch_cooking', 'preparations_batch', 'plannings',
    'modeles_courses', 'templates_semaine', 'points_utilisateurs', 'automations',
        'contacts_famille', 'anniversaires_famille', 'evenements_familiaux',
        'voyages', 'checklists_voyage', 'documents_famille',
        -- Maison extensions
        'contrats_maison', 'artisans', 'interventions_artisans', 'garanties',
        'incidents_sav', 'articles_cellier', 'diagnostics_maison',
        'estimations_immobilieres', 'checklists_vacances', 'items_checklist',
        'traitements_nuisibles', 'devis_comparatifs', 'entretiens_saisonniers',
        -- Utilitaires
        'notes_memos', 'journal_bord', 'contacts_utiles', 'liens_favoris',
        'mots_de_passe_maison', 'releves_energie',
        -- Tables anciennement updated_at (colonnes renommées modifie_le)
        'listes_courses', 'meubles', 'taches_entretien', 'stocks_maison',
        'preferences_utilisateurs', 'depenses', 'budgets_mensuels', 'config_meteo',
        'calendriers_externes', 'preferences_notifications',
        'configs_calendriers_externes', 'evenements_calendrier',
        'plans_jardin', 'zones_jardin', 'plantes_jardin',
        'pieces_maison', 'objets_maison',
        'preferences_home', 'taches_home', 'objectifs_autonomie',
        'contrats', 'budgets_home'
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

-- PARTIE 10 : DONNÉES DE RÉFÉRENCE
-- ============================================================================
-- Profils utilisateurs par défaut (Anne & Mathieu)
INSERT INTO profils_utilisateurs (
        username,
        display_name,
        avatar_emoji,
        objectif_pas_quotidien,
        objectif_calories_brulees,
        objectif_minutes_actives,
        garmin_connected,
        theme_prefere,
        preferences_modules,
        cree_le,
        modifie_le
    )
VALUES (
        'anne',
        'Anne',
        '👩',
        10000,
        500,
        30,
        FALSE,
        'auto',
        '{
        "cuisine": {"nb_suggestions_ia": 5, "types_cuisine_preferes": [], "duree_max_batch_min": 120},
        "famille": {"activites_favorites_jules": [], "frequence_rappels_routines": "quotidien"},
        "maison": {"seuil_alerte_entretien_jours": 7},
        "planning": {"horizon_defaut": "semaine"},
        "budget": {"seuils_alerte_pct": 80}
    }'::jsonb,
        NOW(),
        NOW()
    ) ON CONFLICT (username) DO NOTHING;
INSERT INTO profils_utilisateurs (
        username,
        display_name,
        avatar_emoji,
        objectif_pas_quotidien,
        objectif_calories_brulees,
        objectif_minutes_actives,
        garmin_connected,
        theme_prefere,
        preferences_modules,
        cree_le,
        modifie_le
    )
VALUES (
        'mathieu',
        'Mathieu',
        '👨',
        10000,
        500,
        30,
        FALSE,
        'auto',
        '{
        "cuisine": {"nb_suggestions_ia": 5, "types_cuisine_preferes": [], "duree_max_batch_min": 120},
        "famille": {"activites_favorites_jules": [], "frequence_rappels_routines": "quotidien"},
        "maison": {"seuil_alerte_entretien_jours": 7},
        "planning": {"horizon_defaut": "semaine"},
        "budget": {"seuils_alerte_pct": 80}
    }'::jsonb,
        NOW(),
        NOW()
    ) ON CONFLICT (username) DO NOTHING;
-- Configuration jeux par défaut
INSERT INTO jeux_configuration (cle, valeur, description)
VALUES (
        'seuil_value_alerte',
        '2.0',
        'Seuil de value minimum pour créer une alerte'
    ),
    (
        'seuil_value_haute',
        '2.5',
        'Seuil de value pour opportunité haute'
    ),
    (
        'seuil_series_minimum',
        '3',
        'Série minimum significative'
    ),
    (
        'sync_paris_interval_hours',
        '6',
        'Intervalle sync paris en heures'
    ),
    (
        'sync_loto_days',
        'mon,wed,sat',
        'Jours de sync loto'
    ),
    ('sync_loto_hour', '21:30', 'Heure de sync loto') ON CONFLICT (cle) DO NOTHING;
-- Préférences maison par défaut
INSERT INTO preferences_home (id, max_taches_jour, max_heures_jour)
VALUES (1, 3, 2.0) ON CONFLICT (id) DO NOTHING;
-- Budgets maison par défaut
INSERT INTO budgets_home (categorie, montant_mensuel, alerte_pourcent)
VALUES ('jardin', 100.00, 80),
    ('entretien', 50.00, 80),
    ('energie', 200.00, 90),
    ('travaux', 150.00, 80),
    ('equipement', 100.00, 80),
    ('decoration', 50.00, 80),
    ('assurance', 150.00, 95),
    ('autre', 50.00, 80) ON CONFLICT (categorie) DO NOTHING;
-- Objectifs autonomie alimentaire
INSERT INTO objectifs_autonomie (legume, besoin_kg_an, surface_ideale_m2)
VALUES ('Tomate', 40.00, 8.00),
    ('Courgette', 25.00, 6.00),
    ('Haricot vert', 15.00, 5.00),
    ('Pomme de terre', 80.00, 20.00),
    ('Carotte', 20.00, 4.00),
    ('Salade', 30.00, 3.00),
    ('Poireau', 15.00, 3.00),
    ('Oignon', 10.00, 2.00),
    ('Ail', 3.00, 1.00),
    ('Fraise', 10.00, 4.00) ON CONFLICT (legume) DO NOTHING;
-- Entretiens saisonniers prédéfinis
INSERT INTO entretiens_saisonniers (
        nom,
        description,
        categorie,
        saison,
        mois_recommande,
        mois_rappel,
        frequence,
        professionnel_requis,
        obligatoire,
        cout_estime,
        duree_minutes
    )
VALUES -- AUTOMNE
    (
        'Entretien chaudière',
        'Visite annuelle obligatoire de la chaudière gaz/fioul',
        'chauffage',
        'automne',
        9,
        8,
        'annuel',
        TRUE,
        TRUE,
        150.00,
        60
    ),
    (
        'Ramonage cheminée',
        'Ramonage obligatoire des conduits de fumée (1 à 2 fois/an)',
        'chauffage',
        'automne',
        10,
        9,
        'annuel',
        TRUE,
        TRUE,
        80.00,
        45
    ),
    (
        'Purge des radiateurs',
        'Purger les radiateurs avant mise en route du chauffage',
        'chauffage',
        'automne',
        10,
        9,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Nettoyage gouttières',
        'Retirer les feuilles mortes des gouttières',
        'toiture',
        'automne',
        11,
        10,
        'semestriel',
        FALSE,
        FALSE,
        0.00,
        60
    ),
    (
        'Vérification toiture',
        'Contrôle visuel tuiles/ardoises, étanchéité',
        'toiture',
        'automne',
        10,
        9,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Isolation fenêtres',
        'Vérifier joints fenêtres, calfeutrage si nécessaire',
        'isolation',
        'automne',
        10,
        9,
        'annuel',
        FALSE,
        FALSE,
        20.00,
        60
    ),
    (
        'Rentrer plantes fragiles',
        'Mettre à l''abri les plantes gélives',
        'jardin',
        'automne',
        10,
        9,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Préparer la tondeuse (hivernage)',
        'Vidanger, nettoyer, ranger la tondeuse pour l''hiver',
        'jardin',
        'automne',
        11,
        10,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        45
    ),
    -- HIVER
    (
        'Vérification détecteurs fumée',
        'Tester les détecteurs, changer les piles si besoin',
        'securite',
        'hiver',
        1,
        12,
        'semestriel',
        FALSE,
        TRUE,
        10.00,
        15
    ),
    (
        'Contrôle VMC',
        'Nettoyage bouches VMC et vérification fonctionnement',
        'ventilation',
        'hiver',
        1,
        12,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Couper eau extérieure',
        'Fermer les robinets extérieurs et purger pour éviter le gel',
        'plomberie',
        'hiver',
        12,
        11,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        15
    ),
    (
        'Vérifier isolation combles',
        'Contrôle visuel isolation toiture/combles',
        'isolation',
        'hiver',
        1,
        12,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    -- PRINTEMPS
    (
        'Entretien climatisation',
        'Nettoyage filtres et vérification avant été',
        'climatisation',
        'printemps',
        4,
        3,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Nettoyage terrasse',
        'Nettoyage haute pression terrasse, dalles, mobilier',
        'exterieur',
        'printemps',
        4,
        3,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        120
    ),
    (
        'Révision tondeuse',
        'Remise en service tondeuse, affûtage lame, huile',
        'jardin',
        'printemps',
        3,
        2,
        'annuel',
        FALSE,
        FALSE,
        15.00,
        30
    ),
    (
        'Vernissage/traitement bois extérieur',
        'Traitement mobilier jardin, clôtures, portail bois',
        'exterieur',
        'printemps',
        4,
        3,
        'annuel',
        FALSE,
        FALSE,
        50.00,
        180
    ),
    (
        'Vérification étanchéité toiture',
        'Post-hiver: contrôle fuites après gel/neige',
        'toiture',
        'printemps',
        3,
        2,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Nettoyage gouttières (printemps)',
        'Second nettoyage annuel des gouttières',
        'toiture',
        'printemps',
        4,
        3,
        'semestriel',
        FALSE,
        FALSE,
        0.00,
        60
    ),
    (
        'Traitement anti-mousse toiture',
        'Application produit anti-mousse sur tuiles',
        'toiture',
        'printemps',
        4,
        3,
        'annuel',
        FALSE,
        FALSE,
        40.00,
        120
    ),
    (
        'Remettre eau extérieure',
        'Réouvrir robinets extérieurs après risque gel',
        'plomberie',
        'printemps',
        3,
        2,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        10
    ),
    -- ÉTÉ
    (
        'Entretien portail automatique',
        'Graissage, vérification cellules, télécommandes',
        'exterieur',
        'ete',
        6,
        5,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        30
    ),
    (
        'Contrôle extincteurs',
        'Vérification pression, date péremption',
        'securite',
        'ete',
        6,
        5,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        15
    ),
    (
        'Traitement bois charpente',
        'Traitement préventif anti-insectes xylophages',
        'toiture',
        'ete',
        7,
        6,
        'annuel',
        TRUE,
        FALSE,
        200.00,
        240
    ),
    (
        'Vérification tableau électrique',
        'Contrôle visuel disjoncteurs, test différentiel',
        'electricite',
        'ete',
        6,
        5,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        20
    ),
    (
        'Nettoyage chauffe-eau',
        'Vidange partielle et détartrage',
        'plomberie',
        'ete',
        7,
        6,
        'annuel',
        FALSE,
        FALSE,
        0.00,
        45
    ),
    -- TOUTE L'ANNÉE
    (
        'Relevé compteurs eau',
        'Relevé index compteurs pour suivi consommation',
        'plomberie',
        'toute_annee',
        NULL,
        NULL,
        'trimestriel',
        FALSE,
        FALSE,
        0.00,
        5
    ),
    (
        'Test alarme',
        'Tester le système d''alarme et changer piles détecteurs',
        'securite',
        'toute_annee',
        NULL,
        NULL,
        'trimestriel',
        FALSE,
        FALSE,
        0.00,
        15
    ),
    (
        'Contrôle pression chaudière',
        'Vérifier entre 1 et 1.5 bar',
        'chauffage',
        'toute_annee',
        NULL,
        NULL,
        'trimestriel',
        FALSE,
        FALSE,
        0.00,
        5
    ),
    (
        'Nettoyage filtres aspirateur',
        'Nettoyer/remplacer les filtres',
        'menage',
        'toute_annee',
        NULL,
        NULL,
        'trimestriel',
        FALSE,
        FALSE,
        10.00,
        15
    ),
    (
        'Vérification joints salle de bain',
        'Contrôle moisissures, étanchéité joints silicone',
        'plomberie',
        'toute_annee',
        NULL,
        NULL,
        'semestriel',
        FALSE,
        FALSE,
        15.00,
        20
    ) ON CONFLICT DO NOTHING;
-- Préférences de notification par défaut
INSERT INTO preferences_notifications (
        courses_rappel,
        repas_suggestion,
        stock_alerte,
        meteo_alerte,
        budget_alerte,
        quiet_hours_start,
        quiet_hours_end,
        modules_actifs,
        canal_prefere,
        cree_le,
        modifie_le
    )
VALUES (
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        '22:00',
        '07:00',
        '{
        "cuisine": {"suggestions_repas": true, "stock_bas": true, "batch_cooking": false},
        "famille": {"routines_jules": true, "activites_weekend": true, "achats_planifier": false},
        "maison": {"entretien_programme": true, "charges_payer": true, "jardin_arrosage": false},
        "planning": {"rappels_evenements": true, "taches_retard": true},
        "budget": {"depassement_seuil": true, "resume_mensuel": false}
    }'::jsonb,
        'push',
        NOW(),
        NOW()
    ) ON CONFLICT DO NOTHING;
-- Grants Supabase
GRANT SELECT,
    INSERT,
    UPDATE,
    DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE,
    SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
-- ============================================================================

-- Source: 17_migrations_absorbees.sql
-- ============================================================================
-- ASSISTANT MATANNE — Migrations absorbees (SQL-first)
-- ============================================================================
-- Objectif: conserver un script idempotent pour aligner les schemas existants
-- avec les conventions actuelles quand les colonnes ont evolue.
-- ============================================================================

-- Phase 5: workflow validation v2 (planning + courses)

-- Plannings: ajoute `etat` si absent, puis migre depuis `actif` si present.
ALTER TABLE plannings
    ADD COLUMN IF NOT EXISTS etat VARCHAR(20) NOT NULL DEFAULT 'brouillon';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'plannings' AND column_name = 'actif'
    ) THEN
        UPDATE plannings
        SET etat = CASE
            WHEN actif IS TRUE THEN 'valide'
            ELSE 'archive'
        END
        WHERE etat = 'brouillon';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_plannings_etat ON plannings(etat);

-- Listes de courses: ajoute `etat` et `archivee`, puis migre depuis `statut` si present.
ALTER TABLE listes_courses
    ADD COLUMN IF NOT EXISTS etat VARCHAR(20) NOT NULL DEFAULT 'brouillon';

ALTER TABLE listes_courses
    ADD COLUMN IF NOT EXISTS archivee BOOLEAN NOT NULL DEFAULT FALSE;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'listes_courses' AND column_name = 'statut'
    ) THEN
        UPDATE listes_courses
        SET etat = CASE
            WHEN statut IN ('active', 'en_cours') THEN 'active'
            WHEN statut IN ('completee', 'archivee') THEN 'terminee'
            ELSE 'brouillon'
        END
        WHERE etat = 'brouillon';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_listes_courses_etat ON listes_courses(etat);
CREATE INDEX IF NOT EXISTS ix_listes_courses_archivee ON listes_courses(archivee);

-- Source: 99_footer.sql
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

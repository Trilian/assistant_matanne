-- ============================================================================
-- ASSISTANT MATANNE — Tables Cuisine
-- ============================================================================
-- Contient : ingredients, recettes, inventaire, listes_courses, plannings,
--            modeles_courses, templates_semaine, batch_cooking, ...
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100) NOT NULL DEFAULT 'Autre',
    unite VARCHAR(50) NOT NULL DEFAULT 'pièce',
    calories_pour_100g FLOAT,
    saison VARCHAR(50),
    allergene BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ingredients_nom ON ingredients(nom);
CREATE INDEX IF NOT EXISTS ix_ingredients_categorie ON ingredients(categorie);
CREATE INDEX IF NOT EXISTS ix_ingredients_saison ON ingredients(saison);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recettes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    -- Temps & Portions
    temps_preparation INTEGER NOT NULL DEFAULT 0,
    temps_cuisson INTEGER NOT NULL DEFAULT 0,
    portions INTEGER NOT NULL DEFAULT 4,
    difficulte VARCHAR(50) NOT NULL DEFAULT 'moyen',
    -- Catégorisation
    type_repas VARCHAR(50) NOT NULL DEFAULT 'diner',
    saison VARCHAR(50) NOT NULL DEFAULT 'toute_année',
    categorie VARCHAR(100) NOT NULL DEFAULT 'Plat',
    -- Flags - Tags système
    est_rapide BOOLEAN NOT NULL DEFAULT FALSE,
    est_equilibre BOOLEAN NOT NULL DEFAULT FALSE,
    est_vegetarien BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_bebe BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_batch BOOLEAN NOT NULL DEFAULT FALSE,
    congelable BOOLEAN NOT NULL DEFAULT FALSE,
    -- Types de protéines
    type_proteines VARCHAR(100),
    -- Catégorie nutritionnelle (pour équilibre assiette PNNS)
    -- Valeurs : proteines_poisson | proteines_viande_rouge | proteines_volaille |
    --           proteines_oeuf | proteines_legumineuses | feculents | legumes_principaux | mixte
    categorie_nutritionnelle VARCHAR(50),
    -- Bio & Local
    est_bio BOOLEAN NOT NULL DEFAULT FALSE,
    est_local BOOLEAN NOT NULL DEFAULT FALSE,
    score_bio INTEGER NOT NULL DEFAULT 0,
    score_local INTEGER NOT NULL DEFAULT 0,
    -- Robots compatibles
    compatible_cookeo BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_monsieur_cuisine BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_airfryer BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_multicooker BOOLEAN NOT NULL DEFAULT FALSE,
    -- Instructions robots
    instructions_cookeo TEXT,
    instructions_monsieur_cuisine TEXT,
    instructions_airfryer TEXT,
    -- Nutrition
    calories INTEGER,
    proteines FLOAT,
    lipides FLOAT,
    glucides FLOAT,
    -- IA
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    score_ia FLOAT,
    -- Media
    url_image VARCHAR(500),
    url_source VARCHAR(500),
    -- Timestamps
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_temps_preparation_positif CHECK (temps_preparation >= 0),
    CONSTRAINT ck_temps_cuisson_positif CHECK (temps_cuisson >= 0),
    CONSTRAINT ck_portions_positive CHECK (portions > 0)
);
CREATE INDEX IF NOT EXISTS ix_recettes_nom ON recettes(nom);
CREATE INDEX IF NOT EXISTS ix_recettes_type_repas ON recettes(type_repas);
CREATE INDEX IF NOT EXISTS ix_recettes_saison ON recettes(saison);
CREATE INDEX IF NOT EXISTS ix_recettes_categorie ON recettes(categorie);
CREATE INDEX IF NOT EXISTS ix_recettes_est_rapide ON recettes(est_rapide);
CREATE INDEX IF NOT EXISTS ix_recettes_est_vegetarien ON recettes(est_vegetarien);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_bebe ON recettes(compatible_bebe);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_batch ON recettes(compatible_batch);
CREATE INDEX IF NOT EXISTS ix_recettes_est_bio ON recettes(est_bio);
CREATE INDEX IF NOT EXISTS ix_recettes_est_local ON recettes(est_local);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_cookeo ON recettes(compatible_cookeo);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_monsieur_cuisine ON recettes(compatible_monsieur_cuisine);
CREATE INDEX IF NOT EXISTS ix_recettes_compatible_airfryer ON recettes(compatible_airfryer);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plannings (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    semaine_debut DATE NOT NULL,
    semaine_fin DATE NOT NULL,
    etat VARCHAR(20) NOT NULL DEFAULT 'brouillon',
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_plannings_semaine_debut ON plannings(semaine_debut);
CREATE INDEX IF NOT EXISTS ix_plannings_etat ON plannings(etat);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS listes_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    etat VARCHAR(20) NOT NULL DEFAULT 'brouillon',
    archivee BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_listes_courses_etat ON listes_courses(etat);
CREATE INDEX IF NOT EXISTS ix_listes_courses_archivee ON listes_courses(archivee);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS modeles_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    utilisateur_id VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    articles_data JSONB
);
CREATE INDEX IF NOT EXISTS ix_modeles_courses_nom ON modeles_courses(nom);
CREATE INDEX IF NOT EXISTS ix_modeles_courses_utilisateur_id ON modeles_courses(utilisateur_id);
CREATE INDEX IF NOT EXISTS ix_modeles_courses_actif ON modeles_courses(actif);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS templates_semaine (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS config_batch_cooking (
    id SERIAL PRIMARY KEY,
    jours_batch JSONB NOT NULL DEFAULT '[6]',
    heure_debut_preferee TIME DEFAULT '10:00',
    duree_max_session INTEGER NOT NULL DEFAULT 180,
    avec_jules_par_defaut BOOLEAN NOT NULL DEFAULT TRUE,
    robots_disponibles JSONB NOT NULL DEFAULT '["four", "plaques"]',
    preferences_stockage JSONB,
    -- Mapping jour_batch → jours couverts, ex: {"2": [2, 3, 4], "6": [6, 0, 1, 2]}
    couverture_jours JSONB,
    objectif_portions_semaine INTEGER NOT NULL DEFAULT 20,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_config_batch_duree_positive CHECK (duree_max_session > 0),
    CONSTRAINT ck_config_batch_objectif_positif CHECK (objectif_portions_semaine > 0)
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recette_ingredients (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantite FLOAT NOT NULL,
    unite VARCHAR(50) NOT NULL,
    optionnel BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_recette_ing_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT fk_recette_ing_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_positive CHECK (quantite > 0),
    CONSTRAINT uq_recette_ingredient UNIQUE (recette_id, ingredient_id)
);
CREATE INDEX IF NOT EXISTS ix_recette_ingredients_recette ON recette_ingredients(recette_id);
CREATE INDEX IF NOT EXISTS ix_recette_ingredients_ingredient ON recette_ingredients(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_recette_ingredients_ingredient_id ON recette_ingredients(ingredient_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS etapes_recette (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    ordre INTEGER NOT NULL,
    titre VARCHAR(200),
    description TEXT NOT NULL,
    duree INTEGER,
    robots_optionnels JSONB,
    temperature INTEGER,
    est_supervision BOOLEAN DEFAULT FALSE,
    groupe_parallele INTEGER DEFAULT 0,
    CONSTRAINT fk_etapes_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_ordre_positif CHECK (ordre > 0)
);
CREATE INDEX IF NOT EXISTS ix_etapes_recette_recette ON etapes_recette(recette_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS versions_recette (
    id SERIAL PRIMARY KEY,
    recette_base_id INTEGER NOT NULL,
    type_version VARCHAR(50) NOT NULL,
    instructions_modifiees TEXT,
    ingredients_modifies JSONB,
    notes_bebe TEXT,
    etapes_paralleles_batch JSONB,
    temps_optimise_batch INTEGER,
    modifications_resume JSONB NOT NULL DEFAULT '[]'::jsonb,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_versions_recette FOREIGN KEY (recette_base_id) REFERENCES recettes(id) ON DELETE CASCADE
);
COMMENT ON COLUMN versions_recette.modifications_resume IS 'Résumé des modifications apportées (liste de chaînes), ex: ["sans sel", "champignons mixés"]';
CREATE INDEX IF NOT EXISTS ix_versions_recette_base ON versions_recette(recette_base_id);
CREATE INDEX IF NOT EXISTS ix_versions_recette_type ON versions_recette(type_version);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historique_recettes (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    date_preparation DATE NOT NULL,
    portions_cuisinees INTEGER NOT NULL DEFAULT 1,
    note INTEGER,
    avis TEXT,
    feedback VARCHAR(20) DEFAULT 'neutral',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_historique_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_note_valide CHECK (
        note IS NULL
        OR (
            note >= 0
            AND note <= 5
        )
    ),
    CONSTRAINT ck_portions_cuisinees_positive CHECK (portions_cuisinees > 0)
);
CREATE INDEX IF NOT EXISTS ix_historique_recettes_recette ON historique_recettes(recette_id);
CREATE INDEX IF NOT EXISTS ix_historique_recettes_date ON historique_recettes(date_preparation);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS repas_batch (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions_creees INTEGER NOT NULL DEFAULT 4,
    portions_restantes INTEGER NOT NULL DEFAULT 4,
    date_preparation DATE NOT NULL,
    date_peremption DATE NOT NULL,
    container_type VARCHAR(100),
    localisation VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_batch_meals_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS ix_batch_meals_recette ON repas_batch(recette_id);
CREATE INDEX IF NOT EXISTS ix_batch_meals_date_prep ON repas_batch(date_preparation);
CREATE INDEX IF NOT EXISTS ix_batch_meals_date_peremption ON repas_batch(date_peremption);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS retours_recettes (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    recette_id INTEGER NOT NULL,
    feedback VARCHAR(20) NOT NULL DEFAULT 'neutral',
    contexte VARCHAR(200),
    notes TEXT,
    planifie_cette_semaine BOOLEAN NOT NULL DEFAULT FALSE,
    date_planifie TIMESTAMP WITH TIME ZONE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_recipe_feedbacks_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_feedback_type CHECK (feedback IN ('like', 'dislike', 'neutral'))
);
CREATE INDEX IF NOT EXISTS ix_recipe_feedbacks_user ON retours_recettes(user_id);
CREATE INDEX IF NOT EXISTS ix_recipe_feedbacks_recette ON retours_recettes(recette_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_recipe_feedback ON retours_recettes(user_id, recette_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventaire (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 0.0,
    quantite_min FLOAT NOT NULL DEFAULT 1.0,
    emplacement VARCHAR(100),
    date_peremption DATE,
    date_entree DATE NOT NULL DEFAULT CURRENT_DATE,
    derniere_maj TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    photo_url VARCHAR(500),
    photo_filename VARCHAR(200),
    photo_uploaded_at TIMESTAMP WITH TIME ZONE,
    code_barres VARCHAR(50),
    prix_unitaire FLOAT,
    CONSTRAINT fk_inventaire_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_inventaire_positive CHECK (quantite >= 0),
    CONSTRAINT ck_seuil_positif CHECK (quantite_min >= 0)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_inventaire_ingredient ON inventaire(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_inventaire_ingredient ON inventaire(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_inventaire_emplacement ON inventaire(emplacement);
CREATE INDEX IF NOT EXISTS ix_inventaire_peremption ON inventaire(date_peremption);
CREATE INDEX IF NOT EXISTS ix_inventaire_derniere_maj ON inventaire(derniere_maj);
CREATE UNIQUE INDEX IF NOT EXISTS uq_code_barres ON inventaire(code_barres);
CREATE INDEX IF NOT EXISTS ix_inventaire_code_barres ON inventaire(code_barres);
CREATE INDEX IF NOT EXISTS ix_inventaire_date_entree ON inventaire(date_entree);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historique_inventaire (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    type_modification VARCHAR(50) NOT NULL,
    quantite_avant FLOAT,
    quantite_apres FLOAT,
    quantite_min_avant FLOAT,
    quantite_min_apres FLOAT,
    date_peremption_avant DATE,
    date_peremption_apres DATE,
    emplacement_avant VARCHAR(100),
    emplacement_apres VARCHAR(100),
    date_modification TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    utilisateur VARCHAR(100),
    notes TEXT,
    CONSTRAINT fk_hist_inv_article FOREIGN KEY (article_id) REFERENCES inventaire(id) ON DELETE CASCADE,
    CONSTRAINT fk_hist_inv_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_article ON historique_inventaire(article_id);
CREATE INDEX IF NOT EXISTS idx_historique_inventaire_article_id ON historique_inventaire(article_id);
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_ingredient ON historique_inventaire(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_type ON historique_inventaire(type_modification);
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_date ON historique_inventaire(date_modification);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles_courses (
    id SERIAL PRIMARY KEY,
    liste_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantite_necessaire FLOAT NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    achete BOOLEAN NOT NULL DEFAULT FALSE,
    suggere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    achete_le TIMESTAMP WITH TIME ZONE,
    rayon_magasin VARCHAR(100),
    magasin_cible VARCHAR(50),
    famille_produit VARCHAR(50),
    sous_famille_produit VARCHAR(50),
    prix_unitaire FLOAT,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_articles_courses_liste FOREIGN KEY (liste_id) REFERENCES listes_courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_articles_courses_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_articles_courses_positive CHECK (quantite_necessaire > 0)
);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_id ON articles_courses(liste_id);
CREATE INDEX IF NOT EXISTS ix_articles_courses_ingredient_id ON articles_courses(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_articles_courses_priorite ON articles_courses(priorite);
CREATE INDEX IF NOT EXISTS ix_articles_courses_achete ON articles_courses(achete);
CREATE INDEX IF NOT EXISTS ix_articles_courses_cree_le ON articles_courses(cree_le);
CREATE INDEX IF NOT EXISTS ix_articles_courses_famille_produit ON articles_courses(famille_produit);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles_modeles (
    id SERIAL PRIMARY KEY,
    modele_id INTEGER NOT NULL,
    ingredient_id INTEGER,
    nom_article VARCHAR(100) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1.0,
    unite VARCHAR(20) NOT NULL DEFAULT 'pièce',
    rayon_magasin VARCHAR(100) NOT NULL DEFAULT 'Autre',
    priorite VARCHAR(20) NOT NULL DEFAULT 'moyenne',
    notes TEXT,
    ordre INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_articles_modeles_modele FOREIGN KEY (modele_id) REFERENCES modeles_courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_articles_modeles_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_article_modele_quantite_positive CHECK (quantite > 0),
        CONSTRAINT ck_article_modele_priorite_valide CHECK (
            priorite IN ('haute', 'moyenne', 'basse')
        )
);
CREATE INDEX IF NOT EXISTS ix_articles_modeles_modele ON articles_modeles(modele_id);
CREATE INDEX IF NOT EXISTS ix_articles_modeles_ingredient ON articles_modeles(ingredient_id);


-- ─── Correspondances Carrefour Drive ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS correspondances_drive (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER,
    nom_article VARCHAR(200) NOT NULL,
    produit_drive_id VARCHAR(100) NOT NULL,
    produit_drive_nom VARCHAR(300) NOT NULL,
    produit_drive_ean VARCHAR(50),
    produit_drive_url VARCHAR(500),
    quantite_par_defaut FLOAT NOT NULL DEFAULT 1.0,
    nb_utilisations INTEGER NOT NULL DEFAULT 0,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_correspondances_drive_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE SET NULL,
    CONSTRAINT ck_correspondance_drive_quantite_positive CHECK (quantite_par_defaut > 0)
);
CREATE INDEX IF NOT EXISTS ix_correspondances_drive_nom_article ON correspondances_drive(nom_article);
CREATE INDEX IF NOT EXISTS ix_correspondances_drive_produit_id ON correspondances_drive(produit_drive_id);
CREATE INDEX IF NOT EXISTS ix_correspondances_drive_ingredient ON correspondances_drive(ingredient_id);
CREATE INDEX IF NOT EXISTS ix_correspondances_drive_actif ON correspondances_drive(actif);
CREATE UNIQUE INDEX IF NOT EXISTS ix_correspondances_drive_article_produit ON correspondances_drive(nom_article, produit_drive_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS repas (
    id SERIAL PRIMARY KEY,
    planning_id INTEGER NOT NULL,
    recette_id INTEGER,
    date_repas DATE NOT NULL,
    type_repas VARCHAR(50) NOT NULL DEFAULT 'diner',
    portion_ajustee INTEGER,
    prepare BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    entree VARCHAR(200),
    entree_recette_id INTEGER,
    dessert VARCHAR(200),
    dessert_recette_id INTEGER,
    dessert_jules VARCHAR(200),
    dessert_jules_recette_id INTEGER,
    plat_jules TEXT,
    notes_jules TEXT,
    adaptation_auto BOOLEAN NOT NULL DEFAULT TRUE,
    contexte_meteo VARCHAR(50),
    laitage VARCHAR(200),
    -- Accompagnements (migrations 006+)
    legumes VARCHAR(200),
    legumes_recette_id INTEGER,
    feculents VARCHAR(200),
    feculents_recette_id INTEGER,
    proteine_accompagnement VARCHAR(200),
    proteine_accompagnement_recette_id INTEGER,
    -- Goûter PNNS
    fruit_gouter VARCHAR(100),
    gateau_gouter VARCHAR(100),
    -- Équilibre PNNS calculé
    score_equilibre SMALLINT,
    alertes_equilibre JSONB,
    -- Restes
    est_reste BOOLEAN NOT NULL DEFAULT FALSE,
    reste_description VARCHAR(200),
    CONSTRAINT fk_repas_planning FOREIGN KEY (planning_id) REFERENCES plannings(id) ON DELETE CASCADE,
    CONSTRAINT fk_repas_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT fk_repas_entree_recette FOREIGN KEY (entree_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT fk_repas_dessert_recette FOREIGN KEY (dessert_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT fk_repas_dessert_jules_recette FOREIGN KEY (dessert_jules_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT fk_repas_legumes_recette FOREIGN KEY (legumes_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT fk_repas_feculents_recette FOREIGN KEY (feculents_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT fk_repas_proteine_acc_recette FOREIGN KEY (proteine_accompagnement_recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT ck_repas_portions_valides CHECK (
        portion_ajustee IS NULL
        OR (
            portion_ajustee > 0
            AND portion_ajustee <= 20
        )
    )
);
COMMENT ON COLUMN repas.fruit IS 'Fruit entier ou compote (goûter) — texte libre, ex: Pomme, Compote poire';
COMMENT ON COLUMN repas.legumes IS 'Légumes accompagnement (déjeuner/dîner) — texte libre, ex: Haricots verts, Courgettes sautées';
COMMENT ON COLUMN repas.legumes_recette_id IS 'Recette liée pour les légumes (optionnel, sinon texte libre dans `legumes`)';
COMMENT ON COLUMN repas.feculents IS 'Féculents accompagnement — texte libre (ex: Riz basmati, Pommes de terre vapeur)';
COMMENT ON COLUMN repas.feculents_recette_id IS 'Recette liée pour les féculents (optionnel)';
COMMENT ON COLUMN repas.proteine_accompagnement IS 'Protéine quand le plat est féculent/légume (ex: Escalope de dinde, Lentilles)';
COMMENT ON COLUMN repas.proteine_accompagnement_recette_id IS 'Recette liée pour la protéine accompagnement';
COMMENT ON COLUMN repas.fruit_gouter IS 'Fruit frais ou compote au goûter (PNNS) — ex: Pomme, Compote poire sans sucre';
COMMENT ON COLUMN repas.gateau_gouter IS 'Gâteau/biscuit sain au goûter (PNNS) — ex: Cake maison, Barre céréales';
COMMENT ON COLUMN repas.score_equilibre IS 'Score PNNS calculé 0-100 (NULL=non applicable). Vert≥80, Orange 50-79, Rouge<50';
COMMENT ON COLUMN repas.alertes_equilibre IS 'Liste alertes équilibre : ["Pas de légumes", "Féculents manquants", "Protéine manquante"]';
CREATE INDEX IF NOT EXISTS ix_repas_planning ON repas(planning_id);
CREATE INDEX IF NOT EXISTS idx_repas_planning_id ON repas(planning_id);
CREATE INDEX IF NOT EXISTS ix_repas_recette ON repas(recette_id);
CREATE INDEX IF NOT EXISTS ix_repas_date ON repas(date_repas);
CREATE INDEX IF NOT EXISTS ix_repas_type ON repas(type_repas);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS elements_templates (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    jour_semaine INTEGER NOT NULL,
    heure_debut VARCHAR(5) NOT NULL,
    heure_fin VARCHAR(5),
    titre VARCHAR(200) NOT NULL,
    type_event VARCHAR(50) DEFAULT 'autre',
    lieu VARCHAR(200),
    couleur VARCHAR(20),
    CONSTRAINT fk_template_items_template FOREIGN KEY (template_id) REFERENCES templates_semaine(id) ON DELETE CASCADE,
    CONSTRAINT ck_template_jour_valide CHECK (
        jour_semaine >= 0
        AND jour_semaine <= 6
    )
);
CREATE INDEX IF NOT EXISTS idx_template_jour ON elements_templates(template_id, jour_semaine);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions_batch_cooking (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_session DATE NOT NULL,
    heure_debut TIME,
    heure_fin TIME,
    duree_estimee INTEGER NOT NULL DEFAULT 120,
    duree_reelle INTEGER,
    statut VARCHAR(20) NOT NULL DEFAULT 'planifiee',
    avec_jules BOOLEAN NOT NULL DEFAULT FALSE,
    planning_id INTEGER,
    recettes_selectionnees JSONB,
    robots_utilises JSONB,
    notes_avant TEXT,
    notes_apres TEXT,
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    nb_portions_preparees INTEGER NOT NULL DEFAULT 0,
    nb_recettes_completees INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_sessions_batch_planning FOREIGN KEY (planning_id) REFERENCES plannings(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_session_duree_estimee_positive CHECK (duree_estimee > 0),
        CONSTRAINT ck_session_duree_reelle_positive CHECK (
            duree_reelle IS NULL
            OR duree_reelle > 0
        ),
        CONSTRAINT ck_session_portions_positive CHECK (nb_portions_preparees >= 0),
        CONSTRAINT ck_session_recettes_positive CHECK (nb_recettes_completees >= 0)
);
CREATE INDEX IF NOT EXISTS ix_sessions_batch_date ON sessions_batch_cooking(date_session);
CREATE INDEX IF NOT EXISTS ix_sessions_batch_statut ON sessions_batch_cooking(statut);
CREATE INDEX IF NOT EXISTS ix_sessions_batch_planning ON sessions_batch_cooking(planning_id);
CREATE INDEX IF NOT EXISTS idx_session_date_statut ON sessions_batch_cooking(date_session, statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS etapes_batch_cooking (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    recette_id INTEGER,
    ordre INTEGER NOT NULL,
    groupe_parallele INTEGER NOT NULL DEFAULT 0,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    duree_minutes INTEGER NOT NULL DEFAULT 10,
    duree_reelle INTEGER,
    robots_requis JSONB,
    est_supervision BOOLEAN NOT NULL DEFAULT FALSE,
    alerte_bruit BOOLEAN NOT NULL DEFAULT FALSE,
    temperature INTEGER,
    statut VARCHAR(20) NOT NULL DEFAULT 'a_faire',
    heure_debut TIMESTAMP WITH TIME ZONE,
    heure_fin TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    timer_actif BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_etapes_batch_session FOREIGN KEY (session_id) REFERENCES sessions_batch_cooking(id) ON DELETE CASCADE,
    CONSTRAINT fk_etapes_batch_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_etape_batch_ordre_positif CHECK (ordre > 0),
        CONSTRAINT ck_etape_batch_duree_positive CHECK (duree_minutes > 0),
        CONSTRAINT ck_etape_batch_duree_reelle_positive CHECK (
            duree_reelle IS NULL
            OR duree_reelle > 0
        )
);
CREATE INDEX IF NOT EXISTS ix_etapes_batch_session ON etapes_batch_cooking(session_id);
CREATE INDEX IF NOT EXISTS ix_etapes_batch_recette ON etapes_batch_cooking(recette_id);
CREATE INDEX IF NOT EXISTS idx_etape_session_ordre ON etapes_batch_cooking(session_id, ordre);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preparations_batch (
    id SERIAL PRIMARY KEY,
    session_id INTEGER,
    recette_id INTEGER,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions_initiales INTEGER NOT NULL DEFAULT 4,
    portions_restantes INTEGER NOT NULL DEFAULT 4,
    date_preparation DATE NOT NULL,
    date_peremption DATE NOT NULL,
    localisation VARCHAR(50) NOT NULL DEFAULT 'frigo',
    container VARCHAR(100),
    etagere VARCHAR(50),
    repas_attribues JSONB,
    notes TEXT,
    photo_url VARCHAR(500),
    consomme BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_prep_batch_session FOREIGN KEY (session_id) REFERENCES sessions_batch_cooking(id) ON DELETE
    SET NULL,
        CONSTRAINT fk_prep_batch_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_prep_portions_initiales_positive CHECK (portions_initiales > 0),
        CONSTRAINT ck_prep_portions_restantes_positive CHECK (portions_restantes >= 0)
);
CREATE INDEX IF NOT EXISTS ix_prep_batch_session ON preparations_batch(session_id);
CREATE INDEX IF NOT EXISTS ix_prep_batch_recette ON preparations_batch(recette_id);
CREATE INDEX IF NOT EXISTS ix_prep_batch_date ON preparations_batch(date_preparation);
CREATE INDEX IF NOT EXISTS ix_prep_batch_peremption ON preparations_batch(date_peremption);
CREATE INDEX IF NOT EXISTS ix_prep_batch_localisation ON preparations_batch(localisation);
CREATE INDEX IF NOT EXISTS ix_prep_batch_consomme ON preparations_batch(consomme);
CREATE INDEX IF NOT EXISTS idx_prep_localisation_peremption ON preparations_batch(localisation, date_peremption);
CREATE UNIQUE INDEX IF NOT EXISTS uq_prep_session_recette
    ON preparations_batch (session_id, recette_id)
    WHERE session_id IS NOT NULL AND recette_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_prep_consomme_peremption ON preparations_batch(consomme, date_peremption);


-- ─────────────────────────────────────────────────────────────────────────────
-- Congélation batch cooking
CREATE TABLE IF NOT EXISTS batch_cooking_congelation (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_congelation DATE NOT NULL DEFAULT CURRENT_DATE,
    date_limite DATE NOT NULL,
    portions INTEGER NOT NULL DEFAULT 1,
    categorie VARCHAR(50) NOT NULL DEFAULT 'autre',
    recette_id INTEGER,
    session_id INTEGER,
    notes TEXT,
    consomme BOOLEAN NOT NULL DEFAULT FALSE,
    date_consommation DATE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_congelation_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT fk_congelation_session FOREIGN KEY (session_id) REFERENCES sessions_batch_cooking(id) ON DELETE SET NULL,
    CONSTRAINT ck_congelation_portions_positive CHECK (portions > 0),
    CONSTRAINT ck_congelation_categorie CHECK (categorie IN (
        'viande', 'poisson', 'legume', 'fruit', 'plat_cuisine',
        'soupe', 'sauce', 'pain', 'patisserie', 'herbes', 'autre'
    ))
);
CREATE INDEX IF NOT EXISTS ix_congelation_date_limite ON batch_cooking_congelation(date_limite);
CREATE INDEX IF NOT EXISTS ix_congelation_categorie ON batch_cooking_congelation(categorie);
CREATE INDEX IF NOT EXISTS ix_congelation_consomme ON batch_cooking_congelation(consomme);
CREATE INDEX IF NOT EXISTS ix_congelation_recette ON batch_cooking_congelation(recette_id);
CREATE INDEX IF NOT EXISTS idx_congelation_consomme_limite ON batch_cooking_congelation(consomme, date_limite)
    WHERE consomme = FALSE;



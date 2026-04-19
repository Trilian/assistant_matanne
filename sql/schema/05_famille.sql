-- ============================================================================
-- ASSISTANT MATANNE — Tables Famille
-- ============================================================================
-- Contient : profils_enfants, activités_famille, budgets_famille, Garmin,
--            santé, jalons, contacts, documents, anniversaires
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profils_enfants (
    id SERIAL PRIMARY KEY,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    taille_vetements JSONB DEFAULT '{}'::jsonb,
    pointure VARCHAR(50),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS routines_sante (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    jours JSONB DEFAULT '[]'::jsonb,
    heure_preferee VARCHAR(10),
    duree_minutes INTEGER NOT NULL DEFAULT 30,
    rappel BOOLEAN NOT NULL DEFAULT TRUE,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_health_routines_type ON routines_sante(type_routine);
CREATE INDEX IF NOT EXISTS ix_health_routines_actif ON routines_sante(actif);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS objectifs_sante (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    valeur_cible FLOAT NOT NULL,
    unite VARCHAR(50) NOT NULL,
    valeur_actuelle FLOAT,
    date_debut DATE NOT NULL DEFAULT CURRENT_DATE,
    date_cible DATE NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_objective_valeur_positive CHECK (valeur_cible > 0),
    CONSTRAINT ck_objective_dates CHECK (date_debut <= date_cible)
);
CREATE INDEX IF NOT EXISTS ix_health_objectives_categorie ON objectifs_sante(categorie);
CREATE INDEX IF NOT EXISTS ix_health_objectives_statut ON objectifs_sante(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activites_weekend (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_activite VARCHAR(100) NOT NULL,
    date_prevue DATE NOT NULL,
    heure_debut VARCHAR(10),
    duree_estimee_h FLOAT,
    lieu VARCHAR(200),
    adresse TEXT,
    latitude FLOAT,
    longitude FLOAT,
    adapte_jules BOOLEAN NOT NULL DEFAULT TRUE,
    age_min_mois INTEGER,
    cout_estime FLOAT,
    cout_reel FLOAT,
    meteo_requise VARCHAR(50),
    statut VARCHAR(50) NOT NULL DEFAULT 'planifié',
    note_lieu INTEGER,
    commentaire TEXT,
    a_refaire BOOLEAN,
    participants JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_weekend_note_range CHECK (
        note_lieu IS NULL
        OR (
            note_lieu >= 1
            AND note_lieu <= 5
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_weekend_activities_type ON activites_weekend(type_activite);
CREATE INDEX IF NOT EXISTS ix_weekend_activities_date ON activites_weekend(date_prevue);
CREATE INDEX IF NOT EXISTS ix_weekend_activities_statut ON activites_weekend(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS achats_famille (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(50) NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    prix_estime FLOAT,
    prix_reel FLOAT,
    url VARCHAR(500),
    image_url VARCHAR(500),
    magasin VARCHAR(200),
    taille VARCHAR(50),
    age_recommande_mois INTEGER,
    achete BOOLEAN NOT NULL DEFAULT FALSE,
    date_achat DATE,
    suggere_par VARCHAR(50),
    pour_qui VARCHAR(50) NOT NULL DEFAULT 'famille',
    a_revendre BOOLEAN NOT NULL DEFAULT FALSE,
    prix_revente_estime FLOAT,
    vendu_le DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_family_purchases_categorie ON achats_famille(categorie);
CREATE INDEX IF NOT EXISTS ix_family_purchases_priorite ON achats_famille(priorite);
CREATE INDEX IF NOT EXISTS ix_family_purchases_achete ON achats_famille(achete);
CREATE INDEX IF NOT EXISTS ix_achats_famille_pour_qui ON achats_famille(pour_qui);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activites_famille (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_activite VARCHAR(100) NOT NULL,
    date_prevue DATE NOT NULL,
    heure_debut TIME,
    duree_heures FLOAT,
    lieu VARCHAR(200),
    qui_participe JSONB,
    age_minimal_recommande INTEGER,
    cout_estime FLOAT,
    cout_reel FLOAT,
    statut VARCHAR(50) NOT NULL DEFAULT 'planifié',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_activite_duree_positive CHECK (
        duree_heures IS NULL
        OR duree_heures > 0
    ),
    CONSTRAINT ck_activite_age_positif CHECK (
        age_minimal_recommande IS NULL
        OR age_minimal_recommande >= 0
    )
);
CREATE INDEX IF NOT EXISTS ix_family_activities_type ON activites_famille(type_activite);
CREATE INDEX IF NOT EXISTS ix_family_activities_date ON activites_famille(date_prevue);
CREATE INDEX IF NOT EXISTS ix_family_activities_statut ON activites_famille(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS budgets_famille (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    categorie VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    montant FLOAT NOT NULL,
    magasin VARCHAR(200),
    est_recurrent BOOLEAN NOT NULL DEFAULT FALSE,
    frequence_recurrence VARCHAR(50),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_budget_montant_positive CHECK (montant > 0)
);
CREATE INDEX IF NOT EXISTS ix_family_budgets_date ON budgets_famille(date);
CREATE INDEX IF NOT EXISTS ix_family_budgets_categorie ON budgets_famille(categorie);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles_achats_famille (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1.0,
    prix_estime FLOAT NOT NULL DEFAULT 0.0,
    liste VARCHAR(50) NOT NULL DEFAULT 'Nous',
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    date_ajout TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    date_achat TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_shopping_items_titre ON articles_achats_famille(titre);
CREATE INDEX IF NOT EXISTS ix_shopping_items_categorie ON articles_achats_famille(categorie);
CREATE INDEX IF NOT EXISTS ix_shopping_items_liste ON articles_achats_famille(liste);
CREATE INDEX IF NOT EXISTS ix_shopping_items_actif ON articles_achats_famille(actif);
CREATE INDEX IF NOT EXISTS ix_shopping_items_date ON articles_achats_famille(date_ajout);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historique_achats (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    article_nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100),
    rayon_magasin VARCHAR(100),
    derniere_achat TIMESTAMP WITH TIME ZONE NOT NULL,
    frequence_jours INTEGER,
    nb_achats INTEGER NOT NULL DEFAULT 1,
    prix_dernier FLOAT,
    prix_moyen FLOAT
);
CREATE INDEX IF NOT EXISTS ix_historique_achats_nom ON historique_achats(article_nom);
CREATE INDEX IF NOT EXISTS ix_historique_achats_date ON historique_achats(derniere_achat);
CREATE INDEX IF NOT EXISTS ix_historique_achats_nom_date ON historique_achats(article_nom, derniere_achat);
CREATE INDEX IF NOT EXISTS ix_historique_achats_user_id ON historique_achats(user_id);
CREATE INDEX IF NOT EXISTS ix_historique_achats_user_nom ON historique_achats(user_id, article_nom);
COMMENT ON COLUMN historique_achats.user_id IS 'Identifiant de l''utilisateur propriétaire (NULL = données legacy partagées)';


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS garmin_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    oauth_token VARCHAR(500) NOT NULL,
    oauth_token_secret VARCHAR(500) NOT NULL,
    garmin_user_id VARCHAR(100),
    derniere_sync TIMESTAMP WITH TIME ZONE,
    sync_active BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_tokens_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_garmin_tokens_user_id ON garmin_tokens(user_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activites_garmin (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    garmin_activity_id VARCHAR(100) NOT NULL,
    type_activite VARCHAR(50) NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    duree_secondes INTEGER NOT NULL,
    distance_metres FLOAT,
    calories INTEGER,
    fc_moyenne INTEGER,
    fc_max INTEGER,
    vitesse_moyenne FLOAT,
    allure_moyenne FLOAT,
    elevation_gain INTEGER,
    raw_data JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_activities_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE,
    CONSTRAINT ck_garmin_duree_positive CHECK (duree_secondes > 0)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_garmin_activity_id ON activites_garmin(garmin_activity_id);
CREATE INDEX IF NOT EXISTS ix_garmin_activities_user ON activites_garmin(user_id);
CREATE INDEX IF NOT EXISTS ix_garmin_activities_type ON activites_garmin(type_activite);
CREATE INDEX IF NOT EXISTS ix_garmin_activities_date ON activites_garmin(date_debut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resumes_quotidiens_garmin (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    pas INTEGER NOT NULL DEFAULT 0,
    distance_metres INTEGER NOT NULL DEFAULT 0,
    calories_totales INTEGER NOT NULL DEFAULT 0,
    calories_actives INTEGER NOT NULL DEFAULT 0,
    minutes_actives INTEGER NOT NULL DEFAULT 0,
    minutes_tres_actives INTEGER NOT NULL DEFAULT 0,
    fc_repos INTEGER,
    fc_min INTEGER,
    fc_max INTEGER,
    sommeil_total_minutes INTEGER,
    sommeil_profond_minutes INTEGER,
    sommeil_leger_minutes INTEGER,
    sommeil_rem_minutes INTEGER,
    stress_moyen INTEGER,
    body_battery_max INTEGER,
    body_battery_min INTEGER,
    raw_data JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_daily_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_garmin_daily_user ON resumes_quotidiens_garmin(user_id);
CREATE INDEX IF NOT EXISTS ix_garmin_daily_date ON resumes_quotidiens_garmin(date);
CREATE UNIQUE INDEX IF NOT EXISTS uq_garmin_daily_user_date ON resumes_quotidiens_garmin(user_id, date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS journaux_alimentaires (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    heure TIMESTAMP WITH TIME ZONE,
    repas VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    calories_estimees INTEGER,
    proteines_g FLOAT,
    glucides_g FLOAT,
    lipides_g FLOAT,
    qualite INTEGER,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_food_logs_user FOREIGN KEY (user_id) REFERENCES profils_utilisateurs(id) ON DELETE CASCADE,
    CONSTRAINT ck_food_qualite_range CHECK (
        qualite IS NULL
        OR (
            qualite >= 1
            AND qualite <= 5
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_food_logs_user ON journaux_alimentaires(user_id);
CREATE INDEX IF NOT EXISTS ix_food_logs_date ON journaux_alimentaires(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS entrees_bien_etre (
    id SERIAL PRIMARY KEY,
    child_id INTEGER,
    username VARCHAR(200),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    mood VARCHAR(100),
    sleep_hours FLOAT,
    activity VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_wellbeing_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_wellbeing_child ON entrees_bien_etre(child_id);
CREATE INDEX IF NOT EXISTS ix_wellbeing_username ON entrees_bien_etre(username);
CREATE INDEX IF NOT EXISTS ix_wellbeing_date ON entrees_bien_etre(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jalons (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    date_atteint DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    contexte_narratif TEXT,
    lieu VARCHAR(200),
    emotion_parents VARCHAR(50),
    age_mois_atteint INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_milestones_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_milestones_child ON jalons(child_id);
CREATE INDEX IF NOT EXISTS idx_jalons_profil_id ON jalons(child_id);
CREATE INDEX IF NOT EXISTS ix_milestones_categorie ON jalons(categorie);
CREATE INDEX IF NOT EXISTS ix_milestones_date ON jalons(date_atteint);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS entrees_sante (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    type_activite VARCHAR(100) NOT NULL,
    duree_minutes INTEGER NOT NULL,
    intensite VARCHAR(50),
    calories_brulees INTEGER,
    note_energie INTEGER,
    note_moral INTEGER,
    ressenti TEXT,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_health_entries_routine FOREIGN KEY (routine_id) REFERENCES routines_sante(id) ON DELETE CASCADE,
    CONSTRAINT ck_entry_duree_positive CHECK (duree_minutes > 0),
    CONSTRAINT ck_entry_energie CHECK (
        note_energie IS NULL
        OR (
            note_energie >= 1
            AND note_energie <= 10
        )
    ),
    CONSTRAINT ck_entry_moral CHECK (
        note_moral IS NULL
        OR (
            note_moral >= 1
            AND note_moral <= 10
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_health_entries_routine ON entrees_sante(routine_id);
CREATE INDEX IF NOT EXISTS ix_health_entries_date ON entrees_sante(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vaccins (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    date_vaccination DATE NOT NULL,
    numero_lot VARCHAR(100),
    medecin VARCHAR(200),
    lieu VARCHAR(200),
    rappel_prevu DATE,
    dose_numero INTEGER DEFAULT 1,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_vaccins_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE CASCADE,
    CONSTRAINT ck_vaccins_dose_positive CHECK (dose_numero > 0)
);
CREATE INDEX IF NOT EXISTS ix_vaccins_child ON vaccins(child_id);
CREATE INDEX IF NOT EXISTS ix_vaccins_rappel ON vaccins(rappel_prevu);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rendez_vous_medicaux (
    id SERIAL PRIMARY KEY,
    child_id INTEGER,
    membre_famille VARCHAR(100),
    specialite VARCHAR(100) NOT NULL,
    medecin VARCHAR(200),
    date_rdv TIMESTAMP WITH TIME ZONE NOT NULL,
    lieu VARCHAR(300),
    motif TEXT,
    compte_rendu TEXT,
    ordonnance TEXT,
    prochain_rdv DATE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_rdv_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS ix_rdv_child ON rendez_vous_medicaux(child_id);
CREATE INDEX IF NOT EXISTS ix_rdv_date ON rendez_vous_medicaux(date_rdv);
CREATE INDEX IF NOT EXISTS ix_rdv_membre ON rendez_vous_medicaux(membre_famille);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mesures_croissance (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL,
    date_mesure DATE NOT NULL,
    age_mois NUMERIC(5, 1) NOT NULL,
    poids_kg NUMERIC(5, 2),
    taille_cm NUMERIC(5, 1),
    perimetre_cranien_cm NUMERIC(5, 1),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_croissance_child FOREIGN KEY (child_id) REFERENCES profils_enfants(id) ON DELETE CASCADE,
    CONSTRAINT ck_croissance_age_positif CHECK (age_mois >= 0),
    CONSTRAINT ck_croissance_poids_positif CHECK (
        poids_kg IS NULL
        OR poids_kg > 0
    ),
    CONSTRAINT ck_croissance_taille_positive CHECK (
        taille_cm IS NULL
        OR taille_cm > 0
    )
);
CREATE INDEX IF NOT EXISTS ix_croissance_child ON mesures_croissance(child_id);
CREATE INDEX IF NOT EXISTS ix_croissance_date ON mesures_croissance(date_mesure);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts_famille (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    prenom VARCHAR(200),
    telephone VARCHAR(30),
    email VARCHAR(300),
    adresse TEXT,
    categorie VARCHAR(50) NOT NULL DEFAULT 'famille',
    relation VARCHAR(100),
    notes TEXT,
    est_urgence BOOLEAN NOT NULL DEFAULT FALSE,
    sous_categorie VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_contacts_categorie CHECK (
        categorie IN (
            'medical',
            'garde',
            'education',
            'administration',
            'famille',
            'urgence'
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_contacts_categorie ON contacts_famille(categorie);
CREATE INDEX IF NOT EXISTS ix_contacts_urgence ON contacts_famille(est_urgence)
WHERE est_urgence = TRUE;


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS anniversaires_famille (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_naissance DATE NOT NULL,
    relation VARCHAR(100),
    notes TEXT,
    rappel_jours_avant JSONB DEFAULT '[7, 1]',
    idees_cadeaux TEXT,
    historique_cadeaux JSONB DEFAULT '[]',
    actif BOOLEAN NOT NULL DEFAULT true,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_anniversaires_date ON anniversaires_famille(date_naissance);
CREATE INDEX IF NOT EXISTS ix_anniversaires_actif ON anniversaires_famille(actif);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checklists_anniversaire (
    id SERIAL PRIMARY KEY,
    anniversaire_id INTEGER NOT NULL REFERENCES anniversaires_famille(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    budget_total FLOAT,
    date_limite DATE,
    completee BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    maj_auto_le TIMESTAMP,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_checklists_anniversaire_anniversaire_id ON checklists_anniversaire(anniversaire_id);
CREATE INDEX IF NOT EXISTS ix_checklists_anniversaire_completee ON checklists_anniversaire(completee);

CREATE TABLE IF NOT EXISTS items_checklist_anniversaire (
    id SERIAL PRIMARY KEY,
    checklist_id INTEGER NOT NULL REFERENCES checklists_anniversaire(id) ON DELETE CASCADE,
    categorie VARCHAR(50) NOT NULL,
    libelle VARCHAR(300) NOT NULL,
    budget_estime FLOAT,
    budget_reel FLOAT,
    fait BOOLEAN NOT NULL DEFAULT FALSE,
    priorite VARCHAR(20) NOT NULL DEFAULT 'moyenne',
    responsable VARCHAR(50),
    quand VARCHAR(20),
    source VARCHAR(20) NOT NULL DEFAULT 'manuel',
    score_pertinence FLOAT,
    raison_suggestion TEXT,
    ordre INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_items_checklist_anniversaire_checklist_id ON items_checklist_anniversaire(checklist_id);
CREATE INDEX IF NOT EXISTS ix_items_checklist_anniversaire_categorie ON items_checklist_anniversaire(categorie);
CREATE INDEX IF NOT EXISTS ix_items_checklist_anniversaire_fait ON items_checklist_anniversaire(fait);
CREATE INDEX IF NOT EXISTS ix_items_checklist_anniversaire_source ON items_checklist_anniversaire(source);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS evenements_familiaux (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    date_fin TIMESTAMP WITH TIME ZONE,
    date_evenement DATE DEFAULT CURRENT_DATE,
    lieu VARCHAR(300),
    type_evenement VARCHAR(50) NOT NULL DEFAULT 'famille',
    recurrence VARCHAR(30),
    rappel_minutes INTEGER,
    rappel_jours_avant INTEGER NOT NULL DEFAULT 7,
    participants JSONB DEFAULT '[]',
    couleur VARCHAR(20),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_evt_type CHECK (
        type_evenement IN (
            'famille',
            'medical',
            'scolaire',
            'loisir',
            'administratif',
            'couple'
        )
    ),
    CONSTRAINT ck_evt_dates CHECK (
        date_fin IS NULL
        OR date_fin >= date_debut
    )
);
CREATE INDEX IF NOT EXISTS ix_evenements_date_debut ON evenements_familiaux(date_debut);
CREATE INDEX IF NOT EXISTS ix_evenements_type ON evenements_familiaux(type_evenement);
CREATE INDEX IF NOT EXISTS ix_evenements_familiaux_date_evenement ON evenements_familiaux(date_evenement);
CREATE INDEX IF NOT EXISTS ix_evenements_familiaux_actif ON evenements_familiaux(actif);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents_famille (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(300) NOT NULL,
    titre VARCHAR(200),
    type_document VARCHAR(50) NOT NULL,
    categorie VARCHAR(50) NOT NULL DEFAULT 'autre',
    fichier_url VARCHAR(500),
    fichier_nom VARCHAR(200),
    date_expiration DATE,
    date_document DATE,
    membre_famille VARCHAR(100),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    rappel_expiration_jours INTEGER DEFAULT 30,
    tags JSONB DEFAULT '[]',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_doc_type CHECK (
        type_document IN (
            'identite',
            'medical',
            'scolaire',
            'administratif',
            'assurance',
            'autre'
        )
    )
);
CREATE INDEX IF NOT EXISTS ix_documents_type ON documents_famille(type_document);
CREATE INDEX IF NOT EXISTS ix_documents_expiration ON documents_famille(date_expiration)
WHERE date_expiration IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_documents_membre ON documents_famille(membre_famille);
CREATE INDEX IF NOT EXISTS ix_documents_famille_categorie ON documents_famille(categorie);
CREATE INDEX IF NOT EXISTS ix_documents_famille_actif ON documents_famille(actif);

-- ============================================================================
-- PARTIE 5 : TABLES MAISON (sans modèles ORM — migration 020)
-- ============================================================================


-- Source: 06_maison.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Maison
-- ============================================================================
-- Contient : projets, routines, jardin, entretien, stocks, pièces,
--            objets, artisans, énergie, maison extensions
-- ============================================================================


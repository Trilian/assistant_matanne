-- ════════════════════════════════════════════════════════════════════════════
-- SQL CORRECT généré depuis les modèles SQLAlchemy
-- Assistant MaTanne v2.0 - 25 Janvier 2026
-- À copier-coller dans Supabase SQL Editor
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS calendar_events (
	id SERIAL NOT NULL, 
	titre VARCHAR(200) NOT NULL, 
	description TEXT, 
	date_debut TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	date_fin TIMESTAMP WITHOUT TIME ZONE, 
	lieu VARCHAR(200), 
	type_event VARCHAR(50) NOT NULL, 
	couleur VARCHAR(20), 
	rappel_avant_minutes INTEGER, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_calendar_events PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS child_profiles (
	id SERIAL NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	date_of_birth DATE, 
	gender VARCHAR(20), 
	notes TEXT, 
	actif BOOLEAN NOT NULL, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_child_profiles PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS family_activities (
	id SERIAL NOT NULL, 
	titre VARCHAR(200) NOT NULL, 
	description TEXT, 
	type_activite VARCHAR(100) NOT NULL, 
	date_prevue DATE NOT NULL, 
	duree_heures FLOAT, 
	lieu VARCHAR(200), 
	qui_participe JSONB, 
	age_minimal_recommande INTEGER, 
	cout_estime FLOAT, 
	cout_reel FLOAT, 
	statut VARCHAR(50) NOT NULL, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_family_activities PRIMARY KEY (id), 
	CONSTRAINT ck_family_activities_ck_activite_duree_positive CHECK (duree_heures > 0), 
	CONSTRAINT ck_family_activities_ck_activite_age_positif CHECK (age_minimal_recommande >= 0)
)

;


CREATE TABLE IF NOT EXISTS family_budgets (
	id SERIAL NOT NULL, 
	date DATE NOT NULL, 
	categorie VARCHAR(100) NOT NULL, 
	description VARCHAR(200), 
	montant FLOAT NOT NULL, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_family_budgets PRIMARY KEY (id), 
	CONSTRAINT ck_family_budgets_ck_budget_montant_positive CHECK (montant > 0)
)

;


CREATE TABLE IF NOT EXISTS garden_items (
	id SERIAL NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	type VARCHAR(100) NOT NULL, 
	location VARCHAR(200), 
	statut VARCHAR(50) NOT NULL, 
	date_plantation DATE, 
	date_recolte_prevue DATE, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_garden_items PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS health_objectives (
	id SERIAL NOT NULL, 
	titre VARCHAR(200) NOT NULL, 
	description TEXT, 
	categorie VARCHAR(100) NOT NULL, 
	valeur_cible FLOAT NOT NULL, 
	unite VARCHAR(50) NOT NULL, 
	valeur_actuelle FLOAT, 
	date_debut DATE NOT NULL, 
	date_cible DATE NOT NULL, 
	priorite VARCHAR(50) NOT NULL, 
	statut VARCHAR(50) NOT NULL, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_health_objectives PRIMARY KEY (id), 
	CONSTRAINT ck_health_objectives_ck_objective_valeur_positive CHECK (valeur_cible > 0), 
	CONSTRAINT ck_health_objectives_ck_objective_dates CHECK (date_debut <= date_cible)
)

;


CREATE TABLE IF NOT EXISTS health_routines (
	id SERIAL NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	description TEXT, 
	type_routine VARCHAR(100) NOT NULL, 
	frequence VARCHAR(50) NOT NULL, 
	duree_minutes INTEGER NOT NULL, 
	intensite VARCHAR(50) NOT NULL, 
	jours_semaine JSONB, 
	calories_brulees_estimees INTEGER, 
	actif BOOLEAN NOT NULL, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_health_routines PRIMARY KEY (id), 
	CONSTRAINT ck_health_routines_ck_routine_duree_positive CHECK (duree_minutes > 0)
)

;


CREATE TABLE IF NOT EXISTS ingredients (
	id SERIAL NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	categorie VARCHAR(100), 
	unite VARCHAR(50) NOT NULL, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_ingredients PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS modeles_courses (
	id SERIAL NOT NULL, 
	nom VARCHAR(100) NOT NULL, 
	description TEXT, 
	utilisateur_id VARCHAR(100), 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	modifie_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	actif BOOLEAN NOT NULL, 
	articles_data JSONB, 
	CONSTRAINT pk_modeles_courses PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS plannings (
	id SERIAL NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	semaine_debut DATE NOT NULL, 
	semaine_fin DATE NOT NULL, 
	actif BOOLEAN NOT NULL, 
	genere_par_ia BOOLEAN NOT NULL, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_plannings PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS projects (
	id SERIAL NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	description TEXT, 
	statut VARCHAR(50) NOT NULL, 
	priorite VARCHAR(50) NOT NULL, 
	date_debut DATE, 
	date_fin_prevue DATE, 
	date_fin_reelle DATE, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_projects PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS recettes (
	id SERIAL NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	description TEXT, 
	temps_preparation INTEGER NOT NULL, 
	temps_cuisson INTEGER NOT NULL, 
	portions INTEGER NOT NULL, 
	difficulte VARCHAR(50) NOT NULL, 
	type_repas VARCHAR(50) NOT NULL, 
	saison VARCHAR(50) NOT NULL, 
	categorie VARCHAR(100), 
	est_rapide BOOLEAN NOT NULL, 
	est_equilibre BOOLEAN NOT NULL, 
	compatible_bebe BOOLEAN NOT NULL, 
	compatible_batch BOOLEAN NOT NULL, 
	congelable BOOLEAN NOT NULL, 
	est_bio BOOLEAN NOT NULL, 
	est_local BOOLEAN NOT NULL, 
	score_bio INTEGER NOT NULL, 
	score_local INTEGER NOT NULL, 
	compatible_cookeo BOOLEAN NOT NULL, 
	compatible_monsieur_cuisine BOOLEAN NOT NULL, 
	compatible_airfryer BOOLEAN NOT NULL, 
	compatible_multicooker BOOLEAN NOT NULL, 
	calories INTEGER, 
	proteines FLOAT, 
	lipides FLOAT, 
	glucides FLOAT, 
	genere_par_ia BOOLEAN NOT NULL, 
	score_ia FLOAT, 
	url_image VARCHAR(500), 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	modifie_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_recettes PRIMARY KEY (id), 
	CONSTRAINT ck_recettes_ck_temps_prep_positif CHECK (temps_preparation >= 0), 
	CONSTRAINT ck_recettes_ck_temps_cuisson_positif CHECK (temps_cuisson >= 0), 
	CONSTRAINT ck_recettes_ck_portions_valides CHECK (portions > 0 AND portions <= 20), 
	CONSTRAINT ck_recettes_ck_score_bio CHECK (score_bio >= 0 AND score_bio <= 100), 
	CONSTRAINT ck_recettes_ck_score_local CHECK (score_local >= 0 AND score_local <= 100)
)

;


CREATE TABLE IF NOT EXISTS routines (
	id SERIAL NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	description TEXT, 
	categorie VARCHAR(100), 
	frequence VARCHAR(50) NOT NULL, 
	actif BOOLEAN NOT NULL, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_routines PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS shopping_items_famille (
	id SERIAL NOT NULL, 
	titre VARCHAR(200) NOT NULL, 
	categorie VARCHAR(50) NOT NULL, 
	quantite FLOAT NOT NULL, 
	prix_estime FLOAT NOT NULL, 
	liste VARCHAR(50) NOT NULL, 
	actif BOOLEAN NOT NULL, 
	date_ajout TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	date_achat TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT pk_shopping_items_famille PRIMARY KEY (id)
)

;


CREATE TABLE IF NOT EXISTS articles_modeles (
	id SERIAL NOT NULL, 
	modele_id INTEGER NOT NULL, 
	ingredient_id INTEGER, 
	nom_article VARCHAR(100) NOT NULL, 
	quantite FLOAT NOT NULL, 
	unite VARCHAR(20) NOT NULL, 
	rayon_magasin VARCHAR(100) NOT NULL, 
	priorite VARCHAR(20) NOT NULL, 
	notes TEXT, 
	ordre INTEGER NOT NULL, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_articles_modeles PRIMARY KEY (id), 
	CONSTRAINT ck_articles_modeles_ck_article_modele_quantite_positive CHECK (quantite > 0), 
	CONSTRAINT ck_articles_modeles_ck_article_modele_priorite_valide CHECK (priorite IN ('haute', 'moyenne', 'basse')), 
	CONSTRAINT fk_articles_modeles_modele_id_modeles_courses FOREIGN KEY(modele_id) REFERENCES modeles_courses (id) ON DELETE CASCADE, 
	CONSTRAINT fk_articles_modeles_ingredient_id_ingredients FOREIGN KEY(ingredient_id) REFERENCES ingredients (id) ON DELETE SET NULL
)

;


CREATE TABLE IF NOT EXISTS batch_meals (
	id SERIAL NOT NULL, 
	recette_id INTEGER, 
	nom VARCHAR(200) NOT NULL, 
	description TEXT, 
	portions_creees INTEGER NOT NULL, 
	portions_restantes INTEGER NOT NULL, 
	date_preparation DATE NOT NULL, 
	date_peremption DATE NOT NULL, 
	container_type VARCHAR(100), 
	localisation VARCHAR(200), 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_batch_meals PRIMARY KEY (id), 
	CONSTRAINT fk_batch_meals_recette_id_recettes FOREIGN KEY(recette_id) REFERENCES recettes (id) ON DELETE SET NULL
)

;


CREATE TABLE IF NOT EXISTS etapes_recette (
	id SERIAL NOT NULL, 
	recette_id INTEGER NOT NULL, 
	ordre INTEGER NOT NULL, 
	description TEXT NOT NULL, 
	duree INTEGER, 
	CONSTRAINT pk_etapes_recette PRIMARY KEY (id), 
	CONSTRAINT ck_etapes_recette_ck_ordre_positif CHECK (ordre > 0), 
	CONSTRAINT fk_etapes_recette_recette_id_recettes FOREIGN KEY(recette_id) REFERENCES recettes (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS garden_logs (
	id SERIAL NOT NULL, 
	garden_item_id INTEGER, 
	date DATE NOT NULL, 
	action VARCHAR(200) NOT NULL, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_garden_logs PRIMARY KEY (id), 
	CONSTRAINT fk_garden_logs_garden_item_id_garden_items FOREIGN KEY(garden_item_id) REFERENCES garden_items (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS health_entries (
	id SERIAL NOT NULL, 
	routine_id INTEGER, 
	date DATE NOT NULL, 
	type_activite VARCHAR(100) NOT NULL, 
	duree_minutes INTEGER NOT NULL, 
	intensite VARCHAR(50) NOT NULL, 
	calories_brulees INTEGER, 
	note_energie INTEGER, 
	note_moral INTEGER, 
	ressenti TEXT, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_health_entries PRIMARY KEY (id), 
	CONSTRAINT ck_health_entries_ck_entry_duree_positive CHECK (duree_minutes > 0), 
	CONSTRAINT ck_health_entries_ck_entry_energie CHECK (note_energie >= 1 AND note_energie <= 10), 
	CONSTRAINT ck_health_entries_ck_entry_moral CHECK (note_moral >= 1 AND note_moral <= 10), 
	CONSTRAINT fk_health_entries_routine_id_health_routines FOREIGN KEY(routine_id) REFERENCES health_routines (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS historique_recettes (
	id SERIAL NOT NULL, 
	recette_id INTEGER NOT NULL, 
	date_cuisson DATE NOT NULL, 
	portions_cuisinees INTEGER NOT NULL, 
	note INTEGER, 
	avis TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_historique_recettes PRIMARY KEY (id), 
	CONSTRAINT ck_historique_recettes_ck_note_valide CHECK (note IS NULL OR (note >= 0 AND note <= 5)), 
	CONSTRAINT ck_historique_recettes_ck_portions_cuisinees_positive CHECK (portions_cuisinees > 0), 
	CONSTRAINT fk_historique_recettes_recette_id_recettes FOREIGN KEY(recette_id) REFERENCES recettes (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS inventaire (
	id SERIAL NOT NULL, 
	ingredient_id INTEGER NOT NULL, 
	quantite FLOAT NOT NULL, 
	quantite_min FLOAT NOT NULL, 
	emplacement VARCHAR(100), 
	date_peremption DATE, 
	derniere_maj TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	photo_url VARCHAR(500), 
	photo_filename VARCHAR(200), 
	photo_uploaded_at TIMESTAMP WITHOUT TIME ZONE, 
	code_barres VARCHAR(50), 
	prix_unitaire FLOAT, 
	CONSTRAINT pk_inventaire PRIMARY KEY (id), 
	CONSTRAINT ck_inventaire_ck_quantite_inventaire_positive CHECK (quantite >= 0), 
	CONSTRAINT ck_inventaire_ck_seuil_positif CHECK (quantite_min >= 0), 
	CONSTRAINT fk_inventaire_ingredient_id_ingredients FOREIGN KEY(ingredient_id) REFERENCES ingredients (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS liste_courses (
	id SERIAL NOT NULL, 
	ingredient_id INTEGER NOT NULL, 
	quantite_necessaire FLOAT NOT NULL, 
	priorite VARCHAR(50) NOT NULL, 
	achete BOOLEAN NOT NULL, 
	suggere_par_ia BOOLEAN NOT NULL, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	achete_le TIMESTAMP WITHOUT TIME ZONE, 
	rayon_magasin VARCHAR(100), 
	magasin_cible VARCHAR(50), 
	notes TEXT, 
	CONSTRAINT pk_liste_courses PRIMARY KEY (id), 
	CONSTRAINT ck_liste_courses_ck_quantite_courses_positive CHECK (quantite_necessaire > 0), 
	CONSTRAINT fk_liste_courses_ingredient_id_ingredients FOREIGN KEY(ingredient_id) REFERENCES ingredients (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS milestones (
	id SERIAL NOT NULL, 
	child_id INTEGER NOT NULL, 
	titre VARCHAR(200) NOT NULL, 
	description TEXT, 
	categorie VARCHAR(100) NOT NULL, 
	date_atteint DATE NOT NULL, 
	photo_url VARCHAR(500), 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_milestones PRIMARY KEY (id), 
	CONSTRAINT fk_milestones_child_id_child_profiles FOREIGN KEY(child_id) REFERENCES child_profiles (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS project_tasks (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	description TEXT, 
	statut VARCHAR(50) NOT NULL, 
	priorite VARCHAR(50) NOT NULL, 
	"date_echÚance" DATE, 
	"assignÚ_Ó" VARCHAR(200), 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_project_tasks PRIMARY KEY (id), 
	CONSTRAINT fk_project_tasks_project_id_projects FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS recette_ingredients (
	id SERIAL NOT NULL, 
	recette_id INTEGER NOT NULL, 
	ingredient_id INTEGER NOT NULL, 
	quantite FLOAT NOT NULL, 
	unite VARCHAR(50) NOT NULL, 
	optionnel BOOLEAN NOT NULL, 
	CONSTRAINT pk_recette_ingredients PRIMARY KEY (id), 
	CONSTRAINT ck_recette_ingredients_ck_quantite_positive CHECK (quantite > 0), 
	CONSTRAINT fk_recette_ingredients_recette_id_recettes FOREIGN KEY(recette_id) REFERENCES recettes (id) ON DELETE CASCADE, 
	CONSTRAINT fk_recette_ingredients_ingredient_id_ingredients FOREIGN KEY(ingredient_id) REFERENCES ingredients (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS repas (
	id SERIAL NOT NULL, 
	planning_id INTEGER NOT NULL, 
	recette_id INTEGER, 
	date_repas DATE NOT NULL, 
	type_repas VARCHAR(50) NOT NULL, 
	portion_ajustee INTEGER, 
	prepare BOOLEAN NOT NULL, 
	notes TEXT, 
	CONSTRAINT pk_repas PRIMARY KEY (id), 
	CONSTRAINT fk_repas_planning_id_plannings FOREIGN KEY(planning_id) REFERENCES plannings (id) ON DELETE CASCADE, 
	CONSTRAINT fk_repas_recette_id_recettes FOREIGN KEY(recette_id) REFERENCES recettes (id) ON DELETE SET NULL
)

;


CREATE TABLE IF NOT EXISTS routine_tasks (
	id SERIAL NOT NULL, 
	routine_id INTEGER NOT NULL, 
	nom VARCHAR(200) NOT NULL, 
	description TEXT, 
	ordre INTEGER NOT NULL, 
	heure_prevue VARCHAR(5), 
	fait_le DATE, 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_routine_tasks PRIMARY KEY (id), 
	CONSTRAINT fk_routine_tasks_routine_id_routines FOREIGN KEY(routine_id) REFERENCES routines (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS versions_recette (
	id SERIAL NOT NULL, 
	recette_base_id INTEGER NOT NULL, 
	type_version VARCHAR(50) NOT NULL, 
	instructions_modifiees TEXT, 
	ingredients_modifies JSONB, 
	notes_bebe TEXT, 
	etapes_paralleles_batch JSONB, 
	temps_optimise_batch INTEGER, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_versions_recette PRIMARY KEY (id), 
	CONSTRAINT fk_versions_recette_recette_base_id_recettes FOREIGN KEY(recette_base_id) REFERENCES recettes (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS wellbeing_entries (
	id SERIAL NOT NULL, 
	child_id INTEGER, 
	username VARCHAR(200), 
	date DATE NOT NULL, 
	mood VARCHAR(100), 
	sleep_hours FLOAT, 
	activity VARCHAR(200), 
	notes TEXT, 
	cree_le TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT pk_wellbeing_entries PRIMARY KEY (id), 
	CONSTRAINT fk_wellbeing_entries_child_id_child_profiles FOREIGN KEY(child_id) REFERENCES child_profiles (id) ON DELETE CASCADE
)

;


CREATE TABLE IF NOT EXISTS historique_inventaire (
	id SERIAL NOT NULL, 
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
	date_modification TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	utilisateur VARCHAR(100), 
	notes TEXT, 
	CONSTRAINT pk_historique_inventaire PRIMARY KEY (id), 
	CONSTRAINT fk_historique_inventaire_article_id_inventaire FOREIGN KEY(article_id) REFERENCES inventaire (id) ON DELETE CASCADE, 
	CONSTRAINT fk_historique_inventaire_ingredient_id_ingredients FOREIGN KEY(ingredient_id) REFERENCES ingredients (id) ON DELETE CASCADE
)

;




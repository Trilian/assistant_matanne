// ═══════════════════════════════════════════════════════════
// Types Maison
// ═══════════════════════════════════════════════════════════

export interface ConseilMaisonHub {
  titre: string;
  description: string;
  niveau: "info" | "warning" | "urgent";
  module_source: string;
  action_type: "voir" | "planifier_entretien" | "acheter";
  action_payload: {
    chemin?: string;
    nom?: string;
    categorie?: string;
    [key: string]: unknown;
  };
  icone?: string;
}

export interface ProjetMaison {
  id: number;
  nom: string;
  description?: string;
  statut: string;
  priorite?: string;
  date_debut?: string;
  date_fin_prevue?: string;
  date_fin_reelle?: string;
  taches_count: number;
}

export interface TacheEntretien {
  id: number;
  nom: string;
  description?: string;
  categorie?: string;
  piece?: string;
  frequence_jours?: number;
  derniere_fois?: string;
  prochaine_fois?: string;
  duree_minutes?: number;
  responsable?: string;
  priorite?: string;
  fait: boolean;
}

export interface ElementJardin {
  id: number;
  nom: string;
  type?: string;
  location?: string;
  statut?: string;
  date_plantation?: string;
  date_recolte_prevue?: string;
  notes?: string;
}

export interface StockMaison {
  id: number;
  nom: string;
  categorie?: string;
  quantite: number;
  unite?: string;
  seuil_alerte: number;
  emplacement?: string;
  prix_unitaire?: number;
  en_alerte: boolean;
}

export interface ChargesMaison {
  id: number;
  type: string;
  fournisseur?: string;
  montant: number;
  date: string;
  mois: string;
  annee: number;
  commentaire?: string;
}

export interface CalendrierSemis {
  mois: number;
  mois_nom: string;
  a_semer: { nom: string; type: string; details: string }[];
  a_planter: { nom: string; type: string; details: string }[];
  a_recolter: { nom: string; type: string; details: string }[];
  conseils: string[];
}

export interface SanteZone {
  zone: string;
  total_taches: number;
  taches_a_jour: number;
  taches_en_retard: number;
  score_sante: number;
}

export interface SanteAppareils {
  score_global: number;
  zones: SanteZone[];
  actions_urgentes: {
    tache: string;
    zone: string;
    jours_retard: number;
    priorite?: string;
  }[];
}

// ═══════════════════════════════════════════════════════════
// Types Meubles
// ═══════════════════════════════════════════════════════════

export interface Meuble {
  id: number;
  nom: string;
  piece?: string;
  categorie?: string;
  prix_estime?: number;
  url_reference?: string;
  priorite?: string;
  statut?: string;
  notes?: string;
}

export interface BudgetMeublesResume {
  total_estime: number;
  prix_max: number;
  par_piece: Record<string, number>;
  nb_meubles: number;
}

// ═══════════════════════════════════════════════════════════
// Types Cellier
// ═══════════════════════════════════════════════════════════

export interface ArticleCellier {
  id: number;
  nom: string;
  categorie?: string;
  quantite: number;
  unite?: string;
  emplacement?: string;
  date_achat?: string;
  date_peremption?: string;
  seuil_alerte?: number;
  prix_unitaire?: number;
  code_barre?: string;
  notes?: string;
}

export interface AlertePeremption {
  id: number;
  nom: string;
  date_peremption: string;
  jours_restants: number;
  quantite: number;
}

export interface StatsCellier {
  total_articles: number;
  par_categorie: Record<string, number>;
  valeur_totale: number;
  articles_perimes: number;
  articles_bientot_perimes: number;
  articles_perimes_bientot?: number;
}

// ═══════════════════════════════════════════════════════════
// Types Artisans
// ═══════════════════════════════════════════════════════════

export interface Artisan {
  id: number;
  nom: string;
  metier: string;
  telephone?: string;
  email?: string;
  adresse?: string;
  note_satisfaction?: number;
  commentaire?: string;
  dernier_passage?: string;
}

export interface InterventionArtisan {
  id: number;
  artisan_id: number;
  date: string;
  description: string;
  cout?: number;
  etat?: string;
  notes?: string;
}

export interface StatsArtisans {
  total_artisans: number;
  par_metier: Record<string, number>;
  depenses_totales: number;
  total_depenses?: number;
  total_interventions: number;
}

// ═══════════════════════════════════════════════════════════
// Types Contrats
// ═══════════════════════════════════════════════════════════

export interface Abonnement {
  id: number;
  type_abonnement: string;
  fournisseur: string;
  numero_contrat?: string;
  prix_mensuel?: number;
  date_debut?: string;
  date_fin_engagement?: string;
  meilleur_prix_trouve?: number;
  fournisseur_alternatif?: string;
  notes?: string;
}

export interface AlerteAbonnement {
  id: number;
  type_abonnement: string;
  fournisseur: string;
  date_fin_engagement: string;
  jours_restants: number;
}

export interface ResumeAbonnements {
  total_mensuel: number;
  total_annuel: number;
  par_type: Record<string, number>;
}

// ═══════════════════════════════════════════════════════════
// Types Diagnostics & Estimations
// ═══════════════════════════════════════════════════════════

export interface DiagnosticImmobilier {
  id: number;
  type_diagnostic: string;
  date_realisation: string;
  date_expiration?: string;
  diagnostiqueur?: string;
  resultat?: string;
  document_url?: string;
  notes?: string;
}

export interface EstimationImmobiliere {
  id: number;
  date: string;
  valeur_estimee: number;
  source?: string;
  surface_m2?: number;
  prix_m2?: number;
  notes?: string;
}

// ═══════════════════════════════════════════════════════════
// Types Éco-Tips
// ═══════════════════════════════════════════════════════════

export interface ActionEcologique {
  id: number;
  titre: string;
  description?: string;
  categorie?: string;
  impact?: string;
  economie_estimee?: number;
  actif: boolean;
  date_debut?: string;
}

// ═══════════════════════════════════════════════════════════
// Types Dépenses
// ═══════════════════════════════════════════════════════════

export interface DepenseMaison {
  id: number;
  libelle: string;
  montant: number;
  categorie: string;
  date: string;
  fournisseur?: string;
  recurrence?: string;
  notes?: string;
}

export interface StatsDepenses {
  total_mois: number;
  total_mois_courant?: number;
  total_annee: number;
  total_annee_courante?: number;
  moyenne_mensuelle: number;
  delta_mois_precedent: number;
  par_categorie: Record<string, number>;
}

// ═══════════════════════════════════════════════════════════
// Types Extensions (Nuisibles, Devis, Entretien saisonnier, Relevés)
// ═══════════════════════════════════════════════════════════

export interface TraitementNuisible {
  id: number;
  type_nuisible: string;
  zone?: string;
  produit_utilise?: string;
  date_traitement: string;
  date_prochain?: string;
  efficacite?: string;
  notes?: string;
}

export interface DevisComparatif {
  id: number;
  projet_id?: number;
  artisan_nom: string;
  montant_ht: number;
  montant_ttc: number;
  date_devis: string;
  date_validite?: string;
  statut: string;
  fichier_url?: string;
  notes?: string;
  lignes?: LigneDevis[];
}

export interface LigneDevis {
  id: number;
  devis_id: number;
  description: string;
  quantite: number;
  prix_unitaire: number;
  total: number;
}

export interface EntretienSaisonnier {
  id: number;
  tache: string;
  saison: string;
  mois_recommande?: number;
  fait: boolean;
  date_realisation?: string;
  notes?: string;
}

export interface ReleveCompteur {
  id: number;
  type_compteur: string;
  valeur: number;
  date_releve: string;
  notes?: string;
}

// ═══════════════════════════════════════════════════════════
// Types Visualisation Plan
// ═══════════════════════════════════════════════════════════

export interface PieceMaison {
  id: number;
  nom: string;
  type_piece?: string;
  etage: number;
  surface_m2?: number;
  couleur?: string;
  position_x?: number;
  position_y?: number;
  largeur?: number;
  hauteur?: number;
  objets?: ObjetMaison[];
}

export interface ObjetMaison {
  id: number;
  piece_id: number;
  nom: string;
  type?: string;
  statut?: string;
  position_x?: number;
  position_y?: number;
  date_achat?: string;
  duree_garantie_mois?: number;
  marque?: string;
  modele?: string;
  sous_garantie?: boolean;
}

// ═══════════════════════════════════════════════════════════
// Types Hub Stats
// ═══════════════════════════════════════════════════════════

export interface StatsHubMaison {
  projets_en_cours: number;
  taches_en_retard: number;
  depenses_mois: number;
  stocks_en_alerte: number;
  articles_perimes: number;
  diagnostics_expirant: number;
}

// ═══════════════════════════════════════════════════════════
// Types Simulations Rénovation [PHASE 1]
// ═══════════════════════════════════════════════════════════

export interface SimulationRenovation {
  id: number;
  nom: string;
  description?: string;
  type_projet: string; // "conversion_piece", "isolation", "amenagement_terrain", etc.
  statut: "brouillon" | "en_cours" | "termine" | "archive";
  pieces_concernees?: string;
  zones_terrain?: string;
  projet_id?: number;
  plan_id?: number;
  tags?: string;
  notes?: string;
  scenarios_count: number;
  created_at?: string;
  updated_at?: string;
}

export interface ScenarioSimulation {
  id: number;
  simulation_id: number;
  nom: string;
  description?: string;
  est_favori: boolean;
  budget_estime_min?: number;
  budget_estime_max?: number;
  budget_materiaux?: number;
  budget_main_oeuvre?: number;
  duree_estimee_jours?: number;
  score_faisabilite?: number; // 0-100
  analyse_faisabilite?: string;
  contraintes_techniques?: string;
  recommandations?: string;
  impact_dpe?: string; // "D→B", etc.
  gain_energetique_pct?: number;
  plus_value_estimee?: number;
  postes_travaux?: PosteTravaux[];
  artisans_necessaires?: string;
  plan_avant_id?: number;
  plan_apres_id?: number;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface PosteTravaux {
  poste: string;
  budget_min?: number;
  budget_max?: number;
  diy?: boolean;
  duree?: number; // jours
}

export interface ComparaisonScenarios {
  simulation: SimulationRenovation;
  scenarios: ScenarioSimulation[];
  meilleur_budget?: number; // ID du scénario
  meilleur_faisabilite?: number;
  meilleur_rapport?: number;
}

// ═══════════════════════════════════════════════════════════
// Types Plans Maison 2D/3D [PHASE 1]
// ═══════════════════════════════════════════════════════════

export interface PlanMaison {
  id: number;
  nom: string;
  description?: string;
  type_plan: "interieur" | "terrain" | "etage_0" | "etage_1" | string;
  version: number;
  est_actif: boolean;
  donnees_canvas?: CanvasData; // Données react-konva JSON
  echelle_px_par_m: number;
  largeur_canvas: number;
  hauteur_canvas: number;
  etage: number;
  thumbnail_path?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CanvasData {
  murs?: Mur[];
  portes?: Porte[];
  fenetres?: Fenetre[];
  meubles?: MeublePlan[];
  annotations?: Annotation[];
  [key: string]: unknown;
}

export interface Mur {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  epaisseur: number; // cm
  porteur: boolean;
  couleur?: string;
  label?: string;
}

export interface Porte {
  id: string;
  x: number;
  y: number;
  largeur: number; // cm
  hauteur: number;
  cote: "gauche" | "droite" | "double";
  label?: string;
}

export interface Fenetre {
  id: string;
  x: number;
  y: number;
  largeur: number;
  hauteur: number;
  double_vitrage: boolean;
  label?: string;
}

export interface MeublePlan {
  id: string;
  nom: string;
  type: string; // "canape", "table", "lit", etc.
  x: number;
  y: number;
  largeur: number;
  hauteur: number;
  rotation: number; // degrés
  couleur?: string;
}

export interface Annotation {
  id: string;
  x: number;
  y: number;
  texte: string;
  type: "imaison" | "coffrage" | "warning" | "note";
  icone?: string;
}

// ═══════════════════════════════════════════════════════════
// Types Zones Terrain [PHASE 1]
// ═══════════════════════════════════════════════════════════

export interface ZoneTerrain {
  id: number;
  nom: string;
  type_zone: "potager" | "pelouse" | "terrasse" | "abri" | "allee" | "parking" | string;
  description?: string;
  surface_m2?: number;
  altitude_min?: number;
  altitude_max?: number;
  pente_pct?: number; // %
  exposition?: "nord" | "sud" | "est" | "ouest";
  geometrie?: Coordonnee[];
  lien_jardin: boolean;
  etat: "existant" | "a_amenager" | "en_travaux";
  date_amenagement?: string;
  cout_amenagement?: number;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Coordonnee {
  x: number;
  y: number;
}

// ═══════════════════════════════════════════════════════════
// Types Briefing Maison (contexte quotidien)
// ═══════════════════════════════════════════════════════════

export interface TacheJourMaison {
  nom: string;
  categorie?: string;
  duree_estimee_min?: number;
  priorite?: string;
  source?: string;
  fait: boolean;
  id_source?: number;
}

export interface MeteoResumeMaison {
  temperature_min?: number;
  temperature_max?: number;
  description?: string;
  precipitation_mm?: number;
  impact_jardin?: string;
  impact_menage?: string;
  alertes_meteo: string[];
}

export interface AlerteMaison {
  type: string;
  niveau: string;
  titre: string;
  message: string;
  action_url?: string;
  date_echeance?: string;
  entite_id?: number;
}

export interface BriefingMaison {
  date: string;
  resume: string;
  taches_jour: string[];
  taches_jour_detail: TacheJourMaison[];
  meteo?: MeteoResumeMaison;
  alertes: AlerteMaison[];
  projets_actifs: { id: number; nom: string; priorite?: string; avancement?: number }[];
  entretiens_saisonniers: { nom: string; description?: string; mois: number[] }[];
  jardin: { type: string; nom: string; urgence?: string; action?: string }[];
  cellier_alertes: { nom: string; jours_restants: number; quantite?: number }[];
  energie_anomalies: { type: string; message: string }[];
  eco_score_jour?: number;
}

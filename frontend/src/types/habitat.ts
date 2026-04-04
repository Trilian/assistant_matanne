export interface ScenarioHabitat {
  id: number;
  nom: string;
  description?: string;
  budget_estime?: number;
  surface_finale_m2?: number;
  nb_chambres?: number;
  score_global?: number;
  avantages: string[];
  inconvenients: string[];
  notes?: string;
  statut: string;
}

export interface CritereScenarioHabitat {
  id: number;
  scenario_id: number;
  nom: string;
  poids?: number;
  note?: number;
  commentaire?: string;
  score_global?: number;
}

export interface CritereImmoHabitat {
  id: number;
  nom: string;
  departements: string[];
  villes: string[];
  rayon_km: number;
  budget_min?: number;
  budget_max?: number;
  seuil_alerte?: number;
  actif: boolean;
}

export interface AnnonceHabitat {
  id: number;
  source: string;
  url_source: string;
  titre?: string;
  prix?: number;
  surface_m2?: number;
  surface_terrain_m2?: number;
  nb_pieces?: number;
  ville?: string;
  code_postal?: string;
  statut: string;
  score_pertinence?: number;
  prix_m2_secteur?: number;
  ecart_prix_pct?: number;
}

export interface PlanHabitat {
  id: number;
  scenario_id?: number;
  nom: string;
  type_plan: string;
  image_importee_url?: string;
  surface_totale_m2?: number;
  budget_estime?: number;
  version: number;
  suggestions_ia?: SuggestionPieceHabitat[];
}

export interface PieceHabitat {
  id: number;
  plan_id: number;
  nom: string;
  type_piece?: string;
  surface_m2?: number;
}

export interface ProjetDecoHabitat {
  id: number;
  piece_id?: number;
  nom_piece: string;
  style?: string;
  palette_couleurs?: string[];
  inspirations?: string[];
  budget_prevu?: number;
  budget_depense?: number;
  statut: string;
}

export interface ZoneJardinHabitat {
  id: number;
  plan_id: number;
  nom: string;
  type_zone?: string;
  surface_m2?: number;
  position_x?: number;
  position_y?: number;
  largeur?: number;
  longueur?: number;
  donnees_canvas?: import("@/types/commun").ObjetDonnees;
  plantes?: string[];
  amenagements?: string[];
  budget_estime?: number;
}

export interface HabitatHub {
  scenarios: number;
  annonces: number;
  plans: number;
  projets_deco: number;
  zones_jardin: number;
  alertes: number;
  annonces_a_traiter: number;
  budget_deco_total: number;
  budget_deco_depense: number;
}

export interface AlerteHabitat {
  id?: number;
  titre?: string;
  source: string;
  ville?: string;
  score?: number;
  prix?: number;
  ecart_prix_pct?: number;
  url_source: string;
  statut?: string;
}

export interface PointCarteHabitat {
  ville?: string;
  code_postal?: string;
  nb_annonces: number;
  score_max: number;
  prix_min?: number;
  prix_max?: number;
  latitude?: number;
  longitude?: number;
}

export interface StatSourceVeilleHabitat {
  source: string;
  url: string;
  annonces: number;
  alertes: number;
}

export interface ResultatSynchronisationVeilleHabitat {
  criteres: number;
  annonces_creees: number;
  annonces_mises_a_jour: number;
  alertes: number;
  sources: string[];
  stats_sources: StatSourceVeilleHabitat[];
}

export interface SuggestionPieceHabitat {
  nom: string;
  type_piece: string;
  surface_m2?: number;
  actions: string[];
}

export interface AnalysePlanHabitat {
  resume: string;
  points_forts: string[];
  risques: string[];
  budget_estime?: number;
  circulation_note?: number;
  suggestions_pieces: SuggestionPieceHabitat[];
  prompt_image?: string | null;
}

export interface HistoriquePlanHabitat {
  id: number;
  prompt_utilisateur: string;
  analyse_ia: AnalysePlanHabitat;
  image_generee_url?: string | null;
  acceptee?: boolean | null;
}

export interface ResultatImageHabitat {
  statut: string;
  modele: string;
  prompt: string;
  image_base64?: string | null;
  message?: string | null;
}

export interface ResultatAnalysePlanHabitat {
  plan_id: number;
  historique_id: number;
  analyse: AnalysePlanHabitat;
  image?: ResultatImageHabitat | null;
}

export interface ConceptDecoHabitat {
  resume: string;
  palette_couleurs: string[];
  materiaux: string[];
  achats_prioritaires: string[];
  prompt_image?: string | null;
}

export interface ResultatConceptDecoHabitat {
  projet_id: number;
  concept: ConceptDecoHabitat;
  image?: ResultatImageHabitat | null;
}

export interface ResumeJardinHabitat {
  zones: number;
  surface_totale_m2: number;
  budget_estime: number;
  types: string[];
}

export interface HistoriqueMarcheHabitatPoint {
  mois: string;
  transactions: number;
  prix_m2_median?: number | null;
  prix_m2_moyen?: number | null;
  valeur_moyenne?: number | null;
}

export interface RepartitionTypeMarcheHabitat {
  type_local: string;
  transactions: number;
  prix_m2_median?: number | null;
}

export interface TransactionMarcheHabitat {
  date_mutation: string;
  valeur_fonciere?: number | null;
  surface_m2?: number | null;
  prix_m2?: number | null;
  type_local?: string | null;
  nb_pieces?: number | null;
  code_postal?: string | null;
  commune?: string | null;
  adresse?: string | null;
}

export interface ResultatMarcheHabitat {
  source: {
    dataset_id: string;
    resource_id?: string | null;
    resource_title?: string | null;
  };
  query: {
    departement?: string | null;
    commune?: string | null;
    code_postal?: string | null;
    type_local?: string | null;
    nb_pieces_min?: number | null;
    surface_min_m2?: number | null;
  };
  resume: {
    nb_transactions: number;
    prix_m2_median?: number | null;
    prix_m2_moyen?: number | null;
    valeur_mediane?: number | null;
    surface_mediane?: number | null;
    dernier_mois?: HistoriqueMarcheHabitatPoint | null;
  };
  historique: HistoriqueMarcheHabitatPoint[];
  repartition_types: RepartitionTypeMarcheHabitat[];
  transactions: TransactionMarcheHabitat[];
}

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
  ville?: string;
  statut: string;
  score_pertinence?: number;
}

export interface PlanHabitat {
  id: number;
  scenario_id?: number;
  nom: string;
  type_plan: string;
  surface_totale_m2?: number;
  budget_estime?: number;
  version: number;
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
  budget_estime?: number;
}

export interface HabitatHub {
  scenarios: number;
  annonces: number;
  plans: number;
  projets_deco: number;
  zones_jardin: number;
}

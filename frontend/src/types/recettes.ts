// ═══════════════════════════════════════════════════════════
// Types Recettes
// ═══════════════════════════════════════════════════════════

export interface VersionRecette {
  id: number;
  recette_base_id: number;
  type_version: string; // 'jules' | 'cookeo' | 'monsieur_cuisine' | 'airfryer'
  instructions_modifiees?: string;
  ingredients_modifies?: Record<string, string>;
  notes_bebe?: string;
  modifications_resume: string[];
  recette_nom?: string;
  age_mois_jules?: number;
  alertes?: string[];
}

export interface EtapeRecette {
  id: number;
  ordre: number;
  description: string;
  titre?: string;
  duree?: number;
}

export interface Recette {
  id: number;
  nom: string;
  description?: string;
  instructions?: string;
  etapes?: EtapeRecette[];
  temps_preparation?: number;
  temps_cuisson?: number;
  portions?: number;
  difficulte?: "facile" | "moyen" | "difficile";
  categorie?: string;
  tags?: string[];
  image_url?: string;
  url_source?: string;
  ingredients: IngredientRecette[];
  est_favori?: boolean;
  genere_par_ia?: boolean;
  jours_depuis_derniere_cuisson?: number;
  compatible_cookeo?: boolean;
  compatible_monsieur_cuisine?: boolean;
  compatible_airfryer?: boolean;
  compatible_batch?: boolean;
  instructions_cookeo?: string;
  instructions_monsieur_cuisine?: string;
  instructions_airfryer?: string;
  calories?: number;
  proteines?: number;
  lipides?: number;
  glucides?: number;
  // Adaptations persistées
  version_jules?: VersionRecette;
  versions_robots?: VersionRecette[];
  created_at: string;
  updated_at?: string;
}

export interface IngredientRecette {
  id?: number;
  nom: string;
  quantite?: number;
  unite?: string;
  ordre?: number;
}

export interface CreerRecetteDTO {
  nom: string;
  description?: string;
  instructions?: string;
  temps_preparation?: number;
  temps_cuisson?: number;
  portions?: number;
  difficulte?: "facile" | "moyen" | "difficile";
  categorie?: string;
  tags?: string[];
  ingredients: Omit<IngredientRecette, "id">[];
}

export interface SuggestionRecette {
  nom: string;
  description: string;
  temps_total: number;
  difficulte: string;
  ingredients_principaux: string[];
  raison?: string;
}

export interface DoublonRecette {
  recette_source: { id: number; nom: string };
  recette_proche: { id: number; nom: string };
  score_similarite: number;
  raisons: string[];
  ingredients_communs?: string[];
}

export type FeedbackRecette = "like" | "neutral" | "dislike";

export interface RetourRecettePayload {
  recette_id: number;
  feedback: FeedbackRecette;
  note?: number;
  contexte?: string;
}

export interface RetourRecette {
  id: number;
  recette_id: number;
  feedback: FeedbackRecette;
  note?: number;
  contexte?: string;
  created_at: string;
}

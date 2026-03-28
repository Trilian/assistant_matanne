// ═══════════════════════════════════════════════════════════
// Types Recettes
// ═══════════════════════════════════════════════════════════

export interface Recette {
  id: number;
  nom: string;
  description?: string;
  instructions?: string;
  temps_preparation?: number;
  temps_cuisson?: number;
  portions?: number;
  difficulte?: "facile" | "moyen" | "difficile";
  categorie?: string;
  tags?: string[];
  image_url?: string;
  url_source?: string;
  ingredients: IngredientRecette[];
  note_moyenne?: number;
  est_favori?: boolean;
  compatible_cookeo?: boolean;
  compatible_monsieur_cuisine?: boolean;
  compatible_airfryer?: boolean;
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

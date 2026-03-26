// ═══════════════════════════════════════════════════════════
// Types Planning
// ═══════════════════════════════════════════════════════════

export type TypeRepas = "petit_dejeuner" | "dejeuner" | "gouter" | "diner";

export interface RepasPlanning {
  id: number;
  date_repas: string; // ISO date string (YYYY-MM-DD) — alias 'date' also accepted
  date?: string; // legacy alias pour compatibilité entrante
  type_repas: TypeRepas;
  recette_id?: number;
  recette_nom?: string;
  notes?: string;
  portions?: number;
  nutri_score?: string | null;
}

export interface PlanningSemaine {
  planning_id?: number;
  semaine: string;
  debut: string;
  fin: string;
  repas: RepasPlanning[];
}

export interface CreerRepasPlanningDTO {
  date: string;
  type_repas: TypeRepas;
  recette_id?: number;
  notes?: string;
  portions?: number;
}

export interface SuggestionRecettePlanning {
  id: number;
  nom: string;
  description?: string;
  temps_total: number;
  categorie?: string;
}

export interface GenererPlanningParams {
  date_debut?: string;
  nb_jours?: number;
  nb_personnes?: number;
  preferences?: Record<string, unknown>;
}

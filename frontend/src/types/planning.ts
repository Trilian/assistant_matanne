// ═══════════════════════════════════════════════════════════
// Types Planning
// ═══════════════════════════════════════════════════════════

import type { ObjetDonnees } from "@/types/commun";

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
  plat_jules?: string;
  notes_jules?: string;
  adaptation_auto?: boolean;
  compatible_cookeo?: boolean;
  compatible_monsieur_cuisine?: boolean;
  compatible_airfryer?: boolean;
}

export interface PlanningSemaine {
  planning_id?: number;
  semaine: string;
  debut: string;
  fin: string;
  repas: RepasPlanning[];
}

export interface PlanningMensuel {
  mois: string;
  debut: string;
  fin: string;
  repas: RepasPlanning[];
  par_jour: Record<string, RepasPlanning[]>;
}

export interface ConflitPlanning {
  type: string;
  niveau: "erreur" | "avertissement" | "info";
  message: string;
  date_jour: string;
  suggestion?: string | null;
  evenement_1?: ObjetDonnees | null;
  evenement_2?: ObjetDonnees | null;
}

export interface RapportConflitsPlanning {
  date_debut: string;
  date_fin: string;
  resume: string;
  nb_erreurs: number;
  nb_avertissements: number;
  nb_infos: number;
  items: ConflitPlanning[];
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
  preferences?: ObjetDonnees;
}

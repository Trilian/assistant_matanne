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
  genere_par_ia?: boolean;
  // Entrée (texte seul ou recette si complexe)
  entree?: string;
  entree_recette_id?: number;
  entree_recette_nom?: string;
  // Laitage (texte seul, jamais une recette)
  laitage?: string;
  // Fruit entier ou compote (goûter — ex: "Pomme", "Compote poire")
  fruit?: string;
  // Légumes accompagnement (déjeuner/dîner — ex: "Haricots verts", "Courgettes sautées")
  legumes?: string;
  // Dessert (texte seul ou recette si complexe)
  dessert?: string;
  dessert_recette_id?: number;
  dessert_recette_nom?: string;
  compatible_cookeo?: boolean;
  compatible_monsieur_cuisine?: boolean;
  compatible_airfryer?: boolean;
  // Reste réchauffé
  est_reste?: boolean;
  reste_description?: string | null;
  // Équilibre nutritionnel assiette (déj / dîner)
  legumes_recette_id?: number;
  feculents?: string;
  feculents_recette_id?: number;
  proteine_accompagnement?: string;
  proteine_accompagnement_recette_id?: number;
  // Goûter PNNS4
  fruit_gouter?: string;
  gateau_gouter?: string;
  // Score PNNS4 (0-100, null si non applicable)
  score_equilibre?: number | null;
  alertes_equilibre?: string[] | null;
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

export interface SuggestionAccompagnement {
  legumes: string[];
  feculents: string[];
  proteines: string[];
  categorie_detectee?: string | null;
}

export interface CreerRepasPlanningDTO {
  date: string;
  type_repas: TypeRepas;
  recette_id?: number;
  notes?: string;
  portions?: number;
  entree?: string;
  entree_recette_id?: number;
  dessert?: string;
  dessert_recette_id?: number;
  legumes?: string;
  legumes_recette_id?: number;
  feculents?: string;
  feculents_recette_id?: number;
  proteine_accompagnement?: string;
  proteine_accompagnement_recette_id?: number;
  laitage?: string;
  fruit_gouter?: string;
  gateau_gouter?: string;
}

export interface SuggestionRecettePlanning {
  id: number;
  nom: string;
  description?: string;
  temps_total: number;
  categorie?: string;
  genere_par_ia?: boolean;
}

export interface GenererPlanningParams {
  date_debut?: string;
  nb_jours?: number;
  nb_personnes?: number;
  preferences?: ObjetDonnees;
  legumes_souhaites?: string[];
  feculents_souhaites?: string[];
  plats_souhaites?: string[];
  ingredients_interdits?: string[];
  autoriser_restes?: boolean;
  cuisines_souhaitees?: string[];
}

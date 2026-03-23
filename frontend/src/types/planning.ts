// ═══════════════════════════════════════════════════════════
// Types Planning
// ═══════════════════════════════════════════════════════════

export type TypeRepas = "petit_dejeuner" | "dejeuner" | "gouter" | "diner";

export interface RepasPlanning {
  id: number;
  date: string;
  type_repas: TypeRepas;
  recette_id?: number;
  recette_nom?: string;
  notes?: string;
  portions?: number;
}

export interface PlanningSemaine {
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

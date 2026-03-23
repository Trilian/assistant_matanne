// ═══════════════════════════════════════════════════════════
// Types Batch Cooking
// ═══════════════════════════════════════════════════════════

export interface EtapeBatchCooking {
  id: number;
  ordre: number;
  groupe_parallele?: number;
  titre: string;
  duree_minutes?: number;
  robots_requis: string[];
  statut: string;
  est_terminee: boolean;
}

export interface SessionBatchCooking {
  id: number;
  nom: string;
  date_session?: string;
  heure_debut?: string;
  heure_fin?: string;
  duree_estimee?: number;
  duree_reelle?: number;
  statut: string;
  avec_jules: boolean;
  planning_id?: number;
  recettes_selectionnees: number[];
  robots_utilises: string[];
  genere_par_ia: boolean;
  etapes_count: number;
  progression: number;
  etapes?: EtapeBatchCooking[];
}

export interface CreerSessionBatchDTO {
  nom: string;
  date_session?: string;
  duree_estimee?: number;
  avec_jules?: boolean;
  recettes_selectionnees?: number[];
}

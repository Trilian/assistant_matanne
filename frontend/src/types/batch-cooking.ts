// ═══════════════════════════════════════════════════════════
// Types Batch Cooking
// ═══════════════════════════════════════════════════════════

export type StatutSessionBatch = 'planifiee' | 'en_cours' | 'terminee' | 'annulee' | 'pause'

export interface EtapeBatchCooking {
  id: number
  ordre: number
  groupe_parallele?: number | null
  titre: string
  duree_minutes?: number
  robots_requis: string[]
  statut: string
  est_terminee: boolean
  description?: string | null
  est_supervision?: boolean
  temperature?: number | null
}

export interface SessionBatchCooking {
  id: number
  nom: string
  date_session: string
  heure_debut?: string
  heure_fin?: string
  duree_estimee?: number
  duree_reelle?: number
  statut: StatutSessionBatch
  avec_jules: boolean
  planning_id?: number
  recettes_selectionnees: number[]
  robots_utilises: string[]
  preparations_simples: string[]
  genere_par_ia: boolean
  etapes_count: number
  progression: number
  etapes?: EtapeBatchCooking[]
}

export interface CreerSessionBatchDTO {
  nom: string
  date_session?: string
  duree_estimee?: number
  avec_jules?: boolean
  recettes_selectionnees?: number[]
  robots_utilises?: string[]
  planning_id?: number
}

export interface ModifierSessionBatchDTO {
  nom?: string
  date_session?: string
  statut?: StatutSessionBatch
  duree_estimee?: number
  avec_jules?: boolean
  recettes_selectionnees?: number[]
  robots_utilises?: string[]
}

export interface PreparationBatch {
  id: number
  nom: string
  portions_initiales?: number
  portions_restantes?: number
  date_preparation?: string
  date_peremption?: string
  localisation?: string
  container?: string
  consomme: boolean
  jours_avant_peremption?: number | null
  alerte_peremption?: boolean
}

export interface ConfigBatchCooking {
  jours_batch: number[]
  heure_debut_preferee?: string
  duree_max_session?: number
  avec_jules_par_defaut: boolean
  robots_disponibles: string[]
  objectif_portions_semaine: number
  couverture_jours?: Record<string, number[]> | null
}

export interface GenererSessionDepuisPlanningOptions {
  planning_id: number
  date_session: string
  nom?: string
  avec_jules?: boolean
  recettes_selectionnees?: number[]
  preparations_simples?: string[]
  /** @deprecated remplacé par recettes_selectionnees */
  jours_cibles?: number[]
}

export interface RecetteDepuisPlanningItem {
  id: number
  nom: string
  type_repas: string
  compatible_batch: boolean
}

export interface RecettesDepuisPlanningResponse {
  recettes: RecetteDepuisPlanningItem[]
  preparations_simples: string[]
}

export interface RecetteSessionBatch {
  id: number
  nom: string
  portions: number
}

export interface GenererSessionDepuisPlanningResult {
  session_id: number
  nom: string
  nb_recettes: number
  recettes: RecetteSessionBatch[]
  duree_estimee: number
  robots_utilises: string[]
}

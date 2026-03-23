// ═══════════════════════════════════════════════════════════
// Types Jeux
// ═══════════════════════════════════════════════════════════

export interface PariSportif {
  id: number;
  match_id?: number;
  type_pari: string;
  prediction?: string;
  cote: number;
  mise: number;
  statut: string;
  gain?: number;
  est_virtuel?: boolean;
  confiance_prediction?: number;
}

export interface MatchJeu {
  id: number;
  equipe_domicile?: string;
  equipe_exterieur?: string;
  championnat?: string;
  journee?: number;
  date_match: string;
  heure?: string;
  score_domicile?: number;
  score_exterieur?: number;
  resultat?: string;
  joue: boolean;
  cote_domicile?: number;
  cote_nul?: number;
  cote_exterieur?: number;
}

export interface TirageLoto {
  id: number;
  date_tirage: string;
  numeros: number[];
  numero_chance?: number;
  numeros_str?: string;
  jackpot_euros?: number;
  gagnants_rang1?: number;
}

export interface GrilleLoto {
  id: number;
  tirage_id?: number;
  numeros: number[];
  numero_chance?: number;
  est_virtuelle: boolean;
  source_prediction?: string;
}

export interface StatsParis {
  total_paris: number;
  total_mise: number;
  total_gain: number;
  benefice: number;
  taux_reussite: number;
  par_statut: Record<string, number>;
}

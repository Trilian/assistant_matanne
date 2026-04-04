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

// ─── Séries & Alertes ─────────────────────────────────────

export interface SerieJeux {
  id: number;
  type_jeu: string;
  marche: string;
  championnat?: string;
  serie_actuelle: number;
  frequence: number;
  value: number;
  niveau_opportunite: string;
}

export interface AlerteJeux {
  id: number;
  type_jeu: string;
  marche: string;
  championnat?: string;
  value_alerte: number;
  serie_alerte: number;
  frequence_alerte: number;
  seuil_utilise: number;
  notifie: boolean;
  date_creation?: string;
}

// ─── Prédictions & Value Bets ─────────────────────────────

export interface PredictionMatch {
  match_id: number;
  equipe_domicile?: string;
  equipe_exterieur?: string;
  resultat: string;
  probas: Record<string, number>;
  confiance: number;
  niveau_confiance: string;
  raisons: string[];
  conseil: string;
}

export interface ValueBet {
  match_id: number;
  equipe_domicile?: string;
  equipe_exterieur?: string;
  date_match: string;
  cote_bookmaker: number;
  proba_estimee: number;
  edge_pct: number;
  ev: number;
  type_pari: string;
  prediction: string;
}

// ─── Loto & Euromillions Stats ────────────────────────────

export interface NumeroRetard {
  numero: number;
  type_numero: string;
  serie_actuelle: number;
  frequence: number;
  derniere_sortie?: string;
  value: number;
}

export interface StatsLoto {
  total_tirages: number;
  frequences_numeros: Record<number, number>;
  numeros_chauds: number[];
  numeros_froids: number[];
  numeros_retard: NumeroRetard[];
}

export interface TirageEuromillions {
  id: number;
  date_tirage: string;
  numeros: number[];
  etoiles: number[];
  jackpot_euros?: number;
  gagnants_rang1?: number;
}

export interface GrilleEuromillions {
  id: number;
  tirage_id?: number;
  numeros: number[];
  etoiles: number[];
  est_virtuelle: boolean;
  source_prediction?: string;
  mise: number;
  gain?: number;
  rang?: number;
}

export interface StatsEuromillions {
  total_tirages: number;
  frequences_numeros: Record<number, number>;
  frequences_etoiles: Record<number, number>;
  numeros_chauds: number[];
  numeros_froids: number[];
  numeros_retard: NumeroRetard[];
  etoiles_chaudes: number[];
  etoiles_froides: number[];
}

// ─── Performance ──────────────────────────────────────────

export interface KPIsJeux {
  roi_mois: number;
  taux_reussite_mois: number;
  benefice_mois: number;
  paris_actifs: number;
}

export interface PerformanceMois {
  mois: string;
  roi: number;
  nb_paris: number;
  benefice: number;
}

export interface PerformanceJeux {
  roi: number;
  taux_reussite: number;
  benefice: number;
  nb_paris: number;
  par_mois: PerformanceMois[];
  par_championnat: Record<string, Record<string, number>>;
  par_type_pari: Record<string, Record<string, number>>;
  meilleur_mois?: string;
  pire_mois?: string;
  serie_gagnante_max: number;
  serie_perdante_max: number;
}

// ─── Analyse IA ───────────────────────────────────────────

export interface AnalyseIA {
  resume: string;
  points_cles: string[];
  recommandations: string[];
  avertissement: string;
  confiance: number;
  genere_le?: string;
}

// ─── Grilles générées ─────────────────────────────────────

export interface GrilleGeneree {
  numeros: number[];
  special: number[];
  strategie: string;
  analyse_ia?: string;
}

// ─── Backtest ─────────────────────────────────────────────

export interface BacktestResultat {
  type_jeu: string;
  nb_predictions: number;
  nb_correctes: number;
  taux_reussite: number;
  tirages_moyens: number;
  seuil_value: number;
  avertissement: string;
}

// ─── Résumé mensuel ───────────────────────────────────────

export interface ResumeMensuel {
  mois: string;
  analyse: string;
  points_forts: string[];
  points_faibles: string[];
  recommandations: string[];
  kpis: KPIsJeux;
}

// ─── Notifications ────────────────────────────────────────

export interface NotificationJeux {
  id: string;
  type: string;
  titre: string;
  message: string;
  urgence: string;
  type_jeu: string;
  lue: boolean;
  date_creation?: string;
}

// ─── Dashboard agrégé ─────────────────────────────────────

export interface DashboardJeux {
  opportunites: SerieJeux[];
  matchs_jour: MatchJourDashboard[];
  value_bets: ValueBet[];
  loto_retard: NumeroRetard[];
  kpis: KPIsJeux;
  analyse_ia?: AnalyseIA;
}

export interface MatchJourDashboard {
  id: number;
  equipe_domicile?: string;
  equipe_exterieur?: string;
  championnat?: string;
  heure?: string;
  cote_domicile?: number;
  cote_nul?: number;
  cote_exterieur?: number;
  prediction?: {
    resultat: string;
    confiance: number;
  };
}

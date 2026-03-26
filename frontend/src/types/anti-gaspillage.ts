// ═══════════════════════════════════════════════════════════
// Types Anti-Gaspillage
// ═══════════════════════════════════════════════════════════

export interface ScoreAntiGaspillage {
  score: number;
  articles_perimes_mois: number;
  articles_sauves_mois: number;
  economie_estimee: number;
}

export interface ArticleUrgent {
  id: number;
  nom: string;
  date_peremption: string;
  jours_restants: number;
  quantite?: number;
  unite?: string;
}

export interface RecetteRescue {
  id: number;
  nom: string;
  ingredients_utilises: string[];
  temps_total?: number;
  difficulte?: string;
}

export interface DonneesAntiGaspillage {
  score: ScoreAntiGaspillage;
  articles_urgents: ArticleUrgent[];
  recettes_rescue: RecetteRescue[];
}

export interface SemaineGaspillage {
  debut: string;
  fin: string;
  score: number;
  articles_perimes: number;
  articles_sauves: number;
  economie: number;
}

export interface BadgeGaspillage {
  id: string;
  nom: string;
  description: string;
  emoji: string;
  obtenu: boolean;
  condition_valeur: number;
  valeur_actuelle: number;
}

export interface HistoriqueGaspillage {
  semaines: SemaineGaspillage[];
  badges: BadgeGaspillage[];
  score_moyen_4s: number;
  tendance: "hausse" | "baisse" | "stable";
}

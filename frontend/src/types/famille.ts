// ═══════════════════════════════════════════════════════════
// Types Famille
// ═══════════════════════════════════════════════════════════

export interface ProfilEnfant {
  id: number;
  prenom: string;
  date_naissance: string;
  sexe?: string;
  photo_url?: string;
  est_actif: boolean;
}

export interface JalonJules {
  id: number;
  categorie: string;
  titre: string;
  description?: string;
  date_observation?: string;
  age_mois?: number;
  notes?: string;
  photo_url?: string;
}

export interface Activite {
  id: number;
  titre: string;
  description?: string;
  type: string;
  date: string;
  duree_minutes?: number;
  lieu?: string;
  participants?: string[];
  recurrence?: string;
  est_terminee: boolean;
}

export interface Routine {
  id: number;
  nom: string;
  type: "matin" | "soir" | "journee";
  etapes: EtapeRoutine[];
  est_active: boolean;
}

export interface EtapeRoutine {
  id: number;
  titre: string;
  duree_minutes?: number;
  ordre: number;
  est_terminee: boolean;
}

export interface DepenseBudget {
  id: number;
  libelle: string;
  montant: number;
  categorie: string;
  date: string;
  notes?: string;
}

export interface StatsBudget {
  total_mois: number;
  par_categorie: Record<string, number>;
  mois: string;
}

export interface ArticleWeekend {
  id: number;
  titre: string;
  description?: string;
  type: string;
  date?: string;
  lieu?: string;
  est_planifie: boolean;
}

export interface Anniversaire {
  id: number;
  nom_personne: string;
  date_naissance: string;
  relation: string;
  rappel_jours_avant: number[];
  idees_cadeaux?: string;
  historique_cadeaux?: string[];
  notes?: string;
  actif: boolean;
  age?: number;
  jours_restants?: number;
  cree_le: string;
}

export interface EvenementFamilial {
  id: number;
  titre: string;
  date_evenement: string;
  type_evenement: string;
  recurrence: string;
  rappel_jours_avant: number;
  notes?: string;
  participants?: string[];
  actif: boolean;
  cree_le: string;
}

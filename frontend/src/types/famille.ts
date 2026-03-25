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

// ═══════════════════════════════════════════════════════════
// Contexte Familial (Phase M/N)
// ═══════════════════════════════════════════════════════════

export interface MeteoActuelle {
  emoji?: string;
  temperature_min?: number;
  temperature_max?: number;
  condition?: string;
  precipitation_mm?: number;
  vent_km_h?: number;
  previsions_7j: {
    date: string;
    emoji: string;
    temp_min: number;
    temp_max: number;
    condition: string;
    precipitation_mm: number;
  }[];
}

export interface JourSpecial {
  nom: string;
  date: string;
  type: string;
  jours_restants: number;
}

export interface JulesContexte {
  age_mois: number;
  date_naissance: string;
  prochains_jalons: string[];
}

export interface DocumentExpirant {
  titre: string;
  jours_restants: number;
  severite: "info" | "warning" | "danger";
}

export interface AnniversaireContexte {
  id: number;
  nom_personne: string;
  age?: number;
  relation: string;
  jours_restants: number;
  idees_cadeaux?: string;
}

export interface RoutineContexte {
  id: number;
  nom: string;
  categorie?: string;
}

export interface ActiviteContexte {
  id: number;
  titre: string;
  date?: string;
  type_activite?: string;
  lieu?: string;
}

export interface AchatUrgent {
  id: number;
  nom: string;
  categorie: string;
  priorite: string;
  prix_estime?: number;
  suggere_par?: string;
}

export interface ContexteFamilial {
  meteo?: MeteoActuelle;
  jours_speciaux: JourSpecial[];
  anniversaires_proches: AnniversaireContexte[];
  jules?: JulesContexte;
  documents_expirants: DocumentExpirant[];
  routines_du_moment: RoutineContexte[];
  activites_a_venir: ActiviteContexte[];
  achats_urgents: AchatUrgent[];
}

// ═══════════════════════════════════════════════════════════
// Achats Famille (Phase M4/P)
// ═══════════════════════════════════════════════════════════

export interface AchatFamille {
  id: number;
  nom: string;
  categorie: string;
  priorite: string;
  prix_estime?: number;
  prix_reel?: number;
  taille?: string;
  magasin?: string;
  url?: string;
  description?: string;
  age_recommande_mois?: number;
  suggere_par?: string;
  achete: boolean;
  date_achat?: string;
}

export interface SuggestionAchat {
  titre: string;
  description: string;
  fourchette_prix?: string;
  ou_acheter?: string;
  pertinence?: string;
}

// ═══════════════════════════════════════════════════════════
// Rappels (Phase Q)
// ═══════════════════════════════════════════════════════════

export interface RappelFamille {
  type: string;
  message: string;
  priorite: "danger" | "warning" | "info";
  date_cible?: string;
  jours_restants?: number;
  click_url?: string;
}

// ═══════════════════════════════════════════════════════════
// Croissance OMS (Phase R)
// ═══════════════════════════════════════════════════════════

export interface PercentilesOMS {
  P3?: number;
  P15?: number;
  P50?: number;
  P85?: number;
  P97?: number;
}

export interface CroissanceData {
  age_mois: number;
  normes: Record<string, PercentilesOMS>;
}

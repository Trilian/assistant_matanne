// ═══════════════════════════════════════════════════════════
// Types Maison
// ═══════════════════════════════════════════════════════════

export interface ProjetMaison {
  id: number;
  nom: string;
  description?: string;
  statut: string;
  priorite?: string;
  date_debut?: string;
  date_fin_prevue?: string;
  date_fin_reelle?: string;
  taches_count: number;
}

export interface TacheEntretien {
  id: number;
  nom: string;
  description?: string;
  categorie?: string;
  piece?: string;
  frequence_jours?: number;
  derniere_fois?: string;
  prochaine_fois?: string;
  duree_minutes?: number;
  responsable?: string;
  priorite?: string;
  fait: boolean;
}

export interface ElementJardin {
  id: number;
  nom: string;
  type?: string;
  location?: string;
  statut?: string;
  date_plantation?: string;
  date_recolte_prevue?: string;
  notes?: string;
}

export interface StockMaison {
  id: number;
  nom: string;
  categorie?: string;
  quantite: number;
  unite?: string;
  seuil_alerte: number;
  emplacement?: string;
  prix_unitaire?: number;
  en_alerte: boolean;
}

export interface ChargesMaison {
  id: number;
  type: string;
  fournisseur?: string;
  montant: number;
  date: string;
  mois: string;
  annee: number;
  commentaire?: string;
}

export interface CalendrierSemis {
  mois: number;
  mois_nom: string;
  a_semer: { nom: string; type: string; details: string }[];
  a_planter: { nom: string; type: string; details: string }[];
  a_recolter: { nom: string; type: string; details: string }[];
  conseils: string[];
}

export interface SanteZone {
  zone: string;
  total_taches: number;
  taches_a_jour: number;
  taches_en_retard: number;
  score_sante: number;
}

export interface SanteAppareils {
  score_global: number;
  zones: SanteZone[];
  actions_urgentes: {
    tache: string;
    zone: string;
    jours_retard: number;
    priorite?: string;
  }[];
}

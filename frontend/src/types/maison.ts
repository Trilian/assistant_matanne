// ═══════════════════════════════════════════════════════════
// Types Maison
// ═══════════════════════════════════════════════════════════

export interface ConseilMaisonHub {
  titre: string;
  description: string;
  niveau: "info" | "warning" | "urgent";
  module_source: string;
  action_type: "voir" | "planifier_entretien" | "acheter";
  action_payload: {
    chemin?: string;
    nom?: string;
    categorie?: string;
    [key: string]: unknown;
  };
  icone?: string;
}

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

// ═══════════════════════════════════════════════════════════
// Types Meubles
// ═══════════════════════════════════════════════════════════

export interface Meuble {
  id: number;
  nom: string;
  piece?: string;
  categorie?: string;
  prix_estime?: number;
  url_reference?: string;
  priorite?: string;
  statut?: string;
  notes?: string;
}

export interface BudgetMeublesResume {
  total_estime: number;
  prix_max: number;
  par_piece: Record<string, number>;
  nb_meubles: number;
}

// ═══════════════════════════════════════════════════════════
// Types Cellier
// ═══════════════════════════════════════════════════════════

export interface ArticleCellier {
  id: number;
  nom: string;
  categorie?: string;
  quantite: number;
  unite?: string;
  emplacement?: string;
  date_achat?: string;
  date_peremption?: string;
  seuil_alerte?: number;
  prix_unitaire?: number;
  code_barre?: string;
  notes?: string;
}

export interface AlertePeremption {
  id: number;
  nom: string;
  date_peremption: string;
  jours_restants: number;
  quantite: number;
}

export interface StatsCellier {
  total_articles: number;
  par_categorie: Record<string, number>;
  valeur_totale: number;
  articles_perimes: number;
  articles_bientot_perimes: number;
  articles_perimes_bientot?: number;
}

// ═══════════════════════════════════════════════════════════
// Types Artisans
// ═══════════════════════════════════════════════════════════

export interface Artisan {
  id: number;
  nom: string;
  metier: string;
  telephone?: string;
  email?: string;
  adresse?: string;
  note_satisfaction?: number;
  commentaire?: string;
  dernier_passage?: string;
}

export interface InterventionArtisan {
  id: number;
  artisan_id: number;
  date: string;
  description: string;
  cout?: number;
  etat?: string;
  notes?: string;
}

export interface StatsArtisans {
  total_artisans: number;
  par_metier: Record<string, number>;
  depenses_totales: number;
  total_depenses?: number;
  total_interventions: number;
}

// ═══════════════════════════════════════════════════════════
// Types Contrats
// ═══════════════════════════════════════════════════════════

export interface Contrat {
  id: number;
  nom: string;
  type_contrat: string;
  fournisseur?: string;
  numero_contrat?: string;
  montant_mensuel?: number;
  montant_annuel?: number;
  date_debut: string;
  date_fin?: string;
  date_resiliation?: string;
  statut: string;
  notes?: string;
}

export interface AlerteContrat {
  id: number;
  nom: string;
  type_contrat: string;
  date_fin: string;
  jours_restants: number;
}

export interface ResumeFinancierContrats {
  total_mensuel: number;
  total_annuel: number;
  par_type: Record<string, number>;
}

// ═══════════════════════════════════════════════════════════
// Types Garanties
// ═══════════════════════════════════════════════════════════

export interface Garantie {
  id: number;
  appareil: string;
  nom?: string;
  marque?: string;
  numero_serie?: string;
  numero?: string;
  date_achat: string;
  date_debut?: string;
  date_fin_garantie: string;
  date_fin?: string;
  magasin?: string;
  fournisseur?: string;
  prix_achat?: number;
  piece?: string;
  document_url?: string;
  statut: string;
  notes?: string;
}

export interface IncidentSAV {
  id: number;
  garantie_id: number;
  date: string;
  description: string;
  statut: string;
  cout_reparation?: number;
  reference_dossier?: string;
  notes?: string;
}

export interface AlerteGarantie {
  id: number;
  appareil: string;
  date_fin_garantie: string;
  jours_restants: number;
}

export interface StatsGaranties {
  total: number;
  actives: number;
  expirees: number;
  valeur_totale: number;
}

export interface AlertePredictiveGarantie {
  garantie_id: number;
  nom_appareil: string;
  piece?: string;
  date_achat: string;
  duree_vie_ans: number;
  age_mois: number;
  mois_restants_estimes: number;
  niveau: "CRITIQUE" | "HAUTE" | "MOYENNE" | "BASSE";
  action_recommandee: string;
  action_url: string;
}

export interface ResultatDossierSAV {
  incident_id: number;
  message: string;
  prochaine_action: string;
  action_url: string;
}

// ═══════════════════════════════════════════════════════════
// Types Diagnostics & Estimations
// ═══════════════════════════════════════════════════════════

export interface DiagnosticImmobilier {
  id: number;
  type_diagnostic: string;
  date_realisation: string;
  date_expiration?: string;
  diagnostiqueur?: string;
  resultat?: string;
  document_url?: string;
  notes?: string;
}

export interface EstimationImmobiliere {
  id: number;
  date: string;
  valeur_estimee: number;
  source?: string;
  surface_m2?: number;
  prix_m2?: number;
  notes?: string;
}

// ═══════════════════════════════════════════════════════════
// Types Éco-Tips
// ═══════════════════════════════════════════════════════════

export interface ActionEcologique {
  id: number;
  titre: string;
  description?: string;
  categorie?: string;
  impact?: string;
  economie_estimee?: number;
  actif: boolean;
  date_debut?: string;
}

// ═══════════════════════════════════════════════════════════
// Types Dépenses
// ═══════════════════════════════════════════════════════════

export interface DepenseMaison {
  id: number;
  libelle: string;
  montant: number;
  categorie: string;
  date: string;
  fournisseur?: string;
  recurrence?: string;
  notes?: string;
}

export interface StatsDepenses {
  total_mois: number;
  total_mois_courant?: number;
  total_annee: number;
  total_annee_courante?: number;
  moyenne_mensuelle: number;
  delta_mois_precedent: number;
  par_categorie: Record<string, number>;
}

// ═══════════════════════════════════════════════════════════
// Types Extensions (Nuisibles, Devis, Entretien saisonnier, Relevés)
// ═══════════════════════════════════════════════════════════

export interface TraitementNuisible {
  id: number;
  type_nuisible: string;
  zone?: string;
  produit_utilise?: string;
  date_traitement: string;
  date_prochain?: string;
  efficacite?: string;
  notes?: string;
}

export interface DevisComparatif {
  id: number;
  projet_id?: number;
  artisan_nom: string;
  montant_ht: number;
  montant_ttc: number;
  date_devis: string;
  date_validite?: string;
  statut: string;
  fichier_url?: string;
  notes?: string;
  lignes?: LigneDevis[];
}

export interface LigneDevis {
  id: number;
  devis_id: number;
  description: string;
  quantite: number;
  prix_unitaire: number;
  total: number;
}

export interface EntretienSaisonnier {
  id: number;
  tache: string;
  saison: string;
  mois_recommande?: number;
  fait: boolean;
  date_realisation?: string;
  notes?: string;
}

export interface ReleveCompteur {
  id: number;
  type_compteur: string;
  valeur: number;
  date_releve: string;
  notes?: string;
}

// ═══════════════════════════════════════════════════════════
// Types Visualisation Plan
// ═══════════════════════════════════════════════════════════

export interface PieceMaison {
  id: number;
  nom: string;
  type_piece?: string;
  etage: number;
  surface_m2?: number;
  couleur?: string;
  position_x?: number;
  position_y?: number;
  largeur?: number;
  hauteur?: number;
  objets?: ObjetMaison[];
}

export interface ObjetMaison {
  id: number;
  piece_id: number;
  nom: string;
  type?: string;
  position_x?: number;
  position_y?: number;
}

// ═══════════════════════════════════════════════════════════
// Types Hub Stats
// ═══════════════════════════════════════════════════════════

export interface StatsHubMaison {
  projets_en_cours: number;
  taches_en_retard: number;
  garanties_expirant: number;
  contrats_a_renouveler: number;
  depenses_mois: number;
  stocks_en_alerte: number;
  articles_perimes: number;
  diagnostics_expirant: number;
}

// ═══════════════════════════════════════════════════════════
// Types Briefing Maison (contexte quotidien)
// ═══════════════════════════════════════════════════════════

export interface TacheJourMaison {
  nom: string;
  categorie?: string;
  duree_estimee_min?: number;
  priorite?: string;
  source?: string;
  fait: boolean;
  id_source?: number;
}

export interface MeteoResumeMaison {
  temperature_min?: number;
  temperature_max?: number;
  description?: string;
  precipitation_mm?: number;
  impact_jardin?: string;
  impact_menage?: string;
  alertes_meteo: string[];
}

export interface AlerteMaison {
  type: string;
  niveau: string;
  titre: string;
  message: string;
  action_url?: string;
  date_echeance?: string;
  entite_id?: number;
}

export interface BriefingMaison {
  date: string;
  resume: string;
  taches_jour: string[];
  taches_jour_detail: TacheJourMaison[];
  meteo?: MeteoResumeMaison;
  alertes: AlerteMaison[];
  projets_actifs: { id: number; nom: string; priorite?: string; avancement?: number }[];
  entretiens_saisonniers: { nom: string; description?: string; mois: number[] }[];
  jardin: { type: string; nom: string; urgence?: string; action?: string }[];
  cellier_alertes: { nom: string; jours_restants: number; quantite?: number }[];
  energie_anomalies: { type: string; message: string }[];
  eco_score_jour?: number;
}

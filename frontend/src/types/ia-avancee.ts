import type { ListeObjetsDonnees, ObjetDonnees } from "@/types/commun"

export interface SuggestionAchat {
  nom: string
  raison: string
  urgence: 'haute' | 'normale' | 'basse' | string
  frequence_achat_jours?: number | null
  quantite_suggeree?: string | null
}

export interface SuggestionsAchatsResponse {
  suggestions: SuggestionAchat[]
  nb_produits_analyses: number
  periode_analyse_jours: number
}

export interface PlanningAdaptatifResponse {
  recommandations: string[]
  repas_suggerees: ListeObjetsDonnees
  activites_suggerees: ListeObjetsDonnees
  score_adaptation: number
  contexte_utilise: ObjetDonnees
}

export interface DiagnosticPlantResponse {
  nom_plante: string
  etat_general: string
  problemes_detectes: string[]
  causes_probables: string[]
  traitements_recommandes: string[]
  arrosage_conseil?: string | null
  exposition_conseil?: string | null
  confiance: number
}

export interface PosteVigilance {
  [key: string]: unknown
}

export interface PrevisionsDepensesResponse {
  depenses_actuelles: number
  prevision_fin_mois: number
  budget_mensuel: number
  ecart_prevu: number
  tendance: string
  postes_vigilance: PosteVigilance[]
  conseils_economies: string[]
}

export interface IdeeCadeau {
  titre: string
  description: string
  fourchette_prix: string
  ou_acheter?: string | null
  pertinence: string
  raison?: string | null
}

export interface SuggestionsIdeasResponse {
  idees: IdeeCadeau[]
  destinataire: string
  occasion: string
}

export interface AnalysePhotoMultiResponse {
  contexte_detecte: string
  resume: string
  details: ObjetDonnees
  actions_suggerees: string[]
  confiance: number
}

export interface OptimisationRoutine {
  routine_concernee: string
  probleme_identifie: string
  suggestion: string
  gain_estime?: string | null
  priorite: string
}

export interface OptimisationRoutinesResponse {
  optimisations: OptimisationRoutine[]
  score_efficacite_actuel: number
  score_efficacite_projete: number
}

export interface AnalyseDocumentPhotoResponse {
  type_document: string
  titre: string
  date_document?: string | null
  emetteur?: string | null
  montant?: number | null
  informations_cles: string[]
  categorie_suggeree?: string | null
  actions_suggerees: string[]
}

export interface MateriauNecessaire {
  [key: string]: unknown
}

export interface EstimationTravauxResponse {
  type_travaux: string
  description: string
  budget_min: number
  budget_max: number
  duree_estimee?: string | null
  difficulte: string
  diy_possible: boolean
  artisans_recommandes: string[]
  materiaux_necessaires: MateriauNecessaire[]
}

export interface JourVoyage {
  jour: number
  date?: string | null
  activites: string[]
  repas_suggerees: string[]
  budget_jour?: number | null
  conseils: string[]
}

export interface PlanningVoyageResponse {
  destination: string
  duree_jours: number
  budget_total_estime: number
  jours: JourVoyage[]
  check_list_depart: string[]
  conseils_generaux: string[]
  adaptations_enfant: string[]
}

export interface RecommandationEnergie {
  titre: string
  description: string
  economie_estimee?: string | null
  cout_mise_en_oeuvre?: string | null
  difficulte: string
  priorite: string
  categorie: string
}

export interface EconomiesEnergieResponse {
  recommandations: RecommandationEnergie[]
  consommation_actuelle_resume?: string | null
  potentiel_economie_global?: string | null
}

export interface PredictionPanne {
  equipement: string
  risque: string
  probabilite_pct: number
  delai_estime?: string | null
  signes_alerte: string[]
  maintenance_preventive: string[]
  cout_remplacement_estime?: string | null
}

export interface PredictionPannesResponse {
  predictions: PredictionPanne[]
  nb_equipements_analyses: number
  score_sante_global: number
}

export interface SuggestionProactive {
  module: string
  titre: string
  message: string
  action_url?: string | null
  priorite: string
  contexte?: string | null
}

export interface SuggestionsProactivesResponse {
  suggestions: SuggestionProactive[]
  date_generation?: string | null
}

export interface AdaptationMeteo {
  type_adaptation: string
  condition_meteo: string
  recommandation: string
  impact: string
}

export interface AdaptationPlanningMeteoResponse {
  adaptations: AdaptationMeteo[]
  meteo_resume: ObjetDonnees
  date_prevision?: string | null
}

// ═══════════════════════════════════════════════════════════
// P6 — IA Avancée & Intelligence Proactive
// ═══════════════════════════════════════════════════════════

export interface InsightAnalytics {
  categorie: string
  titre: string
  valeur: string | number
  tendance: 'hausse' | 'baisse' | 'stable' | string
  detail?: string | null
}

export interface InsightsAnalyticsResponse {
  periode_mois: number
  insights: InsightAnalytics[]
  score_global?: number | null
  recommandations: string[]
}

export interface PiloteAutoStatus {
  actif: boolean
  niveau_autonomie: string
  modules_actifs: string[]
  derniere_action?: string | null
}

export interface ActionPiloteAutoRecente {
  module: string
  action: string
  date: string
  statut: string
  details?: string | null
}

export interface AutoTagsResponse {
  tags: string[]
  confiance: number
}

export interface MemoVocalResponse {
  module: string
  action: string
  contenu: string
  tags: string[]
  destination_url: string
  confiance: number
}

export interface AnomalieJardin {
  plante: string
  type_anomalie: string
  description: string
  severite: 'faible' | 'moyenne' | 'haute' | string
  recommandation: string
}

export interface AnomaliesJardinResponse {
  anomalies: AnomalieJardin[]
  recommandations: string[]
}

export interface ScoreEcologiqueResponse {
  score: string
  details: string
  recommandations: string[]
}

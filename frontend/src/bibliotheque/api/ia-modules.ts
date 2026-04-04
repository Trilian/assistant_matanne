import { clientApi } from "./client";

const API_PREFIX = "/api/v1/ia/modules";

export interface PredictionConsommationRequest {
  ingredient_nom: string;
  stock_actuel_kg: number;
  historique_achat_mensuel: Array<{
    date?: string;
    quantite_kg?: number;
  }>;
}

export interface PredictionConsommationResponse {
  ingredient_nom: string;
  consommation_hebdo_kg: number;
  stock_actuel_kg: number;
  jours_autonomie: number;
  seuil_reapprovisionnement_kg: number;
  raison: string;
}

export interface MealPlanningDay {
  jour?: string;
  date?: string;
  petit_dej?: string;
  petit_dejeuner?: string;
  midi?: string;
  dejeuner?: string;
  soir?: string;
  diner?: string;
}

export interface AnalyseVarietePlanningRequest {
  planning_repas: MealPlanningDay[];
}

export interface AnalyseVarieteResponse {
  score_variete: number;
  proteins_bien_repartis: boolean;
  types_cuisines: string[];
  repetitions_problematiques: string[];
  recommandations: string[];
}

export interface OptimisationNutritionPlanningRequest {
  planning_repas: MealPlanningDay[];
  restrictions?: string[];
}

export interface OptimisationNutritionPlanningResponse {
  calories_jour: Record<string, number>;
  proteines_equilibree: boolean;
  fruits_legumes_quota: number;
  equilibre_fibre: boolean;
  aliments_a_privilegier: string[];
  aliments_a_limiter: string[];
}

export interface SimplificationPlanningRequest {
  planning_repas: MealPlanningDay[];
  nb_heures_cuisine_max?: number;
}

export interface SimplificationPlanningResponse {
  nb_recettes_complexes: number;
  suggestions_simplification: string[];
  gain_temps_minutes: number;
  recettes_simples_substitution: string[];
  charge_globale: string;
}

export interface MeteoContexte {
  date: string;
  meteo: string;
  activites_suggerees: string[];
  recommandations?: string[];
}

export interface AnalyseImpactsMeteoRequest {
  previsions_7j: Array<{
    date: string;
    meteo: string;
    temperature_min: number;
    temperature_max: number;
    precipitation_mm: number;
  }>;
  saison: string;
}

export interface AnalyseHabitudeRequest {
  habitude_nom: string;
  historique_7j: number[];
  description_contexte?: string;
}

export interface AnalyseHabitudeResponse {
  compliance_rate: number;
  tendance: string;
  score_tendance: number;
}

export interface EstimationProjetMaisonRequest {
  projet_description: string;
  surface_m2: number;
  type_maison: string;
  contraintes?: string[];
}

export interface EstimationProjetResponse {
  cout_estime_min: number;
  cout_estime_max: number;
  duree_estimee_j: number;
  professionnel_recommande?: boolean;
  complexite_estimee?: string;
}

export interface DonneesNutritionPersonneRequest {
  personne_nom: string;
  age_ans: number;
  sexe: "M" | "F";
  activite_niveau: string;
  recettes_semaine: string[];
  objectif_sante?: string;
  donnees_garmin_semaine?: unknown;
}

export interface DonneesNutritionnellesResponse {
  calories_journalieres_recommandees: number;
  proteines_g_j: number;
  glucides_g_j: number;
  lipides_g_j: number;
  notes_personnalisees?: string;
}

export async function predireConsommationInventaire(
  body: PredictionConsommationRequest
): Promise<PredictionConsommationResponse> {
  const { data } = await clientApi.post<PredictionConsommationResponse>(
    `${API_PREFIX}/inventaire/prediction-consommation`,
    body
  );
  return data;
}

export async function analyserVarietePlanningRepas(
  body: AnalyseVarietePlanningRequest
): Promise<AnalyseVarieteResponse> {
  const { data } = await clientApi.post<AnalyseVarieteResponse>(
    `${API_PREFIX}/planning/analyse-variete`,
    body
  );
  return data;
}

export async function optimiserNutritionPlanningRepas(
  body: OptimisationNutritionPlanningRequest
): Promise<OptimisationNutritionPlanningResponse> {
  const { data } = await clientApi.post<OptimisationNutritionPlanningResponse>(
    `${API_PREFIX}/planning/optimisation-nutrition`,
    body
  );
  return data;
}

export async function suggererSimplificationPlanningRepas(
  body: SimplificationPlanningRequest
): Promise<SimplificationPlanningResponse> {
  const { data } = await clientApi.post<SimplificationPlanningResponse>(
    `${API_PREFIX}/planning/suggestions-simplification`,
    body
  );
  return data;
}

export async function analyserImpactsMeteo(
  body: AnalyseImpactsMeteoRequest
): Promise<MeteoContexte[]> {
  const { data } = await clientApi.post<MeteoContexte[]>(`${API_PREFIX}/meteo/impacts`, body);
  return data;
}

export async function analyserHabitudeFamille(
  body: AnalyseHabitudeRequest
): Promise<AnalyseHabitudeResponse> {
  const { data } = await clientApi.post<AnalyseHabitudeResponse>(`${API_PREFIX}/habitudes/analyse`, body);
  return data;
}

export async function estimerProjetMaison(
  body: EstimationProjetMaisonRequest
): Promise<EstimationProjetResponse> {
  const { data } = await clientApi.post<EstimationProjetResponse>(`${API_PREFIX}/maison/projets/estimation`, body);
  return data;
}

export async function analyserNutritionPersonne(
  body: DonneesNutritionPersonneRequest
): Promise<DonneesNutritionnellesResponse> {
  const { data } = await clientApi.post<DonneesNutritionnellesResponse>(`${API_PREFIX}/nutrition/personne`, body);
  return data;
}
